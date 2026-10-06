"""Collect the prespecified BBCA event windows and screener examples."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo
from sectors_mcp_probe import Client

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/dividend-research'
design=json.loads((OUT/'research-design.json').read_text())

def call(client, name, arguments, path):
    if path.exists(): return
    result=client.request('tools/call',{'name':name,'arguments':arguments})
    if result.get('isError'): raise RuntimeError(f'{name} returned a tool error')
    path.write_text(json.dumps({'transport':'MCP Streamable HTTP','retrieved_at':datetime.now(ZoneInfo('Asia/Makassar')).isoformat(),'tool':name,'arguments':arguments,'result':result},ensure_ascii=False,indent=2)+'\n')

def event_job(event):
    ex=date.fromisoformat(event['ex_date'])
    start=(ex-timedelta(days=25)).isoformat()
    end=(ex+timedelta(days=60)).isoformat()
    client=Client();client.initialize()
    call(client,'fetch-daily-price',{'symbol':'BBCA','start':start,'end':end},OUT/f'bbca-prices-{ex}.json')
    call(client,'fetch-index-daily',{'index_code':'ihsg','start':start,'end':end},OUT/f'ihsg-{ex}.json')
    path=OUT/f'calendar-{ex}.json'
    if not path.exists():
        result=subprocess.run([sys.executable,str(ROOT/'work/sectors_calendar_probe.py'),'--start',ex.isoformat(),'--end',ex.isoformat(),'--output',str(path)],capture_output=True,text=True)
        if result.returncode: raise RuntimeError(result.stdout+result.stderr)
    return {'event':str(ex),'files':3,'status':'collected'}

def screener_job(symbol):
    client=Client();client.initialize()
    call(client,'fetch-company-report',{'symbol':symbol,'sections':['dividend']},OUT/f'dividend-{symbol}.json')
    return {'screener_symbol':symbol,'status':'collected'}

jobs=[(event_job,e) for e in design['events']]+[(screener_job,s) for s in ['DMAS','LPPF','ADRO','CFIN','RALS']]
errors=[]
with ThreadPoolExecutor(max_workers=3) as pool:
    futures={pool.submit(fn,arg):str(arg) for fn,arg in jobs}
    for future in as_completed(futures):
        try: print(json.dumps(future.result()),flush=True)
        except Exception as exc:
            errors.append({'job':futures[future],'error':str(exc)})
            print(json.dumps(errors[-1]),flush=True)
if errors: raise SystemExit(1)
