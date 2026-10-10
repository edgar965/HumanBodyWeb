# -*- coding: utf-8 -*-
"""Blendmaterialbild — läuft IN Blender (aus `blendmaterialgraph.py`): ein Bild eines Bildknotens als Eintrag des Materialgraphen.

Der lokale Backer liest die Pixel selbst (`core/dienste/hautbacken/hautbackenbild.py`), Blender liefert nur Pfad und die Angaben, die Cycles zum Bild braucht
(`ImageTextureNode::image_params`, `intern/cycles/scene/shader_nodes.cpp`): Farbraum, Alpha-Modus, Quelle. Eine gepackte Datei schreibt `Blendexport.bildpfad` unverändert
neben den Export; ein Format, das cv2 nicht liest (DDS, TGA, EXR …), legt `Blendexport.als_png` als PNG ab (Pixel unverändert, Farbraum „Non-Color"). Kennzeichen
`ungeprueft` nennt Fälle, in denen der lokale Weg nicht gegen Blender gemessen ist (gepacktes oder umgewandeltes Bild).
"""

import os


class Blendmaterialbild:
    #: Endungen, die der lokale Backer ohne Umweg liest (cv2).
    DIREKT = ('.png', '.jpg', '.jpeg', '.bmp')

    def __init__(self, exporter):
        self.exporter = exporter
        self.bilder = {}

    def eintrag(self, bild):
        """Name des Bildeintrags (Schlüssel in `bilder`) für ein Blender-Bild; legt den Eintrag beim ersten Mal an."""
        if bild.name in self.bilder:
            return bild.name
        pfad = self.exporter.bildpfad(bild)
        gepackt = bild.packed_file is not None
        ungeprueft = []
        if pfad and os.path.isfile(pfad) and os.path.splitext(pfad)[1].lower() not in self.DIREKT:
            name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in bild.name) + '_umgewandelt.png'
            pfad = self.exporter.als_png(bild, name)
            ungeprueft.append('Format %s nach PNG umgewandelt (Cycles liest es mit OpenImageIO)' % os.path.splitext(bild.filepath)[1])
        if gepackt:
            ungeprueft.append('gepackte Datei (Cycles liest sie über Blenders eigenen Bildspeicher)')
        self.bilder[bild.name] = {
            'datei': pfad or None,
            'farbraum': bild.colorspace_settings.name,
            'alpha_modus': bild.alpha_mode,
            'quelle': bild.source,
            'ist_float': bool(bild.is_float),
            'kanaele': int(bild.channels),
            'tiefe': int(bild.depth),
            'groesse': [int(bild.size[0]), int(bild.size[1])],
            'gepackt': gepackt,
            'ungeprueft': ungeprueft,
        }
        return bild.name
