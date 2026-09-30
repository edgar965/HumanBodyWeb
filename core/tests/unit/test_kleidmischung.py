# -*- coding: utf-8 -*-
u"""Die Kleidungsmischung über die Haut (`Genesis9/kleidmischung.py`, `kleidmischflaeche.py`, 30.09.2026).

Kunststücke: Die Haut ist eine Ebene bei z = 0 (Normale +z), jedes „Kleidungsstück" ein Gitter im Abstand `h` darüber, x
nach rechts, y nach oben. So lässt sich nachrechnen, was an echten Stücken nur zu messen ist (`ProjektTemp/_wegwerf/
kleidgenerisch/mischprobe.py`): Höhe im Verhältnis der Anteile, ein Stück je Stelle, der Rand, der Auslauf, die
Gegenfarbe.

    A: x 0,0 … 1,0, Höhe 5 mm        B: x 0,5 … 1,5, Höhe 20 mm        Überlappung x 0,5 … 1,0
"""
import unittest

import numpy as np
from Genesis9.kleidmischflaeche import G9kleidmischflaeche
from Genesis9.kleidmischung import G9kleidmischung
from Genesis9.oberflaechenbindung import G9oberflaechenbindung
from scipy.spatial import cKDTree

SCHRITT = 0.02
MM = 1000.0


def haut():
    u"""Die Ebene z = 0 als Körper: Punkte, Normalen, Dreiecke, Baum — `G9oberflaechenbindung`."""
    xs, ys = np.arange(-0.4, 1.9, SCHRITT), np.arange(-0.2, 0.9, SCHRITT)
    punkte = np.array([[x, y, 0.0] for y in ys for x in xs])
    dreiecke = _gitterdreiecke(len(xs), len(ys))
    normalen = np.tile([0.0, 0.0, 1.0], (len(punkte), 1))
    return G9oberflaechenbindung(punkte, normalen, dreiecke, cKDTree(punkte.astype(np.float32)))


def _gitterdreiecke(spalten, zeilen):
    aus = []
    for j in range(zeilen - 1):
        for i in range(spalten - 1):
            a = j * spalten + i
            aus += [[a, a + 1, a + spalten], [a + 1, a + spalten + 1, a + spalten]]
    return np.array(aus, dtype=np.int64)


def stueck(koerper, name, x0, x1, hoehe, gruppen=True):
    u"""`(Name, rohes Netz)` — ein Gitter x0…x1, y 0…0,6 in der Höhe `hoehe` (Meter), mit Bindung wie der Bau sie
    mitgibt."""
    xs, ys = np.arange(x0, x1 + SCHRITT / 2, SCHRITT), np.arange(0.0, 0.6 + SCHRITT / 2, SCHRITT)
    punkte = np.array([[x, y, hoehe] for y in ys for x in xs])
    dreiecke = _gitterdreiecke(len(xs), len(ys))
    netz = {'punkte': punkte, 'dreiecke': dreiecke,
            'normalen': np.tile([0.0, 0.0, 1.0], (len(punkte), 1)),
            'uv': np.column_stack([punkte[:, 0], punkte[:, 1]]),
            'haut': {'knochen': ['hip'], 'index': np.zeros((len(punkte), 4), dtype=np.int64),
                     'gewicht': np.tile([1.0, 0, 0, 0], (len(punkte), 1))},
            'stufen': 0, 'art': None, 'name': name, 'stoff': None,
            'bindung': koerper.fuer(punkte, fern=10.0)}
    if gruppen:
        netz['gruppen'] = [{'name': name, 'index_ab': 0, 'index_anzahl': len(dreiecke) * 3, 'kachel': 1001,
                            'bilder': {}}]
    return name, netz


class MischungBasis(unittest.TestCase):

    #: Ein weicher Rand von 5 cm.
    UEBERGANG = 0.05

    def setUp(self):
        self.koerper = haut()
        _n, self.netz_a = stueck(self.koerper, 'A', 0.0, 1.0, 0.005)
        _n, self.netz_b = stueck(self.koerper, 'B', 0.5, 1.5, 0.020)
        self.a = G9kleidmischflaeche.aus_netz('A', 0, self.netz_a, self.koerper)
        self.b = G9kleidmischflaeche.aus_netz('B', 0, self.netz_b, self.koerper)

    def mischen(self, anteil_a=1.0, anteil_b=0.3, uebergang=None):
        aus = G9kleidmischung.mischen([self.a, self.b], {'A': anteil_a, 'B': anteil_b}, ['A', 'B'],
                                      self.UEBERGANG if uebergang is None else uebergang)
        return aus[0], aus[1]

    @staticmethod
    def zone(f, von, bis):
        return (f.punkte[:, 0] >= von) & (f.punkte[:, 0] <= bis)


class FlaecheTest(MischungBasis):

    def test_1_hoehe_und_hautstelle_kommen_aus_der_bindung(self):
        self.assertAlmostEqual(float(np.median(self.a.hoehe)) * MM, 5.0, places=1)
        self.assertAlmostEqual(float(np.median(self.b.hoehe)) * MM, 20.0, places=1)
        # Die Hautstelle liegt senkrecht unter dem Punkt: gleiches x und y, z = 0.
        np.testing.assert_allclose(self.a.haut[:, :2], self.a.punkte[:, :2], atol=1e-6)
        np.testing.assert_allclose(self.a.haut[:, 2], 0.0, atol=1e-6)

    def test_2_punkt_ist_hautstelle_plus_versatz(self):
        np.testing.assert_allclose(self.b.haut + self.b.versatz, self.b.punkte, atol=1e-9)

    def test_3_punkt_ohne_bindung_wird_ohne_grenze_nachgeholt(self):
        u"""Ein Rocksaum weit über dem Bein (jenseits `FERN_M`, Dreieck −1) bekommt seine Hautstelle trotzdem."""
        _n, netz = stueck(self.koerper, 'C', 0.0, 0.4, 0.30)     # 30 cm: weit über der Grenze von 8 cm
        self.assertTrue((np.asarray(netz['bindung']['dreieck'])[:, 0] >= 0).all())      # mit fern=10 gebunden
        netz['bindung'] = self.koerper.fuer(netz['punkte'])       # Vorgabe: jenseits 8 cm ungebunden
        self.assertTrue((np.asarray(netz['bindung']['dreieck'])[:, 0] < 0).all())
        f = G9kleidmischflaeche.aus_netz('C', 0, netz, self.koerper)
        self.assertAlmostEqual(float(np.median(f.hoehe)) * MM, 300.0, places=0)

    def test_4_ein_netz_ohne_bindung_bekommt_seine_hautstelle_ganz_vom_koerper(self):
        u"""HumanBody: Das Netz trägt keine Bindung (der Browser hält dort nichts an der Haut) — jeder Punkt wird
        der Haut des Körpers zugeordnet, mit demselben Ergebnis wie mit der Bindung des Baus."""
        ohne = dict(self.netz_a)
        del ohne['bindung']
        f = G9kleidmischflaeche.aus_netz('A', 0, ohne, self.koerper)
        np.testing.assert_allclose(f.haut, self.a.haut, atol=1e-6)
        np.testing.assert_allclose(f.hoehe, self.a.hoehe, atol=1e-6)


class ZoneTest(MischungBasis):

    def test_1_in_der_zone_gilt_das_verhaeltnis_der_anteile(self):
        u"""100 % A und 30 % B: Höhe = (1·5 + 0,3·20) / 1,3 = 8,46 mm — nicht 5, nicht 20, nicht 12,5."""
        (pa, _ba, _fa), _b = self.mischen(1.0, 0.3)
        innen = self.zone(self.a, 0.62, 0.90)
        np.testing.assert_allclose(pa[innen, 2] * MM, 11.0 / 1.3, atol=0.3)

    def test_2_nur_das_verhaeltnis_zaehlt_nicht_die_summe(self):
        (p1, _b1, _f1), _ = self.mischen(1.0, 0.3)
        (p2, _b2, _f2), _ = self.mischen(2.0, 0.6)
        np.testing.assert_allclose(p1, p2, atol=1e-9)

    def test_3_gleiche_anteile_ergeben_das_mittel(self):
        (pa, _ba, _fa), _b = self.mischen(1.0, 1.0)
        innen = self.zone(self.a, 0.62, 0.90)
        np.testing.assert_allclose(pa[innen, 2] * MM, 12.5, atol=0.3)

    def test_4_das_mittel_liegt_nie_in_der_haut(self):
        (pa, _ba, _fa), (pb, _bb, _fb) = self.mischen(1.0, 5.0)
        self.assertGreater(float(pa[:, 2].min()), 0.0)
        self.assertGreater(float(pb[:, 2].min()), 0.0)

    def test_5_ausserhalb_bleibt_alles_wo_es_ist(self):
        u"""Weiter als Radius und Auslauf vom Gegenstück: kein Punkt bewegt sich um mehr als eine Rundung."""
        (pa, _ba, _fa), (pb, _bb, _fb) = self.mischen(1.0, 0.3)
        weit_a = self.zone(self.a, -1.0, 0.30)
        weit_b = self.zone(self.b, 1.20, 2.0)
        np.testing.assert_allclose(pa[weit_a], self.a.punkte[weit_a], atol=1e-9)
        np.testing.assert_allclose(pb[weit_b], self.b.punkte[weit_b], atol=1e-9)

    def test_6_ohne_auslauf_gibt_es_keinen_uebergang(self):
        (pa, _ba, _fa), _b = self.mischen(1.0, 0.3, uebergang=0.0)
        aussen = ~self.zone(self.a, 0.30, 1.0)
        np.testing.assert_allclose(pa[aussen], self.a.punkte[aussen], atol=1e-9)

    def test_7_der_auslauf_ist_weich_und_endet_bei_null(self):
        u"""Vom Rand der Zone nach außen: die Verschiebung nimmt ab und ist nach `uebergang` Metern null."""
        (pa, _ba, _fa), _b = self.mischen(1.0, 0.3)
        verschiebung = np.abs(pa[:, 2] - self.a.punkte[:, 2])
        zeile = np.isclose(self.a.punkte[:, 1], 0.30, atol=1e-6)
        x = self.a.punkte[zeile, 0]
        v = verschiebung[zeile]
        rand = x[v > 1e-5].min()                  # der äußerste bewegte Punkt links
        innen = v[(x > 0.62) & (x < 0.9)].mean()
        self.assertGreater(innen, 0.002)
        self.assertLess(v[x < rand - 1e-9].max(initial=0.0), 1e-9)
        ramp = v[(x >= rand) & (x <= 0.62)]
        self.assertTrue((np.diff(ramp) >= -1e-9).all(), 'der Auslauf steigt zur Zone hin an')


class EineFlaecheTest(MischungBasis):

    def test_1_das_staerkere_stueck_bleibt_ganz(self):
        (_pa, ba, _fa), _b = self.mischen(1.0, 0.3)
        self.assertTrue(ba.all())

    def test_2_das_schwaechere_faellt_in_der_zone_weg_und_ausserhalb_bleibt_es(self):
        _a, (_pb, bb, _fb) = self.mischen(1.0, 0.3)
        innen = self.zone(self.b, 0.62, 0.90)
        aussen = self.zone(self.b, 1.20, 2.0)
        self.assertFalse(bb[innen].any())
        self.assertTrue(bb[aussen].all())

    def test_3_umgekehrt_wenn_b_staerker_ist(self):
        aus = G9kleidmischung.mischen([self.a, self.b], {'A': 0.3, 'B': 1.0}, ['B', 'A'], self.UEBERGANG)
        self.assertTrue(aus[1][1].all())
        self.assertFalse(aus[0][1][self.zone(self.a, 0.62, 0.90)].any())

    def test_4_am_rand_treffen_sich_beide_flaechen(self):
        u"""Kein Riss: Von der Kante des stärkeren Stücks (x = 1,0) bis zum nächsten bleibenden Punkt des schwächeren
        ist
        es höchstens ein paar Gitterschritte weit — gemessen 20 mm bei Schritt 20 mm."""
        (pa, ba, _fa), (pb, bb, _fb) = self.mischen(1.0, 0.3)
        kante = np.isclose(self.a.punkte[:, 0], 1.0)
        abstand, _n = cKDTree(pb[bb]).query(pa[kante])
        self.assertLess(float(abstand.max()), 3 * SCHRITT)

    def test_5_der_ring_nimmt_die_punkte_der_dreiecke_mit(self):
        u"""Ein einzelner bleibender Punkt bringt alle Punkte seiner Dreiecke mit — sonst risse es am Zonenrand."""
        d = self.b.dreiecke
        punkt = int(np.flatnonzero(np.isclose(self.b.punkte[:, 0], 0.9) & np.isclose(self.b.punkte[:, 1], 0.3))[0])
        bleibt = np.zeros(len(self.b.punkte), dtype=bool)
        bleibt[punkt] = True
        ring = G9kleidmischung._ring(self.b, bleibt)
        self.assertEqual(set(np.flatnonzero(ring)), set(np.unique(d[(d == punkt).any(axis=1)])))


class GegenfarbeTest(MischungBasis):

    def test_1_jeder_punkt_kennt_die_punkte_des_anderen_an_seiner_stelle(self):
        (_pa, _ba, fremd_a), (_pb, _bb, fremd_b) = self.mischen(1.0, 0.3)
        self.assertEqual([f[0] for f in fremd_a], ['B'])
        self.assertEqual([f[0] for f in fremd_b], ['A'])
        _s, nummer, gewicht, deckung = fremd_a[0]
        self.assertEqual(nummer.shape[0], len(self.a.punkte))
        np.testing.assert_allclose(gewicht.sum(axis=1), 1.0, atol=1e-9)
        self.assertLess(int(nummer.max()), len(self.b.punkte))
        self.assertEqual(deckung.shape, (len(self.a.punkte),))

    def test_2_deckung_ist_eins_in_der_zone_null_weit_davon_und_dazwischen_weich(self):
        (_pa, _ba, fremd_a), _b = self.mischen(1.0, 0.3)
        deckung = fremd_a[0][3]
        self.assertTrue(np.allclose(deckung[self.zone(self.a, 0.62, 0.95)], 1.0))
        self.assertTrue(np.allclose(deckung[self.zone(self.a, -1.0, 0.30)], 0.0))
        zeile = np.isclose(self.a.punkte[:, 1], 0.30, atol=1e-6)
        rampe = deckung[zeile & self.zone(self.a, 0.30, 0.62)]
        self.assertTrue(((rampe > 0.0) & (rampe < 1.0)).any())

    def test_3_die_nummern_zeigen_auf_punkte_an_derselben_stelle(self):
        (_pa, _ba, fremd_a), _b = self.mischen(1.0, 0.3)
        _s, nummer, _g, deckung = fremd_a[0]
        innen = np.flatnonzero((deckung == 1.0) & self.zone(self.a, 0.62, 0.90))
        x_a = self.a.punkte[innen, 0]
        x_b = self.b.punkte[nummer[innen, 0], 0]
        self.assertLess(float(np.abs(x_a - x_b).max()), 2 * SCHRITT)


class NetzTest(MischungBasis):

    def test_1_neues_netz_schneidet_alle_felder_gleich(self):
        _a, (pb, bb, _fb) = self.mischen(1.0, 0.3)
        neu = self.b.neues_netz(self.netz_b, pb, bb, self.koerper)
        n = len(neu['punkte'])
        self.assertEqual(n, int(bb.sum()))
        for feld in ('normalen', 'uv'):
            self.assertEqual(len(neu[feld]), n, feld)
        for feld in ('dreieck', 'bary', 'abstand', 'mischung'):
            self.assertEqual(len(neu['bindung'][feld]), n, feld)
        self.assertEqual(len(neu['haut']['index']), n)
        self.assertLess(int(np.asarray(neu['dreiecke']).max()), n)
        self.assertIsNone(neu.get('stoff'))         # dForce gilt fürs ungeschnittene Netz

    def test_2_bindung_folgt_den_bewegten_punkten(self):
        u"""Der Browser hält Stoff über `abstand` an der Haut — mit dem alten Abstand spränge er beim ersten Bild
        zurück."""
        (pa, ba, _fa), _b = self.mischen(1.0, 0.3)
        neu = self.a.neues_netz(self.netz_a, pa, ba, self.koerper)
        np.testing.assert_allclose(np.asarray(neu['bindung']['abstand'], dtype=np.float64), pa[ba, 2], atol=1e-4)

    def test_3_nichts_uebrig_ist_none(self):
        self.assertIsNone(self.a.neues_netz(self.netz_a, self.a.punkte, np.zeros(len(self.a.punkte), dtype=bool),
                                            self.koerper))

    def test_4_unbewegtes_netz_behaelt_seine_normalen(self):
        alle = np.ones(len(self.a.punkte), dtype=bool)
        neu = self.a.neues_netz(self.netz_a, self.a.punkte.copy(), alle, self.koerper)
        np.testing.assert_allclose(neu['normalen'], self.netz_a['normalen'])

    def test_5_normalen_der_bewegten_flaeche_stehen_senkrecht_zur_ebene(self):
        (pa, ba, _fa), _b = self.mischen(1.0, 0.3)
        neu = self.a.neues_netz(self.netz_a, pa, ba, self.koerper)
        n = np.asarray(neu['normalen'])
        np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1.0, atol=1e-6)
        self.assertGreater(float(n[:, 2].min()), 0.9)

    def test_6_ohne_bindung_bleibt_das_netz_ohne_bindung(self):
        u"""HumanBody: Die Mischung erfindet keine Bindung — der Browser hielte das Stück sonst an der falschen
        (Genesis-)Fläche."""
        ohne = dict(self.netz_a)
        del ohne['bindung']
        f = G9kleidmischflaeche.aus_netz('A', 0, ohne, self.koerper)
        (pa, ba, _fa), _b = self.mischen(1.0, 0.3)
        neu = f.neues_netz(ohne, pa, ba, self.koerper)
        self.assertNotIn('bindung', neu)
        self.assertEqual(len(neu['punkte']), int(ba.sum()))

    def test_7_stoff_misch_nennt_quelle_und_versatz_der_bleibenden_punkte(self):
        u"""Der Stoffschwung schwingt das ungeschnittene Netz: `quelle` sagt je bleibendem Punkt, aus welchem Punkt des
        ungeschnittenen Netzes er stammt, `versatz` um wie viel die Mischung ihn verschoben hat."""
        _a, (pb, bb, _fb) = self.mischen(1.0, 0.3)
        quelle, versatz = self.b.stoff_misch(pb, bb)
        self.assertEqual(quelle.dtype, np.uint32)
        self.assertEqual(versatz.dtype, np.float32)
        np.testing.assert_array_equal(quelle, np.flatnonzero(bb))
        np.testing.assert_allclose(versatz, (pb - self.b.punkte)[bb], atol=1e-6)
        self.assertGreater(float(np.abs(versatz).max()), 0.001)              # in der Zone ist B bewegt: 20 mm → Mittel
        ruhig = np.linalg.norm(versatz, axis=1) < 1e-9
        self.assertTrue(ruhig.any())                                          # weit von der Zone: nichts verschoben

    def test_8_ohne_zuschnitt_ist_die_quelle_die_reihenfolge_selbst(self):
        alle = np.ones(len(self.a.punkte), dtype=bool)
        quelle, versatz = self.a.stoff_misch(self.a.punkte.copy(), alle)
        np.testing.assert_array_equal(quelle, np.arange(len(self.a.punkte)))
        self.assertEqual(float(np.abs(versatz).max()), 0.0)


if __name__ == '__main__':
    unittest.main()
