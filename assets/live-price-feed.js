(function () {
  const feedUrl = "/data/market-prices.json";
  const STALE_MS = 26 * 60 * 60 * 1000;
  const normalize = s => String(s || "").replace(/[۰-۹]/g, d => "۰۱۲۳۴۵۶۷۸۹".indexOf(d)).replace(/[\u0660-\u0669]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d)).replace(/,/g, "").replace(/\s+/g, " ").trim();
  const tokens = s => normalize(s).toLowerCase().match(/[a-zآ-ی]+|\d+(?:\.\d+)?/g) || [];
  const score = (a, b) => {
    const aa = tokens(a), bb = new Set(tokens(b));
    return aa.reduce((n, x) => n + (bb.has(x) ? (x.match(/^\d/) ? 4 : 2) : 0), 0);
  };
  const format = n => new Intl.NumberFormat("fa-IR").format(Math.round(Number(n)));
  async function run() {
    // Keep this script safe on pages without a price table.
    const tables = document.querySelectorAll(".price-table, .price-table-card table");
    if (!tables.length) return;
    let data;
    try {
      const res = await fetch(feedUrl, { cache: "no-store" });
      if (!res.ok) return;
      data = await res.json();
    } catch (_) { return; }
    if (!Array.isArray(data.rows) || !data.rows.length) return;

    const updatedAt = Date.parse(data.updated_at_utc || "");
    const isFresh = Number.isFinite(updatedAt) && (Date.now() - updatedAt) <= STALE_MS;
    document.querySelectorAll(".live-price-meta").forEach(el => el.remove());
    const meta = document.createElement("p");
    meta.className = "last-update live-price-meta";
    meta.textContent = data.published_date
      ? "تاریخ اعلام قیمت: " + data.published_date + " | واحد: " + (data.unit || "نیازمند تأیید") + " | مبالغ به " + (data.currency || "تومان")
      : "آخرین دریافت قیمت: " + (Number.isFinite(updatedAt) ? new Date(updatedAt).toLocaleString("fa-IR") : "زمان نامشخص");
    if (!isFresh) meta.textContent += " — قیمت ها نیازمند بررسی هستند";
    const anchor = document.querySelector(".price-section, .price-table-card, .section, .hero");
    if (anchor) anchor.prepend(meta);

    tables.forEach(table => {
      table.querySelectorAll("tbody tr").forEach(row => {
        const cells = row.querySelectorAll("td");
        if (!cells.length) return;
        // Match the product label, not the size/weight cells. The feed contains
        // one confirmed price per product family, not per size.
        const label = normalize(cells[0].textContent).toLowerCase();
        let best = null, bestScore = 0, tied = false;
        for (const item of data.rows) {
          const aliases = (item.raw || []).map(value => normalize(value).toLowerCase()).filter(Boolean);
          const exactAlias = aliases.find(alias => label.includes(alias));
          if (exactAlias) {
            best = item;
            bestScore = 100 + exactAlias.length;
            tied = false;
            break;
          }
          const s = score(label, aliases.join(" "));
          if (s > bestScore) { bestScore = s; best = item; tied = false; }
          else if (s > 0 && s === bestScore) { tied = true; }
        }
        // Do not guess a family price for a generic or ambiguous product label.
        if (!best || bestScore < 2 || tied) return;
        // Prefer an explicit .quote cell; otherwise use the conventional third cell
        // used by the site's existing price cards. This keeps legacy tables intact.
        const priceCell = row.querySelector(".quote") || cells[2];
        if (priceCell) {
          priceCell.textContent = format(best.price) + " تومان";
          priceCell.classList.add("live-price");
          priceCell.setAttribute("data-price-source", "ahaneiffel-market-feed");
          priceCell.title = isFresh
            ? "قیمت دریافت شده از منبع قیمت آهن ایفل"
            : "آخرین قیمت دریافت شده؛ زمان به روزرسانی نیازمند بررسی است";
        }
        const status = row.querySelector(".flat, .up, .down") || cells[3];
        if (status) status.textContent = isFresh ? "به روز" : "نیازمند بررسی";
      });
    });
  }
  run();
})();
