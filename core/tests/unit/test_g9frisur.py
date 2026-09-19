# -*- coding: utf-8 -*-
u"""HumanBody-Frisur auf dem Genesis-9-Kopf (`core/dienste/g9frisur.py`).

Edgar, 19.09.2026: „bei Genesis sehe ich nicht alle Assets die ich bei
HumanBody sehe, z.B. Haar. mach das, teste auch ob das Haar von HumanBody /
MakeHuman auf Genesis fittet." Gemessen (`_wegwerf/mess_haar_genesis.py`):
Genesis-Kopf 18,4 x 16,4 x 20,9 cm gegen HumanBody 17,4 x 14,5 x 18,8 — nur
verschoben stecken 25 % der Haarpunkte im Schaedel, achsweise skaliert 1,4 %,
mit dem Heben aus der Haut 0. Die Zahlen hier sind Kunstkoepfe; die Regel
(achsweise Skala um Scheitel und Kastenmitte, `head` traegt alles) ist das,
was geprueft wird.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste import g9frisur
from core.dienste.g9frisur import G9frisur


class _Netz:
    def __init__(self, *_a, **_k):
        pass

    def koerperflaeche(self):
        # Eine flache "Kopfhaut" bei y = 1.5, Normale nach oben — was darunter
        # liegt, wird gehoben.
        x, z = np.meshgrid(np.linspace(-0.2, 0.2, 9), np.linspace(-0.2, 0.2, 9))
        p = np.column_stack([x.ravel(), np.full(x.size, 1.5), z.ravel()])
        n = np.tile([0.0, 1.0, 0.0], (len(p), 1))
        from Genesis9.kollision import G9kollision
        return p, n, G9kollision.baum(p)


class G9frisurTest(SimpleTestCase):
    databases = set()

    def test_der_name_ist_ein_dateiname_ohne_weg(self):
        with mock.patch.object(G9frisur, 'ordner', classmethod(lambda cls: 'X:/nirgends')):
            with self.assertRaises(FileNotFoundError):
                G9frisur.pfad('../../etc/passwd')
            with self.assertRaises(ValueError):
                G9frisur.pfad('')

    def test_kasten_und_bezug(self):
        p = np.array([[-0.1, 1.5, -0.1], [0.1, 1.7, 0.1], [0.0, 1.6, 0.0]])
        k = G9frisur._kasten(p)
        np.testing.assert_allclose(k['scheitel'], [0.1, 1.7, 0.1])
        np.testing.assert_allclose(G9frisur._bezug(k), [0.0, 1.7, 0.0])
        with self.assertRaises(ValueError):
            G9frisur._kasten(np.zeros((0, 3)))

    def test_bauen_skaliert_achsweise_und_hebt_aus_der_haut(self):
        # HumanBody-Kopf 0,2 breit / 0,2 hoch / 0,2 tief, Genesis-Kopf 0,3 / 0,2 / 0,4
        hb = {'min': np.array([-0.1, 1.5, -0.1]), 'max': np.array([0.1, 1.7, 0.1]),
              'scheitel': np.array([0.0, 1.7, 0.0])}
        g9 = {'min': np.array([-0.15, 1.5, -0.2]), 'max': np.array([0.15, 1.7, 0.2]),
              'scheitel': np.array([0.0, 1.7, 0.0])}
        haar = np.array([[0.1, 1.7, 0.1], [-0.1, 1.6, -0.1], [0.0, 1.45, 0.0]])   # letzter im Kopf
        dreiecke = np.array([[0, 1, 2]])
        frisur = G9frisur.__new__(G9frisur)
        frisur.figur = mock.Mock(formung=object())
        frisur.geschlecht = 'female'
        with mock.patch.object(G9frisur, 'laden', staticmethod(lambda pfad: (haar, dreiecke))), \
                mock.patch.object(G9frisur, 'pfad', classmethod(lambda cls, name: name)), \
                mock.patch.object(G9frisur, 'kopf_hb', classmethod(lambda cls, g: hb)), \
                mock.patch.object(G9frisur, 'kopf_g9', lambda self: g9), \
                mock.patch.object(g9frisur, 'G9koerpernetz', _Netz):
            netz = frisur.bauen('probe', stufen=1)
        p = netz['punkte']
        # Breite x 1,5, Tiefe x 2, Hoehe x 1 — um Scheitel/Kastenmitte
        np.testing.assert_allclose(p[0], [0.15, 1.7, 0.2], atol=1e-9)
        np.testing.assert_allclose(p[1][[0, 2]], [-0.15, -0.2], atol=1e-9)
        # Der Punkt unter der Kopfhaut (1,45 < 1,5) steht danach ueber ihr
        self.assertGreaterEqual(p[2][1], 1.5 + G9frisur.ABSTAND - 1e-6)
        self.assertGreater(netz['hub_mm'], 40)
        self.assertEqual(netz['haut']['knochen'], ['head'])
        self.assertEqual(netz['haut']['gewicht'].shape, (3, 4))
        np.testing.assert_allclose(netz['haut']['gewicht'][:, 0], 1.0)
        self.assertEqual(netz['name'], 'probe')

    def test_die_adresse_und_der_browserweg_stehen(self):
        from django.conf import settings
        urls = (settings.BASE_DIR / 'core' / 'urls_charakter.py').read_text(encoding='utf-8')
        self.assertIn("genesis9-figur/frisur/<str:name>/", urls)
        statik = settings.BASE_DIR / 'static' / 'viewer' / 'scene'
        haar = (statik / 'hair.js').read_text(encoding='utf-8')
        self.assertIn("if (inst.quelle === 'genesis9') { Genesis9frisur.waehlen(", haar)
        self.assertIn("Genesis9frisur.faerben(Genesis9frisur.netz(inst)", haar)
        bereiche = (statik / 'eigenschaftenbereiche.js').read_text(encoding='utf-8')
        self.assertIn("GENESIS9_AUCH = ['hair']", bereiche)
        frisur = (statik / 'genesis9' / 'genesis9frisur.js').read_text(encoding='utf-8')
        # In `clothMeshes`, sonst bindet `_kleiderBinden` sie nach einem Umbau nicht um.
        self.assertIn("inst.clothMeshes[Genesis9frisur.SCHLUESSEL] = inst._einhaengen(netz, teil.hautgewichte)", frisur)
