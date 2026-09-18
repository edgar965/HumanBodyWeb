# -*- coding: utf-8 -*-
u"""Das Laden einer Genesis-9-Figur (18.09.2026 nachts, Edgar: „die performance
ist ja sehr schlecht … mehr als 1 minute", „erst mit geringer auflösung, dann
asynchron mit höherer"):

1. `Netzstufenwahl.aus_anfrage`: `?stufen=0..3` gilt und schlaegt den Keks —
   damit holt der Browser den Kaefig zuerst (`genesis9aufbau.js`).
2. `Netzantwort.hautgewichte(kompakt=True)`: uint16-Spalten, uint8-Gewichte,
   `kodierung: 'u16u8'`; die Gewichte kommen auf 1/255 genau zurueck.
3. `G9kollision.baum`/`naechste`: der unbalancierte Baum findet DIESELBEN
   Nachbarn wie scipys Vorgabe (auf Kunstpunkten; gemessen war er 40-mal
   schneller); `hinaus` mit durchgereichtem Baum hebt wie ohne.
4. `G9posen._art`: Formpresets (`preset_shape`) nur unter `Characters`,
   Ausdruecke aus `Expressions`, Toon-Posen als Pose; `_lesen` liest den
   Reglerwert eines Formpresets.

Sabotage-Gegenproben: `aus_anfrage` vor `aus_cookies` vertauschen -> Fall 1
rot; `* 255.0` in `hautgewichte` weg -> Fall 2 rot; `balanced_tree=False`
in `baum` auf True (mit compact) aendert Fall 3 nicht (gleiche Nachbarn —
das ist der Punkt), `workers` weg auch nicht: Fall 3 prueft Gleichheit, die
Zeit steht in `ProjektTemp/g9_kollision_messung.py`.
"""
import base64
from pathlib import Path

import numpy as np
from django.test import RequestFactory, SimpleTestCase
from scipy.spatial import cKDTree

from core.daten.netzantwort import Netzantwort
from core.dienste.netzstufenwahl import Netzstufenwahl
from Genesis9.dson import G9dson
from Genesis9.kollision import G9kollision
from Genesis9.posen import G9posen


class Ladezeit(SimpleTestCase):

    databases = set()

    def test_1_stufe_aus_der_anfrage_schlaegt_den_keks(self):
        for get, soll in (({}, None), ({'stufen': '0'}, 0), ({'stufen': '2'}, 2),
                          ({'stufen': '3'}, 3), ({'stufen': '4'}, None),
                          ({'stufen': 'x'}, None)):
            self.assertEqual(Netzstufenwahl.aus_anfrage(get), soll, get)
        gesehen = []

        def ansicht(request):
            gesehen.append(Netzstufenwahl.gewaehlt())
            return 'antwort'

        anfrage = RequestFactory().get('/api/character/genesis9-figur/x/netz/',
                                       {'stufen': '0'})
        anfrage.COOKIES['netzstufen'] = '3'
        Netzstufenwahl(ansicht)(anfrage)
        anfrage = RequestFactory().get('/api/character/genesis9-figur/x/netz/')
        anfrage.COOKIES['netzstufen'] = '3'
        Netzstufenwahl(ansicht)(anfrage)
        self.assertEqual(gesehen, [0, 3])

    def test_2_hautgewichte_kompakt(self):
        haut = {'knochen': ['a', 'b'],
                'index': np.array([[0, 1, 0, 0], [1, 0, 0, 0]]),
                'gewicht': np.array([[0.6, 0.4, 0, 0], [1.0, 0, 0, 0]])}
        k = Netzantwort.hautgewichte(haut, kompakt=True)
        self.assertEqual(k['kodierung'], 'u16u8')
        spalten = np.frombuffer(base64.b64decode(k['skin_indices']), dtype=np.uint16)
        gewicht = np.frombuffer(base64.b64decode(k['skin_weights']), dtype=np.uint8)
        self.assertEqual(list(spalten), [0, 1, 0, 0, 1, 0, 0, 0])
        np.testing.assert_allclose(gewicht / 255.0, [0.6, 0.4, 0, 0, 1, 0, 0, 0],
                                   atol=1 / 255)
        self.assertNotIn('kodierung', Netzantwort.hautgewichte(haut))

    def test_3_unbalancierter_baum_gleiche_nachbarn(self):
        zufall = np.random.default_rng(7)
        koerper = zufall.normal(size=(4000, 3))
        kleid = koerper[:300] + zufall.normal(scale=0.002, size=(300, 3))
        _w, soll = cKDTree(koerper).query(kleid, k=1)
        _w, ist = G9kollision.naechste(G9kollision.baum(koerper), kleid)
        self.assertEqual(list(ist), list(soll))
        normalen = np.tile([0.0, 0.0, 1.0], (len(koerper), 1))
        innen = koerper[:50] - [0, 0, 0.005]           # 5 mm unter der Flaeche
        ohne = G9kollision.hinaus(innen, koerper, normalen)
        mit = G9kollision.hinaus(innen, koerper, normalen,
                                 baum=G9kollision.baum(koerper))
        np.testing.assert_allclose(ohne, mit)
        self.assertEqual(G9kollision.innen(mit, koerper, normalen), 0)

    def test_4_formpresets_ausdruecke_toon(self):
        art = G9posen._art
        chars = Path('People/Genesis 9/Characters/P3D/x.duf')
        self.assertEqual(art('preset_shape', 'charakter', chars), 'form')
        self.assertIsNone(art('preset_shape', None,
                              Path('People/Genesis 9/Poses/x.duf')))
        self.assertEqual(art('preset_pose', 'charakter',
                             Path('People/Genesis 9/Characters/P3D/Expressions/x.duf')),
                         'ausdruck')
        self.assertIsNone(art('preset_pose', 'charakter', chars))
        self.assertEqual(art('preset_pose', 'ausdruck',
                             Path('People/Genesis 9/Expressions/x.duf')), 'ausdruck')
        self.assertEqual(art('preset_pose', None,
                             Path('People/Genesis 9 Toon/Poses/x.duf')), 'pose')
        self.assertIsNone(art('preset_material', None, chars))
        doc = G9dson('f.duf', {'scene': {'animations': [
            {'url': 'name://@selection#P3DUrsula_body_bs_Body:?value/value',
             'keys': [[0, 1]]},
            {'url': 'name://@selection#P3DUrsula_head_bs_Head:?value/value',
             'keys': [[0, 0]]}]}})
        knochen, regler = G9posen._lesen(doc)
        self.assertEqual((knochen, regler), ({}, {'P3DUrsula_body_bs_Body': 1.0}))
