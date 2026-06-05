const path = require('path');
const DIST = path.resolve(__dirname, '..', 'dist');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = path.join(__dirname, 'shots');
require('fs').mkdirSync(OUT, { recursive: true });

const targets = [
  ['home', 'index.html'],
  ['contact', 'contact/index.html'],
  ['formations', 'formations/index.html'],
  ['article', 'le-secret-professionnel-et-son-partage-entre-ethique-et-deontologie/index.html'],
];

(async () => {
  const puppeteer = (await import('puppeteer-core')).default;
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox', '--allow-file-access-from-files'] });
  for (const [name, rel] of targets) {
    const page = await browser.newPage();
    const fails = [];
    page.on('requestfailed', r => fails.push(r.url().replace(/^file:\/\/\//, '') + ' (' + (r.failure() || {}).errorText + ')'));
    page.on('pageerror', e => fails.push('JS:' + e.message.split('\n')[0]));
    const url = 'file:///' + path.join(DIST, rel).replace(/\\/g, '/');
    // desktop
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 }).catch(e => console.log(name, 'goto warn', e.message));
    // scroll through to trigger IntersectionObserver animations/counters
    await page.evaluate(async () => {
      await new Promise(res => {
        let y = 0; const step = window.innerHeight * 0.6;
        const t = setInterval(() => { window.scrollBy(0, step); y += step; if (y >= document.body.scrollHeight) { clearInterval(t); res(); } }, 120);
      });
    });
    await new Promise(r => setTimeout(r, 1500));
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(OUT, name + '-desktop.png'), fullPage: true });
    // mobile
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1, isMobile: true });
    await page.reload({ waitUntil: 'networkidle2', timeout: 60000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(OUT, name + '-mobile.png'), fullPage: false });
    // collect console/page errors + failed requests
    const uniq = [...new Set(fails)].filter(f => !/fonts\.(googleapis|gstatic)|gravatar|2aformation\.com/.test(f));
    console.log('shot:', name, '| issues:', uniq.length ? uniq.slice(0, 8) : 'none');
    await page.close();
  }
  await browser.close();
  console.log('done');
})().catch(e => { console.error(e); process.exit(1); });
