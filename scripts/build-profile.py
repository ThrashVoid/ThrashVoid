"""Generate the public GitHub calendar, statistics, and line-reveal ASCII artwork."""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
from html import escape
from datetime import date, datetime, timezone, timedelta
from collections import defaultdict
import calendar
import json
import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps, ImageEnhance

OUT = Path("assets")
OUT.mkdir(exist_ok=True)
LOGIN = "Thrash-PRX"

def get_json(url, payload=None):
    headers = {"User-Agent": "thrash-profile-artwork", "Accept": "application/json"}
    if payload is not None:
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
        headers["Content-Type"] = "application/json"
    req = Request(url, data=json.dumps(payload).encode() if payload else None, headers=headers)
    with urlopen(req, timeout=40) as response:
        return json.load(response)

result = get_json("https://api.github.com/graphql", {
    "query": "query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
    "variables": {"login": LOGIN}
})
if result.get("errors"):
    raise RuntimeError("GitHub did not return a complete public contribution calendar")
days = [d for w in result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
assert days and all(isinstance(d["contributionCount"], int) and d["contributionCount"] >= 0 for d in days)
days.sort(key=lambda d: d["date"])
counts = {date.fromisoformat(d["date"]): d["contributionCount"] for d in days}
total = sum(counts.values())
active = sum(v > 0 for v in counts.values())
longest = run = 0
for value in counts.values():
    run = run + 1 if value else 0
    longest = max(longest, run)
anchor = max(counts)
if not counts[anchor]:
    anchor -= timedelta(days=1)
current = 0
while counts.get(anchor, 0) > 0:
    current += 1
    anchor -= timedelta(days=1)
months = defaultdict(int)
for day, count in counts.items():
    months[(day.year, day.month)] += count
month_keys = list(months)[-12:]
best = max(counts.values())
stamp = max(counts).isoformat()

source = OUT / "portrait-source.png"
if source.exists():
    image = Image.open(source).convert("RGB")
else:
    req = Request("https://avatars.githubusercontent.com/u/273518122?v=4&s=512", headers={"User-Agent": "thrash-profile-artwork"})
    with urlopen(req, timeout=30) as response:
        image = Image.open(BytesIO(response.read())).convert("RGB")
# Portrait dimensions are independent of the original image resolution.
image = ImageOps.fit(image, (160, 96), centering=(0.5, 0.45))
image = ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(1.3)
ramp = " .,:;irsXA253hMHGS#9B&@"
ascii_rows = ["".join(ramp[min(len(ramp)-1,int(image.getpixel((x,y))/256*len(ramp)))] for x in range(160)) for y in range(96)]
THEMES = {
    "dark": dict(bg="#0d1117", fg="#e6edf3", muted="#8b949e", edge="#30363d", accent="#79c0ff", green=["#161b22","#0e4429","#006d32","#26a641","#39d353"]),
    "light": dict(bg="#ffffff", fg="#1f2328", muted="#656d76", edge="#d0d7de", accent="#0969da", green=["#ebedf0","#9be9a8","#40c463","#30a14e","#216e39"])
}
STYLE = """
.reveal{animation:reveal 12s linear infinite}
@keyframes reveal{0%{clip-path:inset(0 100% 0 0)}5%,95%{clip-path:inset(0 0 0 0)}100%{clip-path:inset(0 100% 0 0)}}
.cell{animation:cell .35s ease-out both}
@keyframes cell{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
.bar{transform-box:fill-box;transform-origin:bottom;animation:grow 1s ease-out both}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.number{animation:appear 1s ease-out both}
@keyframes appear{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@media(prefers-reduced-motion:reduce){.reveal,.cell,.bar,.number{animation:none!important;clip-path:none!important;opacity:1!important;transform:none!important}}
"""
def start(w,h,title,t):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}"><style>{STYLE}</style><rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="8" fill="{t["bg"]}" stroke="{t["edge"]}"/>']
def text(parts,x,y,value,t,size=20,color=None,extra=""):
    parts.append(f'<text x="{x}" y="{y}" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="{size}" fill="{color or t["fg"]}" {extra}>{escape(str(value))}</text>')
def save(name,parts):
    content="".join(parts)+"</svg>"
    ET.fromstring(content)
    (OUT/name).write_text(content,encoding="utf-8")

for theme,t in THEMES.items():
    # Full-width animated contribution calendar.
    p=start(880,250,"Public GitHub contribution calendar",t)
    text(p,26,34,"CONTRIBUTIONS",t,13,t["muted"],'letter-spacing="2"')
    text(p,854,34,str(total)+" / PUBLIC LAST YEAR",t,13,t["muted"],'text-anchor="end"')
    first=min(counts)
    origin=first-timedelta(days=(first.weekday()+1)%7)
    last_month=None
    for day,count in counts.items():
        week=(day-origin).days//7
        row=(day.weekday()+1)%7
        x,y=48+week*15,76+row*15
        month=(day.year,day.month)
        if month!=last_month:
            text(p,x,62,calendar.month_abbr[day.month],t,10,t["muted"])
            last_month=month
        level=0 if count==0 else 1 if count<=2 else 2 if count<=5 else 3 if count<=10 else 4
        p.append(f'<rect class="cell" style="animation-delay:{week*.018+row*.012:.3f}s" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{t["green"][level]}"><title>{day.isoformat()}: {count} contributions</title></rect>')
    text(p,18,102,"M",t,9,t["muted"])
    text(p,18,132,"W",t,9,t["muted"])
    text(p,18,162,"F",t,9,t["muted"])
    text(p,26,222,f"{active} active days",t,12,t["muted"])
    text(p,854,222,f"Updated {stamp}",t,12,t["muted"],'text-anchor="end"')
    save(f"calendar-{theme}.svg",p)

    # Large ASCII illustration, revealed row by row.
    p=start(840,880,"Hanif — animated ASCII artwork",t)
    text(p,30,42,"HANIF",t,17,t["fg"],'letter-spacing="4"')
    text(p,810,42,"THRASH-PRX",t,13,t["muted"],'text-anchor="end" letter-spacing="2"')
    for y,line in enumerate(ascii_rows):
        delay=y*.025
        text(p,20,86+y*7.75,line,t,7.3,t["fg"],f'class="reveal" style="animation-delay:{delay:.3f}s" xml:space="preserve" textLength="800" lengthAdjust="spacing"')
    save(f"portrait-{theme}.svg",p)

    # Equal-height stats panel, derived exclusively from the calendar.
    p=start(840,880,"GitHub contribution statistics",t)
    text(p,38,48,"PUBLIC / LAST YEAR",t,17,t["muted"],'letter-spacing="2"')
    metrics=[(total,"CONTRIBUTIONS"),(active,"ACTIVE DAYS"),(current,"CURRENT STREAK"),(longest,"LONGEST STREAK")]
    for i,(value,label) in enumerate(metrics):
        x=44+(i%2)*398
        y=168+(i//2)*205
        text(p,x,y,value,t,80,t["accent"],f'class="number" style="animation-delay:{.15+i*.14}s" font-weight="700"')
        text(p,x,y+40,label,t,16,t["muted"],'letter-spacing="1"')
    p.append(f'<path d="M38 500H802" stroke="{t["edge"]}"/>')
    text(p,44,548,"CONTRIBUTIONS / MONTH",t,17,t["muted"],'letter-spacing="1"')
    max_month=max(months[k] for k in month_keys) or 1
    slot=748/12
    for i,key in enumerate(month_keys):
        x=48+i*slot
        val=months[key]
        height=215*val/max_month
        if val:
            p.append(f'<rect class="bar" style="animation-delay:{.3+i*.055}s" x="{x:.2f}" y="{802-height:.2f}" width="32" height="{height:.2f}" rx="2" fill="{t["accent"]}"/>')
            text(p,x+16,790-height,val,t,13,t["fg"],'text-anchor="middle"')
        text(p,x+16,833,calendar.month_abbr[key[1]][0],t,14,t["muted"],'text-anchor="middle"')
    text(p,44,866,f"Best day: {best} contributions",t,12,t["muted"])
    text(p,798,866,stamp,t,12,t["muted"],'text-anchor="end"')
    save(f"stats-{theme}.svg",p)

Path("data").mkdir(exist_ok=True)
Path("data/activity.json").write_text(json.dumps({"login":LOGIN,"capturedAt":datetime.now(timezone.utc).isoformat(),"source":"GitHub public contribution calendar","days":days},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"total":total,"active_days":active,"current_streak":current,"longest_streak":longest,"updated":stamp,"artwork_files":6,"portrait_source":"photo" if source.exists() else "public avatar"}))
