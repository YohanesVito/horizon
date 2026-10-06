"""Small, explicit Sectors sample to support real multi-issuer replay."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from sectors_mcp_probe import Client

OUT = Path(__file__).resolve().parents[1] / 'outputs/mvp-sectors'
OUT.mkdir(exist_ok=True)
jobs = [(f'prices-{s}.json', 'fetch-daily-price', {'symbol': s, 'start': '2025-02-24', 'end': '2025-05-20'}) for s in ['BBRI','BMRI','BBNI','LPPF']]
jobs += [(f'report-{s}.json', 'fetch-company-report', {'symbol':s,'sections':['dividend']}) for s in ['BBRI','BMRI','BBNI']]

def collect(job):
    name,tool,args=job
    path=OUT/name
    if path.exists(): return {'file':name,'cached':True}
    c=Client();c.initialize()
    result=c.request('tools/call',{'name':tool,'arguments':args})
    if result.get('isError'): raise RuntimeError(f'{tool} failed: {result}')
    path.write_text(json.dumps({'transport':'MCP Streamable HTTP','retrieved_at':datetime.now(timezone.utc).isoformat(),'tool':tool,'arguments':args,'result':result},ensure_ascii=False,indent=2)+'\n')
    return {'file':name,'ok':True}

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2) as pool:
        for r in pool.map(collect,jobs): print(json.dumps(r),flush=True)
