const CACHE='doombot-v20-2-2-no-connection-banner-theory-restore-1';
self.addEventListener('install',e=>e.waitUntil(self.skipWaiting()));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 if(e.request.method!=='GET')return;
 const u=new URL(e.request.url); if(u.origin!==self.location.origin)return;
 if(e.request.mode==='navigate'||/\.(?:html|css|js|json)$/.test(u.pathname)){
  e.respondWith(fetch(e.request,{cache:'no-store'}).catch(()=>caches.match(e.request,{ignoreSearch:true})));
 }
});