// GitHub Pages project URL guard
// Prevent accidental redirects to legacy/custom domains.
(function () {
  var host = window.location.hostname;
  var allowedHost = 'vahiiidabdoooli1369-gif.github.io';
  var pathPrefix = '/Ahaneiffel';
  if (host === allowedHost && !window.location.pathname.startsWith(pathPrefix)) {
    window.location.replace(pathPrefix + '/');
  }
})();
