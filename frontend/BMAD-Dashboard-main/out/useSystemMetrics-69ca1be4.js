import{c as h,r as o}from"./index-156284ae.js";/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const k=h("TrendingUp",[["polyline",{points:"22 7 13.5 15.5 8.5 10.5 2 17",key:"126l90"}],["polyline",{points:"16 7 22 7 22 13",key:"kwv8wd"}]]);/**
 * @license lucide-react v0.294.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const g=h("Wifi",[["path",{d:"M5 13a10 10 0 0 1 14 0",key:"6v8j51"}],["path",{d:"M8.5 16.5a5 5 0 0 1 7 0",key:"sej527"}],["path",{d:"M2 8.82a15 15 0 0 1 20 0",key:"dnpr2z"}],["line",{x1:"12",x2:"12.01",y1:"20",y2:"20",key:"of4bc4"}]]),f="/api",w=5e3,d=async(m,a={},p=w)=>{const n=new AbortController,c=setTimeout(()=>n.abort(),p);try{const r=await fetch(m,{...a,signal:n.signal});return clearTimeout(c),r}catch(r){throw clearTimeout(c),r instanceof Error&&r.name==="AbortError"?new Error("Request timeout - server niet bereikbaar"):r}},E=()=>{const[m,a]=o.useState(null),[p,n]=o.useState(!0),[c,r]=o.useState(null),[i,y]=o.useState(0),l=o.useCallback(async()=>{const u=Date.now();try{n(!0),r(null);const e=await d(`${f}/metrics`,{method:"GET",headers:{"Content-Type":"application/json"}},w);if(!e.ok){const s=await e.text().catch(()=>"Unknown error");throw new Error(`Server error: ${e.status} - ${s}`)}const t=await e.json();if(t&&t.metrics&&t.metrics.system_health){a(t.metrics),y(0);const s=Date.now()-u;s>500&&console.warn(`⚠️ Slow API Response: SystemMetrics took ${s}ms`)}else throw console.warn("Invalid metrics response structure:",t),new Error("Ongeldige data van server ontvangen")}catch(e){const t=e instanceof Error?e.message:"Verbinding met server mislukt";r(t),console.error("Error fetching system metrics:",e),y(s=>s+1),a(null)}finally{n(!1)}},[]);return o.useEffect(()=>{l();const u=15e3,e=Math.min(Math.pow(2,i),8),t=i>0?u*e:u,s=setTimeout(l,t);return()=>clearTimeout(s)},[l,i]),{metrics:m,loading:p,error:c,retryCount:i,fetchMetrics:l}};export{k as T,g as W,E as u};
//# sourceMappingURL=useSystemMetrics-69ca1be4.js.map
