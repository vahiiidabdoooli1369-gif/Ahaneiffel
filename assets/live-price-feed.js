(function () {
  const feedUrl = "/data/market-prices.json";
  const normalize = s => String(s || "").replace(/[۰-۹]/g, d => "۰۱۲۳۴۵۶۷۸۹".indexOf(d)).replace(/[\u0660-\u0669]/g, d => "٠١٢٣٤٥٦٧٨٩".indexOf(d)).replace(/,/g, "").replace(/\s+/g, " ").trim();
  const tokens = s => normalize(s).toLowerCase().match(/[a-zآ-ی]+|\d+(?:\.\d+)?/g) || [];
  const score = (a, b) => {
    const aa = tokens(a), bb = new Set(tokens(b));
    return aa.reduce((n, x) => n + (bb.has(x) ? (x.match(/^\d/) ? 4 : 2) : 0), 0);
  };
  const format = n => new Intl.NumberFormat("fa-IR").format(Math.round(Number(n)));
  async function run() {
    const tables = document.querySelectorAll(".price-table");
    if (!tables.length) return;
    let data;
    try {
      const res = await fetch(feedUrl, { cache: "no-store" });
      if (!res.ok) return;
      data = await res.json();
    } catch (_) { return; }
    if (!Array.isArray(data.rows) || !data.rows.length) return;
    document.querySelectorAll(".live-price-meta").forEach(el => el.remove());
    const meta = document.createElement("p");
    meta.className = "last-update live-price-meta";
    meta.textContent = "آخرین دریافت قیمت: " + new Date(data.updated_at_utc).toLocaleString("fa-IR");
    const anchor = document.querySelector(".price-section, .section, .hero");
    if (anchor) anchor.prepend(meta);
    tables.forEach(table => {
      table.querySelectorAll("tbody tr").forEach(row => {
        const cells = row.querySelectorAll("td");
        if (!cells.length) return;
        const text = row.textContent;
        let best = null, bestScore = 0;
        for (const item of data.rows) {
          const s = score(text, item.raw.join(" "));
          if (s > bestScore) { bestScore = s; best = item; }
        }
        if (!best || bestScore < 4) return;
        const priceCell = row.querySelector(".quote");
        if (priceCell) {
          priceCell.textContent = format(best.price) + " تومان";
          priceCell.classList.add("live-price");
          priceCell.title = "قیمت دریافت شده از منبع قیمت آهن ایفل";
        }
        const status = row.querySelector(".flat, .up, .down");
        if (status) status.textContent = "به روز";
      });
    });
  }
  run();
})();