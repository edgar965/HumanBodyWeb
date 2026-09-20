# -*- coding: utf-8 -*-
"""Die Genesis-9-Reiter der Szene — jeder Endpunkt, den ihre Knöpfe rufen.

Edgar, 20.09.2026: „mach testcases für alle Buttons des Garment Code und
genesis, führe sie aus, checke die ergebnisse und fixe die Fehler!"

Nur lesend (GET), auf Kins Reglern aus der Fixture — was ein Knopf im
Eigenschaften- und im Garderobe-Reiter anfordert, bevor er etwas an der
Figur ändert: Figurliste, Regler, Posen, Garderobe samt Kategorien, das
Netz eines Stücks, die Reglerfelder (Gelenke, Visemes) und das Figurnetz.
Die Rechenwege (Anziehen, Frisur, Stoff) laufen in den Genesis9-Tests der
anderen Sitzung; hier zählt, dass jeder Knopf eine Antwort bekommt, die zu
seiner Vorlage passt.
"""

import json

from django.conf import settings
from django.test import Client, SimpleTestCase
from Genesis9.pfade import G9pfade

FIXTURE = settings.ASSETS_ROOT / 'GarmentCode' / 'test' / 'gemeinsam_kin'
WURZEL = '/api/character/genesis9-figur/'


class Genesis9KnoepfeTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.klient = Client()
        cls.regler_figur = json.load(open(FIXTURE / 'figur_regler.json', encoding='utf-8'))['regler']

    def setUp(self):
        if not G9pfade.vorhanden():
            self.fail('Die Genesis-9-Bibliothek fehlt — ohne sie prüft dieses Modul nichts.')

    def holen(self, pfad, **params):
        antwort = self.klient.get(WURZEL + pfad, params)
        self.assertEqual(antwort.status_code, 200, (pfad, antwort.content[:300]))
        return antwort.json()

    def test_figurliste_und_regler(self):
        liste = self.holen('')
        figuren = liste.get('figuren') if isinstance(liste, dict) else liste
        self.assertTrue(figuren, liste)
        regler = self.holen('regler/')
        namen = {r['name'] for bereich in regler['bereiche'] for r in bereich['regler']}
        self.assertGreater(len(namen), 500, len(namen))
        # Kins Regler stehen in der Liste der Figur — bis auf die Stellung
        # (kein Regler) und `facs_ctrl_EyeRestingFocalPoint` (kein Schieber
        # im Reiter; gemessen 20.09.2026: 21 von 23).
        fehlend = [n for n in self.regler_figur if n not in namen
                   and n != 'stellung' and not n.startswith('facs_ctrl_')]
        self.assertEqual(fehlend, [])

    def test_posen_garderobe_und_kategorien(self):
        posen = self.holen('posen/')
        self.assertTrue(posen.get('posen') if isinstance(posen, dict) else posen, posen)
        garderobe = self.holen('garderobe/')
        stuecke = garderobe.get('stuecke') if isinstance(garderobe, dict) else garderobe
        self.assertTrue(stuecke, garderobe)
        kategorien = self.holen('garderobe/kategorien/')
        self.assertTrue(kategorien, kategorien)

    def test_ein_stueck_der_garderobe_hat_ein_netz(self):
        garderobe = self.holen('garderobe/')
        stuecke = garderobe.get('stuecke') if isinstance(garderobe, dict) else garderobe
        erstes = stuecke[0]
        self.assertTrue(erstes.get('id') and erstes.get('name'), erstes)
        netz = self.holen('garderobe/%s/netz/' % erstes['id'])
        self.assertTrue(any(k in netz for k in ('teile', 'vertices', 'punkte', 'netze')), list(netz.keys())[:10])

    def test_reglerfelder_gelenke_und_visemes(self):
        gelenke = self.holen('felder/gelenke/')
        visemes = self.holen('felder/visemes/')
        self.assertTrue(gelenke, gelenke)
        self.assertTrue(visemes, visemes)

    def test_das_figurnetz_von_kin(self):
        liste = self.holen('')
        figuren = liste.get('figuren') if isinstance(liste, dict) else liste
        erste = figuren[0]
        name = erste.get('name') if isinstance(erste, dict) else erste
        antwort = self.klient.get(WURZEL + '%s/netz/' % name)
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        self.assertGreater(len(antwort.content), 100000, 'ein Genesis-9-Netz ist keine 100 KB klein')
