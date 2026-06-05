/* Build pipeline: WordPress (Blocksy + Elementor) mirror -> clean static site.
 * - Per-page CSS: concat (DOM order) -> PurgeCSS (safelisted) -> clean-css minify.
 * - JS: relocate each external file to assets/js (deduped, terser-minified); inline scripts left in place.
 * - Images copied to assets/images (subpaths preserved). Fonts downloaded locally to assets/fonts.
 * - Internal page links kept (permalink structure preserved). WP head cruft stripped.
 * Source mirror is read-only; everything is written to ./dist.
 */
const fs = require('fs');
const fsp = fs.promises;
const path = require('path');
const https = require('https');
const cheerio = require('cheerio');
const CleanCSS = require('clean-css');
const { minify } = require('terser');
const { PurgeCSS } = require('purgecss');

const ROOT = path.resolve(__dirname, '..');
const DIST = path.join(ROOT, 'dist');
const LIVE = 'https://2aformation.com/';
const P = path.posix;

const BLOCK_DIRS = new Set(['wp-admin', 'wp-includes', 'wp-content', 'wp-json',
  'feed', 'comments', 'search', 'dist', '_build', 'author', 'xmlrpc.php']);

const EL_CORE_RE = /wp-content\/plugins\/elementor\/assets\/js\/(frontend-modules|frontend|webpack\.runtime)\.min\.js$/;
const EL_JS = LIVE + 'wp-content/plugins/elementor/assets/js/';
const BLOCKSY_BUNDLE = 'wp-content/themes/blocksy/static/bundle';
const elementorCore = new Set(); // resPaths of elementor core js referenced by pages
const standaloneCss = new Map();  // resPath -> distPath (lazy CSS, url-rebased)

// resPath = site-root-relative posix path of an asset (no leading slash, no query/hash)
const imagesNeeded = new Map();   // resPath -> distPath
const fontsNeeded = new Map();    // resPath -> distPath  (downloaded from LIVE)
const filesNeeded = new Map();    // resPath -> distPath  (pdf etc.)
const jsNeeded = new Map();       // resPath -> distPath
const report = { pages: [], jsFiles: 0, images: 0, fonts: 0, docs: 0, cssBefore: 0, cssAfter: 0, fontFail: [], imgFail: [] };

const IMG_EXT = /\.(png|jpe?g|gif|svg|webp|ico|avif|bmp)$/i;
const FONT_EXT = /\.(woff2?|ttf|eot|otf)$/i;
const DOC_EXT = /\.(pdf|docx?|xlsx?|pptx?|zip|csv)$/i;

function stripQH(s) { return s.replace(/[?#].*$/, ''); }

// Resolve a URL referenced from a file located in `baseDir` (posix, root-relative).
// Returns { kind:'local', resPath } | { kind:'external', url } | { kind:'data' } | null
function resolveUrl(raw, baseDir) {
  if (!raw) return null;
  let u = raw.trim().replace(/^['"]|['"]$/g, '');
  if (!u || u.startsWith('data:') || u.startsWith('#') || u.startsWith('mailto:') ||
      u.startsWith('tel:') || u.startsWith('javascript:')) return { kind: 'data' };
  let m;
  if ((m = u.match(/^https?:\/\/([^/]+)(\/.*)?$/i))) {
    const host = m[1].toLowerCase();
    if (host === '2aformation.com' || host === 'www.2aformation.com') {
      return { kind: 'local', resPath: stripQH((m[2] || '/').replace(/^\//, '')) };
    }
    return { kind: 'external', url: u };
  }
  if (u.startsWith('//')) {
    const host = u.slice(2).split('/')[0].toLowerCase();
    if (host === '2aformation.com' || host === 'www.2aformation.com') {
      return { kind: 'local', resPath: stripQH(u.slice(2).split('/').slice(1).join('/')) };
    }
    return { kind: 'external', url: 'https:' + u };
  }
  if (u.startsWith('/')) return { kind: 'local', resPath: stripQH(u.replace(/^\//, '')) };
  // relative
  const joined = P.normalize(P.join(baseDir || '', stripQH(u)));
  return { kind: 'local', resPath: joined.replace(/^(\.\.\/)+/, '') };
}

function mapResource(resPath) {
  const clean = resPath.replace(/^\.?\//, '');
  if (FONT_EXT.test(clean)) {
    const dp = 'assets/fonts/' + P.basename(clean);
    fontsNeeded.set(clean, dp);
    return dp;
  }
  if (IMG_EXT.test(clean)) {
    const sub = clean.replace(/^wp-content\//, '').replace(/[^a-zA-Z0-9._\/-]/g, '_');
    const dp = 'assets/images/' + sub;
    imagesNeeded.set(clean, dp);
    return dp;
  }
  if (DOC_EXT.test(clean)) {
    const dp = 'assets/files/' + P.basename(clean);
    filesNeeded.set(clean, dp);
    return dp;
  }
  return null;
}

function mapJs(resPath) {
  const clean = resPath.replace(/^\.?\//, '');
  if (jsNeeded.has(clean)) return jsNeeded.get(clean);
  const base = P.basename(clean).replace(/[^a-zA-Z0-9._-]/g, '_');
  let dp = 'assets/js/' + base;
  const used = new Set(jsNeeded.values());
  let i = 2;
  while (used.has(dp)) { dp = 'assets/js/' + base.replace(/\.js$/i, '') + '-' + i + '.js'; i++; }
  jsNeeded.set(clean, dp);
  return dp;
}

// path from a page dir (root-relative, '' for home) to a dist asset path
function relFromPage(pageDir, assetPath) {
  const r = P.relative(pageDir || '.', assetPath);
  return r.startsWith('.') ? r : (pageDir ? r : './' + r);
}
function relFromCss(assetPath) { return P.relative('assets/css', assetPath); }

// Rewrite url(...) inside a CSS string. baseDir = source dir of that CSS (root-relative posix).
function rewriteCssUrls(css, baseDir) {
  return css.replace(/url\(\s*('[^']*'|"[^"]*"|[^)]*)\s*\)/gi, (full, inner) => {
    const r = resolveUrl(inner, baseDir);
    if (!r || r.kind === 'data') return full;
    if (r.kind === 'external') return full;
    const dp = mapResource(r.resPath);
    if (!dp) return full;
    return `url(${relFromCss(dp)})`;
  }).replace(/@import\s+(['"])([^'"]+)\1/gi, (full, q, href) => {
    // leave @imports of external; local handled by inlining elsewhere if any
    return full;
  });
}

function rewriteSrcset(val, pageDir) {
  return val.split(',').map(part => {
    const seg = part.trim();
    if (!seg) return null;
    const sp = seg.split(/\s+/);
    const r = resolveUrl(sp[0], pageDir);
    if (r && r.kind === 'local') {
      const dp = mapResource(r.resPath);
      if (dp) sp[0] = relFromPage(pageDir, dp);
    }
    return sp.join(' ');
  }).filter(Boolean).join(', ');
}

function rewriteInlineStyle(style, pageDir) {
  return style.replace(/url\(\s*('[^']*'|"[^"]*"|[^)]*)\s*\)/gi, (full, inner) => {
    const r = resolveUrl(inner, pageDir);
    if (!r || r.kind !== 'local') return full;
    const dp = mapResource(r.resPath);
    if (!dp) return full;
    return `url(${relFromPage(pageDir, dp)})`;
  });
}

const PURGE_SAFELIST = {
  standard: [
    'animated', 'elementor-invisible', /-active$/, /active$/, /is-active/, /-open$/,
    /opened$/, /-show$/, /shown$/, 'sticky', /scrolled/, /toggled/, /lazyloaded/, /lazyloading/,
    /^elementor-/, /^e-/, /^swiper/, /^ct-/, /^wpforms/, /^menu/, /^sub-menu/, /^current[-_]/,
    /^fadeIn/, /^fadeOut/, /^slideIn/, /^slideOut/, /^zoomIn/, /^bounce/, /^flip/, /^bob/, /^pulse/,
    /^screen-reader/, 'html', 'body',
  ],
  greedy: [/elementor/, /swiper/, /wpforms/, /^ct-/, /^e-con/, /animat/, /lazyload/, /^fadeIn/, /bob/],
};

function escapeRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
// Substring/attribute class selectors ([class*=x], [class^=x], [class~=x]) can't be
// evaluated by PurgeCSS from static HTML -> collect their values and safelist them.
function attrClassSubstrings(css) {
  const out = new Set();
  const re = /\[class[*^$~|]?=\s*(['"]?)([^'"\]\s]+)\1\s*[iIsS]?\]/g;
  let m;
  while ((m = re.exec(css))) out.add(m[2]);
  return [...out];
}

async function buildPageCss(name, cssChunks, htmlString, pageDir) {
  let combined = '';
  for (const c of cssChunks) combined += '\n' + rewriteCssUrls(c.css, c.baseDir);
  report.cssBefore += Buffer.byteLength(combined);
  let purged = combined;
  try {
    const subs = attrClassSubstrings(combined).map(s => new RegExp(escapeRegex(s)));
    const safelist = {
      standard: PURGE_SAFELIST.standard,
      greedy: [...PURGE_SAFELIST.greedy, ...subs],
    };
    const res = await new PurgeCSS().purge({
      content: [{ raw: htmlString, extension: 'html' }],
      css: [{ raw: combined }],
      safelist,
      keyframes: false, fontFace: false, variables: false,
    });
    if (res && res[0] && res[0].css) purged = res[0].css;
  } catch (e) { console.warn('  PurgeCSS skipped for', name, '-', e.message); }
  const min = new CleanCSS({ level: 2, rebase: false }).minify(purged);
  const out = min.styles || purged;
  report.cssAfter += Buffer.byteLength(out);
  const distPath = `assets/css/${name}.min.css`;
  await fsp.mkdir(path.join(DIST, 'assets', 'css'), { recursive: true });
  await fsp.writeFile(path.join(DIST, distPath), out);
  return distPath;
}

function stripCruft($) {
  const sel = [
    'link[rel="profile"]', 'link[rel="pingback"]', 'link[rel="shortlink"]',
    'link[rel="EditURI"]', 'link[rel="wlwmanifest"]', 'link[rel="https://api.w.org/"]',
    'meta[name="generator"]',
  ];
  sel.forEach(s => $(s).remove());
  $('link[rel="alternate"]').each((i, el) => {
    const t = ($(el).attr('type') || '').toLowerCase();
    if (/rss|oembed|application\/json$|xml\+oembed/.test(t)) $(el).remove();
  });
  $('link[rel="dns-prefetch"]').each((i, el) => {
    const h = ($(el).attr('href') || '');
    if (/s\.w\.org|wp\.com|gravatar/.test(h)) $(el).remove();
  });
  // WordPress emoji + embed scripts/styles
  $('script').each((i, el) => {
    const s = ($(el).attr('src') || '') + ($(el).html() || '');
    if (/wp-emoji|wpemoji|wp-embed\.min\.js|concatemoji/.test(s)) $(el).remove();
  });
  $('style').each((i, el) => {
    const c = $(el).html() || '';
    if (/wp-emoji|emoji/.test(c) && c.length < 600) $(el).remove();
  });
  // strip HTML comments
  $('*').contents().each(function () {
    if (this.type === 'comment') $(this).remove();
  });
}

async function processPage(page) {
  const html = await fsp.readFile(page.htmlPath, 'utf8');
  const $ = cheerio.load(html, { decodeEntities: false });
  const pageDir = page.slug; // '' for home

  stripCruft($);

  // ---- collect CSS (document order), skip external + noscript ----
  const cssChunks = [];
  let firstCssNode = null;
  const cssToRemove = [];
  $('link[rel="stylesheet"], style').each((i, el) => {
    const $el = $(el);
    if ($el.parents('noscript').length) return;
    if (el.tagName === 'link') {
      const href = $el.attr('href') || '';
      const r = resolveUrl(href, pageDir);
      if (!r || r.kind !== 'local') return; // external font CDN stays
      try {
        const css = fs.readFileSync(path.join(ROOT, r.resPath), 'utf8');
        cssChunks.push({ css, baseDir: P.dirname(r.resPath) });
        if (!firstCssNode) firstCssNode = el;
        cssToRemove.push(el);
      } catch (e) { /* missing file -> drop link silently */ cssToRemove.push(el); }
    } else { // <style>
      cssChunks.push({ css: $el.html() || '', baseDir: pageDir });
      if (!firstCssNode) firstCssNode = el;
      cssToRemove.push(el);
    }
  });

  // noscript stylesheet -> repath file, keep tag
  $('noscript link[rel="stylesheet"]').each((i, el) => {
    const href = $(el).attr('href') || '';
    const r = resolveUrl(href, pageDir);
    if (r && r.kind === 'local') {
      const clean = r.resPath;
      const dp = 'assets/css/' + P.basename(clean);
      filesNeeded.set(clean, dp); // copy raw
      $(el).attr('href', relFromPage(pageDir, dp));
    }
  });

  // ---- relocate external JS, leave inline scripts ----
  $('script').each((i, el) => {
    const $el = $(el);
    if ($el.parents('noscript').length) return;
    const src = $el.attr('src');
    if (!src) return;
    const type = ($el.attr('type') || '').toLowerCase();
    if (type && !['text/javascript', 'application/javascript', 'module', ''].includes(type)) return;
    const r = resolveUrl(src, pageDir);
    if (!r || r.kind !== 'local') return;
    let dp;
    if (EL_CORE_RE.test(r.resPath)) {
      dp = 'assets/elementor/js/' + P.basename(r.resPath);
      elementorCore.add(r.resPath);
    } else {
      dp = mapJs(r.resPath);
    }
    $el.attr('src', relFromPage(pageDir, dp));
  });

  // ---- rewrite framework chunk publicPaths to local (Elementor + Blocksy) ----
  const elAssets = (relFromPage(pageDir, 'assets/elementor') + '/');
  const ctBundle = (relFromPage(pageDir, 'assets/js/blocksy') + '/');
  $('script').each((i, el) => {
    const node = el.children && el.children[0];
    if (!node || typeof node.data !== 'string') return;
    let d = node.data;
    if (d.includes('elementorFrontendConfig') && d.includes('"assets"')) {
      d = d.replace(/("assets":")[^"]*(")/, `$1${elAssets}$2`);
    }
    if (d.includes('ct_localizations') && d.includes('"public_url"')) {
      d = d.replace(/("public_url":")[^"]*(")/, `$1${ctBundle}$2`);
    }
    // Blocksy lazy-load registry: quoted paths to theme/plugin static bundle assets
    // (keys: url, back_to_top, lazy_load, search_lazy, ...) -> local copies
    d = d.replace(/"(\.\.?\/[^"]*static\/bundle\/[^"]+\.(?:css|js))"/g, (full, rawpath) => {
      const r = resolveUrl(rawpath, pageDir);
      if (!r || r.kind !== 'local') return full;
      const base = P.basename(r.resPath);
      if (/\.js$/i.test(r.resPath)) {
        const dp = 'assets/js/' + base;
        filesNeeded.set(r.resPath, dp);
        return '"' + relFromPage(pageDir, dp) + '"';
      }
      const dp = 'assets/css/lazy/' + base;
      standaloneCss.set(r.resPath, dp);
      return '"' + relFromPage(pageDir, dp) + '"';
    });
    if (d !== node.data) node.data = d;
  });

  // ---- images: src / srcset / data attrs ----
  $('img, source').each((i, el) => {
    const $el = $(el);
    ['src', 'data-src', 'data-lazy-src'].forEach(a => {
      const v = $el.attr(a);
      if (v) { const r = resolveUrl(v, pageDir); if (r && r.kind === 'local') { const dp = mapResource(r.resPath); if (dp) $el.attr(a, relFromPage(pageDir, dp)); } }
    });
    ['srcset', 'data-srcset', 'data-lazy-srcset'].forEach(a => {
      const v = $el.attr(a);
      if (v) $el.attr(a, rewriteSrcset(v, pageDir));
    });
  });
  // favicons / apple-touch / generic icon links
  $('link[rel*="icon"], link[rel="apple-touch-icon"]').each((i, el) => {
    const v = $(el).attr('href'); if (!v) return;
    const r = resolveUrl(v, pageDir); if (r && r.kind === 'local') { const dp = mapResource(r.resPath); if (dp) $(el).attr('href', relFromPage(pageDir, dp)); }
  });
  // anchors to local documents (pdf, etc.)
  $('a[href]').each((i, el) => {
    const v = $(el).attr('href');
    const r = resolveUrl(v, pageDir);
    if (r && r.kind === 'local' && DOC_EXT.test(r.resPath)) {
      const dp = mapResource(r.resPath);
      if (dp) $(el).attr('href', relFromPage(pageDir, dp));
    }
  });
  // inline background-image styles
  $('[style]').each((i, el) => {
    const s = $(el).attr('style');
    if (s && /url\(/i.test(s)) $(el).attr('style', rewriteInlineStyle(s, pageDir));
  });

  // ---- build the page CSS bundle & swap nodes ----
  const cssName = page.slug ? page.slug : 'home';
  const htmlForPurge = $.html();
  const cssDist = await buildPageCss(cssName, cssChunks, htmlForPurge, pageDir);
  if (firstCssNode) {
    $(firstCssNode).before(`<link rel="stylesheet" href="${relFromPage(pageDir, cssDist)}" />\n`);
  } else {
    $('head').append(`<link rel="stylesheet" href="${relFromPage(pageDir, cssDist)}" />\n`);
  }
  cssToRemove.forEach(el => $(el).remove());

  // ---- write HTML ----
  const outDir = path.join(DIST, pageDir);
  await fsp.mkdir(outDir, { recursive: true });
  await fsp.writeFile(path.join(outDir, 'index.html'), $.html());
  report.pages.push(page.slug || '(home)');
}

// ---------- asset copy / download ----------
function get(url, redirects = 0) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (StaticBuild)' } }, res => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && redirects < 5) {
        res.resume(); return resolve(get(new URL(res.headers.location, url).href, redirects + 1));
      }
      if (res.statusCode !== 200) { res.resume(); return reject(new Error('HTTP ' + res.statusCode)); }
      const chunks = []; res.on('data', d => chunks.push(d));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', reject);
  });
}

async function pool(items, n, fn) {
  const it = items[Symbol.iterator]();
  const workers = Array.from({ length: n }, async () => {
    for (let r = it.next(); !r.done; r = it.next()) await fn(r.value);
  });
  await Promise.all(workers);
}

async function copyLocal(resPath, distPath, failBucket) {
  const src = path.join(ROOT, resPath);
  const dst = path.join(DIST, distPath);
  await fsp.mkdir(path.dirname(dst), { recursive: true });
  try {
    await fsp.copyFile(src, dst);
  } catch (e) {
    try { const buf = await get(LIVE + resPath); await fsp.writeFile(dst, buf); }
    catch (e2) { report[failBucket].push(resPath); }
  }
}

async function run() {
  // Clean dist *contents* (not the dir itself) so an open Explorer/terminal handle
  // on dist/ doesn't block the rebuild with EBUSY.
  await fsp.mkdir(DIST, { recursive: true });
  for (const e of await fsp.readdir(DIST)) {
    await fsp.rm(path.join(DIST, e), { recursive: true, force: true, maxRetries: 10, retryDelay: 300 });
  }

  // discover pages
  const pages = [];
  if (fs.existsSync(path.join(ROOT, 'index.html'))) pages.push({ slug: '', htmlPath: path.join(ROOT, 'index.html') });
  for (const ent of await fsp.readdir(ROOT, { withFileTypes: true })) {
    if (!ent.isDirectory() || BLOCK_DIRS.has(ent.name)) continue;
    const idx = path.join(ROOT, ent.name, 'index.html');
    if (fs.existsSync(idx)) pages.push({ slug: ent.name, htmlPath: idx });
  }
  console.log('Pages:', pages.length);
  for (const p of pages) { await processPage(p); }

  // lazy/standalone CSS (Blocksy back_to_top, non-critical, flexy, ...): rebase url() + minify.
  // Done before image/font pools so newly referenced assets get copied.
  if (standaloneCss.size) {
    await fsp.mkdir(path.join(DIST, 'assets', 'css', 'lazy'), { recursive: true });
    for (const [resPath, dp] of standaloneCss) {
      let css;
      try { css = fs.readFileSync(path.join(ROOT, resPath), 'utf8'); }
      catch { try { css = (await get(LIVE + resPath)).toString('utf8'); } catch { continue; } }
      const rebased = rewriteCssUrls(css, P.dirname(resPath));
      const min = new CleanCSS({ level: 2, rebase: false }).minify(rebased);
      await fsp.writeFile(path.join(DIST, dp), min.styles || rebased);
    }
    console.log('Lazy CSS        :', standaloneCss.size);
  }

  // process JS (copy + terser)
  console.log('JS files:', jsNeeded.size);
  await pool([...jsNeeded.entries()], 6, async ([resPath, distPath]) => {
    const dst = path.join(DIST, distPath);
    await fsp.mkdir(path.dirname(dst), { recursive: true });
    let code;
    try { code = await fsp.readFile(path.join(ROOT, resPath), 'utf8'); }
    catch { try { code = (await get(LIVE + resPath)).toString('utf8'); } catch { return; } }
    try {
      const out = await minify(code, { compress: true, mangle: false });
      await fsp.writeFile(dst, out.code || code);
    } catch { await fsp.writeFile(dst, code); }
    report.jsFiles++;
  });

  // images
  console.log('Images:', imagesNeeded.size);
  await pool([...imagesNeeded.entries()], 8, async ([r, d]) => { await copyLocal(r, d, 'imgFail'); report.images++; });
  // docs + noscript css raw copies
  await pool([...filesNeeded.entries()], 6, async ([r, d]) => { await copyLocal(r, d, 'imgFail'); report.docs++; });
  // fonts (download from live)
  console.log('Fonts:', fontsNeeded.size);
  await pool([...fontsNeeded.entries()], 8, async ([r, d]) => {
    const dst = path.join(DIST, d);
    await fsp.mkdir(path.dirname(dst), { recursive: true });
    try { const buf = await get(LIVE + r); await fsp.writeFile(dst, buf); report.fonts++; }
    catch (e) {
      try { await fsp.copyFile(path.join(ROOT, r), dst); report.fonts++; }
      catch { report.fontFail.push(r); }
    }
  });

  // ---- Blocksy: copy webpack bundle chunks locally ----
  const ctSrc = path.join(ROOT, BLOCKSY_BUNDLE);
  const ctDst = path.join(DIST, 'assets', 'js', 'blocksy');
  let ctCount = 0;
  if (fs.existsSync(ctSrc)) {
    await fsp.mkdir(ctDst, { recursive: true });
    for (const f of await fsp.readdir(ctSrc)) {
      if (f.endsWith('.js')) { await fsp.copyFile(path.join(ctSrc, f), path.join(ctDst, f)); ctCount++; }
    }
  }
  console.log('Blocksy chunks  :', ctCount);

  // ---- Elementor: fetch current self-consistent JS set (core + chunks) from live ----
  const elDir = path.join(DIST, 'assets', 'elementor', 'js');
  await fsp.mkdir(elDir, { recursive: true });
  let elCount = 0;
  try {
    const core = ['webpack.runtime.min.js', 'frontend-modules.min.js', 'frontend.min.js'];
    let runtimeTxt = '';
    for (const f of core) {
      const buf = await get(EL_JS + f);
      if (f === 'webpack.runtime.min.js') runtimeTxt = buf.toString('utf8');
      await fsp.writeFile(path.join(elDir, f), buf); elCount++;
    }
    // chunk filenames are quoted *.js literals inside the runtime's chunk-url builder
    const chunks = [...new Set((runtimeTxt.match(/"[A-Za-z0-9_.\-]+\.js"/g) || []).map(s => s.slice(1, -1)))]
      .filter(f => /\.js$/.test(f) && !core.includes(f));
    await pool(chunks, 8, async f => {
      try { await fsp.writeFile(path.join(elDir, f), await get(EL_JS + f)); elCount++; }
      catch (e) { report.fontFail.push('el-chunk ' + f); }
    });
    console.log('Elementor JS    :', elCount, '(core + ' + chunks.length + ' chunks)');
  } catch (e) { console.warn('Elementor fetch failed:', e.message); }

  // report
  const kb = n => (n / 1024).toFixed(1) + ' KB';
  console.log('\n==== BUILD REPORT ====');
  console.log('Pages built     :', report.pages.length);
  console.log('JS files        :', report.jsFiles);
  console.log('Images copied   :', report.images, '(fail:', report.imgFail.length + ')');
  console.log('Docs copied     :', report.docs);
  console.log('Fonts localized :', report.fonts, '(fail:', report.fontFail.length + ')');
  console.log('CSS total before:', kb(report.cssBefore));
  console.log('CSS total after :', kb(report.cssAfter), '(' + (100 - report.cssAfter / report.cssBefore * 100).toFixed(1) + '% smaller)');
  if (report.fontFail.length) console.log('Font failures   :', report.fontFail.slice(0, 10));
  if (report.imgFail.length) console.log('Image failures  :', report.imgFail.slice(0, 10));
  await fsp.writeFile(path.join(DIST, 'build-report.json'), JSON.stringify(report, null, 2));
}

run().catch(e => { console.error(e); process.exit(1); });
