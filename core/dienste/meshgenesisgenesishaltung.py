# -*- coding: utf-8 -*-
"""Meshgenesisgenesishaltung — die Haltung eines Tests als Daz-Gelenkwinkel für `Genesis9Modell` (19.11.2026).

Edgar: „merge beide anzeigen zu einem Code. nimm die schnellste lösung von beiden“ — das Genesis-Ergebnis
der Foto-Genesis-Seite (`Fotogenesistestfigur`) baute die Figur aus einem vorab gerechneten Anzeigenetz
mit eigener Häutung, Charakter, Mesh-Genesis-Jobseite und Abspielleiste mit `Genesis9Modell`. Gemessen
im Chrome (frischer Tab, Körper, Augen und 7 Stücke von Goldprinzessin _57, je dreimal): Anzeigenetz
2.258–2.921 ms, Genesis9Modell 2.305–2.803 ms — gleich schnell; es bleibt der Code der Charakter-Seite.
Dafür braucht die Figur die Haltung als Winkel (`figur.drehung`, wie `Meshgenesisgenesis.probe` für die
Jobseite); die Testdaten trugen sie nur als Drehung je Knochen gegen die Ruhelage (`dreh`).

Die Rechnung (`Meshgenesisdazwinkel.aus_drehungen`, Knochen für Knochen) kostet 1,6–2,2 s je Abruf
(gemessen 19.11.2026, `ProjektTemp/_wegwerf/gc_sim_torch/haltung_zeit.py`; ohne sie 0,03 s) — darum liegt
das Ergebnis neben der Ergebnisdatei (`<ergebnis>_drehung.json`), gültig für Änderungszeit und Knochenliste;
mit der Ablage 0,018 s je Abruf.

    Meshgenesisgenesishaltung.drehung(knochen aus kinematik.json, dreh (N, 3, 3), ergebnisdatei, art) -> {…} | None

`art` (seit 19.11.2026 abends, Fassung 2): welche Haltung der Datei — 'foto' (`dreh`) oder 'stand' (`dreh_stand`, die Fußregel von 3dtools-96: Füße
flach, Figur gesenkt). Beide liegen in derselben Datei mit derselben Änderungszeit; ohne die Art im Schlüssel und im Dateinamen gäbe die Ablage
der einen die Winkel der anderen. `Meshgenesishaltungwahl.felder` sagt, welche die Anzeige nimmt.
"""
import hashlib
import json
import logging
from pathlib import Path

from KoerperKI_alle.npztorch import Npztorch

from ..atomic_write import AtomarSchreiber
from .meshgenesisdazwinkel import Meshgenesisdazwinkel
from .meshgenesisgenesis import Meshgenesisgenesis

logger = logging.getLogger(__name__)

__all__ = ['Meshgenesisgenesishaltung']


class Meshgenesisgenesishaltung:
    FASSUNG = 2

    @classmethod
    def drehung(cls, knochen, dreh, datei=None, art='foto'):
        u"""Daz-Gelenkwinkel der Haltung `dreh` — None, wenn sie sich nicht rechnen lassen (die Seite zeigt
        die Figur dann in der Ruhelage und sagt es). `datei`: die Ergebnisdatei, aus der `dreh` stammt; `art`: 'foto' | 'stand'."""
        ablage, schluessel = cls._ablage(datei, knochen, art)
        if ablage is not None:
            try:
                alt = json.loads(ablage.read_text(encoding='utf-8'))
                if alt.get('schluessel') == schluessel:
                    return alt.get('drehung')
            except (OSError, ValueError):
                pass
        try:
            drehung = Meshgenesisgenesis.drehung(knochen, Meshgenesisdazwinkel.aus_drehungen(dreh, knochen))
        except (ValueError, RuntimeError, KeyError, IndexError) as fehler:
            logger.warning('Meshgenesisgenesishaltung: Winkel nicht gerechnet (%s)', fehler)
            return None
        if ablage is not None:
            try:
                AtomarSchreiber.json_schreiben(ablage, {'schluessel': schluessel, 'drehung': drehung})
            except OSError as fehler:
                logger.warning('Meshgenesisgenesishaltung: %s nicht geschrieben (%s)', ablage, fehler)
        return drehung

    @classmethod
    def _ablage(cls, datei, knochen, art='foto'):
        u"""(Pfad der Ablage, Schlüssel aus Fassung, Haltungsart, Änderungszeit und Knochennamen) — ohne Datei
        (None, None). `datei` ist der logische Name (`….npz`), die echte Datei oft `….pt` (`Npztorch`)."""
        if datei is None:
            return None, None
        datei = Path(datei)
        try:
            stand = Npztorch.stat(datei).st_mtime_ns
        except OSError:
            return None, None
        namen = hashlib.sha1('|'.join(k['name'] for k in knochen).encode('utf-8')).hexdigest()[:12]
        endung = '_drehung.json' if art == 'foto' else '_drehung_%s.json' % art
        return datei.with_name(datei.stem + endung), 'v%d:%s:%d:%s' % (cls.FASSUNG, art, stand, namen)
