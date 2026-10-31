#!/usr/bin/env python3
"""Genera los logos e íconos de Visualtech Slicer a partir del logo de Gráfica Visualtech.

Uso: python3 make_assets.py <carpeta_fuentes> <carpeta_salida>

El texto del logo se convierte en trazos (paths) porque el lector de SVG de
OrcaSlicer (nanosvg) no dibuja elementos <text>.
"""
import io
import os
import sys

import cairosvg
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image

FONT_DIR, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

ACCENT = "#f4732a"
LIGHT = {"ink": "#050606", "mid": "#707478"}
DARK = {"ink": "#f2f2f3", "mid": "#8a8e93"}
GRAPHITE = "#1e1f22"

FIRA = TTFont(os.path.join(FONT_DIR, "FiraSansCondensed-Regular.ttf"))
MONT = instancer.instantiateVariableFont(
    TTFont(os.path.join(FONT_DIR, "Montserrat-Italic.ttf")), {"wght": 800})


def text_path(font, text, x, y, size, text_length=None, letter_spacing=0.0):
    """Devuelve el atributo d de un path con el texto dibujado en (x, y) de línea base."""
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    names = [cmap[ord(c)] for c in text]
    spacing_units = letter_spacing * upm
    natural = sum(hmtx[n][0] for n in names) + spacing_units * (len(names) - 1)
    sx = (text_length / (natural * size / upm)) if text_length else 1.0
    pen = SVGPathPen(gs)
    cursor = 0.0
    for n in names:
        k = size / upm
        t = TransformPen(pen, (k * sx, 0, 0, -k, x + cursor * k * sx, y))
        gs[n].draw(t)
        cursor += hmtx[n][0] + spacing_units
    return pen.getCommands(), natural * size / upm * sx


RHOMBI = [  # de abajo hacia arriba, como en el logo
    ("M373 398 461 486 373 574 285 486Z", "ink"),
    ("M373 339 461 427 373 515 285 427Z", "mid"),
    ("M373 278 461 366 373 454 285 366Z", "accent"),
]


def rhombi(pal, dx=0, dy=0, scale=1.0):
    out = []
    for d, role in RHOMBI:
        color = ACCENT if role == "accent" else pal[role]
        out.append(f'<path d="{d}" fill="{color}"/>')
    return (f'<g transform="translate({dx} {dy}) scale({scale})">' + "".join(out) + "</g>")


def logo_group(pal):
    g1, _ = text_path(FIRA, "Gráfica", 593, 318, 158, 376)
    visual_len = 910 * 6 / 10  # "Visual" ocupa la parte proporcional del ancho total
    # Ancho natural de cada parte para repartir textLength=910 entre "Visual" y "tech".
    _, wv = text_path(FIRA, "Visual", 0, 0, 250)
    _, wt = text_path(FIRA, "tech", 0, 0, 250)
    sv = 910 * wv / (wv + wt)
    g2, _ = text_path(FIRA, "Visual", 488, 541, 250, sv)
    g3, _ = text_path(FIRA, "tech", 488 + sv, 541, 250, 910 - sv)
    del visual_len
    return (rhombi(pal) +
            f'<path d="{g1}" fill="{pal["ink"]}"/>'
            f'<path d="{g2}" fill="{pal["ink"]}"/>'
            f'<path d="{g3}" fill="{ACCENT}"/>')


def svg(w, h, body, viewbox=None):
    vb = viewbox or f"0 0 {w} {h}"
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">'
            f"{body}</svg>\n")


def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    return content


# --- Logo completo (alto 400, ancho 1160 en coordenadas del logo original) ---
for mode, pal in (("light", LIGHT), ("dark", DARK)):
    save(f"logo_{mode}.svg", svg(1160, 400, logo_group(pal), "270 190 1160 400"))

# --- Ícono de la app: tres rombos sobre cuadrado grafito redondeado ---
ICON_BODY = (f'<rect x="0" y="0" width="512" height="512" rx="96" fill="{GRAPHITE}"/>' +
             rhombi(DARK, dx=256 - 373 * 1.25, dy=256 - 426 * 1.25, scale=1.25))
icon_svg = save("icon.svg", svg(512, 512, ICON_BODY))
ICON_TRANSPARENT = rhombi(LIGHT, dx=256 - 373 * 1.5, dy=256 - 426 * 1.5, scale=1.5)
icon_t_svg = save("icon_transparent.svg", svg(512, 512, ICON_TRANSPARENT))


# --- Título de la app en Montserrat 800 itálica ---
def title_paths(text, x, y, size, color):
    d, w = text_path(MONT, text, x, y, size, letter_spacing=0.01)
    return f'<path d="{d}" fill="{color}"/>', w


# Pantalla de inicio 480x480: rombos, nombre y línea naranja con rombo
for mode, pal in (("light", LIGHT), ("dark", DARK)):
    bg = "#ffffff" if mode == "light" else "#1b1c1e"
    ink = "#1e1f22" if mode == "light" else "#f2f2f3"
    t1, w1 = title_paths("VISUALTECH", 0, 0, 52, ink)
    _, w1 = text_path(MONT, "VISUALTECH", 0, 0, 52, letter_spacing=0.01)
    _, w2 = text_path(MONT, "SLICER", 0, 0, 52, letter_spacing=0.01)
    p1, _ = title_paths("VISUALTECH", 240 - w1 / 2, 340, 52, ink)
    p2, _ = title_paths("SLICER", 240 - w2 / 2, 396, 52, ACCENT)
    body = (f'<rect width="480" height="480" fill="{bg}"/>' +
            rhombi(pal, dx=240 - 373 * 0.62, dy=160 - 426 * 0.62, scale=0.62) + p1 + p2 +
            f'<rect x="60" y="430" width="360" height="2" fill="{ACCENT}"/>'
            f'<rect x="414" y="425" width="8" height="8" fill="{ACCENT}" transform="rotate(45 418 429)"/>')
    save(f"splash_{mode}.svg", svg(480, 480, body))

# "Acerca de" 560x125: logo + separador + nombre de la app
for mode, pal in (("light", LIGHT), ("dark", DARK)):
    ink = "#1e1f22" if mode == "light" else "#f2f2f3"
    line = "#dcdee1" if mode == "light" else "#2c2e32"
    s = 105 / 400  # el logo ocupa 105 px de alto
    logo = f'<g transform="translate(0 10) scale({s}) translate(-270 -190)">{logo_group(pal)}</g>'
    sep = f'<rect x="{1160 * s + 18}" y="22" width="1" height="81" fill="{line}"/>'
    p, _ = title_paths("SLICER", 1160 * s + 38, 80, 44, ink)
    save(f"about_{mode}.svg", svg(560, 125, logo + sep + p))

# Logo horizontal 214x80 (barra superior y asistentes)
for mode, pal in (("light", LIGHT), ("dark", DARK)):
    s = 214 / 1160
    body = f'<g transform="translate(0 {(80 - 400 * s) / 2}) scale({s}) translate(-270 -190)">{logo_group(pal)}</g>'
    save(f"horizontal_{mode}.svg", svg(214, 80, body))


# --- PNG e ICO ---
def png(svg_text, size):
    data = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(data)).convert("RGBA")


for size in (32, 64, 128, 154, 184, 192, 256, 1024):
    png(icon_svg, size).save(os.path.join(OUT, f"icon_{size}.png"))
png(icon_t_svg, 192).save(os.path.join(OUT, "icon_transparent_192.png"))
png(icon_svg, 192).convert("LA").convert("RGBA").save(os.path.join(OUT, "icon_grayscale_192.png"))

big = png(icon_svg, 256)
big.save(os.path.join(OUT, "icon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
big.save(os.path.join(OUT, "icon_256.ico"), sizes=[(256, 256)])
png(icon_svg, 154).save(os.path.join(OUT, "icon_154.ico"), sizes=[(154, 154)])

# Vistas previas para revisar a ojo
for name in ("splash_light", "splash_dark", "about_light", "about_dark", "logo_light", "logo_dark"):
    with open(os.path.join(OUT, f"{name}.svg"), encoding="utf-8") as f:
        cairosvg.svg2png(bytestring=f.read().encode(), write_to=os.path.join(OUT, f"_preview_{name}.png"),
                         output_width=560 if name.startswith("about") else 480)
print("Listo:", sorted(os.listdir(OUT)))
