"""Read the official Sectors calendar endpoint not exposed in MCP tools/list."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
try:
    from .sectors_mcp_probe import load_key
except ImportError:  # Direct script invocation remains supported.
    from sectors_mcp_probe import load_key

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--start',required=True)
    p.add_argument('--end',required=True)
    p.add_argument('--type',default='dividend')
    p.add_argument('--output',required=True)
    a=p.parse_args()
    key=load_key()
    url='https://api.sectors.app/v2/corporate-actions/?'+urlencode({'start':a.start,'end':a.end,'type':a.type})
    cfg='\n'.join(['url = '+json.dumps(url),'header = '+json.dumps('Authorization: '+key),'header = "Accept: application/json"'])+'\n'
    r=subprocess.run(['curl','--silent','--show-error','--max-time','40','--config','-','--write-out','\n%{http_code}'],input=cfg,text=True,capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.replace(key,'[REDACTED]'))
    body,status=r.stdout.rsplit('\n',1)
    result=json.loads(body.replace(key,'[REDACTED]'))
    output=Path(a.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'transport':'Sectors REST GET; endpoint absent from inspected MCP registry','url':url,'retrieved_at':datetime.now(ZoneInfo('Asia/Makassar')).isoformat(),'http_status':int(status),'result':result},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':int(status),'output':str(output),'keys':list(result) if isinstance(result,dict) else None}))
    if int(status)>=400: raise SystemExit(1)

if __name__=='__main__': main()
