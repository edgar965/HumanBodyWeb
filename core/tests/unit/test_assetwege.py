# -*- coding: utf-8 -*-
u"""Die drei Baeume unter `Assets/` sind erreichbar — und zwar SO, wie der
Code sie anspricht (07.09.2026).

WARUM (Edgar: „verschiebe auch die alle nach A:\\3DTools\\Assets")
==================================================================
`assetCreator` und `PhotoToTexture` lagen bis zum 07.09.2026 unter
`HumanBody/`, `GarmentCode` seit dem Vormittag unter `Assets/`. Ein
Importweg, der nach einem Umzug ins Leere zeigt, faellt NICHT beim
Serverstart auf: Alle drei werden erst im Rumpf einer Methode geholt
(schwere Abhaengigkeiten, teils andere Umgebung). Der Fehler kommt beim
ersten echten Lauf — beim Anziehen eines Kleidungsstuecks, beim Backen
einer Textur.

DER GEFUNDENE FALL: `PhotoToTexture` IST EIN PAKET
==================================================
`core/dienste/texturbacken.py` legte den ORDNER in den `sys.path` und
holte `from bake_texture import bake_with_backend`. Seit `bake_texture`
seine Hilfsklasse relativ zieht (`from .uvkarte import Uvkarte`), wirft
das „attempted relative import with no known parent package" — der Weg
war also schon vor dem Umzug kaputt und ist es beim Umzug geblieben.
Gefunden hat es nicht das Lesen, sondern der Versuch, den Import nach
dem Verschieben einmal wirklich auszufuehren.

Deshalb prueft dieser Fall den ganzen Weg und nicht nur, ob die Datei da
liegt: Ein Dateitest waere in genau diesem Fall gruen geblieben.
"""
import importlib
import unittest

from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()
Humanbodypfad.assets()


class AssetsLiegenDaTest(SimpleTestCase):
    u"""Die Ordner selbst."""

    databases = []

    #: Was unter `Assets/` liegen muss, und woran man es erkennt.
    ORDNER = (('assetCreator', 'GarmentFitter/__init__.py'),
              ('PhotoToTexture', 'bake_texture.py'),
              ('GarmentCode', 'anziehen.py'))

    def test_jeder_baum_liegt_unter_assets(self):
        from pathlib import Path
        wurzel = Path(str(settings.ASSETS_ROOT))
        fehlt = ['%s/%s' % (ordner, probe) for ordner, probe in self.ORDNER
                 if not (wurzel / ordner / probe).is_file()]
        self.assertEqual(fehlt, [], 'Nicht unter Assets/: %s' % fehlt)

    def test_der_suchpfad_kennt_beide_ebenen(self):
        u"""`Assets/` fuer `from GarmentCode…`, `Assets/assetCreator/` fuer
        `from GarmentFitter…` — die Importe im Code lauten verschieden.
        """
        import sys
        assets = str(settings.ASSETS_ROOT)
        self.assertIn(assets, sys.path)
        self.assertIn(str(settings.ASSETS_ROOT / 'assetCreator'), sys.path)


class ImportwegeTest(SimpleTestCase):
    u"""Die Importe, die der Code wirklich schreibt."""

    databases = []

    #: (Modul, Name) — genau die Schreibweisen aus dem Produktivcode.
    WEGE = (('GarmentFitter', 'fit_garment'),
            ('GarmentFitter.fitter', '_compute_vertex_normals'),
            ('GarmentFitter.obj_io', 'ObjIo'),
            ('assetCreator.GarmentFitter.smpl_library.objleser', 'Objleser'),
            ('UMA', 'Garderobe'),
            ('UMA.formregler', 'Formregler'))

    def test_jeder_weg_traegt(self):
        kaputt = []
        for modul, name in self.WEGE:
            try:
                if not hasattr(importlib.import_module(modul), name):
                    kaputt.append('%s hat kein %s' % (modul, name))
            except Exception as fehler:               # noqa: BLE001
                kaputt.append('%s: %s: %s'
                              % (modul, type(fehler).__name__, fehler))
        self.assertEqual(kaputt, [], '; '.join(kaputt))

    def test_photototexture_nur_als_paket(self):
        u"""Der Fall vom 07.09.2026, in beide Richtungen.

        `PhotoToTexture.bake_texture` traegt; `bake_texture` allein darf
        es NICHT tun — sonst waere die Gegenprobe stumpf und der Test
        haette den Fehler gar nicht finden koennen.
        """
        try:
            import cv2                                # noqa: F401
        except ImportError:                            # pragma: no cover
            raise unittest.SkipTest('cv2 fehlt in dieser Umgebung')
        modul = importlib.import_module('PhotoToTexture.bake_texture')
        self.assertTrue(hasattr(modul, 'bake_with_backend'))

        import sys
        ordner = str(settings.ASSETS_ROOT / 'PhotoToTexture')
        sys.path.insert(0, ordner)
        for name in ('bake_texture', 'PhotoToTexture.bake_texture'):
            sys.modules.pop(name, None)
        try:
            with self.assertRaises(ImportError):
                importlib.import_module('bake_texture')
        finally:
            if ordner in sys.path:
                sys.path.remove(ordner)
            sys.modules.pop('bake_texture', None)
