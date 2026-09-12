# -*- coding: utf-8 -*-
u"""Bvhablage — Bildzahl aus dem Kopf, Pfad nur in der Bibliothek.

WARUM (12.09.2026, Befund `testdeckung`): `Bvhablage` liegt auf drei
Arbeitswegen (Bibliothek, Bearbeitung, Retarget) und ist die EINE Stelle
für eine Pfadprüfung, die sicherheitsrelevant ist — am 15.08.2026 konnten
zwei Endpunkte jede `.bvh` des Rechners überschreiben. Kein Test nannte die
Klasse. Hier steht:

1. `frames_lesen` liest `Frames:` aus dem Kopf und antwortet 0, wenn die
   Datei fehlt oder die Zahl keine ist — nie mit einer Ausnahme.
2. `pfad_pruefen` gibt einen Pfad in der Bibliothek zurück und `None` für
   alles außerhalb, auch für `..`-Wege und für die eingestellten
   Studio-Ordner (BEWUSST nicht `SafePath.fuer_bvh()`, siehe Docstring).

Die Umleitung greift nachweislich: `wurzel()` liegt im Testordner, nicht
unter `3DObjects` (Regel `test-isolation`).

Aufruf: python manage.py test core.tests.unit.test_bvhablage
"""
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.bvhablage import Bvhablage
from ._pruefablage import Pruefablage


class BvhablageTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        ablage = Pruefablage.ordner('bvhablage_')
        self.basis = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        self.bvh = self.basis / 'bvh'
        self.kategorie = self.bvh / 'Probe'
        self.kategorie.mkdir(parents=True)
        # Die Einstellung zeigt wie im Betrieb auf EINE Kategorie.
        umschaltung = override_settings(HUMANBODY_BVH_DIR=str(self.kategorie))
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)

    def _bvh(self, name, kopf):
        pfad = self.kategorie / name
        pfad.write_text(kopf, encoding='utf-8')
        return pfad

    # -- Umleitung ------------------------------------------------------------

    def test_die_umleitung_greift(self):
        self.assertEqual(Bvhablage.wurzel(), self.bvh.resolve())

    # -- Bildzahl --------------------------------------------------------------

    def test_frames_aus_dem_kopf(self):
        pfad = self._bvh('a.bvh',
                         'HIERARCHY\nMOTION\nFrames: 120\nFrame Time: 0.0333\n')
        self.assertEqual(Bvhablage.frames_lesen(pfad), 120)

    def test_frames_ohne_zeile_und_ohne_datei(self):
        pfad = self._bvh('leer.bvh', 'HIERARCHY\nMOTION\n')
        self.assertEqual(Bvhablage.frames_lesen(pfad), 0)
        self.assertEqual(Bvhablage.frames_lesen(self.kategorie / 'fehlt.bvh'), 0)

    def test_frames_keine_zahl(self):
        pfad = self._bvh('kaputt.bvh', 'MOTION\nFrames: viele\n')
        self.assertEqual(Bvhablage.frames_lesen(pfad), 0)

    # -- Pfadprüfung -----------------------------------------------------------

    def test_pfad_in_der_bibliothek(self):
        pfad = self._bvh('walk.bvh', 'HIERARCHY\n')
        self.assertEqual(Bvhablage.pfad_pruefen(str(pfad)), pfad.resolve())
        # Auch eine andere Kategorie unter derselben Wurzel.
        andere = self.bvh / 'Andere' / 'x.bvh'
        self.assertEqual(Bvhablage.pfad_pruefen(str(andere)), andere.resolve())

    def test_pfad_ausserhalb_wird_abgelehnt(self):
        self.assertIsNone(Bvhablage.pfad_pruefen(str(self.basis / 'daneben.bvh')))
        hinauf = self.kategorie / '..' / '..' / 'x.bvh'
        self.assertIsNone(Bvhablage.pfad_pruefen(str(hinauf)))
        self.assertIsNone(Bvhablage.pfad_pruefen(''))
        self.assertIsNone(Bvhablage.pfad_pruefen(None))

    def test_eingestellte_studio_ordner_zaehlen_hier_nicht(self):
        # `SafePath.fuer_bvh()` ließe MEDIA_ROOT zu; die Bibliotheksverwaltung
        # löscht und verschiebt und darf das nur in der Bibliothek.
        medien = self.basis / 'media'
        medien.mkdir()
        with override_settings(MEDIA_ROOT=str(medien)):
            self.assertIsNone(Bvhablage.pfad_pruefen(str(medien / 'x.bvh')))
