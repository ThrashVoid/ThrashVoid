import { readFile, writeFile, mkdir } from 'node:fs/promises';

const activity = JSON.parse(await readFile(new URL('../data/activity.json', import.meta.url), 'utf8'));
const days = [...activity.days].sort((a, b) => a.date.localeCompare(b.date));
if (!days.length || days.length > 371 || days.some(d => !/^\d{4}-\d{2}-\d{2}$/.test(d.date) || !Number.isInteger(d.contributionCount) || d.contributionCount < 0)) throw new Error('Invalid activity data');
const total = days.reduce((s, d) => s + d.contributionCount, 0);
const active = days.filter(d => d.contributionCount > 0).length;
const best = Math.max(...days.map(d => d.contributionCount));
let streak = 0, longest = 0;
for (const d of days) { streak = d.contributionCount > 0 ? streak + 1 : 0; longest = Math.max(longest, streak); }
const escape = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[c]);
const start = new Date(days[0].date + 'T00:00:00Z');
const offset = start.getUTCDay();
const colors = ['#28323b', '#986026', '#d58e33', '#ffb648', '#ffe3a1'];
const pellets = days.map((d, i) => {
  const n = offset + i;
  const x = 70 + Math.floor(n / 7) * 15;
  const y = 246 + (n % 7) * 15;
  const level = d.contributionCount === 0 ? 0 : d.contributionCount <= 2 ? 1 : d.contributionCount <= 4 ? 2 : d.contributionCount <= 7 ? 3 : 4;
  const size = level ? 4.2 : 1.7;
  return `<circle cx="${x}" cy="${y}" r="${size}" fill="${colors[level]}"><title>${escape(d.date)}: ${d.contributionCount} public contributions</title></circle>`;
}).join('');
const stats = [[total, 'CONTRIBUTIONS'], [active, 'ACTIVE DAYS'], [best, 'BEST DAY'], [longest, 'BEST STREAK']].map(([value, label], i) => {
  const x = 62 + i * 211;
  return `<g transform="translate(${x} 423)"><text class="stat" y="0">${value}</text><text class="label" y="22">${label}</text></g>`;
}).join('');
const date = new Date(activity.capturedAt).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata' }).toUpperCase();
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 500" role="img" aria-labelledby="title desc">
<title id="title">Shaik Hanif - Thrash. Build. Play. Repeat.</title>
<desc id="desc">An arcade inspired calendar of ${total} public contributions across ${active} active days. Best day ${best}; best streak ${longest} days. Snapshot ${escape(date)}.</desc>
<style>
text { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: #edf0f2; }
.mono,.label { font-family: 'Courier New', monospace; letter-spacing: 2px; }
.label { font-size: 10px; fill: #a5b1be; }
.stat { font-size: 32px; font-weight: 700; }
.runner { animation: travel 14s ease-in-out infinite; }
.ghost { animation: follow 14s ease-in-out infinite; }
@keyframes travel { 0%,10% { transform: translateX(0); } 48%,58% { transform: translateX(630px); } 90%,100% { transform: translateX(0); } }
@keyframes follow { 0%,10% { transform: translateX(0); } 48%,58% { transform: translateX(590px); } 90%,100% { transform: translateX(0); } }
@media (prefers-reduced-motion: reduce) { .runner,.ghost { animation: none; } }
</style>
<rect width="920" height="500" fill="#10161d"/>
<path d="M0 0H920" stroke="#ffb648" stroke-width="5"/>
<text class="mono" x="52" y="43" font-size="11" fill="#ffb648" style="fill:#ffb648">PLAYER 01 / THRASH-PRX</text>
<text class="label" x="868" y="43" text-anchor="end">SOFTWARE � HARDWARE � PLAY</text>
<text x="48" y="116" font-size="66" font-weight="800" letter-spacing="-2.5">SHAIK HANIF<tspan fill="#ffb648">.</tspan></text>
<text x="52" y="152" font-size="17" fill="#b4c0ca" style="fill:#b4c0ca">Building useful tools. Exploring how things work.</text>
<path d="M52 185H868" stroke="#2b3642"/>
<text class="label" x="52" y="213">PUBLIC ACTIVITY / LAST 365 DAYS</text>
<text class="label" x="868" y="213" text-anchor="end">${escape(date)}</text>
<path d="M52 231H868V353H52Z M61 239H859V345H61Z" stroke="#304959" stroke-width="1" fill="none"/>
${pellets}
<path d="M52 373H868" stroke="#2b3642"/>
${stats}
<path d="M52 465H868" stroke="#2b3642"/>
<g transform="translate(180 470)"><g class="ghost"><path d="M-12 13V4a8 8 0 0 1 16 0v9l-3-3-3 3-3-3-3 3z" fill="#7dc4d4"/><circle cx="-7" cy="3" r="2" fill="#10161d"/><circle cx="0" cy="3" r="2" fill="#10161d"/></g></g>
<g transform="translate(84 478)"><g class="runner"><path d="M0 0L8-6A10 10 0 1 0 8 6Z" fill="#ffb648"/></g></g>
<text class="mono" x="868" y="489" font-size="9" text-anchor="end" style="fill:#9daab7">BUILD. PLAY. REPEAT.</text>
</svg>`;
await mkdir(new URL('../assets/', import.meta.url), { recursive: true });
await writeFile(new URL('../assets/arcade.svg', import.meta.url), svg);
console.log(`Rendered public activity: ${total} contributions, ${active} active days.`);

