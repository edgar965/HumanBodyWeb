# -*- coding: utf-8 -*-
"""Posebestimmung — SAM 3D Body am Bild einer Person und die Gelenke im Netz, für JEDEN Lauf, der eine Pose braucht (11.10.2026).

Aus `Engine2d3dKleiderpose` herausgelöst, als der Import (`Blendimportpose`, Jobseite „Mesh-3D“) denselben Weg brauchte: ein Bild der Person (ein Foto oder ein Rendering des
Körpers) geht durch SAM 3D Body in vier Drehungen (seit 01.11.2026 im Prozess auf der Karte,
`Sam3dbodyTorch.S3dbschaetzer`; bis dahin der Runner `_run_sam3dpose.py` in python12, ein eigener Prozess je
Bild); die Gelenke der gewählten Drehung werden in die Silhouette des Netzes gelegt
(`Engine2d3dKleiderposeabbildung`) und als `landmarken.npz` (`roh` (33, 3), `treffer` (33)) abgelegt — das Format, das `Meshfigurerkennungsschritt` über `auftrag['landmarken_hand']` liest.

Die Klasse kennt weder Auftrag noch Schritt: Sie bekommt einen Ordner (`pose/`), `melden(anteil, text)` und `angehalten()` und gibt Wörterbücher zurück. Ablage und Ergebnisfeld gehören dem Aufrufer.
Der Lauf von SAM ist an Bild, Fassung und Drehungen gebunden (`sam3d.json`, `artefakte-benennen.md`): dieselben Gelenke werden nicht neu gerechnet, wenn nur die Drehung oder die Auswahl wechselt.
"""

import json
import logging
import os
import time

import numpy as np
from django.conf import settings

from .engine2d3dkleiderposeabbildung import Engine2d3dKleiderposeabbildung
from .engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke

logger = logging.getLogger('core')

__all__ = ['Posebestimmung']


class Posebestimmung:
    DREHUNGEN = (0, 90, 180, 270)
    #: Die Fassung der Ablage `sam3d.json` — eine andere gilt nie als aktuell. 2 seit 01.11.2026: gerechnet im
    #: Prozess (`Sam3dbodyTorch`, python14) statt vom Runner in python12.
    FASSUNG = 2
    #: Anteil des Fortschritts, den SAM belegt (der Rest gehört dem Aufrufer: Abbildung, Bilder).
    ANTEIL_SAM = 0.6

    def __init__(self, ordner, bezeichnung, melden, angehalten=lambda: False, abbrechen=RuntimeError):
        """`ordner`: Pfad (`pathlib.Path`) des Ordners `pose/`; `bezeichnung` für das Log; `abbrechen`: die Ausnahme, die bei `angehalten()` fliegt."""
        self.ordner = ordner
        self.bezeichnung = bezeichnung
        self.melden = melden
        self.angehalten = angehalten
        self.abbrechen = abbrechen

    @staticmethod
    def stand(pfad):
        s = os.stat(str(pfad))
        return [s.st_size, s.st_mtime_ns]

    # ------------------------------------------------------------- SAM 3D Body

    def sam(self, png, drehungen=DREHUNGEN, schluessel=None):
        """`(sam3d.json als dict, neu_gerechnet)` — aus der Ablage, wenn Bild, Fassung und Drehungen stimmen,
        sonst rechnet SAM 3D Body im Prozess (`_rechnen`).

        `schluessel` (JSON-fähig) ersetzt den Stempel der Bilddatei, wenn das Bild bei jedem Lauf neu gerendert wird (`Mesh3dansicht.eingaben`): seine Dateizeit ändert sich dann jedes Mal, und SAM rechnete
        jedes Mal neu (40 s am Zauberer, `sam_neu_gerechnet` war in jedem Lauf wahr)."""
        self.ordner.mkdir(parents=True, exist_ok=True)
        datei = self.ordner / 'sam3d.json'
        quelle = self.stand(png) if schluessel is None else schluessel
        try:
            alt = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            alt = None
        if alt and alt.get('fassung') == self.FASSUNG and alt.get('quelle') == quelle and all(str(g) in alt.get('drehungen', {}) for g in drehungen):
            return alt, False
        sam = self._rechnen(png, drehungen)
        sam.update(fassung=self.FASSUNG, quelle=quelle)
        datei.write_text(json.dumps(sam), encoding='utf-8')
        return sam, True

    def _rechnen(self, png, drehungen):
        """SAM 3D Body im Prozess, Ergebnis im Format des Runners (`_run_sam3dpose.py`: `namen`, `bildgroesse`,
        `kasten`, je Drehung `k2` auf 2 und `k3`/`cam_t` auf 5 Stellen, `brennweite`, `bildgroesse_gedreht`; eine
        Drehung ohne Ausgabe trägt `fehler`). Das Foto wie dort: RGBA mit PIL über Grau gelegt, Kasten um Alpha > 127."""
        import torch
        from PIL import Image
        from Sam3dbodyTorch.schaetzer import S3dbschaetzer

        rgba = Image.open(png).convert('RGBA')
        grund = Image.new('RGBA', rgba.size, (S3dbschaetzer.GRAU,) * 3 + (255,))
        rgb = np.array(Image.alpha_composite(grund, rgba).convert('RGB'))
        maske = np.array(rgba)[:, :, 3] > 127
        self._fortschritt(2, 'SAM 3D Body: Modell laden')
        t = time.perf_counter()
        s = S3dbschaetzer(gewichte=settings.SAM3DBODY_CHECKPOINT, mhr=settings.SAM3DBODY_MHR)
        self._fortschritt(40, 'Modell geladen in %.1f s' % (time.perf_counter() - t))
        logger.info('%s: SAM 3D Body im Prozess geladen in %.1f s', self.bezeichnung, time.perf_counter() - t)
        sam = {'namen': list(s.namen), 'bildgroesse': [rgba.size[0], rgba.size[1]], 'kasten': s.kasten(maske),
               'drehungen': {}}
        try:
            for nr, grad in enumerate(drehungen):
                if self.angehalten():
                    raise self.abbrechen()
                self._fortschritt(40 + 55 * nr / len(drehungen), 'Drehung %d°' % grad)
                try:
                    e = s.punkte(rgb, maske, grad=int(grad), freistellen=False)
                except S3dbschaetzer.KeineAusgabe:      # wie beim Runner: steht im Ergebnis, die anderen laufen weiter
                    sam['drehungen'][str(grad)] = {'fehler': 'keine Ausgabe'}
                    continue
                sam['drehungen'][str(grad)] = {
                    'k2': np.round(e['k2'], 2).tolist(), 'k3': np.round(e['k3'], 5).tolist(),
                    'cam_t': np.round(e['cam_t'], 5).tolist(), 'brennweite': e['brennweite'],
                    'bildgroesse_gedreht': e['bildgroesse_gedreht']}
        finally:
            del s
            torch.cuda.empty_cache()
        sam['dauer_s'] = round(time.perf_counter() - t, 1)
        return sam

    def _fortschritt(self, wert, text):
        self.melden(self.ANTEIL_SAM * max(0, min(99, int(wert))) / 100.0, 'Pose: ' + text)

    # --------------------------------------------------------------- Abbildung

    def abbilden(self, netz, png, sam, grad, weglassen=(), masstab=False):
        """Die Gelenke der Drehung `grad` ins Netz: `{abbildung, scan, alpha, roh, treffer, liste, masstab}`; schreibt `landmarken.npz`.
        `netz`: Datei (GLB/OBJ …), die `Meshfigurscan` liest; `png`: das Bild, auf dem das Netz liegt (RGBA, Alpha = Person)."""
        from PIL import Image

        from ..daten.meshto3dpfad import Meshto3dpfad

        e = sam['drehungen'].get(str(grad)) or {}
        if 'k2' not in e:
            raise RuntimeError('SAM 3D Body hat in der Drehung %d° nichts geliefert (%s)' % (grad, e.get('fehler') or 'keine Ausgabe'))
        weglassen = tuple(weglassen)
        with Meshto3dpfad():
            from meshfigur_scan import Meshfigurscan
            scan = Meshfigurscan.laden(netz)
        alpha = np.asarray(Image.open(png).convert('RGBA'))[:, :, 3]
        abbildung = Engine2d3dKleiderposeabbildung(scan, alpha)
        roh, treffer, liste = abbildung.landmarken(np.asarray(e['k2']), sam['namen'], Engine2d3dKleiderposegelenke.ZUORDNUNG, weglassen, k3=e.get('k3'))
        if int((treffer > 0).sum()) < 4:
            raise RuntimeError('Zu wenige Gelenke im Netz (%d) — Drehung oder Auswahl der Gelenke prüfen' % int((treffer > 0).sum()))
        np.savez(self.ordner / 'landmarken.npz', roh=roh, treffer=treffer)
        m = None
        if masstab:
            verwendet = [n for n in Engine2d3dKleiderposegelenke.HAUPT if n not in weglassen]
            m = abbildung.masstab(e['k3'], e['cam_t'], e['brennweite'], sam['namen'], verwendet)
        return {'abbildung': abbildung, 'scan': scan, 'alpha': alpha, 'roh': roh, 'treffer': treffer, 'liste': liste, 'masstab': m}
