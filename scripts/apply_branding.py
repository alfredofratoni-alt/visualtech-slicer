#!/usr/bin/env python3
"""Aplica la identidad de Gráfica Visualtech sobre una copia de OrcaSlicer.

Uso: python3 scripts/apply_branding.py <carpeta_de_OrcaSlicer>

Qué cambia:
  - Nombre visible del programa y del instalador.
  - Íconos, pantalla de inicio, logos del "Acerca de" y de la barra superior.
  - Color de acento: verde azulado de Orca -> naranja Visualtech #F4732A.
  - Modo oscuro en tonos grafito.

Qué NO cambia (a propósito):
  - Cómo lamina: el motor y los perfiles quedan intactos.
  - La carpeta interna de configuración y las traducciones (clave "OrcaSlicer").
  - Los avisos de copyright y licencia de OrcaSlicer, PrusaSlicer y Bambu Studio,
    que la licencia AGPL-3.0 obliga a mantener.
"""
import pathlib
import re
import shutil
import sys

ORCA = pathlib.Path(sys.argv[1]).resolve()
HERE = pathlib.Path(__file__).resolve().parent.parent
ASSETS = HERE / "branding" / "assets"

APP_NAME = "Visualtech Slicer"
APP_FILE = "VisualtechSlicer"
VENDOR = "Grafica Visualtech"
HOMEPAGE = "https://github.com/alfredofratoni-alt/visualtech-slicer"

problems = []


def edit(rel, replacements, required=True):
    """Reemplazos literales o regex en un archivo. Avisa si alguno no encontró nada."""
    path = ORCA / rel
    text = path.read_text(encoding="utf-8")
    for old, new, *flags in replacements:
        if flags and flags[0] == "re":
            text, n = re.subn(old, new, text)
        else:
            n = text.count(old)
            text = text.replace(old, new)
        if n == 0 and required:
            problems.append(f"{rel}: no se encontró {old!r}")
    path.write_text(text, encoding="utf-8")


# 1. Nombre del programa ------------------------------------------------------
edit("version.inc", [('set(SLIC3R_APP_NAME "OrcaSlicer")', f'set(SLIC3R_APP_NAME "{APP_NAME}")')])
edit("src/libslic3r/libslic3r.h", [('#define SLIC3R_APP_FULL_NAME "Orca Slicer"',
                                    f'#define SLIC3R_APP_FULL_NAME "{APP_NAME}"')])
edit("src/slic3r/GUI/GUI_App.cpp", [('std::wstring prog_desc = L"OrcaSlicer";',
                                     f'std::wstring prog_desc = L"{APP_NAME}";')])
# Título de la ventana (barra de tareas) e ícono de bandeja
edit("src/slic3r/GUI/Plater.cpp", [('m_project_name + " - OrcaSlicer"', f'm_project_name + " - {APP_NAME}"')])
edit("src/slic3r/GUI/MainFrame.cpp", [('wxBITMAP_TYPE_ICO), "OrcaSlicer")', f'wxBITMAP_TYPE_ICO), "{APP_NAME}")')])

# Asistente de bienvenida y página de inicio (HTML): nombre del programa.
# "Orca Cloud" y las menciones a OrcaSlicer como autor de plugins se dejan, porque son correctas.
for f in list((ORCA / "resources" / "web").rglob("*.js")) + list((ORCA / "resources" / "web").rglob("*.html")):
    text = f.read_text(encoding="utf-8")
    new = text.replace("Orca Slicer", APP_NAME)
    if new != text:
        f.write_text(new, encoding="utf-8")

# 2. Instalador de Windows ----------------------------------------------------
edit("CMakeLists.txt", [
    ('set (CPACK_PACKAGE_NAME "OrcaSlicer")', f'set (CPACK_PACKAGE_NAME "{APP_NAME}")'),
    ('set (CPACK_PACKAGE_VENDOR "SoftFever")', f'set (CPACK_PACKAGE_VENDOR "{VENDOR}")'),
    ('set (CPACK_PACKAGE_FILE_NAME "OrcaSlicer_Windows_Installer_V${SoftFever_VERSION}")',
     f'set (CPACK_PACKAGE_FILE_NAME "{APP_FILE}_Windows_Installer_V${{SoftFever_VERSION}}")'),
    ('set (CPACK_PACKAGE_DESCRIPTION_SUMMARY "Orca Slicer is an open source slicer for FDM printers")',
     f'set (CPACK_PACKAGE_DESCRIPTION_SUMMARY "{APP_NAME}: laminador de {VENDOR}, basado en OrcaSlicer")'),
    ('set (CPACK_PACKAGE_HOMEPAGE_URL "https://github.com/OrcaSlicer/OrcaSlicer")',
     f'set (CPACK_PACKAGE_HOMEPAGE_URL "{HOMEPAGE}")'),
    ('set (CPACK_PACKAGE_INSTALL_REGISTRY_KEY "OrcaSlicer")',
     f'set (CPACK_PACKAGE_INSTALL_REGISTRY_KEY "{APP_FILE}")'),
    ('set(CPACK_PACKAGE_EXECUTABLES "orca-slicer;OrcaSlicer")',
     f'set(CPACK_PACKAGE_EXECUTABLES "orca-slicer;{APP_NAME}")'),
    ('set(CPACK_WIX_UPGRADE_GUID "058245e8-20e0-4a95-9ab7-1acfe17ad511")',
     'set(CPACK_WIX_UPGRADE_GUID "6f3c1a52-8e1d-4c7b-9a54-2b7e0d9f4c31")'),
])

# 3. Imágenes -----------------------------------------------------------------
IMAGES = {
    "icon.ico": ["OrcaSlicer.ico"],
    "icon_154.ico": ["OrcaSlicerTitle.ico"],
    "icon_256.ico": ["OrcaSlicer-mac_256px.ico"],
    "icon_154.png": ["OrcaSlicer.png", "OrcaSlicerTitle.png", "OrcaSlicer_154.png"],
    "icon_184.png": ["OrcaSlicer_154_title.png"],
    "icon_32.png": ["OrcaSlicer_32px.png"],
    "icon_64.png": ["OrcaSlicer_64.png"],
    "icon_128.png": ["OrcaSlicer_128px.png", "OrcaSlicer-mac_128px.png"],
    "icon_192.png": ["OrcaSlicer_192px.png"],
    "icon_grayscale_192.png": ["OrcaSlicer_192px_grayscale.png"],
    "icon_transparent_192.png": ["OrcaSlicer_192px_transparent.png"],
    "icon.svg": ["OrcaSlicer.svg"],
    "icon_transparent.svg": ["OrcaSlicer_gradient.svg", "OrcaSlicer_gradient_circle.svg",
                             "OrcaSlicer_gradient_narrow.svg", "OrcaSlicer_gray.svg", "studio_logo.svg"],
    "splash_light.svg": ["splash_logo.svg"],
    "splash_dark.svg": ["splash_logo_dark.svg"],
    "about_light.svg": ["OrcaSlicer_about.svg"],
    "about_dark.svg": ["OrcaSlicer_about_dark.svg"],
    "horizontal_light.svg": ["OrcaSlicer_horizontal_light.svg"],
    "horizontal_dark.svg": ["OrcaSlicer_horizontal_dark.svg"],
}
img_dir = ORCA / "resources" / "images"
for src, targets in IMAGES.items():
    for t in targets:
        if not (img_dir / t).exists():
            problems.append(f"falta la imagen original {t}")
        shutil.copyfile(ASSETS / src, img_dir / t)
# Logos del asistente de bienvenida y de la página de inicio
web_img = ORCA / "resources" / "web" / "image"
shutil.copyfile(ASSETS / "icon_154.png", web_img / "logo.png")
from PIL import Image  # noqa: E402
_icon = Image.open(ASSETS / "icon_1024.png").convert("RGBA").resize((339, 339), Image.LANCZOS)
_logo2 = Image.new("RGBA", (339, 406), (0, 0, 0, 0))
_logo2.paste(_icon, (0, 33), _icon)
_logo2.save(web_img / "logo2.png")

# 4. Color de acento ----------------------------------------------------------
HEX = [  # (Orca, Visualtech)
    ("#009688", "#F4732A"),  # acento
    ("#009687", "#F4732A"),
    ("#26A69A", "#FF7A2D"),  # hover (brillo +6 %)
    ("#00675B", "#D9621F"),  # acento oscurecido
    ("#008172", "#FF7A2D"),  # hover en modo oscuro
    ("#4DB6AC", "#F7A072"),  # acento suave
    ("#3B4446", "#1E1F22"),  # barra superior -> grafito
    ("#009789", "#F4732A"),
    ("#BFE1DE", "#FDE6D8"),  # fondo de ítem seleccionado (naranja claro)
    ("#E5F0EE", "#FEF1E8"),  # fondo suave
    ("#223C3C", "#3A2416"),  # ítem seleccionado en modo oscuro
]
GENERIC = [
    (r"0x009688\b", "0xF4732A"),
    (r"\b0,\s*150,\s*136\b", "244, 115, 42"),
    (r"ImVec4\(0\.00f, 0\.59f, 0\.53f", "ImVec4(0.96f, 0.45f, 0.16f"),
]
patterns = [(re.compile(re.escape(a), re.I), b) for a, b in HEX] + [(re.compile(a), b) for a, b in GENERIC]

roots = [(ORCA / "src", ("*.cpp", "*.hpp", "*.h")),
         (ORCA / "resources" / "images", ("*.svg",)),
         (ORCA / "resources" / "web", ("*.css", "*.html", "*.js", "*.svg"))]
changed = 0
for root, globs in roots:
    for g in globs:
        for f in root.rglob(g):
            try:
                text = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            new = text
            for rx, rep in patterns:
                new = rx.sub(rep, new)
            if new != text:
                f.write_text(new, encoding="utf-8")
                changed += 1

edit("src/libslic3r/Color.hpp", [
    ("{0.0f, 150.f / 255.0f, 136.0f / 255}", "{244.0f / 255.0f, 115.f / 255.0f, 42.0f / 255}"),
    ("{0.0f, 150.f / 255.0f, 136.0f / 255, 1.0f}", "{244.0f / 255.0f, 115.f / 255.0f, 42.0f / 255, 1.0f}"),
])

# 5. Modo oscuro grafito (tabla de equivalencias claro -> oscuro) ------------
edit("src/slic3r/GUI/Widgets/StateColor.cpp", [
    (r'\{"#F4732A", "#[0-9A-Fa-f]{6}"\}', '{"#F4732A", "#F4732A"}', "re"),   # el naranja no cambia
    (r'\{"#FF7A2D", "#[0-9A-Fa-f]{6}"\}', '{"#FF7A2D", "#FF7A2D"}', "re"),
    (r'\{"#1E1F22", "#[0-9A-Fa-f]{6}"\}', '{"#1E1F22", "#131415"}', "re"),   # barra superior
    (r'\{"#FFFFFF", "#[0-9A-Fa-f]{6}"\}', '{"#FFFFFF", "#1B1C1E"}', "re"),   # fondo de ventanas
    (r'\{"#FEFFFF", "#[0-9A-Fa-f]{6}"\}', '{"#FEFFFF", "#131415"}', "re"),   # barra lateral
    (r'\{"#EEEEEE", "#[0-9A-Fa-f]{6}"\}', '{"#EEEEEE", "#2C2E32"}', "re"),   # líneas separadoras
    (r'\{"#262E30", "#[0-9A-Fa-f]{6}"\}', '{"#262E30", "#F2F2F3"}', "re"),   # texto
])

print(f"Marca aplicada. Archivos con color modificado: {changed}")
if problems:
    print("ATENCIÓN, revisar:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
