# -*- coding: utf-8 -*-
"""ProjektTemp — die EINE Stelle für Zwischendateien.

WARUM (Review 13.08.2026)
------------------------
Zwei Gründe, und der erste ist eine Projektregel mit Vorgeschichte:

1. **Nichts nach System-Temp.** Sechs Stellen benutzten
   `tempfile.NamedTemporaryFile()` bzw. `tempfile.mkdtemp()` ohne `dir=` und
   schrieben damit nach `C:\\Users\\…\\AppData\\Local\\Temp`. In diesem Projekt
   ist das ausdrücklich verboten — es hat einmal rund 100 GB Datenmüll auf C:
   hinterlassen. Zwischendateien gehören ins Projektverzeichnis, wo man sie
   sieht und wo Platz ist.

2. **Aufräumen, das auch beim Abbruch greift.** Die Video-Endpunkte hängen ihre
   Löschaufrufe an `response._resource_closers`. Das läuft, wenn die Antwort
   fertig gesendet wurde. Bricht der Browser mitten im Hochladen von 500 MB
   Einzelbildern ab, wird die Antwort NIE fertig — und das Verzeichnis bleibt
   für immer liegen. Kein `finally` kann das abdecken, denn der Abbruch passiert
   außerhalb. Deshalb kehrt hier ein Hausmeister: Bei jedem Anlegen werden
   Reste aufgeräumt, die älter sind als `MAX_ALTER_H`.

WAS DIESE KLASSE NICHT TUT
--------------------------
Sie ersetzt nicht `AtomarSchreiber`. Der legt seine Nebendatei bewusst NEBEN
die Zieldatei (damit `os.replace` auf demselben Laufwerk bleibt) — das ist eine
andere Aufgabe.
"""
import logging
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


class ProjektTemp:
    """Zwischendateien unter `<MEDIA_ROOT>/tmp` statt in System-Temp."""

    #: Reste, die älter sind, werden beim nächsten Anlegen entfernt. 24 Stunden
    #: sind großzügig: Ein Video-Export dauert Minuten, kein Tag.
    MAX_ALTER_H = 24

    #: Wie oft der Hausmeister höchstens läuft. GEMESSEN (15.08.2026) an einem
    #: echten Verzeichnis: `iterdir()` samt `stat()` je Eintrag kostet
    #:      100 Einträge   1,1 ms
    #:    2.000 Einträge  19,9 ms
    #:   10.000 Einträge 138,8 ms
    #: Er lief bei JEDEM `datei()`/`ordner()`; bei viel Betrieb innerhalb eines
    #: Tages zahlt das jede Zwischendatei mit. Fünf Minuten Abstand genügen —
    #: die Grenze ist ohnehin 24 Stunden.
    MIN_ABSTAND_S = 300
    _letzter_lauf = 0.0

    @classmethod
    def verzeichnis(cls):
        """Das Basisverzeichnis (wird angelegt, wenn es fehlt)."""
        p = Path(settings.MEDIA_ROOT) / 'tmp'
        p.mkdir(parents=True, exist_ok=True)
        return p

    # ------------------------------------------------------------------ anlegen

    @classmethod
    def datei(cls, suffix='', prefix='hb_'):
        """Pfad einer neuen, leeren Datei. Der Aufrufer löscht sie — oder der
        Hausmeister tut es später."""
        basis = cls.verzeichnis()
        cls.hausmeister()
        f = tempfile.NamedTemporaryFile(dir=str(basis), suffix=suffix,
                                        prefix=prefix, delete=False)
        f.close()
        return Path(f.name)

    @classmethod
    def ordner(cls, prefix='hb_'):
        """Pfad eines neuen, leeren Verzeichnisses."""
        basis = cls.verzeichnis()
        cls.hausmeister()
        return Path(tempfile.mkdtemp(dir=str(basis), prefix=prefix))

    @classmethod
    @contextmanager
    def wegwerfordner(cls, prefix='hb_'):
        """`with ProjektTemp.wegwerfordner() as ordner:` — wie
        `tempfile.TemporaryDirectory()`, aber im Projekt.

        WARUM ES DEN GIBT (17.08.2026): Vier Stellen der Oberflächen-Testsuite
        benutzten `tempfile.TemporaryDirectory()`. Das schreibt auf C: (verboten)
        UND liegt ausserhalb der Wurzeln, die `SafePath.fuer_studio_projekte()`
        zulässt — `studio_project_save` antwortete dort mit 403, und **48 von
        127 Tests waren seit dem 12.08.2026 rot**, ohne dass jemand hinsah.

        `MEDIA_ROOT/tmp` erfüllt beides: Es ist im Projekt und eine erlaubte
        Wurzel. Aufgeräumt wird auch nach einer Ausnahme.
        """
        ordner = cls.ordner(prefix=prefix)
        try:
            yield ordner
        finally:
            cls.weg(ordner)

    # ---------------------------------------------------------------- aufräumen

    @classmethod
    def weg(cls, *pfade):
        """Datei(en) oder Verzeichnis(se) entfernen — ohne zu klagen.

        Für den `finally`-Zweig gedacht: Was schon weg ist, ist in Ordnung."""
        for p in pfade:
            if not p:
                continue
            p = Path(p)
            try:
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink(missing_ok=True)
            except OSError as e:
                logger.warning('ProjektTemp: %s nicht entfernbar: %s', p, e)

    @classmethod
    def hausmeister(cls, max_alter_h=None, erzwingen=False):
        """Reste entfernen, die älter sind als `max_alter_h`.

        Läuft bei jedem Anlegen mit, aber höchstens alle `MIN_ABSTAND_S`
        Sekunden (siehe die Messung dort) — `erzwingen=True` übergeht das; so
        ruft `apps.ready()` ihn einmal beim Start. Das deckt den Fall ab, dass
        wochenlang keine neue Zwischendatei entsteht und der Müll deshalb
        liegen bleibt.

        Der Fall, den nur der Hausmeister abdeckt: Der Browser bricht das
        Hochladen ab, die Antwort wird nie fertig, und der an sie gehängte
        Löschaufruf läuft deshalb nie."""
        jetzt = time.time()
        if not erzwingen and (jetzt - cls._letzter_lauf) < cls.MIN_ABSTAND_S:
            return 0
        cls._letzter_lauf = jetzt
        grenze = time.time() - (max_alter_h or cls.MAX_ALTER_H) * 3600
        try:
            eintraege = list(Path(settings.MEDIA_ROOT).joinpath('tmp').iterdir())
        # stumm gewollt: Gibt es das Verzeichnis noch nicht, ist nichts
        # aufzuräumen — der Hausmeister läuft beim nächsten Anlegen erneut.
        except OSError:
            return 0
        entfernt = 0
        for p in eintraege:
            try:
                if p.stat().st_mtime >= grenze:
                    continue
            # stumm gewollt: Der Hausmeister laeuft ueber fremde Eintraege;
            # einer, der gerade verschwindet oder gesperrt ist, wird beim
            # naechsten Lauf wieder betrachtet.
            except OSError:
                continue
            cls.weg(p)
            entfernt += 1
        if entfernt:
            logger.info('ProjektTemp: %d alte Reste entfernt (älter als %d h)',
                        entfernt, max_alter_h or cls.MAX_ALTER_H)
        return entfernt
