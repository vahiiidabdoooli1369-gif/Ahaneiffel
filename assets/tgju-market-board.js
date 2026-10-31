(function(){
  "use strict";
  const host=document.querySelector(".visual-hero");
  if(!host || document.getElementById("ae-tgju-board")) return;
  const section=document.createElement("section");
  section.id="ae-tgju-board";
  section.className="ae-tgju-board wide";
  section.setAttribute("aria-label","تابلوی قیمت بازار ارز و فلزات");
  section.innerHTML='<div class="ae-tgju-head"><div><span>نبض بازار</span><h2>تابلوی آنلاین دلار و فلزات پایه</h2></div><small class="ae-tgju-time">در حال دریافت نرخ‌ها…</small></div><div class="ae-tgju-grid"><article class="ae-tgju-item"><span>دلار آزاد</span><strong data-tgju="usd_irr">—</strong><small>تومان</small></article><article class="ae-tgju-item"><span>آلومینیوم جهانی</span><strong data-tgju="aluminum">—</strong><small>دلار به ازای هر تن</small></article></div><p class="ae-tgju-note">منبع: TGJU · نرخ‌ها ممکن است با تأخیر باشند و قیمت قطعی فروش آهن‌آلات محسوب نمی‌شوند.</p>';
  host.insertAdjacentElement("afterend",section);
  const style=document.createElement("style");
  style.textContent='#ae-tgju-board{max-width:1200px;margin:24px auto;padding:22px;background:#102b46;color:#fff;border-radius:18px;box-sizing:border-box}#ae-tgju-board .ae-tgju-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}#ae-tgju-board .ae-tgju-head span{color:#ff851b;font-size:13px;font-weight:800}#ae-tgju-board h2{font-size:clamp(18px,3vw,24px);margin:5px 0 14px;color:#fff}#ae-tgju-board small{color:#c9d6e3}#ae-tgju-board .ae-tgju-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}#ae-tgju-board .ae-tgju-item{background:#17466b;border:1px solid #41617d;border-radius:13px;padding:16px;display:flex;flex-direction:column;gap:7px;min-width:0}#ae-tgju-board .ae-tgju-item span{font-size:14px;color:#e8f0f7}#ae-tgju-board .ae-tgju-item strong{font-size:clamp(22px,4vw,30px);overflow-wrap:anywhere;color:#fff}#ae-tgju-board .ae-tgju-note{font-size:12px;line-height:1.9;color:#d2deea;margin:12px 0 0}@media(max-width:520px){#ae-tgju-board{margin:16px 12px;padding:16px}#ae-tgju-board .ae-tgju-grid{grid-template-columns:1fr}}';
  document.head.appendChild(style);
  const fmt=n=>new Intl.NumberFormat("fa-IR",{maximumFractionDigits:2}).format(Number(n));
  fetch("/data/tgju-market.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("feed unavailable");return r.json()}).then(data=>{
    (data.items||[]).forEach(item=>{const el=section.querySelector('[data-tgju="'+item.id+'"]');if(el)el.textContent=fmt(item.value)});
    const time=new Date(data.updated_at_utc);
    section.querySelector(".ae-tgju-time").textContent="آخرین دریافت: "+(isNaN(time)?"نامشخص":time.toLocaleString("fa-IR",{timeZone:"Asia/Tehran"}));
  }).catch(()=>{section.querySelector(".ae-tgju-time").textContent="دریافت نرخ موقتاً ناموفق بود";});
})();