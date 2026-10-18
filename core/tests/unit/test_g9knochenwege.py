# -*- coding: utf-8 -*-
u"""Knochenwege der Sofortvorschau einer Genesis-9-Pose (`G9knochenwegeapi`, 17.10.2026).

WARUM (Edgar: „posen dauern irrsinnig lange, das sollte doch in 1 s gehen" — „mach erst …
Sofortschau"): Der Klick dreht jetzt das vorhandene Skelett mit `neu · alt⁻¹` der Daz-Knochenmatrizen
(`Genesis9posenvorschau`); im Chrome stand die Vorschau nach 0,18 s (vorher der neue Körper nach
1,4–4,4 s). Am echten Käfig gemessen: Skinning mit diesen Wegen trifft den gebackenen Körper auf
0,00000 mm, ohne Bodenversatz liegt er genau um den Bodenunterschied daneben
(`ProjektTemp/_wegwerf/knochenwege_probe.py`, drei Posen).

1. Einheiten: Daz-Matrix in cm → Browser-Meter, um `boden` gesenkt; der Weg bildet einen alten
   Browserpunkt auf den neuen ab (Kunstmatrizen, Drehung + Verschiebung + Bodenwechsel).
2. Der Endpunkt: ohne `alt`/`neu` 400, unbekannte Figur 404, nur POST.
3. Verdrahtung: Klick im Posenbaum, Auswahl in den Eigenschaften und Reset zeigen die Vorschau VOR dem
   Neubau; die Route steht in `urls_posen.py`.

Tests geschrieben, nicht gelaufen (nur auf Ansage).
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from core.api.g9knochenwege import G9knochenwegeapi

VIEWER = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'charakter'


def stellung(matrizen, boden):
    u"""Was `lagen` von einer `G9formung` braucht: `matrizen().matrizen()` (cm) und `boden()` (m)."""
    return mock.Mock(matrizen=lambda: mock.Mock(matrizen=lambda: matrizen), boden=lambda: boden)


def drehung_y(grad, t_cm):
    w = np.radians(grad)
    m = np.eye(4)
    m[:3, :3] = [[np.cos(w), 0, np.sin(w)], [0, 1, 0], [-np.sin(w), 0, np.cos(w)]]
    m[:3, 3] = t_cm
    return m


class Einheiten(SimpleTestCase):
    databases = set()

    def test_der_weg_bildet_alte_browserpunkte_auf_neue_ab(self):
        m_alt, m_neu = drehung_y(0, [10, 0, 0]), drehung_y(90, [0, 20, 5])
        alt, neu = stellung({'head': m_alt}, -0.10), stellung({'head': m_neu}, 0.05)
        weg = G9knochenwegeapi.wege_zwischen(alt, neu)['head']
        ruhe_cm = np.array([3.0, 150.0, -2.0, 1.0])
        browser = lambda m, boden: (m @ ruhe_cm)[:3] * 0.01 - np.array([0, boden, 0])  # noqa: E731
        alt_b, neu_b = browser(m_alt, -0.10), browser(m_neu, 0.05)
        np.testing.assert_allclose((weg @ np.append(alt_b, 1.0))[:3], neu_b, atol=1e-12)

    def test_spaltenweise_wie_three(self):
        m = np.arange(16, dtype=float).reshape(4, 4)
        self.assertEqual(G9knochenwegeapi._spaltenweise(m)[:4], [0.0, 4.0, 8.0, 12.0])


class Endpunkt(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.fabrik = RequestFactory()

    def _post(self, rumpf, eintrag=True):
        anfrage = self.fabrik.post('/x/', data=json.dumps(rumpf), content_type='application/json')
        with mock.patch('core.api.g9knochenwege.G9pfade.vorhanden', return_value=True), \
                mock.patch('core.api.g9knochenwege.G9figur._eintrag', return_value={} if eintrag else None):
            return G9knochenwegeapi.wege(anfrage, 'basis')

    def test_ohne_alt_und_neu_400(self):
        self.assertEqual(self._post({'neu': {}}).status_code, 400)

    def test_unbekannte_figur_404(self):
        self.assertEqual(self._post({'alt': {}, 'neu': {}}, eintrag=False).status_code, 404)

    def test_nur_post(self):
        self.assertEqual(G9knochenwegeapi.wege(self.fabrik.get('/x/'), 'basis').status_code, 405)


class Verdrahtung(SimpleTestCase):
    databases = set()

    def test_die_vorschau_kommt_vor_dem_neubau(self):
        wahl = (VIEWER / 'posenwahl.js').read_text(encoding='utf-8')
        for rumpf in (wahl.split('static _genesis9(')[1], wahl.split('static zuruecksetzen(')[1]):
            rumpf = rumpf.split('\n    }')[0]
            self.assertIn('Genesis9posenvorschau.zeigen(', rumpf)
            self.assertLess(rumpf.index('Genesis9posenvorschau.zeigen('), rumpf.index('Genesis9lauf.planen('))
        eigenschaften = (VIEWER / 'genesis9' / 'genesis9posen.js').read_text(encoding='utf-8')
        hoerer = eigenschaften.split("wahl.addEventListener('change'")[1]      # der Hörer der Posenwahl — davor steht seither ein Kästchen mit eigenem Hörer
        self.assertLess(hoerer.index('Genesis9posenvorschau.zeigen('), hoerer.index('Genesis9lauf.planen('))

    def test_die_route(self):
        routen = (Path(settings.BASE_DIR) / 'core' / 'urls_posen.py').read_text(encoding='utf-8')
        self.assertIn("'api/character/genesis9-figur/<str:name>/knochenwege/', G9knochenwegeapi.wege", routen)
