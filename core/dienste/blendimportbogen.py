# -*- coding: utf-8 -*-
"""Blendimportbogen — Kontaktbogen der Stücke eines Blend-Imports: je Stück eine Zeile, vier Bilder (Stufe 7 des Konzepts).

    Original      das Stück in der Haltung des Netzes, davor die Käfigpunkte der Figur in derselben Haltung (hellblau)
    Ruhe vorn     das Stück in der Ruhelage der Figur (nach der Rückrechnung), Dreiecke mit verzerrter Kante rot
    Ruhe seitlich dasselbe von der Seite
    Getragen      das GESPEICHERTE Stück, von der Figur in der Haltung des Netzes getragen (Haltungstreue): Farbe grün → rot = Abstand
                  zum Original 0 → 25 mm

Gezeichnet wird auf der CPU mit Pillow (Dreiecke von hinten nach vorn, Flächenlicht) — kein OpenGL, kein Browser: die Prüfung läuft
im Importprozess neben Edgars Arbeit. Das Bild ersetzt keine Sichtprüfung in der Szene, es zeigt, WO die Kennzahlen reißen.
"""

import numpy as np

__all__ = ['Blendimportbogen']


class Blendimportbogen:
    ZELLE = (170, 340)
    RAND = 8
    SPALTEN = ('Original', 'Ruhe vorn', 'Ruhe seitlich', 'Getragen in Haltung')
    GRENZE_MM = 25.0
    LICHT = np.array([0.3, 0.5, 0.8]) / np.linalg.norm([0.3, 0.5, 0.8])

    def __init__(self, kaefig_ruhe, kaefig_posiert):
        self.kaefig = {'posiert': np.asarray(kaefig_posiert, dtype=np.float32), 'ruhe': np.asarray(kaefig_ruhe, dtype=np.float32)}
        self.zeilen = []

    def stueck(self, name, original, ruhe, dreiecke, kante_schlecht, gestellt=None, abstand_mm=None):
        """Ein Stück vormerken (Punkte als float32): `kante_schlecht` (Dreiecke,) bool, `gestellt`/`abstand_mm` aus der Haltungstreue."""
        self.zeilen.append({'name': str(name).strip(), 'original': np.asarray(original, dtype=np.float32),
                            'ruhe': np.asarray(ruhe, dtype=np.float32), 'dreiecke': np.asarray(dreiecke, dtype=np.int64),
                            'schlecht': np.asarray(kante_schlecht, dtype=bool),
                            'gestellt': None if gestellt is None else np.asarray(gestellt, dtype=np.float32),
                            'abstand': None if abstand_mm is None else np.asarray(abstand_mm, dtype=np.float32)})

    @staticmethod
    def schlechte_dreiecke(ruhe, original, dreiecke, von=0.75, bis=1.33):
        """(Dreiecke,) bool — mindestens eine Kante mit Längenverhältnis außerhalb `von`…`bis`."""
        d = np.asarray(dreiecke, dtype=np.int64)
        aus = np.zeros(len(d), dtype=bool)
        for a, b in ((0, 1), (1, 2), (2, 0)):
            v = np.linalg.norm(ruhe[d[:, a]] - ruhe[d[:, b]], axis=1) / np.maximum(np.linalg.norm(original[d[:, a]] - original[d[:, b]], axis=1), 1e-9)
            aus |= (v < von) | (v > bis)
        return aus

    # ------------------------------------------------------------------ Zeichnen

    def _ansicht(self, punkte, seite):
        """(u, v, tiefe): vorn = x nach rechts, y nach oben (näher = größeres z); seitlich = −z nach rechts (näher = größeres x)."""
        p = np.asarray(punkte, dtype=np.float64)
        return (p[:, 0], p[:, 1], p[:, 2]) if not seite else (-p[:, 2], p[:, 1], p[:, 0])

    def _feld(self, bezug, seite):
        u, v, _ = self._ansicht(bezug, seite)
        breite, hoehe = self.ZELLE[0] - 2 * self.RAND, self.ZELLE[1] - 2 * self.RAND
        s = min(breite / max(np.ptp(u), 1e-6), hoehe / max(np.ptp(v), 1e-6))
        return u.min(), v.max(), s, (breite - np.ptp(u) * s) / 2

    def _bild(self, zeichner, ox, oy, feld, punkte, dreiecke, farben, seite, bezug=None):
        u0, v1, s, mitte = feld

        def bildpunkte(p):
            u, v, t = self._ansicht(p, seite)
            return np.column_stack([ox + self.RAND + mitte + (u - u0) * s, oy + self.RAND + (v1 - v) * s]), t

        if bezug is not None:
            xy, _ = bildpunkte(bezug[::5])
            for x, y in xy:
                zeichner.point((x, y), fill=(150, 170, 205))
        xy, tiefe = bildpunkte(punkte)
        d = dreiecke
        p = np.asarray(punkte, dtype=np.float64)
        n = np.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        licht = 0.45 + 0.55 * np.abs(n @ self.LICHT)
        for t in np.argsort(tiefe[d].mean(axis=1)):
            r, g, b = farben[t]
            zeichner.polygon([tuple(xy[i]) for i in d[t]], fill=(int(r * licht[t]), int(g * licht[t]), int(b * licht[t])))

    def schreiben(self, pfad):
        """Das Bild als PNG; den Pfad oder None ohne Stück."""
        from PIL import Image, ImageDraw

        if not self.zeilen:
            return None
        zb, zh = self.ZELLE
        bild = Image.new('RGB', (zb * len(self.SPALTEN), zh * len(self.zeilen)), (24, 26, 40))
        z = ImageDraw.Draw(bild)
        felder = [self._feld(self.kaefig['posiert'], False), self._feld(self.kaefig['ruhe'], False),
                  self._feld(self.kaefig['ruhe'], True), self._feld(self.kaefig['posiert'], False)]
        for reihe, st in enumerate(self.zeilen):
            oy = reihe * zh
            d = st['dreiecke']
            grau = np.full((len(d), 3), 200.0)
            rot = np.where(st['schlecht'][:, None], np.array([235.0, 60.0, 60.0]), grau)
            farben_haltung = grau
            if st['abstand'] is not None:
                f = np.clip(st['abstand'][d].max(axis=1) / self.GRENZE_MM, 0.0, 1.0)
                farben_haltung = np.column_stack([60 + 175 * f, 210 - 150 * f, np.full(len(d), 70.0)])
            ansichten = ((st['original'], grau, False, self.kaefig['posiert']), (st['ruhe'], rot, False, self.kaefig['ruhe']),
                         (st['ruhe'], rot, True, self.kaefig['ruhe']),
                         (st['gestellt'], farben_haltung, False, self.kaefig['posiert']))
            for spalte, (punkte, farben, seite, bezug) in enumerate(ansichten):
                if punkte is None:
                    continue
                self._bild(z, spalte * zb, oy, felder[spalte], punkte, d, farben, seite, bezug)
                z.rectangle([spalte * zb, oy, (spalte + 1) * zb - 1, oy + zh - 1], outline=(60, 64, 90))
            z.text((4, oy + 3), st['name'], fill=(240, 240, 240))
        for spalte, titel in enumerate(self.SPALTEN):
            z.text((spalte * zb + 4, bild.height - 12), titel, fill=(180, 180, 200))
        bild.save(pfad)
        return str(pfad)
