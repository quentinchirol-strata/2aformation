const path = require('path');
const DIST = path.resolve(__dirname, '..', 'dist');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const OUT = path.join(__dirname, 'shots');

(async () => {
  const puppeteer = (await import('puppeteer-core')).default;
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--no-sandbox', '--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });
  const url = 'file:///' + path.join(DIST, 'index.html').replace(/\\/g, '/');
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
  await new Promise(r => setTimeout(r, 1000));
  // find the VISIBLE (desktop) "Se Former" parent menu item
  const box = await page.evaluate(() => {
    const lis = [...document.querySelectorAll('.menu-item-has-children')].filter(e => /se former/i.test(e.textContent));
    const li = lis.find(e => e.getBoundingClientRect().width > 0) || lis[0];
    if (!li) return null;
    const r = li.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  });
  if (box) { await page.mouse.move(box.x - 3, box.y); await new Promise(r => setTimeout(r, 200)); await page.mouse.move(box.x, box.y); }
  else console.log('Se Former item not found');
  await new Promise(r => setTimeout(r, 1200));
  await page.screenshot({ path: path.join(OUT, 'menu-hover.png'), clip: { x: 0, y: 0, width: 1440, height: 420 } });
  // report submenu geometry
  const geo = await page.evaluate(() => {
    const lis = [...document.querySelectorAll('.menu-item-has-children')].filter(e => /se former/i.test(e.textContent));
    const li = lis.find(e => e.getBoundingClientRect().width > 0) || lis[0];
    if (!li) return 'no li';
    const sub = li.querySelector('.sub-menu');
    if (!sub) return 'no submenu';
    const lr = li.getBoundingClientRect(), sr = sub.getBoundingClientRect();
    const cs = getComputedStyle(sub), cl = getComputedStyle(li);
    return {
      liClass: li.className, hasDataSubmenu: li.hasAttribute('data-submenu'), hasCtActive: li.classList.contains('ct-active'),
      liLeft: Math.round(lr.left), subLeft: Math.round(sr.left), subTop: Math.round(sr.top),
      subPos: cs.position, liPos: cl.position, subVisible: cs.visibility, subOpacity: cs.opacity,
    };
  });
  console.log('submenu geometry:', JSON.stringify(geo));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
