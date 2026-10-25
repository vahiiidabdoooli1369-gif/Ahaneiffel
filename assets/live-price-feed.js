(function () {
  const feedUrl = "/data/market-prices.json";
  const STALE_MS = 26 * 60 * 60 * 1000;
  const normalize = s => String(s || "")
    .replace(/[۰-۹]/g, d => "۰۱۲۳۴۵۶۷۸۹".indexOf(d))
    .replace(/[\u0660-\u0669]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d))
    .replace(/,/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
  const format = n => new Intl.NumberFormat("fa-IR").format(Math.round(Number(n)));
  const normalizeDate = value => String(value || "")
    .replace(/[۰-۹]/g, d => "۰۱۲۳۴۵۶۷۸۹".indexOf(d))
    .replace(/[٠-٩]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d))
    .replace(/[.\\-]/g, "/")
    .replace(/\\s+/g, "");

  function todayInTehranJalali() {
    try {
      const parts = new Intl.DateTimeFormat("en-US-u-ca-persian-nu-latn", {
        timeZone: "Asia/Tehran",
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
      }).formatToParts(new Date());
      const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
      if (!values.year || !values.month || !values.day) return "";
      return values.year + "/" + values.month.padStart(2, "0") + "/" + values.day.padStart(2, "0");
    } catch (_) {
      return "";
    }
  }

  async function run() {
    // Only explicitly marked family-level rows may be updated by this generic feed.
    // Size-, brand-, and branch-specific tables are intentionally left untouched.
    const rows = document.querySelectorAll("tr[data-price-family]");
    if (!rows.length) return;

    let data;
    try {
      const res = await fetch(feedUrl, { cache: "no-store" });
      if (!res.ok) return;
      data = await res.json();
    } catch (_) {
      return;
    }
    if (!Array.isArray(data.rows) || !data.rows.length) return;

    const updatedAt = Date.parse(data.updated_at_utc || "");
    const age = Date.now() - updatedAt;
    const publishedDate = normalizeDate(data.published_date);
    const todayDate = todayInTehranJalali();
    const publicationDateMatchesToday = !publishedDate || !todayDate || publishedDate === todayDate;
    const isFresh = Number.isFinite(updatedAt) && age >= 0 && age <= STALE_MS && publicationDateMatchesToday;

    document.querySelectorAll(".live-price-meta").forEach(el => el.remove());
    const meta = document.createElement("p");
    meta.className = "last-update live-price-meta";
    meta.textContent = data.published_date
      ? "تاریخ اعلام قیمت: " + data.published_date + " | واحدها مطابق هر ردیف | مبالغ به " + (data.currency || "تومان")
      : "آخرین دریافت قیمت: " + (Number.isFinite(updatedAt) ? new Date(updatedAt).toLocaleString("fa-IR") : "زمان نامشخص");
    if (!isFresh) meta.textContent += " — قیمت‌ها نیازمند بررسی هستند";

    const anchor = document.querySelector(".price-table-card, .price-section, .section, .hero");
    if (anchor) anchor.prepend(meta);

    rows.forEach(row => {
      const family = normalize(row.getAttribute("data-price-family"));
      const item = data.rows.find(entry =>
        Array.isArray(entry.raw) && entry.raw.some(alias => normalize(alias) === family)
      );
      if (!item) return;

      const priceCell = row.querySelector(".quote");
      if (priceCell) {
        const unit = item.unit || data.unit || "واحد نامشخص";
        priceCell.textContent = format(item.price) + " تومان/" + unit;
        priceCell.classList.add("live-price");
        priceCell.setAttribute("data-price-source", "ahaneiffel-market-feed");
        priceCell.title = isFresh
          ? "قیمت پایه از فید آهن ایفل؛ تأیید نهایی هنگام سفارش"
          : "آخرین قیمت پایه ثبت‌شده؛ زمان به‌روزرسانی نیازمند بررسی است";
      }

      const status = row.querySelector("[data-price-status], .flat, .up, .down");
      if (status) status.textContent = isFresh
        ? "نرخ پایه؛ تأیید نهایی هنگام سفارش"
        : "نیازمند بررسی";
    });
  }

  run();
})();
