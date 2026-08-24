# -*- coding: utf-8 -*-
"""Prozesspruefung — lebt der Prozess mit dieser PID noch?

Herausgelöst aus `werkzeuge._is_pid_alive`, weil daran ein IMPORTZYKLUS hing
(gemeldet vom Werkzeug `abhaengigkeiten`, 18.08.2026):

    werkzeuge -> logbeobachter -> werkzeuge
    werkzeuge -> startaufraeumen -> werkzeuge

Der Beobachter braucht die PID-Prüfung, `werkzeuge` braucht den Beobachter. Dass
beide Importe in Funktionen stehen und deshalb nicht knallen, macht den Ring
nicht besser: Wer eine der Dateien liest, muss die andere kennen.

WARUM `OpenProcess` UND NICHT `os.kill(pid, 0)`
==============================================
Auf Windows gibt es kein Signal 0. `os.kill` wirft dort für einen lebenden
Prozess dasselbe wie für einen toten, wenn die Rechte fehlen. `OpenProcess` mit
`SYNCHRONIZE` fragt genau das, was gemeint ist: Gibt es diesen Prozess noch?

Das Handle wird geschlossen. Ohne `CloseHandle` sammelt jeder Aufruf eines an —
bei einer Beobachtung mit einem Blick je Sekunde sind das 3.600 je Stunde.
"""

import logging

logger = logging.getLogger('core')


class Prozesspruefung:
    """Fragt das Betriebssystem, ob eine PID noch zu einem Prozess gehört."""

    #: `SYNCHRONIZE` — das schwächste Recht, das für die Frage reicht.
    SYNCHRONIZE = 0x00100000

    @classmethod
    def lebt(cls, pid):
        """True, wenn der Prozess läuft. Bei jedem Zweifel False."""
        if not pid:
            return False
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(cls.SYNCHRONIZE, False, int(pid))
            if not handle:
                return False
            kernel32.CloseHandle(handle)
            return True
        except Exception:                                          # noqa: BLE001
            # Kein Windows, keine ctypes, unbrauchbare PID: „lebt nicht" ist die
            # sichere Antwort — sonst wartet die Beobachtung endlos.
            logger.debug('PID-Prüfung für %s fehlgeschlagen', pid, exc_info=True)
            return False
