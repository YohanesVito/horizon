// Real browser/API check. Start local frontend3000/backend8000 first.
// PLAYWRIGHT_MODULE=/tmp/horizon-ui-check/node_modules/playwright node work/verify_simulator_capital.cjs
const fs=require('node:fs');const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base=process.env.UI_BASE_URL || 'http://localhost:3000';
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const evidence={recorded_at:new Date().toISOString(),base,source:'real backend / local Sectors snapshots',checks:[],posts:[],page_errors:[]};
async function read(input){return input.evaluate(e=>({display:e.value,valid:e.checkValidity(),message:e.validationMessage,labelFont:getComputedStyle(e.labels[0]).fontSize,inputFont:getComputedStyle(e).fontSize,inputHeight:e.getBoundingClientRect().height}));}
async function run(){const browser=await chromium.launch({headless:true});try{for(const width of[1440,390]){const page=await browser.newPage({viewport:{width,height:1000}});page.setDefaultTimeout(12000);page.on('pageerror',e=>evidence.page_errors.push(e.message));page.on('request',r=>{if(r.method()==='POST'&&new URL(r.url()).pathname.startsWith('/api/'))evidence.posts.push({path:new URL(r.url()).pathname,body:r.postDataJSON()});});
  await page.goto(base);await page.getByRole('button',{name:'Simulator',exact:true}).click();
  const capital=page.getByLabel('Modal awal (Rp)',{exact:true});const initial=await read(capital);assert.equal(initial.display,'');assert.equal(initial.valid,false);assert.ok(parseFloat(initial.labelFont)>11);assert.ok(parseFloat(initial.inputFont)>12);assert.ok(initial.inputHeight>=52);
  const before=evidence.posts.length;await page.getByRole('button',{name:/Jalankan & bandingkan strategi/}).click();await pause(100);assert.equal(evidence.posts.length,before);
  await page.getByRole('button',{name:/Buka hasil/}).first().click();await page.getByRole('button',{name:'Gunakan input hasil ini',exact:true}).waitFor();
  const oldHistory=await(await page.request.get(base+'/api/simulations')).json();const selectedPrefix=(await page.locator('.run-list button[aria-pressed=true]').getAttribute('aria-label')).match(/Buka hasil (.+)/)[1];const old=oldHistory.find(r=>r.id.startsWith(selectedPrefix));
  await page.getByRole('button',{name:'Gunakan input hasil ini',exact:true}).click();assert.equal(Number((await capital.inputValue()).replaceAll('.','').replace(',','.')),Number(old.input.capital));assert.equal((await read(capital)).valid,true);
  await page.context().grantPermissions(['clipboard-read','clipboard-write']);await page.evaluate(()=>navigator.clipboard.writeText('1e8'));await capital.focus();await capital.press('Meta+A');await capital.press('Meta+V');await pause(60);
  assert.equal((await read(capital)).valid,false);await page.getByRole('button',{name:'Gunakan input hasil ini',exact:true}).click();assert.equal((await read(capital)).valid,true);
  const copy=await read(capital);
  await capital.fill('');await capital.pressSequentially('50000000');assert.equal(await capital.inputValue(),'50.000.000');
  const response=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/simulations'&&r.request().method()==='POST');await page.getByRole('button',{name:/Jalankan & bandingkan strategi/}).click();const created=await(await response).json();let saved;
  for(let i=0;i<80;i++){saved=await(await page.request.get(base+'/api/simulations/'+created.id)).json();if(['completed','failed'].includes(saved.status))break;await pause(100);}
  assert.equal(saved.status,'completed');assert.equal(Number(saved.input.capital),50000000);assert.equal(evidence.posts.at(-1).body.capital,50000000);assert.equal(saved.result.primary.capital,50000000);
  await page.getByRole('button',{name:'Peluang',exact:true}).click();await page.getByRole('button',{name:'Simulator',exact:true}).click();assert.equal(await capital.inputValue(),'');
  await page.getByRole('button',{name:'Peluang',exact:true}).click();await page.getByRole('button',{name:'Buka detail BBCA',exact:true}).click();await page.getByRole('button',{name:/Simulasikan BBCA, ex-date/}).first().click();assert.equal(await capital.inputValue(),'');assert.equal(await page.locator('.event-picker input:checked').count(),1);
  const size=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));assert.equal(size.width,size.scrollWidth);await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});await pause(80);await page.screenshot({path:`outputs/development/simulator-capital-${width}.png`,fullPage:true});
  await page.getByRole('button',{name:'Rencana rotasi',exact:true}).click();const planner=await page.getByLabel('Modal awal (Rp)',{exact:true}).inputValue();assert.equal(planner,'100.000.000');
  await page.getByRole('button',{name:'Intelligence',exact:true}).click();await page.getByRole('button',{name:/Skenario modal/}).click();const scenario=await page.getByLabel('Modal (Rp)',{exact:true}).inputValue();assert.equal(scenario,'100.000.000');
  evidence.checks.push({width,initial,empty_required:'no POST',copied_saved_input:{id:old.id,capital:old.input.capital,observed:copy},run:{id:saved.id,capital:saved.input.capital,status:saved.status,ending_nav:saved.result.primary.ending_nav},fresh_navigation:'empty',detail_handoff:'empty/one BBCA event',defaults:{planner,scenario},size});await page.close();
}evidence.status='passed';}catch(e){evidence.status='failed';evidence.failure=e.stack;throw e;}finally{fs.mkdirSync('outputs/development',{recursive:true});fs.writeFileSync('outputs/development/simulator-capital-verification.json',JSON.stringify(evidence,null,2)+'\n');await browser.close();}}
run().catch(e=>{console.error(e);process.exitCode=1;});
