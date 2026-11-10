"""Separate opt-in IRT HTTP process. POST accepts durable jobs, never runs R."""
from dataclasses import replace
import hmac
import json
import os
from fastapi import FastAPI,Request,Depends
from fastapi.responses import JSONResponse
from ..json_boundary import unique_object
from ..settings import Settings
from ..errors import ServiceError
from ..contracts import validate_notification
from .repository import Repository


def settings_from_env():
    return replace(Settings.from_env(),enabled=os.environ.get('NUMORA_IRT_RESEARCH_ENABLED')=='true',
                   token=os.environ.get('NUMORA_IRT_RESEARCH_TOKEN',''))


def create_app(settings=None,repository=None):
    settings=settings or settings_from_env()
    repository=repository or Repository(settings)
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
    def authorize(request:Request):
        if not settings.enabled:raise ValueError('IRT_RESEARCH_DISABLED')
        if not settings.valid():raise ValueError('IRT_RESEARCH_NOT_CONFIGURED')
        if not hmac.compare_digest(request.headers.get('Authorization','').encode(),('Bearer '+settings.token).encode()):
            raise ValueError('UNAUTHORIZED')
    @app.exception_handler(Exception)
    async def error(request,exc):
        code=str(exc) if isinstance(exc,(ValueError,ServiceError)) else 'INTERNAL_ERROR'
        allowed={'UNAUTHORIZED':401,'IRT_RESEARCH_DISABLED':503,'IRT_RESEARCH_NOT_CONFIGURED':503,
            'INVALID_JSON':422,'BODY_TOO_LARGE':413,'INPUT_DIGEST_MISMATCH':409,'STALE_DISPATCH':409,
            'POLICY_UNAVAILABLE':409,'UNSUPPORTED_CONTRACT':422,'INVALID_NOTIFICATION':422}
        status=allowed.get(code,500)
        if code not in allowed:code='INTERNAL_ERROR'
        return JSONResponse({'type':'urn:numora:irt:'+code.lower(),'title':code,'code':code,'status':status},status_code=status,media_type='application/problem+json',headers={'Cache-Control':'no-store'})
    @app.get('/health/live')
    def live():return {'serviceContract':'irt-calibration-service-v1','status':'alive'}
    @app.get('/health/ready',dependencies=[Depends(authorize)])
    def ready():
        from .operations import readiness
        code=readiness(repository)
        return JSONResponse({'serviceContract':'irt-calibration-service-v1','status':'ready' if code is None else 'blocked',
                             'code':code},status_code=200 if code is None else 503,headers={'Cache-Control':'no-store'})
    @app.get('/api/v1/irt/capabilities',dependencies=[Depends(authorize)])
    def capability():return {'serviceContract':'irt-calibration-service-v1','purpose':'RESEARCH_ONLY','ecosystems':['TRYOUT'],'models':['2PL','GPCM'],'comparisons':False,'publication':False}
    @app.get('/api/v1/irt/operations',dependencies=[Depends(authorize)])
    def operations():
        from .operations import metrics
        try:return JSONResponse(metrics(repository),headers={'Cache-Control':'no-store'})
        except Exception:return JSONResponse({'code':'DATABASE_NOT_READY'},status_code=503,headers={'Cache-Control':'no-store'})
    @app.post('/api/v1/irt/compute/execute',dependencies=[Depends(authorize)])
    async def accept(request:Request):
        if request.headers.get('content-type','').split(';')[0].strip()!='application/json':raise ValueError('INVALID_JSON')
        chunks=[];size=0
        async for chunk in request.stream():
            size+=len(chunk)
            if size>16384:raise ValueError('BODY_TOO_LARGE')
            chunks.append(chunk)
        try:
            value=json.loads(b''.join(chunks),object_pairs_hook=unique_object,
                parse_constant=lambda _:(_ for _ in ()).throw(ValueError()))
        except (ValueError,UnicodeError):raise ValueError('INVALID_JSON') from None
        validate_notification(value)
        from starlette.concurrency import run_in_threadpool
        result=await run_in_threadpool(repository.accept,value)
        return JSONResponse(result,status_code=202 if result['status'] in ['ACCEPTED','RUNNING'] else 200,headers={'Cache-Control':'no-store'})
    @app.get('/api/v1/irt/compute/requests/{request_id}',dependencies=[Depends(authorize)])
    def status(request_id:str,inputDigest:str,dispatchGeneration:int):
        notification={'contractVersion':3,'requestId':request_id,'inputDigest':inputDigest,'dispatchGeneration':dispatchGeneration}
        validate_notification(notification)
        return JSONResponse(repository.get(notification),headers={'Cache-Control':'no-store'})
    return app
