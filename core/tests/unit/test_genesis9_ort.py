# -*- coding: utf-8 -*-
"""Alle eigenen Genesis-9-Daten liegen an EINEM Ort: `3DObjects/models/Genesis9` (08.10.2026).

Edgar: „Code an einer Stelle (3DObjects/models/Genesis mit dem neuen Code mergen)". Bis dahin schrieb der Code nach
`3DObjects/Genesis9`, Skripte mit `HB_OBJECTS_ROOT=…/models` nach `3DObjects/models/Genesis9` — zwei Orte, in jedem die
Hälfte (Bibliothek 2.822 gegen 116 Dateien, Eigenmorphe 124 gegen 68). Jetzt rechnet `G9pfade.eigene_daten()` den Ort,
und jede Ablage hängt daran.

1. `eigene_daten()` ist `<objekte>/models/Genesis9`, die eigene Bibliothek liegt darunter.
2. Jede Ablage (Eigenmorphe, Kleidmorphe, Kleidtexturen, Kleidtransparenz, Haarachsen, Haarzusatz, Papierkorb, Kategorien,
   Pflege) liegt darunter — keine zweite Fassung des Pfads im Code.
3. `G9pfade.daten()` bleibt der Daz-Datenordner (`<Bibliothek>/data`): die neue Methode hat ihn nicht überschrieben (am
   08.10.2026 geschehen: der Server meldete „Daz-Bibliothek fehlt").
4. Im Quelltext steht `objekte() / 'Genesis9'` nirgends mehr.

Sabotage-Gegenprobe: in `eigene_daten` `'models'` weglassen → Fall 1 und 2 rot; die Methode wieder `daten` nennen → Fall 3 rot;
in `eigenmorphe.py` `G9pfade.objekte() / 'Genesis9'` zurückschreiben → Fall 2 und 4 rot.
"""

import inspect
import os
import unittest
from pathlib import Path
from unittest import mock

from Genesis9.eigenmorphe import G9eigenmorphe
from Genesis9.garderobekategorien import G9garderobekategorien
from Genesis9.garderobepflege import G9garderobepflege
from Genesis9.haarachsen import G9haarachsen
from Genesis9.haarzusatz import G9haarzusatz
from Genesis9.kleidmorphe import G9kleidmorphe
from Genesis9.kleidtexturen import G9kleidtexturen
from Genesis9.kleidtransparenz import G9kleidtransparenz
from Genesis9.pfade import G9pfade
from Genesis9.stueckpapierkorb import G9stueckpapierkorb


class Genesis9OrtTest(unittest.TestCase):
    #: Ein Ort, den es nicht gibt: hier wird nichts gelesen und nichts geschrieben.
    WURZEL = Path(__file__).resolve().parent / '_ort_attrappe'

    def setUp(self):
        umgebung = mock.patch.dict(os.environ, {'HB_OBJECTS_ROOT': str(self.WURZEL)})
        umgebung.start()
        self.addCleanup(umgebung.stop)
        os.environ.pop(G9pfade.UMGEBUNG_EIGENE, None)
        self.ort = self.WURZEL / 'models' / 'Genesis9'

    def _ablagen(self):
        return {
            'Eigenmorphe': G9eigenmorphe.ordner(), 'Kleidmorphe': G9kleidmorphe.ordner(),
            'Kleidtexturen': G9kleidtexturen.ordner(), 'Kleidtransparenz': G9kleidtransparenz.ordner(),
            'Haarachsen': G9haarachsen.ordner(), 'Haarzusatz': G9haarzusatz.ordner(),
            'Papierkorb': G9stueckpapierkorb.ordner(), 'Kategorien': G9garderobekategorien.datei(),
            'Pflege': G9garderobepflege.datei(), 'Bibliothek': G9pfade.eigene(),
        }

    def test_1_der_ort_ist_models_genesis9_und_die_bibliothek_liegt_darunter(self):
        self.assertEqual(G9pfade.eigene_daten(), self.ort)
        self.assertEqual(G9pfade.eigene(), self.ort / 'bibliothek')

    def test_2_jede_ablage_liegt_unter_dem_einen_ort(self):
        for name, pfad in self._ablagen().items():
            with self.subTest(ablage=name):
                self.assertTrue(pfad.is_relative_to(self.ort), '%s liegt woanders: %s' % (name, pfad))

    def test_3_daten_bleibt_der_daz_datenordner(self):
        self.assertEqual(G9pfade.daten(), G9pfade.bibliothek() / 'data')
        self.assertNotIn('models', G9pfade.daten().relative_to(G9pfade.bibliothek()).parts)

    def test_4_im_quelltext_steht_der_zweite_ort_nirgends_mehr(self):
        quelle = Path(inspect.getfile(G9pfade)).resolve().parent
        self.assertTrue((quelle / 'eigenmorphe.py').is_file(), quelle)
        treffer = [p.name for p in sorted(quelle.glob('*.py'))
                   if "objekte() / 'Genesis9'" in p.read_text(encoding='utf-8')]
        self.assertEqual(treffer, [], 'diese Module bauen den alten Ort noch selbst')
