"""Build the profile header from the public GitHub avatar. No generated portrait."""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
from html import escape
from PIL import Image, ImageOps, ImageEnhance

OUT = Path("assets")
OUT.mkdir(exist_ok=True)
request = Request("https://avatars.githubusercontent.com/u/273518122?v=4&s=512", headers={"User-Agent": "Thrash-PRX-profile"})
with urlopen(request, timeout=30) as response:
    image = Image.open(BytesIO(response.read())).convert("RGB")
image = ImageOps.fit(image, (54, 36))
image = ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(1.35)
# A light character represents a dark pixel, preserving the portrait on dark backgrounds.
ramp = " .,:;irsXA253hMHGS#9B&@"
portrait = ["".join(ramp[min(len(ramp)-1, int(image.getpixel((x,y))/256*len(ramp)))] for x in range(54)) for y in range(36)]
letters = {
"H":["##   ##","##   ##","#######","##   ##","##   ##"],
"A":[" ##### ","##   ##","#######","##   ##","##   ##"],
"N":["##   ##","###  ##","## # ##","##  ###","##   ##"],
"I":["#######","   ##  ","   ##  ","   ##  ","#######"],
"F":["#######","##     ","#####  ","##     ","##     "]}
name = ["  ".join(letters[c][row] for c in "HANIF") for row in range(5)]
for theme, bg, fg, muted, edge, accent in [
    ("dark","#0d1117","#d7e4ee","#8b949e","#30363d","#79c0ff"),
    ("light","#ffffff","#24292f","#57606a","#d0d7de","#0969da")
]:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="358" viewBox="0 0 960 358" role="img" aria-labelledby="title desc"><title id="title">Shaik Hanif / Thrash</title><desc id="desc">ASCII portrait from Hanif\'s GitHub avatar beside his name in a terminal. Computer Science at VIT-AP. Web, browser tools and hardware.</desc>',
    f'<rect x="1" y="1" width="958" height="356" rx="6" fill="{bg}" stroke="{edge}"/>',
    f'<path d="M1 42H959 M330 42V357" stroke="{edge}"/>',
    f'<g font-family="monospace" fill="{muted}" font-size="12"><text x="24" y="27">hanif@thrash-prx: ~</text><text x="777" y="27">PROFILE / 01</text></g>']
    for y, line in enumerate(portrait):
        parts.append(f'<text x="23" y="{64+y*7.5}" xml:space="preserve" font-family="monospace" font-size="8.4" fill="{fg}">{escape(line)}</text>')
    parts.append(f'<g font-family="monospace" font-size="12" fill="{muted}"><text x="365" y="83">$ whoami</text></g>')
    for y, line in enumerate(name):
        parts.append(f'<text x="365" y="{117+y*16}" xml:space="preserve" font-family="monospace" font-size="13" fill="{accent}">{escape(line)}</text>')
    for y, (line, color) in enumerate([
        ("SHAIK HANIF / THRASH", fg),
        ("Computer Science @ VIT-AP", muted),
        ("Web interfaces. Browser tools. Hardware.", muted)
    ]):
        parts.append(f'<text x="365" y="{226+y*24}" font-family="monospace" font-size="13" fill="{color}">{escape(line)}</text>')
    parts.append(f'<text x="365" y="326" font-family="monospace" font-size="12" fill="{accent}">$ <tspan fill="{muted}">ls projects/</tspan> _</text></svg>')
    (OUT / f"profile-{theme}.svg").write_text("".join(parts), encoding="utf-8")
