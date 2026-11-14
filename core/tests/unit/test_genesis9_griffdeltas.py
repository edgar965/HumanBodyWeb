# -*- coding: utf-8 -*-
"""Genesis 9, 12.11.2026 (Edgar mit Bild vom Fallout Ranger im Tanz: „schuhe falsch gerigged / sitzen nicht", „erkennst du das in deinem
Tanztest?"): Die Fußhaltung eines Schuhs (`griff`) geht als Delta je Knochen an den Browser (`G9griffkette.deltas`, `G9figur._griffdeltas`),
der sie nach jedem Bild der Animation wieder auflegt; Schuhe laufen nie im Stoffschwung (`G9stoff.schuh`). Ohne Daz-Bibliothek, mit Kunstdaten.

Sabotage-Gegenproben (nicht gelaufen): `deltas` mit `mul(mit, inv(ohne))` statt `mul(inv(ohne), mit)` -> Fall 1 rot (die Drehungen vertauschen
nicht); `deltas` ohne den Filter auf die Knochen des Griffs -> Fall 2 rot; `anwenden` nur mit einer Kennung als `ohne_griff` -> Fall 4 rot;
`G9stoff.schuh` immer False -> Fall 5 und 6 rot.
"""
import math
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.griffkette import G9griffkette
from Genesis9.stoff import G9stoff
from humanbody_core.quaternion import Quat


def _um(achse, grad):
    """Quaternion [x, y, z, w] um eine Achse."""
    a = np.asarray(achse, dtype=float) / np.linalg.norm(achse)
    h = math.radians(grad) / 2.0
    return np.array([*(a * math.sin(h)), math.cos(h)])


def _knochen(name, quat):
    return {'name': name, 'quat': [float(w) for w in quat]}


class Genesis9Griffdeltas(SimpleTestCase):
    databases = set()

    def _griff(self, namen):
        return mock.patch('Genesis9.garderobe.G9garderobe.griff', return_value={n: {'rotation/x': 45.0} for n in namen})

    def test_1_delta_fuehrt_ruhe_ohne_griff_auf_ruhe_mit_griff(self):
        ohne = _um((1, 0, 0), 30.0)
        mit = Quat.mul(ohne, _um((0, 1, 0), 60.0))
        with self._griff(['l_foot']):
            d = G9griffkette.deltas([_knochen('l_foot', ohne)], [_knochen('l_foot', mit)], ['schuh'])
        self.assertIn('l_foot', d)
        np.testing.assert_allclose(Quat.mul(ohne, np.asarray(d['l_foot'])), mit, atol=1e-5)

    def test_2_nur_knochen_des_griffs(self):
        ohne = _um((1, 0, 0), 10.0)
        mit = Quat.mul(ohne, _um((0, 0, 1), 40.0))
        with self._griff(['l_foot']):
            d = G9griffkette.deltas([_knochen('l_foot', ohne), _knochen('l_toes', ohne)],
                                    [_knochen('l_foot', mit), _knochen('l_toes', mit)], ['schuh'])
        self.assertEqual(sorted(d), ['l_foot'])

    def test_3_kleine_drehung_ist_kein_delta(self):
        ohne = _um((1, 0, 0), 10.0)
        mit = Quat.mul(ohne, _um((0, 1, 0), G9griffkette.DELTA_MIN_GRAD / 2))
        with self._griff(['l_foot']):
            self.assertEqual(G9griffkette.deltas([_knochen('l_foot', ohne)], [_knochen('l_foot', mit)], ['schuh']), {})

    def test_4_anwenden_laesst_mehrere_stuecke_aus(self):
        eintraege = {'schuh_a': {'stueck_griff': True}, 'schuh_b': {'fusspose': 'x.duf'}}
        griffe = {'schuh_a': {'l_foot': {'rotation/x': 40.0}}, 'schuh_b': {'r_foot': {'rotation/x': 40.0}}}
        with mock.patch('Genesis9.garderobe.G9garderobe.eintrag', side_effect=lambda k: eintraege.get(k)), \
                mock.patch('Genesis9.garderobe.G9garderobe.griff', side_effect=lambda k: griffe.get(k, {})), \
                mock.patch('Genesis9.garderobe.G9garderobe.griffregler', return_value={}):
            drehung = {}
            G9griffkette.anwenden(drehung, {}, ['schuh_a', 'schuh_b'], ohne_griff=('schuh_a', 'schuh_b'))
            self.assertEqual(drehung, {})
            G9griffkette.anwenden(drehung, {}, ['schuh_a', 'schuh_b'], ohne_griff='schuh_a')
            self.assertEqual(sorted(drehung), ['r_foot'])
            self.assertEqual(G9griffkette.schuhe(['schuh_a', 'hemd', 'schuh_b']), ('schuh_a', 'schuh_b'))

    def test_5_schuh_nach_fusshaltung_und_kategorie(self):
        with mock.patch('Genesis9.garderobekategorien.G9garderobekategorien.kategorie', side_effect=lambda e: e.get('_kat', 'Oberteile')):
            self.assertTrue(G9stoff.schuh({'id': 'a', 'stueck_griff': True}))
            self.assertTrue(G9stoff.schuh({'id': 'b', '_kat': 'Schuhe'}))
            self.assertFalse(G9stoff.schuh({'id': 'c', '_kat': 'Kleider'}))

    def test_6_schuh_wird_nie_simuliert(self):
        folger = mock.Mock()
        folger.name = 'EIGEN_Fallout_ranger_Schuhe_Shape'
        with mock.patch('Genesis9.stoff.G9dson.lesen', side_effect=AssertionError('ein Schuh liest keinen dForce-Modifikator')):
            G9stoff.entscheiden(folger, {'id': 'schuh', 'art': 'kleidung', 'stueck_griff': True}, None)
        self.assertFalse(folger.dynamisch)
