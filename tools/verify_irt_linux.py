"""Owned disposable Linux HTTP/daemon/R test and sampled capacity evidence.

Never reads dotenv, shared DB credentials, real respondents or deploy targets.
Docker access is required on this trusted test host. No image is pushed.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import psycopg
from psycopg.rows import dict_row
from research.irt.synthetic import generate

PG='postgres@sha256:f9a7b9ebf6f56201f949db745e47bc423c0f0f8294bafe991cc10bf74b029657'


def command(*args,timeout=180):
    result=subprocess.run(list(args),capture_output=True,text=True,timeout=timeout)
    if result.returncode:
        (ROOT/'.scratch/irt-linux-command-failure.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        raise RuntimeError('Local command failed: '+args[0]+' '+(args[1] if len(args)>1 else ''))
    return result.stdout.strip()


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));return sock.getsockname()[1]


def memory_mib(value):
    quantity=value.split('/')[0].strip()
    for unit,mult in [('GiB',1024),('MiB',1),('KiB',1/1024),('GB',1000**3/1024**2),('MB',1000**2/1024**2),('kB',1000/1024**2),('B',1/1024**2)]:
        if quantity.endswith(unit):return float(quantity[:-len(unit)])*mult
    raise ValueError('Unknown Docker memory unit')


def verify_sources(manifest,profile):
    raw=(ROOT/manifest['profile']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=manifest['profileSha256']:raise ValueError('Profile digest changed')
    for name,pin in {**manifest['sourceSha256'],**profile['sourceSha256']}.items():
        if hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=pin:
            raise ValueError('Source pin changed: '+name)
    actual=command('docker','image','inspect',manifest['producerImage'],'--format','{{.Id}}')
    if actual!=profile['producerImage']:raise ValueError('Producer image mismatch')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--main-repo',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--capacity',action='store_true')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'research/irt-linux-image-v1.json').read_text())
    profile=json.loads((ROOT/manifest['profile']).read_text());verify_sources(manifest,profile)
    suffix=uuid4().hex[:12];pg='numora-irt-linux-pg-'+suffix
    api='numora-irt-linux-api-'+suffix;worker='numora-irt-linux-worker-'+suffix
    volume='numora-irt-linux-work-'+suffix;database='irt_research_test_'+uuid4().hex
    db_port=free_port();http_port=free_port();containers=[];volume_created=False
    url=f'postgresql://fixture@127.0.0.1:{db_port}/{database}'
    base=f'http://127.0.0.1:{http_port}';token='TEST_ONLY_'+uuid4().hex
    metrics={};metric_errors=[];stop=threading.Event()
    host=json.loads(command('docker','info','--format','{{json .}}'))
    report={'purpose':'RESEARCH_ONLY','productionApproved':False,'manifest':manifest,
        'host':{'dockerCPUs':host['NCPU'],'dockerMemoryBytes':host['MemTotal']},
        'targetHardwareValidated':False,'capacityEvidence':'SAMPLED_LOCAL_CORRECTNESS_NOT_SLO',
        'cases':[],'sharedDatabaseTouched':False,'canonicalPublication':False}
    def http(path,body=None,authorized=True):
        headers={'Content-Type':'application/json'}
        if authorized:headers['Authorization']='Bearer '+token
        req=Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        with urlopen(req,timeout=10) as response:return response.status,json.load(response)
    def sample():
        while not stop.is_set():
            try:
                names=command('docker','ps','--format','{{.Names}}',timeout=10).splitlines()
                picked=[n for n in names if n in [api,worker] or n.startswith('numora-irt-') and len(n)==43 and all(c in '0123456789abcdef' for c in n[11:])]
                if picked:
                    rows=command('docker','stats','--no-stream','--format','{{json .}}',*picked,timeout=15)
                    for line in rows.splitlines():
                        row=json.loads(line);role='api' if row['Name']==api else 'producer' if row['Name']==worker else 'R'
                        entry=metrics.setdefault(role,{'sampledPeakWorkingSetMiB':0,'sampledPeakCPUPercent':0,'samples':0})
                        entry['sampledPeakWorkingSetMiB']=max(entry['sampledPeakWorkingSetMiB'],memory_mib(row['MemUsage']))
                        entry['sampledPeakCPUPercent']=max(entry['sampledPeakCPUPercent'],float(row['CPUPerc'].rstrip('%')))
                        entry['samples']+=1
            except Exception:metric_errors.append('SAMPLE_UNAVAILABLE')
            stop.wait(2)
    monitor=None
    try:
        command('docker','run','-d','--name',pg,'-e','POSTGRES_USER=fixture','-e','POSTGRES_DB='+database,
            '-e','POSTGRES_HOST_AUTH_METHOD=trust','-p',f'127.0.0.1:{db_port}:5432','-p',f'127.0.0.1:{http_port}:8080',PG)
        containers.append(pg)
        deadline=time.monotonic()+45
        while True:
            try:
                with psycopg.connect(url,connect_timeout=2):break
            except psycopg.Error:
                if time.monotonic()>deadline:raise RuntimeError('Owned PostgreSQL did not start')
                time.sleep(.5)
        migrate="""import postgres from './packages/database/node_modules/postgres/src/index.js';
import {migrateIntegratedDatabase} from './packages/database/dist/integrated-migrations.js';
const sql=postgres(process.argv[1],{max:1,onnotice:()=>{}});
try{await migrateIntegratedDatabase(sql,process.argv[2]);}finally{await sql.end();}"""
        result=subprocess.run(['node','--input-type=module','-e',migrate,url,str(args.main_repo/'packages/database/drizzle')],
            cwd=args.main_repo,capture_output=True,text=True,timeout=180)
        if result.returncode:raise RuntimeError('Disposable schema migration failed')
        # Reuse the existing synthetic, restricted-role fixture; no production adapter shortcut.
        from tests.service import test_irt_postgres as fixtures
        fixtures.URL=url;fixtures.runtime_profile=lambda:profile
        cls=fixtures.IrtPostgresTests;cls.setUpClass();fixture=cls(methodName='runTest')
        compute=urlparse(cls.urls['compute']);compute_url=urlunparse(compute._replace(netloc=f'{compute.username}@127.0.0.1:5432'))
        command('docker','volume','create',volume);volume_created=True
        command('docker','run','--rm','--network','none','--user','0:0','--mount',f'type=volume,source={volume},target=/irt-work',
            profile['producerImage'],'python','-c',"import os;os.chown('/irt-work',10001,10001);os.chmod('/irt-work',0o700)")
        mount=f'type=bind,source={(ROOT/manifest["profile"]).resolve()},target=/app/research/irt-runtime-linux-v1.json,readonly'
        common=['--network','container:'+pg,'--read-only','--cap-drop','ALL','--security-opt','no-new-privileges',
            '--cpu-period','100000','--cpu-quota','200000','--tmpfs','/tmp:rw,nosuid,size=128m','--mount',mount,
            '-e','NUMORA_IRT_PRODUCER_IMAGE='+profile['producerImage'],'-e','NUMORA_IRT_RESEARCH_ENABLED=true',
            '-e','NUMORA_IRT_RESEARCH_TOKEN='+token,'-e','COMPUTE_DATABASE_URL='+compute_url,
            '-e','COMPUTE_SERVICE_PRINCIPAL_ID='+str(cls.principal)]
        shared=['--group-add','0','--mount','type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock',
            '--mount',f'type=volume,source={volume},target=/irt-work','-e','NUMORA_IRT_WORK_ROOT=/irt-work',
            '-e','NUMORA_IRT_WORK_VOLUME='+volume,'-e','DOCKER_CONFIG=/tmp/docker-config']
        runner=command('docker','run','--rm',*common,*shared,'--memory','512m',
            '-e','IRT_RESEARCH_TEST_IMAGE='+profile['image'],profile['producerImage'],
            'python','-B','-m','unittest','tests.service.test_irt_runner','-v',timeout=120)
        report['linuxRunnerFaults']='PASSED'
        command('docker','run','-d','--name',api,*common,'--memory','256m',profile['producerImage']);containers.append(api)
        deadline=time.monotonic()+30
        while True:
            try:http('/health/live',authorized=False);break
            except (URLError,TimeoutError,ConnectionError):
                if time.monotonic()>deadline:raise RuntimeError('Linux API did not start')
                time.sleep(.5)
        try:http('/api/v1/irt/capabilities',authorized=False);raise AssertionError('Anonymous capability access')
        except HTTPError as error:
            if error.code!=401:raise
        _,capability=http('/api/v1/irt/capabilities')
        assert capability['models']==['2PL','GPCM'] and not capability['publication']
        command('docker','run','-d','--name',worker,*common,*shared,'--memory','512m',profile['producerImage'],
            'python','-m','numora_service.irt.daemon');containers.append(worker)
        monitor=threading.Thread(target=sample,daemon=True);monitor.start()
        cases=[('INSUFFICIENT',2,2,20261119),('HEALTHY',1000,2,20261119)]
        if args.capacity:cases.extend([('CAPACITY',1666,3,20261119),('OVER_LIMIT',1667,3,20261119)])
        for label,per_arm,arms,seed in cases:
            print('Starting '+label+' '+str(per_arm*arms)+' respondents',flush=True)
            value,_=generate(per_arm,seed,arms=arms);notification,_=fixture.fixture(value)
            started=time.monotonic();status,ack=http('/api/v1/irt/compute/execute',notification)
            ack_seconds=time.monotonic()-started
            assert status==202 and ack_seconds<10
            deadline=time.monotonic()+1000
            while True:
                try:
                    _,done=http('/api/v1/irt/compute/requests/'+notification['requestId']+'?'+urlencode({
                        'inputDigest':notification['inputDigest'],'dispatchGeneration':1}))
                except (URLError,TimeoutError,ConnectionError):
                    report['statusPollTransportRetries']=report.get('statusPollTransportRetries',0)+1
                    if time.monotonic()>deadline:raise RuntimeError('Local status polling deadline exceeded')
                    time.sleep(2);continue
                if done['status'] in ['SUCCEEDED','FAILED','EXPIRED']:break
                if time.monotonic()>deadline:raise RuntimeError('Local execution exceeded test deadline')
                time.sleep(1)
            with psycopg.connect(url,row_factory=dict_row) as db:
                row=db.execute('SELECT payload,diagnostics FROM irt_compute.calibration_artifacts_v1 WHERE id=%s',(done['artifactId'],)).fetchone()
                # Research computation must not create canonical participant results or XP.
                assert db.execute('SELECT count(*) FROM assessment_attempts').fetchone()['count']==0
                assert db.execute('SELECT count(*) FROM xp_ledger').fetchone()['count']==0
            payload=row['payload'];outcome=payload['outcome']
            if label=='OVER_LIMIT':
                assert payload['executionStatus']=='FAILED' and payload['failure']['code']=='INVALID_INPUT'
            else:
                assert done['status']=='SUCCEEDED' and len(outcome['respondents'])==per_arm*arms
                assert {r['attemptId'] for r in outcome['respondents']}=={p['attemptId'] for p in value['respondents']}
                if label=='HEALTHY':assert all(r['status']=='SCORED' for r in outcome['respondents'])
                if label=='INSUFFICIENT':assert all(r['score'] is None for r in outcome['respondents'])
            _,replay=http('/api/v1/irt/compute/execute',notification)
            assert replay['artifactId']==done['artifactId']
            from collections import Counter
            case={'label':label,'respondents':per_arm*arms,'arms':arms,'ackSeconds':ack_seconds,
                'elapsedSeconds':time.monotonic()-started,'executionStatus':payload['executionStatus'],
                'measurementState':outcome['measurementState'] if outcome else None,
                'participantStatuses':dict(Counter(p['status'] for p in outcome['respondents'])) if outcome else {},
                'failure':payload['failure'],'artifactDigest':done['artifactDigest'],'sameArtifactOnReplay':True}
            report['cases'].append(case)
            print(json.dumps(case),flush=True)
            (args.output/'progress.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        for name in [api,worker]:
            state=json.loads(command('docker','inspect',name))[0]
            assert not state['State']['OOMKilled']
            report.setdefault('containers',{})['api' if name==api else 'producer']={
                'memoryLimitBytes':state['HostConfig']['Memory'],'cpuQuota':state['HostConfig']['CpuQuota']/state['HostConfig']['CpuPeriod'],
                'oomKilled':False,'readOnlyRoot':state['HostConfig']['ReadonlyRootfs']}
        report['status']='LOCAL_LINUX_VERIFIED'
    finally:
        stop.set()
        if monitor:monitor.join(timeout=20)
        report['sampledMetrics']=metrics;report['metricSampleErrors']=len(metric_errors)
        removed=True
        for name in reversed(containers):
            try:
                logs=subprocess.run(['docker','logs',name],capture_output=True,text=True,timeout=15)
                role='api' if name==api else 'producer' if name==worker else 'postgres'
                (args.output/(role+'.log')).write_text(logs.stdout+'\n'+logs.stderr,encoding='utf-8')
            except subprocess.TimeoutExpired:
                report.setdefault('cleanupWarnings',[]).append('LOG_READ_TIMEOUT')
            try:removed=subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=30).returncode==0 and removed
            except subprocess.TimeoutExpired:removed=False
        if volume_created:
            # An interrupted supervisor may leave its own R child. Restrict
            # cleanup to this run's uniquely named volume, never other jobs.
            try:
                children=command('docker','ps','-a','--filter','volume='+volume,'--format','{{.Names}}',timeout=15).splitlines()
                for child in children:
                    removed=subprocess.run(['docker','rm','-f',child],capture_output=True,timeout=30).returncode==0 and removed
                removed=subprocess.run(['docker','volume','rm',volume],capture_output=True,timeout=30).returncode==0 and removed
            except (RuntimeError,subprocess.TimeoutExpired):removed=False
        report['ownedResourcesRemoved']=removed
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('Linux verification complete; owned resources removed',flush=True)


if __name__=='__main__':main()
