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

import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Blendimportbogen']


class Blendimportbogen:
    ZELLE = (170, 340)
    RAND = 8
    SPALTEN = ('Original', 'Ruhe vorn', 'Ruhe seitlich', 'Getragen in Haltung')
    GRENZE_MM = 25.0
    LICHT = Torchfeld.feld([0.3, 0.5, 0.8], copy=True) / Torchfeld.linalg_norm(Torchfeld.feld([0.3, 0.5, 0.8]))

    def __init__(self, kaefig_ruhe, kaefig_posiert):
        self.kaefig = {'posiert': Torchfeld.feld(kaefig_posiert, dtype=torch.float32), 'ruhe': Torchfeld.feld(kaefig_ruhe, dtype=torch.float32)}
        self.zeilen = []

    def stueck(self, name, original, ruhe, dreiecke, kante_schlecht, gestellt=None, abstand_mm=None):
        """Ein Stück vormerken (Punkte als float32): `kante_schlecht` (Dreiecke,) bool, `gestellt`/`abstand_mm` aus der Haltungstreue."""
        self.zeilen.append({'name': str(name).strip(), 'original': Torchfeld.feld(original, dtype=torch.float32),
                            'ruhe': Torchfeld.feld(ruhe, dtype=torch.float32), 'dreiecke': Torchfeld.feld(dreiecke, dtype=torch.int64),
                            'schlecht': Torchfeld.feld(kante_schlecht, dtype=torch.bool),
                            'gestellt': None if gestellt is None else Torchfeld.feld(gestellt, dtype=torch.float32),
                            'abstand': None if abstand_mm is None else Torchfeld.feld(abstand_mm, dtype=torch.float32)})

    @staticmethod
    def schlechte_dreiecke(ruhe, original, dreiecke, von=0.75, bis=1.33):
        """(Dreiecke,) bool — mindestens eine Kante mit Längenverhältnis außerhalb `von`…`bis`."""
        d = Torchfeld.feld(dreiecke, dtype=torch.int64)
        aus = torch.zeros(len(d), dtype=torch.bool, device='cuda')
        for a, b in ((0, 1), (1, 2), (2, 0)):
            v = Torchfeld.linalg_norm(ruhe[d[:, a]] - ruhe[d[:, b]], dim=1) / Torchfeld.maximum(Torchfeld.linalg_norm(original[d[:, a]] - original[d[:, b]], dim=1), 1e-9)
            aus |= (v < von) | (v > bis)
        return aus

    # ------------------------------------------------------------------ Zeichnen

    def _ansicht(self, punkte, seite):
        """(u, v, tiefe): vorn = x nach rechts, y nach oben (näher = größeres z); seitlich = −z nach rechts (näher = größeres x)."""
        p = Torchfeld.feld(punkte, dtype=torch.float64)
        return (p[:, 0], p[:, 1], p[:, 2]) if not seite else (-p[:, 2], p[:, 1], p[:, 0])

    def _feld(self, bezug, seite):
        u, v, _ = self._ansicht(bezug, seite)
        breite, hoehe = self.ZELLE[0] - 2 * self.RAND, self.ZELLE[1] - 2 * self.RAND
        s = min(breite / max(Torchfeld.ptp(u), 1e-6), hoehe / max(Torchfeld.ptp(v), 1e-6))
        return u.min(), v.max(), s, (breite - Torchfeld.ptp(u) * s) / 2

    def _bild(self, zeichner, ox, oy, feld, punkte, dreiecke, farben, seite, bezug=None):
        u0, v1, s, mitte = feld

        def bildpunkte(p):
            u, v, t = self._ansicht(p, seite)
            return Torchfeld.column_stack([ox + self.RAND + mitte + (u - u0) * s, oy + self.RAND + (v1 - v) * s]), t

        if bezug is not None:
            xy, _ = bildpunkte(bezug[::5])
            for x, y in xy:
                zeichner.point((x, y), fill=(150, 170, 205))
        xy, tiefe = bildpunkte(punkte)
        d = dreiecke
        p = Torchfeld.feld(punkte, dtype=torch.float64)
        n = Torchfeld.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])
        n /= Torchfeld.maximum(Torchfeld.linalg_norm(n, dim=1, keepdim=True), 1e-12)
        licht = 0.45 + 0.55 * Torchfeld.abs(n @ self.LICHT)
        for t in Torchfeld.liste(torch.argsort(tiefe[d].mean(axis=1), stable=True)):
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
            grau = Torchfeld.full((len(d), 3), 200.0)
            rot = torch.where(st['schlecht'][:, None], Torchfeld.feld([235.0, 60.0, 60.0], copy=True), grau)
            farben_haltung = grau
            if st['abstand'] is not None:
                f = Torchfeld.clip(Torchfeld.amax(st['abstand'][d], dim=1) / self.GRENZE_MM, 0.0, 1.0)
                farben_haltung = Torchfeld.column_stack([60 + 175 * f, 210 - 150 * f, Torchfeld.full(len(d), 70.0)])
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
