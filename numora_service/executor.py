"""Bounded subprocess generation; no database handles cross the process boundary."""
import multiprocessing
import logging
import time

from .bridge import config_hash, generate, make_record
from .content import payload
from .contracts import validate_payload
from .errors import ServiceError

LOG = logging.getLogger("numora.generator")


def generate_result(work):
    orig, cfg, seed = (work[k] for k in ("original", "config", "seed"))
    result = generate(orig, cfg, seed, [])
    record = make_record(orig, cfg, config_hash(cfg), seed, 1, result)
    content = payload(record, work["source"])
    validate_payload(content)
    return {"payload": content, "provenance": {
        "questionExternalId": orig["id"], "originalHash": orig["hash"], "originalVersion": orig["version"],
        "configHash": record["config_hash"], "configVersion": record["config_ver"],
        "seed": seed, "drawsUsed": result.draws_used, "valuesUsed": record["values_used"]}}


def child(work, sender):
    try:
        sender.send({"result": generate_result(work)})
    except ServiceError as exc:
        sender.send({"error": exc.code})
    except Exception:
        sender.send({"error": "GENERATION_FAILED"})
    finally:
        sender.close()


def run_process(work, heartbeat, settings):
    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=child, args=(work, sender), daemon=True)
    started = time.monotonic()
    next_heartbeat = started + settings.heartbeat_seconds
    try:
        process.start()
        sender.close()
        while True:
            now = time.monotonic()
            if now - started >= settings.execution_seconds:
                raise ServiceError("GENERATION_TIMEOUT", 504)
            if now >= next_heartbeat:
                heartbeat()
                next_heartbeat = time.monotonic() + settings.heartbeat_seconds
            if receiver.poll(min(0.1, max(0.001, settings.execution_seconds - (now - started)))):
                try:
                    message = receiver.recv()
                except EOFError:
                    raise ServiceError("GENERATION_FAILED", 422) from None
                if "error" in message:
                    raise ServiceError(message["error"], 422)
                return message["result"]
            if not process.is_alive():
                raise ServiceError("GENERATION_FAILED", 422)
    finally:
        if process.is_alive():
            process.terminate()
        if process.pid is not None:
            process.join(timeout=2)
            if process.is_alive():
                process.kill()
                process.join(timeout=2)
        sender.close()
        receiver.close()


class Executor:
    def __init__(self, repository, settings, runner=run_process):
        self.repository, self.settings, self.runner = repository, settings, runner

    def execute(self, notification):
        started = time.monotonic()
        claim = self.repository.claim(notification)
        if "response" in claim:
            LOG.info("request_id=%s execution_id=%s status=%s duration_ms=%d",
                     notification["requestId"], claim["response"]["executionId"],
                     claim["response"]["status"], int((time.monotonic() - started) * 1000))
            return claim["response"]
        execution = claim["execution"]
        try:
            result = self.runner(claim["work"], lambda: self.repository.heartbeat(execution), self.settings)
            response = self.repository.persist(notification, claim, result)
            LOG.info("request_id=%s execution_id=%s status=%s duration_ms=%d",
                     notification["requestId"], execution["id"], response["status"],
                     int((time.monotonic() - started) * 1000))
            return response
        except Exception as exc:
            code = exc.code if isinstance(exc, ServiceError) else "GENERATION_FAILED"
            LOG.info("request_id=%s execution_id=%s failure_code=%s duration_ms=%d",
                     notification["requestId"], execution["id"], code,
                     int((time.monotonic() - started) * 1000))
            try:
                self.repository.fail(execution, code)
            except ServiceError:
                # A commit might have succeeded before transport failed; never overwrite terminal history.
                pass
            if isinstance(exc, ServiceError):
                raise
            raise ServiceError(code, 422) from None
