// Real production UI/API check. Existing preview snapshot; no API mocks.
// PLAYWRIGHT_MODULE=/tmp/horizon-ui-check/node_modules/playwright node work/verify_timeline_pin.cjs [baseline]
const fs=require('node:fs');
const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base=process.env.UI_BASE_URL || 'http://localhost:3000';
const baseline=process.argv[2]==='baseline';
const evidence={recorded_at:new Date().toISOString(),base,mode:baseline?'baseline':'after',source:'real LPPF snapshot API / rendered SVG path coordinates',checks:[],requests:[],page_errors:[]};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function enter(page){await page.goto(base);await page.getByRole('button',{name:'Timeline',exact:true}).click();await page.getByRole('button',{name:/Buka pratinjau LPPF/}).click();await page.getByRole('button',{name:'Fokus tahun 2024',exact:true}).waitFor();await page.locator('svg[aria-label^="Overlay harga LPPF"]').scrollIntoViewIfNeeded();await pause(200);}
async function coordinates(page,year){
  return page.locator('svg[aria-label^="Overlay harga LPPF"]').evaluate((svg,year)=>{
    const series=[...svg.querySelectorAll('[data-period]')].map(g=>({year:Number(g.dataset.period),points:[...g.querySelector('path[stroke]').getAttribute('d').matchAll(/[ML]([\d.-]+),([\d.-]+)/g)].map(m=>({x:Number(m[1]),y:Number(m[2])}))}));
    const target=series.find(s=>s.year===year);const vb=svg.viewBox.baseVal;const box=svg.getBoundingClientRect();
    const ranked=target.points.filter(p=>p.x>80&&p.x<vb.width-40).map(p=>({...p,separation:Math.min(...series.filter(s=>s.year!==year).map(s=>{const q=s.points.reduce((a,b)=>Math.abs(a.x-p.x)<Math.abs(b.x-p.x)?a:b);return Math.hypot(q.x-p.x,q.y-p.y)}))})).sort((a,b)=>b.separation-a.separation);
    const p=ranked[0];return {year,...p,clientX:box.x+p.x*box.width/vb.width,clientY:box.y+p.y*box.height/vb.height};
  },year);
}
async function observe(page){return {locked:await page.locator('.timeline-legend button[aria-pressed=true]').count()?Number((await page.locator('.timeline-legend button[aria-pressed=true]').getAttribute('aria-label')).match(/\d+/)[0]):null,focus:await page.locator('.timeline-focus-heading').innerText(),tooltip:await page.locator('.timeline-tooltip').count()?await page.locator('.timeline-tooltip').innerText():null,meta:await page.locator('.timeline-chart-meta').innerText()};}
async function move(page,year){const point=await coordinates(page,year);await page.mouse.move(point.clientX,point.clientY);await pause(80);return point;}
async function verify(page,width,touch=false){
  await enter(page);const first=await move(page,2024);let observed=await observe(page);assert.match(observed.focus,/2024/);assert.match(observed.tooltip,/2024 · Historis/);assert.equal(observed.locked,null);
  const second=await move(page,2025);observed=await observe(page);assert.match(observed.focus,/2025/);assert.equal(observed.locked,null);
  if(!baseline){const box=await page.locator('svg[aria-label^="Overlay harga LPPF"]').boundingBox();await page.mouse.click(box.x+5,box.y+5);assert.equal((await observe(page)).locked,null);}
  await move(page,2024);
  if(touch){await page.getByRole('button',{name:'Bandingkan semua',exact:true}).click();await page.mouse.move(0,0);assert.equal((await observe(page)).tooltip,null);}
  if(touch) await page.touchscreen.tap(first.clientX,first.clientY);else await page.mouse.click(first.clientX,first.clientY);
  await move(page,2025);observed=await observe(page);
  if(baseline){assert.equal(observed.locked,null);assert.match(observed.focus,/2025/);evidence.checks.push({width,first,second,after_click_and_other_hover:observed,regression:'Direct chart click does not pin before implementation'});return;}
  assert.equal(observed.locked,2024);assert.match(observed.focus,/2024/);assert.match(observed.tooltip,/2024 · Historis/);
  const year2024=await page.locator('g[data-period="2024"] path[stroke]').evaluate(path=>[...path.getAttribute('d').matchAll(/[ML]([\d.-]+),([\d.-]+)/g)].map(m=>Number(m[1])));
  const index=year2024.reduce((best,x,i)=>Math.abs(x-second.x)<Math.abs(year2024[best]-second.x)?i:best,0);
  const dataset=await(await page.request.get(base+'/api/timeline/LPPF?preview=true')).json();const expectedPoint=dataset.history.find(p=>p.year===2024).points.filter(p=>p.change_pct!==null)[index];
  const expectedDate=new Date(expectedPoint.date+'T12:00:00').toLocaleDateString('id-ID',{day:'numeric',month:'short',year:'numeric'});assert.ok(observed.tooltip.includes(expectedDate));
  const pinnedObservation=observed;
  if(touch)await page.touchscreen.tap(second.clientX,second.clientY);else await page.mouse.click(second.clientX,second.clientY);
  const unlocked=await observe(page);assert.equal(unlocked.locked,null);assert.equal(unlocked.tooltip,null);
  const allOpacities=await page.locator('g.timeline-series').evaluateAll(gs=>gs.map(g=>g.getAttribute('opacity')));assert.ok(allOpacities.every(o=>o==='1'));
  await move(page,2025);assert.match((await observe(page)).focus,/2025/);
  await move(page,2024);if(touch)await page.touchscreen.tap(first.clientX,first.clientY);else await page.mouse.click(first.clientX,first.clientY);
  assert.equal((await observe(page)).locked,2024);
  await page.mouse.move(0,0);observed=await observe(page);assert.equal(observed.locked,2024);assert.match(observed.focus,/2024/);assert.equal(observed.tooltip,null);
  await page.getByRole('button',{name:'Fokus tahun 2023',exact:true}).click();await move(page,2025);observed=await observe(page);assert.equal(observed.locked,2023);assert.match(observed.focus,/2023/);assert.match(observed.tooltip,/2023 · Historis/);
  const legendObservation=observed;
  await page.getByRole('button',{name:'Fokus tahun 2023',exact:true}).focus();await page.getByRole('button',{name:'Fokus tahun 2023',exact:true}).press('Enter');await move(page,2025);assert.equal((await observe(page)).locked,null);
  await page.getByRole('button',{name:'Fokus tahun 2022',exact:true}).focus();await page.getByRole('button',{name:'Fokus tahun 2022',exact:true}).press('Space');await move(page,2025);assert.equal((await observe(page)).locked,2022);
  await page.getByRole('button',{name:'Bandingkan semua',exact:true}).click();await move(page,2025);observed=await observe(page);assert.equal(observed.locked,null);assert.match(observed.focus,/2025/);assert.match(observed.tooltip,/2025 · Historis/);
  await move(page,2024);if(touch)await page.touchscreen.tap(first.clientX,first.clientY);else await page.mouse.click(first.clientX,first.clientY);await move(page,2025);
  const size=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));assert.equal(size.scrollWidth,size.width);
  await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});
  await pause(80);
  await page.screenshot({path:`outputs/development/timeline-pin-${width}.png`,fullPage:true});
  evidence.checks.push({width,touch,first,second,pinned:pinnedObservation,expected_pinned_point:{date:expectedPoint.date,close:expectedPoint.close},second_chart_click:{unlocked,all_series_opacities:allOpacities,next_hover:'Jejak dividen2025'},pointer_leave:'retains2024/clears tooltip',outside_plot_click:'does not pin',keyboard:'Enter toggles2023off; Space locks2022',touch_first_tap:touch?'locks without prior hover; second tap unlocks':'not applicable',legend:legendObservation,reset:observed,size});
}
async function run(){const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});try{for(const width of baseline?[1440]:[1440,390]){const page=await browser.newPage({viewport:{width,height:1000},...(width===390?{hasTouch:true,isMobile:true}:{})});page.setDefaultTimeout(12000);page.on('pageerror',e=>evidence.page_errors.push(e.message));page.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/'))evidence.requests.push({method:r.method(),path:new URL(r.url()).pathname+new URL(r.url()).search});});await verify(page,width,width===390);await page.close();}evidence.status='passed';}catch(e){evidence.status='failed';evidence.failure=e.stack;throw e;}finally{fs.mkdirSync('outputs/development',{recursive:true});fs.writeFileSync(`outputs/development/timeline-pin-${baseline?'baseline':'verification'}.json`,JSON.stringify(evidence,null,2)+'\n');await browser.close();}}
run().catch(e=>{console.error(e);process.exitCode=1;});
