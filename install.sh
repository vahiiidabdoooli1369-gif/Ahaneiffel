#!/usr/bin/env bash
set -Eeuo pipefail

SITE="https://ahaneiffel.top"
DEST="${HOME}/seo-files"
TMP="$(mktemp -d -t ahaneiffel-seo-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

echo "🚀 Ahaneiffel SEO Safe Automation"
echo "================================="

mkdir -p "$DEST"

cat > "$TMP/robots.txt" <<'ROBOTS'
User-agent: *
Allow: /

Disallow: /admin/
Disallow: /login/
Disallow: /register/
Disallow: /cart/
Disallow: /checkout/
Disallow: /account/

Sitemap: https://ahaneiffel.top/sitemap.xml
ROBOTS

cat > "$TMP/sitemap.xml" <<'SITEMAP'
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://ahaneiffel.top/</loc>
    <lastmod>2026-10-06</lastmod>
  </url>
</urlset>
SITEMAP

cat > "$TMP/.htaccess" <<'HTACCESS'
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://ahaneiffel.top%{REQUEST_URI} [R=301,L]
RewriteCond %{HTTP_HOST} ^www\.ahaneiffel\.top$ [NC]
RewriteRule ^ https://ahaneiffel.top%{REQUEST_URI} [R=301,L]
</IfModule>

Options -Indexes

<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/plain text/css application/javascript application/json
</IfModule>
HTACCESS

cp "$TMP/robots.txt" "$DEST/robots.txt"
cp "$TMP/sitemap.xml" "$DEST/sitemap.xml"
cp "$TMP/.htaccess" "$DEST/.htaccess"

echo
echo "✅ Local SEO package created:"
echo "   $DEST/robots.txt"
echo "   $DEST/sitemap.xml"
echo "   $DEST/.htaccess"
echo
echo "⚠️ SAFE MODE: nothing has been uploaded to ahaneiffel.top."
echo "⚠️ The generated sitemap is intentionally minimal until the real site's URL structure is audited."
echo
echo "Next: run the audit before replacing any live SEO files."
