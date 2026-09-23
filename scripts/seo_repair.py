import json,re,os
from pathlib import Path
from html import escape

# Prevent an infinite push -> repair -> push loop.
try:
    event=json.load(open(os.environ.get("GITHUB_EVENT_PATH",""),encoding="utf-8"))
    if "[seo-auto-repair]" in event.get("head_commit",{}).get("message",""):
        print("Repair commit detected; nothing to do.")
        raise SystemExit(0)
except (FileNotFoundError,TypeError,json.JSONDecodeError):
    pass

ROOT=Path("."); DOMAIN="https://ahaneiffel.top"

def noindex(s):
    m=re.search(r'<meta\\b[^>]*\\bname=["\']robots["\'][^>]*\\bcontent=["\']([^"\']*)',s,re.I)
    return bool(m and "noindex" in m.group(1).lower())

def url(p):
    r=p.as_posix()
    if r=="index.html": return DOMAIN+"/"
    if r.endswith("/index.html"): return DOMAIN+"/"+r[:-10].rstrip("/")+"/"
    return DOMAIN+"/"+r

desc={
"base-plate/index.html":"راهنمای بیس پلیت فولادی؛ بررسی ابعاد، ضخامت، کاربرد و نکات سفارش و خرید از آهن ایفل.",
"scaffolding-pipe/index.html":"قیمت و مشخصات لوله داربستی؛ بررسی ضخامت، طول، وزن، کاربرد و نکات خرید از آهن ایفل.",
"profile/index.html":"راهنمای قوطی و پروفیل؛ بررسی ابعاد، ضخامت، وزن، کاربرد، برند و قیمت روز از آهن ایفل.",
"angle/index.html":"راهنمای نبشی آهن؛ بررسی سایز، ضخامت، وزن، کاربرد، برند و نکات خرید از آهن ایفل.",
"roofing-sheet/index.html":"راهنمای ورق شیروانی؛ بررسی انواع، ضخامت، پوشش، کاربرد و نکات خرید با قیمت روز.",
"formwork-strip/index.html":"راهنمای تسمه قالب بندی؛ بررسی ابعاد، ضخامت، کاربرد، وزن و نکات انتخاب و خرید.",
"perforated-sheet/index.html":"راهنمای ورق پانچ؛ بررسی انواع سوراخ، ابعاد، ضخامت، کاربرد و نکات خرید.",
"beam/index.html":"راهنمای تیرآهن؛ بررسی سایز، استاندارد، وزن، برند، کاربرد و نکات خرید و استعلام قیمت.",
"sheet/index.html":"راهنمای ورق فولادی؛ بررسی انواع، ضخامت، ابعاد، وزن، کاربرد و نکات خرید.",
"channel/index.html":"راهنمای ناودانی؛ بررسی سایز، استاندارد، وزن، کاربرد و نکات خرید و استعلام قیمت.",
"tools/steel-quality-check/index.html":"ابزار بررسی کیفیت آهن آلات برای کنترل مشخصات، ابعاد، وزن و مدارک پیش از خرید و تحویل.",
"tools/steel-tools/index.html":"مجموعه ابزارهای آهن و فولاد برای محاسبه وزن، مقایسه مقاطع و آماده سازی استعلام خرید.",
"tools/sheet-weight-calculator/index.html":"محاسبه وزن ورق فولادی بر اساس ابعاد و ضخامت؛ ابزار آنلاین آهن ایفل برای برآورد سریع وزن.",
"reference/steel-transport-checklist/index.html":"چک لیست حمل آهن آلات؛ کنترل بار، اسناد، وزن، بسته بندی و تحویل برای کاهش خطا.",
"reference/steel-brand-guide/index.html":"راهنمای انتخاب برند و کارخانه فولادی؛ معیارهای کیفیت، استاندارد، قیمت و استعلام خرید.",
"local/tehran/neighborhoods/afsarieh/index.html":"راهنمای خرید و استعلام آهن آلات در افسریه تهران؛ قیمت روز، تأمین و هماهنگی ارسال از آهن ایفل.",
"local/tehran-province/shahr-e-ghods/index.html":"راهنمای خرید آهن آلات در شهر قدس؛ استعلام قیمت، انتخاب مقطع، تأمین و ارسال سفارش.",
"guides/sheet-weight/index.html":"راهنمای وزن ورق آهن؛ روش محاسبه وزن بر اساس ضخامت، ابعاد و چگالی فولاد.",
"guides/sheet-weight-calculator/index.html":"راهنمای محاسبه وزن ورق؛ فرمول و روش برآورد وزن ورق های فولادی برای خرید و سفارش."
}
h1={
"base-plate/index.html":"راهنمای خرید و انتخاب بیس پلیت","scaffolding-pipe/index.html":"راهنمای خرید لوله داربستی",
"profile/index.html":"قوطی و پروفیل؛ مشخصات، وزن و قیمت روز","angle/index.html":"نبشی آهن؛ مشخصات، وزن و قیمت روز",
"roofing-sheet/index.html":"ورق شیروانی؛ انواع، مشخصات و قیمت روز","formwork-strip/index.html":"تسمه قالب بندی؛ مشخصات و راهنمای خرید",
"perforated-sheet/index.html":"ورق پانچ؛ انواع، مشخصات و راهنمای خرید","beam/index.html":"تیرآهن؛ مشخصات، وزن و راهنمای خرید",
"sheet/index.html":"ورق فولادی؛ انواع، مشخصات و راهنمای خرید","rebar/index.html":"میلگرد؛ مشخصات، وزن و راهنمای خرید",
"channel/index.html":"ناودانی؛ مشخصات، وزن و راهنمای خرید","tools/steel-quality-check/index.html":"ابزار بررسی کیفیت آهن آلات",
"tools/steel-tools/index.html":"ابزارهای تخصصی آهن و فولاد","tools/sheet-weight-calculator/index.html":"محاسبه وزن ورق فولادی",
"reference/steel-transport-checklist/index.html":"چک لیست حمل و تحویل آهن آلات","reference/steel-brand-guide/index.html":"راهنمای انتخاب برند و کارخانه فولادی",
"local/tehran/neighborhoods/afsarieh/index.html":"خرید آهن آلات در افسریه تهران","local/tehran-province/shahr-e-ghods/index.html":"خرید آهن آلات در شهر قدس",
"guides/sheet-weight/index.html":"راهنمای وزن ورق آهن","guides/sheet-weight-calculator/index.html":"راهنمای محاسبه وزن ورق",
"products/angle/angle-40x40.html":"نبشی 40×40؛ مشخصات، وزن و کاربرد"
}

changed=[]
for p in ROOT.rglob("*.html"):
    if ".git" in p.parts or p.as_posix().startswith(".github/"): continue
    s=p.read_text(encoding="utf-8",errors="ignore"); old=s
    if p.name!="404.html" and not noindex(s):
        if not re.search(r'<meta\\b[^>]*\\bname=["\']viewport["\']',s,re.I):
            s=re.sub(r'(<meta\\s+charset=["\'][^>]+>\\s*)',r'\\1<meta name="viewport" content="width=device-width, initial-scale=1">',s,count=1,flags=re.I)
        if not re.search(r'<link\\b[^>]*\\brel=["\']canonical["\']',s,re.I):
            s=re.sub(r'</head>',f'<link rel="canonical" href="{url(p)}"></head>',s,count=1,flags=re.I)
    k=p.as_posix()
    if k in desc and not noindex(s) and not re.search(r'<meta\\b[^>]*\\bname=["\']description["\']',s,re.I):
        s=re.sub(r'(<meta\\s+charset=["\'][^>]+>\\s*)',r'\\1<meta name="description" content="'+escape(desc[k],quote=True)+'">',s,count=1,flags=re.I)
    if k in h1 and not noindex(s) and not re.search(r'<h1\\b[^>]*>\\s*[^<]+',s,re.I):
        tag="<h1>"+h1[k]+"</h1>"
        if re.search(r'<main\\b[^>]*>',s,re.I): s=re.sub(r'(<main\\b[^>]*>)',r'\\1'+tag,s,count=1,flags=re.I)
        else: s=re.sub(r'(<body\\b[^>]*>)',r'\\1'+tag,s,count=1,flags=re.I)
    if s!=old: p.write_text(s,encoding="utf-8"); changed.append(k)

# Fix the 13 previously confirmed broken internal references.
reps={
"knowledge/steel-price-data-methodology/":{"../prices/":"/prices/","../tools/steel-comparison/":"/tools/steel-comparison/"},
"knowledge/steel-mill-certificate/":{"../buy-iron/":"/buy-iron/","../knowledge/steel/steel-delivery-document-check":"/knowledge/steel/steel-delivery-document-check/"},
"knowledge/steel-delivery-acceptance/":{"../guides/steel-delivery-checklist/":"/guides/steel-delivery-checklist/","../buy-iron/":"/buy-iron/"},
"knowledge/steel-weight-tolerance/":{"../tools/steel-weight-calculator/":"/tools/steel-weight-calculator/","../products/":"/products/"},
"reference/":{"../knowledge/steel-standards-vs-grades/":"/knowledge/steel-standards-vs-grades/"}
}
for prefix,mp in reps.items():
    for p in ROOT.rglob("*.html"):
        if not p.as_posix().startswith(prefix): continue
        s=p.read_text(encoding="utf-8",errors="ignore"); old=s
        for a,b in mp.items():
            t=ROOT/b.lstrip("/")
            if t.is_dir(): t=t/"index.html"
            if t.exists(): s=s.replace(a,b)
        if s!=old: p.write_text(s,encoding="utf-8"); changed.append(p.as_posix())

for p in [ROOT/"products/rebar/8/index.html",ROOT/"products/rebar/16/index.html",ROOT/"products/rebar/25/index.html"]:
    if p.exists():
        s=p.read_text(encoding="utf-8",errors="ignore"); old=s
        t=ROOT/"guides/rebar-weight-table/index.html"
        if t.exists(): s=s.replace("/guides/rebar-weight-table/","/guides/rebar-weight-table/")
        if s!=old: p.write_text(s,encoding="utf-8"); changed.append(p.as_posix())

print("SEO repair changed",len(set(changed)),"files")
