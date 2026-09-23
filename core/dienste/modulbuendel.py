# -*- coding: utf-8 -*-
"""Die ES-Module einer Seite als EINE Datei ausliefern (Szene, BVH Studio).

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

ZWEITE SEITE: BVH STUDIO (22.09.2026)
=====================================
Edgar: „ich weiss nicht, wie du phantasierst — ein refresh immer noch > 10 s!!!",
danach direkt: „warum dauert denn laden von 230 modulen laenger als laden
einer gebuendelten datei???" BVH Studio lud seine ~290 Module bis dahin
GENAUSO einzeln wie die Szene vor dem 10.09. — das Buendel-Verfahren gab es
nur fuer `scene/main.js`. Jetzt je Seite ein Eintrag in `SEITEN`
(Einstiegspunkt, Dateiname/Adresse); `EXTERN` bleibt fuer beide gleich —
BVH Studio traegt `three`/`three/addons/*` als BARE SPECIFIER genau wie die
Szene in seiner eigenen Import-Map (nur auf eine lokale Vendor-Kopie statt
auf ein CDN gemappt, `templates/bvh_studio.html`); esbuild sieht nur den
Specifier-STRING, nicht, wohin die Import-Map ihn aufloest — der Ausschluss
wirkt unveraendert.
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
    """Baut und findet das gebündelte Skript einer Seite."""

    #: Einstiegspunkt je Seite, relativ zum Statik-Ordner — `seite` ist der
    #: Schlüssel hier UND das letzte Wort in Datei-/Adressname
    #: (`scene.js`/`studio.js`).
    EINSTIEGE = {
        'scene': 'viewer/scene/main.js',
        'studio': 'viewer/bvh_studio/index.js',
    }

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
    EXTERN = ('three', 'three/addons/*', 'three-subdivide', '/static/djangobase/*')

    #: Länger darf ein Bündel nicht brauchen. Schlägt es fehl, liefert die
    #: Seite die Einzelmodule — langsamer, aber immer richtig.
    ZEITGRENZE_S = 120

    #: Ein Bündel je Fassung; zwei Anfragen gleichzeitig sollen nicht zwei
    #: Läufe starten.
    _schloss = threading.Lock()

    @classmethod
    def wurzel(cls):
        """Der Statik-Ordner dieses Projekts — die Quelle der Module."""
        return os.path.join(settings.BASE_DIR, 'static')

    @classmethod
    def ablage(cls):
        """Der Ordner mit den fertigen Bündeln."""
        return os.path.join(settings.BASE_DIR, cls.ORDNER)

    @classmethod
    def dateiname(cls, seite, fassung):
        return '%s_%s.js' % (seite, fassung)

    @classmethod
    def adresse(cls, seite, fassung):
        """Die Adresse, unter der die Seite das Bündel lädt."""
        return '/buendel/%s/%s.js' % (fassung, seite)

    @classmethod
    def pfad(cls, seite, fassung):
        return os.path.join(cls.ablage(), cls.dateiname(seite, fassung))

    @classmethod
    def esbuild(cls):
        """Das Bündelwerkzeug, oder None.

        Ohne es gibt es kein Bündel — und das ist kein Fehler, sondern der
        Normalfall auf einem Rechner ohne `npm install`.
        """
        for name in ('esbuild.cmd', 'esbuild.exe', 'esbuild'):
            kandidat = os.path.join(settings.BASE_DIR, 'node_modules', '.bin', name)
            if os.path.isfile(kandidat):
                return kandidat
        return shutil.which('esbuild')

    @classmethod
    def bereit(cls, seite, fassung):
        """Ist das Bündel dieser Seite zu dieser Fassung da? Sonst: bauen.

        Gibt den relativen Pfad zurück, oder None — dann lädt die Seite die
        Einzelmodule wie bisher.
        """
        ziel = cls.pfad(seite, fassung)
        if os.path.isfile(ziel) and os.path.getsize(ziel) > 0:
            return cls.adresse(seite, fassung)
        with cls._schloss:
            # Zweite Prüfung im Schloss: Wer hier wartete, findet die Datei
            # womöglich schon fertig vor.
            if os.path.isfile(ziel) and os.path.getsize(ziel) > 0:
                return cls.adresse(seite, fassung)
            return cls.adresse(seite, fassung) if cls._bauen(seite, ziel) else None

    @classmethod
    def _bauen(cls, seite, ziel):
        werkzeug = cls.esbuild()
        if not werkzeug:
            logger.info(
                'Modulbuendel: esbuild fehlt — die Seite laedt '
                'die Einzelmodule (langsamer, aber richtig)'
            )
            return False
        einstieg = cls.EINSTIEGE[seite]
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        befehl = [
            werkzeug,
            os.path.join(cls.wurzel(), *einstieg.split('/')),
            '--bundle',
            '--format=esm',
            '--outfile=%s' % ziel,
            '--log-level=warning',
        ]
        befehl += ['--external:%s' % e for e in cls.EXTERN]
        try:
            lauf = subprocess.run(
                befehl, capture_output=True, text=True, timeout=cls.ZEITGRENZE_S, cwd=settings.BASE_DIR
            )
        except OSError, subprocess.SubprocessError:
            logger.exception('Modulbuendel: Lauf fehlgeschlagen')
            return False
        if lauf.returncode != 0 or not os.path.isfile(ziel):
            logger.error('Modulbuendel: esbuild meldet %s — %s', lauf.returncode, (lauf.stderr or '')[:500])
            return False
        cls._aufraeumen(seite, os.path.dirname(ziel), os.path.basename(ziel))
        logger.info('Modulbuendel: %s gebaut (%d KB)', os.path.basename(ziel), os.path.getsize(ziel) // 1024)
        return True

    @classmethod
    def _aufraeumen(cls, seite, ordner, behalten):
        """Alte Fassungen DIESER Seite wegräumen.

        Ohne das sammelt sich je Codeänderung ein 760-KB-Bündel an — bei
        einem Arbeitstag mit zwanzig Änderungen 15 MB, die niemand mehr
        zuordnen kann. Der Ordner ist SEITENÜBERGREIFEND (Szene und Studio
        legen ihre Bündel nebeneinander ab, 22.09.2026) — ohne den
        Präfix-Filter hätte der Bau des einen Bündels das andere gleich
        mitgelöscht.
        """
        praefix = seite + '_'
        for name in os.listdir(ordner):
            if name == behalten or not name.endswith('.js') or not name.startswith(praefix):
                continue
            try:
                os.remove(os.path.join(ordner, name))
            except OSError:
                # stumm gewollt: Ein nicht löschbares altes Bündel ist kein
                # Grund, die Seite scheitern zu lassen.
                pass
