from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "products"

FAMILY = {
    "rebar": ("میلگرد", "قیمت میلگرد", "/prices/rebar/"),
    "beam": ("تیرآهن", "قیمت تیرآهن", "/prices/beam/"),
    "profile": ("پروفیل", "قیمت پروفیل", "/prices/profile/"),
    "angle": ("نبشی", "قیمت نبشی", "/prices/angle/"),
    "channel": ("ناودانی", "قیمت ناودانی", "/prices/channel/"),
    "sheet": ("ورق سیاه", "قیمت ورق", "/prices/sheet/"),
    "roofing-sheet": ("ورق شیروانی", "قیمت ورق شیروانی", "/prices/roofing-sheet/"),
    "perforated-sheet": ("ورق پانچ", "قیمت ورق پانچ", "/prices/perforated-sheet/"),
    "scaffolding-pipe": ("لوله داربستی", "قیمت لوله داربستی", "/prices/scaffolding-pipe/"),
    "formwork-strip": ("تسمه قالب‌بندی", "قیمت تسمه قالب‌بندی", "/prices/formwork-strip/"),
    "base-plate": ("بیس پلیت", "قیمت بیس پلیت", "/prices/base-plate/"),
}

def label(family, slug):
    s = slug.replace("index.html","").strip("/")
    if family == "profile":
        return f"پروفیل {s.replace('x','×')}"
    if family == "sheet":
        return f"ورق سیاه {s.replace('mm',' میل')}"
    return f"{FAMILY[family][0]} {s.replace('-',' ')}"

def make_block(family, slug):
    name, price_label, price_url = FAMILY[family]
    item = label(family, slug)
    return f'''<section class="card expert-review" id="review">
<h2>نقد و بررسی تخصصی {item}</h2>
<p><strong>جمع‌بندی کاربردی:</strong> {item} را نباید فقط با عدد قیمت مقایسه کرد. برای خرید دقیق باید مشخصات فنی، وزن واقعی، استاندارد یا گرید، کارخانه، مقدار سفارش، موجودی و هزینه حمل هم‌زمان بررسی شوند. این صفحه برای کمک به تصمیم‌گیری قبل از استعلام و خرید تنظیم شده است.</p>
<h3>نقاط قوت و کاربردهای مهم</h3>
<ul>
<li>امکان انتخاب بر اساس نیاز واقعی پروژه و مقایسه با سایزهای نزدیک.</li>
<li>قابل بررسی از نظر وزن، مشخصات فنی، کیفیت ظاهری و شرایط تأمین.</li>
<li>قابل اتصال به قیمت روز و ابزارهای محاسبه و برآورد هزینه آهن ایفل.</li>
</ul>
<h3>محدودیت‌ها و ریسک‌های خرید</h3>
<ul>
<li>نام محصول یا سایز به تنهایی مشخصات کامل کالا را مشخص نمی‌کند.</li>
<li>تفاوت ضخامت، وزن، گرید یا استاندارد می‌تواند قیمت دو پیشنهاد را تغییر دهد.</li>
<li>قیمت بدون هزینه حمل و شرایط تحویل، لزوماً قیمت تمام‌شده نیست.</li>
</ul>
<h3>چه زمانی این محصول انتخاب مناسبی است؟</h3>
<p>وقتی ابعاد و مشخصات موردنیاز از نقشه، محاسبات یا نیاز اجرایی مشخص شده باشد، می‌توان این محصول را با گزینه‌های نزدیک از نظر وزن، قیمت و کاربرد مقایسه کرد. برای اعضای باربر و کاربردهای حساس، انتخاب نهایی باید با مشخصات فنی پروژه تطبیق داده شود و صرفاً بر مبنای قیمت انجام نشود.</p>
<h3>راهنمای خرید مرحله‌به‌مرحله</h3>
<ol>
<li>نام و سایز دقیق محصول را مشخص کنید.</li>
<li>ضخامت، گرید یا استاندارد و کارخانه موردنیاز را تعیین کنید.</li>
<li>تعداد شاخه، طول، ابعاد یا تناژ موردنیاز را مشخص کنید.</li>
<li>قیمت را روی یک واحد مشترک، ترجیحاً کیلوگرم یا تن، مقایسه کنید.</li>
<li>هزینه بارگیری، حمل، تخلیه و زمان تحویل را بررسی کنید.</li>
<li>پیش‌فاکتور را با سفارش تطبیق دهید و هنگام تحویل مشخصات بار را کنترل کنید.</li>
</ol>
<h3>نکته مهم برای مقایسه قیمت</h3>
<p>اگر دو فروشنده قیمت متفاوتی ارائه کردند، ابتدا مشخصات کالا را یکسان کنید. سپس وزن واقعی، قیمت واحد، مقدار، کارخانه، شرایط پرداخت و هزینه حمل را کنار هم بگذارید. تنها در این حالت مقایسه قیمت می‌تواند معنی‌دار باشد.</p>
<h3>جمع‌بندی برای خریدار</h3>
<p>برای خرید {item}، مشخصات کامل سفارش را آماده کنید و سپس قیمت روز و موجودی را استعلام بگیرید. اگر بین دو سایز یا دو مشخصات مردد هستید، کاربرد، وزن موردنیاز و شرایط اجرا را اعلام کنید تا گزینه‌ها بر اساس نیاز واقعی مقایسه شوند.</p>
<p><a href="{price_url}">{price_label}</a> | <a href="/tools/steel-weight-calculator/">محاسبه وزن آهن</a> | <a href="/tools/steel-purchase-cost-calculator/">محاسبه هزینه خرید</a> | <a href="/buy-iron/">خرید آهن آلات</a></p>
</section>'''

changed=0
for p in PRODUCTS.rglob("index.html"):
    rel=p.relative_to(PRODUCTS)
    if len(rel.parts) < 3:
        continue
    family=rel.parts[0]
    if family not in FAMILY or 'id="review"' in p.read_text(encoding="utf-8"):
        continue
    text=p.read_text(encoding="utf-8")
    if re.search(r"</main>", text, re.I):
        text=re.sub(r"</main>", make_block(family, str(rel.parts[1]))+"</main>", text, count=1, flags=re.I)
        p.write_text(text, encoding="utf-8")
        changed += 1
print(f"enriched={changed}")
