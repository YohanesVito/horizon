"""Reproducible descriptive study; no trading or future-data fit."""
from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/dividend-research'
design=json.loads((OUT/'research-design.json').read_text())
def read(path):
    r=json.loads(path.read_text())['result']
    if 'content' in r:
        assert not r.get('isError'),path
        return json.loads(next(b['text'] for b in r['content'] if b['type']=='text'))
    return r

events=[]; paths=[]; frames={}; calendars={}; missing=[]
for e in design['events']:
    ex=e['ex_date']
    p=pd.DataFrame(read(OUT/f'bbca-prices-{ex}.json')).sort_values('date').reset_index(drop=True)
    m=pd.DataFrame(read(OUT/f'ihsg-{ex}.json')).set_index('date')['price']
    assert p.date.is_unique
    assert ((p.low<=p[['open','close']].min(axis=1)) & (p.high>=p[['open','close']].max(axis=1))).all()
    assert (p.volume>0).all()
    cal=[v for v in read(OUT/f'calendar-{ex}.json')['dividend'] if v['symbol']=='BBCA.JK' and v['ex_date']==ex]
    assert len(cal)==1
    cal=cal[0];calendars[ex]=cal
    j=p.index[p.date==ex][0]
    assert j>=10 and j+20<len(p)
    assert p.iloc[j-1].date==cal['cum_date']
    assert e['dividend_amount']==cal['dividend_amount']
    p['offset']=np.arange(len(p))-j
    frames[ex]=p
    entry=float(p.iloc[j-1].close);dps=float(cal['dividend_amount'])
    post=p.iloc[j:j+21]
    recovery=post[post.close>=entry]
    total_bep=post[post.close+dps>=entry]
    row={'ex_date':ex,'cum_date':cal['cum_date'],'recording_date':cal['recording_date'],'payment_date':cal['payment_date'],'declaration_date':None,'dps':dps,'cum_close':entry,'yield_on_cum_price':dps/entry,
         'pre_tminus10_to_cum_return':entry/float(p.iloc[j-10].close)-1,
         'ex_open':float(p.iloc[j].open),'ex_close':float(p.iloc[j].close),
         'ex_open_return':float(p.iloc[j].open)/entry-1,'ex_close_return':float(p.iloc[j].close)/entry-1,
         'ex_gross_total_return':(float(p.iloc[j].close)+dps)/entry-1,
         'price_bep_offset':int(recovery.iloc[0].offset) if len(recovery) else None,
         'gross_total_bep_offset':int(total_bep.iloc[0].offset) if len(total_bep) else None,
         'price_bep_censored_at_t20':not bool(len(recovery)),
         'worst_close_loss_vs_entry_to_t20':float(post.close.min()/entry-1),
         't20_gross_total_return':float((post.iloc[-1].close+dps)/entry-1),
         't20_date':post.iloc[-1].date,
         'cum_matches_previous_observed_session':True}
    for stage in ['recording_date','payment_date']:
        match=p[p.date==cal[stage]]
        row[stage+'_close']=float(match.iloc[0].close) if len(match) else None
        row[stage+'_offset']=int(match.iloc[0].offset) if len(match) else None
    if ex in m and cal['cum_date'] in m:
        row['ihsg_ex_return']=float(m[ex]/m[cal['cum_date']]-1)
        row['market_adjusted_ex_price_return']=row['ex_close_return']-row['ihsg_ex_return']
    else: row['market_adjusted_ex_price_return']=None
    for _,v in p[(p.offset>=-10)&(p.offset<=20)].iterrows():
        paths.append({'ex_date':ex,'date':v.date,'offset':int(v.offset),'close':float(v.close),'relative_price':float(v.close/entry),'gross_relative_wealth':float((v.close+(dps if v.offset>=0 else 0))/entry)})
    missing.append({'ex_date':ex,'stock_dates_without_index':sorted(set(p.date)-set(m.index))})
    events.append(row)

ev=pd.DataFrame(events)
pa=pd.DataFrame(paths)
ev.to_csv(OUT/'bbca-event-metrics.csv',index=False)
pa.to_csv(OUT/'bbca-aligned-paths.csv',index=False)
training=pa[(pa.ex_date<'2025-01-01')&(pa.offset>=0)]
quant=training.groupby('offset').relative_price.quantile([.1,.5,.9]).unstack()
forecast=[]
for row in events:
    if row['ex_date']<'2025-01-01':continue
    for _,actual in pa[(pa.ex_date==row['ex_date'])&(pa.offset>=0)].iterrows():
        q=quant.loc[actual.offset]
        forecast.append({'ex_date':row['ex_date'],'origin':row['cum_date'],'date':actual.date,'offset':int(actual.offset),'actual_close':actual.close,
                         'empirical_median':float(row['cum_close']*q[.5]),'empirical_p10':float(row['cum_close']*q[.1]),'empirical_p90':float(row['cum_close']*q[.9]),
                         'flat_price':row['cum_close'],'price_minus_dividend':row['cum_close']-row['dps']})
fc=pd.DataFrame(forecast)
fc.to_csv(OUT/'bbca-forecast-replay.csv',index=False)
mae={name:float((fc[name]-fc.actual_close).abs().mean()) for name in ['empirical_median','flat_price','price_minus_dividend']}
pr=pearsonr(ev.yield_on_cum_price,ev.ex_close_return)
sr=spearmanr(ev.yield_on_cum_price,ev.ex_close_return)
summary={'created_at':datetime.now(ZoneInfo('Asia/Makassar')).isoformat(),'scope':'BBCA only, 8 events from 2022–2025. Historical descriptive study; no verified declaration timestamps. Prices and dividends retrieved now, not true point-in-time snapshots.',
 'cost_label':'Gross; before transaction fees, taxes and slippage',
 'n_events':len(events),'median_pre_tminus10_to_cum_return':float(ev.pre_tminus10_to_cum_return.median()),
 'pre_cum_positive_count':int((ev.pre_tminus10_to_cum_return>0).sum()),
 'ex_close_negative_count':int((ev.ex_close_return<0).sum()),'median_ex_close_return':float(ev.ex_close_return.median()),
 'median_ex_market_adjusted_price_return':float(ev.market_adjusted_ex_price_return.median()),
 'median_ex_gross_total_return':float(ev.ex_gross_total_return.median()),'ex_gross_negative_count':int((ev.ex_gross_total_return<0).sum()),
 'price_bep_recovered_by_t20':int(ev.price_bep_offset.notna().sum()),'price_bep_censored_at_t20':int(ev.price_bep_offset.isna().sum()),
 'median_recovery_offset_among_recovered_only':float(ev.price_bep_offset.median()),
 'correlation_yield_vs_ex_price_return':{'pearson':float(pr.statistic),'spearman':float(sr.statistic),'n':len(events),'interpretation_limit':'Descriptive, same issuer, tiny dependent sample and common denominator. No causal claim or calibrated predictive strength.'},
 'forecast_replay':{'train_events':6,'test_events':2,'dependent_price_points':len(fc),'mae_IDR':mae,'empirical_p10_p90_observed_coverage':float(((fc.actual_close>=fc.empirical_p10)&(fc.actual_close<=fc.empirical_p90)).mean()),'origin':'Cum-day close; calendar is treated as given. Declaration-stage forecasting not available. Quantile envelope is not a calibrated prediction interval; outcomes across time are dependent.'},
 'missing_benchmark_dates':missing,'events':events}
(OUT/'study-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

ranking=read(OUT/'top5-yield-2025.json')['results']
watch=[]
for row in ranking:
    s=row['symbol'].split('.')[0]
    div=read(OUT/f'dividend-{s}.json')['dividend']['historical_dividends']['2025']
    watch.append({'symbol':s,'provider_total_yield_2025_pct':row['query_values']['total_yield[2025]']*100,'events_grouped_by_ex_year_2025':len(div['breakdown']),'dps_sum_as_reported':div['total_dividend'],'largest_payment_fraction':max(x['total'] for x in div['breakdown'])/div['total_dividend'],'not_a_forward_return_or_strategy_recommendation':True})
pd.DataFrame(watch).to_csv(OUT/'top5-yield-2025.csv',index=False)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
target='2025-03-21';row=next(e for e in events if e['ex_date']==target)
pp=frames[target];pp=pp[(pp.offset>=-6)&(pp.offset<=20)].copy();ff=fc[fc.ex_date==target]
fig=plt.figure(figsize=(13,8.2),layout='constrained')
gs=fig.add_gridspec(3,1,height_ratios=[1.1,4.8,.65])
ax0=fig.add_subplot(gs[0]);ax0.axis('off')
stages=[('Declaration','Belum tersedia'),('Cum','20 Mar 2025'),('Ex','21 Mar 2025'),('Recording','24 Mar 2025'),('Payment','11 Apr 2025')]
for i,(label,value) in enumerate(stages):
    ax0.text((i+.5)/5,.57,label+'\n'+value,ha='center',va='center',transform=ax0.transAxes,fontsize=11,color='#52616b' if i==0 else '#173e47',bbox={'boxstyle':'round,pad=.5','facecolor':'#f0f3f5' if i==0 else '#e5f3ef','edgecolor':'none'})
    if i<4:ax0.text((i+1)/5,.57,'→',ha='center',va='center',transform=ax0.transAxes)
ax0.set_title('BBCA: timeline dividen dan replay perkiraan harga',loc='left',fontsize=16,pad=10)
ax=fig.add_subplot(gs[1])
ax.plot(pd.to_datetime(pp.date),pp.close,label='Harga close aktual',color='#176b74',lw=2.1)
ax.plot(pd.to_datetime(ff.date),ff.empirical_median,label='Median pola 6 kejadian sebelumnya',color='#b75824',lw=1.8,ls='--')
ax.fill_between(pd.to_datetime(ff.date),ff.empirical_p10.to_numpy(),ff.empirical_p90.to_numpy(),color='#ddaa7b',alpha=.25,label='Rentang empiris P10–P90; belum terkalibrasi')
ax.plot(pd.to_datetime(ff.date),ff.price_minus_dividend,color='#70757b',ls=':',label='Acuan sederhana: harga cum − DPS')
for d,label in [(row['cum_date'],'Asal perkiraan: close cum'),(row['payment_date'],'Payment')]:
    ax.axvline(pd.Timestamp(d),color='#b0b7be',lw=1)
ax.set_ylabel('Harga per saham (Rp)');ax.set_xlabel('Tanggal; jarak pada grafik mengikuti kalender')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1));ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
ax.grid(axis='y',alpha=.18);ax.legend(loc='lower left',fontsize=9,frameon=False)
ax2=fig.add_subplot(gs[2]);ax2.axis('off')
ax2.text(0,.8,'Latih: 6 kejadian 2022–2024. Tampilan: satu kejadian uji 2025. Semua data pasar: Sectors.\nReplay bersyarat pada jadwal yang diketahui sekarang; bukan prediksi live. Perhitungan di luar biaya, pajak, dan slippage.',va='top',fontsize=10)
fig.savefig(OUT/'bbca-timeline-replay.png',dpi=170);fig.savefig(OUT/'bbca-timeline-replay.svg');plt.close(fig)

fig,ax=plt.subplots(figsize=(12,6),layout='constrained')
for ex,g in pa.groupby('ex_date'):
    ax.plot(g.offset,(g.relative_price-1)*100,lw=1.2,alpha=.75,label=ex)
ax.axvline(0,color='#333333',ls='--',lw=1);ax.axhline(0,color='#888888',lw=.8)
ax.set_title('BBCA: 8 lintasan harga di sekitar ex-date',loc='left',fontsize=16)
ax.set_xlabel('Urutan sesi yang tersedia relatif terhadap ex-date (t=0)')
ax.set_ylabel('Perubahan harga terhadap close cum (%)')
ax.grid(axis='y',alpha=.18);ax.legend(ncol=4,loc='upper center',bbox_to_anchor=(.5,-.13),frameon=False,fontsize=9)
fig.savefig(OUT/'bbca-event-paths.png',dpi=170);fig.savefig(OUT/'bbca-event-paths.svg');plt.close(fig)
print(json.dumps({k:v for k,v in summary.items() if k not in ['events','missing_benchmark_dates']},ensure_ascii=False,indent=2))
print('TARGET',json.dumps(row))
print('TARGET STAGE FORECASTS',fc[(fc.ex_date==target)&fc.date.isin([row['ex_date'],row['recording_date'],row['payment_date']])].to_json(orient='records'))
