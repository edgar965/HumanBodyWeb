# -*- coding: utf-8 -*-
"""Die Scham-Regler (`G9schammorphe`, `G9schammorphekatalog`) und die Anatomie-Angaben in `G9stueckersatz` — am Kunststück.

WARUM (Edgar, 09.10.2026, zum Scham-Stück von „cute girl": „mach dir alle möglichen Regler dafür, es kommen noch mehr
Varianten"): Die Regler rechnen aus der FORM des Stücks, nicht aus Koordinaten einer Datei. Jede Variante bekommt dieselben
Regler, wenn die Zonen auf ihre Form passen — und sonst nennt sie eigene Grenzen. Geprüft wird an einem Blatt (7 × 10 cm, nach
unten gewölbt), nicht an der echten Scham:

1. Die Normalen zeigen weg vom Becken — bei JEDER Wicklung der Flächen (das Stück schreibt `wicklung=False`).
2. t wächst vom Hügel (vorn) zum Damm (hinten) von 0 auf 1; s liegt zwischen 0 und etwa 1.
3. Jeder Katalogeintrag ist gültig: Name, Zone, Art, Seite; mindestens 30 Regler; die Namen sind eindeutig.
4. „Innere Lippen · Größe" wirkt nur in ihrer Zone (Mitte, hinten), mit dem Betrag, entlang der Normale (nach außen).
5. „links" und „rechts" trennen die Seiten (links = +x, wie die Figur).
6. Breite dehnt quer um die Mittellinie (6 % ⇒ Δx = 0,06 · x), Länge dehnt längs um die Mitte der Zone.
7. Eigene Zonen einer Variante ersetzen die Vorgabe (`"zonen"` in der `.ersetzt.json`).
8. `G9stueckersatz` schreibt `anatomie` und `zonen`, prüft beides streng, liest nur Erlaubtes zurück.

Sabotage-Gegenprobe: das Umdrehen `n = -n` in `G9schammorphe.normalen` weglassen macht Fall 1 rot (umgekehrte Wicklung);
`achse2[1] > 0` → `< 0` in `koordinaten` macht Fall 2 rot; `weich_s` der Zone `innen` auf 5 setzen macht Fall 4 rot (wirkt am
Rand); die Seite (`tanh(x / 0.003)`) in `gewicht` weglassen macht Fall 5 rot.
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.schammorphe import G9schammorphe
from Genesis9.schammorphekatalog import G9schammorphekatalog as K
from Genesis9.stueckersatz import G9stueckersatz

from ._pruefablage import Pruefablage


def blatt(umgekehrt=False, nu=41, nx=21):
    """(punkte, polys): ein Blatt 7 cm (z, vorn +) × 6 cm (x), in der Mitte um 7 mm nach unten gewölbt."""
    p, polys = [], []
    for i in range(nu):
        u = i / (nu - 1)
        for j in range(nx):
            x = -0.03 + 0.06 * j / (nx - 1)
            p.append((x, 0.88 + 8.0 * x * x, 0.07 - 0.10 * u))
    for i in range(nu - 1):
        for j in range(nx - 1):
            a, b, c, d = i * nx + j, i * nx + j + 1, (i + 1) * nx + j + 1, (i + 1) * nx + j
            polys.append([0, 0] + ([d, c, b, a] if umgekehrt else [a, b, c, d]))
    return np.array(p), polys


class SchammorpheTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.p, self.polys = blatt()
        self.k = G9schammorphe.koordinaten(self.p, self.polys)

    def test_1_normalen_zeigen_bei_jeder_wicklung_weg_vom_becken(self):
        for umgekehrt in (False, True):
            p, polys = blatt(umgekehrt)
            n = G9schammorphe.normalen(p, polys)
            self.assertLess(float(n[:, 1].mean()), -0.9, 'Wicklung umgekehrt=%s: Normalen zeigen ins Becken' % umgekehrt)

    def test_2_t_laeuft_vom_huegel_zum_damm_und_s_ueber_die_breite(self):
        t, s = self.k['t'], self.k['s']
        self.assertAlmostEqual(float(t[self.p[:, 2] > 0.0699].mean()), 0.0, places=2)
        self.assertAlmostEqual(float(t[self.p[:, 2] < -0.0299].mean()), 1.0, places=2)
        self.assertLessEqual(float(s.max()), 1.05)
        self.assertLess(float(s[np.abs(self.p[:, 0]) < 0.0001].max()), 0.05, 'Mittellinie: s ≈ 0')
        self.assertAlmostEqual(self.k['laenge'], 0.10, places=3)

    def test_3_jeder_katalogeintrag_ist_gueltig(self):
        from Genesis9.kleidmorphe import G9kleidmorphe
        namen = [e[0] for e in K.EINTRAEGE]
        self.assertGreaterEqual(len(namen), 30)
        self.assertEqual(len(namen), len(set(namen)), 'Namen doppelt')
        for e in K.EINTRAEGE:
            self.assertTrue(G9kleidmorphe.NAME.match(e[0]), e[0])
            self.assertTrue(e[0].startswith(K.PRAEFIX), e[0])
            self.assertIn(e[3], K.ZONEN, e[0])
            self.assertIn(e[4], K.ARTEN, e[0])
            self.assertIn(e[6] if len(e) > 6 else None, (None, 'links', 'rechts'), e[0])
            self.assertTrue(e[1] and e[2], 'Anzeige und Gruppe: %s' % e[0])
        regler = G9schammorphe.regler()
        self.assertEqual([r['name'] for r in regler], ['eigen.' + n for n in namen])
        self.assertTrue(all((r['min'], r['max'], r['vorgabe']) == (-2.0, 2.0, 0.0) for r in regler))
        with self.assertRaises(ValueError):
            K.eintrag('sch_gibt_es_nicht')
        self.assertTrue(K.ist_scham('sch_damm_laenge') and not K.ist_scham('form_weite_unten'))

    def test_4_innen_groesse_wirkt_nur_in_der_zone_und_nach_aussen(self):
        d = G9schammorphe.deltas(self.p, self.polys, K.eintrag('sch_innen_groesse'))
        t, s, n = self.k['t'], self.k['s'], self.k['normalen']
        kern = (t > 0.50) & (t < 0.74) & (s < 0.30)
        self.assertGreater(int(kern.sum()), 30)
        along = np.einsum('ij,ij->i', d[kern], n[kern])
        np.testing.assert_allclose(along, 0.006, atol=1e-5, err_msg='Betrag 6 mm entlang der Normale')
        self.assertLess(float(d[kern][:, 1].max()), 0.0, 'nach außen = nach unten')
        draussen = (t < 0.25) | (t > 0.95) | (s > 0.75)
        self.assertLess(float(np.abs(d[draussen]).max()), 1e-9, 'außerhalb der Zone bewegt sich nichts')

    def test_5_links_und_rechts_trennen_die_seiten(self):
        x = self.p[:, 0]
        links = G9schammorphe.deltas(self.p, self.polys, K.eintrag('sch_aussen_fuelle_links'))
        rechts = G9schammorphe.deltas(self.p, self.polys, K.eintrag('sch_aussen_fuelle_rechts'))
        aussen = np.abs(self.k['s']) > 0.6
        mitte_t = (self.k['t'] > 0.4) & (self.k['t'] < 0.8)
        wahl_l = aussen & mitte_t & (x > 0.012)
        wahl_r = aussen & mitte_t & (x < -0.012)
        self.assertGreater(int(wahl_l.sum()), 20)
        self.assertGreater(float(np.linalg.norm(links[wahl_l], axis=1).min()), 0.004)
        self.assertLess(float(np.linalg.norm(links[wahl_r], axis=1).max()), 1e-4, 'links bewegt die rechte Seite')
        self.assertGreater(float(np.linalg.norm(rechts[wahl_r], axis=1).min()), 0.004)
        self.assertLess(float(np.linalg.norm(rechts[wahl_l], axis=1).max()), 1e-4, 'rechts bewegt die linke Seite')

    def test_6_breite_dehnt_quer_und_laenge_laengs(self):
        breite = G9schammorphe.deltas(self.p, self.polys, K.eintrag('sch_gesamt_breite'))
        np.testing.assert_allclose(breite[:, 0], 0.06 * self.p[:, 0], atol=1e-9)
        np.testing.assert_allclose(breite[:, 1:], 0.0, atol=1e-12)
        laenge = G9schammorphe.deltas(self.p, self.polys, K.eintrag('sch_gesamt_laenge'))
        entlang = laenge @ self.k['achse']
        np.testing.assert_allclose(entlang, (self.k['t'] - 0.5) * self.k['laenge'] * 0.06, atol=1e-9)
        self.assertLess(float(entlang[self.k['t'] < 0.1].max()), 0.0, 'Hügel-Ende wandert nach vorn')
        self.assertGreater(float(entlang[self.k['t'] > 0.9].min()), 0.0, 'Damm-Ende wandert nach hinten')

    def test_7_eigene_zonen_einer_variante_ersetzen_die_vorgabe(self):
        eintrag = K.eintrag('sch_huegel_woelbung')
        vorgabe = G9schammorphe.deltas(self.p, self.polys, eintrag)
        eigen = G9schammorphe.deltas(self.p, self.polys, eintrag, {'huegel': {'t': (0.8, 0.9)}})
        t = self.k['t']
        self.assertGreater(float(np.abs(vorgabe[t < 0.15]).max()), 0.005)
        self.assertLess(float(np.abs(eigen[t < 0.15]).max()), 1e-9, 'der Hügel liegt in der Variante woanders')
        self.assertGreater(float(np.abs(eigen[(t > 0.8) & (t < 0.9)]).max()), 0.005)
        self.assertLess(float(np.abs(vorgabe[t > 0.9]).max()), 1e-9)

    def test_8_unbekannte_art_ist_ein_fehler(self):
        with self.assertRaises(ValueError):
            G9schammorphe.deltas(self.p, self.polys, ('sch_x', 'x', 'g', 'gesamt', 'quirl', 1.0))


class StueckersatzAnatomieTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('anatomie_')
        self.ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        self.duf = self.ordner / 'Scham.duf'
        self.duf.write_text('{}', encoding='utf-8')

    def _eintrag_mit(self):
        return mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=self.duf)

    def test_1_anatomie_und_zonen_gehen_hin_und_zurueck(self):
        pfad = G9stueckersatz.schreiben(self.duf, [], haut_tiefe_mm=30, anatomie='scham',
                                        zonen={'innen': {'t': [0.4, 0.8], 'weich_t': 0.1}})
        daten = json.loads(pfad.read_text(encoding='utf-8'))
        self.assertEqual(daten['anatomie'], 'scham')
        self.assertEqual(daten['haut_tiefe_mm'], 30.0)
        with self._eintrag_mit():
            self.assertEqual(G9stueckersatz.anatomie_fuer({}), 'scham')
            self.assertEqual(G9stueckersatz.zonen_fuer({}), {'innen': {'t': (0.4, 0.8), 'weich_t': 0.1}})
            self.assertEqual(G9stueckersatz.haut_tiefe_fuer({}), 30.0)

    def test_2_ohne_angabe_keine_anatomie_und_keine_zonen(self):
        G9stueckersatz.schreiben(self.duf, [])
        with self._eintrag_mit():
            self.assertEqual(G9stueckersatz.anatomie_fuer({}), '')
            self.assertEqual(G9stueckersatz.zonen_fuer({}), {})
            self.assertEqual(G9stueckersatz.haut_tiefe_fuer({}), 0.0)
        self.assertEqual(G9stueckersatz.anatomie_fuer({}), '', 'Eintrag ohne Dateiangabe')

    def test_3_unsinn_wird_beim_schreiben_abgelehnt_und_beim_lesen_ignoriert(self):
        for falsch in ({'anatomie': 'tier'}, {'zonen': {'huefte': {'t': [0, 1]}}}, {'zonen': {'innen': {'t': [0.4]}}},
                       {'zonen': {'innen': {'x': 1}}}, {'zonen': {'innen': {'weich_t': True}}}, {'haut_tiefe_mm': 0},
                       {'haut_tiefe_mm': 61}):
            with self.assertRaises(ValueError, msg=str(falsch)):
                G9stueckersatz.schreiben(self.duf, [], **falsch)
        pfad = G9stueckersatz.pfad(self.duf)
        pfad.write_text(json.dumps({'anatomie': 'tier', 'zonen': {'huefte': {}}, 'haut_tiefe_mm': True}), encoding='utf-8')
        with self._eintrag_mit():
            self.assertEqual(G9stueckersatz.anatomie_fuer({}), '')
            self.assertEqual(G9stueckersatz.zonen_fuer({}), {})
            self.assertEqual(G9stueckersatz.haut_tiefe_fuer({}), 0.0)
