# -*- coding: utf-8 -*-
"""Hauttextur — ein Bild des Materials so, wie Cycles es hält: RGBA-Bytes unten-zuerst, Alpha nach den Regeln von `ImageMetaData::finalize` und `conform_pixels`.

Übernommen aus `intern/cycles/util/image_metadata.cpp` (`finalize`, `conform_pixels_to_metadata_type`; Blender-Quelltext vom 10.10.2026):
    * Farbraum: `sRGB` bleibt sRGB und wird NACH der Interpolation umgerechnet (`is_compressible_as_srgb`); `Non-Color` ist „Daten"; `Linear Rec.709` ist Arbeitsfarbraum (keine
      Umrechnung). Alles andere braucht OpenColorIO — nicht übernommen, der Fehler nennt den Farbraum.
    * Alpha: Blenders Alpha-Modus STRAIGHT = „unassociated" → die Farben werden mit dem Alpha multipliziert (`(c · a) / 255` in Ganzzahlen), außer bei Daten-Bildern; PREMUL (assoziiert),
      CHANNEL_PACKED und NONE (Alpha ignorieren: Alpha = 1) lassen die Farben unberührt.
    * Kanäle: 1 → (g, g, g, 1), 2 → (g, g, g, a), 3 → (r, g, b, 1).
Nicht übernommen: 16-Bit- und Fließkommabilder (Cycles rechnet sie anders), geteilte Kacheln (UDIM), Bildfolgen — der Fehler sagt, was es ist.
"""

import cv2
import numpy as np
import warp as wp

from .hautgraphfehler import Hautgraphfehler
from .hauttexturkernel import CUBIC, CLIP, CLOSEST, EXTEND, LINEAR, MIRROR, REPEAT, abtasten

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
        self.feld = wp.array(np.ascontiguousarray(rgba[::-1]).reshape(-1), dtype=wp.uint8, device=geraet)

    @staticmethod
    def pruefen(name, eintrag):
        """Warum das Bild nicht gelesen werden kann (Text) oder `''`."""
        if eintrag.get('quelle') != 'FILE':
            return 'Bild „%s": Quelle %s (nur Dateien sind übernommen)' % (name, eintrag.get('quelle'))
        if not eintrag.get('datei'):
            return 'Bild „%s": keine Datei (weder auf der Platte noch gepackt)' % name
        if eintrag.get('ist_float') or eintrag.get('tiefe') in (64, 96, 128):
            return 'Bild „%s": Fließkomma- oder 16-Bit-Bild (noch nicht übernommen)' % name
        farbraum = eintrag.get('farbraum')
        if farbraum != 'sRGB' and farbraum not in DATEN and farbraum not in ARBEITSFARBRAUM:
            return 'Bild „%s": Farbraum „%s" (nur sRGB, Non-Color und Linear Rec.709 sind übernommen)' % (name, farbraum)
        if eintrag.get('alpha_modus') not in ('STRAIGHT', 'PREMUL', 'CHANNEL_PACKED', 'NONE'):
            return 'Bild „%s": Alpha-Modus %s' % (name, eintrag.get('alpha_modus'))
        return ''

    def _lesen(self, pfad):
        """`(h, w, 4)` uint8 RGBA, Alpha nach `conform_pixels` behandelt."""
        roh = cv2.imdecode(np.fromfile(str(pfad), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        if roh is None:
            raise Hautgraphfehler('Bild „%s" nicht lesbar: %s' % (self.name, pfad))
        if roh.dtype != np.uint8:
            raise Hautgraphfehler('Bild „%s": %s statt 8 Bit je Kanal (noch nicht übernommen)' % (self.name, roh.dtype))
        if roh.ndim == 2:
            rgba = np.stack([roh, roh, roh, np.full_like(roh, 255)], axis=-1)
            kanaele = 1
        elif roh.shape[2] == 2:
            rgba = np.stack([roh[..., 0], roh[..., 0], roh[..., 0], roh[..., 1]], axis=-1)
            kanaele = 2
        elif roh.shape[2] == 3:
            rgba = np.concatenate([roh[..., ::-1], np.full(roh.shape[:2] + (1,), 255, np.uint8)], axis=-1)
            kanaele = 3
        else:
            rgba = np.concatenate([roh[..., 2::-1], roh[..., 3:4]], axis=-1)
            kanaele = 4
        # `finalize`: unassociated = STRAIGHT und kein Daten-Bild; dann `conform_pixels`: Farben mit Alpha multiplizieren (nur bei vier Kanälen)
        if kanaele == 4 and self.alpha_modus == 'STRAIGHT' and not self.daten_farbraum:
            rgb = (rgba[..., :3].astype(np.uint32) * rgba[..., 3:4].astype(np.uint32)) // 255
            rgba = np.concatenate([rgb.astype(np.uint8), rgba[..., 3:4]], axis=-1)
        if self.alpha_modus == 'NONE':
            rgba = rgba.copy()
            rgba[..., 3] = 255
        return rgba

    def abtasten(self, koordinate, interpolation, erweiterung, entassoziieren, aus):
        """`aus[i]` (vec4) = das Bild an `koordinate[i]` (u, v, ·) — `svm_node_tex_image`."""
        # „Alpha ent-assoziieren" gilt nur, wenn der Alpha-Ausgang des Knotens gelesen wird und das Bild kein Daten-/Kanal-gepacktes/ignoriertes ist
        ent = int(bool(entassoziieren) and not self.daten_farbraum and self.alpha_modus not in ('CHANNEL_PACKED', 'NONE'))
        wp.launch(abtasten, dim=len(koordinate), inputs=[self.feld, self.breite, self.hoehe, koordinate, INTERPOLATION[interpolation], ERWEITERUNG[erweiterung],
                                                          int(self.srgb), ent, aus], device=self.geraet)
