# -*- coding: utf-8 -*-
u"""Die 230 ES-Module der Szene-Seite als EINE Datei ausliefern.

BEFUND (Edgar, 10.09.2026): „laden dauert doch noch immer länger als 10 s!!"

WAS GEMESSEN WURDE
==================
Im echten Vordergrund (Playwright mit abgeschaltetem Occlusion-Tracking —
ein verdecktes Chrome-Fenster gilt sonst als `hidden` und zeichnet nicht,
dort ist jede Messung wertlos):

    HTML da            55 ms        329 ms
    erstes Bild     1.344 ms      2.164 ms
    229 Module      3.300 ms      5.996 ms     <-- der groesste Posten
    Figur sichtbar  5.956 ms      8.025 ms
    alles fertig   15.374 ms     10.807 ms

Der Grund ist nicht die Datenmenge, sondern die ANZAHL. Jede Anfrage an
diesen Server kostet 10-12 ms Grundaufwand, unabhaengig vom Inhalt — ein
662-Byte-JSON genauso wie eine 9-KB-Moduldatei. Und der Server arbeitet
Anfragen NACHEINANDER ab; gemessen an einem Endpunkt, der 560 ms rechnet:

    1 Anfrage         560 ms
    2 gleichzeitig  1.131 ms   (nacheinander waeren es 1.119 — kein Gewinn)
    6 gleichzeitig  6.308 ms   (nacheinander waeren es 3.358 — doppelt so teuer)

Django fuehrt synchrone Views unter ASGI mit `thread_sensitive=True` aus,
also alle im selben Faden. Daphne laesst sich nicht abschalten, `core/
consumers.py` braucht WebSockets. 230 Module sind damit rund 2,8 Sekunden,
bevor die erste Zeile eigener Code laeuft.

WARUM KEIN HINTERGRUNDPROZESS
=============================
Der uebliche Weg waere ein Beobachter, der bei jeder Dateiaenderung neu
baut. Der hat eine stille Falle: Laeuft er nicht, aendert man Code und
sieht im Browser nichts davon — ohne jeden Hinweis. Bei zwei parallelen
Sitzungen an diesem Projekt ist das keine Theorie.

Deshalb baut der Server selbst, und zwar genau dann, wenn es noetig ist:
Der Dateiname traegt die FASSUNG (`Fassungsstatik.fassung()`, die juengste
Aenderungszeit im Statik-Baum). Ist die Datei zur aktuellen Fassung da,
wird sie ausgeliefert; sonst wird sie gebaut. Eine Aenderung an irgendeiner
JS-Datei aendert die Fassung und damit den Namen — ein veralteter Stand
kann gar nicht erst ausgeliefert werden. Das ist dieselbe Ueberlegung wie
in `~/.claude/rules/artefakte-benennen.md`.

Kosten: der erste Aufruf nach einer Aenderung dauert rund eine Sekunde
laenger (Node starten und buendeln), jeder weitere gar nichts. Gemessen
mit laufendem Node: 84-422 ms je Neubau, davon 786 ms allein der
Node-Start, wenn er kalt ist.
"""

import logging
import os
import shutil
import subprocess
import threading

from django.conf import settings

__all__ = ['Modulbuendel']

logger = logging.getLogger('core')


class Modulbuendel:
    u"""Baut und findet das gebündelte Skript der Szene-Seite."""

    #: Einstiegspunkt, relativ zum Statik-Ordner.
    EINSTIEG = 'viewer/scene/main.js'

    #: Wohin die fertigen Bündel kommen.
    #:
    #: AUSSERHALB von `static/`, und das ist der Kern: Die Fassung ist die
    #: jüngste Änderungszeit im Statik-Baum. Läge das Bündel dort, änderte
    #: sein Bau die Fassung — und die neue Fassung verlangte ein neues
    #: Bündel. Gemessen, bevor es hier lag: Die Seite lieferte nacheinander
    #: `scene_1789043552.js` und `scene_1789043571.js` aus, also zwei Bauten
    #: für eine Änderung. Ausgeliefert wird über eine eigene Route
    #: (`core/api/buendel.py`), die die Fassung genauso im Pfad trägt.
    ORDNER = '_buendel'

    #: Was NICHT mit hineingebündelt wird. `three` kommt aus dem CDN und
    #: steht in der Import-Map der Seite; die djangoBase-Module liegen
    #: außerhalb dieses Projekts und haben ihre eigene Fassung.
    EXTERN = ('three', 'three/addons/*', 'three-subdivide',
              '/static/djangobase/*')

    #: Länger darf ein Bündel nicht brauchen. Schlägt es fehl, liefert die
    #: Seite die Einzelmodule — langsamer, aber immer richtig.
    ZEITGRENZE_S = 120

    #: Ein Bündel je Fassung; zwei Anfragen gleichzeitig sollen nicht zwei
    #: Läufe starten.
    _schloss = threading.Lock()

    @classmethod
    def wurzel(cls):
        u"""Der Statik-Ordner dieses Projekts — die Quelle der Module."""
        return os.path.join(settings.BASE_DIR, 'static')

    @classmethod
    def ablage(cls):
        u"""Der Ordner mit den fertigen Bündeln."""
        return os.path.join(settings.BASE_DIR, cls.ORDNER)

    @classmethod
    def dateiname(cls, fassung):
        return 'scene_%s.js' % fassung

    @classmethod
    def adresse(cls, fassung):
        u"""Die Adresse, unter der die Seite das Bündel lädt."""
        return '/buendel/%s/scene.js' % fassung

    @classmethod
    def pfad(cls, fassung):
        return os.path.join(cls.ablage(), cls.dateiname(fassung))

    @classmethod
    def esbuild(cls):
        u"""Das Bündelwerkzeug, oder None.

        Ohne es gibt es kein Bündel — und das ist kein Fehler, sondern der
        Normalfall auf einem Rechner ohne `npm install`.
        """
        for name in ('esbuild.cmd', 'esbuild.exe', 'esbuild'):
            kandidat = os.path.join(settings.BASE_DIR, 'node_modules',
                                    '.bin', name)
            if os.path.isfile(kandidat):
                return kandidat
        return shutil.which('esbuild')

    @classmethod
    def bereit(cls, fassung):
        u"""Ist das Bündel zu dieser Fassung da? Sonst: bauen.

        Gibt den relativen Pfad zurück, oder None — dann lädt die Seite die
        Einzelmodule wie bisher.
        """
        ziel = cls.pfad(fassung)
        if os.path.isfile(ziel) and os.path.getsize(ziel) > 0:
            return cls.adresse(fassung)
        with cls._schloss:
            # Zweite Prüfung im Schloss: Wer hier wartete, findet die Datei
            # womöglich schon fertig vor.
            if os.path.isfile(ziel) and os.path.getsize(ziel) > 0:
                return cls.adresse(fassung)
            return cls.adresse(fassung) if cls._bauen(ziel) else None

    @classmethod
    def _bauen(cls, ziel):
        werkzeug = cls.esbuild()
        if not werkzeug:
            logger.info('Modulbuendel: esbuild fehlt — die Szene-Seite laedt '
                        'die Einzelmodule (langsamer, aber richtig)')
            return False
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        befehl = [werkzeug,
                  os.path.join(cls.wurzel(), *cls.EINSTIEG.split('/')),
                  '--bundle', '--format=esm', '--outfile=%s' % ziel,
                  '--log-level=warning']
        befehl += ['--external:%s' % e for e in cls.EXTERN]
        try:
            lauf = subprocess.run(befehl, capture_output=True, text=True,
                                  timeout=cls.ZEITGRENZE_S,
                                  cwd=settings.BASE_DIR)
        except (OSError, subprocess.SubprocessError):
            logger.exception('Modulbuendel: Lauf fehlgeschlagen')
            return False
        if lauf.returncode != 0 or not os.path.isfile(ziel):
            logger.error('Modulbuendel: esbuild meldet %s — %s',
                         lauf.returncode, (lauf.stderr or '')[:500])
            return False
        cls._aufraeumen(os.path.dirname(ziel), os.path.basename(ziel))
        logger.info('Modulbuendel: %s gebaut (%d KB)', os.path.basename(ziel),
                    os.path.getsize(ziel) // 1024)
        return True

    @classmethod
    def _aufraeumen(cls, ordner, behalten):
        u"""Alte Fassungen wegräumen.

        Ohne das sammelt sich je Codeänderung ein 760-KB-Bündel an — bei
        einem Arbeitstag mit zwanzig Änderungen 15 MB, die niemand mehr
        zuordnen kann.
        """
        for name in os.listdir(ordner):
            if name == behalten or not name.endswith('.js'):
                continue
            try:
                os.remove(os.path.join(ordner, name))
            except OSError:
                # stumm gewollt: Ein nicht löschbares altes Bündel ist kein
                # Grund, die Seite scheitern zu lassen.
                pass
