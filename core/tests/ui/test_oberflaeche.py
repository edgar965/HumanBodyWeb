# -*- coding: utf-8 -*-
"""Die Oberflächenfälle als reguläre Django-Tests.

    „fixe alles, stelle auch die oberflächen suite und api usw um" (Edgar,
    17.08.2026), nach: „Halte dich an die djangoBase test implementierung und
    baue nichts neues, leite nur ab"

WAS SICH ÄNDERT
===============
Die 127 Fälle in `tests/` liefen über einen EIGENEN Läufer: eine eigene API
(`/api/tests/run/`), eine eigene Seite (`/tests/`) und eigenes JavaScript. Damit
standen sie außerhalb von `manage.py test` — und außerhalb von allem, was
djangoBase mitbringt: Hilfe → Tests, Laufzeit-Historie, Trend, Deckungsprüfung,
Sammelläufe je Art.

Diese Datei ist der Adapter: Aus jeder `TestCategory` wird eine
`django.test.TestCase`-Klasse, aus jedem Fall eine Testmethode. Kein neuer
Rahmen — ab hier ist es Djangos Rahmen, und die Fälle selbst bleiben unverändert.

WIE DIE FÄLLE DEN SERVER ERREICHEN
==================================
`tests/kanal.py` schaltet um: im Testlauf `django.test.Client` (in-process,
Testdatenbank), außerhalb `urllib` an den laufenden Server. Der Fall selbst ruft
weiter `Netzruf.senden(...)` und merkt nichts davon.

WARUM DIE FÄLLE HIER NICHT EINZELN AUFGEZÄHLT SIND
==================================================
Sie stehen in `tests/*.py` — 127 an der Zahl, in 16 Kategorien. Eine Liste hier
wäre eine zweite Wahrheit, die beim ersten neuen Fall veraltet. Django findet die
erzeugten Klassen über die Discovery genauso wie handgeschriebene.
"""

import tempfile

from django.conf import settings
import unittest
from pathlib import Path

from django.test import TestCase, override_settings

from tests import ALL_CATEGORIES
from tests.kanal import ClientKanal, Kanal


#: Wegwerf-Medienordner für den ganzen Lauf.
#:
#: WARUM (28.08.2026, gemessen): In `media/scene_objects/` lagen 2.782
#: Einträge, davon 1.374 mit dem Präfix `pytest_` — Rückstände aus
#: Testläufen, mitten in den echten Mediendaten. Die Bundle-Fälle luden über
#: das Netz an den laufenden Server hoch und landeten damit zwangsläufig
#: dort. Seit sie durch den Kanal gehen, läuft der Upload in-process, und
#: `MEDIA_ROOT` lässt sich umlenken.
#:
#: Das Verzeichnis bleibt für die Dauer des Prozesses stehen und wird von
#: Python selbst geräumt — ein `rmtree` im `tearDown` würde Dateien löschen,
#: die ein noch laufender Fall gerade schreibt.
#: `dir=` ist Pflicht (Befund `lehren-treue`, 29.08.2026): Ohne ihn
#: schreibt `TemporaryDirectory` nach `C:\…\AppData\Local\Temp`, und
#: genau so sind in diesem Projekt einmal rund 100 GB Datenmüll
#: entstanden. `ProjektTemp` geht hier nicht: Es legt unter
#: `MEDIA_ROOT/tmp` ab, und MEDIA_ROOT ist genau das, was hier erst
#: erzeugt wird.
_TEMPBASIS = Path(settings.BASE_DIR).parent / 'ProjektTemp'
_TEMPBASIS.mkdir(exist_ok=True)
_MEDIEN = tempfile.TemporaryDirectory(prefix='hb-ui-medien-',
                                      dir=str(_TEMPBASIS))


@override_settings(MEDIA_ROOT=Path(_MEDIEN.name))
class Oberflaechenfall(TestCase):
    """Basis: schaltet den Kanal auf den Testclient und wieder zurück."""

    #: Wird je Kategorie gesetzt (siehe unten).
    KATEGORIE = None

    def setUp(self):
        super().setUp()
        self._vorher = Kanal.setzen(ClientKanal(self.client))
        self.addCleanup(Kanal.setzen, self._vorher)

    def pruefen(self, fall):
        """Einen Fall fahren und sein Ergebnis als Zusicherung auswerten."""
        ergebnis = fall.run()
        if ergebnis['error']:
            self.fail('%s: %s' % (fall.name, ergebnis['error']))
        self.assertTrue(ergebnis['ok'],
                        '%s: %s' % (fall.name, ergebnis['detail']))


def _methode(fall):
    """Eine Testmethode, die genau diesen Fall fährt."""
    def pruefung(self):
        self.pruefen(fall)
    pruefung.__name__ = 'test_%s' % fall.fn.__name__.replace('test_', '')
    pruefung.__doc__ = fall.description or fall.name
    return pruefung


def _klasse(kategorie):
    """Aus einer `TestCategory` eine `TestCase`-Klasse bauen."""
    inhalt = {'KATEGORIE': kategorie,
              '__doc__': '%s — %s' % (kategorie.name, kategorie.description)}
    for fall in kategorie.cases():
        methode = _methode(fall)
        inhalt[methode.__name__] = methode
    return type(kategorie.__name__, (Oberflaechenfall,), inhalt)


#: Je Kategorie eine Klasse im Modul-Namensraum — Djangos Discovery findet sie
#: darüber. `globals()` ist hier der Punkt: Eine Klasse, die nur in einer Liste
#: steht, wird nicht gefunden.
for _kategorie in ALL_CATEGORIES:
    globals()[_kategorie.__name__] = _klasse(_kategorie)

#: Aufräumen, damit die Schleifenvariable nicht als Modulname stehen bleibt.
del _kategorie


class AdapterTest(unittest.TestCase):
    """Der Adapter selbst — er darf keinen Fall verlieren."""

    def test_jede_kategorie_hat_eine_klasse(self):
        for kategorie in ALL_CATEGORIES:
            self.assertIn(kategorie.__name__, globals(),
                          'Kategorie %s fehlt' % kategorie.__name__)

    def test_jeder_fall_hat_eine_methode(self):
        fehlend = []
        for kategorie in ALL_CATEGORIES:
            klasse = globals()[kategorie.__name__]
            for fall in kategorie.cases():
                name = 'test_%s' % fall.fn.__name__.replace('test_', '')
                if not hasattr(klasse, name):
                    fehlend.append('%s.%s' % (kategorie.__name__, name))
        self.assertEqual(fehlend, [], 'Verlorene Fälle: %s' % fehlend)

    def test_die_zahl_der_faelle_bleibt_sichtbar(self):
        """Die Gesamtzahl steht im Bericht — sinkt sie, ist etwas verschwunden."""
        anzahl = sum(len(k.cases()) for k in ALL_CATEGORIES)
        self.assertGreaterEqual(anzahl, 120,
                                'Nur %d Fälle gefunden' % anzahl)
