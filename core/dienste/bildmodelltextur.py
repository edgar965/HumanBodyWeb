# -*- coding: utf-8 -*-
"""Bildmodelltextur — welche Bilder die Haut liefern und welcher Ton daraus wird.

Edgar (19.09.2026): „Überlege auch ob eine Textur möglich wäre … welches Bild
für die Textur genutzt werden könnte und welches nicht, und wie sich dann
interaktiv die Textur / das Modell verändert, wenn ich eine Textur anwähle /
abwähle."

Stufe 1: Die Sichtung misst je Ausschnitt Hautton, Hautanteil und
Maskenhöhe (`hauttonprobe.py`, YOLO11-Seg + YCrCb-Hautschwelle) und sagt,
ob das Bild taugt (Hauptbild, Haut ≥ 25 % der Maske, Maske ≥ 400 px).
Die Kachel zeigt Farbfeld und Häkchen; `textur_an` ist die Wahl des
Nutzers (Vorgabe = tauglich). `hautton(bilder)` mischt die gewählten
Bilder nach Hautpixeln (Anteil × Maskenhöhe) — der Zustand trägt das
Ergebnis, die 3D-Ansicht tönt die Daz-Haut damit (Faktor gegen den
mittleren Ton der Albedo, `ansicht3d.js`). Beleg an Damira: Vorderansicht
(187, 132, 103), Kopfbild (176, 129, 102), posiertes Bild im Gegenlicht
(121, 93, 74) — darum die Wahl je Bild.

Stufe 2 (Vorschlag): Farbe je Käfigpunkt über die SMPL-X-Projektion des
jeweiligen Bildes (Pose und Kamera sind exakt, `netzabweichung_mm` 0,0)
und die Netzpaarung, gewichtet nach Blickwinkel (Normale · Kamera) und
Auflösung (px je cm), sichtbar nur, was die Personenmaske deckt und
nichts davor liegt (Tiefenprobe); dann je UDIM-Kachel als Textur gebacken
und über die Daz-Haut gelegt. Aufwand: ein Runner (python10), ein
Backschritt (python14), die Ansicht (`vertexColors` sofort, Textur nach).
"""

import numpy as np

__all__ = ['Bildmodelltextur']


class Bildmodelltextur:
    @staticmethod
    def gewaehlt(bild):
        """Zählt das Bild zur Textur? Nutzung (nicht „nur Form"/„aus"), dann die
        Nutzerwahl, sonst die Tauglichkeit — ein Nebenbild mit Körperteil
        (`Bildmodellbildtypen`, 19.09.2026) gilt mit Hautton als gewählt."""
        from .bildmodellbildtypen import Bildmodellbildtypen

        t = bild.get('textur') or {}
        if not t.get('hautton') or not Bildmodellbildtypen.fuer_textur(bild):
            return False
        if 'textur_an' in bild:
            return bool(bild['textur_an'])
        return bool(t.get('tauglich')) or bool(Bildmodellbildtypen.textur_teile(bild))

    @classmethod
    def hautton(cls, bilder):
        """`{hautton: [r, g, b], bilder: n, tauglich: m}` — gemischt nach Hautpixeln."""
        summe = np.zeros(3)
        gewicht = 0.0
        n = 0
        tauglich = 0
        for b in bilder:
            t = b.get('textur') or {}
            if t.get('tauglich'):
                tauglich += 1
            if not cls.gewaehlt(b):
                continue
            w = float(t.get('anteil') or 0) * float(t.get('maske_px') or 0)
            if w <= 0:
                continue
            summe += np.asarray(t['hautton'], dtype=float) * w
            gewicht += w
            n += 1
        if gewicht <= 0:
            return {'hautton': None, 'bilder': 0, 'tauglich': tauglich}
        return {'hautton': [int(round(v)) for v in summe / gewicht], 'bilder': n, 'tauglich': tauglich}
