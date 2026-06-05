/* Verify dist/: every locally-referenced asset (HTML + CSS) exists on disk; flag leftover WP refs. */
const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');
const P = path.posix;
const DIST = path.resolve(__dirname, '..', 'dist');

let broken = [], leftover = [], checked = 0;
const exists = p => { try { fs.accessSync(p); return true; } catch { return false; } };

function isLocal(u) {
  if (!u) return false;
  u = u.trim();
  return !(/^(https?:|\/\/|data:|mailto:|tel:|#|javascript:)/i.test(u));
}
function resolveFromFile(fileAbs, url) {
  const clean = url.split(/[?#]/)[0];
  const dir = path.dirname(fileAbs);
  return path.normalize(path.join(dir, clean));
}

function walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const fp = path.join(dir, e.name);
    if (e.isDirectory()) walk(fp);
    else if (e.name.endsWith('.html')) checkHtml(fp);
    else if (e.name.endsWith('.css')) checkCss(fp);
  }
}

function checkHtml(fp) {
  const html = fs.readFileSync(fp, 'utf8');
  const $ = cheerio.load(html);
  const rel = path.relative(DIST, fp);
  const add = (url, ctx) => {
    if (!isLocal(url)) return;
    checked++;
    if (!exists(resolveFromFile(fp, url))) broken.push(`${rel} [${ctx}] -> ${url}`);
  };
  $('link[href]').each((i, el) => add($(el).attr('href'), 'link'));
  $('script[src]').each((i, el) => add($(el).attr('src'), 'script'));
  $('img[src]').each((i, el) => add($(el).attr('src'), 'img'));
  $('[srcset]').each((i, el) => {
    ($(el).attr('srcset') || '').split(',').forEach(s => { const u = s.trim().split(/\s+/)[0]; add(u, 'srcset'); });
  });
  $('a[href]').each((i, el) => {
    const h = $(el).attr('href');
    if (isLocal(h) && /\.(pdf|docx?|zip|jpe?g|png)$/i.test(h.split(/[?#]/)[0])) add(h, 'a');
  });
  // leftover WP refs (excluding allowed: schema/og meta absolute, google fonts, msapplication)
  $('link[href], script[src], img[src]').each((i, el) => {
    const u = $(el).attr('href') || $(el).attr('src') || '';
    if (/wp-content|wp-includes|wpfc-minified/.test(u)) leftover.push(`${rel} -> ${u}`);
  });
}

function checkCss(fp) {
  const css = fs.readFileSync(fp, 'utf8');
  const rel = path.relative(DIST, fp);
  const re = /url\(\s*(['"]?)([^)'"]+)\1\s*\)/gi; let m;
  while ((m = re.exec(css))) {
    const u = m[2];
    if (!isLocal(u)) continue;
    checked++;
    if (!exists(resolveFromFile(fp, u))) broken.push(`${rel} [css-url] -> ${u}`);
  }
  if (/wp-content|wp-includes|2aformation\.com/.test(css)) {
    const hits = (css.match(/(wp-content|wp-includes|2aformation\.com)/g) || []).length;
    leftover.push(`${rel} -> ${hits} inline WP/live refs in css`);
  }
}

walk(DIST);
console.log('Refs checked     :', checked);
console.log('Broken refs      :', broken.length);
broken.slice(0, 40).forEach(b => console.log('  X', b));
console.log('Leftover WP refs :', leftover.length);
leftover.slice(0, 20).forEach(l => console.log('  ~', l));
if (broken.length === 0) console.log('\nOK: no broken local references.');
