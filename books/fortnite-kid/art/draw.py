#!/usr/bin/env python3
"""Hand-built cartoon illustrations for The Fortnite Kid.

    python3 books/fortnite-kid/art/draw.py      # writes art/*.svg (scenes) and art/cover-art.svg

Everything is drawn in code: a posable cartoon figure (Billy, Mira, Kai's banana), Pip the
Spooky Dash Sprite, and props/scenery. Scenes recreate key moments from the gameplay video
the book is based on, redrawn as cartoons, with our characters in place of the player.
Thick ink outlines + flat colour + one shade, so they still read in greyscale on e-ink.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1200, 750
INK = "#1b1030"

BILLY = dict(skin="#f2c29b", skin2="#d99e78", hair="#6b3f1f", hair2="#4a2a12", top="#3f7bd6", top2="#2d5fb0",
             shorts="#e0505a", shorts2="#b83a44", sock="#ffffff", sock2="#d8d8e8", kind="billy")
MIRA = dict(skin="#5a3a28", skin2="#3a241a", top="#4a2f22", top2="#2f1c14", shorts="#3a241a", shorts2="#24150e",
            sock="#2f1c14", sock2="#1d120d", kind="mira")


def f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pt(x, y) -> str:
    return f"{f(x)},{f(y)}"


def vec(a: float, l: float) -> tuple[float, float]:
    """Angle in degrees from straight down; positive swings towards +x."""
    r = math.radians(a)
    return math.sin(r) * l, math.cos(r) * l


def limb(points, col, w, ink_w=7) -> str:
    d = "M" + " L".join(pt(x, y) for x, y in points)
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{f(w + ink_w * 2)}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" stroke-linecap="round" stroke-linejoin="round"/>')


def blob(d, fill, sw=6, extra="") -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'


def circle(x, y, r, fill, sw=6, extra="") -> str:
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" {extra}/>'


def g(content, tx=0, ty=0, s=1.0, rot=0, flip=False, extra="") -> str:
    t = f"translate({f(tx)} {f(ty)})"
    if rot:
        t += f" rotate({f(rot)})"
    if s != 1 or flip:
        t += f" scale({f(-s if flip else s)} {f(s)})"
    return f'<g transform="{t}" {extra}>{content}</g>'


# --------------------------------------------------------------------------- shared defs

def defs(uid: str) -> str:
    return f"""<defs>
<filter id="{uid}-glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="{uid}-soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
<filter id="{uid}-blur4"><feGaussianBlur stdDeviation="4"/></filter>
<pattern id="{uid}-dots" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
<circle cx="4" cy="4" r="2.6" fill="#ffffff" fill-opacity=".14"/></pattern>
<pattern id="{uid}-dotsdark" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">
<circle cx="4" cy="4" r="2.4" fill="{INK}" fill-opacity=".16"/></pattern>
<pattern id="{uid}-check" width="40" height="40" patternUnits="userSpaceOnUse">
<rect width="40" height="40" fill="#b8692b"/><rect width="20" height="20" fill="#8a4a1c"/><rect x="20" y="20" width="20" height="20" fill="#8a4a1c"/></pattern>
</defs>"""


def frame(uid: str, body: str, bg: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{defs(uid)}<clipPath id="{uid}-clip"><rect x="0" y="0" width="{W}" height="{H}" rx="26"/></clipPath>'
            f'<g clip-path="url(#{uid}-clip)"><rect width="{W}" height="{H}" fill="{bg}"/>{body}</g>'
            f'<rect x="7" y="7" width="{W - 14}" height="{H - 14}" rx="22" fill="none" stroke="{INK}" stroke-width="14"/></svg>')


def sky(uid, top, bottom, dots=True) -> str:
    s = (f'<linearGradient id="{uid}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
         f'<stop offset="1" stop-color="{bottom}"/></linearGradient><rect width="{W}" height="{H}" fill="url(#{uid}-sky)"/>')
    if dots:
        s += f'<rect width="{W}" height="{H}" fill="url(#{uid}-dots)"/>'
    return s


def sfx(text, x, y, size=90, rot=-8, fill="#ffd23f", stroke=INK, shadow="#ff5a1f") -> str:
    style = f'font-family="Anton, Impact, sans-serif" font-size="{size}" text-anchor="middle" letter-spacing="2"'
    t = f'transform="translate({f(x)} {f(y)}) rotate({rot})"'
    return (f'<text {t} {style} fill="{shadow}" stroke="{stroke}" stroke-width="{size * .16:.1f}" stroke-linejoin="round" dx="7" dy="7">{text}</text>'
            f'<text {t} {style} fill="{fill}" stroke="{stroke}" stroke-width="{size * .16:.1f}" stroke-linejoin="round" paint-order="stroke">{text}</text>')


def label(text, x, y, size=34, fill="#ffffff", bg=INK, rot=0, pad=14) -> str:
    w = len(text) * size * .6 + pad * 2
    h = size * 1.35
    return g(f'<rect x="{f(-w / 2)}" y="{f(-h / 2)}" width="{f(w)}" height="{f(h)}" rx="8" fill="{bg}" stroke="{INK}" stroke-width="5"/>'
             f'<text y="{f(size * .36)}" font-family="Barlow Condensed, sans-serif" font-weight="800" font-size="{size}" '
             f'text-anchor="middle" letter-spacing="1.5" fill="{fill}">{text}</text>', x, y, rot=rot)


def burst(x, y, r1, r2, n, fill, sw=6, rot=0) -> str:
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + math.radians(rot)
        r = r1 if i % 2 == 0 else r2
        pts.append(pt(x + math.cos(a) * r, y + math.sin(a) * r))
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'


def speedlines(x, y, n, r1, r2, col="#ffffff", op=.55, w=5, seed=1, a0=0, a1=360) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        a = math.radians(rnd.uniform(a0, a1))
        ra, rb = r1 * rnd.uniform(.9, 1.2), r2 * rnd.uniform(.8, 1.1)
        out.append(f'<line x1="{f(x + math.cos(a) * ra)}" y1="{f(y + math.sin(a) * ra)}" x2="{f(x + math.cos(a) * rb)}" '
                   f'y2="{f(y + math.sin(a) * rb)}" stroke="{col}" stroke-opacity="{op}" stroke-width="{f(w * rnd.uniform(.6, 1.4))}" stroke-linecap="round"/>')
    return "".join(out)


def sparkle(x, y, r, col="#fff6b0") -> str:
    d = f"M{f(x)},{f(y - r)} Q{f(x + r * .18)},{f(y - r * .18)} {f(x + r)},{f(y)} Q{f(x + r * .18)},{f(y + r * .18)} {f(x)},{f(y + r)} " \
        f"Q{f(x - r * .18)},{f(y + r * .18)} {f(x - r)},{f(y)} Q{f(x - r * .18)},{f(y - r * .18)} {f(x)},{f(y - r)}Z"
    return f'<path d="{d}" fill="{col}" stroke="{INK}" stroke-width="3"/>'


def confetti(n, seed, cols=("#ffd23f", "#ff7a1a", "#ffffff", "#c77dff", "#5fd4ff"), area=(0, 0, W, H)) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3])
        c = rnd.choice(cols)
        out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(rnd.uniform(8, 16))}" height="{f(rnd.uniform(14, 26))}" rx="3" fill="{c}" '
                   f'stroke="{INK}" stroke-width="2.5" transform="rotate({rnd.randint(0, 180)} {f(x)} {f(y)})"/>')
    return "".join(out)


def squares(x, y, n, spread, col, seed, size=(8, 22), rise=0) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        dx, dy = rnd.gauss(0, spread), rnd.gauss(0, spread * .8) - rise * rnd.random()
        s = rnd.uniform(*size)
        out.append(f'<rect x="{f(x + dx)}" y="{f(y + dy)}" width="{f(s)}" height="{f(s)}" fill="{col}" fill-opacity="{rnd.uniform(.55, 1):.2f}" '
                   f'stroke="{INK}" stroke-width="2" transform="rotate({rnd.randint(-30, 30)} {f(x + dx)} {f(y + dy)})"/>')
    return "".join(out)


# --------------------------------------------------------------------------- props

def pickaxe(rot=0) -> str:
    """Held at the origin (hand), head up."""
    return g(limb([(0, 40), (0, -120)], "#8a5a2b", 13, 6)
             + blob("M-62,-118 Q0,-160 62,-118 L54,-104 Q0,-136 -54,-104Z", "#c9d3e0")
             + blob("M-12,-132 L12,-132 L12,-104 L-12,-104Z", "#6b7790", 5), rot=rot)


def sweeper(rot=0, col="#9b5de5") -> str:
    """Shotgun, held at the origin, pointing +x."""
    return g(blob("M-34,-12 L60,-16 L150,-14 L150,6 L60,8 L30,14 L-6,40 L-30,34 L-14,10 L-34,8Z", col)
             + blob("M70,6 L118,6 L118,18 L70,18Z", "#3d2a63", 5)
             + f'<rect x="96" y="-24" width="30" height="10" rx="3" fill="{INK}"/>', rot=rot)


def gatekeeper(rot=0) -> str:
    spikes = "".join(blob(f"M{x},-14 L{x + 8},-30 L{x + 16},-14Z", "#c0c4d0", 4) for x in (40, 70, 100))
    return g(spikes + blob("M-34,-14 L150,-18 L160,-6 L160,10 L40,12 L10,16 L-10,42 L-34,36 L-18,10 L-34,8Z", "#2b2d38")
             + f'<rect x="150" y="-14" width="14" height="24" rx="4" fill="#ff3b3b" stroke="{INK}" stroke-width="4"/>', rot=rot)


def rifle(rot=0) -> str:
    return g(blob("M-60,-8 L40,-12 L200,-10 L200,2 L40,4 L-10,10 L-30,26 L-70,22 L-56,4Z", "#a0632f")
             + blob("M40,-12 L200,-10 L200,2 L40,4Z", "#3a3f4f", 5)
             + blob("M20,-34 L110,-34 L114,-20 L16,-20Z", "#2b2d38", 5)
             + circle(112, -27, 7, "#bfe6ff", 3), rot=rot)


def smg(rot=0) -> str:
    return g(blob("M-26,-14 L90,-14 L96,8 L20,10 L12,34 L-6,34 L-4,10 L-26,8Z", "#e8e2d0")
             + "".join(f'<rect x="{x}" y="-10" width="6" height="16" rx="2" fill="{INK}"/>' for x in (24, 40, 56, 72)), rot=rot)


def umbrella(col1="#7b2cbf", col2="#ff4fa3", r=130) -> str:
    """Override 'Brella, handle at the origin, canopy up."""
    segs = []
    n = 6
    for i in range(n):
        a0 = math.pi + math.pi * i / n
        a1 = math.pi + math.pi * (i + 1) / n
        x0, y0 = math.cos(a0) * r, math.sin(a0) * r * .62 - 190
        x1, y1 = math.cos(a1) * r, math.sin(a1) * r * .62 - 190
        segs.append(blob(f"M0,-196 L{f(x0)},{f(y0)} Q{f((x0 + x1) / 2)},{f((y0 + y1) / 2 + 26)} {f(x1)},{f(y1)}Z",
                         col1 if i % 2 else col2, 5))
    circuit = "".join(f'<path d="M{a},-170 l0,-18 l14,-10" fill="none" stroke="#5fd4ff" stroke-width="4" stroke-linecap="round"/>'
                      for a in (-90, -30, 30, 90))
    return limb([(0, 0), (0, -196)], "#222", 7, 5) + "".join(segs) + circuit + circle(0, -200, 9, "#ffd23f", 4)


def pip(x=0, y=0, s=1.0, mood="grin", flip=False, glow_uid=None) -> str:
    """Pip: Trick or Treat Spooky Dash Sprite. Origin at feet centre; ~110 tall at s=1."""
    body = ""
    body += limb([(-22, -14), (-24, 0)], "#e0601a", 10, 5) + limb([(22, -14), (24, 0)], "#e0601a", 10, 5)
    body += blob("M-50,-60 C-56,-104 -20,-112 0,-110 C22,-112 56,-104 50,-60 C46,-24 26,-12 0,-12 C-26,-12 -46,-24 -50,-60Z", "#ff8a1e")
    body += f'<path d="M-16,-108 C-24,-80 -22,-40 -12,-14" fill="none" stroke="#e0601a" stroke-width="5"/>'
    body += f'<path d="M16,-108 C24,-80 22,-40 12,-14" fill="none" stroke="#e0601a" stroke-width="5"/>'
    body += blob("M-4,-108 C-6,-122 2,-130 12,-130 C6,-124 6,-116 6,-108Z", "#5a8a2a", 4)
    glow = f'filter="url(#{glow_uid}-glow)"' if glow_uid else ""
    eye = "#c77dff"
    face = (f'<g {glow}><path d="M-34,-74 L-12,-74 L-22,-92Z" fill="{eye}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M34,-74 L12,-74 L22,-92Z" fill="{eye}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    if mood == "grin":
        face += f'<path d="M-32,-56 Q0,-28 32,-56 L22,-54 L18,-46 L8,-52 L0,-42 L-8,-52 L-18,-46 L-22,-54Z" fill="{eye}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
    elif mood == "shout":
        face += f'<ellipse cx="0" cy="-46" rx="16" ry="14" fill="{eye}" stroke="{INK}" stroke-width="4"/>'
    else:
        face += f'<path d="M-20,-50 Q0,-40 20,-50" fill="none" stroke="{eye}" stroke-width="6" stroke-linecap="round"/>'
    face += "</g>"
    arms = limb([(-46, -60), (-64, -76)], "#ff8a1e", 10, 5) + limb([(46, -60), (64, -78)], "#ff8a1e", 10, 5)
    return g(arms + body + face, x, y, s, flip=flip)


def pumpkin_chest(x, y, s=1.0, uid="p", lit=True) -> str:
    """The big dark Pumpkin Chest with purple flame. Origin bottom centre; ~200 tall at s=1."""
    ribs = "".join(blob(d, c, 6) for d, c in (
        ("M-150,-90 C-160,-170 -80,-200 -40,-190 C-90,-160 -100,-40 -50,-4 C-110,-4 -146,-40 -150,-90Z", "#b4471b"),
        ("M150,-90 C160,-170 80,-200 40,-190 C90,-160 100,-40 50,-4 C110,-4 146,-40 150,-90Z", "#b4471b"),
        ("M-60,-190 C-20,-206 20,-206 60,-190 C80,-140 80,-40 50,-4 L-50,-4 C-80,-40 -80,-140 -60,-190Z", "#d0581f")))
    shade = blob("M-150,-90 C-146,-40 -110,-4 -50,-4 L50,-4 C110,-4 146,-40 150,-90 C120,-40 -120,-40 -150,-90Z", "#7a2a10")
    stalk = blob("M-12,-196 C-16,-226 4,-240 20,-236 C10,-226 10,-210 12,-196Z", "#3e5a1a", 5)
    fl = f'filter="url(#{uid}-glow)"' if lit else ""
    face = (f'<g {fl}><path d="M-92,-120 L-36,-110 L-70,-160Z" fill="#b65cff" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M92,-120 L36,-110 L70,-160Z" fill="#b65cff" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-100,-80 L-70,-70 L-60,-88 L-36,-66 L-16,-86 L0,-64 L16,-86 L36,-66 L60,-88 L70,-70 L100,-80 '
            f'C80,-26 -80,-26 -100,-80Z" fill="#b65cff" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/></g>')
    return g(ribs + shade + stalk + face, x, y, s)


# --------------------------------------------------------------------------- the figure rig

def figure(c: dict, pose: dict) -> str:
    """Cartoon kid (or Mira). Origin at hips; facing +x. ~300 tall for Billy.

    pose: lean, head (tilt), armF/armB=(upper, lower) angles, legF/legB=(upper, lower),
          expr, hold=(svg, rot) drawn at the front hand, holdB at the back hand, pip=True (on back).
    Angles are degrees from straight down; positive swings forwards (+x)."""
    mira = c["kind"] == "mira"
    k = 1.12 if mira else 1.0
    lean = pose.get("lean", 0)
    nx = math.sin(math.radians(lean)) * 96 * k
    ny = -math.cos(math.radians(lean)) * 96 * k
    sh = (nx * .86, ny * .86)
    out_back, out_front = [], []

    def arm(ang, hold, back):
        ua, la = ang
        sx, sy = sh[0] + (-8 if back else 8), sh[1]
        ex, ey = vec(ua, 50 * k)
        ex, ey = sx + ex, sy + ey
        hx, hy = vec(la, 48 * k)
        hx, hy = ex + hx, ey + hy
        top = c["top2"] if back else c["top"]
        s = limb([(sx, sy), (ex, ey), (hx, hy)], top, 26 * k)
        hand = circle(hx, hy, 15 * k, c["skin2"] if back else c["skin"], 5)
        if hold:
            svg, rot, sc = hold if len(hold) == 3 else (*hold, 1.0)
            s += hand + g(svg, hx, hy, sc, rot=rot)
            return s
        return s + hand

    def leg(ang, back):
        ua, la = ang
        hx, hy = (-12 if back else 12), 0
        kx, ky = vec(ua, 54 * k)
        kx, ky = hx + kx, hy + ky
        fx, fy = vec(la, 54 * k)
        fx, fy = kx + fx, ky + fy
        sk = c["skin2"] if back else c["skin"]
        s = limb([(hx, hy), (kx, ky), (fx, fy)], sk, 24 * k)
        sock = c["sock2"] if back else c["sock"]
        s += limb([(kx + (fx - kx) * .45, ky + (fy - ky) * .45), (fx, fy)], sock, 24 * k, 0)
        foot = f'<ellipse cx="{f(fx + 10)}" cy="{f(fy + 4)}" rx="{f(22 * k)}" ry="{f(12 * k)}" fill="{sock}" stroke="{INK}" stroke-width="5" ' \
               f'transform="rotate({f(la * .5)} {f(fx)} {f(fy)})"/>'
        return s + foot

    # back limbs
    out_back.append(arm(pose.get("armB", (-20, -10)), pose.get("holdB"), True))
    out_back.append(leg(pose.get("legB", (-12, 0)), True))
    if pose.get("pip"):
        out_back.append(pip(nx * .8 - 50, ny * .62, .68, pose.get("pipmood", "grin"), glow_uid=pose.get("uid")))
    # shorts + torso
    torso = ""
    if not mira:
        torso += blob(f"M-30,-14 L30,-14 L36,26 L4,30 L0,14 L-4,30 L-36,26Z", c["shorts"], 6)
        torso += f'<path d="M-24,-6 L-28,24 M-8,-8 L-10,26 M10,-8 L12,26 M26,-6 L30,24" stroke="#f7d9a8" stroke-width="4" opacity=".7"/>'
    tl = math.radians(lean)
    ux, uy = math.cos(tl), math.sin(tl)  # across-body unit (perpendicular to spine)
    def P(a, b):  # a across, b along spine (up = +)
        return pt(a * ux + nx * b, a * uy + ny * b)
    wide = 40 * k if not mira else 34 * k
    torso += blob(f"M{P(-wide * .9, 0)} L{P(wide * .9, 0)} Q{P(wide * 1.12, .55)} {P(wide, .95)} L{P(-wide, .95)} Q{P(-wide * 1.12, .55)} {P(-wide * .9, 0)}Z",
                  c["top"], 6)
    if not mira:
        torso += blob(f"M{P(-12, .1)} L{P(12, .1)} L{P(14, .32)} L{P(-14, .32)}Z", c["top2"], 4)  # pocket
        torso += f'<path d="M{P(-6, .95)} L{P(-8, .7)} M{P(6, .95)} L{P(8, .7)}" stroke="#e8eefc" stroke-width="4" stroke-linecap="round"/>'
    else:
        torso += "".join(f'<path d="M{P(a, .1)} Q{P(a + 6, .5)} {P(a - 4, .85)}" fill="none" stroke="{c["top2"]}" stroke-width="5"/>' for a in (-18, 0, 18))
    if not mira:
        torso = blob(f"M{P(-30, .82)} Q{P(-44, 1.12)} {P(-8, 1.12)} L{P(18, 1.0)} L{P(0, .9)}Z", c["top2"], 6) + torso
    out_front.append(torso)
    out_front.append(leg(pose.get("legF", (12, 0)), False))
    # head
    hx, hy = nx * 1.0 + math.sin(tl) * 46 * k, ny * 1.0 - math.cos(tl) * 46 * k
    out_front.append(head(c, hx, hy, pose.get("head", 0) + lean * .5, pose.get("expr", "grin"), pose.get("uid", "x"), k))
    out_front.append(arm(pose.get("armF", (20, 10)), pose.get("hold"), False))
    return "".join(out_back + out_front)


def head(c, x, y, tilt, expr, uid, k) -> str:
    mira = c["kind"] == "mira"
    s = ""
    if mira:
        # antlers
        for side in (-1, 1):
            base = (side * 22, -40)
            s += limb([base, (side * 52, -100), (side * 70, -168)], "#1d120d", 14, 4)
            s += limb([(side * 48, -92), (side * 92, -118), (side * 118, -112)], "#1d120d", 11, 4)
            s += limb([(side * 62, -138), (side * 34, -182)], "#1d120d", 10, 4)
            s += limb([(side * 92, -118), (side * 104, -150)], "#1d120d", 9, 4)
        s += blob("M-44,-6 C-50,-50 -30,-70 0,-70 C30,-70 50,-50 44,-6 C40,30 20,46 0,46 C-20,46 -40,30 -44,-6Z", c["skin"])
        s += f'<path d="M-30,-40 Q-20,-30 -26,-10 M24,-50 Q30,-36 20,-20 M-6,20 Q2,30 -4,40" fill="none" stroke="{c["skin2"]}" stroke-width="5" stroke-linecap="round"/>'
        s += (f'<g filter="url(#{uid}-glow)"><ellipse cx="-14" cy="-6" rx="11" ry="7" fill="#ff2a2a" transform="rotate(12 -14 -6)"/>'
              f'<ellipse cx="22" cy="-6" rx="11" ry="7" fill="#ff2a2a" transform="rotate(-12 22 -6)"/></g>')
        if expr == "smile":
            s += f'<path d="M-8,22 Q6,32 20,20" fill="none" stroke="#1d120d" stroke-width="5" stroke-linecap="round"/>'
        elif expr == "shout":
            s += f'<ellipse cx="6" cy="24" rx="10" ry="9" fill="#1d120d"/>'
        else:
            s += f'<path d="M-6,24 L18,22" stroke="#1d120d" stroke-width="5" stroke-linecap="round"/>'
        return g(s, x, y, k, rot=tilt)
    r = 54
    s += circle(-r * .05, 0, r, c["skin"], 6)
    s += f'<ellipse cx="{-r * .9:.1f}" cy="8" rx="11" ry="15" fill="{c["skin"]}" stroke="{INK}" stroke-width="5"/>'  # ear
    hair = ("M-60,-4 C-70,-40 -50,-70 -14,-72 C-6,-90 20,-84 26,-72 C44,-80 64,-60 56,-34 C66,-30 64,-14 56,-14 "
            "C50,-36 34,-46 10,-44 C20,-36 16,-30 8,-34 C-6,-44 -28,-40 -38,-30 C-44,-22 -50,-12 -52,4Z")
    s += blob(hair, c["hair"], 6)
    s += f'<path d="M-30,-58 Q-14,-66 2,-60 M18,-64 Q34,-66 44,-52" fill="none" stroke="{c["hair2"]}" stroke-width="5" stroke-linecap="round"/>'
    # headset
    s += f'<path d="M-62,6 C-70,-70 40,-96 58,-30" fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
    s += f'<path d="M-62,6 C-70,-70 40,-96 58,-30" fill="none" stroke="#3a3a48" stroke-width="5" stroke-linecap="round"/>'
    s += f'<rect x="-76" y="-10" width="26" height="38" rx="10" fill="#3a3a48" stroke="{INK}" stroke-width="5"/>'
    s += f'<path d="M-60,26 Q-40,52 -4,44" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>' + circle(-2, 44, 6, "#3a3a48", 4)
    # face (3/4 to the right)
    eyes = {"grin": ("open", "M8,20 Q26,40 46,18", "smile"), "shout": ("wide", None, "shout"), "worried": ("open", None, "worried"),
            "determined": ("narrow", "M12,26 L40,24", "line"), "smile": ("happy", "M10,20 Q26,34 44,20", "smile"),
            "scared": ("wide", None, "o")}[expr]
    ek, mouth, mk = eyes
    for ex in (6, 38):
        if ek == "happy":
            s += f'<path d="M{ex - 9},-4 Q{ex},-14 {ex + 9},-4" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
        else:
            ry = 13 if ek == "wide" else (7 if ek == "narrow" else 11)
            s += f'<ellipse cx="{ex}" cy="-6" rx="9" ry="{ry}" fill="#ffffff" stroke="{INK}" stroke-width="4"/><circle cx="{ex + 3}" cy="-5" r="5" fill="{INK}"/>'
    brow = {"determined": "M-2,-26 L16,-20 M30,-20 L48,-26", "worried": "M-2,-22 L16,-28 M30,-28 L48,-22",
            "scared": "M-2,-26 L16,-32 M30,-32 L48,-26", "shout": "M-2,-26 L16,-22 M30,-22 L48,-26"}.get(expr, "M-2,-24 Q7,-30 16,-24 M30,-24 Q39,-30 48,-24")
    s += f'<path d="{brow}" fill="none" stroke="{c["hair2"]}" stroke-width="5" stroke-linecap="round"/>'
    s += f'<path d="M22,4 Q28,12 20,14" fill="none" stroke="{c["skin2"]}" stroke-width="4" stroke-linecap="round"/>'  # nose
    if mk == "smile":
        s += f'<path d="{mouth} Z" fill="#7a1f2b" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
        s += f'<path d="M14,24 Q26,30 40,23" fill="none" stroke="#ffffff" stroke-width="5"/>'
    elif mk == "shout":
        s += f'<ellipse cx="26" cy="30" rx="15" ry="17" fill="#7a1f2b" stroke="{INK}" stroke-width="5"/><ellipse cx="26" cy="38" rx="8" ry="5" fill="#ff7a8a"/>'
    elif mk == "o":
        s += f'<ellipse cx="26" cy="30" rx="8" ry="10" fill="#7a1f2b" stroke="{INK}" stroke-width="5"/>'
    elif mk == "worried":
        s += f'<path d="M12,30 Q20,22 28,30 Q36,38 44,28" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    else:
        s += f'<path d="{mouth}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
    s += f'<ellipse cx="44" cy="14" rx="9" ry="6" fill="#ff8f8f" opacity=".45"/>'
    return g(s, x, y, k, rot=tilt)


def billy(x, y, s=1.0, flip=False, **pose) -> str:
    return g(figure(BILLY, pose), x, y, s, flip=flip)


def mira(x, y, s=1.0, flip=False, **pose) -> str:
    return g(figure(MIRA, pose), x, y, s, flip=flip)


def banana(x, y, s=1.0, flip=False, expr="grin", arms=(-30, 30), hold=None) -> str:
    """Kai's banana costume. Origin at the feet centre; ~330 tall."""
    b = ""
    b += limb([(-22, -60), (-30, -4)], "#2a2a3a", 22) + limb([(24, -60), (30, -4)], "#2a2a3a", 22)
    b += f'<ellipse cx="-34" cy="0" rx="24" ry="12" fill="#ffffff" stroke="{INK}" stroke-width="5"/>'
    b += f'<ellipse cx="36" cy="0" rx="24" ry="12" fill="#ffffff" stroke="{INK}" stroke-width="5"/>'
    b += blob("M-54,-70 C-74,-180 -40,-300 20,-330 C40,-336 52,-326 46,-312 C70,-260 80,-150 56,-70 C40,-36 -40,-36 -54,-70Z", "#ffd83a")
    b += blob("M30,-318 C34,-338 44,-350 58,-346 C56,-334 50,-322 46,-312Z", "#6b4a1e", 5)
    b += f'<path d="M-36,-90 C-48,-170 -24,-260 18,-300" fill="none" stroke="#e6b800" stroke-width="12" stroke-linecap="round"/>'
    b += f'<ellipse cx="-4" cy="-206" rx="16" ry="20" fill="#fff" stroke="{INK}" stroke-width="5"/><circle cx="0" cy="-202" r="8" fill="{INK}"/>'
    b += f'<ellipse cx="34" cy="-206" rx="16" ry="20" fill="#fff" stroke="{INK}" stroke-width="5"/><circle cx="38" cy="-202" r="8" fill="{INK}"/>'
    if expr == "shout":
        b += f'<ellipse cx="18" cy="-158" rx="18" ry="16" fill="#7a1f2b" stroke="{INK}" stroke-width="5"/>'
    else:
        b += blob("M-10,-170 Q18,-136 46,-172 Q18,-156 -10,-170Z", "#7a1f2b", 5)
    al, ar = arms
    lx, ly = vec(al, 90)
    rx, ry = vec(ar, 90)
    b += limb([(-50, -150), (-50 + lx * .5, -150 + ly * .5), (-50 + lx, -150 + ly)], "#ffd83a", 18)
    b += circle(-50 + lx, -150 + ly, 13, "#ffffff", 5)
    b += limb([(54, -150), (54 + rx * .5, -150 + ry * .5), (54 + rx, -150 + ry)], "#ffd83a", 18)
    b += circle(54 + rx, -150 + ry, 13, "#ffffff", 5)
    if hold:
        b += g(hold[0], 54 + rx, -150 + ry, rot=hold[1])
    return g(b, x, y, s, flip=flip)


def player(x, y, s=1.0, col="#555", col2="#333", flip=False, headcol=None, **pose) -> str:
    """Generic other player: reuse the rig with a plain suit."""
    c = dict(skin=headcol or col, skin2=col2, top=col, top2=col2, shorts=col2, shorts2=col2, sock=col2, sock2=col2,
             hair=col2, hair2=col2, kind="mira")
    p = dict(pose)
    body = figure(c, p)
    return g(body, x, y, s, flip=flip)


# --------------------------------------------------------------------------- scenery bits

def tree_round(x, y, r, col, col2, trunk="#3a2416", sw=6) -> str:
    t = limb([(x, y), (x - 6, y - r * 1.2)], trunk, r * .22, 5)
    t += limb([(x - 4, y - r * .9), (x - r * .5, y - r * 1.4)], trunk, r * .12, 4)
    lob = ""
    for dx, dy, rr in ((-r * .55, -r * 1.55, r * .62), (r * .5, -r * 1.6, r * .6), (0, -r * 2.0, r * .7), (-r * .1, -r * 1.35, r * .7)):
        lob += circle(x + dx, y + dy, rr, col, sw)
    lob += f'<path d="M{f(x - r * .9)},{f(y - r * 1.3)} Q{f(x)},{f(y - r * .8)} {f(x + r * .9)},{f(y - r * 1.35)}" fill="none" stroke="{col2}" stroke-width="{f(r * .18)}" stroke-linecap="round" opacity=".8"/>'
    return t + lob


def dead_tree(x, y, h, col="#2a1840", sw=6) -> str:
    return (limb([(x, y), (x + 8, y - h * .5), (x - 6, y - h)], col, h * .07, 5)
            + limb([(x + 6, y - h * .55), (x + h * .3, y - h * .8), (x + h * .42, y - h * .78)], col, h * .04, 4)
            + limb([(x, y - h * .75), (x - h * .28, y - h * .95)], col, h * .035, 4))


def palm(x, y, h, lean=10) -> str:
    tx, ty = x + lean, y - h
    t = limb([(x, y), (x + lean * .4, y - h * .5), (tx, ty)], "#8a5a2b", h * .08, 5)
    for a in (-160, -120, -60, -20, -90):
        r = math.radians(a)
        ex, ey = tx + math.cos(r) * h * .5, ty + math.sin(r) * h * .3 + h * .12
        t += blob(f"M{f(tx)},{f(ty)} Q{f((tx + ex) / 2)},{f(min(ty, ey) - h * .15)} {f(ex)},{f(ey)} Q{f((tx + ex) / 2)},{f(min(ty, ey) - h * .02)} {f(tx)},{f(ty)}Z", "#3fae4a", 5)
    return t


def ground(y, col, col2=None, wobble=12, seed=3) -> str:
    rnd = random.Random(seed)
    pts = [f"0,{H}", f"0,{y}"]
    for x in range(0, W + 100, 100):
        pts.append(f"{x},{f(y + rnd.uniform(-wobble, wobble))}")
    pts.append(f"{W},{H}")
    s = f'<polygon points="{" ".join(pts)}" fill="{col}" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
    return s


def geno_machine(x, y, s=1.0, col="#1a0f2e", lit="#ff4fa3") -> str:
    m = ""
    m += blob("M-260,0 L-230,-120 L-180,-140 L-170,-260 L-120,-280 L-100,-180 L-40,-200 L-20,-360 L30,-380 L50,-220 "
              "L110,-240 L130,-150 L190,-170 L210,-60 L260,0Z", col, 6)
    for xx, yy, hh in ((-150, -250, 80), (5, -350, 120), (100, -220, 60), (-60, -180, 50)):
        m += f'<rect x="{xx}" y="{yy}" width="10" height="{hh}" rx="4" fill="{lit}" opacity=".9"/>'
    m += f'<circle cx="10" cy="-120" r="34" fill="none" stroke="{lit}" stroke-width="8" opacity=".8"/>'
    return g(m, x, y, s)


def storm_column(uid, x, y, w, h) -> str:
    s = f'<g opacity=".95">'
    for i, (rw, op, col) in enumerate(((1.0, .9, "#3b1a6e"), (.8, .9, "#5a2a9e"), (.58, .9, "#7b3fd0"), (.36, .9, "#9d5cff"))):
        s += f'<ellipse cx="{f(x)}" cy="{f(y - h * .72 + i * 16)}" rx="{f(w * rw)}" ry="{f(h * .28 * rw)}" fill="{col}" stroke="{INK}" stroke-width="5" opacity="{op}"/>'
    s += f'<path d="M{f(x - w * .25)},{f(y - h * .45)} Q{f(x)},{f(y - h * .2)} {f(x - w * .08)},{f(y)} L{f(x + w * .08)},{f(y)} Q{f(x + w * .05)},{f(y - h * .2)} {f(x + w * .25)},{f(y - h * .45)}Z" fill="#5a2a9e" stroke="{INK}" stroke-width="5"/>'
    s += f'<path d="M{f(x - w * .5)},{f(y - h * .78)} q30,-14 70,0 t70,0 t70,0" fill="none" stroke="#c9a0ff" stroke-width="5" stroke-linecap="round"/>'
    s += f'<path d="M{f(x + w * .2)},{f(y - h * .66)} l-26,34 l20,4 l-30,44" fill="none" stroke="#ffffff" stroke-width="6" stroke-linejoin="round" filter="url(#{uid}-glow)"/>'
    return s + "</g>"


def storm_wall(x0, x1, top, col="#8b3fe0") -> str:
    """A shimmering storm wall band, drawn as vertical streaks."""
    s = f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{H - top}" fill="{col}" opacity=".55"/>'
    rnd = random.Random(x0 + x1)
    for i in range(int((x1 - x0) / 18)):
        xx = x0 + i * 18 + rnd.uniform(-4, 4)
        s += f'<line x1="{f(xx)}" y1="{top}" x2="{f(xx + rnd.uniform(-10, 10))}" y2="{H}" stroke="#d6b3ff" stroke-opacity="{rnd.uniform(.2, .6):.2f}" stroke-width="{rnd.uniform(2, 6):.1f}"/>'
    return s


def battle_bus(x, y, s=1.0) -> str:
    b = ""
    b += limb([(-120, -120), (-150, -260)], "#555", 6, 3) + limb([(120, -120), (150, -260)], "#555", 6, 3)
    b += limb([(0, -120), (0, -250)], "#555", 6, 3)
    b += f'<ellipse cx="0" cy="-330" rx="230" ry="110" fill="#3fa3ff" stroke="{INK}" stroke-width="7"/>'
    b += f'<path d="M-200,-370 Q0,-450 200,-370" fill="none" stroke="#9fd6ff" stroke-width="16" stroke-linecap="round"/>'
    b += f'<path d="M-60,-232 Q0,-210 60,-232" fill="none" stroke="#2b7bd6" stroke-width="8"/>'
    b += blob("M-200,-120 L190,-120 Q230,-120 236,-80 L240,0 Q240,20 220,20 L-210,20 Q-230,20 -230,0 L-226,-90 Q-224,-120 -200,-120Z", "#3f8bff", 7)
    b += blob("M-226,-30 L240,-30 L240,0 Q240,20 220,20 L-210,20 Q-230,20 -230,0Z", "#2860c8", 6)
    for wx in range(-190, 180, 70):
        b += f'<rect x="{wx}" y="-104" width="52" height="48" rx="8" fill="#bfe6ff" stroke="{INK}" stroke-width="5"/>'
    b += f'<rect x="196" y="-104" width="34" height="60" rx="6" fill="#bfe6ff" stroke="{INK}" stroke-width="5"/>'
    b += circle(-150, 22, 26, "#2a2a3a", 6) + circle(150, 22, 26, "#2a2a3a", 6)
    b += circle(-150, 22, 10, "#aaa", 4) + circle(150, 22, 10, "#aaa", 4)
    b += f'<rect x="-246" y="-96" width="22" height="80" rx="4" fill="{INK}"/>'
    return g(b, x, y, s)


def write(name: str, svg: str) -> None:
    (HERE / f"{name}.svg").write_text(svg, encoding="utf-8")
    print(f"art/{name}.svg")


if __name__ == "__main__":
    from scenes import SCENES  # noqa: E402  (scenes.py builds each picture from the pieces above)
    for name, fn in SCENES.items():
        write(name, fn())
