# -*- coding: utf-8 -*-
"""Engine2d3dKleiderposebilder — die Kontrollbilder des Schritts „pose" (11.10.2026): was SAM 3D Body am Foto gefunden hat und wo die Gelenke im Netz liegen.

`skelett`: das vorbereitete Foto (Person auf Grau, wie SAM es bekommt) um `grad` gedreht, mit den 21 übernommenen Gelenken und den Linien dazwischen — eines je Drehung, die Seite zeigt alle vier.
`netz`: Vorder- und Seitenansicht des Netzes als Umriss (abgetastete Punkte, Tiefe `z` nach rechts) mit den Landmarken — Tiefe und Lage im Körper sind darin zu sehen (grün = im Netz, orange = auf das Netz gezogen).
Nur Pillow, NumPy, SciPy: kein Renderer, kein Browser (`nur-echter-chrome.md`).
"""

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_closing

from .engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke

__all__ = ['Engine2d3dKleiderposebilder']


class Engine2d3dKleiderposebilder:
    #: Längere Seite eines Kontrollbilds in Pixeln.
    KANTE = 640
    FARBEN = {'innen': (70, 220, 100), 'ausserhalb': (255, 170, 0), 'weggelassen': (150, 150, 150)}
    LINIE = (60, 150, 255)
    GRAU = (128, 128, 128)

    @staticmethod
    def foto(png):
        """Das vorbereitete RGBA-Foto auf Grau — dasselbe Bild, das SAM 3D Body bekommt."""
        rgba = Image.open(png).convert('RGBA')
        return Image.alpha_composite(Image.new('RGBA', rgba.size, Engine2d3dKleiderposebilder.GRAU + (255,)), rgba).convert('RGB')

    @staticmethod
    def _drehen(punkte, grad, b, h):
        """Wie `Sam3dposerunner.drehen` (PIL `rotate(grad, expand=True)`): Pixel des ungedrehten Bildes → Pixel der gedrehten Aufnahme."""
        u, v = punkte[:, 0], punkte[:, 1]
        if grad == 0:
            return np.stack([u, v], axis=1)
        if grad == 90:
            return np.stack([v, b - u], axis=1)
        if grad == 180:
            return np.stack([b - u, h - v], axis=1)
        return np.stack([h - v, u], axis=1)

    def skelett(self, rgb, k2, namen, grad, weglassen=(), unter=''):
        """Das Foto um `grad` gedreht mit den Gelenken (`k2` (70, 2) in Pixeln des UNgedrehten Fotos)."""
        b, h = rgb.size
        bild = rgb.rotate(grad, expand=True)
        k = self.KANTE / float(max(bild.size))
        bild = bild.resize((max(1, round(bild.size[0] * k)), max(1, round(bild.size[1] * k))), Image.LANCZOS)
        p = self._drehen(np.asarray(k2, dtype=np.float64), grad, b, h) * k
        index = Engine2d3dKleiderposegelenke.index(namen)
        gelenke = set(Engine2d3dKleiderposegelenke.ZUORDNUNG.values())
        zeichner = ImageDraw.Draw(bild)
        for a, c in Engine2d3dKleiderposegelenke.KNOCHEN:
            if a in gelenke and c in gelenke and a not in weglassen and c not in weglassen:
                zeichner.line([tuple(p[index[a]]), tuple(p[index[c]])], fill=self.LINIE, width=3)
        for name in gelenke:
            x, y = p[index[name]]
            farbe = self.FARBEN['weggelassen' if name in weglassen else 'innen']
            zeichner.ellipse([x - 5, y - 5, x + 5, y + 5], outline=farbe, width=3)
            if name in weglassen:
                zeichner.line([(x - 5, y - 5), (x + 5, y + 5)], fill=farbe, width=2)
                zeichner.line([(x - 5, y + 5), (x + 5, y - 5)], fill=farbe, width=2)
        zeichner.rectangle([0, 0, 190, 20], fill=(0, 0, 0))
        zeichner.text((6, 4), 'Drehung %d° %s' % (grad, unter), fill=(255, 255, 255))
        return bild

    def _umriss(self, u, v, breite, hoehe, rand=3):
        """Maske (hoehe × breite) aus Punkten in Bildkoordinaten, Lücken geschlossen."""
        m = np.zeros((hoehe, breite), bool)
        x, y = np.round(u).astype(int), np.round(v).astype(int)
        ok = (x >= 0) & (x < breite) & (y >= 0) & (y < hoehe)
        m[y[ok], x[ok]] = True
        return binary_closing(m, iterations=rand)

    def netz(self, abbildung, liste):
        """Zwei Ansichten des Netzes nebeneinander: von vorn (wie das Foto) und von der Seite (Tiefe `z` waagerecht, Bildhöhe wie vorn), mit den Landmarken aus `liste` (`netz`, `stand`)."""
        punkte = abbildung._baum_und_punkte()[1]
        x0, y0, x1, y1 = abbildung.kasten
        rand = 0.06 * max(x1 - x0, y1 - y0)
        ausschnitt = (x0 - rand, y0 - rand, x1 + rand, y1 + rand)
        k = self.KANTE / max(ausschnitt[2] - ausschnitt[0], ausschnitt[3] - ausschnitt[1])
        breite, hoehe = round((ausschnitt[2] - ausschnitt[0]) * k), round((ausschnitt[3] - ausschnitt[1]) * k)
        foto = abbildung.auf_foto(punkte)
        vorn = self._umriss((foto[:, 0] - ausschnitt[0]) * k, (foto[:, 1] - ausschnitt[1]) * k, breite, hoehe)
        mass = float(np.sqrt(abbildung.sx * abbildung.sy))                   # Pixel je Netzeinheit, für die Tiefe wie in der Bildebene
        mitte_z = 0.5 * (float(punkte[:, 2].min()) + float(punkte[:, 2].max()))
        seite_u = ((punkte[:, 2] - mitte_z) * mass + 0.5 * (ausschnitt[2] - ausschnitt[0])) * k
        seite = self._umriss(seite_u, (foto[:, 1] - ausschnitt[1]) * k, breite, hoehe)
        blatt = Image.new('RGB', (2 * breite + 12, hoehe), (24, 24, 30))
        for nr, maske in enumerate((vorn, seite)):
            flaeche = Image.fromarray(np.where(maske, 90, 30).astype(np.uint8)).convert('RGB')
            blatt.paste(flaeche, (nr * (breite + 12), 0))
        zeichner = ImageDraw.Draw(blatt)
        zeichner.text((6, 4), 'Netz von vorn', fill=(255, 255, 255))
        zeichner.text((breite + 18, 4), 'Netz von der Seite (Tiefe z nach rechts)', fill=(255, 255, 255))
        for e in liste:
            if 'netz' not in e:
                continue
            px, py, z = e['netz']
            f = abbildung.auf_foto(np.array([[px, py, z]]))[0]
            farbe = self.FARBEN[e['stand']]
            vx, vy = (f[0] - ausschnitt[0]) * k, (f[1] - ausschnitt[1]) * k
            sx = ((z - mitte_z) * mass + 0.5 * (ausschnitt[2] - ausschnitt[0])) * k + breite + 12
            for mx in (vx, sx):
                zeichner.ellipse([mx - 5, vy - 5, mx + 5, vy + 5], outline=farbe, width=3)
        return blatt
