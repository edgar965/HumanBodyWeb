# -*- coding: utf-8 -*-
"""AtomarSchreiber — Dateien ganz oder gar nicht schreiben.

WARUM (Review 12.08.2026)
------------------------
Projekt- und BVH-Dateien wurden direkt beschrieben:

    with open(pfad, 'w') as f:      # ALT
        json.dump(daten, f)

Das ist kein Vorgang, das sind zwei Zustände. Bricht er dazwischen ab — zweiter
Tab speichert gleichzeitig, Anfrage abgebrochen, Platte voll, Prozess beendet —
bleibt eine halb geschriebene Datei liegen. Beim nächsten Laden kommt dann kein
klarer Fehler, sondern ein `JSONDecodeError` an einer Stelle, die mit der Ursache
nichts zu tun hat. Genau diese Sorte Fehler kostet abends eine Stunde.

WIE
---
In dasselbe Verzeichnis wird eine Nebendatei geschrieben, geleert (`flush` +
`os.fsync`, damit die Daten wirklich auf der Platte sind und nicht nur im
Zwischenspeicher des Betriebssystems), dann per `os.replace` an ihren Platz
gerückt. `os.replace` ist auf einem Laufwerk unteilbar: Ein Leser sieht entweder
den alten oder den neuen Stand, nie einen halben.

DASSELBE VERZEICHNIS ist keine Bequemlichkeit, sondern Bedingung: Über
Laufwerksgrenzen hinweg ist `os.replace` kein Umbenennen mehr, sondern ein
Kopieren — und damit wieder unterbrechbar.

WINDOWS: Ist die Zieldatei von einem anderen Programm geöffnet (Editor, Blender,
Virenscanner), schlägt `os.replace` mit `PermissionError` fehl. Das wird KURZ
wiederholt, statt sofort aufzugeben — Virenscanner halten Dateien oft nur
Millisekunden. Bleibt es dabei, wird der Fehler gemeldet und die Nebendatei
entfernt; die Originaldatei ist dann unversehrt.
"""
import json
import logging
import os
import tempfile
import time
from pathlib import Path

logger = logging.getLogger('core')


class AtomarSchreiber:
    """Schreibt Text- und JSON-Dateien unteilbar."""

    #: Wiederholungen, falls Windows die Zieldatei kurz sperrt.
    VERSUCHE = 4
    PAUSE_S = 0.15

    @classmethod
    def json_schreiben(cls, pfad, daten, einzug=2):
        """JSON unteilbar schreiben. Gibt den geschriebenen Pfad zurück."""
        text = json.dumps(daten, indent=einzug, ensure_ascii=False)
        return cls.text_schreiben(pfad, text)

    @classmethod
    def text_schreiben(cls, pfad, text, zeilenende=None):
        """Text unteilbar schreiben.

        `zeilenende='\\n'` erzwingt Unix-Zeilenenden — BVH-Dateien brauchen das,
        sonst stolpern Leser über `\\r\\n`."""
        ziel = Path(pfad)
        ziel.parent.mkdir(parents=True, exist_ok=True)

        tmp_name = None
        try:
            # delete=False, weil die Datei nach dem Schließen noch gebraucht wird;
            # dir=ziel.parent, damit os.replace auf demselben Laufwerk bleibt.
            with tempfile.NamedTemporaryFile(
                    mode='w', encoding='utf-8', newline=zeilenende,
                    dir=str(ziel.parent), prefix='.' + ziel.name + '.', suffix='.tmp',
                    delete=False) as f:
                tmp_name = f.name
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            cls._ersetzen(tmp_name, ziel)
            tmp_name = None
            return ziel
        finally:
            if tmp_name and os.path.exists(tmp_name):
                try:
                    os.unlink(tmp_name)
                except OSError:
                    logger.warning('AtomarSchreiber: Nebendatei blieb liegen: %s', tmp_name)

    @classmethod
    def _ersetzen(cls, quelle, ziel):
        letzter = None
        for versuch in range(cls.VERSUCHE):
            try:
                os.replace(quelle, str(ziel))
                return
            # stumm gewollt: Der letzte Fehlschlag steht nach der Versuchsreihe im Log
            # (`letzter`) — je Versuch zu protokollieren wäre derselbe Fehler dreimal.
            except PermissionError as e:
                # Typisch Windows: Datei ist kurz von einem anderen Programm offen.
                letzter = e
                time.sleep(cls.PAUSE_S * (versuch + 1))
        logger.error('AtomarSchreiber: %s liess sich nicht ersetzen: %s', ziel, letzter)
        raise letzter
