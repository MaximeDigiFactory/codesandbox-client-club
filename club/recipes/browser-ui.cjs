const{chromium,firefox,webkit}=require('/browser/node_modules/playwright');const fs=require('fs');let raw='';process.stdin.on('data',d=>raw+=d);process.stdin.on('end',async()=>{
 const a=JSON.parse(raw),all=[];
 for(const [engine,launcher]of Object.entries({chromium,firefox,webkit})){
  const row={engine,scope:'Actual dc10 production UI, local TLS test relay; domain blocking simulation, not a browser extension',requests:[],errors:[],files:[]};let b;
  try{
   b=await launcher.launch({headless:true,timeout:15000,args:engine==='chromium'&&!a.public?['--ignore-certificate-errors']:[]});const c=await b.newContext({ignoreHTTPSErrors:!a.public,acceptDownloads:true});c.setDefaultTimeout(6000);if(engine==='chromium'&&!a.public){try{await c.grantPermissions(['local-network-access'],{origin:'https://librechat.digiconseil.fr'})}catch(e){row.errors.push('Test fixture permission: '+e.message.slice(0,120))}}
   await c.route('**/api/auth/refresh',r=>r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({token:a.token,user:a.user})}));
   if(!a.public)await c.route('**/api/config',async r=>{const x=await r.fetch(),j=await x.json();j.bundlerURL='https://artefacts.digiconseil.fr';j.staticBundlerURL='https://preview.artefacts.digiconseil.fr';await r.fulfill({response:x,json:j})});
   await c.route(/.*(?:codesandbox\.io|csbops\.io|doubleclick\.net|googlesyndication\.com).*/,r=>r.abort('blockedbyclient'));
   const p=await c.newPage();p.on('requestfailed',r=>{try{const u=new URL(r.url());row.errors.push(u.hostname+u.pathname+' '+r.failure()?.errorText)}catch{}});p.on('request',r=>{const u=new URL(r.url());if(['http:','https:'].includes(u.protocol))row.requests.push({host:u.hostname,path:u.pathname})});p.on('pageerror',e=>row.errors.push(e.message.slice(0,250)));p.on('console',m=>{if(m.type()==='error')row.errors.push(m.text().slice(0,250))});
   await p.goto('https://librechat.digiconseil.fr/c/'+a.conversationId);await p.waitForTimeout(4000);row.page=new URL(p.url()).pathname;row.fileButtons=(await p.locator('button').allTextContents()).filter(s=>/bilan\./.test(s));
   for(const file of a.files){
    const f={filename:file.filename};let btn=p.locator('[data-artifact-trigger]').filter({hasText:file.filename}).first();f.nativeCardCount=await p.locator('[data-artifact-trigger]').filter({hasText:file.filename}).count();
    if(f.nativeCardCount){await btn.click();await p.waitForTimeout(4000);f.frames=p.frames().map(fr=>{try{const u=new URL(fr.url());return{host:u.hostname,path:u.pathname}}catch{return{path:fr.url()}}});f.renderedText=[];
     for(const fr of p.frames()){if(fr.url().includes('.artefacts.digiconseil.fr')&&!fr.url().includes('__csb_relay')){try{f.renderedText.push((await fr.locator('body').innerText()).slice(0,1200));f.generatedCSP=await fr.evaluate(async()=>{const r=await fetch(location.href);return r.headers.get('Content-Security-Policy')})}catch(e){f.previewError=e.name}}}
     f.timeoutText=await p.getByText(/Couldn't connect to server|static environment timeout/).count();f.downloadControls=await p.locator('button').evaluateAll(bs=>bs.map(b=>({title:b.getAttribute('title'),aria:b.getAttribute('aria-label'),text:b.innerText})).filter(x=>/download|télécharger/i.test(JSON.stringify(x))));
     const dl=p.getByRole('button',{name:'Download Artifact',exact:true});if(await dl.count()){try{const event=p.waitForEvent('download',{timeout:12000});await dl.click();const d=await event,data=fs.readFileSync(await d.path());f.download={filename:d.suggestedFilename(),bytes:data.length,sha256:require('crypto').createHash('sha256').update(data).digest('hex')};}catch(e){f.downloadError=e.name}}
    }else if(file.filename.endsWith('.pdf')){f.pdfPanelNative=false;const card=p.locator('button').filter({hasText:file.filename}).first();f.nativeFileCardCount=await p.locator('button').filter({hasText:file.filename}).count();if(f.nativeFileCardCount){try{const event=p.waitForEvent('download',{timeout:10000});await card.click();const d=await event,data=fs.readFileSync(await d.path());f.download={filename:d.suggestedFilename(),bytes:data.length,sha256:require('crypto').createHash('sha256').update(data).digest('hex')};}catch(e){f.downloadError=e.name}}}row.files.push(f);console.log(engine,file.filename,'cards',f.nativeCardCount,'frames',f.renderedText?.length,'timeout',f.timeoutText,'download',f.download?.filename||f.downloadError||'none')
   }
   row.codeSandboxRequests=row.requests.filter(x=>/(?:codesandbox\.io|csbops\.io)$/.test(x.host));console.log(engine,'external CodeSandbox requests',row.codeSandboxRequests.length);await c.close()
  }catch(e){row.failure=e.message.slice(0,400);console.log(engine,'failure',row.failure)}finally{if(b)await b.close()}
  all.push(row);fs.writeFileSync('/evidence/BROWSER-PREVIEW-LOCAL.json',JSON.stringify(all,null,2));
 }
 console.log('Saved sanitized network capture without tokens or headers');
});
