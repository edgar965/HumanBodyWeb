# -*- coding: utf-8 -*-
u"""Alle acht BVH-Formate müssen in der Registry stehen.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`formats.py` (504 Zeilen, acht Formatklassen) wurde in das Paket
`formats/` zerlegt — eine Klasse je Datei. Der Importpfad blieb gleich,
aber die Registrierung hängt seither an acht Importzeilen in
`formats/__init__.py`.

**Diese Importe sehen unbenutzt aus.** `Skeleton.__init_subclass__`
trägt jede Unterklasse beim Import in `Skeleton._registry` ein; im
Modul selbst wird der Name danach nirgends verwendet. Ein Import-Fixer,
ein Linter oder ein aufräumender Mensch nimmt so eine Zeile heraus — und
dann fehlt ein Format:

* `Skeleton.detect()` findet es nicht mehr,
* eine BVH-Datei dieses Formats läuft in den Zweig „unbekannt",
* die Animation kommt verdreht heraus, ohne Fehlermeldung.

Deshalb steht an jeder Zeile ein `# noqa: F401`.

WIE WEIT DIESER TEST WIRKLICH TRÄGT (nachgemessen, nicht behauptet)
-------------------------------------------------------------------
Die Probe aufs Exempel — eine Importzeile entfernen — ergab, dass DREI
Stellen jedes Format namentlich nennen:

    humanbody_core/skeleton/formats/__init__.py   (die Registrierung)
    humanbody_core/skeleton/__init__.py           `from .formats import …`
    humanbody_core/__init__.py                    dasselbe eine Ebene höher

Fehlt eines an einer dieser Stellen, bricht der Import mit
`ImportError` ab — das Projekt startet gar nicht mehr. Der Fall „ein
Format verschwindet still" verlangt also, dass jemand an allen drei
Stellen konsequent aufräumt. Möglich ist genau das (ein Linter meldet
alle drei Zeilen als unbenutzt), aber die erste Verteidigungslinie sind
die expliziten Importe, nicht dieser Test.

Er bleibt trotzdem: Die anderen fünf Fälle prüfen, was kein
`ImportError` je bemerkt — dass jede Klasse in einer eigenen Datei
liegt, dass `__all__` und die Registry zusammenpassen, und dass jedes
Format eine EIGENE Zuordnungstabelle trägt statt einer geerbten leeren.

Aufruf:  python manage.py test core.tests.unit.test_skelettformate
"""
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton import formats  # noqa: E402
from humanbody_core.skeleton.skeleton import Skeleton  # noqa: E402


class RegistryTest(SimpleTestCase):
    u"""Was `Skeleton.detect()` kennen muss."""

    #: Die Formate aus dem Paket `formats/` — Kennung: Klassenname.
    AUS_DEM_PAKET = {
        'CMU': 'SkeletonCMU',
        'MIXAMO': 'SkeletonMixamo',
        'MOCAPNET': 'SkeletonMocapNet',
        'AIST': 'SkeletonAIST_SMPL',
        'OPENPOSE': 'SkeletonOpenPose',
        'BANDAI': 'SkeletonBandai',
        'SMPL': 'SkeletonSMPL',
        'MEDIAPIPE': 'SkeletonMediaPipe',
    }

    #: Die zwei, die in `skeleton.py` selbst stehen und nicht im Paket.
    AUS_SKELETON_PY = ('RIGIFY', 'META')

    def test_jedes_format_ist_registriert(self):
        fehlen = [k for k in self.AUS_DEM_PAKET if k not in Skeleton._registry]
        self.assertEqual(fehlen, [],
                         'Fehlende Formate — vermutlich wurde eine Importzeile '
                         'in formats/__init__.py als "unbenutzt" entfernt')

    def test_jede_kennung_zeigt_auf_die_richtige_klasse(self):
        for kennung, klassenname in self.AUS_DEM_PAKET.items():
            self.assertEqual(Skeleton._registry[kennung].__name__, klassenname)

    def test_auch_die_beiden_aus_skeleton_py(self):
        for kennung in self.AUS_SKELETON_PY:
            self.assertIn(kennung, Skeleton._registry)

    def test_jede_klasse_liegt_in_einer_eigenen_datei(self):
        u"""Das war der Zweck der Aufteilung — sonst wächst es zurück."""
        module = {}
        for klassenname in self.AUS_DEM_PAKET.values():
            klasse = getattr(formats, klassenname)
            module.setdefault(klasse.__module__, []).append(klassenname)
        doppelt = {m: n for m, n in module.items() if len(n) > 1}
        self.assertEqual(doppelt, {},
                         'Mehrere Formate in einer Datei: %s' % doppelt)

    def test_das_paket_reicht_alle_namen_durch(self):
        u"""`from .formats import SkeletonCMU` muss weiter tragen."""
        for klassenname in self.AUS_DEM_PAKET.values():
            self.assertTrue(hasattr(formats, klassenname),
                            '%s ist über das Paket nicht erreichbar'
                            % klassenname)
        self.assertEqual(sorted(formats.__all__),
                         sorted(self.AUS_DEM_PAKET.values()),
                         '__all__ und die Registry sind auseinandergelaufen')

    def test_jede_klasse_traegt_ihre_eigene_zuordnung(self):
        u"""Eine geerbte leere Tabelle wäre eine stille Fehlerquelle.

        `BONE_MAP_TO_RIGIFY` muss in der Klasse SELBST stehen, nicht von
        `Skeleton` geerbt sein — sonst ordnet das Format nichts zu und
        die Figur bleibt in Ruhestellung stehen.
        """
        ohne = []
        for klassenname in self.AUS_DEM_PAKET.values():
            klasse = getattr(formats, klassenname)
            if 'BONE_MAP_TO_RIGIFY' not in vars(klasse):
                ohne.append(klassenname)
        self.assertEqual(ohne, [],
                         'Diese Formate haben keine eigene Zuordnungstabelle')
