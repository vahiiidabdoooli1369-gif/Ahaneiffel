const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("assets/live-price-feed.js", "utf8");

function jalaliDate(date) {
  const parts = new Intl.DateTimeFormat("en-US-u-ca-persian-nu-latn", {
    timeZone: "Asia/Tehran",
    year: "numeric",
    month: "2-digit",
    day: "2-digit"
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]));
  return values.year + "/" + values.month.padStart(2, "0") + "/" + values.day.padStart(2, "0");
}

async function evaluateFeed(publishedDate, updatedAt) {
  const priceCell = {
    textContent: "",
    title: "",
    classList: { add() {} },
    setAttribute() {}
  };
  const status = { textContent: "" };
  const row = {
    getAttribute(name) {
      return name === "data-price-family" ? "میلگرد" : "";
    },
    querySelector(selector) {
      return selector === ".quote" ? priceCell : status;
    }
  };
  const anchor = {
    meta: null,
    prepend(element) { this.meta = element; }
  };
  const document = {
    querySelectorAll(selector) {
      if (selector === "tr[data-price-family]") return [row];
      return [];
    },
    createElement() {
      return { className: "", textContent: "", remove() {} };
    },
    querySelector() { return anchor; }
  };
  const data = {
    published_date: publishedDate,
    updated_at_utc: updatedAt,
    currency: "تومان",
    unit: "کیلوگرم",
    rows: [{ raw: ["میلگرد", "میلگرد آجدار"], price: 122000 }]
  };
  const context = {
    document,
    fetch: async () => ({ ok: true, json: async () => data }),
    Date,
    Intl,
    console
  };
  vm.runInNewContext(source, context);
  await new Promise(resolve => setTimeout(resolve, 0));
  return { status: status.textContent, title: priceCell.title, price: priceCell.textContent, meta: anchor.meta ? anchor.meta.textContent : "" };
}

(async () => {
  const now = new Date();
  const today = jalaliDate(now);
  const oldDay = jalaliDate(new Date(now.getTime() - 48 * 60 * 60 * 1000));

  const fresh = await evaluateFeed(today, now.toISOString());
  assert.match(fresh.status, /نرخ پایه/);
  assert.match(fresh.title, /تأیید نهایی/);
  assert.match(fresh.price, /122/);

  const stalePublishedDate = await evaluateFeed(oldDay, now.toISOString());
  assert.equal(stalePublishedDate.status, "نیازمند بررسی");
  assert.match(stalePublishedDate.title, /نیازمند بررسی/);
  assert.match(stalePublishedDate.meta, /قیمت‌ها نیازمند بررسی هستند/);

  const staleTimestamp = await evaluateFeed(today, new Date(now.getTime() - 27 * 60 * 60 * 1000).toISOString());
  assert.equal(staleTimestamp.status, "نیازمند بررسی");

  console.log("Price-feed freshness tests passed: same-day, previous-day, and stale timestamp.");
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
