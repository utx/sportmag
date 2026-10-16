"""The book's illustrations, one function per scene. Built from the pieces in draw.py."""
from __future__ import annotations

import math
import random

from draw import (INK, H, W, banana, battle_bus, billy, blob, burst, circle, confetti, dead_tree, f, frame, g, gatekeeper,
                  geno_machine, ground, label, limb, mira, palm, pickaxe, pip, player, pt, pumpkin_chest, rifle, sfx, sky, smg,
                  sparkle, speedlines, squares, storm_column, storm_wall, sweeper, tree_round, umbrella)


# --------------------------------------------------------------------------- more props

def tv(x, y, w, h, screen="#7b2cbf", inner="") -> str:
    return (blob(f"M{x - 10},{y - 10} h{w + 20} v{h + 20} h{-(w + 20)}Z", "#22222e", 7)
            + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{screen}" stroke="{INK}" stroke-width="4"/>' + inner
            + blob(f"M{x + w / 2 - 50},{y + h + 10} h100 l20,26 h-140Z", "#22222e", 6))


def controller(x, y, s=1.0, rot=0) -> str:
    c = blob("M-60,-14 Q-56,-34 -30,-30 L30,-30 Q56,-34 60,-14 L70,26 Q72,44 54,40 L30,20 L-30,20 L-54,40 Q-72,44 -70,26Z", "#2b2d38")
    c += circle(-34, -6, 9, "#555", 3) + circle(30, -10, 6, "#5fd4ff", 3) + circle(42, 0, 6, "#ff5a5a", 3) + circle(18, 2, 6, "#5aff8a", 3)
    return g(c, x, y, s, rot=rot)


def beanbag(x, y, s=1.0, col="#e85d75") -> str:
    return g(blob("M-130,0 C-150,-60 -100,-120 -20,-110 C60,-120 150,-80 130,-10 C120,20 -110,24 -130,0Z", col, 7)
             + f'<path d="M-90,-40 Q-10,-70 90,-44" fill="none" stroke="#b8405a" stroke-width="10" stroke-linecap="round"/>', x, y, s)


def tombstone(x, y, s=1.0, rot=0, col="#7d7a99") -> str:
    return g(blob("M-34,0 L-34,-70 Q-34,-104 0,-104 Q34,-104 34,-70 L34,0Z", col, 6)
             + f'<path d="M-14,-74 h28 M0,-88 v40" stroke="#5a5778" stroke-width="7" stroke-linecap="round"/>', x, y, s, rot=rot)


def house(x, y, w, h, col, roof, rot=0, lit="#c9ff5a") -> str:
    hs = blob(f"M{-w / 2},0 L{-w / 2},{-h} L{w / 2},{-h} L{w / 2},0Z", col, 6)
    hs += blob(f"M{-w / 2 - 20},{-h} L0,{-h - w * .55} L{w / 2 + 20},{-h}Z", roof, 6)
    for wx in (-w / 4, w / 4):
        hs += f'<rect x="{f(wx - 16)}" y="{f(-h * .72)}" width="32" height="38" fill="{lit}" stroke="{INK}" stroke-width="5"/>'
    hs += f'<rect x="-18" y="-60" width="36" height="60" fill="#2a1a3a" stroke="{INK}" stroke-width="5"/>'
    return g(hs, x, y, rot=rot)


def digger(x, y, s=1.0) -> str:
    d = ""
    d += blob("M-260,0 L-260,-60 L120,-60 L120,0Z", "#3a3a48", 6)
    for wx in range(-230, 110, 56):
        d += circle(wx, -30, 22, "#22222e", 5)
    d += blob("M-220,-60 L-220,-250 L20,-250 L60,-180 L80,-60Z", "#ff8a1e", 7)
    d += blob("M-196,-232 L0,-232 L32,-176 L-196,-176Z", "#bfe6ff", 6)
    d += blob("M80,-150 L230,-300 L270,-270 L130,-120Z", "#ff8a1e", 7)
    d += blob("M230,-300 L330,-180 L300,-120 L250,-160 L270,-270Z", "#e0601a", 7)
    d += "".join(blob(f"M{tx},-130 l14,30 l12,-36Z", "#c0c4d0", 4) for tx in (262, 282))
    return g(d, x, y, s)


def cheat_panel(x, y, arrows, done=2) -> str:
    p = f'<rect x="{x}" y="{y}" width="230" height="64" rx="10" fill="#4b1a8a" stroke="{INK}" stroke-width="5"/>'
    p += f'<rect x="{x + 6}" y="{y + 6}" width="218" height="52" rx="7" fill="none" stroke="#c77dff" stroke-width="3"/>'
    for i, a in enumerate(arrows):
        cx, cy = x + 28 + i * 43, y + 32
        rot = {"→": 0, "↓": 90, "←": 180, "↑": -90}[a]
        col = "#ffd23f" if i < done else "#ffb35a"
        p += g(f'<path d="M-14,-6 L2,-6 L2,-14 L16,0 L2,14 L2,6 L-14,6Z" fill="{col}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>', cx, cy, 1.15, rot=rot)
    return p


def nite_unit(x, y, s=1.0, eye_dx=0, uid="x") -> str:
    n = ""
    n += limb([(-30, -110), (-36, 0)], "#7d8396", 30) + limb([(30, -110), (36, 0)], "#7d8396", 30)
    n += blob("M-70,-260 L70,-260 L80,-110 L-80,-110Z", "#b7bdcc", 7)
    n += blob("M-80,-110 L80,-110 L70,-90 L-70,-90Z", "#7d8396", 6)
    n += limb([(-78, -240), (-110, -160), (-100, -100)], "#9aa1b3", 24) + limb([(78, -240), (110, -160), (100, -100)], "#9aa1b3", 24)
    n += circle(-100, -96, 18, "#ff4a4a", 5) + circle(100, -96, 18, "#ff4a4a", 5)
    n += blob("M-50,-350 L50,-350 L60,-270 L-60,-270Z", "#c9cedb", 7)
    n += f'<rect x="-44" y="-322" width="88" height="20" rx="10" fill="#22222e" stroke="{INK}" stroke-width="4"/>'
    n += f'<rect x="{-18 + eye_dx}" y="-319" width="36" height="14" rx="7" fill="#ff3030" filter="url(#{uid}-glow)"/>'
    return g(n, x, y, s)


def console(x, y, s=1.0, uid="x") -> str:
    c = blob("M-110,0 L-110,-300 Q-110,-330 -80,-330 L80,-330 Q110,-330 110,-300 L110,0Z", "#1e1430", 7)
    c += blob("M-90,-310 L90,-310 L90,-170 L-90,-170Z", "#ff4fa3", 6)
    c += f'<rect x="-80" y="-300" width="160" height="120" fill="#2a0f3e" stroke="{INK}" stroke-width="4"/>'
    for i, col in enumerate(("#5fd4ff", "#c77dff", "#ffd23f")):
        c += f'<rect x="{-72 + i * 50}" y="-292" width="44" height="104" rx="6" fill="{col}" stroke="{INK}" stroke-width="4"/>'
    c += blob("M-120,-160 L120,-160 L130,-110 L-130,-110Z", "#ff4fa3", 6)
    for i, col in enumerate(("#ff3b6b", "#ffd23f", "#5fd4ff")):
        c += circle(-60 + i * 60, -136, 16, col, 5)
    c += f'<rect x="-10" y="-1000" width="20" height="670" fill="#ffb3e0" opacity=".55" filter="url(#{uid}-blur4)"/>'
    return g(c, x, y, s)


def gpu_tower(x, y, w, h, col="#2a2440", lit="#5fd4ff") -> str:
    t = blob(f"M{x},{y} L{x},{y - h} L{x + w},{y - h} L{x + w},{y}Z", col, 6)
    for i in range(int(h / 60)):
        t += f'<rect x="{x + 14}" y="{y - h + 20 + i * 60}" width="{w - 28}" height="14" rx="6" fill="{lit}" opacity=".85"/>'
    return t


def fan(x, y, r, rot=0, col="#3d3560") -> str:
    fn = circle(x, y, r, col, 7) + circle(x, y, r * .82, "#1e1430", 5)
    for i in range(5):
        a = rot + i * 72
        fn += g(blob(f"M0,0 Q{r * .3},{-r * .5} {r * .1},{-r * .78} Q{-r * .1},{-r * .45} 0,0Z", "#8a83b0", 4), x, y, rot=a)
    return fn + circle(x, y, r * .16, "#ff4fa3", 4)


def circuit_floor(y, col="#20183a", line="#ff4fa3", seed=4) -> str:
    rnd = random.Random(seed)
    s = f'<rect x="0" y="{y}" width="{W}" height="{H - y}" fill="{col}"/><line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{INK}" stroke-width="6"/>'
    for _ in range(14):
        x0 = rnd.uniform(0, W)
        yy = rnd.uniform(y + 20, H)
        s += f'<path d="M{f(x0)},{f(yy)} h{f(rnd.uniform(40, 160))} l{f(rnd.uniform(20, 50))},{f(rnd.uniform(-30, 30))} h{f(rnd.uniform(40, 120))}" ' \
             f'fill="none" stroke="{rnd.choice([line, "#5fd4ff"])}" stroke-width="4" stroke-linecap="round" opacity=".8"/>'
    return s


def duck(x, y, s=1.0, flip=False) -> str:
    d = blob("M-80,0 C-110,-30 -100,-90 -40,-90 C-30,-140 40,-160 60,-110 C70,-90 60,-70 40,-66 C90,-70 110,-30 80,0Z", "#ffd83a", 7)
    d += blob("M58,-112 C80,-114 104,-104 100,-92 C84,-88 66,-92 56,-98Z", "#ff8a1e", 5)
    d += circle(30, -118, 8, INK, 0)
    d += f'<path d="M-50,-40 Q-10,-20 30,-44" fill="none" stroke="#e6b800" stroke-width="8" stroke-linecap="round"/>'
    return g(d, x, y, s, flip=flip)


def honey(x, y, s=1.0) -> str:
    h = ""
    h += f'<ellipse cx="-26" cy="-58" rx="22" ry="14" fill="#e6f7ff" stroke="{INK}" stroke-width="4" transform="rotate(-30 -26 -58)" opacity=".9"/>'
    h += f'<ellipse cx="26" cy="-58" rx="22" ry="14" fill="#e6f7ff" stroke="{INK}" stroke-width="4" transform="rotate(30 26 -58)" opacity=".9"/>'
    h += circle(0, -30, 32, "#ffc61a", 6)
    h += f'<path d="M-30,-40 Q0,-30 30,-40 M-32,-20 Q0,-10 32,-20" fill="none" stroke="{INK}" stroke-width="8"/>'
    h += circle(-10, -38, 5, INK, 0) + circle(10, -38, 5, INK, 0)
    h += f'<path d="M-6,-26 Q0,-20 6,-26" fill="none" stroke="{INK}" stroke-width="3"/>'
    h += f'<path d="M-8,-60 Q-14,-76 -20,-78 M8,-60 Q14,-76 20,-78" fill="none" stroke="{INK}" stroke-width="3"/>'
    return g(h, x, y, s)


def bees(x, y, n, spread, seed) -> str:
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        bx, by = x + rnd.gauss(0, spread), y + rnd.gauss(0, spread * .6)
        out.append(g(f'<ellipse cx="0" cy="0" rx="9" ry="7" fill="#ffc61a" stroke="{INK}" stroke-width="2.5"/>'
                     f'<path d="M-2,-6 v12 M3,-6 v12" stroke="{INK}" stroke-width="2.5"/>'
                     f'<ellipse cx="-2" cy="-9" rx="5" ry="4" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>', bx, by, rot=rnd.randint(-40, 40)))
    return "".join(out)


def stage(x, y, rx, ry, top="#3b2a6e", side="#24184a", lit="#ffd23f") -> str:
    s = f'<path d="M{x - rx},{y} L{x - rx},{y + 70} A{rx},{ry} 0 0 0 {x + rx},{y + 70} L{x + rx},{y}Z" fill="{side}" stroke="{INK}" stroke-width="6"/>'
    s += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{top}" stroke="{INK}" stroke-width="6"/>'
    s += f'<ellipse cx="{x}" cy="{y}" rx="{rx * .82}" ry="{ry * .78}" fill="none" stroke="{lit}" stroke-width="4" stroke-dasharray="14 12" opacity=".7"/>'
    return s


def lantern(x, y, s=1.0, col="#c77dff", uid="x") -> str:
    return g(f'<line x1="0" y1="-40" x2="0" y2="-20" stroke="{INK}" stroke-width="4"/>'
             + blob("M-16,-20 h32 l6,40 h-44Z", "#2a1a3a", 5) + f'<rect x="-10" y="-14" width="20" height="28" fill="{col}" filter="url(#{uid}-glow)"/>', x, y, s)


def victory_banner(x, y, s=1.0, rot=-6) -> str:
    b = blob("M-420,-70 L380,-90 L440,-20 L400,60 L-400,80 L-460,10Z", "#ff7a1a", 8)
    b += blob("M-390,-50 L360,-66 L410,-14 L376,44 L-376,60 L-424,6Z", "#ffb02e", 5)
    b += g(blob("M-50,0 L-60,-60 L-28,-30 L0,-74 L28,-30 L60,-60 L50,0Z", "#ffd23f", 6), -300, -70, .9)
    b += ('<text x="20" y="34" font-family="Anton, Impact, sans-serif" font-size="98" text-anchor="middle" fill="#ffffff" '
          f'stroke="{INK}" stroke-width="12" stroke-linejoin="round" paint-order="stroke" letter-spacing="2">#1 VICTORY ROYALE</text>')
    return g(b, x, y, s, rot=rot)


def hills_checker(uid, y, col="#3fae4a", col2="#2f8a3a") -> str:
    s = f'<path d="M0,{y} C200,{y - 140} 380,{y - 120} 520,{y - 20} C640,{y - 150} 900,{y - 160} 1200,{y - 40} L1200,{H} L0,{H}Z" fill="url(#{uid}-check)" stroke="{INK}" stroke-width="6"/>'
    s += f'<path d="M0,{y} C200,{y - 140} 380,{y - 120} 520,{y - 20} C640,{y - 150} 900,{y - 160} 1200,{y - 40} L1200,{y + 4} C900,{y - 110} 640,{y - 100} 520,{y + 24} C380,{y - 76} 200,{y - 96} 0,{y + 40}Z" fill="{col}" stroke="{INK}" stroke-width="6"/>'
    return s


def car(x, y, s=1.0, rot=0, col="#2f9e6e") -> str:
    c = blob("M-150,0 L-150,-50 L-90,-60 L-50,-110 L70,-110 L110,-60 L160,-50 L160,0Z", col, 7)
    c += blob("M-36,-98 L60,-98 L92,-62 L-70,-62Z", "#bfe6ff", 5)
    c += circle(-90, 4, 30, "#22222e", 6) + circle(100, 4, 30, "#22222e", 6)
    return g(c, x, y, s, rot=rot)


def mask_face(x, y, s=1.0, uid="x") -> str:
    m = blob("M-80,-100 Q0,-130 80,-100 Q100,-20 70,60 Q0,110 -70,60 Q-100,-20 -80,-100Z", "#e8e4f2", 6)
    m += f'<path d="M-80,-100 Q0,-130 80,-100 Q100,-20 70,60" fill="none" stroke="#b8b0d0" stroke-width="10" opacity=".7"/>'
    m += f'<g filter="url(#{uid}-glow)"><path d="M-56,-20 L-14,-10 L-50,4Z" fill="#9fe8ff"/><path d="M56,-20 L14,-10 L50,4Z" fill="#9fe8ff"/></g>'
    m += f'<path d="M-30,50 L30,50" stroke="#8a82a8" stroke-width="6" stroke-linecap="round"/>'
    return g(m, x, y, s, extra='opacity=".9"')


# --------------------------------------------------------------------------- scenes

def s_bedroom():
    u = "bed"
    b = '<rect width="1200" height="750" fill="#141028"/>'
    b += '<rect x="0" y="560" width="1200" height="190" fill="#231a3c" stroke="#1b1030" stroke-width="6"/>'
    # window with lightning
    b += blob("M60,70 h250 v260 h-250Z", "#3a5aa8", 8) + '<path d="M185,70 v260 M60,200 h250" stroke="#1b1030" stroke-width="8"/>'
    b += f'<path d="M230,90 l-40,70 h30 l-46,80" fill="none" stroke="#ffffff" stroke-width="8" stroke-linejoin="round" filter="url(#{u}-glow)"/>'
    b += blob("M40,60 h40 v300 h-40Z", "#5a3f8a", 6) + blob("M290,60 h40 v300 h-40Z", "#5a3f8a", 6)
    for sx, sy in ((420, 60), (520, 110), (640, 50), (760, 120), (880, 70), (980, 140), (1100, 60)):
        b += sparkle(sx, sy, 12, "#d8ff8a")
    # purple light pouring from TV
    b += f'<path d="M1110,330 L560,750 L1200,750 L1200,300Z" fill="#a24dff" opacity=".35" filter="url(#{u}-soft)"/>'
    b += f'<ellipse cx="1000" cy="420" rx="300" ry="210" fill="#b65cff" opacity=".45" filter="url(#{u}-soft)"/>'
    b += blob("M840,530 h320 v40 h-320Z", "#3a2a1a", 6)
    inner = speedlines(1000, 390, 30, 70, 160, "#ffffff", .5, 5, seed=5)
    inner += ('<text x="1000" y="384" font-family="Anton, sans-serif" font-size="27" text-anchor="middle" fill="#ffffff">PLAYER OVERRIDE:</text>'
              '<text x="1000" y="420" font-family="Anton, sans-serif" font-size="27" text-anchor="middle" fill="#ffd23f">ACCEPTED</text>')
    b += tv(870, 300, 260, 180, "#7b2cbf", inner)
    b += beanbag(470, 640, 1.2)
    b += controller(560, 560, .9, rot=-30)
    # Billy lifting off, feet turning into squares
    b += squares(760, 470, 70, 70, "#c77dff", 11, (10, 26), rise=120)
    b += billy(470, 360, 1.15, lean=-8, armF=(140, 170), armB=(-140, -170), legF=(40, 70), legB=(10, 50), expr="scared", uid=u,
               head=-6)
    b += squares(560, 470, 40, 40, "#d8a3ff", 12, (8, 20))
    b += speedlines(470, 280, 18, 230, 300, "#c77dff", .8, 6, seed=2, a0=-160, a1=-20)
    b += sfx("ZZZAP!", 820, 140, 110, -8, "#d8a3ff", INK, "#7b2cbf")
    return frame(u, b, "#141028")


def s_bus():
    u = "bus"
    b = sky(u, "#5fb4ff", "#c79bff")
    b += f'<ellipse cx="600" cy="980" rx="900" ry="420" fill="#4cae55" stroke="{INK}" stroke-width="7"/>'
    b += f'<ellipse cx="600" cy="990" rx="960" ry="440" fill="none" stroke="#7fd6ff" stroke-width="30"/>'
    b += f'<path d="M180,640 Q300,600 420,650 Q330,700 180,640Z" fill="#ff7a1a" stroke="{INK}" stroke-width="5"/>'
    b += f'<path d="M820,660 Q920,610 1040,670 Q930,720 820,660Z" fill="#c74bd6" stroke="{INK}" stroke-width="5" opacity=".9"/>'
    b += f'<path d="M260,600 Q330,560 400,598" fill="none" stroke="#ffffff" stroke-width="8" opacity=".6"/>'
    b += geno_machine(620, 640, .42)
    b += storm_column(u, 625, 560, 170, 360)
    b += f'<path d="M80,640 l40,-60 l30,40 l30,-50 l40,70Z" fill="#ffffff" stroke="{INK}" stroke-width="5"/>'
    b += battle_bus(880, 420, .82)
    b += g(billy(0, 0, 1.0, lean=0, armF=(120, 140), armB=(-120, -140), legF=(-30, -60), legB=(-60, -80), expr="shout", pip=False, uid=u),
           300, 300, .95, rot=-58)
    b += speedlines(300, 300, 22, 210, 330, "#ffffff", .8, 6, seed=9, a0=-80, a1=40)
    b += sfx("WHOOOSH!", 300, 120, 92, -10, "#ffffff", INK, "#3f7bd6")
    return frame(u, b, "#5fb4ff")


def s_pumpkin():
    u = "pmk"
    b = sky(u, "#1d0f45", "#6a2fb0")
    b += f'<circle cx="600" cy="110" r="64" fill="#fff1c2" stroke="{INK}" stroke-width="6"/>'
    b += dead_tree(120, 640, 420) + dead_tree(1120, 640, 380)
    b += ground(600, "#4b2c7a", seed=8)
    b += burst(820, 470, 250, 150, 14, "#ffb02e", 7)
    b += burst(820, 470, 170, 100, 12, "#fff1a8", 5, rot=10)
    b += pumpkin_chest(820, 610, .95, u)
    b += squares(820, 420, 26, 110, "#ff8a1e", 21, (14, 30))
    b += pip(870, 300, 1.15, "shout", glow_uid=u)
    b += speedlines(870, 240, 10, 80, 140, "#ffffff", .9, 6, seed=4, a0=180, a1=360)
    b += billy(380, 470, 1.1, lean=24, armF=(118, 140), armB=(90, 120), legF=(50, 0), legB=(-50, -10), expr="shout",
               hold=(pickaxe(), 72), uid=u)
    b += sfx("CRUNCH!", 300, 150, 120, -10)
    return frame(u, b, "#1d0f45")


def s_extraction():
    u = "ext"
    b = sky(u, "#8fd8ff", "#e0b8ff")
    # loop-the-loop
    b += f'<circle cx="300" cy="300" r="190" fill="none" stroke="{INK}" stroke-width="58"/>'
    b += f'<circle cx="300" cy="300" r="190" fill="none" stroke="#b8692b" stroke-width="44"/>'
    b += f'<circle cx="300" cy="300" r="190" fill="none" stroke="#3fae4a" stroke-width="16" stroke-dasharray="1 0"/>'
    b += palm(1080, 520, 260, 30) + palm(980, 520, 200, -20)
    b += hills_checker(u, 560)
    # rings
    for rx, ry in ((620, 340), (680, 300), (740, 290)):
        b += f'<ellipse cx="{rx}" cy="{ry}" rx="20" ry="26" fill="none" stroke="{INK}" stroke-width="14"/><ellipse cx="{rx}" cy="{ry}" rx="20" ry="26" fill="none" stroke="#ffd23f" stroke-width="7"/>'
    # beam + crate
    b += f'<rect x="780" y="0" width="140" height="640" fill="#ffffff" opacity=".7" filter="url(#{u}-blur4)"/>'
    b += f'<ellipse cx="850" cy="640" rx="170" ry="40" fill="#5fd4ff" stroke="{INK}" stroke-width="6"/>'
    b += f'<path d="M850,640 m-90,0 a90,22 0 1,1 180,0 a60,15 0 1,1 -120,0 a30,8 0 1,1 60,0" fill="none" stroke="#1d6fd6" stroke-width="6"/>'
    crate = blob("M-70,0 L-70,-150 Q-70,-200 0,-200 Q70,-200 70,-150 L70,0Z", "#c9d3e0", 7)
    crate += f'<path d="M-70,-120 H70 M-70,-60 H70" stroke="#5fd4ff" stroke-width="8"/>'
    crate += blob("M-80,0 h160 v18 h-160Z", "#6b7790", 5)
    b += g(crate, 850, 420, .9)
    b += speedlines(850, 220, 10, 40, 140, "#ffffff", .9, 6, seed=3, a0=250, a1=290)
    b += billy(540, 560, 1.0, lean=-20, armF=(60, 100), armB=(-60, -30), legF=(80, 170), legB=(70, 150), expr="grin", pip=True, uid=u)
    b += speedlines(420, 560, 8, 60, 160, "#ffffff", .9, 6, seed=5, a0=160, a1=200)
    b += label("CALL EXTRACTION CRATE", 850, 712, 30)
    b += label("0:45", 1080, 70, 40, "#ffd23f")
    return frame(u, b, "#8fd8ff")



def red_tree(x, y, r):
    return tree_round(x, y, r, "#e0283c", "#a8162a", "#2a1220")


def s_cheatcode():
    u = "code"
    b = sky(u, "#3b1a7a", "#c04ab0")
    b += f'<path d="M700,330 L820,250 L900,270 L1020,200 L1200,260 L1200,420 L700,420Z" fill="#5a2a6e" stroke="{INK}" stroke-width="6"/>'
    b += blob("M930,232 l22,-36 l24,30Z", "#7a4a8e", 5)
    # Mira's silhouette with a scope glint on the ridge
    b += g(mira(0, 0, 1.0, armF=(95, 90), armB=(60, 90), hold=(rifle(), -4, .8), uid=u), 960, 190, .32)
    b += sparkle(1010, 168, 22, "#ffffff")
    for x, r in ((90, 70), (230, 90), (1120, 80), (640, 60), (760, 66)):
        b += red_tree(x, 520 if x not in (640, 760) else 430, r)
    b += ground(560, "#d05a9e", seed=6)
    b += digger(560, 640, 1.05)
    b += cheat_panel(330, 395, "→←→↑→", done=3)
    b += billy(230, 520, 1.05, lean=6, armF=(150, 120), armB=(-30, 10), legF=(14, 0), legB=(-24, -10), expr="determined", pip=True, uid=u)
    b += burst(560, 380, 46, 22, 9, "#ffd23f", 5)
    b += speedlines(560, 380, 10, 30, 80, "#ffffff", .9, 4, seed=8)
    b += sfx("CLANG!", 700, 150, 96, 8)
    b += label("INPUT CODE", 445, 485, 26, "#ffd23f")
    return frame(u, b, "#3b1a7a")


def s_console():
    u = "con"
    b = sky(u, "#1b1040", "#5a2a9e")
    ring = ('<text x="600" y="92" font-family="Anton, sans-serif" font-size="48" text-anchor="middle" fill="#ffffff" '
            f'stroke="{INK}" stroke-width="9" stroke-linejoin="round" paint-order="stroke" letter-spacing="2">BILLY HAS OVERRIDDEN THE MATCH</text>')
    b += f'<ellipse cx="600" cy="80" rx="560" ry="60" fill="#ff4fa3" opacity=".25" filter="url(#{u}-soft)"/>' + ring
    b += gpu_tower(40, 600, 150, 420) + gpu_tower(980, 600, 170, 460, lit="#ff4fa3")
    b += fan(330, 300, 110, 15) + fan(840, 260, 80, 40)
    b += f'<path d="M190,440 C320,380 420,520 560,470" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/>'
    b += f'<path d="M190,440 C320,380 420,520 560,470" fill="none" stroke="#ff7ad1" stroke-width="28" stroke-linecap="round"/>'
    b += circuit_floor(590)
    b += console(600, 640, 1.0, u)
    b += nite_unit(330, 690, .82, 10, u) + nite_unit(900, 690, .82, -12, u) + nite_unit(1080, 700, .6, -8, u)
    b += billy(500, 520, 1.0, lean=14, armF=(130, 110), armB=(70, 100), legF=(30, 0), legB=(-40, -20), expr="shout", pip=True, uid=u)
    b += sfx("SLAM!", 760, 220, 90, 10)
    return frame(u, b, "#1b1040")


def s_victory():
    u = "vic"
    b = sky(u, "#ffb02e", "#7a3fbf")
    b += burst(600, 260, 700, 500, 22, "#ffd06a", 0)
    b += f'<rect width="1200" height="750" fill="url(#{u}-dots)"/>'
    b += geno_machine(980, 640, .7, "#3a1a5a")
    b += storm_column(u, 990, 470, 180, 380)
    b += victory_banner(560, 150, .92)
    b += f'<path d="M0,620 L300,560 L560,600 L900,560 L1200,610 L1200,750 L0,750Z" fill="#6b5a78" stroke="{INK}" stroke-width="6"/>'
    b += blob("M120,600 l60,-50 l90,10 l20,40Z", "#8a7a98", 5) + blob("M860,580 l40,-30 l60,6 l10,30Z", "#8a7a98", 5)
    b += billy(560, 530, 1.1, lean=-4, armF=(160, 175), armB=(-160, -175), legF=(20, 0), legB=(-20, 0), expr="grin", uid=u)
    b += pip(730, 380, .9, "grin", glow_uid=u)
    b += confetti(110, 7)
    return frame(u, b, "#ffb02e")


def s_lobby():
    u = "lob"
    b = sky(u, "#120a2e", "#3b1a6e")
    for i in range(40):
        rnd = random.Random(i)
        b += f'<circle cx="{rnd.uniform(0, 1200):.0f}" cy="{rnd.uniform(0, 750):.0f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#d8c8ff" opacity=".6"/>'
    words = ["PLAY", "OVERRIDE", "SHOP", "LOCKER", "QUESTS"]
    for i, w in enumerate(words):
        b += (f'<text x="{120 + i * 235}" y="78" font-family="Anton, sans-serif" font-size="{60 if w == "PLAY" else 40}" text-anchor="middle" '
              f'fill="{"#ffd23f" if w == "PLAY" else "#bba8ff"}" opacity="{1 if w == "PLAY" else .7}">{w}</text>')
    # far stage with Mira
    b += stage(980, 470, 170, 46, "#2a1e4a", "#1a1236", "#7a6aa0")
    b += pumpkin_chest(1080, 470, .22, u, lit=False)
    b += g(mira(0, 0, 1.0, armF=(10, 60), armB=(-10, 40), legF=(90, 10), legB=(80, 0), expr="flat", uid=u, head=8), 960, 480, .62)
    # Billy's stage
    b += stage(420, 570, 330, 90)
    b += pumpkin_chest(170, 560, .35, u) + pumpkin_chest(660, 570, .3, u)
    b += lantern(250, 250, 1.2, uid=u) + lantern(640, 210, 1.0, uid=u) + lantern(820, 330, .8, uid=u)
    b += billy(420, 450, 1.05, armF=(30, 20), armB=(-20, -10), expr="worried", pip=True, uid=u, head=-6)
    b += label("READY", 420, 150, 44, "#1b1030", "#ffd23f")
    b += label("FINDING NEXT MATCH...", 980, 700, 26)
    b += f'<path d="M0,690 Q300,650 600,700 T1200,680 L1200,750 L0,750Z" fill="#cfc0ff" opacity=".18"/>'
    return frame(u, b, "#120a2e")


def fog(y, seed, op=.5, col="#b9a8e0"):
    rnd = random.Random(seed)
    return "".join(f'<ellipse cx="{rnd.uniform(-100, 1300):.0f}" cy="{y + rnd.uniform(-40, 40):.0f}" rx="{rnd.uniform(140, 300):.0f}" ry="{rnd.uniform(30, 60):.0f}" '
                   f'fill="{col}" opacity="{op}"/>' for _ in range(12))


def graveyard_bg(u):
    b = sky(u, "#0f0a26", "#3d2a6a")
    b += f'<circle cx="160" cy="130" r="64" fill="#e8f0c8" stroke="{INK}" stroke-width="6"/>'
    b += house(420, 430, 150, 150, "#3a3060", "#24183e", 4) + house(250, 450, 120, 120, "#2f5a4a", "#1d3a30", -5)
    m = blob("M820,440 L820,180 L870,120 L920,180 L920,240 L1010,240 L1010,150 L1050,100 L1090,150 L1090,440Z", "#2a2048", 6)
    m += f'<rect x="1036" y="160" width="28" height="36" fill="#ffe36b" stroke="{INK}" stroke-width="4" filter="url(#{u}-glow)"/>'
    m += "".join(f'<rect x="{x}" y="{y}" width="26" height="34" fill="#4a3a70" stroke="{INK}" stroke-width="4"/>' for x, y in ((850, 260), (850, 340), (950, 300), (1040, 300)))
    b += m
    b += dead_tree(640, 470, 300, "#1d1236")
    b += fog(430, 3, .35)
    b += ground(500, "#2e2552", seed=12)
    for x, y, s, r in ((80, 600, .9, -6), (300, 560, .7, 5), (720, 570, .7, -4), (880, 610, .8, 8), (1140, 590, .9, -3)):
        b += tombstone(x, y, s, r)
    return b


def angel(x, y, s=1.0):
    a = blob("M-30,0 L-24,-120 Q0,-140 24,-120 L30,0Z", "#9a97b8", 6)
    a += circle(0, -150, 24, "#9a97b8", 6)
    a += blob("M-24,-110 Q-90,-150 -70,-60 Q-50,-90 -24,-80Z", "#b5b2cc", 5)
    a += blob("M24,-110 Q70,-140 60,-100 L40,-96Z", "#b5b2cc", 5)
    return g(a, x, y, s)


def s_neighborhood():
    u = "nbh"
    b = graveyard_bg(u)
    b += angel(860, 620, 1.1)
    b += mira(800, 470, 1.0, flip=True, armF=(80, 90), armB=(40, 80), legF=(14, 0), legB=(-18, 0), hold=(gatekeeper(), -4), expr="flat", uid=u)
    b += billy(300, 500, 1.05, armF=(10, 30), armB=(-14, -4), legF=(10, 0), legB=(-14, 0), expr="worried", uid=u, hold=(rifle(), 70, .8))
    b += fog(700, 9, .45)
    return frame(u, b, "#0f0a26")


def s_eliminated():
    u = "elim"
    b = graveyard_bg(u)
    b += angel(1000, 620, .9)
    b += player(1060, 650, .8, "#7d9a5a", "#4a6a32", flip=True, lean=82, armF=(150, 110), armB=(120, 100), legF=(-80, -95), legB=(-95, -100), uid=u,
                hold=(sweeper(col="#5a6a8a"), -10, .7))
    b += mira(820, 470, 1.0, armF=(30, 20), armB=(-20, -10), legF=(10, 0), legB=(-14, 0), hold=(gatekeeper(), 70), expr="shout", uid=u, head=10)
    b += f'<g opacity=".55">{billy(320, 490, 1.05, lean=-10, armF=(60, 40), armB=(-60, -40), expr="scared", uid=u)}</g>'
    b += squares(330, 380, 120, 110, "#c77dff", 31, (10, 28), rise=260)
    b += squares(330, 300, 60, 140, "#9d5cff", 32, (6, 16), rise=300)
    b += fog(700, 4, .45)
    b += label("ELIMINATED", 330, 120, 46, "#ffffff", "#e0283c", rot=-6)
    return frame(u, b, "#0f0a26")


def s_grove():
    u = "grv"
    b = sky(u, "#ffcf7a", "#ff8a4a")
    cols = [("#e0283c", "#a8162a"), ("#ff8a1e", "#d0601a"), ("#ffc61a", "#d89a10"), ("#b8341e", "#8a2414"), ("#ff6a2a", "#c84a1a")]
    rnd = random.Random(3)
    for i in range(9):
        c1, c2 = cols[i % 5]
        b += tree_round(60 + i * 140 + rnd.uniform(-20, 20), 520 + rnd.uniform(-20, 20), rnd.uniform(70, 100), c1, c2)
    b += ground(520, "#c8642a", seed=13)
    # duck diner
    d = blob("M140,690 L140,420 Q140,330 300,320 L900,320 Q1060,330 1060,420 L1060,690Z", "#5fd4ff", 7)
    d += blob("M140,430 L1060,430 L1060,470 L140,470Z", "#ff6ab0", 6)
    for wx in range(200, 1000, 130):
        d += f'<rect x="{wx}" y="500" width="90" height="80" rx="10" fill="#e6f7ff" stroke="{INK}" stroke-width="5"/>'
    d += f'<path d="M200,330 C260,240 360,240 400,320" fill="none" stroke="{INK}" stroke-width="40" stroke-linecap="round"/>'
    d += f'<path d="M200,330 C260,240 360,240 400,320" fill="none" stroke="#ff6ab0" stroke-width="28" stroke-linecap="round" stroke-dasharray="30 18"/>'
    b += d
    b += duck(830, 322, 1.25) + duck(1040, 330, .9)
    # Billy lying on the roof, rifle forward
    b += billy(560, 300, 1.0, lean=86, armF=(92, 96), armB=(100, 96), legF=(-84, -92), legB=(-92, -96), expr="determined", uid=u,
               hold=(rifle(), -4, .9), head=-80)
    b += pip(470, 290, .7, "grin", glow_uid=u)
    for i in range(16):
        r = random.Random(i + 40)
        b += g(blob("M0,-10 Q10,0 0,10 Q-10,0 0,-10Z", r.choice(["#e0283c", "#ffc61a", "#ff8a1e"]), 3), r.uniform(0, 1200), r.uniform(0, 300), rot=r.randint(0, 90))
    return frame(u, b, "#ffcf7a")


def s_bridge():
    u = "brg"
    b = sky(u, "#ffb86a", "#e86a5a")
    for i, (x, r, c1, c2) in enumerate(((100, 90, "#ffc61a", "#d89a10"), (300, 80, "#e0283c", "#a8162a"), (900, 90, "#ff8a1e", "#d0601a"), (1100, 85, "#b8341e", "#8a2414"))):
        b += tree_round(x, 470, r, c1, c2)
    b += ground(470, "#c8642a", seed=21)
    b += storm_wall(0, 210, 0)
    b += f'<path d="M0,620 Q600,560 1200,620 L1200,750 L0,750Z" fill="#5fb0ff" stroke="{INK}" stroke-width="6"/>'
    # bridge wall
    br = blob("M140,560 L1060,560 L1060,420 L140,420Z", "#a39cb8", 7)
    for row in range(3):
        for col in range(10):
            x = 150 + col * 92 + (46 if row % 2 else 0)
            if x < 1040:
                br += f'<rect x="{x}" y="{424 + row * 46}" width="86" height="40" rx="6" fill="#bdb7cf" stroke="{INK}" stroke-width="4"/>'
    b += mira(800, 380, .95, flip=True, armF=(60, 120), armB=(40, 100), expr="smile", uid=u, head=-8)
    b += billy(420, 390, 1.0, armF=(70, 130), armB=(50, 110), expr="smile", pip=True, uid=u, head=6)
    b += br
    b += honey(610, 330, 1.3)
    b += sparkle(560, 250, 14) + sparkle(670, 240, 10)
    return frame(u, b, "#ffb86a")


def s_squad():
    u = "sqd"
    b = sky(u, "#120a2e", "#3b1a6e")
    for i in range(40):
        rnd = random.Random(i + 100)
        b += f'<circle cx="{rnd.uniform(0, 1200):.0f}" cy="{rnd.uniform(0, 750):.0f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#d8c8ff" opacity=".6"/>'
    b += ('<text x="600" y="80" font-family="Anton, sans-serif" font-size="56" text-anchor="middle" fill="#ffd23f" '
          f'stroke="{INK}" stroke-width="9" paint-order="stroke" letter-spacing="3">SQUADS · ZERO BUILD</text>')
    b += stage(600, 600, 500, 110)
    b += lantern(120, 250, 1.1, uid=u) + lantern(1080, 260, 1.1, uid=u)
    b += billy(400, 470, 1.0, armF=(40, 30), armB=(-30, -20), expr="grin", pip=True, uid=u)
    b += mira(640, 450, .95, armF=(20, 10), armB=(-20, -10), expr="smile", uid=u)
    b += honey(720, 300, .6)
    b += banana(860, 640, .95, arms=(-150, 150))
    for x in (400, 640, 860):
        b += label("READY", x, 160 if x != 640 else 120, 34, "#1b1030", "#ffd23f")
    return frame(u, b, "#120a2e")


def s_hackers():
    u = "hck"
    b = sky(u, "#1b1040", "#6a2a9e")
    b += ('<text x="600" y="96" font-family="Anton, sans-serif" font-size="70" text-anchor="middle" fill="#ff3b3b" '
          f'stroke="{INK}" stroke-width="10" paint-order="stroke" letter-spacing="4" filter="url(#{u}-glow)">HACKERS DETECTED</text>')
    b += gpu_tower(30, 600, 140, 400, lit="#ff4fa3") + gpu_tower(1030, 600, 150, 440)
    b += fan(800, 380, 150, 25)
    b += circuit_floor(590)
    b += speedlines(930, 300, 14, 150, 230, "#ffffff", .7, 6, seed=14)
    b += car(930, 300, 1.05, rot=-160, col="#ffd23f")
    b += bees(700, 560, 22, 60, 2) + bees(330, 380, 16, 50, 5)
    b += banana(220, 690, .75, flip=False, arms=(-160, -120), hold=(smg(), -20))
    b += mira(560, 480, 1.0, armF=(95, 92), armB=(80, 90), legF=(30, 0), legB=(-30, -10), hold=(gatekeeper(), -10), expr="shout", uid=u)
    b += honey(500, 240, .55)
    b += burst(760, 470, 50, 26, 9, "#ffd23f", 5)
    b += sfx("BOOM!", 980, 640, 100, -6)
    return frame(u, b, "#1b1040")


def s_final():
    u = "fin"
    b = sky(u, "#14092e", "#4a1e7a")
    b += storm_column(u, 760, 360, 520, 520)
    b += mask_face(760, 120, .9, u)
    b += geno_machine(800, 640, 1.25, "#120a24")
    b += storm_wall(0, 120, 0) + storm_wall(1100, 1200, 0)
    b += f'<path d="M0,640 L200,520 L360,560 L460,500 L600,600 L1200,620 L1200,750 L0,750Z" fill="#5a4a6a" stroke="{INK}" stroke-width="6"/>'
    b += blob("M200,520 l60,-40 l50,30 l50,10 l-30,40Z", "#7a6a8a", 5)
    # dash streak
    b += f'<path d="M140,120 L520,470" stroke="#c77dff" stroke-width="70" stroke-linecap="round" opacity=".45" filter="url(#{u}-blur4)"/>'
    b += f'<path d="M140,120 L520,470" stroke="#f0d8ff" stroke-width="16" stroke-linecap="round" opacity=".8"/>'
    b += g(billy(0, 0, 1.0, lean=40, armF=(110, 100), armB=(-60, -30), legF=(-30, -70), legB=(-70, -100), expr="shout", pip=True, uid=u,
                 hold=(sweeper(), 0, .9)), 520, 470, .9, rot=10)
    b += player(860, 600, .8, "#c0c4d0", "#7d8396", flip=True, headcol="#e8eef8", armF=(80, 80), armB=(60, 70), uid=u, expr="flat")
    b += bees(860, 420, 30, 60, 8)
    b += mira(1040, 600, .9, flip=True, armF=(95, 92), armB=(80, 90), hold=(gatekeeper(), -6), expr="shout", uid=u)
    b += sfx("PIP!", 330, 250, 80, -14, "#ff8a1e", INK, "#7b2cbf")
    return frame(u, b, "#14092e")


def s_home():
    u = "hom"
    b = '<rect width="1200" height="750" fill="#ffe9c2"/>'
    b += f'<path d="M80,60 h300 v300 h-300Z" fill="#9fd6ff" stroke="{INK}" stroke-width="8"/>'
    b += f'<circle cx="300" cy="140" r="46" fill="#ffd23f" stroke="{INK}" stroke-width="6"/>'
    b += f'<path d="M80,300 Q160,250 230,290 Q300,240 380,280 L380,360 L80,360Z" fill="#c84a3a" stroke="{INK}" stroke-width="5"/>'
    b += f'<path d="M230,60 v300 M80,210 h300" stroke="{INK}" stroke-width="8"/>'
    b += f'<path d="M380,60 L700,750 L900,750 L380,360Z" fill="#fff6c8" opacity=".55"/>'
    b += blob("M60,50 h40 v330 h-40Z", "#7ab06a", 6) + blob("M360,50 h40 v330 h-40Z", "#7ab06a", 6)
    b += '<rect x="0" y="560" width="1200" height="190" fill="#c9a07a" stroke="#1b1030" stroke-width="6"/>'
    inner = (f'<rect x="760" y="200" width="380" height="250" fill="#2a1458"/>'
             f'<ellipse cx="950" cy="400" rx="90" ry="22" fill="#5fd4ff" stroke="{INK}" stroke-width="4"/>'
             + pip(950, 398, 1.05, "grin", glow_uid=u)
             + f'<rect x="866" y="220" width="168" height="40" rx="8" fill="#ffd23f" stroke="{INK}" stroke-width="4"/>'
             '<text x="950" y="250" font-family="Anton, sans-serif" font-size="28" text-anchor="middle" fill="#1b1030">MASTERED</text>')
    b += blob("M720,470 h460 v40 h-460Z", "#6b4a2e", 6)
    b += tv(760, 200, 380, 250, "#2a1458", inner)
    b += beanbag(430, 650, 1.3)
    b += billy(430, 500, 1.05, lean=-6, armF=(70, 110), armB=(40, 100), legF=(80, 20), legB=(70, 10), expr="grin", uid=u,
               hold=(controller(0, 0, .7), 0))
    return frame(u, b, "#ffe9c2")


def s_cover():
    """Portrait background for cover.html (800x1280); the title and words are HTML on top."""
    u = "cov"
    cw, ch = 800, 1280
    from draw import defs
    b = (f'<linearGradient id="{u}-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0628"/>'
         f'<stop offset=".5" stop-color="#3a1670"/><stop offset=".82" stop-color="#b8459a"/><stop offset="1" stop-color="#ff8a4a"/></linearGradient>'
         f'<rect width="{cw}" height="{ch}" fill="url(#{u}-sky)"/><rect width="{cw}" height="{ch}" fill="url(#{u}-dots)"/>')
    rnd = random.Random(5)
    for _ in range(60):
        b += f'<circle cx="{rnd.uniform(0, cw):.0f}" cy="{rnd.uniform(0, 700):.0f}" r="{rnd.uniform(1.5, 3.5):.1f}" fill="#ffffff" opacity="{rnd.uniform(.3, .9):.2f}"/>'
    b += f'<circle cx="420" cy="760" r="330" fill="#ff9a4a" opacity=".35" filter="url(#{u}-soft)"/>'
    for cx, cy, s in ((120, 600, 1.0), (690, 820, 1.2), (180, 980, .8)):
        b += g(f'<path d="M-90,0 Q-90,-40 -50,-40 Q-40,-80 0,-70 Q40,-90 60,-50 Q100,-50 100,0Z" fill="#e8d8ff" stroke="{INK}" stroke-width="6" opacity=".9"/>', cx, cy, s)
    # island
    b += f'<ellipse cx="400" cy="1500" rx="760" ry="420" fill="#4cae55" stroke="{INK}" stroke-width="8"/>'
    b += f'<ellipse cx="400" cy="1510" rx="800" ry="440" fill="none" stroke="#7fd6ff" stroke-width="26"/>'
    b += f'<path d="M60,1150 Q180,1110 300,1160 Q200,1210 60,1150Z" fill="#ff7a1a" stroke="{INK}" stroke-width="6"/>'
    b += f'<path d="M540,1170 Q640,1120 770,1170 Q650,1230 540,1170Z" fill="#c74bd6" stroke="{INK}" stroke-width="6"/>'
    b += geno_machine(430, 1190, .45)
    b += storm_column(u, 435, 1120, 170, 400)
    b += battle_bus(610, 420, .5)
    # Mira on a tower, lower left
    b += blob("M50,1280 L50,1010 L36,990 L154,990 L140,1010 L140,1280Z", "#5d5a7d", 7)
    b += blob("M36,990 L95,950 L154,990Z", "#3d3a5d", 6)
    b += mira(96, 905, .52, armF=(20, 10), armB=(-20, -10), expr="flat", uid=u)
    # Billy gliding under the 'Brella (held in the back hand), Pip on his back, pointing down at the Island
    b += billy(450, 860, 1.3, lean=-6, armF=(70, 40), armB=(-128, -150), legF=(24, -6), legB=(-14, -34), expr="grin", pip=True, uid=u,
               holdB=(umbrella(), -28, 1.0))
    b += speedlines(430, 800, 12, 330, 420, "#ffffff", .35, 5, seed=33, a0=60, a1=120)
    b += pumpkin_chest(680, 1130, .5, u)
    for sx, sy in ((90, 540), (730, 640), (680, 300), (110, 380)):
        b += sparkle(sx, sy, 16)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}">{defs(u)}{b}</svg>')


def s_cover_fg():
    """Transparent foreground for the poster cover: Billy, the 'Brella and Pip, laid over the publisher's poster."""
    u = "cvf"
    cw, ch = 800, 1280
    from draw import defs
    b = f'<ellipse cx="400" cy="700" rx="270" ry="300" fill="#ffd9a0" opacity=".55" filter="url(#{u}-soft)"/>'
    b += f'<ellipse cx="400" cy="700" rx="200" ry="230" fill="#ffffff" opacity=".35" filter="url(#{u}-soft)"/>'
    b += speedlines(400, 720, 26, 250, 380, "#ffffff", .55, 6, seed=33, a0=0, a1=360)
    b += billy(410, 800, 1.42, lean=-6, armF=(70, 40), armB=(-128, -150), legF=(24, -6), legB=(-14, -34), expr="grin", pip=True, uid=u,
               holdB=(umbrella(), -28, 1.0))
    for sx, sy in ((150, 600), (660, 560), (640, 900), (170, 930)):
        b += sparkle(sx, sy, 18)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}">{defs(u)}{b}</svg>'


SCENES = {"cover-fg": s_cover_fg, "cover-art": s_cover, "grove": s_grove, "bridge": s_bridge, "squad": s_squad, "hackers": s_hackers, "final": s_final, "home": s_home, "bedroom": s_bedroom, "bus": s_bus, "pumpkin": s_pumpkin, "extraction": s_extraction, "cheatcode": s_cheatcode,
          "console": s_console, "victory": s_victory, "lobby": s_lobby, "neighborhood": s_neighborhood, "eliminated": s_eliminated}
