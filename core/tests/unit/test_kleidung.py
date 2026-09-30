# -*- coding: utf-8 -*-
"""Kleidung in „Mesh to 3D" (29.09.2026) — Hautmodell, Bänder, Flächenkarte, Maske, Zurückrechnen, Objekt.

Edgar: „Überleg dir was zu den Kleider … wegen kleider habe ich dir schon gesagt, du sollst das tun!" — nach einem
Lauf, dessen Figur einen Torso in Shirtform trug. Gemessen am Lauf 2026.09.29.13.42.12: Der Hautton der Kette
(92, 78, 75) lag mit Lab a*/b* ≈ 3,5/0 auf dem Shirt (2,9/−0,7); die kahle Haut liegt bei 9–12/5–11.

Alles an Kunstdaten — Kunstlandmarken, Kunstproben, ein Gitter als Netz, ohne Datenbank, ohne GPU, ohne echtes Netz.
NICHT gelaufen (Tests nur auf Ansage).
"""

import unittest
from pathlib import Path

import numpy as np
from Kleidung.kleidungsentposen import Kleidungsentposen
from Kleidung.kleidungsmaske import Kleidungsmaske
from Kleidung.kleidungsobjekt import Kleidungsobjekt

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from meshfigur_hautbaender import Meshfigurhautbaender  # noqa: E402
from meshfigur_hautkarte import Meshfigurhautkarte  # noqa: E402
from meshfigur_hautmodell import Meshfigurhautmodell  # noqa: E402

HAUT = (190, 140, 120)
STOFF = (128, 128, 130)


def koerper():
    """33 Landmarken einer aufrechten Figur (Y oben, Meter) — nur die, die die Bausteine lesen."""
    k = np.full((33, 3), np.nan)
    k[0] = (0.0, 1.55, 0.05)
    k[11], k[12] = (0.19, 1.40, 0.0), (-0.19, 1.40, 0.0)
    k[13], k[14] = (0.30, 1.15, 0.0), (-0.30, 1.15, 0.0)
    k[15], k[16] = (0.36, 0.90, 0.0), (-0.36, 0.90, 0.0)
    k[19], k[20] = (0.38, 0.80, 0.0), (-0.38, 0.80, 0.0)
    k[23], k[24] = (0.10, 0.90, 0.0), (-0.10, 0.90, 0.0)
    k[25], k[26] = (0.10, 0.50, 0.0), (-0.10, 0.50, 0.0)
    k[27], k[28] = (0.10, 0.10, 0.0), (-0.10, 0.10, 0.0)
    k[31], k[32] = (0.10, 0.02, 0.10), (-0.10, 0.02, 0.10)
    return k


def entlang(a, b, n, radius, t=(0.0, 1.0), zufall=0):
    """(n, 3) Punkte um die Strecke a–b, im Abschnitt `t`."""
    z = np.random.default_rng(zufall)
    a, b = np.asarray(a, float), np.asarray(b, float)
    s = z.uniform(t[0], t[1], n)
    quer = z.normal(size=(n, 3)) * radius * 0.5
    return a + s[:, None] * (b - a) + quer


def farben(n, farbe, streuung=6.0, zufall=1):
    z = np.random.default_rng(zufall)
    return np.clip(np.asarray(farbe, float) + z.normal(size=(n, 3)) * streuung, 0, 255)


class HautmodellTest(unittest.TestCase):
    def _proben(self, mit_stoff_am_arm=False):
        k = koerper()
        orte, cols = [], []
        gruppen = [((14, 16), 0.045, (0.4, 0.9), HAUT), ((13, 15), 0.045, (0.4, 0.9),
                                                          STOFF if mit_stoff_am_arm else HAUT),
                   ((26, 28), 0.06, (0.2, 0.75), HAUT), ((25, 27), 0.06, (0.2, 0.75), HAUT)]
        for (a, b), r, t, farbe in gruppen:
            orte.append(entlang(k[a], k[b], 200, r, t))
            cols.append(farben(200, farbe))
        # Rumpf: Stoff (mitten zwischen Schultern und Hüfte)
        orte.append(entlang((0, 1.35, 0), (0, 0.95, 0), 600, 0.12, zufall=5))
        cols.append(farben(600, STOFF))
        return k, np.concatenate(orte), np.concatenate(cols)

    def test_lab_grau_ist_unbunt_und_haut_ist_warm(self):
        lab = Meshfigurhautmodell.lab(np.array([STOFF, HAUT]))
        self.assertLess(float(np.hypot(lab[0, 1], lab[0, 2])), 3.0)
        self.assertGreater(float(lab[1, 1]), 8.0)
        self.assertGreater(float(lab[1, 2]), 8.0)

    def test_hautton_kommt_von_den_kahlen_stellen_nicht_vom_rumpf(self):
        k, p, f = self._proben()
        m = Meshfigurhautmodell.messen(p, f, k)
        self.assertIsNotNone(m)
        # Der Rumpf (Stoff) macht 600 von 1400 Proben aus — der Ton ist trotzdem die Haut.
        self.assertTrue(all(abs(a - b) < 15 for a, b in zip(m.hautton, HAUT, strict=True)), m.hautton)
        self.assertGreater(m.buntheit, 12.0)

    def test_stoff_ist_neutraler_nicht_anders_bunt(self):
        k, p, f = self._proben()
        m = Meshfigurhautmodell.messen(p, f, k)
        ist = m.ist_haut(np.array([HAUT, (215, 150, 120), STOFF, (230, 20, 20), (30, 60, 200)]))
        # Haut und kräftigere Haut derselben Farbe: ja. Grau, kräftig rotes und blaues Tuch: nein.
        self.assertEqual(ist.tolist(), [True, True, False, False, False])

    def test_eine_bedeckte_gruppe_wird_verworfen(self):
        k, p, f = self._proben(mit_stoff_am_arm=True)
        m = Meshfigurhautmodell.messen(p, f, k)
        self.assertIsNotNone(m)
        self.assertFalse(m.gruppen['unterarm_l']['angenommen'])
        self.assertTrue(m.gruppen['unterarm_r']['angenommen'])
        self.assertNotIn('unterarm_l', m.angenommen)

    def test_ohne_zwei_kahle_stellen_kein_modell(self):
        k = koerper()
        p = entlang((0, 1.35, 0), (0, 0.95, 0), 600, 0.12)
        self.assertIsNone(Meshfigurhautmodell.messen(p, farben(600, STOFF), k))

    def test_landmarken_mit_zu_wenigen_ansichten_zaehlen_nicht(self):
        k, p, f = self._proben()
        treffer = np.full(33, 1)
        self.assertIsNone(Meshfigurhautmodell.messen(p, f, k, treffer=treffer))


class BaenderTest(unittest.TestCase):
    def setUp(self):
        self.b = Meshfigurhautbaender(koerper())

    def test_hautfleck_im_shirt_wird_stoff(self):
        # 25 % „Haut" im Rumpf verstreut: seine Bänder bleiben bedeckt (6 von 800 Punkten liegen außerhalb).
        orte = entlang((0, 1.35, 0), (0, 0.95, 0), 800, 0.10, zufall=2)
        haut = np.random.default_rng(3).uniform(size=800) < 0.25
        neu, anteile = self.b.entscheiden(orte, np.ones(800), haut)
        self.assertFalse(neu[self.b.zuordnen(orte)[0] == 0].any())  # Achse 0 = Rumpf
        self.assertLess(max(anteile['rumpf']), 0.5)

    def test_dunkle_flecken_am_kahlen_arm_bleiben_haut(self):
        # Unterarm: 15 % dunkel (Haare, Uhr) — das Band bleibt kahl, alles dort ist Haut.
        k = koerper()
        orte = entlang(k[14], k[16], 600, 0.03, zufall=4)
        haut = np.random.default_rng(6).uniform(size=600) > 0.15
        neu, _ = self.b.entscheiden(orte, np.ones(600), haut)
        self.assertTrue(neu.all())

    def test_ein_aermel_endet_an_einer_bandgrenze(self):
        k = koerper()
        orte = entlang(k[12], k[14], 1200, 0.03, zufall=7)
        t = ((orte - k[12]) @ (k[14] - k[12])) / float((k[14] - k[12]) @ (k[14] - k[12]))
        haut = t > 0.5  # obere Hälfte Ärmel (Stoff), untere kahl
        neu, _ = self.b.entscheiden(orte, np.ones(1200), haut)
        self.assertLess(float(neu[t < 0.35].mean()), 0.05)
        self.assertGreater(float(neu[t > 0.7].mean()), 0.95)

    def test_der_hals_bleibt_beim_farburteil(self):
        # Über der Schulterlinie plus 2 cm gehört keine Fläche einem Band — sonst wurde das Gesicht Teil des
        # Kragenbands und „bedeckt" (im Bild gesehen, 29.09.2026).
        orte = np.array([[0.0, 1.60, 0.05], [0.0, 1.50, 0.05], [0.0, 1.20, 0.10]])
        haut = np.array([True, True, False])
        neu, _ = self.b.entscheiden(orte, np.ones(3), haut)
        self.assertEqual(neu.tolist(), [True, True, False])

    def test_ohne_schulterlandmarken_keine_obergrenze_und_kein_absturz(self):
        k = koerper()
        k[11:13] = np.nan
        b = Meshfigurhautbaender(k)
        self.assertEqual(b.oben, np.inf)
        self.assertNotIn('rumpf', [a[0] for a in b.achsen])


class Kunstscan:
    """Ein senkrechtes Gitter in der XY-Ebene (x −0,2…0,2, y 0…1,6) als Netz mit einer Farbe je Fläche."""

    def __init__(self, farbe_je_flaeche, nx=20, ny=32):
        xs, ys = np.linspace(-0.2, 0.2, nx + 1), np.linspace(0.0, 1.6, ny + 1)
        gx, gy = np.meshgrid(xs, ys)
        self.punkte = np.stack([gx.ravel(), gy.ravel(), np.zeros(gx.size)], axis=1)
        idx = np.arange((nx + 1) * (ny + 1)).reshape(ny + 1, nx + 1)
        a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, :-1].ravel(), idx[1:, 1:].ravel()
        self.flaechen = np.concatenate([np.stack([a, b, c], 1), np.stack([b, d, c], 1)])
        self.nx, self.ny = nx, ny
        self._farben = np.asarray(farbe_je_flaeche(self), dtype=np.float64)

    def farben(self, flaeche, bary):
        return self._farben[np.asarray(flaeche)]

    def hoehe_je_flaeche(self):
        return self.punkte[self.flaechen].mean(axis=1)[:, 1]


class _Modell:
    """Nur `ist_haut` — Rot ≥ 128 gilt als Haut."""

    @staticmethod
    def ist_haut(farben):
        return np.asarray(farben)[:, 0] >= 128


class HautkarteTest(unittest.TestCase):
    def test_einzelne_flecken_fallen_heraus_grosse_bleiben(self):
        def farbe(s):
            y = s.hoehe_je_flaeche()
            f = np.tile(np.array([200.0, 150.0, 130.0]), (len(y), 1))
            f[y > 0.8] = (60, 60, 65)  # obere Hälfte Stoff
            f[3] = (60, 60, 65)  # ein dunkler Fleck in der Haut
            f[np.flatnonzero(y > 0.8)[10]] = (200, 150, 130)  # ein Hautfleck im Stoff
            return f

        scan = Kunstscan(farbe)
        haut = Meshfigurhautkarte(scan, _Modell()).rechnen()['haut']
        y = scan.hoehe_je_flaeche()
        self.assertTrue(haut[y < 0.7].all())
        self.assertFalse(haut[y > 0.9].any())

    def test_mit_landmarken_gilt_das_band_als_ganzes(self):
        def farbe(s):
            return np.tile(np.array([200.0, 150.0, 130.0]), (len(s.flaechen), 1))

        scan = Kunstscan(farbe)
        karte = Meshfigurhautkarte(scan, _Modell(), koerper())
        self.assertIsNotNone(karte.baender)
        self.assertTrue(karte.rechnen()['haut'].all())


class MaskeTest(unittest.TestCase):
    def test_oberteil_hose_fuesse_nach_lage_und_der_kopf_nie(self):
        def farbe(s):
            y = s.hoehe_je_flaeche()
            f = np.tile(np.array([200.0, 150.0, 130.0]), (len(y), 1))
            f[(y > 0.95) & (y < 1.35)] = (60, 60, 65)  # Oberteil
            f[(y > 0.3) & (y < 0.8)] = (60, 60, 65)  # Hose
            f[y < 0.15] = (60, 60, 65)  # Füße
            f[y > 1.45] = (60, 60, 65)  # Haar
            return f

        scan = Kunstscan(farbe)
        karte = Meshfigurhautkarte(scan, _Modell())
        haut = karte.rechnen()['haut']
        m = Kleidungsmaske(scan.punkte, scan.flaechen, haut, koerper(), None, karte).rechnen()
        y = scan.hoehe_je_flaeche()
        art = m['stueck']
        self.assertTrue((art[(y > 1.0) & (y < 1.3)] == Kleidungsmaske.OBERTEIL).all())
        self.assertTrue((art[(y > 0.35) & (y < 0.75)] == Kleidungsmaske.HOSE).all())
        self.assertTrue((art[y < 0.12] == Kleidungsmaske.FUESSE).all())
        self.assertFalse(m['kleidung'][y > 1.45].any())
        self.assertEqual(sorted(s['name'] for s in m['stuecke']),
                         sorted(['Oberteil', 'Hose / Rock', 'Socken / Schuhe']))


class EntposenTest(unittest.TestCase):
    def test_eine_starre_bewegung_wird_genau_zurueckgerechnet(self):
        from scipy.spatial.transform import Rotation

        rest = np.random.default_rng(0).uniform(-0.5, 0.5, (400, 3))
        r = Rotation.from_euler('xyz', [20, -35, 50], degrees=True).as_matrix()
        posiert = rest @ r.T + np.array([0.3, 0.1, -0.2])
        aus = Kleidungsentposen(rest, posiert).ruhelage(posiert[:60] + 0.0)
        np.testing.assert_allclose(aus, rest[:60], atol=1e-6)

    def test_zwei_glieder_mit_verschiedener_bewegung_bleiben_je_bei_ihrem_glied(self):
        from scipy.spatial.transform import Rotation

        z = np.random.default_rng(1)
        a = z.normal(size=(300, 3)) * 0.06
        b = z.normal(size=(300, 3)) * 0.06 + np.array([1.0, 0.0, 0.0])
        rest = np.concatenate([a, b])
        ra = Rotation.from_euler('z', 30, degrees=True).as_matrix()
        rb = Rotation.from_euler('y', -60, degrees=True).as_matrix()
        posiert = np.concatenate([a @ ra.T, (b - [1, 0, 0]) @ rb.T + [1.5, 0.2, 0.0]])
        ent = Kleidungsentposen(rest, posiert)
        np.testing.assert_allclose(ent.ruhelage(posiert[:20]), rest[:20], atol=1e-3)
        np.testing.assert_allclose(ent.ruhelage(posiert[300:320]), rest[300:320], atol=1e-3)

    def test_falsche_form_wird_abgelehnt(self):
        with self.assertRaises(ValueError):
            Kleidungsentposen(np.zeros((10, 3)), np.zeros((11, 3)))

    def test_pruefen_meldet_rms_und_p95(self):
        rest = np.random.default_rng(2).uniform(-0.5, 0.5, (500, 3))
        aus = Kleidungsentposen(rest, rest + 0.1).pruefen(anzahl=100)
        self.assertLess(aus['rms_mm'], 0.01)
        self.assertEqual(set(aus), {'rms_mm', 'p95_mm'})


class ObjektTest(unittest.TestCase):
    def test_ein_punkt_mit_zwei_uv_wird_doppelt_angelegt(self):
        punkte = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=float)
        flaechen = np.array([[0, 1, 2], [0, 2, 3]])
        uv = np.array([[[0.0, 0.0], [0.5, 0.0], [0.5, 0.5]], [[0.9, 0.9], [0.5, 0.5], [0.0, 0.5]]])
        p, u, f = Kleidungsobjekt.punkte_mit_uv(punkte, flaechen, uv)
        self.assertEqual((len(p), len(u)), (5, 5))
        self.assertEqual(f.shape, (2, 3))
        # Punkt 0 steht zweimal da — mit je seiner UV.
        self.assertEqual(int(((p == [0, 0, 0]).all(axis=1)).sum()), 2)

    def test_glb_hat_kleidung_und_textur(self):
        punkte = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
        uv = np.array([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]])
        textur = np.full((64, 64, 3), 100, dtype=np.uint8)
        with Pruefablage.ordner('kleidung_') as ordner:
            pfad = Path(ordner) / 'k.glb'
            aus = Kleidungsobjekt.schreiben(pfad, punkte, np.array([[0, 1, 2]]), uv, textur)
            daten = pfad.read_bytes()
        self.assertEqual(aus['flaechen'], 1)
        self.assertEqual(daten[:4], b'glTF')
        self.assertIn(b'Kleidung', daten)


class HaarfarbeTest(unittest.TestCase):
    def test_belichtetes_haar_ist_die_hellere_haelfte(self):
        from Haar.haarteilung import Haarteilung

        f = np.concatenate([np.tile([50.0, 50.0, 50.0], (50, 1)), np.tile([150.0, 140.0, 140.0], (50, 1))])
        farbe = Haarteilung._farbe(f, np.ones(100))
        self.assertEqual(farbe['median'], [50, 50, 50])
        self.assertEqual(farbe['haar'], [150, 140, 140])

    def test_gleich_helle_flaechen_geben_ihre_farbe(self):
        from Haar.haarteilung import Haarteilung

        farbe = Haarteilung._farbe(np.tile([90.0, 80.0, 70.0], (10, 1)), np.ones(10))
        self.assertEqual(farbe['haar'], [90, 80, 70])


if __name__ == '__main__':
    unittest.main()
