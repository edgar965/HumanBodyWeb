# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkoerper — Schritt „koerper" von „2D3D Kleider": die Genesis-9-Figur zum Netz (30.09.2026).

Zwei Quellen (Option `koerper.quelle`):

    uebernehmen   den fertigen Körper-Fit eines Auftrags „Mesh to 3D" (`koerper.auftrag`, Kennung) übernehmen:
                  Reglerstellung samt Eigenmorph, gebackene Kacheln, der Befund von Haar und Kleidung — und DESSEN
                  Netz samt Lage der Erkennung als Bezug für die 3D-Note der Iterationen (`arbeit/bezugsnetz.glb`,
                  `bezugsnetz_lage.npz`). Sekunden statt Minuten; für den ersten Lauf der Pipeline (Edgar, 30.09.2026:
                  „mach erstmal die ganze pipeline in geringer auflösung").
    rechnen       die Kette von „Mesh to 3D" auf dem Netz dieses Auftrags (Schritt „netz"): erkennung · haar ·
                  kleidung ·
                  kalibrierung · koerper · gesicht · rest · textur · vorschau · frisur — dieselben Schrittklassen,
                  unverändert, über `Engine2d3dKleiderkoerperlauf` (rund 15 min Grafikkarte). Speichern gehört nicht dazu.
                  Die FRISUR seit 01.10.2026: ohne sie hatten die Iterationen keine Kandidaten und begannen mit der
                  Vorgabe (`.52`: langes rotes Haar am Mann); die Iterationen wechseln weiter zwischen den Kandidaten.

Danach liegt die Stellung in `ergebnis['regler']['stellung']` (+ `rest`), wie „Mesh to 3D" sie schreibt —
`Engine2d3dKleidergrundfigur` baut daraus die Grundfigur mit Rig, `job.stellung()` liest sie für Bühne und Export.
"""

import logging
import shutil
import time

import numpy as np

from ..daten.meshfigurablage import Meshfigurablage
from ..models import Meshfigurauftrag
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderkoerper']


class Engine2d3dKleiderkoerper:
    #: Was aus dem Ergebnis des fremden Auftrags mitkommt (Felder von `Meshfigurauftrag.ergebnis`).
    FELDER = ('regler', 'rest', 'fototextur', 'kopfeigen', 'erkennung', 'koerper', 'gesicht', 'haar', 'kleidung',
              'testfall', 'frisur')
    #: Schritte der Kette „Mesh to 3D", die hier laufen (Quelle „rechnen").
    KETTE = ('erkennung', 'haar', 'kleidung', 'kalibrierung', 'koerper', 'gesicht', 'rest', 'textur', 'vorschau',
             'frisur')

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Engine2d3dKleideroptionen.koerper(self.job.optionen)

    def ausfuehren(self):
        t = time.perf_counter()
        if self.optionen.get('quelle') == 'rechnen':
            self._rechnen()
        else:
            self._uebernehmen()
        self.job.ergebnis.setdefault('koerperquelle', {})['sekunden'] = round(time.perf_counter() - t, 1)

    # ---------------------------------------------------------- übernehmen

    def _uebernehmen(self):
        kennung = str(self.optionen.get('auftrag') or '').strip()
        if not kennung:
            raise RuntimeError('Körper übernehmen: keine Kennung eines Auftrags „Mesh to 3D" (Option „Auftrag")')
        fremd = Meshfigurauftrag.objects.filter(kennung=kennung).first()
        if fremd is None:
            raise RuntimeError('Auftrag „Mesh to 3D" %s gibt es nicht' % kennung)
        stellung = ((fremd.ergebnis or {}).get('regler') or {}).get('stellung')
        if not stellung:
            raise RuntimeError('Auftrag %s hat keine fertige Figur (kein `regler.stellung`)' % kennung)
        self.lauf.melden(0.1, 'Körper aus „Mesh to 3D" %s übernehmen' % kennung)
        quelle = Meshfigurablage(kennung)
        ergebnis = self.job.ergebnis
        for feld in self.FELDER:
            if feld in (fremd.ergebnis or {}):
                ergebnis[feld] = fremd.ergebnis[feld]
            else:
                ergebnis.pop(feld, None)
        # Kacheln und Augenbild neben die eigenen Ergebnisse — die Bühne und der Export lesen sie von hier.
        kopiert = []
        foto = ergebnis.get('fototextur') or {}
        for name in list((foto.get('kacheln') or {}).values()) + [foto.get('augen')]:
            if name and quelle.ergebnis(name).is_file():
                shutil.copy2(quelle.ergebnis(name), self.ablage.ergebnis(name))
                kopiert.append(name)
        # Das Netz des Fits samt Lage: der 3D-Bezug der Iterationen.
        netz = quelle.netzdatei()
        bezug = None
        if netz is not None:
            bezug = self.ablage.arbeit(self.ablage.BEZUGSNETZ)
            shutil.copy2(netz, bezug)
            lage = quelle.arbeit('scan_lage.npz')
            if lage.is_file():
                shutil.copy2(lage, self.ablage.arbeit(self.ablage.BEZUGSLAGE))
        ergebnis['koerperquelle'] = {'quelle': 'uebernehmen', 'auftrag': kennung, 'name': fremd.name,
                                     'regler': len(stellung), 'kacheln': kopiert,
                                     'bezugsnetz': bezug.name if bezug else None}
        self.lauf.melden(1.0, 'Körper übernommen: %d Regler, %d Kacheln' % (len(stellung), len(kopiert)))

    # ------------------------------------------------------------- rechnen

    def _tiefe(self):
        """Das Tiefennetz (Option `koerper.tiefe`, `Netztiefe`) schreiben, bevor die Kette das Netz liest — oder ablegen, warum nicht. Ein Fehler hält den Lauf nicht auf: die Kette rechnet dann auf
        dem Original, und der Grund steht im Ergebnis (`ergebnis.netztiefe`) — nie ein stilles Zurückfallen."""
        from .netztiefe import Netztiefe
        try:
            bericht = Netztiefe(self.job, self.ablage).sichern()
        except Exception as fehler:  # noqa: BLE001 — siehe Docstring
            logger.exception('2D3D Kleider %s: Netztiefe gescheitert', self.job.kennung)
            bericht = {'aktiv': False, 'grund': 'Fehler: %s' % str(fehler)[:300]}
        self.job.ergebnis['netztiefe'] = bericht
        self.lauf.sichern('ergebnis')
        if bericht.get('aktiv'):
            self.lauf.melden(0.0, 'Netztiefe angeglichen (Faktor bis %.2f)' % bericht.get('staerkster_faktor', 1.0))

    def _rechnen(self):
        from .engine2d3dkleiderkoerperlauf import Engine2d3dKleiderkoerperlauf
        if self.ablage.netzdatei(original=True) is None:
            raise RuntimeError('Kein Netz — erst der Schritt „netz"')
        self._tiefe()
        kette = Engine2d3dKleiderkoerperlauf(self.lauf, self.optionen)
        schritte = kette.schrittfolge()
        for nummer, name in enumerate(self.KETTE):
            if self.lauf.angehalten():
                raise self.lauf.Angehalten()
            kette.band(nummer / len(self.KETTE), (nummer + 1) / len(self.KETTE), name)
            t = time.perf_counter()
            schritte[name]()
            self.job.ergebnis.setdefault('dauer_koerper', {})[name] = round(time.perf_counter() - t, 1)
            self.lauf.sichern('ergebnis')
        # Das eigene Netz ist der 3D-Bezug — mit der Lage der Erkennung.
        shutil.copy2(self.ablage.netzdatei(), self.ablage.arbeit(self.ablage.BEZUGSNETZ))
        lage = self.ablage.arbeit('scan_lage.npz')
        if lage.is_file():
            with np.load(lage) as d:
                np.savez(self.ablage.arbeit(self.ablage.BEZUGSLAGE), matrix=d['matrix'])
        self.job.ergebnis['koerperquelle'] = {'quelle': 'rechnen', 'bezugsnetz': self.ablage.BEZUGSNETZ}
