"""Render animated ASCII artwork from the public GitHub avatar."""
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
ramps = [" .,:;irsXA253hMHGS#9B&@", " .:;irssXX25hhMHG##B&@", " .,:;irrXA253hMHGS#B&@"]
letters = {
"H":["##   ##","##   ##","#######","##   ##","##   ##"],
"A":[" ##### ","##   ##","#######","##   ##","##   ##"],
"N":["##   ##","###  ##","## # ##","##  ###","##   ##"],
"I":["#######","   ##  ","   ##  ","   ##  ","#######"],
"F":["#######","##     ","#####  ","##     ","##     "]}
name = ["  ".join(letters[c][row] for c in "HANIF") for row in range(5)]
css = """
.frame0{animation:frame0 4.8s steps(1,end) infinite}
.frame1{opacity:0;animation:frame1 4.8s steps(1,end) infinite}
.frame2{opacity:0;animation:frame2 4.8s steps(1,end) infinite}
@keyframes frame0{0%,100%{opacity:1}33%,66%{opacity:0}}
@keyframes frame1{0%,66%,100%{opacity:0}33%{opacity:1}}
@keyframes frame2{0%,33%,100%{opacity:0}66%{opacity:1}}
.name{animation:reveal 1.1s steps(42,end) both}
@keyframes reveal{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@media(prefers-reduced-motion:reduce){
.frame0{animation:none;opacity:1}.frame1,.frame2{animation:none;opacity:0}
.name{animation:none;clip-path:none}
}
"""
for theme, bg, fg, muted, accent in [
    ("dark","#0d1117","#d7e4ee","#8b949e","#79c0ff"),
    ("light","#ffffff","#24292f","#57606a","#0969da")
]:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="title desc"><title id="title">Hanif / Thrash-PRX</title><desc id="desc">Animated ASCII avatar and name.</desc><style>{css}</style><rect width="960" height="300" fill="{bg}"/>']
    for y in range(36):
        for frame, ramp in enumerate(ramps):
            line = "".join(ramp[min(len(ramp)-1, int(image.getpixel((x,y))/256*len(ramp)))] for x in range(54))
            parts.append(f'<text class="frame{frame}" style="animation-delay:-{y*.11:.2f}s" x="28" y="{24+y*7.3}" xml:space="preserve" font-family="monospace" font-size="8.4" fill="{fg}">{escape(line)}</text>')
    parts.append('<g class="name">')
    for y, line in enumerate(name):
        parts.append(f'<text x="365" y="{110+y*16}" xml:space="preserve" font-family="monospace" font-size="13" fill="{accent}">{escape(line)}</text>')
    parts.append(f'</g><text x="365" y="225" font-family="monospace" font-size="13" letter-spacing="3" fill="{muted}">THRASH-PRX</text></svg>')
    (OUT / f"ascii-{theme}.svg").write_text("".join(parts), encoding="utf-8")
