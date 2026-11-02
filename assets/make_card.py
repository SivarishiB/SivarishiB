"""Generate an animated ASCII-portrait + neofetch-style SVG card from a photo."""
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from html import escape
import sys

SRC, OUT = sys.argv[1], sys.argv[2]

# ---------- ASCII portrait ----------
import cv2, numpy as np
g = cv2.cvtColor(cv2.imread(SRC), cv2.COLOR_BGR2GRAY)
g = g[200:820, 190:720]                          # head + shoulders
bgmask = g > 205                                 # bright studio wall
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
eq = clahe.apply(cv2.GaussianBlur(g, (5, 5), 0))

COLS = 82
CHAR_W, LINE_H = 5.4, 9.0           # font-size 9px monospace
h, w = g.shape
ROWS = int(h / w * COLS * CHAR_W / LINE_H)
small = cv2.resize(eq, (COLS, ROWS), interpolation=cv2.INTER_AREA)
msk = cv2.resize(bgmask.astype(np.uint8) * 255, (COLS, ROWS), interpolation=cv2.INTER_AREA) > 140

RAMP = ".:-=+*#%@@"            # dark -> bright (light text on dark bg)
lines = []
for y in range(ROWS):
    row = ""
    for x in range(COLS):
        if msk[y, x]:
            row += " "
        else:
            v = small[y, x] / 255
            row += RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))]
    lines.append(row.rstrip())

# ---------- neofetch panel ----------
INFO = [
    ("title", "rishi@github"),
    ("rule", "-" * 28),
    ("kv", "Name", "Sivarishi B"),
    ("kv", "Role", "Python / Django Full-Stack Dev"),
    ("kv", "Based", "Bengaluru, IN"),
    ("kv", "Degree", "B.Tech CSE · SRM IST '25"),
    ("kv", "CGPA", "8.37"),
    ("kv", "Exp", "SDE Intern @ Infosys"),
    ("kv", "Cert", "Oracle MySQL 8.0 Developer"),
    ("blank",),
    ("kv", "Core", "Python, Django, MySQL, SQL"),
    ("kv", "Web", "JavaScript, TypeScript, React"),
    ("kv", "Backend", "Node.js, REST APIs, Supabase"),
    ("kv", "Data", "Pandas, NumPy"),
    ("kv", "ML", "TensorFlow, OpenCV"),
    ("kv", "Tools", "Git, Linux CLI"),
    ("blank",),
    ("kv", "Builds", "Night Guardian · Elegant Shopping"),
    ("kv", "Status", "open to SDE roles ✦"),
    ("blank",),
    ("palette",),
    ("blank",),
    ("prompt",),
]

BG, FG, DIM, ACC, ACC2 = "#0b0f14", "#d6e2ee", "#5b6b7c", "#5eead4", "#f472b6"
PAD = 28
PORTRAIT_W = COLS * CHAR_W
PANEL_X = PAD + PORTRAIT_W + 40
W = int(PANEL_X + 330 + PAD)
TOP = 64
H = int(max(TOP + ROWS * LINE_H, TOP + len(INFO) * 18) + PAD + 8)

out = []
out.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Sivarishi B — ASCII portrait and profile">
<style>
  .mono {{ font-family: ui-monospace, SFMono-Regular, "JetBrains Mono", Menlo, Consolas, monospace; }}
  .a {{ font-size: 9px; fill: {ACC}; white-space: pre; opacity: 0; animation: rowIn .5s ease-out forwards; }}
  .t {{ font-size: 14px; fill: {FG}; opacity: 0; animation: rowIn .35s ease-out forwards; white-space: pre; }}
  .k {{ fill: {ACC}; font-weight: 700; }}
  .h {{ fill: {ACC2}; font-weight: 700; }}
  .d {{ fill: {DIM}; }}
  @keyframes rowIn {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
  .scan {{ animation: scan 4.5s linear 3.2s infinite; opacity: 0; }}
  @keyframes scan {{ 0% {{ transform: translateY(0); opacity: .0; }} 5% {{ opacity: .55; }} 95% {{ opacity: .55; }} 100% {{ transform: translateY({ROWS * LINE_H}px); opacity: 0; }} }}
  .glitch {{ animation: glitch 6s steps(1) 4s infinite; }}
  @keyframes glitch {{ 0%,100% {{ transform: none; }} 92% {{ transform: translateX(3px); }} 93% {{ transform: translateX(-4px); }} 94% {{ transform: none; }} }}
  .cursor {{ animation: blink 1s steps(1) infinite; fill: {ACC}; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .sw {{ opacity: 0; animation: rowIn .3s ease-out forwards; }}
</style>
<defs>
  <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{ACC}" stop-opacity="0"/>
    <stop offset="1" stop-color="{ACC}" stop-opacity=".9"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC2}"/>
  </linearGradient>
  <clipPath id="pc"><rect x="{PAD}" y="{TOP - 12}" width="{PORTRAIT_W}" height="{ROWS * LINE_H + 4}"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#1f2a36"/>
<!-- window chrome -->
<circle cx="24" cy="22" r="6" fill="#ff5f57"/><circle cx="44" cy="22" r="6" fill="#febc2e"/><circle cx="64" cy="22" r="6" fill="#28c840"/>
<text x="{W / 2}" y="27" text-anchor="middle" class="mono" font-size="12" fill="{DIM}">~/sivarishi — zsh — neofetch</text>
<line x1="0" y1="42" x2="{W}" y2="42" stroke="#1f2a36"/>
''')

# portrait rows
out.append(f'<g class="mono glitch" clip-path="url(#pc)">')
for i, row in enumerate(lines):
    if not row.strip():
        continue
    delay = 0.15 + i * 0.028
    out.append(f'<text class="a" x="{PAD}" y="{TOP + i * LINE_H:.1f}" style="animation-delay:{delay:.2f}s" xml:space="preserve">{escape(row)}</text>')
out.append(f'<rect class="scan" x="{PAD}" y="{TOP - 30}" width="{PORTRAIT_W}" height="22" fill="url(#beam)"/>')
out.append("</g>")

# info panel
y = TOP + 2
t0 = 0.6
for j, item in enumerate(INFO):
    d = t0 + j * 0.09
    st = f'style="animation-delay:{d:.2f}s"'
    kind = item[0]
    if kind == "title":
        out.append(f'<text class="mono t" x="{PANEL_X}" y="{y}" {st}><tspan class="h">rishi</tspan><tspan class="d">@</tspan><tspan class="k">github</tspan></text>')
    elif kind == "rule":
        out.append(f'<text class="mono t d" x="{PANEL_X}" y="{y}" {st}>{item[1]}</text>')
    elif kind == "kv":
        out.append(f'<text class="mono t" x="{PANEL_X}" y="{y}" {st}><tspan class="k">{escape(item[1])}</tspan><tspan class="d">: </tspan>{escape(item[2])}</text>')
    elif kind == "palette":
        cols = ["#0b0f14", "#f87171", "#4ade80", "#facc15", "#60a5fa", "#f472b6", "#5eead4", "#d6e2ee"]
        for c_i, c in enumerate(cols):
            out.append(f'<rect class="sw" x="{PANEL_X + c_i * 26}" y="{y - 13}" width="24" height="16" rx="2" fill="{c}" stroke="#1f2a36" style="animation-delay:{d + c_i * 0.05:.2f}s"/>')
    elif kind == "prompt":
        out.append(f'<text class="mono t" x="{PANEL_X}" y="{y}" {st}><tspan class="h">❯</tspan> echo "what the flex?"</text>')
        out.append(f'<rect class="cursor" x="{PANEL_X + 196}" y="{y - 12}" width="8" height="15"/>')
    y += 18

out.append("</svg>")
open(OUT, "w").write("\n".join(out))
print("rows", ROWS, "size", W, H)
