# Visualtech Slicer

Laminador de **Gráfica Visualtech** para las impresoras Elegoo OrangeStorm Giga.
Es OrcaSlicer con la identidad de Visualtech: mismo motor, mismos perfiles, otra cara.

## Descargar

1. Entrá a la pestaña **Actions** de este repositorio.
2. Abrí la última ejecución con tilde verde de "Compilar Visualtech Slicer (Windows)".
3. Abajo, en **Artifacts**, descargá:
   - `VisualtechSlicer-instalador-Windows`: el instalador.
   - `VisualtechSlicer-portable-Windows`: una versión que corre sin instalar.

La primera compilación tarda entre 3 y 4 horas porque arma todas las librerías.
Las siguientes tardan alrededor de 1 hora y media.

## Primer uso

En el asistente inicial elegí la impresora **Elegoo OrangeStorm Giga** con boquilla **0.8**.

## Cómo está armado

Este repositorio no copia el código de OrcaSlicer. En cada compilación:

1. Baja OrcaSlicer en la versión indicada en `ORCA_TAG`
   (`.github/workflows/compilar-windows.yml`).
2. Corre `scripts/apply_branding.py`, que cambia nombre, logos, íconos y colores.
3. Compila y arma el instalador.

| Carpeta | Contenido |
|---|---|
| `branding/assets/` | Logos e íconos listos para usar |
| `branding/make_assets.py` | Genera los logos a partir del logo de Gráfica Visualtech |
| `branding/previews/` | Vistas previas para revisar a ojo |
| `scripts/apply_branding.py` | Aplica la marca sobre OrcaSlicer |

### Actualizar a una versión nueva de OrcaSlicer

Cambiá `ORCA_TAG` en el workflow (por ejemplo `v2.5.0`) y guardá. Si el script avisa que
no encontró algo, es que OrcaSlicer cambió ese archivo y hay que ajustar el reemplazo.

### Cambiar los logos

Editá `branding/make_assets.py` y corré:

```
pip install cairosvg pillow fonttools
python3 branding/make_assets.py branding/fonts branding/assets
```

## Licencia

Visualtech Slicer se basa en [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer),
que a su vez se basa en PrusaSlicer y Bambu Studio. Se distribuye bajo la
**GNU Affero General Public License v3** (ver `LICENSE`). Los avisos de copyright
originales se mantienen dentro del programa, en la ventana "Acerca de".

Las fuentes Fira Sans Condensed y Montserrat se usan bajo la SIL Open Font License
(`branding/fonts/OFL-*.txt`).
