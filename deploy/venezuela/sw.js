const CACHE="cqs-ve-202607021047";
const CORE=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png",
"/files/ferulas/ferula-guia-uso.pdf","/files/ferulas/ferula-identificador.pdf","/files/ferulas/ferula-instrucciones-ostec.pdf"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>Promise.allSettled(CORE.map(u=>c.add(u)))).then(()=>self.skipWaiting()));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
 if(e.request.method!=="GET")return;
 const u=new URL(e.request.url);
 // Map tiles: cache-first (immutable)
 if(/(^|\.)tile\.openstreetmap\.fr$/.test(u.hostname)){ e.respondWith(caches.open(CACHE).then(c=>c.match(e.request).then(r=>r||fetch(e.request).then(resp=>{try{c.put(e.request,resp.clone());}catch(_){}return resp;}).catch(()=>r)))); return; }
 // Live APIs: network-first
 if(/(^|\.)vzla\.api\.ushahidi\.io$/.test(u.hostname)||/(^|\.)api\.fablabs\.io$/.test(u.hostname)){ e.respondWith(fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(CACHE).then(c=>{try{c.put(e.request,cp);}catch(_){}});return resp;}).catch(()=>caches.match(e.request))); return; }
 if(u.origin!==location.origin) return;
 // The page / HTML: NETWORK-FIRST — always fresh online; cached copy only as offline fallback
 if(e.request.mode==="navigate" || u.pathname.endsWith("/") || u.pathname.endsWith("index.html")){
   e.respondWith(fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(CACHE).then(c=>{try{c.put(e.request,cp);}catch(_){}});return resp;}).catch(()=>caches.match(e.request).then(r=>r||caches.match("./index.html"))));
   return;
 }
 // Other same-origin assets: cache-first
 e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(CACHE).then(c=>{try{c.put(e.request,cp);}catch(_){}});return resp;}).catch(()=>caches.match("./index.html"))));
});
