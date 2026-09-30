# -*- coding: utf-8 -*-
u"""„Haar – Generisch" mischt auch auf einer HumanBody-Figur (30.09.2026).

Edgar: „auf einer HumanBody soll das haar genau so gemischt werden". Bis dahin trug eine
HumanBody-Figur nur die Hauptsorte (`G9haargenerisch.aufloesen`). Jetzt baut `G9haarmischbau`
jede Sorte über den Bauweg der Figurart — auf HumanBody `G9kleidhumanbody.antwort` — und dünnt
jedes Teil mit demselben Eingriff aus. Geprüft mit Attrappen (keine Bibliothek, kein Netz): die
Weiche im Endpunkt, der Eingriff je Teil, die Kappe nur von der Hauptsorte, die Figurart in der
Antwort. Dazu, was nur im Quelltext steht: Stranghaar fällt auf HumanBody nicht mehr weg, die
Formachsen wirken dort, und der Browser verdeckt die Haut unter einem Daz-Stück auch dort.
"""
from pathlib import Path
from unittest import mock

import numpy as np
from asgiref.sync import async_to_sync
from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from core.dienste.g9haarmischbau import G9haarmischbau


def netz(punkte=8, art=None):
    u"""Zwei getrennte Quadrate — zwei Inseln, wie zwei Strähnen."""
    p = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
                  [5, 0, 0], [6, 0, 0], [6, 1, 0], [5, 1, 0]], dtype=np.float64)[:punkte]
    return {'punkte': p, 'dreiecke': np.array([[0, 1, 2], [0, 2, 3], [4, 5, 6], [4, 6, 7]]),
            'normalen': np.zeros_like(p), 'uv': np.zeros((len(p), 2)), 'gruppen': [],
            'haut': None, 'art': art, 'name': 'geometry', 'stufen': 0}


class Attrappenbau:
    u"""Wie `G9kleidhumanbody.antwort`: je Teil `vor_antwort(nummer, netz)`, dann die Antwort."""

    def __init__(self, teile_je_sorte, figurart='humanbody', scheitert=()):
        self.teile_je_sorte = teile_je_sorte
        self.figurart = figurart
        self.scheitert = set(scheitert)
        self.aufrufe = []

    def __call__(self, kennung, eintrag, rumpf, vor_antwort=None):
        from django.http import JsonResponse
        self.aufrufe.append((kennung, dict(rumpf.get('regler_stueck') or {})))
        if kennung in self.scheitert:
            return JsonResponse({'fehler': 'kaputt'}, status=500)
        teile = []
        for nummer, n in enumerate(self.teile_je_sorte[kennung]):
            n = vor_antwort(nummer, n) if vor_antwort else n
            if n is not None:
                teile.append({'name': n['name'], 'vertex_count': len(n['punkte']), 'art': n.get('art')})
        return {'kennung': kennung, 'teile': teile, 'boden': 0.0, 'stufen': 1,
                'figurart': self.figurart, 'innen': [], 'aussen': []}


MISCHUNG = [('toulouse_hair', 0.5, {'achse.laenge': 1.0}), ('g9_base_dforce_pixie_hair', 0.5, {})]


class Mischbau(SimpleTestCase):
    databases = set()

    def bauen(self, bau, mischung=MISCHUNG):
        with mock.patch('core.dienste.g9haarmischbau.G9haargenerisch.mischung', return_value=mischung), \
                mock.patch('core.dienste.g9haarmischbau.G9garderobe.eintrag', return_value={}):
            return G9haarmischbau.antwort({'figurart': 'humanbody', 'regler_stueck': {}}, bau)

    def test_1_humanbody_figurart_geht_in_die_antwort(self):
        bau = Attrappenbau({'toulouse_hair': [netz()], 'g9_base_dforce_pixie_hair': [netz()]})
        aus = self.bauen(bau)
        self.assertEqual(aus['figurart'], 'humanbody')
        self.assertEqual(aus['kennung'], 'haar_generisch')
        self.assertEqual([t['sorte'] for t in aus['teile']], ['toulouse_hair', 'g9_base_dforce_pixie_hair'])
        # Die Regler gehen OHNE Präfix an die Sorte — auch die Formachse.
        self.assertEqual(bau.aufrufe[0], ('toulouse_hair', {'achse.laenge': 1.0}))

    def test_2_die_kappe_kommt_nur_von_der_hauptsorte(self):
        bau = Attrappenbau({'toulouse_hair': [netz(art='kappe'), netz()],
                            'g9_base_dforce_pixie_hair': [netz(art='kappe'), netz()]})
        aus = self.bauen(bau)
        kappen = [t['sorte'] for t in aus['teile'] if t['art'] == 'kappe']
        self.assertEqual(kappen, ['toulouse_hair'])

    def test_3_eine_kaputte_beimischung_kostet_nicht_die_frisur(self):
        bau = Attrappenbau({'toulouse_hair': [netz()], 'g9_base_dforce_pixie_hair': [netz()]},
                           scheitert={'g9_base_dforce_pixie_hair'})
        aus = self.bauen(bau)
        self.assertEqual({t['sorte'] for t in aus['teile']}, {'toulouse_hair'})

    def test_4_genesis_antwort_traegt_keine_figurart(self):
        bau = Attrappenbau({'toulouse_hair': [netz()], 'g9_base_dforce_pixie_hair': [netz()]},
                           figurart=None)
        self.assertNotIn('figurart', self.bauen(bau))

    def test_9_die_attrappe_hat_die_signatur_beider_bauwege(self):
        u"""`~/.claude/rules/attrappen-signatur.md`: Die Attrappe prüft den Aufrufer, nicht das
        Original — beide echten Bauwege müssen annehmen, was der Mischbau übergibt."""
        import inspect

        from core.api.g9garderobe import G9garderobeapi
        from core.api.g9kleidhumanbody import G9kleidhumanbody

        def namen(f):
            return set(inspect.signature(f).parameters) - {'self', 'cls'}

        attrappe = namen(Attrappenbau.__call__)
        for echt in (G9kleidhumanbody.antwort, G9garderobeapi._kleid):
            self.assertEqual(namen(echt), attrappe, echt.__qualname__)


class Weiche(SimpleTestCase):
    databases = set()

    def anfrage(self, rumpf):
        return RequestFactory().post('/api/character/genesis9-figur/garderobe/haar_generisch/netz/',
                                     data=rumpf, content_type='application/json')

    def test_5_haar_generisch_auf_humanbody_mischt_ueber_den_humanbody_weg(self):
        from core.api.g9garderobe import G9garderobeapi
        from core.api.g9kleidhumanbody import G9kleidhumanbody
        with mock.patch('core.api.g9garderobe.G9pfade.vorhanden', return_value=True), \
                mock.patch('core.api.g9garderobe.G9antworten.liefern', return_value='antwort') as liefern, \
                mock.patch('core.api.g9garderobe.G9haarmischbau.antwort', return_value={}) as misch:
            aus = async_to_sync(G9garderobeapi.kleidnetz)(
                self.anfrage('{"figurart": "humanbody", "geschlecht": "female"}'), 'haar_generisch')
            self.assertEqual(aus, 'antwort')
            art, name, _rumpf, bauen = liefern.call_args[0][:4]
            self.assertEqual((art, name), ('kleidhb', 'haar_generisch'))
            self.assertEqual(liefern.call_args[1]['eintrag'], G9haarmischbau.KENNZEICHEN)
            bauen()
        # `assertEqual`, nicht `assertIs`: Jeder Zugriff auf eine Klassenmethode baut ein neues
        # gebundenes Objekt; gleich sind sie, wenn Funktion und Klasse gleich sind.
        self.assertEqual(misch.call_args[0][1], G9kleidhumanbody.antwort)

    def test_6_auf_genesis_bleibt_der_genesis_weg(self):
        from core.api.g9garderobe import G9garderobeapi
        with mock.patch('core.api.g9garderobe.G9pfade.vorhanden', return_value=True), \
                mock.patch('core.api.g9garderobe.G9antworten.liefern', return_value='antwort') as liefern, \
                mock.patch('core.api.g9garderobe.G9haarmischbau.antwort', return_value={}) as misch:
            async_to_sync(G9garderobeapi.kleidnetz)(self.anfrage('{}'), 'haar_generisch')
            self.assertEqual(liefern.call_args[0][0], 'kleid')
            liefern.call_args[0][3]()
        self.assertEqual(misch.call_args[0][1], G9garderobeapi._kleid)


class Quelltext(SimpleTestCase):
    u"""Was nur im Quelltext steht — ein Lauf bräuchte die Daz-Bibliothek und eine HumanBody-Figur."""
    databases = set()

    def lesen(self, *teile):
        return Path(settings.BASE_DIR, *teile).read_text(encoding='utf-8')

    def test_7_humanbody_weg_laesst_stranghaar_nicht_mehr_weg(self):
        api = self.lesen('core', 'api', 'g9kleidhumanbody.py')
        self.assertNotIn("!= 'strang']", api)                       # der alte Filter
        self.assertIn('G9hbstrang.uebertragen(traeger, punkte)', api)
        self.assertIn('def antwort(cls, kennung, eintrag, rumpf, vor_antwort=None)', api)
        self.assertIn('G9haarachsen.anwenden(kennung, teile, roh,', api)
        self.assertIn("'art': eintrag.get('art')", api)

    def test_8_browser_verdeckt_die_haut_unter_daz_stuecken_auf_humanbody(self):
        js = self.lesen('static', 'viewer', 'charakter', 'genesis9', 'dazkleidung.js')
        self.assertIn('netz.userData.art = daten.art', js)
        self.assertIn('Hautverdeckung.planen(inst)', js)
        # Nicht über das Stückereignis: dort hört auch `GarmentcodeAbsatz` und setzte den Absatz
        # einer Daz-Sandale zurück.
        self.assertNotIn('Stueckereignis.melden', js)
