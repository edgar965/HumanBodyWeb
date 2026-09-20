# -*- coding: utf-8 -*-
u"""Edgars Einteilung der Daz-Garderobe (`G9garderobekategorien`, 20.09.2026).

Edgar: „kannst du Unterteilungen machen, Kategorien wie bei GarmentCode? Plus
Kontextmenü bei jedem Item, mit dem ich das in eine andere Kategorie
verschieben kann." Die Einteilung liegt als JSON neben den eigenen Morphs
(`3DObjects/Genesis9/garderobe_kategorien.json`); hier zeigt `datei()` in
einen Wegwerfordner. Vier Zusagen:

1. Ohne Datei: die Vorgaben (seit 20.09.2026 nachts die GarmentCode-Namen aus
   `G9dazkategorien.REIHENFOLGE`), leere Zuordnung; ein Stueck gehoert zu
   seiner Vorgabe — ohne Daz-Metadaten nach der Art.
2. Verschieben in eine NEUE Kategorie legt sie an (hinten, nach den
   Vorgaben) und ueberlebt das Neuladen.
3. Zurueck in die Vorgabe raeumt den Eintrag weg — und eine eigene Kategorie
   ohne Stueck verschwindet (der Browser zeigt nur besetzte).
4. Ein untauglicher Name (leer, zu lang, Steuerzeichen) wird abgewiesen, ohne
   die Datei anzufassen.

Sabotage: `_geordnet` ohne `name in besetzt` -> Fall 3 rot; `_taugt` ohne
Laengengrenze -> Fall 4 rot.
"""
import json
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.dazkategorien import G9dazkategorien
from Genesis9.garderobekategorien import G9garderobekategorien

VORGABEN = list(G9dazkategorien.REIHENFOLGE)


class GarderobekategorienTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.datei = Path(self.ordner.name) / 'garderobe_kategorien.json'
        self._patch = mock.patch.object(G9garderobekategorien, 'datei',
                                        classmethod(lambda cls: self.datei))
        self._patch.start()
        # Keine Daz-Bibliothek im Test: die Vorgabe kommt aus der Art.
        self._ohne = mock.patch.object(G9dazkategorien, 'metadaten', staticmethod(lambda e: None))
        self._ohne.start()

    def tearDown(self):
        self._ohne.stop()
        self._patch.stop()
        self.ordner.cleanup()

    def test_1_ohne_datei_die_vorgaben(self):
        stand = G9garderobekategorien.laden()
        self.assertEqual(stand, {'kategorien': VORGABEN, 'zuordnung': {}})
        self.assertEqual(G9garderobekategorien.kategorie({'id': 'x', 'art': 'haar'}, stand), 'Haare')
        self.assertEqual(G9garderobekategorien.kategorie({'id': 'x', 'art': 'requisit'}, stand),
                         'Requisiten')
        self.assertEqual(G9garderobekategorien.kategorie({'id': 'x', 'art': 'unbekannt'}, stand),
                         'Oberteile')
        self.assertFalse(self.datei.exists(), 'Lesen darf nichts anlegen')

    def test_2_neue_kategorie_ueberlebt_das_neuladen(self):
        stand = G9garderobekategorien.verschieben('hs_viola_hair_g9', ' Stranghaar ', vorgabe='Haare')
        self.assertEqual(stand['kategorien'], VORGABEN + ['Stranghaar'])
        self.assertEqual(stand['zuordnung'], {'hs_viola_hair_g9': 'Stranghaar'})
        self.assertEqual(G9garderobekategorien.laden(), stand)
        roh = json.loads(self.datei.read_text(encoding='utf-8'))
        self.assertEqual(roh['zuordnung']['hs_viola_hair_g9'], 'Stranghaar')
        self.assertFalse(self.datei.with_suffix('.json.neu').exists(), 'Nachbardatei bleibt liegen')
        eintrag = {'id': 'hs_viola_hair_g9', 'art': 'haar'}
        self.assertEqual(G9garderobekategorien.kategorie(eintrag), 'Stranghaar')

    def test_3_zurueck_in_die_vorgabe_raeumt_auf(self):
        G9garderobekategorien.verschieben('a', 'Fantasy', vorgabe='Hosen')
        G9garderobekategorien.verschieben('b', 'Fantasy', vorgabe='Haare')
        stand = G9garderobekategorien.verschieben('a', 'Hosen', vorgabe='Hosen')
        self.assertNotIn('a', stand['zuordnung'], 'Vorgabe steht nicht in der Zuordnung')
        self.assertIn('Fantasy', stand['kategorien'], 'b liegt noch darin')
        stand = G9garderobekategorien.verschieben('b', 'Haare', vorgabe='Haare')
        self.assertEqual(stand, {'kategorien': VORGABEN, 'zuordnung': {}})
        # In eine Vorgabe verschieben, die nicht die eigene ist: bleibt ein Eintrag.
        stand = G9garderobekategorien.verschieben('a', 'Haare', vorgabe='Hosen')
        self.assertEqual(stand['zuordnung'], {'a': 'Haare'})

    def test_4_untauglicher_name_wird_abgewiesen(self):
        for name in ('', '   ', None, 'x' * 41, 'Zeile\nUmbruch'):
            with self.assertRaises(ValueError, msg=repr(name)):
                G9garderobekategorien.verschieben('a', name, vorgabe='Hosen')
        self.assertFalse(self.datei.exists())
        stand = G9garderobekategorien.verschieben('a', 'x' * 40, vorgabe='Hosen')
        self.assertEqual(stand['zuordnung']['a'], 'x' * 40)
