# -*- coding: utf-8 -*-
"""Musterablage und Objdatei — Namensprüfung, drei Dateien, Indexe ab 1.

WARUM (17.08.2026)
=================
`pattern_save` war 99 Zeilen und schrieb in die Kleidungsbibliothek unter
`HumanBody/data/garment_library/` — also in Produktivdaten. Ungedeckt war dabei
beides, was wirklich weh tut:

* **Die Namensprüfung.** Der Name wird zu einem Ordnernamen. Ein `..` oder ein
  `/` darin legt Dateien außerhalb der Bibliothek ab.
* **Die OBJ-Indexe.** Wavefront zählt Flächen ab EINS. Ohne das `+1` liest
  Blender die Datei teils gar nicht, teils mit verschobenem Netz — und das fällt
  erst auf, wenn jemand das Kleidungsstück öffnet.

Geschrieben wird hier NIE in die echte Bibliothek: `override_settings` zeigt auf
einen Ordner unter `media/tmp/`.
"""

import json

import numpy as np
from django.test import SimpleTestCase, override_settings

from core.api.musterablage import Musterablage
from core.daten.objdatei import Objdatei


class NamenspruefungTest(SimpleTestCase):

    def einwand(self, **rumpf):
        rumpf.setdefault('pattern', {'panels': [{'name': 'vorn'}]})
        return Musterablage(rumpf).fehler()

    def test_name_ist_pflicht(self):
        self.assertEqual(self.einwand(name='  '), 'Name is required')

    def test_pfadausbruch_wird_abgelehnt(self):
        for boese in ('../../etc', 'a/b', 'a\\b', '..'):
            self.assertEqual(self.einwand(name=boese), 'Invalid name', boese)

    def test_muster_braucht_flaechen(self):
        self.assertEqual(Musterablage({'name': 'x', 'pattern': {}}).fehler(),
                         'Pattern with panels is required')
        self.assertEqual(Musterablage({'name': 'x'}).fehler(),
                         'Pattern with panels is required')

    def test_gueltige_eingabe_hat_keinen_einwand(self):
        self.assertIsNone(self.einwand(name='mein Rock'))

    def test_kategorie_wird_kleingeschrieben(self):
        self.assertEqual(Musterablage({'category': 'Tops'}).kategorie, 'tops')


class ObjdateiTest(SimpleTestCase):

    def zeilen(self):
        punkte = np.array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0], [6.0, 7.0, 8.0]])
        dreiecke = np.array([[0, 1, 2]])
        return list(Objdatei(punkte, dreiecke, kopfzeile='Probe').zeilen())

    def test_flaechen_zaehlen_ab_eins(self):
        """`f 0 1 2` wäre kaputt — OBJ ist 1-basiert."""
        self.assertEqual(self.zeilen()[-1], 'f 1 2 3')

    def test_punkte_mit_sechs_stellen(self):
        self.assertEqual(self.zeilen()[1], 'v 0.000000 1.000000 2.000000')

    def test_kopfzeile_ist_ein_kommentar(self):
        self.assertEqual(self.zeilen()[0], '# Probe')


class AblegenTest(SimpleTestCase):

    def setUp(self):
        from django.conf import settings
        from pathlib import Path
        self.wurzel = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'mustertest'
        umgebung = override_settings(
            HUMANBODY_GARMENT_LIBRARY_DIR=str(self.wurzel))
        umgebung.enable()
        self.addCleanup(umgebung.disable)

    def ablegen(self):
        muster = {'panels': [{'name': 'vorn'}]}
        ablage = Musterablage({'name': 'probe', 'category': 'Tops',
                               'pattern': muster, 'color': [1, 0, 0],
                               'roughness': 0.5, 'metalness': 0.1})
        ergebnis = {'vertices': np.zeros((3, 3), dtype=np.float32),
                    'faces': np.array([[0, 1, 2]])}
        return ablage, ablage.ablegen(ergebnis)

    def test_kennung_ist_kategorie_und_name(self):
        _, kennung = self.ablegen()
        self.assertEqual(kennung, 'tops/probe')

    def test_drei_dateien_liegen_im_ordner(self):
        ablage, _ = self.ablegen()
        from pathlib import Path
        ordner = Path(ablage.ordner())
        for datei in ('garment.obj', 'specification.json', 'garment.json'):
            self.assertTrue((ordner / datei).is_file(), datei)

    def test_muster_bleibt_bearbeitbar(self):
        """Ohne `specification.json` kann der Entwurf das Stück nie mehr öffnen."""
        ablage, _ = self.ablegen()
        from pathlib import Path
        gelesen = json.loads(
            (Path(ablage.ordner()) / 'specification.json').read_text(
                encoding='utf-8'))
        self.assertEqual(gelesen['panels'][0]['name'], 'vorn')

    def test_beschreibung_traegt_die_werkstoffwerte(self):
        ablage, _ = self.ablegen()
        beschreibung = ablage.beschreibung()
        self.assertEqual(beschreibung['color'], [1, 0, 0])
        self.assertEqual(beschreibung['roughness'], 0.5)
        self.assertEqual(beschreibung['metalness'], 0.1)
        self.assertEqual(beschreibung['mesh_file'], 'garment.obj')
