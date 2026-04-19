// Mobile nav toggle + External links + Shopee gclid relay
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', !expanded);
      navLinks.classList.toggle('active');
    });
  }

  // ===== gclid 擷取與暫存 =====
  // 從 URL 拿 gclid（Google Ads 點擊 ID），存到 sessionStorage，
  // 訪客在站內跳頁時 gclid 仍可跟著傳到蝦皮連結。
  var urlParams = new URLSearchParams(window.location.search);
  var gclidFromUrl = urlParams.get('gclid');
  if (gclidFromUrl) {
    try { sessionStorage.setItem('gclid', gclidFromUrl); } catch (e) {}
  }
  var gclid = gclidFromUrl;
  if (!gclid) {
    try { gclid = sessionStorage.getItem('gclid'); } catch (e) {}
  }

  // ===== 判斷是否為蝦皮連結 =====
  function isShopeeLink(link) {
    var host = link.hostname || '';
    return /(^|\.)shopee\.tw$/i.test(host) || /(^|\.)s\.shopee\.tw$/i.test(host)
      || /(^|\.)shope\.ee$/i.test(host);
  }

  // ===== 替蝦皮連結附加 utm_content=gclid =====
  // 依據本站驗證：Shopee TW sub_id 的正確欄位是 utm_content
  function attachGclidToShopee(link) {
    if (!gclid) return;
    try {
      var url = new URL(link.href);
      // 若已有 utm_content，保留原值；否則塞 gclid
      if (!url.searchParams.get('utm_content')) {
        url.searchParams.set('utm_content', gclid);
      }
      link.href = url.toString();
    } catch (e) {}
  }

  // ===== 掃過所有外部連結 =====
  var links = document.querySelectorAll('a[href^="http"]');
  var siteHost = window.location.hostname;
  links.forEach(function (link) {
    if (link.hostname !== siteHost) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
      if (isShopeeLink(link)) {
        attachGclidToShopee(link);
      }
    }
  });

  // ===== 保險：點擊當下再補一次（處理動態載入或延遲改網址的情況） =====
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[href]');
    if (!link) return;
    if (link.hostname === siteHost) return;
    if (isShopeeLink(link)) {
      attachGclidToShopee(link);
    }
  });
});
