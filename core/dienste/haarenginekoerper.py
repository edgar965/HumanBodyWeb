# -*- coding: utf-8 -*-
"""Haarenginekoerper — Schritt „koerper" von „2D3D Kleider": die Genesis-9-Figur zum Netz (30.09.2026).

Zwei Quellen (Option `koerper.quelle`):

    uebernehmen   den fertigen Körper-Fit eines Auftrags „Mesh to 3D" (`koerper.auftrag`, Kennung) übernehmen:
                  Reglerstellung samt Eigenmorph, gebackene Kacheln, der Befund von Haar und Kleidung — und DESSEN
                  Netz samt Lage der Erkennung als Bezug für die 3D-Note der Iterationen (`arbeit/bezugsnetz.glb`,
                  `bezugsnetz_lage.npz`). Sekunden statt Minuten; für den ersten Lauf der Pipeline (Edgar, 30.09.2026:
                  „mach erstmal die ganze pipeline in geringer auflösung").
    rechnen       die Kette von „Mesh to 3D" auf dem Netz dieses Auftrags (Schritt „netz"): erkennung · haar ·
                  kleidung ·
                  kalibrierung · koerper · gesicht · rest · textur · vorschau — dieselben Schrittklassen, unverändert,
                  über `Haarenginekoerperlauf` (rund 15 min Grafikkarte). Frisur und Speichern gehören nicht dazu:
                  Frisur und Kleider sind hier Sache der Iterationen.

Danach liegt die Stellung in `ergebnis['regler']['stellung']` (+ `rest`), wie „Mesh to 3D" sie schreibt —
`Haarenginegrundfigur` baut daraus die Grundfigur mit Rig, `job.stellung()` liest sie für Bühne und Export.
"""

import logging
import shutil
import time

import numpy as np

from ..daten.meshfigurablage import Meshfigurablage
from ..models import Meshfigurauftrag
from .haarengineoptionen import Haarengineoptionen

logger = logging.getLogger('core')

__all__ = ['Haarenginekoerper']


class Haarenginekoerper:
    #: Was aus dem Ergebnis des fremden Auftrags mitkommt (Felder von `Meshfigurauftrag.ergebnis`).
    FELDER = ('regler', 'rest', 'fototextur', 'kopfeigen', 'erkennung', 'koerper', 'gesicht', 'haar', 'kleidung',
              'testfall', 'frisur')
    #: Schritte der Kette „Mesh to 3D", die hier laufen (Quelle „rechnen").
    KETTE = ('erkennung', 'haar', 'kleidung', 'kalibrierung', 'koerper', 'gesicht', 'rest', 'textur', 'vorschau')

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = Haarengineoptionen.koerper(self.job.optionen)

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

    def _rechnen(self):
        from .haarenginekoerperlauf import Haarenginekoerperlauf
        if self.ablage.netzdatei() is None:
            raise RuntimeError('Kein Netz — erst der Schritt „netz"')
        kette = Haarenginekoerperlauf(self.lauf, self.optionen)
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
