# Bounded fresh-process backend import observation

7October2026 (Asia/Calcutta), E2-040 follow-up / INC-056. Software revision faf60a707d8751dad7823684c3967e4d7dfc3961. **Windows import-only observation, not the historical failure reproduced/resolved, a stress test, model evaluation or experiment approval.** Four probes predeclared before execution; no replacements or adaptive retries. Stop on first failure,30second child timeout, fresh hidden Python processes using current existing virtual environment.

## Actual observation

| Probe | Import order | Fresh process | Result |
|---|---|---|---|
| 1 | Isolation Forest then autoencoder | Yes | Both backends imported |
| 2 | Autoencoder then Isolation Forest | Yes | Both backends imported |
| 3 | Isolation Forest then autoencoder | Yes | Both backends imported |
| 4 | Autoencoder then Isolation Forest | Yes | Both backends imported |

Planned4/launched4/not launched0, each child returned0/no capturedstderr. Every probe reports Python3.12.14, scikit-learn1.9.1/numpy2.5.3/scipy1.18.1/joblib1.6.0/threadpoolctl3.7.0/narwhals2.26.0/cloudpickle3.1.2. model_fitting_performed=false; parent root_cause_identified=false/actions_executed empty. This calls both existing _backend import/pin checks, not model constructors or fit/predict. It does not exercise the full-suite load/state that accompanied the earlier fault, all DLL paths, future availability or Linux fresh-process behavior.

No package install/upgrade/cache purge, model weights, collection, Docker/systemd/clock change, network/response or human data. Ordinary interpreter imports may use their normal ignored bytecode caches; no deliberate cache repair. Foreground diagnostic completes here, no future watch/schedule. If a probe had failed it would retain its safe category and leave remaining probes unlaunched, not retry to get success. Child raw stdout/stderr exceptions are not copied into publication; unexpected exit/stderr or timeout gets a generic status. Actual successful console JSON was inspected; no generated JSON report was saved. This Markdown is a manually transcribed observation record with the exact executed command, not an independently signed receipt.

The four successes do not establish INC-056's original cause or a repair. Its original failedXML SHA cdbbb46f11703516e63b180b26115ac5d66cd30184b600bee5eff89bbfec5571 remains unchanged. INC-057's reporting fix was established separately with injected faults/software tests. No more import batches are scheduled or needed to manufacture a fixed verdict. [Diagnostic contract](RUNTIME_ML_BACKEND_DIAGNOSTICS.md), [incident distinctions](INCIDENTS.md).

## Exact executed command

From repository root, existing Windows environment; the command prints JSON to the console without editing input files:

```powershell
@'
import json
import subprocess
import sys

child = '''import json,sys
from cloudguard import runtime_ml as ml, runtime_autoencoder as ae
order=json.loads(sys.argv[1])
try:
    for name in order:
        (ml if name == "iforest" else ae)._backend()
    result={"status":"backends_imported","python":sys.version.split()[0],"dependencies":ml._dependency_versions(),"model_fitting_performed":False}
except ml.RuntimeMLBackendError as error:
    result={"status":"backend_rejected",**ml.backend_failure_fields(error),"model_fitting_performed":False}
except Exception:
    result={"status":"unexpected_exception","model_fitting_performed":False}
print(json.dumps(result))
'''
orders = [['iforest','autoencoder'],['autoencoder','iforest'],['iforest','autoencoder'],['autoencoder','iforest']]
rows=[]
for index,order in enumerate(orders,1):
    try:
        run=subprocess.run([sys.executable,'-c',child,json.dumps(order)],capture_output=True,text=True,timeout=30,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if run.returncode != 0 or run.stderr:
            result={'status':'child_failed_or_stderr','model_fitting_performed':False}
        else:
            result=json.loads(run.stdout)
    except subprocess.TimeoutExpired:
        result={'status':'child_timeout','model_fitting_performed':False}
    rows.append({'probe':index,'order':order,'fresh_python_process':True,**result})
    if result['status'] != 'backends_imported':
        break
report={'protocol':'bounded_backend_import_observation_v1','planned_probes':4,'launched_probes':len(rows),'not_launched_probes':4-len(rows),'probes':rows,'root_cause_identified':False,'model_fitting_performed':False,'actions_executed':[]}
print(json.dumps(report,indent=2))
'@ | .venv/Scripts/python.exe -
```

This is a one-off diagnostic command, not a newly implemented production health/monitoring tool. Malformed child JSON/unexpected parent exceptions may abort without a full report; no transactional capture/hard resource sandbox guarantee. Four independent planned import observations are not automatic retries of a failed workload, and their success is not a benchmark denominator.
