(()=>{if(window.__AHANEIFFEL_SOCIAL_FLOAT__)return;window.__AHANEIFFEL_SOCIAL_FLOAT__=true;
const links=[
{n:"تماس",u:"tel:+989125143831",c:"call",svg:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.5 15.5 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1.02-.24c1.12.37 2.32.56 3.58.56.55 0 1 .45 1 1V20c0 .55-.45 1-1 1C10.6 21 3 13.4 3 4c0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.26.19 2.46.56 3.58a1 1 0 0 1-.25 1.02l-2.21 2.2Z"/></svg>'},
{n:"واتساپ",u:"https://wa.me/989367227775",c:"whatsapp",svg:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.5 3.5A11.8 11.8 0 0 0 12.1 0C5.6 0 .4 5.2.4 11.7c0 2.1.6 4.1 1.6 5.9L.3 24l6.6-1.7c1.8 1 3.4 1.4 5.2 1.4 6.5 0 11.7-5.2 11.7-11.7 0-3.2-1.2-6.2-3.3-8.5ZM12.1 21.7c-1.6 0-3.2-.4-4.6-1.3l-.3-.2-3.9 1 1-3.8-.2-.3a9.9 9.9 0 1 1 8 4.6Zm5.4-7.4c-.3-.2-1.8-.9-2.1-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-1.8-.9-3-1.6-4.2-3.6-.3-.5.3-.5.8-1.5.1-.2.1-.4 0-.6l-.9-2.1c-.2-.5-.5-.4-.7-.4h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.4 3.7 5.9 5.2 2.2 1 2.7 1 3.7.8.7-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.2-.1-.4-.2-.7-.4Z"/></svg>'},
{n:"روبیکا",u:"https://rubika.ir/Ahaneiffel",c:"rubika",svg:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 1.2a10.8 10.8 0 1 0 0 21.6 10.8 10.8 0 0 0 0-21.6Zm5.4 7.2-2.2 7.1c-.2.6-.5.8-1 .8h-4c-.5 0-.8-.2-1-.7L7.1 11c-.2-.5.1-.9.6-.9h2.1l.8-2.2c.1-.4.4-.6.8-.6h5.2c.6 0 1 .5.8 1.1Zm-7.2 5.9h3.1l1.3-4.2h-5.8l1.4 4.2Z"/></svg>'},
{n:"بله",u:"https://ble.ir/%D8%A8%D8%A7%D8%B2%D8%B1%DA%AF%D8%A7%D9%86%DB%8C%20%D9%81%D9%84%D8%B2%D8%A7%D8%AA%20%D8%A7%DB%8C%D9%81%D9%84",c:"bale",svg:'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.1a9.9 9.9 0 0 0-9.9 9.8c0 2.1.7 4.1 2 5.8l-.9 4.2 4.1-1.1c1.4.7 3 1 4.7 1a9.9 9.9 0 1 0 0-19.7Zm5.2 10.2-6 4.1c-.5.3-1.1 0-1.1-.6v-2.1l-3.1-1.3c-.7-.3-.7-1.2 0-1.5l8.6-3.8c.7-.3 1.4.3 1.2 1l-1 3.4 1.4-.2c.8-.1 1.2.7.6 1Z"/></svg>'}
];
const box=document.createElement("div");box.className="ahaneiffel-social-float";box.setAttribute("aria-label","ارتباط با آهن ایفل");
box.innerHTML=links.map(x=>'<a class="aef-social '+x.c+'" href="'+x.u+'" target="_blank" rel="noopener noreferrer" aria-label="'+x.n+'"><span class="aef-icon">'+x.svg+'</span><span class="aef-label">'+x.n+'</span></a>').join("");
document.body.appendChild(box);
const st=document.createElement("style");st.textContent=`.ahaneiffel-social-float{position:fixed;left:10px;top:50%;transform:translateY(-50%);z-index:99999;display:flex;flex-direction:column;gap:9px;direction:ltr}.aef-social{width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#fff;box-shadow:0 5px 18px rgba(0,0,0,.22);transition:transform .2s ease,width .2s ease;border:2px solid rgba(255,255,255,.9);overflow:hidden}.aef-social:hover{transform:scale(1.08)}.aef-icon{width:27px;height:27px;display:flex}.aef-icon svg{width:100%;height:100%}.aef-label{position:absolute;left:58px;background:#0b1522;color:#fff;padding:7px 10px;border-radius:8px;white-space:nowrap;font-size:13px;opacity:0;pointer-events:none;transform:translateX(-5px);transition:.2s}.aef-social:hover .aef-label,.aef-social:focus-visible .aef-label{opacity:1;transform:none}.aef-social.call{background:linear-gradient(145deg,#ffb35f,#ff851b);color:#14283b;animation:aePhoneRing 1.25s ease-in-out infinite;transform-origin:50% 15%;box-shadow:0 0 0 0 rgba(255,133,27,.58),0 6px 20px rgba(255,133,27,.38)}.aef-social.call .aef-icon{width:25px;height:25px}.aef-social.call:after{content:"";position:absolute;inset:-5px;border:2px solid rgba(255,133,27,.7);border-radius:50%;animation:aePhonePulse 1.8s ease-out infinite;pointer-events:none}.aef-social.call:hover{animation-play-state:paused;transform:scale(1.1)}@keyframes aePhoneRing{0%,100%{rotate:0deg}8%,24%,40%{rotate:-13deg}16%,32%,48%{rotate:13deg}56%{rotate:0deg}}@keyframes aePhonePulse{0%{transform:scale(.88);opacity:.85}75%,100%{transform:scale(1.32);opacity:0}}.aef-social.whatsapp{background:#25D366}.aef-social.rubika{background:#7b2cff}.aef-social.bale{background:#168de2}@media(prefers-reduced-motion:reduce){.aef-social.call,.aef-social.call:after{animation:none!important}}@media(max-width:600px){.ahaneiffel-social-float{left:7px;gap:7px}.aef-social{width:42px;height:42px}.aef-icon{width:23px;height:23px}.aef-label{display:none}}`;
document.head.appendChild(st);
})();
// نمایش تصاویر واقعی نبشی در هاب و صفحات سایز نبشی
(()=> {
  const p = decodeURIComponent(location.pathname).toLowerCase();
  const h1 = document.querySelector('main h1') || document.querySelector('h1');
  const title = (document.title || '').toLowerCase();
  const isAnglePage = p.includes('/products/angle/') || p.includes('/angle-') || p.includes('نبشی') || (h1 && h1.textContent.toLowerCase().includes('نبشی')) || title.includes('نبشی');
  if (!isAnglePage || document.getElementById('ae-angle-image') || document.getElementById('ae-angle-gallery')) return;

  const images = [
    {file:"IMG-20260902-WA0007.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 1"},
    {file:"IMG_۲۰۲۶۰۸۰۵_۱۰۵۴۳۳.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 2"},
    {file:"InShot_۲۰۲۵۰۵۱۵_۱۹۲۴۵۸۴۰۲.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 3"},
    {file:"InShot_۲۰۲۵۰۶۰۳_۱۰۰۹۲۹۰۷۴.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 4"},
    {file:"InShot_۲۰۲۵۰۶۰۹_۱۷۲۵۵۹۷۶۰.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 5"},
    {file:"Polish_۲۰۲۵۰۵۱۶_۲۱۱۱۴۴۳۱۰.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 6"},
    {file:"b754a6c7707960f3ef383fdf7dc6823b.jpg", alt:"عکس واقعی نبشی فولادی آهن ایفل 7"},
    {file:"file_000000004e8881f496f699a98494e3d8.png", alt:"عکس واقعی نبشی فولادی آهن ایفل 8"}
  ];
  const imageUrl = file => '/' + file.split('/').map(encodeURIComponent).join('/');
  const setImageSource = (img, file) => {
    img.onerror = () => {
      if (img.dataset.aeFallback === '1') return;
      img.dataset.aeFallback = '1';
      img.src = 'https://raw.githubusercontent.com/vahiiidabdoooli1369-gif/Ahaneiffel/main/' + file.split('/').map(encodeURIComponent).join('/');
    };
    img.src = imageUrl(file);
  };
  const style = document.createElement('style');
  style.textContent = `
    .ae-angle-image{margin:18px auto 24px;max-width:1100px;text-align:center}
    .ae-angle-image img{display:block;width:100%;max-height:520px;object-fit:contain;background:#fff;border:1px solid #e6edf5;border-radius:18px;box-shadow:0 10px 30px rgba(10,42,80,.10)}
    .ae-angle-image figcaption{margin-top:8px;font-size:13px;color:#5b6673}
    .ae-angle-gallery{margin:26px 0;padding:clamp(14px,3vw,24px);background:#fff;border:1px solid #e5edf6;border-radius:20px;box-shadow:0 12px 34px rgba(10,42,80,.07)}
    .ae-angle-gallery h2{margin:0 0 8px;color:#123c68;font-size:clamp(20px,3vw,28px)}
    .ae-angle-gallery>p{margin:0 0 18px;color:#526477;line-height:1.9}
    .ae-angle-gallery-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
    .ae-angle-gallery-card{min-width:0;margin:0;padding:9px;border:1px solid #e7edf4;border-radius:14px;background:#f9fbfe}
    .ae-angle-gallery-card img{display:block;width:100%;height:190px;object-fit:contain;background:#fff;border-radius:10px}
    .ae-angle-gallery-card figcaption{padding:8px 2px 2px;text-align:center;font-size:13px;color:#334b63}
    @media(max-width:760px){.ae-angle-gallery-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.ae-angle-gallery-card img{height:150px}}
    @media(max-width:380px){.ae-angle-gallery-grid{grid-template-columns:1fr}.ae-angle-gallery-card img{height:210px}}
  `;
  document.head.appendChild(style);

  const isHub = p.endsWith('/products/angle/') || p.endsWith('/products/angle/index.html');
  if (isHub) {
    const gallery = document.createElement('section');
    gallery.id = 'ae-angle-gallery';
    gallery.className = 'ae-angle-gallery';
    gallery.setAttribute('aria-labelledby','ae-angle-gallery-title');
    gallery.innerHTML = '<h2 id="ae-angle-gallery-title">گالری تصاویر نبشی آهنی</h2><p>نمونه تصاویر نبشی برای بررسی محصول و انتخاب پیش از استعلام از آهن ایفل.</p><div class="ae-angle-gallery-grid"></div>';
    const grid = gallery.querySelector('.ae-angle-gallery-grid');
    images.forEach((item, i) => {
      const figure = document.createElement('figure');
      figure.className = 'ae-angle-gallery-card';
      const img = document.createElement('img');
      setImageSource(img, item.file);
      img.alt = item.alt;
      img.loading = 'lazy';
      img.decoding = 'async';
      img.width = 480;
      img.height = 360;
      const caption = document.createElement('figcaption');
      caption.textContent = 'تصویر نبشی فولادی ' + (i + 1);
      figure.append(img, caption);
      grid.appendChild(figure);
    });
    const hero = document.querySelector('main .hero');
    if (hero && hero.parentNode) hero.parentNode.insertBefore(gallery, hero.nextSibling);
    else (document.querySelector('main') || document.body).appendChild(gallery);
    return;
  }

  const main = document.querySelector('main') || document.body;
  const sizes = ['30x30','40x40','50x50','60x60','80x80','100x100'];
  const size = sizes.find(value => p.includes('/' + value + '/')) || '30x30';
  const sizeIndex = sizes.indexOf(size);
  const item = images[sizeIndex] || images[0];
  const figure = document.createElement('figure');
  figure.id = 'ae-angle-image';
  figure.className = 'ae-angle-image';
  const img = document.createElement('img');
  setImageSource(img, item.file);
  img.alt = item.alt;
  img.width = 1200;
  img.height = 700;
  img.loading = 'eager';
  img.decoding = 'async';
  const caption = document.createElement('figcaption');
  caption.textContent = 'تصویر نبشی فولادی | آهن ایفل';
  figure.append(img, caption);
  if (h1 && h1.parentNode) h1.parentNode.insertBefore(figure, h1.nextSibling);
  else main.prepend(figure);
})();