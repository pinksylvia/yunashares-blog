// Mobile nav toggle
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

  // 所有外部連結自動開新視窗
  var links = document.querySelectorAll('a[href^="http"]');
  var host = window.location.hostname;
  links.forEach(function (link) {
    if (link.hostname !== host) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });
});
