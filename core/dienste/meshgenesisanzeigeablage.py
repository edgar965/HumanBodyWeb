# -*- coding: utf-8 -*-
"""Meshgenesisanzeigeablage — das fertige Anzeigepaket einer Testfigur auf Netzstufe 1 als Datei, vorgebaut am Ende jedes Rechenlaufs (13.11.2026). Besitzer: Mesh-Genesis.

Edgar, 13.11.2026, zu `/foto-genesis/test/zauberer_performancen/`: „warum erscheint immer noch bei den Jobs … das genesis modell erst nach langer Zeit, und wird nicht vorher gebaut?? Ich habe
das schon 10 Mal aufgetragen dass es vorher gebaut wird und schnell angezeigt wird!“ — Bis dahin lag die Stufe 1 (`Meshgenesisflaechennetzfein`) nur im Speicher des Servers: nach jedem
Neustart oder Autoreload baute der erste Abruf sie neu (Server-Log 13.11.2026 21:05–21:07: 98 s und 108 s; davon 52 s die Einzelzuweisungen in `G9netzstufe._hautstufe`, seit dem Stapel-
Umbau 4,9 s). Jetzt:
- `Meshgenesisflaechennetz.paket(…, stufe=1)` liest zuerst diese Datei und schreibt sie nach jedem Bau (`lesen`, `schreiben`);
- `Meshgenesisrechenlauf.ausfuehren` baut sie am Ende jedes Laufs (`vorbauen`) — die Seite findet die Figur fertig vor.
Der Name trägt den Stand von allem, woraus das Paket entsteht (artefakte-benennen): `netz.npz` und `materialien.json` (`Meshgenesisflaechennetz._stand`), `modell.json` (Regler und
Anatomie-Stück, wie der Schlüssel in `Meshgenesisflaechennetzfein.netz`), `matrix` ja/nein und `FASSUNG` — ändert sich der Bau der Stufe 1 (`Meshgenesisflaechennetzfein`, `G9netzstufe`,
`G9hdmorphe`), steigt `FASSUNG`. Ein Paket anderen Stands wird nie gelesen; beim Schreiben fallen ältere Pakete desselben Ordners weg (nur eigene Dateien `stufe1_*.bin`).

    Meshgenesisanzeigeablage.lesen(modell, matrix) -> bytes | None
    Meshgenesisanzeigeablage.schreiben(modell, matrix, paket)
    Meshgenesisanzeigeablage.vorbauen(kennung, geschlecht) -> float | None       Sekunden, None ohne Figur
"""

import hashlib
import logging
import time

from ..atomic_write import AtomarSchreiber
from .meshgenesisdatensatz import Meshgenesisdatensatz

logger = logging.getLogger('core')

__all__ = ['Meshgenesisanzeigeablage']


class Meshgenesisanzeigeablage:
    FASSUNG = 1
    MUSTER = 'stufe1_*.bin'

    @classmethod
    def _datei(cls, modell, matrix):
        """Pfad des Pakets zum jetzigen Stand oder None (kein Netz)."""
        from .meshgenesisflaechennetz import Meshgenesisflaechennetz
        ordner = Meshgenesisflaechennetz.ordner(modell)
        stand = Meshgenesisflaechennetz._stand(ordner)
        if stand is None:
            return None
        try:
            modell_stand = (Meshgenesisdatensatz.ordner(modell) / 'modell.json').stat().st_mtime_ns
        except OSError:
            modell_stand = None
        h = hashlib.sha1(repr((cls.FASSUNG, stand, modell_stand, bool(matrix))).encode('utf-8')).hexdigest()[:16]
        return ordner / ('stufe1_%s_%s.bin' % ('m' if matrix else 'o', h))

    @classmethod
    def lesen(cls, modell, matrix):
        datei = cls._datei(modell, matrix)
        if datei is None or not datei.is_file():
            return None
        try:
            return datei.read_bytes()
        except OSError as fehler:
            logger.warning('Meshgenesisanzeigeablage: %s unlesbar (%s)', datei, fehler)
            return None

    @classmethod
    def schreiben(cls, modell, matrix, paket):
        datei = cls._datei(modell, matrix)
        if datei is None or not paket:
            return
        try:
            AtomarSchreiber.bytes_schreiben(datei, paket)
            for alt in datei.parent.glob('stufe1_%s_*.bin' % ('m' if matrix else 'o')):
                if alt != datei:
                    alt.unlink(missing_ok=True)
        except OSError as fehler:
            logger.warning('Meshgenesisanzeigeablage: %s nicht geschrieben (%s)', datei, fehler)

    @classmethod
    def vorbauen(cls, kennung, geschlecht):
        """Das Paket, wie die Jobseiten es holen (`?stufe=1&matrix=1`), und das ohne Matrix (Mesh-Genesis-Testseite) bauen und ablegen. → Sekunden oder None ohne Figur."""
        from .meshgenesisflaechennetz import Meshgenesisflaechennetz
        from .meshgenesistest import Meshgenesistest
        modell = Meshgenesistest.form_ordner(kennung, geschlecht)
        if modell is None:
            return None
        t = time.perf_counter()
        for matrix in (True, False):
            Meshgenesisflaechennetz.paket(modell, stufe=1, matrix=matrix)
        dauer = time.perf_counter() - t
        logger.info('Meshgenesisanzeigeablage: Stufe 1 von %s (%s) vorgebaut in %.1f s', kennung, geschlecht, dauer)
        return dauer
