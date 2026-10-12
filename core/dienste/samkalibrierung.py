# -*- coding: utf-8 -*-
"""Samkalibrierung — Genesis selbst durch SAM 3D Body schicken (12.10.2026), damit „Mesh to 3D" die Gelenke aus der Pose (`landmarken_hand`) mit dem Versatz liest, den SAM auf Genesis zeigt.

Derselbe Weg wie beim Netz des Imports: die Grundfigur als GLB (`G9figurglb`), von vorn gerendert (`Mesh3dansicht`), SAM 3D Body (`Posebestimmung`, python12), die Gelenke ins Netz gelegt (Tiefe = Mitte der Dicke,
`Engine2d3dKleiderposeabbildung.TIEFE`). Der Versatz je Gelenk ist SAM-Punkt − Daz-Gelenk des Anker-Knochens (`G9netzlandmarken.ANKER`); er kommt als `G9netzlandmarkensam` in die Ablage.

Warum es das braucht (gemessen 12.10.2026, Auftrag „Edgar"): die Tabelle für MediaPipe liegt bis 4,2 cm neben den SAM-Punkten (Hüfte), und mit dem Median als Tiefe lagen die SAM-Hüften 8–12 cm daneben
(masculine +11,8 cm, feminine −7,7 cm am selben Gelenk — Vorder- oder Rückseite des Rumpfs, je nachdem welche Schicht mehr Punkte hatte). Mit der Mitte der Dicke: ≤ 3,5 cm Versatz, Unterschied zwischen
den Grundfiguren ≤ 1,5 cm.

Läuft einmal je Rechner (rund 2,5 Minuten, GPU), `manage.py sam_kalibrieren`; ohne Tabelle rechnet der Runner mit der von MediaPipe weiter und sagt es im Ergebnis (`gelenk_versatz`).
"""

import logging

import numpy as np
from Genesis9.figurglb import G9figurglb
from Genesis9.formung import G9formung
from Genesis9.netzlandmarken import G9netzlandmarken
from Genesis9.netzlandmarkensam import G9netzlandmarkensam
from Genesis9.pfade import G9pfade

from .mesh3dansicht import Mesh3dansicht
from .meshfigurregler import Meshfigurregler
from .posebestimmung import Posebestimmung

logger = logging.getLogger('core')

__all__ = ['Samkalibrierung']


class Samkalibrierung:
    ORDNER = 'sam_kalibrierung'

    def __init__(self, melden=lambda anteil, text: None):
        self.melden = melden

    def ausfuehren(self):
        """Rechnet beide Grundfiguren, legt `G9netzlandmarkensam` ab und gibt `(Tabelle, Bericht)` zurück."""
        versatz, bericht = {}, {}
        for i, basis in enumerate(G9netzlandmarkensam.BASEN):
            ordner = G9pfade.ablage() / self.ORDNER / basis
            ordner.mkdir(parents=True, exist_ok=True)
            versatz[basis], bericht[basis] = self._figur(basis, ordner, lambda a, t, i=i: self.melden((i + a) / len(G9netzlandmarkensam.BASEN), t))
        tabelle = G9netzlandmarkensam.bauen(versatz)
        bericht['pfad'] = str(tabelle.speichern())
        bericht['steckbrief'] = tabelle.steckbrief()
        return tabelle, bericht

    def _figur(self, basis, ordner, melden):
        grund = Meshfigurregler.GRUNDFIGUREN[basis]
        glb = ordner / 'genesis.glb'
        G9figurglb(grund).schreiben(glb)
        ansicht = Mesh3dansicht.vorne(glb, ordner / 'ansicht_vorne.png')
        best = Posebestimmung(ordner, 'SAM-Kalibrierung ' + basis, melden)
        sam, neu = best.sam(ansicht, schluessel=Mesh3dansicht.eingaben(glb))
        e = best.abbilden(glb, ansicht, sam, 0)
        roh = np.asarray(e['roh'], float)
        gelenke = {k['name']: np.asarray(k['kopf'], float) for k in G9formung(grund).skelett().gelenkknochen()}
        versatz = np.full((len(G9netzlandmarken.ANKER), 3), np.nan)
        for i, (nummer, knochen) in enumerate(G9netzlandmarken.ANKER.items()):
            if np.isfinite(roh[nummer]).all():
                versatz[i] = roh[nummer] - gelenke[knochen]
            else:
                logger.warning('SAM-Kalibrierung %s: Gelenk %d (%s) nicht gefunden', basis, nummer, knochen)
        return versatz, {'sam_neu_gerechnet': neu, 'gelenke_gesetzt': int((e['treffer'] > 0).sum()), 'iou': round(float(e['abbildung'].iou), 3)}
