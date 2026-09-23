import json,re,os
from pathlib import Path
from html import escape

try:
    with open(os.environ.get("GITHUB_EVENT_PATH",""),encoding="utf-8") as f:
        event=json.load(f)
    if "[seo-auto-repair]" in event.get("head_commit",{}).get("message",""):
        raise SystemExit(0)
except (FileNotFoundError,TypeError,json.JSONDecodeError):
    pass

ROOT=Path("."); DOMAIN="https://ahaneiffel.top"
CANON_RE=r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>'

def noindex(s):
    m=re.search(r'<meta\b[^>]*\bname=["\']robots["\'][^>]*\bcontent=["\']([^"\']*)',s,re.I)
    return bool(m and "noindex" in m.group(1).lower())

def page_url(p):
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
    tags=re.findall(CANON_RE,s,re.I)
    if len(tags)>1:
        preferred=tags[0]
        s=re.sub(CANON_RE,"",s,flags=re.I)
        s=re.sub(r'</head>',preferred+'</head>',s,count=1,flags=re.I)
    elif len(tags)==0 and p.name!="404.html" and not noindex(s):
        s=re.sub(r'</head>',f'<link rel="canonical" href="{page_url(p)}"></head>',s,count=1,flags=re.I)
    if p.name!="404.html" and not noindex(s):
        if not re.search(r'<meta\b[^>]*\bname=["\']viewport["\']',s,re.I):
            s=re.sub(r'(<meta\s+charset=["\'][^>]+>\s*)',r'\1<meta name="viewport" content="width=device-width, initial-scale=1">',s,count=1,flags=re.I)
    k=p.as_posix()
    if k in desc and not noindex(s) and not re.search(r'<meta\b[^>]*\bname=["\']description["\']',s,re.I):
        tag=f'<meta name="description" content="{escape(desc[k],quote=True)}">'
        s=re.sub(r'(<meta\s+charset=["\'][^>]+>\s*)',r'\1'+tag,s,count=1,flags=re.I)
    if k in h1 and not noindex(s) and not re.search(r'<h1\b[^>]*>\s*[^<]+',s,re.I):
        tag=f'<h1>{h1[k]}</h1>'
        if re.search(r'<main\b[^>]*>',s,re.I): s=re.sub(r'(<main\b[^>]*>)',r'\1'+tag,s,count=1,flags=re.I)
        else: s=re.sub(r'(<body\b[^>]*>)',r'\1'+tag,s,count=1,flags=re.I)
    if s!=old:
        p.write_text(s,encoding="utf-8"); changed.append(k)

replacements={
"reference/":{"../knowledge/steel-standards-vs-grades/":"/knowledge/steel-standards-vs-grades/"},
"knowledge/steel-price-data-methodology/":{"../prices/":"/prices/","../tools/steel-comparison/":"/tools/steel-comparison/"},
"knowledge/steel-mill-certificate/":{"../buy-iron/":"/buy-iron/","../knowledge/steel/steel-delivery-document-check":"/knowledge/steel/steel-delivery-document-check/"},
"knowledge/steel-delivery-acceptance/":{"../guides/steel-delivery-checklist/":"/guides/steel-delivery-checklist/","../buy-iron/":"/buy-iron/"},
"knowledge/steel-weight-tolerance/":{"../tools/steel-weight-calculator/":"/tools/steel-weight-calculator/","../products/":"/products/"}
}
for prefix,mp in replacements.items():
    for p in ROOT.rglob("*.html"):
        if not p.as_posix().startswith(prefix): continue
        s=p.read_text(encoding="utf-8",errors="ignore"); old=s
        for a,b in mp.items():
            t=ROOT/b.lstrip("/")
            if t.is_dir(): t=t/"index.html"
            if t.exists(): s=s.replace(a,b)
        if s!=old:
            p.write_text(s,encoding="utf-8"); changed.append(p.as_posix())

print("SEO repair changed",len(set(changed)),"files")


# Normalize malformed double-parent traversal and repair the confirmed rebar guide target.
for p in ROOT.rglob("*.html"):
    if ".git" in p.parts: continue
    s=p.read_text(encoding="utf-8",errors="ignore"); old=s
    s=re.sub(r'href=(["\'])\.\.//',r'href=\1/',s)
    s=s.replace('/guides/rebar-weight-table/','/guides/rebar-weight/')
    if s!=old:
        p.write_text(s,encoding="utf-8")
        changed.append(p.as_posix())

# Add one contextual inbound hub to the previously reported orphan guide pages.
orphan_slugs = [
"brand-factory-price-check","steel-purchase-timing","profile-dimensional-control","steel-waste-by-product",
"steel-project-material-selection","scaffolding-pipe-thickness-choice","profile-cutting-planning","base-plate-ordering",
"galvanized-vs-painted-sheet","steel-semantic-buying-path","steel-dimension-control","steel-storage-layout",
"beam-site-inspection","upn-vs-upe-channel","rebar-site-inspection","sheet-3mm-vs-4mm","steel-order-master-checklist",
"sheet-cutting-vs-full","steel-quality-dispute","steel-inspection-center","steel-manufacturer-selection","angle-equal-unequal",
"steel-supplier-comparison","steel-weight-scale-vs-table","advanced-steel","formwork-strip-selection","beam-brand-size-price",
"square-vs-rectangular-profile","steel-stock-reservation","steel-price-alert-interpretation","sheet-brand-size-price",
"channel-upn-upe","steel-order-change-control","steel-field-checklists","steel-receiving-quantity","sheet-surface-inspection",
"steel-loading-sequence","steel-unit-conversion","roofing-sheet-coating","steel-storage-site","formwork-strip-size-choice",
"steel-delivery-risk","steel-alternative-product","profile-40x40-vs-50x50","steel-delivery-evidence","steel-size-weight-price",
"steel-data-confidence","base-plate-size-thickness","profile-brand-size-price","rebar-12-vs-14","angle-channel-brand-size-price",
"rebar-brand-size-price"
]
hub=ROOT/"guides/index.html"
if hub.exists() and "<!-- SEO ORPHAN HUB -->" not in hub.read_text(encoding="utf-8",errors="ignore"):
    s=hub.read_text(encoding="utf-8",errors="ignore")
    links=[]
    for slug in orphan_slugs:
        if (ROOT/"guides"/slug/"index.html").exists():
            label=slug.replace("-"," ")
            links.append(f'<li><a href="/guides/{slug}/">{label}</a></li>')
    block='<!-- SEO ORPHAN HUB --><section aria-labelledby="seo-orphan-hub"><h2 id="seo-orphan-hub">راهنماهای تخصصی بیشتر</h2><ul>'+''.join(links)+'</ul></section>'
    s=re.sub(r'</main>',block+'</main>',s,count=1,flags=re.I)
    hub.write_text(s,encoding="utf-8")
    changed.append("guides/index.html")

p=ROOT/"prices/index.html"
if p.exists() and "/prices/price-network/" not in p.read_text(encoding="utf-8",errors="ignore") and (ROOT/"prices/price-network/index.html").exists():
    s=p.read_text(encoding="utf-8",errors="ignore")
    s=re.sub(r'</main>','<p><a href="/prices/price-network/">شبکه قیمت آهن آلات</a></p></main>',s,count=1,flags=re.I)
    p.write_text(s,encoding="utf-8"); changed.append("prices/index.html")
