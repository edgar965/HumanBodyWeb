# -*- coding: utf-8 -*-
u"""Ein Testpaket, das nur laeuft, wenn es ausdruecklich gemeint ist.

WARUM (Edgar, 09.09.2026: „baue die automatische Testsuite um, alles was
mehr als 1 s dauert soll in die Longrunner hinein, das dauert mir alles zu
lange")
=====================================================================
Die Regel stand bis dahin bei 5 Sekunden je Modul und nur fuer EIN Paket
(`core/tests/longrunner`). Bei 1 Sekunde trifft sie zwei weitere Pakete,
und die lassen sich nicht verschieben:

    core/tests/automated      31,8 s   sammelt `djangobase.grundtests`
    core/tests/performance    26,5 s   sammelt `djangobase.leistungstests`

Beide bestehen aus einer Datei mit `from djangobase.X import *`; die
Testklassen selbst liegen im geteilten Paket, das in sechs Projekten
haengt (`A:/shared/djangoBase/CLAUDE.md`) — dort eine Ausnahme fuer
DIESES Projekt einzubauen wirkte sofort in allen. Und sie ins
longrunner-Paket zu schieben, haette die Reiter „Grundabsicherung" und
„Ladezeiten" in Hilfe -> Tests auf 0 Faelle gesetzt.

Deshalb entscheidet jedes der drei Pakete selbst, ueber das
`load_tests`-Protokoll: Steht sein Name im Aufruf, sammelt es; sonst
liefert es eine LEERE Suite.

GEMESSEN (09.09.2026, `manage.py test --durations 3000`, je Modul
aufsummiert): Der Sammellauf brauchte 113 s fuer 1.667 Faelle. Die 21
Module ueber 1 Sekunde trugen davon 108,6 s — die beiden Pakete oben
allein 58,3 s, also die Haelfte der Wartezeit bei zusammen ACHT Faellen.

EINE LEERE SUITE WIRD GEMELDET, NICHT VERSCHWIEGEN. Ein Paket, das still
nichts liefert, sieht aus wie ein Paket ohne Tests
(`~/.claude/rules/analysewerkzeuge.md`: ein Pruefer, der nichts findet und
Entwarnung meldet, ist der teuerste).
"""
import logging
import os
import sys
import unittest

from django.conf import settings

logger = logging.getLogger('core')


class Nurgemeint:
    u"""Der Waechter vor einem langsamen Testpaket."""

    #: Damit laesst sich JEDES dieser Pakete einschalten — etwa in einem
    #: naechtlichen Lauf, der wirklich alles fahren soll.
    SCHALTER = 'LONGRUNNER'

    #: Was als „gesetzt" gilt. `'0'` und `'nein'` bewusst nicht.
    WAHR = ('1', 'true', 'ja')

    def __init__(self, marke, ordner, dauer=None):
        #: Das Wort, an dem ein ausdruecklicher Aufruf zu erkennen ist —
        #: der letzte Teil des Paketpfads (`core.tests.automated`).
        self.marke = marke
        self.ordner = ordner
        #: Grobe Laufzeit fuer die Meldung; None laesst sie weg.
        self.dauer = dauer

    def angefordert(self, argumente=None, umgebung=None):
        u"""Ist dieses Paket ausdruecklich gemeint?

        Mit Parametern, damit ein Test die Entscheidung ohne echtes
        `sys.argv` nachrechnen kann — sonst waere gerade sie die einzige,
        die niemand prueft.

        `argumente[1:]`: `argv[0]` ist der Programmpfad. Laege das Projekt
        in einem Ordner mit „automated" im Namen, waere sonst jeder Lauf
        ein ausdruecklicher.
        """
        argumente = sys.argv if argumente is None else argumente
        umgebung = os.environ if umgebung is None else umgebung
        if str(umgebung.get(self.SCHALTER, '')).strip() in self.WAHR:
            return True
        return any(self.marke in str(a) for a in argumente[1:])

    def module(self):
        return [n for n in sorted(os.listdir(self.ordner))
                if n.startswith('test_') and n.endswith('.py')]

    def sammeln(self, loader, pattern):
        u"""Das `load_tests`-Protokoll: Wir sammeln selbst — oder eben nicht."""
        if not self.angefordert():
            logger.info(
                '%s uebersprungen (%d Module%s). Zum Fahren: manage.py test '
                'core.tests.%s  oder  %s=1', self.marke, len(self.module()),
                ', rund %s' % self.dauer if self.dauer else '',
                self.marke, self.SCHALTER)
            return unittest.TestSuite()
        return loader.discover(self.ordner, pattern=pattern or 'test*.py',
                               top_level_dir=str(settings.BASE_DIR))

    # `top_level_dir` IST DER UNTERSCHIED ZWISCHEN LAUFEN UND SCHEITERN
    # =================================================================
    # Ohne ihn nimmt `discover` den Startordner als oberste Ebene und
    # importiert `test_mhpfade` als TOP-LEVEL-Modul — ohne Paketkontext.
    # Jeder Import ueber die Paketgrenze bricht dann ab:
    #
    #     from ..unit._humanbodypfad import Humanbodypfad
    #     ImportError: attempted relative import with no known parent package
    #
    # Gefunden am 09.09.2026 beim Verschieben der 1-Sekunden-Module: Es
    # traf zehn, und ZWEI davon (`test_mhpfade`, `test_uma_gegenprobe_lauf`)
    # lagen schon seit dem 08.09.2026 hier und waren die ganze Zeit
    # unlaufbar. Aufgefallen ist es nur, weil dieser Lauf ausdruecklich
    # gefahren wurde — im Sammellauf ist das Paket stumm, und ein Modul,
    # das der Loader nicht importieren kann, wird als `_FailedTest`
    # gemeldet. Steht es in einem Paket, das nie laeuft, sieht es niemand.
    #
    # `settings.BASE_DIR` statt einer `.parent`-Kette: Nach einem
    # Dateiumzug zeigte die Kette stumm eine Ebene daneben
    # (`~/.claude/rules/projektpfade.md`).
