# -*- coding: utf-8 -*-
"""Ai2d3dzeile2 — Zeile 2 der Jobseite (gerechnete Figur → Genesis-Modell, Feld 3) für die Tests
(02.11.2026): die Renderings DER SEITE aus der Kamera jedes Fotos (`<Job>/abnahme/seite_<nr>.png`, RGBA, im
Chrome `window.__ai2d3d.seitenbilder()`, `Ai2d3dseitenbild`) und die Kleidungsstücke der Figur
(`<Job>/figur/kleider_<geschlecht>/k/<id>/anzeige/netz.npz`, Ruhelage). Nur lesen, nur numpy/PIL.

Ein Rendering, das älter ist als die Figur, zeigt einen anderen Stand: `veraltet()` nennt es, der Test
misst es dann nicht (nie das Bild eines anderen Laufs).

    z = Ai2d3dzeile2(objects_root, 'EdgarTrip')
    rgb, figur = z.bild('1.jpg', (h, w))      # auf (h, w) umgetastet; None ohne Rendering
    punkte, dreiecke = z.stueck('oberteil')   # None ohne Stück
"""
import json
from pathlib import Path

import numpy as np

__all__ = ['Ai2d3dzeile2']


class Ai2d3dzeile2:
    def __init__(self, objects_root, job):
        self.ordner = Path(objects_root) / 'ai2d3d' / job
        datei = self.ordner / 'abnahme' / 'kameras.json'
        self.kameras = json.loads(datei.read_text(encoding='utf-8'))['kameras'] if datei.is_file() else {}
        self.kleider = next(iter(sorted((self.ordner / 'figur').glob('kleider_*'))), None)

    def seitenbild(self, datei):
        k = next((k for k in self.kameras.values() if k['datei'] == datei), None)
        return None if k is None else self.ordner / 'abnahme' / ('seite_%d.png' % k['nr'])

    def figur_zeit(self):
        """Jüngste Datei der Figur (Netz, Haut, Kleider; ohne Sicherungen `_*`) — ein Rendering davor zeigt
        einen anderen Stand."""
        wurzel = self.ordner / 'figur'
        teile = [p for p in wurzel.glob('*_*/**/*')
                 if p.is_file() and not any(t.startswith('_') for t in p.relative_to(wurzel).parts)]
        return max((p.stat().st_mtime for p in teile), default=0.0)

    def veraltet(self):
        """[Dateiname] der Renderings, die fehlen oder älter als die Figur sind."""
        stand, aus = self.figur_zeit(), []
        for k in self.kameras.values():
            p = self.seitenbild(k['datei'])
            if not p.is_file() or p.stat().st_mtime < stand:
                aus.append(k['datei'])
        return aus

    def bild(self, datei, form):
        from PIL import Image
        pfad = self.seitenbild(datei)
        if pfad is None or not pfad.is_file():
            return None
        h, w = form
        a = np.asarray(Image.open(pfad).convert('RGBA').resize((w, h), Image.BILINEAR)).astype(np.float64)
        return a[..., :3], a[..., 3] >= 128

    def stueck(self, art):
        """(Punkte (N, 3) m, Dreiecke (T, 3)) des Kleidungsstücks dieser Art (`eintrag.json` `art`, z. B.
        'oberteil', 'hose'), oder None."""
        if self.kleider is None:
            return None
        for e in sorted((self.kleider / 'k').glob('*/eintrag.json')):
            if json.loads(e.read_text(encoding='utf-8')).get('art') == art:
                with np.load(e.parent / 'anzeige' / 'netz.npz') as z:
                    return z['ruhe'].astype(np.float64), z['dreiecke'].astype(np.int64)
        return None
