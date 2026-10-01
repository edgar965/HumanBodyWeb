# -*- coding: utf-8 -*-
"""Gesichtsvorrat — die Gesichtsmaße des Kopf-Renders je Kopfstand nur einmal messen (01.10.2026).

Der Kopf-Render (`Genesishaarrender.bild_kopf`, Mitsuba, Saat 0) ist für dieselbe Szene bitgleich, aber jedes Teil der
Szene lenkt Lichtwege um: ein anderer Shirtsaum, eine Haarlocke am Rücken → andere Pixel im Gesicht → die Landmarken
springen um 1–2 % → der Gesichtsterm der `Gesamtnote` um ±0,009, mehr als `Rundenauswahl.TOLERANZ` (0,002).
Gemessen am `_test_fixe` (01.10.2026): Runde 41 → 0,0919, Runde 43 → 0,1007 bei unverändertem Kopf; die Rundenauswahl
verwarf Funktionen am Rauschen statt an ihrer Wirkung.

Selbst DIESELBE Szene misst nicht gleich: Runde 49 und die Leerrunde 55 (gleiches Modell, gleiche Fotonote) gaben Nase
1,0048 / 1,0089, Kinn 1,2143 / 1,2177. Und jede Haar-Operation änderte den Render: Clump (im Bild unsichtbar, Foto und
IoU bitgleich) hob die Note um 0,013. Ein Render nur aus dem Körper half nicht: am kahlen Kopf setzt der Detektor die
Stirn anders als auf dem Foto mit Haar (Augenhöhe 0,944 → 0,907, Kinn 1,22 → 1,28, Note +0,036). Und mehr Abtastungen
auch nicht: über vier Saaten schwankt der Term bei 512 noch um 0,0125 (`ProjektTemp/_wegwerf/ortsmorph/kopfrauschen.py`).

Deshalb: gerendert wird mit allen Teilen (wie das Foto), der Schlüssel aber kommt NUR aus dem Körper
(`Gesichtsmasse.befund` gibt nur ihn her) — alle Punkte ab `KOPF_M` unter dem Scheitel, gerundet auf `RASTER_M`, mit
Farbe, dazu Ansicht, Rendergröße und Fassung der Landmarken. Haar und Kleidung stellen keinen Kopfregler; eine
Haar-Operation misst das Gesicht nicht neu. Ändert sich der Kopf (Kopf- oder Körperregler), misst `Gesichtsmasse` über
vier Saaten (Median). Ablage: `gesicht_vorrat.json` im
Arbeitsordner des Auftrags, höchstens `GRENZE` Einträge (die ältesten fallen heraus).
"""

import hashlib
import json
import logging

import numpy as np

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Gesichtsvorrat']


class Gesichtsvorrat:
    DATEI = 'gesicht_vorrat.json'
    #: Bis so weit unter dem Scheitel zählt ein Punkt zum Kopfstand (Stirn bis Kinn). Gemessen an `koerper_huelle`
    #: (Rumpf 0,55–0,72): sie bewegt Körperpunkte 0,25–0,30 m unter dem Scheitel bis 15,6 mm (Schultern), 0,20–0,25 m
    #: bis 0,68 mm, darüber nichts — mit 0,30 maß jede Rumpfänderung das Gesicht neu (`kopfpunkte.py`, 01.10.2026).
    #: Die Daz-Gruppe „Head" reicht bis 1,37 m (Hals) und taugt deshalb nicht als Grenze.
    KOPF_M = 0.20
    #: Punkte auf 0,1 mm gerundet — die Häutung rechnet für denselben Stand bitgleich, das Raster fängt nur Rundung ab.
    RASTER_M = 1e-4
    GRENZE = 200

    def __init__(self, ablage):
        self.pfad = ablage.arbeit(self.DATEI)

    @classmethod
    def schluessel(cls, teile, winkel, groesse, fassung):
        koerper = next((t for t in teile if t.get('art') == 'koerper'), teile[0] if teile else None)
        if koerper is None:
            return None
        k = np.asarray(koerper['punkte'], dtype=np.float64)
        scheitel = float(k[:, 1].max())
        # Relativ zum Schwerpunkt des Kopfes: eine Verschiebung der ganzen Figur (Boden, Höhe) misst nicht neu.
        mitte = k[k[:, 1] >= scheitel - cls.KOPF_M].mean(axis=0)
        h = hashlib.sha1(('%r|%r|%r' % (round(float(winkel), 3), tuple(groesse), fassung)).encode('utf-8'))
        for t in teile:
            p = np.asarray(t['punkte'], dtype=np.float64)
            p = p[p[:, 1] >= scheitel - cls.KOPF_M] - mitte
            if not len(p):
                continue
            h.update(str(t.get('sorte') or t.get('art')).encode('utf-8'))
            h.update(repr(t.get('farbe')).encode('utf-8'))
            h.update(np.round(p / cls.RASTER_M).astype(np.int64).tobytes())
        return h.hexdigest()

    def _lesen(self):
        if not self.pfad.is_file():
            return {}
        try:
            with open(self.pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except (OSError, ValueError):
            return {}

    def holen(self, schluessel):
        """Die Maße des Renders zu diesem Kopfstand oder None."""
        if not schluessel:
            return None
        return (self._lesen().get(schluessel) or {}).get('render')

    def ablegen(self, schluessel, render):
        if not schluessel or not render:
            return
        alt = self._lesen()
        alt.pop(schluessel, None)
        alt[schluessel] = {'render': render}
        while len(alt) > self.GRENZE:
            alt.pop(next(iter(alt)))
        try:
            self.pfad.parent.mkdir(parents=True, exist_ok=True)
            AtomarSchreiber.json_schreiben(self.pfad, alt)
        except OSError as fehler:
            logger.warning('Gesichtsvorrat nicht geschrieben (%s)', fehler)
