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
Prozess dasselbe wie für einen toten, wenn die Rechte fehlen. `OpenProcess`
fragt genau das, was gemeint ist: Gibt es diesen Prozess noch?

Das Handle wird geschlossen. Ohne `CloseHandle` sammelt jeder Aufruf eines an —
bei einer Beobachtung mit einem Blick je Sekunde sind das 3.600 je Stunde.

UND DER EXITCODE (12.09.2026, aus `Umabauer._prozess_lebt` uebernommen)
=======================================================================
`OpenProcess` gelingt auch fuer einen BEENDETEN Prozess, solange irgendwer
sein Handle haelt — ein `subprocess.Popen`-Objekt tut genau das, bis es
aufgeraeumt wird. Erst `GetExitCodeProcess` sagt, ob er noch laeuft
(259 = STILL_ACTIVE). Vorher stand diese Pruefung ein zweites Mal im
UMA-Bauer; jetzt fragt der hier.
"""

import logging

logger = logging.getLogger('core')


class Prozesspruefung:
    """Fragt das Betriebssystem, ob eine PID noch zu einem Prozess gehört."""

    #: `PROCESS_QUERY_LIMITED_INFORMATION` — das schwächste Recht, mit dem
    #: `GetExitCodeProcess` antwortet.
    ABFRAGE = 0x1000
    #: Was `GetExitCodeProcess` für einen laufenden Prozess liefert.
    STILL_ACTIVE = 259

    @classmethod
    def lebt(cls, pid):
        """True, wenn der Prozess läuft. Bei jedem Zweifel False."""
        if not pid:
            return False
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            kernel32.OpenProcess.restype = wintypes.HANDLE
            handle = kernel32.OpenProcess(cls.ABFRAGE, False, int(pid))
            if not handle:
                return False
            try:
                code = wintypes.DWORD()
                kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
                return code.value == cls.STILL_ACTIVE
            finally:
                kernel32.CloseHandle(handle)
        except Exception:                                          # noqa: BLE001
            # Kein Windows, keine ctypes, unbrauchbare PID: „lebt nicht" ist die
            # sichere Antwort — sonst wartet die Beobachtung endlos.
            logger.debug('PID-Prüfung für %s fehlgeschlagen', pid, exc_info=True)
            return False
