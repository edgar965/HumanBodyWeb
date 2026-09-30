# -*- coding: utf-8 -*-
"""Kostuemblender — einen Stapel Kandidaten von mehreren dauerhaft laufenden Blender-Prozessen bauen und
rendern lassen (`effekte/blender/kostuembau.py`, Betriebsart „Dienst", verwaltet von `Kostuemarbeiter`).

Bis 30.09.2026 startete jede Runde einen neuen Blender-Prozess, der die Grundfigur lud (4–9 s gemessen) und
die Kandidaten nacheinander rechnete (je 0,6–0,8 s): Eine Runde mit acht Kandidaten war zu drei Vierteln
Warten aufs Laden — und mehr Prozesse je Runde hätten es nicht besser gemacht (4 × 2 Kandidaten 14,8 s gegen
16,3 s bei einem Prozess). Jetzt laden `parallel` Arbeiter die Figur EINMAL je Lauf; jede Runde verteilt die
Kandidaten reihum und sammelt die Berichte ein. Ein Arbeiter, der stirbt oder zu alt wird, wird ersetzt;
scheitert eine Runde an einem Arbeiter, läuft sie einmal mit frischen Arbeitern nochmal.

`dauerhaft=False` (Voreinstellung): Die Arbeiter werden nach jedem `rendern` wieder beendet — so verhält sich
ein einzelner Aufruf wie früher (Wegwerf-Skripte, Proben). Der Kreislauf setzt `dauerhaft=True` und ruft am
Ende `schliessen`.
"""

import logging
import shutil
import time
import uuid
from pathlib import Path

from .kostuemarbeiter import Kostuemarbeiter

logger = logging.getLogger('core')

__all__ = ['Kostuemblender']


class Kostuemblender:
    SKRIPT = Kostuemarbeiter.SKRIPT
    BREITE, HOEHE = 256, 384

    def __init__(self, lauf, parallel=1, dauerhaft=False):
        self.lauf = lauf
        self.ablage = lauf.ablage
        self.parallel = max(1, int(parallel))
        self.dauerhaft = dauerhaft
        self.arbeiter = []
        self._koerper = None
        # Ein EIGENER Postfach-Ordner je Kostuemblender: Ein Wegwerf-Skript oder eine Probe am selben Auftrag
        # darf die Arbeiter eines laufenden Kreislaufs nicht mit wegräumen (30.09.2026: genau das passierte —
        # `schliessen` einer Probe löschte den gemeinsamen Ordner, die Arbeiter des Laufs starben beim
        # Schreiben ihrer Antwort).
        self.wurzel = self.ablage.arbeit('kostuem_dienst') / uuid.uuid4().hex[:8]

    # ---------------------------------------------------------------- Arbeiter

    def _bereitmachen(self, koerper, anzahl):
        """`anzahl` laufende Arbeiter mit geladener Figur — fehlende, tote und alte werden neu gestartet (alle
        gleichzeitig, sie laden parallel)."""
        if self._koerper != str(koerper):
            self.schliessen()
            self._koerper = str(koerper)
        neu = []
        for i in range(anzahl):
            if i < len(self.arbeiter):
                if self.arbeiter[i].lebt() and not self.arbeiter[i].alt():
                    continue
                self.arbeiter[i].beenden()
            frisch = Kostuemarbeiter(self.lauf, i, koerper, self.BREITE, self.HOEHE, self.wurzel)
            frisch.starten()
            neu.append(frisch)
            if i < len(self.arbeiter):
                self.arbeiter[i] = frisch
            else:
                self.arbeiter.append(frisch)
        for frisch in neu:
            frisch.bereit()
        return self.arbeiter[:anzahl]

    def schliessen(self):
        """Alle Arbeiter beenden und ihr Postfach wegräumen."""
        for arbeiter in self.arbeiter:
            arbeiter.beenden()
        self.arbeiter = []
        self._koerper = None
        shutil.rmtree(self.wurzel, ignore_errors=True)

    # ---------------------------------------------------------------- Rendern

    def rendern(
        self,
        koerper,
        aus,
        kandidaten,
        winkel,
        glb=False,
        blend=False,
        fortschritt=None,
        haltung=True,
        texturen=None,
        textur_winkel=None,
        masken=None,
        basis=None,
        sicht=False,
    ):
        """`kandidaten`: [(name, parameter)] → Bericht (dict: `vorn_grad`, `koerper`, `kandidaten` {name: …},
        `sekunden`). Bilder unter `aus/<name>/`. `glb`: je Kandidat Figur + Kostüm + Rig; `haltung`: in der
        gestellten Haltung (sonst Ruhelage des Rigs). `texturen`: {winkel: Pfad} der normierten
        Vorlagenflächen — dann bekommen Modell und GLB die Farben der Vorlage (Fototextur), `textur_winkel`
        die Blickwinkel, die damit zusätzlich gerendert werden (`winkel` muss die der Vorlagen enthalten).
        `masken`: {winkel: Pfad} der Silhouetten der Vorlage — dann folgt der Mantel dem Umriss
        (`Kostuemhuelle`); `basis`: der Wertesatz des Ausgangsmodells, an dem die Normierung der Hülle hängt
        (ohne: der erste Kandidat)."""
        aus = Path(aus)
        aus.mkdir(parents=True, exist_ok=True)
        befehl = {
            'aus': str(aus),
            'winkel': [float(w) for w in winkel],
            'glb': glb,
            'blend': blend,
            'haltung': haltung,
        }
        if texturen:
            befehl['texturen'] = {str(w): str(p) for w, p in texturen.items()}
            befehl['textur_winkel'] = [float(w) for w in textur_winkel or []]
        if masken:
            befehl['masken'] = {str(w): str(p) for w, p in masken.items()}
            befehl['basis'] = basis
        if sicht:
            befehl['sicht'] = True
        try:
            bericht = self._mit_wiederholung(koerper, befehl, kandidaten, fortschritt)
        finally:
            if not self.dauerhaft:
                self.schliessen()
        return bericht

    #: Versuche je Runde (frische Arbeiter nach jedem Fehlschlag). Ein Lauf, der eine ganze Nacht rechnet, darf an
    #: einem einzelnen Ausfall nicht enden (30.09.2026 01:39: ein PermissionError beendete ihn nach 770 Runden).
    VERSUCHE = 3

    def _mit_wiederholung(self, koerper, befehl, kandidaten, fortschritt):
        for versuch in range(1, self.VERSUCHE + 1):
            try:
                return self._einmal(koerper, befehl, kandidaten, fortschritt)
            except RuntimeError as fehler:
                logger.warning(
                    'BlenderModel: Blender-Arbeiter gescheitert (%s) — Versuch %d von %d',
                    fehler,
                    versuch,
                    self.VERSUCHE,
                )
                self.schliessen()
                if versuch == self.VERSUCHE:
                    raise
                time.sleep(2.0 * versuch)

    def _einmal(self, koerper, befehl, kandidaten, fortschritt):
        t0 = time.perf_counter()
        n = min(self.parallel, len(kandidaten))
        arbeiter = self._bereitmachen(koerper, n)
        if fortschritt:
            fortschritt('Blender: %d Kandidaten auf %d Prozessen' % (len(kandidaten), n))
        nummern = [
            a.senden(
                dict(befehl, kandidaten=[{'name': name, 'parameter': p} for name, p in kandidaten[i::n]])
            )
            for i, a in enumerate(arbeiter)
        ]
        berichte = []
        for i, (a, nummer) in enumerate(zip(arbeiter, nummern, strict=True), 1):
            berichte.append(a.antwort(nummer))
            if fortschritt and n > 1:
                fortschritt('Blender: %d von %d Prozessen fertig' % (i, n))
        bericht = dict(berichte[0], kandidaten={})
        for b in berichte:
            bericht['kandidaten'].update(b['kandidaten'])
        bericht['sekunden'] = round(time.perf_counter() - t0, 1)
        return bericht
