# -*- coding: utf-8 -*-
"""Bildmodell-Schätzung: die Einzelschätzer laufen im Wrapperpfad (19.09.2026).

`Bildmodellschaetzung._einzeln` importierte `photo_analyzer.analyze` im
`with Wrapperpfad()` und rief es danach auf. `analyze` lädt das
Backend-Modul aber erst beim ersten Aufruf — und da war der Pfad wieder
weg. Alle 20 Kopf- und Körperbilder des Damira-Auftrags standen auf
„the 'package' argument is required to perform a relative import for
'.pymafx_photo'"; SMPLest-X war nicht betroffen, weil es seinen eigenen
Prozess startet. Seitdem bleibt der Pfad für die ganze Schleife.

Sabotage: `with`-Block wieder nur um den Import → `test_der_pfad_steht_
waehrend_des_aufrufs` rot. `Fotobackends.laden` ohne Pfad gibt None
statt des TypeErrors → `test_ohne_pfad_kein_typeerror`.
"""

import os
import sys
import types
import unittest
from pathlib import Path

from core.daten.wrapperpfad import Wrapperpfad
from core.dienste.bildmodellschaetzung import Bildmodellschaetzung


class Ablageattrappe:
    def zuschnitt(self):
        return Path('A:/gibt/es/nicht')

    def schaetzung(self):
        return Path('A:/gibt/es/nicht')


class Jobattrappe:
    bilder = []


class EinzelschaetzerTest(unittest.TestCase):
    def setUp(self):
        # Andere Prüfmodule (`_wrappersuchpfad`) lassen den Pfad dauerhaft
        # stehen — hier beginnt jeder Fall ohne ihn, und am Ende steht er
        # wieder so, wie er war.
        self.pfad = Wrapperpfad.pfad()
        self.vorher = list(sys.path)
        # `settings.WRAPPERS_DIR` schreibt `HumanBodyWeb/../VideoToBVH`, die
        # Prüfhelfer den aufgelösten Pfad — beide meinen denselben Ordner.
        soll = os.path.normcase(os.path.abspath(self.pfad))
        sys.path[:] = [p for p in sys.path if os.path.normcase(os.path.abspath(p)) != soll]
        self.echt = sys.modules.pop('photo_analyzer', None)
        self.addCleanup(self._zurueck)

    def _zurueck(self):
        sys.path[:] = self.vorher
        sys.modules.pop('photo_analyzer', None)
        if self.echt is not None:
            sys.modules['photo_analyzer'] = self.echt

    def test_der_pfad_steht_waehrend_des_aufrufs(self):
        gesehen = []

        def analyze(pfad, backend='mediapipe'):
            gesehen.append(self.pfad in sys.path)
            return {'betas': [0.0] * 10, 'face_shape': [0.0] * 100, 'confidence': 0.9}

        sys.modules['photo_analyzer'] = types.SimpleNamespace(analyze=analyze)
        bild = {'datei': 'kopf.jpg', 'kategorie': 'kopf', 'gewicht': 1.0}
        s = Bildmodellschaetzung(Jobattrappe(), Ablageattrappe(), {})
        s._einzeln([bild], 'pymafx', None, 'gesichtsschaetzung')
        self.assertEqual(gesehen, [True])
        self.assertEqual(len(bild['gesichtsschaetzung']['face_shape']), 100)
        self.assertNotIn('fehler', bild['gesichtsschaetzung'])
        self.assertNotIn(self.pfad, sys.path, 'nach der Schleife ist der Pfad wieder weg')

    def test_ohne_pfad_kein_typeerror(self):
        """`Fotobackends.laden` außerhalb des Pfads: None und eine Warnung, keine Ausnahme."""
        with Wrapperpfad():
            from photo_analyzer import Fotobackends
        sys.modules.pop('pymafx_photo', None)
        self.assertIsNone(Fotobackends.laden('pymafx'))


class MehrbildTest(unittest.TestCase):
    """`Bildmodellmehrbild`: ein Prozess je Schätzer, die letzte JSON-Zeile zählt."""

    def test_befehl_pymafx_ohne_schwelle_smplest_mit(self):
        from core.dienste.bildmodellmehrbild import Bildmodellmehrbild

        b = Bildmodellmehrbild('pymafx').befehl(['a.jpg'])
        self.assertTrue(b[1].endswith('_run_pymafx_bilder.py'), b)
        self.assertEqual(b[2:], ['a.jpg'])
        b = Bildmodellmehrbild('smplest_x', ['--zuversicht', '0.2']).befehl(['a.jpg', 'b.jpg'])
        self.assertTrue(b[1].endswith('_run_smplest_x_bilder.py'), b)
        self.assertEqual(b[2:], ['--zuversicht', '0.2', 'a.jpg', 'b.jpg'])
        self.assertFalse(Bildmodellmehrbild.kann('hmr2'), 'HMR 2.0 läuft je Bild')

    def test_die_letzte_json_zeile_gilt(self):
        from core.dienste.bildmodellmehrbild import Bildmodellmehrbild

        aus = (
            'Lade Modell\n{"bilder": [{"datei": "x"}]}\nWarnung\n'
            '{"bilder": [{"datei": "a.jpg", "betas": [1]}]}\n'
        )
        self.assertEqual(Bildmodellmehrbild.antwort(aus)['bilder'][0]['datei'], 'a.jpg')
        self.assertIsNone(Bildmodellmehrbild.antwort('nur Text'))
