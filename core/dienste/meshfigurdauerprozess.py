# -*- coding: utf-8 -*-
"""Meshfigurdauerprozess — der python10-Prozess, der alle Runner-Schritte eines Laufs „Mesh to 3D" nacheinander rechnet (12.10.2026).

Edgar: „optimiere weiter, z.B. Nicht gebaut: ein Dauerprozess für alle Schritte." Bisher startete `Meshfigurlauf.runner` für jeden Schritt einen neuen Prozess (Torch importieren 4–5 s, CUDA-Kontext, Daten laden: rund zehn Sekunden
Fixkosten, siebenmal je Lauf). Hier bleibt EIN Prozess (`_run_meshfigur.py --dauer`, `Meshfigurdauerlauf`) stehen; jeder Schritt ist ein Befehl auf seinem stdin, seine Ausgabe dieselben Zeilen wie im Einzelaufruf, abgeschlossen von
`[ende] <schritt>`. Der Zustand zwischen den Schritten läuft weiter über die Dateien im Arbeitsordner, nie über den Speicher des Prozesses.

Was den Prozess beendet (der nächste Schritt startet dann einen frischen): Ende des Laufs (`schliessen`), ein Fehler im Schritt (das Kind beendet sich selbst), Anhalten durch den Nutzer, Stille über der Zeitgrenze, ein totes Kind.
Aus ist er mit `MESHFIGUR_DAUER=0` — dann startet `Meshfigurlauf.runner` wieder einen Prozess je Schritt.
"""

import json
import logging
import os
import threading

from ..pipeline_process import PipelineProzess

logger = logging.getLogger('core')

__all__ = ['Meshfigurdauerprozess']


class Meshfigurdauerprozess:
    """Hält den Prozess eines Laufs; ein Befehl zur Zeit (Sperre)."""

    SCHALTER = 'MESHFIGUR_DAUER'
    #: So lange darf das Kind nach `ende` noch brauchen, bevor es beendet wird (CUDA-Kontext abbauen).
    ENDE_FRIST_S = 20

    def __init__(self):
        self._pp = None
        self._schloss = threading.Lock()

    @classmethod
    def erlaubt(cls):
        return os.environ.get(cls.SCHALTER, '1') != '0'

    def lebt(self):
        return self._pp is not None and self._pp.proc.poll() is None

    @property
    def pid(self):
        return None if self._pp is None else self._pp.proc.pid

    def rechnen(self, befehl, auftrag, schritt, runde, umgebung, cwd, bei_zeile, stille_s):
        """Einen Schritt im Dauerprozess rechnen. `bei_zeile(zeile)` bekommt jede Ausgabezeile (ohne `[ende]`) und darf werfen (Anhalten) — dann wird der Prozess beendet. Rückgabe: die letzten stderr-Zeilen
        als Text (für Fehlermeldungen des Aufrufers). Wirft `RuntimeError`, wenn der Prozess ohne `[ende]` endet oder nicht startet, und `PipelineStille` bei Stille."""
        with self._schloss:
            try:
                pp = self._bereit(befehl, umgebung, cwd)
                pp.senden(json.dumps({'auftrag': str(auftrag), 'schritt': schritt, 'runde': runde}, ensure_ascii=False))
                for zeile in pp.stdout_zeilen(stille_timeout=stille_s):
                    zeile = zeile.rstrip('\n')
                    if zeile.startswith('[ende]'):
                        return pp.fehlertext(1500)
                    bei_zeile(zeile)
                raise RuntimeError('Der Runner endete ohne Antwort (%s)' % (pp.fehlertext(1500) or 'kein Fehlertext'))
            except BaseException:
                self._verwerfen()           # jeder Abbruch beendet den Prozess — der nächste Schritt startet frisch
                raise

    def _bereit(self, befehl, umgebung, cwd):
        if not self.lebt():
            self._verwerfen()
            self._pp = PipelineProzess.starten(list(befehl), cwd=cwd, env_extra=umgebung, stdin_offen=True)
            logger.info('Mesh to 3D: Dauerprozess %s gestartet', self._pp.proc.pid)
        return self._pp

    def _verwerfen(self):
        pp, self._pp = self._pp, None
        if pp is not None:
            pp.beenden()

    def schliessen(self):
        """Dem Kind `ende` schicken und auf sein Ende warten; sonst beenden. Wiederholbar."""
        with self._schloss:
            pp, self._pp = self._pp, None
            if pp is None:
                return
            try:
                if pp.proc.poll() is None:
                    pp.senden('ende')
                    pp.stdin_schliessen()
                    pp.warten(timeout=self.ENDE_FRIST_S)
            except Exception:  # noqa: BLE001 — hängt es, wird es beendet; mehr braucht der Aufrufer nicht zu wissen
                logger.warning('Mesh to 3D: Dauerprozess endet nicht von selbst, wird beendet')
            finally:
                pp.beenden()
