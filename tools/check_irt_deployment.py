"""Validate Compose semantics without starting containers or resolving real secrets."""
import json,os,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='irt-compose-check-') as folder:
        empty=Path(folder)/'empty.env';empty.write_text('')
        env={**os.environ,'IRT_PRODUCER_IMAGE':'sha256:'+'a'*64,'IRT_PRIVATE_ENV_FILE':str(empty),'IRT_POSTGRES_ENV_FILE':str(empty),'IRT_RUNTIME_PROFILE_FILE':str(ROOT/'research/irt-runtime-linux-v3.json'),'IRT_DOCKER_GID':'0'}
        env.pop('NUMORA_IRT_PRODUCTION_ENABLED',None);env.pop('NUMORA_IRT_RESEARCH_ENABLED',None)
        for mode in ['research','production']:
            result=subprocess.run(['docker','compose','-f',str(ROOT/f'deploy/irt-{mode}.compose.yaml'),'--profile',mode,'config','--format','json'],env=env,capture_output=True,text=True,timeout=30)
            if result.returncode:raise RuntimeError('COMPOSE_CONFIG_INVALID')
            services=json.loads(result.stdout)['services'];api=services['api'];worker=services['worker']
            assert api['tmpfs']==['/tmp:rw,nosuid,size=64m']
            assert api['network_mode']=='host' and not any('docker.sock' in v.get('source','') for v in api['volumes'])
            assert int(worker['mem_limit'])==1073741824 and int(api['mem_limit'])==268435456
            assert worker['environment']['NUMORA_IRT_WORK_VOLUME'] in ('numora-irt-research-work','numora-irt-production-work')
            if mode=='production':
                assert 'postgres' not in services
                assert api['environment']['NUMORA_IRT_PRODUCTION_ENABLED']=='false'
                assert api['environment']['NUMORA_IRT_RESEARCH_ENABLED']=='false'
            else:assert services['postgres']['ports'][0]['host_ip']=='127.0.0.1'
            print(mode.upper()+'_COMPOSE_VALID')


if __name__=='__main__':main()
