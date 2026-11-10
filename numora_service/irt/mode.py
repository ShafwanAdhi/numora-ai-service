"""Server-selected deployment mode; policy approval remains an external database decision."""
import os


def purpose():
    mode=os.environ.get('NUMORA_IRT_MODE','RESEARCH')
    if mode not in ('RESEARCH','PRODUCTION'):raise ValueError('IRT_MODE_INVALID')
    return 'PRODUCTION' if mode=='PRODUCTION' else 'RESEARCH_ONLY'


def enabled():
    if purpose()=='PRODUCTION':
        return os.environ.get('NUMORA_IRT_PRODUCTION_ENABLED')=='true' and os.environ.get('NUMORA_IRT_RESEARCH_ENABLED')!='true'
    return os.environ.get('NUMORA_IRT_RESEARCH_ENABLED')=='true' and os.environ.get('NUMORA_IRT_PRODUCTION_ENABLED')!='true'


def token():
    return os.environ.get('NUMORA_IRT_TOKEN' if purpose()=='PRODUCTION' else 'NUMORA_IRT_RESEARCH_TOKEN','')
