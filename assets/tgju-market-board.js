(function(){
  "use strict";
  if(document.getElementById("ae-tgju-ticker")) return;
  const footer=document.querySelector("footer");
  if(!footer) return;
  const bar=document.createElement("section");
  bar.id="ae-tgju-ticker";
  bar.setAttribute("aria-label","نوار قیمت آنلاین دلار و فلزات");
  bar.innerHTML='<div class="ae-ticker-label"><span class="ae-live-dot"></span>نبض بازار</div><div class="ae-ticker-window"><div class="ae-ticker-track"><span class="ae-ticker-loading">در حال دریافت قیمت‌های بازار…</span></div></div><a class="ae-ticker-source" href="https://www.tgju.org/" target="_blank" rel="noopener noreferrer">منبع: TGJU</a>';
  footer.parentNode.insertBefore(bar,footer);
  const style=document.createElement("style");
  style.textContent='#ae-tgju-ticker{direction:rtl;width:100%;min-height:54px;display:flex;align-items:center;gap:16px;box-sizing:border-box;padding:9px max(14px,calc((100% - 1200px)/2));background:#102b46;color:#fff;border-top:3px solid #ff851b;overflow:hidden;font-family:inherit;position:relative;z-index:20}#ae-tgju-ticker .ae-ticker-label{white-space:nowrap;font-weight:800;color:#ffb15f;display:flex;align-items:center;gap:8px;font-size:13px}#ae-tgju-ticker .ae-live-dot{width:8px;height:8px;background:#36d399;border-radius:50%;box-shadow:0 0 0 4px #36d39925}#ae-tgju-ticker .ae-ticker-window{flex:1;min-width:0;overflow:hidden}#ae-tgju-ticker .ae-ticker-track{display:flex;align-items:center;gap:34px;width:max-content;white-space:nowrap;animation:aeTickerMove 28s linear infinite}#ae-tgju-ticker:hover .ae-ticker-track{animation-play-state:paused}#ae-tgju-ticker .ae-ticker-entry{font-size:13px;color:#e5edf5;display:inline-flex;align-items:center;gap:8px}#ae-tgju-ticker .ae-ticker-entry b{color:#fff;font-size:14px}#ae-tgju-ticker .ae-ticker-entry i{font-style:normal;color:#ffad55;font-size:11px}#ae-tgju-ticker .ae-ticker-sep{color:#ff851b}#ae-tgju-ticker .ae-ticker-source{white-space:nowrap;color:#c5d5e4;text-decoration:none;font-size:11px;border-right:1px solid #49627a;padding-right:12px}#ae-tgju-ticker .ae-ticker-source:hover{color:#ffb15f}@keyframes aeTickerMove{from{transform:translateX(0)}to{transform:translateX(50%)}}@media(max-width:600px){#ae-tgju-ticker{gap:10px;padding:10px 12px;min-height:50px}#ae-tgju-ticker .ae-ticker-label{font-size:11px}#ae-tgju-ticker .ae-ticker-source{font-size:10px;padding-right:8px}#ae-tgju-ticker .ae-ticker-track{gap:22px;animation-duration:22s}}@media(prefers-reduced-motion:reduce){#ae-tgju-ticker .ae-ticker-track{animation:none;transform:none}}';
  document.head.appendChild(style);
  const number=n=>new Intl.NumberFormat("fa-IR",{maximumFractionDigits:2}).format(Number(n));
  fetch("/data/tgju-market.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("feed unavailable");return r.json()}).then(data=>{
    const items=(data.items||[]).filter(x=>Number.isFinite(Number(x.value)));
    const track=bar.querySelector(".ae-ticker-track");
    if(!items.length){track.textContent="قیمت‌ها پس از دریافت معتبر از منبع نمایش داده می‌شوند.";return;}
    const entries=items.map(x=>'<span class="ae-ticker-entry"><span class="ae-ticker-sep">◆</span>'+x.name+' <b>'+number(x.value)+'</b><i>'+x.unit+'</i></span>').join("");
    track.innerHTML=entries+entries;
    const stamp=data.updated_at_utc?new Date(data.updated_at_utc):null;
    if(stamp&&!isNaN(stamp)) bar.setAttribute("aria-label","نوار قیمت آنلاین؛ آخرین دریافت "+stamp.toLocaleString("fa-IR",{timeZone:"Asia/Tehran"}));
  }).catch(()=>{bar.querySelector(".ae-ticker-track").textContent="دریافت قیمت بازار موقتاً در دسترس نیست.";});
})();