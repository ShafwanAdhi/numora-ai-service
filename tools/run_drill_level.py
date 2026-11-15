"""Run Drill LEVEL producer locally; no publication or Main writes."""
import argparse,json,hashlib,os
from pathlib import Path
from numora_service.irt.producer import run
from numora_service.irt.runner import run as run_r

def main():
 ap=argparse.ArgumentParser();ap.add_argument("input",type=Path);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
 if os.environ.get("NUMORA_IRT_DRILL_RESEARCH_ENABLED")!="true": raise SystemExit("IRT_DRILL_RESEARCH_DISABLED")
 value=json.loads(a.input.read_text(encoding="utf-8")); assert value["ecosystem"]=="DRILL" and value["context"]["scope"]=="LEVEL"
 dispatch={"executionId":value["calibrationId"],"dispatchGeneration":1}
 def runner(work): return run_r(work,image=os.environ.get("NUMORA_IRT_RESEARCH_IMAGE"),timeout=900)
 result,diagnostics=run(value,dispatch,runner)
 result["drillResearchCandidate"]=True;result["productionApproved"]=False
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({"artifact":result,"diagnostics":diagnostics},indent=2,allow_nan=False)+"\n")
 print(json.dumps({"status":"PASS","measurementState":result["outcome"]["measurementState"],"respondents":len(result["outcome"]["respondents"]),"digest":hashlib.sha256(a.output.read_bytes()).hexdigest()}))
if __name__=="__main__":main()
