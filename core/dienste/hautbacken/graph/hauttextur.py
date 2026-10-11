# -*- coding: utf-8 -*-
"""Hauttextur — ein Bild des Materials so, wie Cycles es hält: RGBA unten-zuerst, Alpha nach den Regeln von `ImageMetaData::finalize` und `conform_pixels`.

Übernommen aus `intern/cycles/util/image_metadata.cpp` (`finalize`, `conform_pixels_to_metadata_type`), `util/image.h` (`util_image_multiply_native`) und `scene/image.cpp` (Bildtypen);
Blender-Quelltext vom 10.10.2026 und 11.10.2026:
    * Farbraum: `sRGB` bleibt sRGB und wird NACH der Interpolation umgerechnet (`is_compressible_as_srgb`); `Non-Color` ist „Daten"; `Linear Rec.709` ist Arbeitsfarbraum (keine
      Umrechnung). Alles andere braucht OpenColorIO — nicht übernommen, der Fehler nennt den Farbraum.
    * Alpha: Blenders Alpha-Modus STRAIGHT = „unassociated" → die Farben werden mit dem Alpha multipliziert (`(c · a) / 255` bzw. `/ 65535` in Ganzzahlen), außer bei Daten-Bildern; PREMUL
      (assoziiert), CHANNEL_PACKED und NONE (Alpha ignorieren: Alpha = 1) lassen die Farben unberührt.
    * Kanäle: 1 → (g, g, g, 1), 2 → (g, g, g, a), 3 → (r, g, b, 1).
    * Tiefe: 8 Bit (`BYTE`) und 16 Bit (`USHORT`, ein PNG/TIFF mit 16 Bit je Kanal) werden als Ganzzahlen gehalten und durch ihr Maximum geteilt; hier liegen beide mit 16 Bit je Kanal
      im Speicher (ein 8-Bit-Wert x als x · 257: x · 257 / 65535 ist genau x / 255).
Nicht übernommen: Fließkommabilder (`FLOAT`/`HALF`: EXR, HDR), geteilte Kacheln (UDIM), Bildfolgen — der Fehler sagt, was es ist.
"""

import cv2
import numpy as np
import warp as wp

from .hautgraphfehler import Hautgraphfehler
from .hauttexturkernel import CLIP, CLOSEST, CUBIC, EXTEND, LINEAR, MIRROR, REPEAT, abtasten

__all__ = ['Hauttextur']

INTERPOLATION = {'Linear': LINEAR, 'Closest': CLOSEST, 'Cubic': CUBIC, 'Smart': CUBIC}          # `ImageInterpolator::interp`: alles andere ist kubisch
ERWEITERUNG = {'REPEAT': REPEAT, 'EXTEND': EXTEND, 'CLIP': CLIP, 'MIRROR': MIRROR}
DATEN = ('Non-Color', 'Raw')
ARBEITSFARBRAUM = ('Linear Rec.709', 'scene_linear', 'Linear')


class Hauttextur:
    def __init__(self, name, eintrag, geraet='cuda:0'):
        """`eintrag`: der Bildeintrag des Graphen (`bilder[name]`): `datei`, `farbraum`, `alpha_modus`, `quelle`, `ist_float`."""
        grund = self.pruefen(name, eintrag)
        if grund:
            raise Hautgraphfehler(grund)
        self.name, self.geraet = name, geraet
        self.daten_farbraum = eintrag['farbraum'] in DATEN
        self.srgb = eintrag['farbraum'] == 'sRGB'
        self.alpha_modus = eintrag['alpha_modus']
        rgba = self._lesen(eintrag['datei'])
        self.hoehe, self.breite = rgba.shape[:2]
        # Cycles hält die Zeilen unten-zuerst (der Lader spiegelt Dateien beim Lesen, Blenders Bildspeicher ist von Haus aus so).
        self.feld = wp.array(np.ascontiguousarray(rgba[::-1]).reshape(-1), dtype=wp.uint16, device=geraet)

    @staticmethod
    def pruefen(name, eintrag):
        """Warum das Bild nicht gelesen werden kann (Text) oder `''`."""
        if eintrag.get('quelle') != 'FILE':
            return 'Bild „%s": Quelle %s (nur Dateien sind übernommen)' % (name, eintrag.get('quelle'))
        if not eintrag.get('datei'):
            return 'Bild „%s": keine Datei (weder auf der Platte noch gepackt)' % name
        if eintrag.get('ist_float') and eintrag.get('gepackt'):
            # Ein gepacktes Bild liest Cycles aus Blenders Bildspeicher (`BlenderImageLoader`): als Fließkomma, schon in den Arbeitsfarbraum gerechnet — nicht übernommen.
            # Eine Datei liest Cycles selbst (OpenImageIO): 8 oder 16 Bit je Kanal bleiben Ganzzahlen; ob sie Fließkomma ist, zeigt erst die Datei (`_lesen`). Blenders `is_float`
            # sagt das nicht (ein 16-Bit-PNG ist dort Fließkomma, für Cycles `USHORT`).
            return 'Bild „%s": gepacktes Bild mit mehr als 8 Bit (Cycles liest es als Fließkomma aus Blenders Bildspeicher; noch nicht übernommen)' % name
        farbraum = eintrag.get('farbraum')
        if farbraum != 'sRGB' and farbraum not in DATEN and farbraum not in ARBEITSFARBRAUM:
            return 'Bild „%s": Farbraum „%s" (nur sRGB, Non-Color und Linear Rec.709 sind übernommen)' % (name, farbraum)
        if eintrag.get('alpha_modus') not in ('STRAIGHT', 'PREMUL', 'CHANNEL_PACKED', 'NONE'):
            return 'Bild „%s": Alpha-Modus %s' % (name, eintrag.get('alpha_modus'))
        return ''

    def _lesen(self, pfad):
        """`(h, w, 4)` uint16 RGBA (8-Bit-Dateien als Wert · 257), Alpha nach `conform_pixels` behandelt."""
        roh = cv2.imdecode(np.fromfile(str(pfad), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if roh is None:
            raise Hautgraphfehler('Bild „%s" nicht lesbar: %s' % (self.name, pfad))
        if roh.dtype not in (np.uint8, np.uint16):
            raise Hautgraphfehler('Bild „%s": %s je Kanal — Fließkommabilder sind noch nicht übernommen (nur 8 und 16 Bit)' % (self.name, roh.dtype))
        maximum = 65535 if roh.dtype == np.uint16 else 255            # `util_image_cast_from_float<…>(1.0f)`: der Wert „voll" des Speichertyps
        if roh.ndim == 2:
            rgba = np.stack([roh, roh, roh, np.full_like(roh, maximum)], axis=-1)
            kanaele = 1
        elif roh.shape[2] == 2:
            rgba = np.stack([roh[..., 0], roh[..., 0], roh[..., 0], roh[..., 1]], axis=-1)
            kanaele = 2
        elif roh.shape[2] == 3:
            rgba = np.concatenate([roh[..., ::-1], np.full(roh.shape[:2] + (1,), maximum, roh.dtype)], axis=-1)
            kanaele = 3
        else:
            rgba = np.concatenate([roh[..., 2::-1], roh[..., 3:4]], axis=-1)
            kanaele = 4
        # `finalize`: unassociated = STRAIGHT und kein Daten-Bild; dann `conform_pixels`: Farben mit Alpha multiplizieren (nur bei vier Kanälen), `util_image_multiply_native`: (a · b) / Maximum
        if kanaele == 4 and self.alpha_modus == 'STRAIGHT' and not self.daten_farbraum:
            rgb = (rgba[..., :3].astype(np.uint32) * rgba[..., 3:4].astype(np.uint32)) // maximum
            rgba = np.concatenate([rgb.astype(roh.dtype), rgba[..., 3:4]], axis=-1)
        if self.alpha_modus == 'NONE':
            rgba = rgba.copy()
            rgba[..., 3] = maximum
        if roh.dtype == np.uint8:
            rgba = rgba.astype(np.uint16) * np.uint16(257)
        return rgba

    def abtasten(self, koordinate, interpolation, erweiterung, entassoziieren, aus):
        """`aus[i]` (vec4) = das Bild an `koordinate[i]` (u, v, ·) — `svm_node_tex_image`."""
        # „Alpha ent-assoziieren" gilt nur, wenn der Alpha-Ausgang des Knotens gelesen wird und das Bild kein Daten-/Kanal-gepacktes/ignoriertes ist
        ent = int(bool(entassoziieren) and not self.daten_farbraum and self.alpha_modus not in ('CHANNEL_PACKED', 'NONE'))
        wp.launch(abtasten, dim=len(koordinate), inputs=[self.feld, self.breite, self.hoehe, koordinate, INTERPOLATION[interpolation], ERWEITERUNG[erweiterung],
                                                          int(self.srgb), ent, aus], device=self.geraet)
