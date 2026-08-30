# -*- coding: utf-8 -*-
u"""Stromleser — die beiden Faeden, die stdout und stderr leerlesen.

Aus `pipeline_process.py` herausgeloest (30.08.2026, Befund `dateigroesse`).
Die Datei trug zwei Dinge: das Starten eines Subprozesses und das Leerlesen
seiner Stroeme. Das Zweite ist eine eigene Sache — und die mit der teuersten
Begruendung im Rumpf (siehe `stderr`).

WARUM UEBERHAUPT FAEDEN: Laeuft der Pipe-Puffer (etwa 64 KB) voll, blockiert
der Kindprozess beim Schreiben, waehrend Django auf die naechste stdout-Zeile
wartet. Beide warten dann aufeinander, und der Auftrag haengt.
"""
import logging
import queue                                                       # noqa: F401

logger = logging.getLogger('core')


class Stromleser:
    """Liest die Stroeme eines Subprozesses in eigenen Faeden leer."""

    #: So viele stderr-Zeilen werden behalten. Mehr braucht keine Fehlermeldung,
    #: und ein Modell-Download mit Fortschrittsbalken schreibt Zehntausende.
    STDERR_ZEILEN = 400

    #: Endemarke in der stdout-Warteschlange. Eine eigene Kennung statt `None`,
    #: damit eine leere Zeile aus der Pipeline nicht als Ende gelesen wird.
    ENDE = object()

    @staticmethod
    def stderr_lesen(strom, ziel):
        # KEIN Lock um Anhängen und Kürzen, und das ist geprüft: `str.join` und
        # `list(...)` auf der Leserseite sind C-Funktionen, die den GIL nicht
        # abgeben — ein anderer Faden läuft währenddessen gar nicht. Zwei
        # Modelle haben hier unabhängig ein Datenrennen vorhergesagt;
        # `Docu/gegenprobe_stderr_race.py` hat es mit 3,2 Mio. Anhänge- und
        # 434.000 Lesevorgängen nicht auslösen können (13.08.2026).
        # ACHTUNG: Diese Zusicherung fällt mit dem GIL. Die Gegenprobe prüft
        # `sys._is_gil_enabled()` mit und schlägt an, wenn sie nicht mehr gilt.
        try:
            for zeile in strom:
                ziel.append(zeile)
                if len(ziel) > Stromleser.STDERR_ZEILEN:
                    del ziel[:-Stromleser.STDERR_ZEILEN]
        # stumm gewollt: Der Strom wurde geschlossen — der Prozess ist fertig.
        # Das ist das normale Ende dieses Fadens, kein Fehler.
        except (ValueError, OSError):
            pass

    @classmethod
    def stdout_lesen(cls, strom, ziel_q):
        """stdout leerlesen — ohne Rücksicht darauf, ob jemand abholt."""
        try:
            for zeile in strom:
                ziel_q.put(zeile)
        # stumm gewollt: Strom geschlossen — normales Ende. Das `finally`
        # darunter setzt die Endmarke, sonst wartet der Abholer ewig.
        except (ValueError, OSError):
            pass
        finally:
            ziel_q.put(cls.ENDE)    # auch im Fehlerfall: sonst wartet der Abholer ewig


__all__ = ['Stromleser']
