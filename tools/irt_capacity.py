"""Read-only Linux capacity gate. Swap is evidence, never available RAM."""
from datetime import datetime,timezone
import json
import os
from pathlib import Path

LIMITS_MIB={'api':256,'worker':1024,'R':2048,'postgres':512,'hostReserve':512}
CPU_LIMITS={'api':0.25,'worker':0.5,'R':2,'postgres':0.5}


def evaluate(cpus,available_mib):
    required=sum(LIMITS_MIB.values())
    return {'status':'READY' if cpus>=sum(CPU_LIMITS.values()) and available_mib>=required else 'BLOCKED_CAPACITY',
            'cpus':cpus,'availableMiB':available_mib,'requiredMiB':required,'limitsMiB':LIMITS_MIB,
            'requiredCpu':sum(CPU_LIMITS.values()),'upgradeRecommendation':'4 vCPU / 8 GiB; remeasure available RAM after upgrade'}


def main():
    mem={k:int(v.split()[0]) for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
    cpus=len(os.sched_getaffinity(0))
    report=evaluate(cpus,mem['MemAvailable']//1024)
    report.update(measuredAt=datetime.now(timezone.utc).isoformat(),totalMiB=mem['MemTotal']//1024,
                  swapUsedMiB=(mem['SwapTotal']-mem['SwapFree'])//1024,R='NOT_RUN')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
