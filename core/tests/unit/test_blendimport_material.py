# -*- coding: utf-8 -*-
"""Blender-Import: Gewebe der Kleider und Strähnen des Haars kommen mit (Edgar, 08.10.2026) — die Teile ohne Blender.

Edgar zu „cute girl": „Haare sind in Blender viel fein granularer als der Import den du gemacht hast, das Oberteil hat
eine andere Struktur". Gemessen am Shader-Baum der .blend (`mat_dump.py`): die Bluse legt über die Grundnormale eine zweite
Normal-Map-Karte (`ACVI_Detail_Cloth_Cotton3_Normal.dds`, 256 px), die das Mapping 75 × 75 kachelt — das Fischgrät-Gewebe,
das der Import fallen ließ (DDS und nur die erste Normalenkarte). Die Hose kachelt 25 ×. Das Haar ist Hashed-Alpha.

1. Der Exporter erkennt die zweite, gekachelte Normalenkarte (`Blendexport.detailnormale`), legt ein DDS als PNG ab und
   nennt die Wiederholungen (`kachelung`); ohne zweite Karte oder ohne Vector-Math-Knoten gibt es nichts.
2. Das Stück-Material trägt `detailnormalen` und `detail_kachel`; `alpha_schwelle` NUR beim Haar mit Alpha-Bild.
3. Die Kanäle: `Detail Normal Map` als Bild, `Detail Horizontal/Vertical Tiles` und `Alpha Cutoff` als Zahlen — und der
   Leser (`G9material`) bringt sie als `detailkachel_u/v` und `alphaschwelle` wieder heraus (Hin- und Rückweg).

Sabotage-Gegenprobe: in `detailnormale` `< 2` durch `< 1` ersetzen → `test_3` (eine Karte) rot; `alpha_schwelle` ohne
`haar and` → `StueckmaterialTest.test_2` rot; `detail_kachel` aus `animationen` streichen → `MaterialkanaeleTest.test_3`
rot; `Alpha Cutoff` aus `WERTE` → `test_4` rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.material import G9material
from Genesis9.materialkanaele import G9materialkanaele

from core.dienste.blendimportstuecke import Blendimportstuecke


class _Eingaenge:
    """Blenders `inputs`: in Reihenfolge iterierbar und per Name (`.get`, `[…]`) erreichbar."""

    def __init__(self, namen):
        self._namen = dict(namen)

    def __iter__(self):
        return iter(self._namen.values())

    def get(self, name):
        return self._namen.get(name)

    def __getitem__(self, name):
        return self._namen[name]

    def __setitem__(self, name, buchse):
        self._namen[name] = buchse


def _buchse(von=None, wert=None):
    return SimpleNamespace(is_linked=von is not None, links=[SimpleNamespace(from_node=von)] if von is not None else [],
                           default_value=wert)


def _knoten(typ, name, eingaenge=None, **felder):
    return SimpleNamespace(type=typ, name=name, inputs=_Eingaenge(eingaenge or {}), **felder)


class DetailnormaleTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.gespeichert = []
        self.kopien = []
        bpy = ModuleType('bpy')
        bpy.path = SimpleNamespace(abspath=lambda pfad, library=None: pfad)
        bpy.data = SimpleNamespace(images=SimpleNamespace(new=self._neues_bild))
        pfad = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport' / 'blendexport.py'
        with mock.patch.dict(sys.modules, {'bpy': bpy}):
            spec = importlib.util.spec_from_file_location('blendexport_test', pfad)
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
        with mock.patch('os.makedirs'):      # der Exporter legt seinen Zielordner an — hier nicht
            self.exporter = modul.Blendexport('exportziel')

    def _neues_bild(self, name, breite, hoehe, alpha=False, float_buffer=False):
        """Blenders `images.new`: eine Kopie, die ihre Pixel annimmt und sich speichern lässt."""
        kopie = SimpleNamespace(name=name, size=(breite, hoehe), filepath_raw='', file_format='', pixel=None,
                                colorspace_settings=SimpleNamespace(name=''))
        kopie.pixels = SimpleNamespace(foreach_set=lambda werte: setattr(kopie, 'pixel', list(werte)))
        kopie.save = lambda: self.gespeichert.append((kopie.filepath_raw, kopie.file_format, kopie.pixel))
        self.kopien.append(kopie)
        return kopie

    def _bildknoten(self, pfad):
        # Ein 1 × 2-Bild: acht Zahlen RGBA, so wie `pixels.foreach_get` sie liefert.
        bild = SimpleNamespace(filepath=pfad, library=None, size=(1, 2))
        bild.pixels = SimpleNamespace(foreach_get=lambda ziel: ziel.__setitem__(slice(None), [0.25, 0.5, 1.0, 1.0] * 2))
        mapping = _knoten('MAPPING', 'Mapping', {'Vector': _buchse(_knoten('TEX_COORD', 'Koordinate')),
                                                 'Scale': _buchse(wert=(75.0, 75.0, 1.0))})
        return _knoten('TEX_IMAGE', 'Detailbild', {'Vector': _buchse(mapping)}, image=bild)

    def _material(self, bildknoten, zweite_karte=True):
        grund = _knoten('NORMAL_MAP', 'Grund', {'Color': _buchse(_knoten('TEX_IMAGE', 'Grundbild', image=None))})
        detail = _knoten('NORMAL_MAP', 'Detail', {'Color': _buchse(bildknoten)})
        mathe = _knoten('VECT_MATH', 'Summe', {'Vector': _buchse(grund),
                                               'Vector_001': _buchse(detail) if zweite_karte else _buchse()})
        return _knoten('BSDF_PRINCIPLED', 'Principled', {'Normal': _buchse(mathe)})

    def test_1_die_zweite_karte_samt_kachelung_wird_erkannt(self):
        aus = self.exporter.detailnormale(self._material(self._bildknoten('A:/x/detail.png')), 'shirt')
        self.assertEqual(aus['detailnormalen'], os.path.normpath('A:/x/detail.png'))
        self.assertEqual(aus['detail_kachel'], [75.0, 75.0])
        self.assertEqual(self.gespeichert, [], 'ein PNG wird nicht neu geschrieben')

    def test_2_ein_dds_wird_als_png_neben_den_export_gelegt(self):
        aus = self.exporter.detailnormale(self._material(self._bildknoten('A:/x/Cotton3_Normal.dds')), 'cute shirt!')
        self.assertEqual(os.path.basename(aus['detailnormalen']), 'detail_cute_shirt_.png')
        datei, format_, pixel = self.gespeichert[0]
        self.assertEqual((datei, format_), (aus['detailnormalen'], 'PNG'))
        self.assertEqual(pixel, [0.25, 0.5, 1.0, 1.0] * 2, 'die Pixel gehen unverändert in die Kopie')
        self.assertEqual(self.kopien[0].colorspace_settings.name, 'Non-Color', 'Normalenkarte: keine Farbumrechnung')

    def test_3_ohne_zweite_karte_oder_ohne_vector_math_gibt_es_nichts(self):
        eine = self._material(self._bildknoten('A:/x/d.png'), zweite_karte=False)
        self.assertEqual(self.exporter.detailnormale(eine, 's'), {})
        direkt = _knoten('BSDF_PRINCIPLED', 'P', {'Normal': _buchse(_knoten('NORMAL_MAP', 'n'))})
        self.assertEqual(self.exporter.detailnormale(direkt, 's'), {})
        ohne = _knoten('BSDF_PRINCIPLED', 'P', {'Normal': _buchse()})
        self.assertEqual(self.exporter.detailnormale(ohne, 's'), {})

    def test_4_ohne_mapping_gilt_eine_einfache_wiederholung(self):
        bildknoten = _knoten('TEX_IMAGE', 'Detailbild', {'Vector': _buchse()}, image=SimpleNamespace(filepath='A:/x/d.png',
                                                                                                   library=None))
        self.assertEqual(self.exporter.kachelung(bildknoten), [1.0, 1.0])


class StueckmaterialTest(SimpleTestCase):
    databases = set()

    QUELLE = {'farbe': None, 'normalen': 'A:/x/shirt_normal.png', 'detailnormalen': 'A:/x/detail_shirt.png',
              'detail_kachel': [75.0, 75.0], 'alpha': 'A:/x/kein_alpha.png'}

    def _material(self, quelle, haar):
        with mock.patch.object(Blendimportstuecke, 'alphabild', staticmethod(lambda bild, ziel: str(ziel))):
            return Blendimportstuecke.material('k', quelle, Path('ordner'), haar)

    def test_1_das_gewebe_kommt_ins_material(self):
        m = self._material(self.QUELLE, haar=False)
        self.assertEqual(m['detailnormalen'], 'A:/x/detail_shirt.png')
        self.assertEqual(m['detail_kachel'], [75.0, 75.0])

    def test_2_die_alphaschwelle_gibt_es_nur_beim_haar_mit_alphabild(self):
        haar = self._material(self.QUELLE, haar=True)
        kleid = self._material(self.QUELLE, haar=False)
        ohne = self._material({**self.QUELLE, 'alpha': None}, haar=True)
        self.assertEqual(haar['alpha_schwelle'], Blendimportstuecke.HAAR_ALPHA_SCHWELLE)
        self.assertIsNone(kleid['alpha_schwelle'])
        self.assertIsNone(ohne['alpha_schwelle'], 'ohne Alpha-Bild gibt es nichts zu schneiden')


class MaterialkanaeleTest(SimpleTestCase):
    databases = set()

    ANGABEN = {'detailnormalen': '/d.png', 'detail_kachel': [75.0, 25.0], 'alpha_schwelle': 0.18}

    def test_3_die_kanaele_tragen_bild_kachelung_und_schnitt(self):
        extra = G9materialkanaele.extra({'normalen': '/n.png', 'detailnormalen': '/d.png'})
        namen = {k['channel']['id']: k['channel']['image_file'] for k in extra[0]['channels']}
        self.assertEqual(namen, {'Normal Map': '/n.png', 'Detail Normal Map': '/d.png'})
        animationen = G9materialkanaele.animationen('Gruppe', self.ANGABEN, True)
        werte = {a['url'].rsplit('/channels/', 1)[1].rsplit('/value', 1)[0]: a['keys'][0][1] for a in animationen}
        self.assertEqual(werte, {'Detail Horizontal Tiles': 75.0, 'Detail Vertical Tiles': 25.0, 'Alpha Cutoff': 0.18})
        # Ohne Bild keine Kachelung, ohne Alpha-Bild kein Schnitt.
        ohne = G9materialkanaele.animationen('G', {'detail_kachel': [75.0, 75.0], 'alpha_schwelle': 0.18}, False)
        self.assertEqual(ohne, [])

    def test_4_der_leser_bringt_kachelung_und_schnitt_wieder_heraus(self):
        gelesen = {}
        for a in G9materialkanaele.animationen('Gruppe', self.ANGABEN, True):
            gruppe, art, wert = G9material._wert(a)
            gelesen[art] = (gruppe, wert)
        self.assertEqual(gelesen, {'detailkachel_u': ('Gruppe', 75.0), 'detailkachel_v': ('Gruppe', 25.0),
                                   'alphaschwelle': ('Gruppe', 0.18)})
