import hmac
import json

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from . import SERVICE_CONTRACT
from .bridge import catalog, validate_config, workspace
from .contracts import validate_notification
from .errors import ServiceError
from .executor import Executor
from .repository import Repository
from .settings import Settings


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def create_app(settings=None, repository=None, runner=None):
    settings = settings or Settings.from_env()
    bank, configs = workspace()
    repository = repository or Repository(settings, bank)
    executor = Executor(repository, settings, runner) if runner else Executor(repository, settings)
    app = FastAPI(title="Numora Generator", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)

    @app.exception_handler(ServiceError)
    async def service_error(request, exc):
        return JSONResponse({"type": "urn:numora:generator:" + exc.code.lower(), "title": exc.code,
                             "status": exc.status, "code": exc.code}, status_code=exc.status,
                            media_type="application/problem+json", headers={"Cache-Control": "no-store"})

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, exc):
        return await service_error(request, ServiceError("INVALID_REQUEST", 422))

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return await service_error(request, ServiceError("HTTP_" + str(exc.status_code), exc.status_code))

    @app.exception_handler(Exception)
    async def unknown_error(request, exc):
        return await service_error(request, ServiceError("INTERNAL_ERROR", 500))

    @app.middleware("http")
    async def bounded_body(request, call_next):
        if request.method == "POST":
            # Authenticate before reading a body. Stream limits also protect chunked requests.
            try:
                authorize(request)
            except ServiceError as exc:
                return await service_error(request, exc)
            chunks, size = [], 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > 16384:
                    return await service_error(request, ServiceError("BODY_TOO_LARGE", 413))
                chunks.append(chunk)
            request._body = b"".join(chunks)
        try:
            response = await call_next(request)
        except Exception:
            # Prevent ASGI's default traceback logger from printing unexpected secret-bearing exceptions.
            response = await service_error(request, ServiceError("INTERNAL_ERROR", 500))
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    def authorize(request: Request):
        if not settings.enabled:
            raise ServiceError("GENERATOR_DISABLED", 503)
        if not settings.valid():
            raise ServiceError("GENERATOR_NOT_CONFIGURED", 503)
        header = request.headers.get("Authorization", "")
        if not hmac.compare_digest(header.encode(), ("Bearer " + settings.token).encode()):
            raise ServiceError("UNAUTHORIZED", 401)

    @app.get("/health/live")
    def live():
        return {"serviceContract": SERVICE_CONTRACT, "status": "alive"}

    @app.get("/health/ready", dependencies=[Depends(authorize)])
    def ready():
        for qid in bank.ids():
            if configs.versions(qid):
                cfg, _ = configs.load(qid)
                if validate_config(cfg, bank.get(qid)):
                    raise ServiceError("BANK_CONFIG_INVALID", 503)
        catalog(bank, configs)
        repository.ready()
        return {"serviceContract": SERVICE_CONTRACT, "status": "ready"}

    @app.get("/api/v1/generators", dependencies=[Depends(authorize)])
    def generators():
        return {"serviceContract": SERVICE_CONTRACT, "items": catalog(bank, configs)}

    @app.post("/api/v1/compute/execute", dependencies=[Depends(authorize)])
    async def execute(request: Request):
        if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
            raise ServiceError("JSON_REQUIRED", 415)
        try:
            notification = json.loads(await request.body(), object_pairs_hook=unique_object,
                                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, UnicodeError):
            raise ServiceError("INVALID_JSON", 422) from None
        validate_notification(notification)
        from starlette.concurrency import run_in_threadpool
        response = await run_in_threadpool(executor.execute, notification)
        return JSONResponse(response, status_code=202 if response["status"] == "RUNNING" else 200)

    return app
