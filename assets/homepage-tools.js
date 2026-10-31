(()=>{"use strict";
const routes=[
{keys:["میلگرد","آجدار","rebar"],url:"/products/rebar/"},
{keys:["تیرآهن","تيرآهن","ipe","beam"],url:"/products/beam/"},
{keys:["پروفیل","قوطی","قوطي","profile"],url:"/products/profile/"},
{keys:["نبشی","نبشي","angle"],url:"/products/angle/"},
{keys:["ناودانی","ناوداني","channel"],url:"/products/channel/"},
{keys:["ورق شیروانی","شیروانی","کرکره","roof"],url:"/products/roofing-sheet/"},
{keys:["ورق پانچ","پانچ","perforated"],url:"/products/perforated-sheet/"},
{keys:["لوله","داربستی","pipe"],url:"/products/scaffolding-pipe/"},
{keys:["ورق","sheet"],url:"/products/sheet/"}
];
document.querySelectorAll(".ae-search-form").forEach(form=>form.addEventListener("submit",event=>{
 event.preventDefault();const field=form.querySelector('input[name="q"]');const q=(field?.value||"").trim();if(!q){field?.focus();return}
 const normalized=q.toLocaleLowerCase("fa");const match=routes.find(item=>item.keys.some(key=>normalized.includes(key)));
 window.location.href=match?match.url:"/products/?q="+encodeURIComponent(q);
}));
const quote=document.getElementById("ae-quick-quote");
if(quote)quote.addEventListener("submit",event=>{
 event.preventDefault();const data=new FormData(quote);
 const product=String(data.get("product")||"").trim();if(!product){quote.querySelector("select")?.focus();return}
 const parts=["سلام، برای آهن ایفل درخواست استعلام قیمت و پیش‌فاکتور دارم.","محصول: "+product];
 if(data.get("spec"))parts.push("سایز/ضخامت/برند: "+data.get("spec"));
 if(data.get("quantity"))parts.push("مقدار: "+data.get("quantity"));
 parts.push("لطفاً قیمت روز، موجودی و هزینه حمل را اعلام کنید.");
 window.open("https://wa.me/989367227775?text="+encodeURIComponent(parts.join("\n")),"_blank","noopener");
});
})();