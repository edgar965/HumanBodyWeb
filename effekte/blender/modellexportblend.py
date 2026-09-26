# -*- coding: utf-8 -*-
"""modellexportblend — eine GLB in eine .blend umschreiben.

Aufruf (aus `core/dienste/modellexportlauf.py`), MIT `--factory-startup`:

    blender -b --factory-startup --python modellexportblend.py -- --glb <quelle.glb> --blend <ziel.blend>

Nur DAS tut dieses Skript: GLB importieren (Netz, Skin, Werkstoffe samt
Texturen, Animation — glTF trägt das alles), leere Szene, dann speichern.
Kein eigener Retarget- oder Simulationsschritt wie bei `kleidwind.py` — die
Figur kommt aus dem Browser bereits fertig.

`--factory-startup` IST PFLICHT (Fund 26.09.2026): Ohne das lädt Blender
Edgars volles Nutzerprofil samt aller installierten Add-ons (KeenTools,
MPFB, HumanBodyBlender, MB-Lab, BVH-Retargeter, …). Mindestens eines legt
dabei ein eigenes Boilerplate-Objekt („Icosphere", 42 Punkte, ohne Werkstoff)
in der Szene an — nicht nur beim Start, sondern hartnäckig: es sogar VOR
dem Speichern wieder zu löschen (`bpy.data.objects.remove`) half nicht, es
war in der gespeicherten Datei trotzdem da. Nur mit `--factory-startup`
(Werks-Add-ons, ohne Nutzerprofil — glTF-Im/Export ist eines der aktivierten
Werks-Add-ons) bleibt die Szene sauber, UND der Start ist ohne das
Add-on-Laden spürbar schneller.
"""

import argparse
import sys

import bpy  # noqa: E402  # pyright: ignore[reportMissingImports]  (Blender)


def argumente(argv):
    parser = argparse.ArgumentParser(prog='modellexportblend')
    parser.add_argument('--glb', required=True)
    parser.add_argument('--blend', required=True)
    # Blender reicht alles vor "--" unverändert mit durch; nur der Teil danach
    # gehört uns.
    trenner = argv.index('--') if '--' in argv else len(argv)
    return parser.parse_args(argv[trenner + 1:])


def main():
    a = argumente(sys.argv)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.glb)
    bpy.ops.wm.save_as_mainfile(filepath=a.blend)
    print('modellexportblend: geschrieben %s' % a.blend, flush=True)


if __name__ == '__main__':
    main()
