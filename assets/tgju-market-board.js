(function(){
  "use strict";

  if (document.getElementById("AE_PRICE_BAR")) return;

  var bar = document.createElement("div");
  bar.id = "AE_PRICE_BAR";
  bar.innerHTML =
    '<div class="ae-price-title">قیمت روز</div>' +
    '<div id="ae-price-window"><div id="ae-price-track">' +
    '<span class="ae-loading">در حال دریافت قیمت‌ها...</span>' +
    '</div></div>';

  document.body.appendChild(bar);

  var style = document.createElement("style");
  style.textContent = `
    #AE_PRICE_BAR{
      position:fixed;bottom:0;left:0;width:100%;height:42px;z-index:2147483000;
      display:flex;align-items:center;direction:rtl;background:#102B46;
      border-top:2px solid #FF851B;box-sizing:border-box;overflow:hidden;font-family:inherit
    }
    #AE_PRICE_BAR *{box-sizing:border-box}
    #AE_PRICE_BAR .ae-price-title{
      flex:0 0 auto;height:100%;display:flex;align-items:center;padding:0 12px;
      background:#FF851B;color:#102B46;font-size:12px;font-weight:900;white-space:nowrap
    }
    #ae-price-window{flex:1;min-width:0;height:100%;overflow:hidden;display:flex;align-items:center}
    #ae-price-track{
      display:flex;align-items:center;width:max-content;white-space:nowrap;
      animation:aePriceMove 20s linear infinite;will-change:transform
    }
    #ae-price-track:hover{animation-play-state:paused}
    #AE_PRICE_BAR .ae-price-item{
      display:inline-flex;align-items:center;gap:7px;padding:0 14px;height:25px;
      border-left:1px solid #49627A;font-size:12px
    }
    #AE_PRICE_BAR .ae-price-name{color:#fff;font-weight:600}
    #AE_PRICE_BAR .ae-price-value{color:#FFAB55;font-weight:900;direction:rtl}
    #AE_PRICE_BAR .ae-loading{color:#fff;font-size:11px;padding:0 12px}
    @keyframes aePriceMove{from{transform:translateX(0)}to{transform:translateX(50%)}}
    body{padding-bottom:42px!important}
    @media(max-width:600px){
      #AE_PRICE_BAR .ae-price-title{padding:0 9px;font-size:11px}
      #AE_PRICE_BAR .ae-price-item{padding:0 10px;font-size:11px}
    }
    @media(prefers-reduced-motion:reduce){#ae-price-track{animation:none}}
  `;
  document.head.appendChild(style);

  var track = document.getElementById("ae-price-track");

  function escapeHTML(value){
    return String(value).replace(/[&<>"']/g,function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
    });
  }

  window.navasanret = function(data){
    try{
      var html = typeof data === "string" ? JSON.parse(data) : data;
      if(typeof html !== "string") html = String(html || "");
      var doc = new DOMParser().parseFromString(html,"text/html");
      var rows = doc.querySelectorAll("tr");
      var items = [];

      rows.forEach(function(row){
        var cells = Array.from(row.querySelectorAll("th,td"));
        if(cells.length < 2) return;

        var texts = cells.map(function(cell){
          return cell.textContent.trim().replace(/\\s+/g," ");
        });

        var name = "";
        var price = "";
        var table = row.closest("table");
        var headerCells = table
          ? Array.from(table.querySelectorAll("tr:first-child th, tr:first-child td"))
          : [];
        var priceIndex = headerCells.findIndex(function(cell){
          return /قیمت|price/i.test(cell.textContent);
        });

        if(priceIndex >= 0 && cells[priceIndex]){
          price = texts[priceIndex];
          name = texts.find(function(t,i){
            return i !== priceIndex && t &&
              !/قیمت|تغییر|زمان|تاریخ|درصد|time|date/i.test(t);
          }) || "";
        }

        if(!price){
          var candidates = texts.filter(function(t){
            return /[0-9۰-۹]/.test(t) &&
              !/[:：]/.test(t) &&
              !/درصد|ساعت|دقیقه|امروز|دیروز|time|date/i.test(t);
          });
          name = texts.find(function(t){
            return t && !/[0-9۰-۹]/.test(t) &&
              !/قیمت|تغییر|زمان|تاریخ|time|date/i.test(t);
          }) || "";
          price = candidates.length ? candidates[0] : "";
        }

        if(name && price && name !== price){
          items.push({name:name,price:price});
        }
      });

      if(!items.length){
        track.innerHTML = '<span class="ae-loading">قیمت‌ها دریافت نشد؛ خروجی منبع قابل تشخیص نیست.</span>';
        return;
      }

      var output = items.map(function(item){
        return '<span class="ae-price-item">' +
          '<span class="ae-price-name">' + escapeHTML(item.name) + '</span>' +
          '<span class="ae-price-value">' + escapeHTML(item.price) + '</span>' +
          '</span>';
      }).join("");

      track.innerHTML = output + output;
    }catch(error){
      track.innerHTML = '<span class="ae-loading">خطا در دریافت قیمت‌ها</span>';
    }
  };

  var source = document.createElement("script");
  source.src = "https://www.navasan.tech/wp-navasan.php?usd&eur&18ayar&sekkeh&bahar&nim&rob&abshodeh&xau&btc";
  source.async = true;
  source.onerror = function(){
    track.innerHTML = '<span class="ae-loading">اتصال به منبع قیمت موقتاً برقرار نشد.</span>';
  };
  document.head.appendChild(source);
})();