// Real snapshot backend/browser checks. Run after starting FastAPI8000 + Next3000:
// PLAYWRIGHT_MODULE=/tmp/horizon-ui-check/node_modules/playwright node work/verify_ui_feedback.cjs baseline
const fs = require('node:fs');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.UI_BASE_URL || 'http://127.0.0.1:3000';
const output = 'outputs/development/ui-feedback-verification.json';
const evidence = { recorded_at: new Date().toISOString(), base, source: 'real API / local Sectors snapshots', requests: [], browser_errors: [], browser_console: [], response_errors: [] };
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function run() {
  const browser = await chromium.launch({headless:true, ...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {})});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  page.setDefaultTimeout(12000);
  page.on('request', request => { if(new URL(request.url()).pathname.startsWith('/api/')) evidence.requests.push({method:request.method(),path:new URL(request.url()).pathname + new URL(request.url()).search, ...(request.method()==='POST' ? {body:request.postDataJSON()} : {})}); });
  page.on('pageerror', error => evidence.browser_errors.push(error.message));
  page.on('console',message=>{if(['warning','error'].includes(message.type()))evidence.browser_console.push({type:message.type(),message:message.text(),location:message.location()});});
  page.on('response',response=>{if(response.status()>=400)evidence.response_errors.push({status:response.status(),path:new URL(response.url()).pathname});});
  const count = path => evidence.requests.filter(r=>r.method==='GET' && r.path===path).length;
  try {
    const cacheStarted = Date.now();
    await page.goto(base);
    await page.getByRole('button',{name:'Buka detail BBCA',exact:true}).waitFor();
    await sleep(250);
    const initialBBCA = count('/api/companies/BBCA');
    await page.getByRole('button',{name:'Buka detail BBCA',exact:true}).click();
    await page.getByRole('button',{name:'Tutup detail',exact:true}).click();
    await page.getByRole('button',{name:'Buka detail BBCA',exact:true}).click();
    await sleep(250);
    assert.equal(count('/api/companies/BBCA'), initialBBCA);
    await page.getByRole('button',{name:'Tutup detail',exact:true}).click();
    await page.getByRole('button',{name:'Timeline',exact:true}).click();
    await page.getByRole('button',{name:/Buka pratinjau LPPF/}).click();
    await page.getByRole('button',{name:'Fokus tahun 2025',exact:true}).waitFor();
    const initialTimeline = count('/api/timeline/LPPF?preview=true');
    await page.getByRole('button',{name:'Fokus tahun 2024',exact:true}).click();
    await page.getByRole('button',{name:'Harga Rp',exact:true}).click();
    await page.getByRole('button',{name:'Perubahan %',exact:true}).click();
    await page.getByRole('button',{name:'Fokus tahun 2023',exact:true}).hover();
    await page.locator('svg[aria-label^="Overlay harga LPPF"]').hover({position:{x:400,y:180}});
    await sleep(250);
    assert.equal(count('/api/timeline/LPPF?preview=true'),initialTimeline);
    evidence.cache = {bbca:{initial:initialBBCA,after_two_detail_opens:count('/api/companies/BBCA')},timeline:{initial:initialTimeline,after_year_currency_hover:count('/api/timeline/LPPF?preview=true')},checked_controls:['year focus','Rp/%','hover'],elapsed_ms:Date.now()-cacheStarted,existing_stale_time_ms:60000,timeframe_zoom:'not implemented / not tested'};
    if(process.argv[2] !== 'baseline') await verifyForms(page, evidence);
    evidence.status='passed';
  } catch(error) { evidence.status='failed'; evidence.failure=error.stack; throw error; }
  finally { fs.mkdirSync('outputs/development',{recursive:true});fs.writeFileSync(output,JSON.stringify(evidence,null,2)+'\n');await browser.close(); }
}
async function verifyForms(page,evidence) {
  const read = input => input.evaluate(e=>({display:e.value,valid:e.checkValidity(),message:e.validationMessage,caret:e.selectionStart}));
  const postCount = path => evidence.requests.filter(r=>r.method==='POST' && r.path===path).length;
  async function paste(input,text) {
    await page.context().grantPermissions(['clipboard-read','clipboard-write']);
    await page.evaluate(text=>navigator.clipboard.writeText(text),text);
    await input.focus();await input.press('Meta+A');await input.press('Meta+V');await sleep(70);
  }
  async function submit(button,path) {
    const response = page.waitForResponse(r=>new URL(r.url()).pathname===path && r.request().method()==='POST');
    await button.click();const res=await response;assert.equal(res.status(),path==='/api/simulations'?202:201);return res.json();
  }
  await page.getByRole('button',{name:'Simulator',exact:true}).click();
  const capital = page.getByLabel('Modal awal (Rp)',{exact:true});
  const runButton = page.getByRole('button',{name:/Jalankan & bandingkan strategi/});
  await capital.fill('');await capital.pressSequentially('100000000');
  assert.equal(await capital.inputValue(),'100.000.000');
  const edit=[];
  await capital.fill('1.234.567');await capital.evaluate(e=>e.setSelectionRange(3,3));await capital.pressSequentially('9');
  edit.push(await read(capital));assert.equal(await capital.inputValue(),'12.934.567');assert.equal(edit.at(-1).caret,4);
  await capital.press('Backspace');assert.equal(await capital.inputValue(),'1.234.567');edit.push(await read(capital));
  await capital.evaluate(e=>e.setSelectionRange(2,2));await capital.press('Backspace');assert.equal(await capital.inputValue(),'234.567');edit.push(await read(capital));
  const invalid=[];
  for(const value of ['', '0', '1.000.000.000.001', '1,5', 'abc']) {
    await capital.fill(value);const observed=await read(capital);assert.equal(observed.valid,false);
    const before=postCount('/api/simulations');await runButton.click();await sleep(80);assert.equal(postCount('/api/simulations'),before);invalid.push({input:value,...observed});
  }
  await capital.fill('100.000.000');await paste(capital,'1e8');
  assert.equal((await read(capital)).valid,false);assert.equal(await capital.inputValue(),'100.000.000');
  await capital.press('ArrowRight');await capital.press('Backspace');assert.equal((await read(capital)).valid,true);
  await paste(capital,'50.000.000');assert.equal(await capital.inputValue(),'50.000.000');assert.equal(await page.locator('input[type=hidden][name=capital]').inputValue(),'50000000');
  const radios=page.locator('input[type=radio][name=allocation]');assert.equal(await radios.count(),3);
  await radios.nth(0).focus();await radios.nth(0).press('Space');assert.equal(await radios.nth(0).isChecked(),true);
  await radios.nth(0).press('ArrowRight');assert.equal(await radios.nth(1).isChecked(),true);
  await radios.nth(1).press('ArrowRight');assert.equal(await radios.nth(2).isChecked(),true);
  const simulations=[];
  for(const mode of ['single','equal','rotation']) {
    await page.locator(`input[name=allocation][value=${mode}]`).check();
    const created=await submit(runButton,'/api/simulations');
    let saved;
    for(let attempt=0;attempt<80;attempt++) { saved=await (await page.request.get(`${base}/api/simulations/${created.id}`)).json();if(['completed','failed'].includes(saved.status))break;await sleep(100); }
    assert.equal(saved.status,'completed');assert.equal(saved.input.allocation,mode);assert.equal(Number(saved.input.capital),50000000);assert.equal(saved.input.compare,true);assert.equal(saved.result.primary.allocation,mode);assert.equal(saved.result.alternatives.length,3);
    simulations.push({id:saved.id,input:saved.input,primary:saved.result.primary.allocation,alternatives:saved.result.alternatives.map(r=>r.allocation),return_pct:saved.result.primary.return_pct,ending_nav:saved.result.primary.ending_nav});
    await page.getByRole('button',{name:'Gunakan input hasil ini',exact:true}).waitFor();
  }
  await capital.fill('123');await page.getByRole('button',{name:'Gunakan input hasil ini',exact:true}).click();assert.equal(await capital.inputValue(),'50.000.000');assert.equal(await page.locator('input[type=hidden][name=capital]').inputValue(),'50000000');
  await paste(capital,'1e8');assert.equal((await read(capital)).valid,false);
  await page.getByRole('button',{name:'Gunakan input hasil ini',exact:true}).click();
  const copyRecovery=await read(capital);
  evidence.copy_recovery=copyRecovery;
  assert.equal(copyRecovery.valid,true,'Copying saved input must clear invalid paste at unchanged numeric value');
  evidence.simulator={typed_raw:'100000000 → 100.000.000',paste:'50.000.000 → 50000000',invalid,editing:edit,keyboard_radio:'Space / ArrowRight selects single→equal→rotation',simulations,copy_saved_capital:'123 → 50.000.000'};
  await page.getByRole('button',{name:'Rencana rotasi',exact:true}).click();
  const plannerCapital=page.getByLabel('Modal awal (Rp)',{exact:true});await paste(plannerCapital,'50.000.000');
  const plan=await submit(page.getByRole('button',{name:/Susun kandidat rute/}),'/api/rotation-plans');assert.equal(Number(plan.input.capital),50000000);
  const persistedPlan=await(await page.request.get(`${base}/api/rotation-plans/${plan.id}`)).json();assert.equal(persistedPlan.input.capital,plan.input.capital);
  evidence.planner={id:plan.id,display:await plannerCapital.inputValue(),capital:plan.input.capital,candidates:plan.candidates.length};
  await page.getByRole('button',{name:'Intelligence',exact:true}).click();await page.getByRole('button',{name:/Skenario modal/}).click();
  const scenarioCapital=page.getByLabel('Modal (Rp)',{exact:true});await paste(scenarioCapital,'50.000.000,25');
  const entry=page.getByLabel('Asumsi harga entry (Rp)',{exact:true});await entry.fill('10.000,5');
  const dps=page.getByLabel('Asumsi DPS (Rp)',{exact:true});await dps.fill('0,125');
  const scenario=await submit(page.getByRole('button',{name:/Hitung skenario/}),'/api/scenarios');
  assert.equal(Number(scenario.input.capital),50000000.25);assert.equal(Number(scenario.input.entry_price),10000.5);assert.equal(Number(scenario.input.dps),0.125);
  const scenarioHistory=await(await page.request.get(`${base}/api/scenarios`)).json();assert.ok(scenarioHistory.some(r=>r.id===scenario.id && r.input.dps===scenario.input.dps));
  evidence.scenario={id:scenario.id,display:{capital:await scenarioCapital.inputValue(),entry:await entry.inputValue(),dps:await dps.inputValue()},input:scenario.input};
  evidence.responsive=[];
  for(const width of [1440,390]) {
    await page.setViewportSize({width,height:1000});
    for(const view of ['Simulator','Rencana rotasi','Intelligence']) {
      await page.getByRole('button',{name:view,exact:true}).click();await sleep(150);
      const size=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));assert.ok(size.scrollWidth<=size.width);evidence.responsive.push({view,...size});
      if(view==='Simulator') { const selected=page.locator('.strategy-card.selected');assert.equal(await selected.count(),1); }
      if(view==='Simulator') await page.screenshot({path:`outputs/development/ui-feedback-simulator-${width}.png`,fullPage:true});
    }
  }
}
run().catch(error=>{console.error(error);process.exitCode=1;});
