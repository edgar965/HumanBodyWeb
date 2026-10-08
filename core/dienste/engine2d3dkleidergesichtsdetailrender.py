# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtsdetailrender — die Bilderreihen „Augen", „Mund", „Nase" des Reiters „Gesicht" (07.10.2026).

Edgar: „augenform auch nicht, mach im Tab Gesicht auch eine Bilderreihe für augen, Mund, Nase" (nach „mund ist halb offen beim Modell (im Mesh nicht), mundproportionen und nasenproportionen
stimmen nicht"). Je Bereich ein PNG mit drei Ansichten (vorn, 45°, Seite), je Ansicht drei Bilder: das Netz (Kopfnetz, sonst Körpernetz — `Engine2d3dKleiderGesichtslage`), das Modell (`stand_*.glb`)
und die Überlagerung der Landmarken-Linien (rot = Netz, blau = Modell) auf dem Modell. Beide Seiten stehen in der Ruhehaltung des Modells, aus derselben Kamera (orthografisch, Bildmitte = Mitte der
Landmarken des Bereichs), mit demselben Licht — nur so zeigt ein Unterschied im Bild einen Unterschied der Form.

Die Modell-Landmarken sind die eigenen der Figur (Dreieck + Anteile, `Engine2d3dKleiderGesichtslage._modell_gesicht`), nicht die nächsten Flächenpunkte der Netz-Landmarken.

GL-Rendern gehört in einen eigenen Prozess (`manage.py engine2d3dkleider_gesichtsdetail`), nicht in einen Anfrage-Faden des Servers (`Engine2d3dKleiderGesichtsdetail`).
"""

import json

import numpy as np
import pyrender
import trimesh
from Genesis9.pyrenderreihenfolge import G9pyrenderreihenfolge
from PIL import Image, ImageDraw, ImageFont

from .engine2d3dkleidergesichtsdetail import Engine2d3dKleiderGesichtsdetail

__all__ = ['Engine2d3dKleiderGesichtsdetailrender']

# Ringe und Linien der MediaPipe-Landmarken (478 Punkte; Indizes wie in `Engine2d3dKleiderGesichtsvergleich.LINIEN`). Ring = geschlossen, Linie = offen.
RECHTES_AUGE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LINKES_AUGE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RECHTE_BRAUE = [46, 53, 52, 65, 55, 107, 66, 105, 63, 70]
LINKE_BRAUE = [276, 283, 282, 295, 285, 336, 296, 334, 293, 300]
LIPPEN_AUSSEN = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
LIPPEN_INNEN = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]


class Engine2d3dKleiderGesichtsdetailrender:
    #: Bereich → Titel, Fensterhöhe (m), Ringe, Linien, Einzelpunkte.
    REGIONEN = {
        'augen': {'titel': 'Augen und Brauen', 'fenster': 0.17, 'ringe': [RECHTES_AUGE, LINKES_AUGE, RECHTE_BRAUE, LINKE_BRAUE], 'linien': [], 'punkte': [468, 473]},
        'mund': {'titel': 'Mund', 'fenster': 0.11, 'ringe': [LIPPEN_AUSSEN, LIPPEN_INNEN], 'linien': [], 'punkte': []},
        'nase': {'titel': 'Nase', 'fenster': 0.11, 'ringe': [], 'punkte': [1, 4],
                 'linien': [[168, 6, 197, 195, 5, 4], [129, 98, 97, 2, 326, 327, 358], [49, 48, 64], [279, 278, 294]]},
    }
    #: (Azimut der Kamera in Grad, Beschriftung). −90 = von rechts gesehen, das Gesicht schaut nach rechts im Bild (wie das Seitenfoto).
    ANSICHTEN = ((0, 'vorn'), (-45, '45° von rechts'), (-90, 'Seite von rechts'))
    KANTE = 400
    GRUND = (24, 24, 32)
    ROT, BLAU = (255, 60, 60), (70, 140, 255)

    # ----------------------------------------------------------------------------- Aufruf

    @classmethod
    def erzeugen(cls, job, ablage, fassung):
        """Schreibt `ergebnis/gesicht_<bereich>_<fassung>.png` für alle Bereiche; gibt die Dateinamen zurück."""
        from .engine2d3dkleidergesichtslage import Engine2d3dKleiderGesichtslage

        lage = Engine2d3dKleiderGesichtslage.berechnen(job, ablage)
        if lage['netz_pfad'] is None or lage['modell_gesicht'] is None:
            raise ValueError('Kein Netz oder keine Landmarken der Figur (`arbeit/genesis_ende.npz`) — erst nach dem Schritt „Körper“.')
        lage['gesicht'] = Engine2d3dKleiderGesichtslage.auf_flaeche(lage)       # die Netz-Landmarken auf der Fläche, wie die Anpassung sie nimmt
        stand = ablage.ergebnis('stand.json')
        if not stand.is_file():
            raise ValueError('Noch kein Modell des Stands (`ergebnis/stand.json`).')
        modell_pfad = ablage.ergebnis(json.loads(stand.read_text(encoding='utf-8')).get('datei') or '')
        if not modell_pfad.is_file():
            raise ValueError('Die Datei des Stands fehlt: %s' % modell_pfad.name)
        netz = cls._szene(lage['netz_pfad'], lage['netz_matrix'])
        modell = cls._szene(modell_pfad)
        namen = []
        G9pyrenderreihenfolge.anwenden()          # Wimpern und Brauen nach der Haut zeichnen (sonst wechselt das Bild von Aufruf zu Aufruf, 08.10.2026)
        werk = pyrender.OffscreenRenderer(cls.KANTE, cls.KANTE)
        try:
            for bereich in cls.REGIONEN:
                bild = cls._bereich(bereich, netz, modell, lage, werk, job.name)
                name = Engine2d3dKleiderGesichtsdetail.dateiname(bereich, fassung)
                bild.save(str(ablage.ergebnis(name)))
                namen.append(name)
        finally:
            werk.delete()
        return namen

    # ----------------------------------------------------------------------------- Bild je Bereich

    @classmethod
    def _bereich(cls, bereich, netz, modell, lage, werk, auftragsname):
        r = cls.REGIONEN[bereich]
        indizes = sorted({i for ring in r['ringe'] for i in ring} | {i for linie in r['linien'] for i in linie} | set(r['punkte']))
        gueltig = [i for i in indizes if np.isfinite(lage['gesicht'][i]).all() and np.isfinite(lage['modell_gesicht'][i]).all()]
        mitte = np.nanmean(lage['gesicht'][gueltig], axis=0)
        kopfzeile = 30
        tafel = Image.new('RGB', (3 * cls.KANTE, kopfzeile + len(cls.ANSICHTEN) * cls.KANTE), cls.GRUND)
        zeichner = ImageDraw.Draw(tafel)
        schrift = cls._schrift(15)
        zeichner.text((8, 7), '%s — %s: Mesh = %s (links) · Modell (Mitte) · Überlagerung: rot = Mesh-Landmarken, blau = Modell-Landmarken' % (
            auftragsname, r['titel'], lage['netz_art']), fill=(230, 230, 235), font=schrift)
        for zeile, (azimut, text) in enumerate(cls.ANSICHTEN):
            kamera = cls._kamera(azimut, mitte, r['fenster'])
            bilder = [cls._rendern(werk, szene, kamera) for szene in (netz, modell)]
            ueber = Image.blend(Image.new('RGB', bilder[1].size, cls.GRUND), bilder[1], 0.6)
            lauf = ImageDraw.Draw(ueber)
            for quelle, farbe in ((lage['gesicht'], cls.ROT), (lage['modell_gesicht'], cls.BLAU)):
                cls._zeichnen(lauf, quelle, r, kamera, farbe)
            for spalte, bild in enumerate(bilder + [ueber]):
                tafel.paste(bild, (spalte * cls.KANTE, kopfzeile + zeile * cls.KANTE))
            zeichner.text((8, kopfzeile + zeile * cls.KANTE + 6), text, fill=(255, 255, 255), font=schrift)
        return tafel

    @staticmethod
    def _schrift(groesse):
        """Eine Schrift mit Umlauten (die eingebaute von Pillow kennt keine) — Arial/DejaVu, sonst die eingebaute."""
        for name in ('arial.ttf', 'DejaVuSans.ttf'):
            try:
                return ImageFont.truetype(name, groesse)
            except OSError:
                continue
        return ImageFont.load_default()

    @classmethod
    def _zeichnen(cls, zeichner, punkte, region, kamera, farbe):
        def px(i):
            return cls._projizieren(punkte[i], kamera)

        for ring in region['ringe']:
            xy = [px(i) for i in ring if np.isfinite(punkte[i]).all()]
            if len(xy) > 2:
                zeichner.line(xy + [xy[0]], fill=farbe, width=2)
        for linie in region['linien']:
            xy = [px(i) for i in linie if np.isfinite(punkte[i]).all()]
            if len(xy) > 1:
                zeichner.line(xy, fill=farbe, width=2)
        for i in region['punkte']:
            if np.isfinite(punkte[i]).all():
                x, y = px(i)
                zeichner.ellipse([x - 3, y - 3, x + 3, y + 3], outline=farbe, width=2)

    # ----------------------------------------------------------------------------- Kamera und Rendern

    @staticmethod
    def _szene(pfad, matrix=None):
        geladen = trimesh.load(str(pfad), process=False)
        szene = geladen if isinstance(geladen, trimesh.Scene) else trimesh.Scene(geladen)
        if matrix is not None:
            szene.apply_transform(np.asarray(matrix, dtype=float))
        return szene

    @classmethod
    def _kamera(cls, azimut, mitte, fenster):
        a = np.radians(azimut)
        drehung = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
        lage = np.eye(4)
        lage[:3, :3] = drehung
        lage[:3, 3] = np.asarray(mitte) + drehung @ np.array([0.0, 0.0, 3.0])
        return {'lage': lage, 'fenster': float(fenster)}

    @classmethod
    def _projizieren(cls, p, kamera):
        """Weltpunkt → Pixel (orthografisch, `fenster` Meter über `KANTE` Pixel)."""
        lage = kamera['lage']
        kam = lage[:3, :3].T @ (np.asarray(p, dtype=float) - lage[:3, 3])
        halb = kamera['fenster'] / 2.0
        return (kam[0] / halb + 1.0) / 2.0 * cls.KANTE, (1.0 - (kam[1] / halb + 1.0) / 2.0) * cls.KANTE

    @classmethod
    def _rendern(cls, werk, szene_tm, kamera):
        szene = pyrender.Scene.from_trimesh_scene(szene_tm, bg_color=(cls.GRUND[0] / 255, cls.GRUND[1] / 255, cls.GRUND[2] / 255, 1.0), ambient_light=(0.55, 0.55, 0.55))
        halb = kamera['fenster'] / 2.0
        szene.add(pyrender.OrthographicCamera(xmag=halb, ymag=halb, znear=0.1, zfar=10.0), pose=kamera['lage'])
        szene.add(pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.4), pose=kamera['lage'])
        farbe, _ = werk.render(szene)
        return Image.fromarray(farbe)
