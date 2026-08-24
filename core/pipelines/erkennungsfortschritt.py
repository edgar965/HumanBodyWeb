# -*- coding: utf-8 -*-
"""Fortschritt einer 2D-Erkennung aus den Ausgabezeilen des Wrappers lesen.

WARUM (17.08.2026): Diese Auswertung stand ZWEIMAL in `erkennung2d.py` — einmal
für MediaPipe, einmal für die neuen Erkenner (RTMPose/ViTPose/YOLO11). Beide
Male dieselben 25 Zeilen: `TOTAL:` lesen, `PROGRESS:` lesen, auf eine Meldung je
Sekunde drosseln, Prozent, Bildrate und Restzeit rechnen, speichern. Gefunden
von `kapselung` (drei Funktionen um dieselben drei Werte herum).

DIE DROSSELUNG IST KEIN SCHÖNHEITSFEHLER: Der Wrapper meldet mit
`--progress-interval 1` JEDE Frame. Ohne die Sperre schreibt eine
30-fps-Pipeline dreißigmal je Sekunde in die Datenbank — bei einem Video mit
3.000 Bildern 3.000 UPDATEs statt hundert.

WARUM DIE ZEIT HEREINGEGEBEN WIRD: `jetzt=` als Parameter statt `time.time()` im
Rumpf. Nur so ist die Rechnung prüfbar, ohne auf die Uhr zu warten — dasselbe
Muster wie in `Fortschrittsleser` für den MocapNET-Lauf.
"""

import logging

logger = logging.getLogger('core')


class Erkennungsfortschritt:
    """Wertet die Zeilen eines 2D-Erkenners aus und schreibt sie an den Auftrag."""

    #: Die 2D-Erkennung ist der erste Abschnitt des Laufs. Sie darf höchstens
    #: bis hierher zählen, danach kommt MocapNET.
    ANTEIL = 45
    #: Höchstens eine Datenbankschreibung je Sekunde.
    SPERRE_S = 1.0

    def __init__(self, job, gesamt, jetzt, name='', anteil=None):
        self.job = job
        self.gesamt = gesamt or 0
        self.start = jetzt
        #: Name des Erkenners für die Textmeldung; leer = ohne Vorsatz.
        self.name = name
        #: Bis wohin dieser Abschnitt zählt. MocapNET v4 macht Erkennung UND
        #: BVH in einem Lauf und darf deshalb bis 98 % zählen — vorher stand
        #: dieselbe Auswertung dafür ein zweites Mal in `mocapnet4.py`
        #: (Kriterium 6, gefunden 17.08.2026).
        self.anteil = self.ANTEIL if anteil is None else anteil
        self._letzte = 0.0

    def zeile_lesen(self, zeile, jetzt):
        """Eine Ausgabezeile verarbeiten. True, wenn etwas geschrieben wurde."""
        zeile = zeile.strip()
        if zeile.startswith('STATUS:'):
            return self._melden('%s%s' % (self._vorsatz(), zeile[7:]))
        if zeile.startswith('TOTAL:'):
            return self._gesamtzahl(zeile[6:], jetzt)
        if zeile.startswith('PROGRESS:'):
            return self._fortschritt(zeile[9:], jetzt)
        return False

    # ------------------------------------------------------------- Einzelfälle

    def _gesamtzahl(self, text, jetzt):
        """`TOTAL:` setzt die Bezugsgröße — und die Uhr.

        Der Erkenner meldet sie erst, NACHDEM er seine Modelle geladen hat. Ohne
        das Zurücksetzen der Startzeit ginge die Ladezeit in die Bildrate ein und
        die Restzeit wäre am Anfang um ein Vielfaches zu hoch.
        """
        try:
            self.gesamt = int(text)
        except ValueError:
            logger.debug('TOTAL unlesbar: %r', text, exc_info=True)
            return False
        self.start = jetzt
        return self._melden('0 / %d frames — starting...' % self.gesamt)

    def _fortschritt(self, text, jetzt):
        if jetzt - self._letzte < self.SPERRE_S:
            return False
        zahlen = self._zahlen(text)
        if not zahlen:
            return False
        aktuell, gesamt = zahlen
        if gesamt <= 0 or aktuell <= 0:
            return False
        self._letzte = jetzt
        bilder_je_s = aktuell / max(jetzt - self.start, 0.1)
        rest = int((gesamt - aktuell) / max(bilder_je_s, 0.01))
        self.job.progress = int((aktuell / gesamt) * self.anteil)
        return self._melden('%s%d / %d frames — %.1f fps, ~%ds left'
                            % (self._vorsatz(), aktuell, gesamt,
                               bilder_je_s, rest))

    def _zahlen(self, text):
        """`50/125` oder `50` — im zweiten Fall gilt die bekannte Gesamtzahl."""
        teile = text.split('/')
        try:
            aktuell = int(teile[0])
            gesamt = int(teile[1]) if len(teile) > 1 else self.gesamt
        except (ValueError, IndexError):
            logger.debug('PROGRESS unlesbar: %r', text, exc_info=True)
            return None
        return aktuell, gesamt

    def _vorsatz(self):
        return '%s: ' % self.name if self.name else ''

    def _melden(self, text):
        self.job.progress_detail = text
        self.job.save()
        return True

    # ------------------------------------------------------------- Startzustand

    def anfangsmeldung(self, status, wobei=''):
        """Auftrag auf 0 % setzen, bevor der Erkenner losläuft.

        `wobei` steht nur in der Wartemeldung („Starting MocapNET v4…") und
        nicht vor jeder Fortschrittszeile — dafür ist `name` da.
        """
        self.job.status = status
        self.job.progress = 0
        self.job.progress_detail = (
            '0 / %d frames' % self.gesamt if self.gesamt
            else 'Starting %s...' % (wobei or self.name or 'detection'))
        self.job.save()
