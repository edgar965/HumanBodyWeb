# -*- coding: utf-8 -*-
"""„Kopf-Eigen" (Seite „Gesichtsform", 27.09.2026) — Rahmen, Schnitte, Löser, Vorgaben, Abschnitt.

Edgar: „ein Panel wo man die Gesichtsform malen kann, Schnitte aus unterschiedlichen Perspektiven (vorne,
seitlich, 5-10 Schnitte horizontal und vertikal)" und „diese neuen Morphs sollen in einem neuen Abschnitt
‚Kopf-Eigen' erscheinen". Ohne Daz-Bibliothek: Kunstlandmarken, ein Gitter als Netz, eine Halbkugel als
Gesicht, der Löser auf einer Punktreihe.
"""

import unittest
from unittest import mock

import numpy as np
from scipy import sparse

from Genesis9.gesichtsrahmen import G9gesichtsrahmen
from Genesis9.gesichtsschnitte import G9gesichtsschnitte
from Genesis9.schnittloeser import G9schnittloeser
from Genesis9.schnittvorgaben import G9schnittvorgaben


def landmarken():
    """(478, 3) — ein Kunstgesicht in Weltlage: Blick +Z, Augen auf y = 1,6 m, 62 mm auseinander."""
    g = np.full((478, 3), np.nan)
    g[33], g[263] = (-0.045, 1.6, 0.0), (0.045, 1.6, 0.0)
    g[133], g[362] = (-0.015, 1.6, 0.0), (0.015, 1.6, 0.0)
    g[10], g[152] = (0.0, 1.66, 0.0), (0.0, 1.49, 0.0)
    g[1] = (0.0, 1.56, 0.03)
    winkel = np.linspace(0, 2 * np.pi, len(G9gesichtsrahmen.OVAL), endpoint=False)
    for w, i in zip(winkel, G9gesichtsrahmen.OVAL, strict=True):
        g[i] = (0.07 * np.sin(w), 1.58 + 0.09 * np.cos(w), -0.01)
    return g


class RahmenTest(unittest.TestCase):
    def test_achsen_und_ursprung(self):
        r = G9gesichtsrahmen(landmarken())
        np.testing.assert_allclose(r.ursprung, (0.0, 1.6, 0.0))
        np.testing.assert_allclose(r.achsen, np.eye(3), atol=1e-12)  # x' rechts, y' oben, z' vorn

    def test_hin_und_zurueck(self):
        r = G9gesichtsrahmen(landmarken())
        p = np.array([[0.01, 1.62, 0.02]])
        np.testing.assert_allclose(r.heraus(r.hinein(p)), p)

    def test_ohne_traeger_kein_rahmen(self):
        g = landmarken()
        g[152] = np.nan
        with self.assertRaises(ValueError):
            G9gesichtsrahmen(g)

    def test_ovalbereich_und_innen(self):
        r = G9gesichtsrahmen(landmarken())
        von, bis = r.bereich(1, -0.02)  # waagerecht 2 cm unter den Augen
        self.assertLess(von, -0.06)
        self.assertGreater(bis, 0.06)
        quadrat = [(0, 0), (1, 0), (1, 1), (0, 1)]
        np.testing.assert_array_equal(G9gesichtsrahmen.innen(quadrat, [(0.5, 0.5), (2, 0.5)]), [True, False])


class SchnitteTest(unittest.TestCase):
    """Eine Halbkugel (r 0,1 m) vor dem Rahmen: das Profil ist ein Kreisbogen, z' = sqrt(r² − u² − lage²)."""

    def _kugel(self):
        import trimesh

        k = trimesh.creation.icosphere(subdivisions=5, radius=0.1)
        k.apply_translation((0.0, 1.6, -0.1 + 0.03))  # Scheitel 3 cm vor dem Ursprung
        return k.vertices, k.faces

    def test_profil_ist_der_kreisbogen(self):
        r = G9gesichtsrahmen(landmarken())
        punkte, flaechen = self._kugel()
        s = G9gesichtsschnitte(r)
        p = s.profile(punkte, flaechen, {'waagerecht': [0.0], 'senkrecht': []})[0]
        erwartet = np.sqrt(0.1 ** 2 - p['u'] ** 2) - 0.1 + 0.03
        ok = np.isfinite(p['z'])
        self.assertGreater(ok.mean(), 0.95)
        np.testing.assert_allclose(p['z'][ok], erwartet[ok], atol=5e-4)

    def test_lagen_im_oval(self):
        lagen = G9gesichtsschnitte(G9gesichtsrahmen(landmarken())).lagen(7, 5)
        self.assertEqual((len(lagen['waagerecht']), len(lagen['senkrecht'])), (7, 5))
        self.assertTrue(all(-0.09 < w < 0.09 for w in lagen['waagerecht']))

    def test_liste_hin_und_zurueck(self):
        p = [{'art': 'waagerecht', 'lage': 0.01, 'u': np.array([0.0, 0.001]), 'z': np.array([0.02, np.nan])}]
        liste = G9gesichtsschnitte.als_liste(p)
        self.assertEqual(liste[0]['z'], [20.0, None])
        zurueck = G9gesichtsschnitte.aus_liste(liste)[0]
        np.testing.assert_allclose(zurueck['z'][:1], [0.02])
        self.assertTrue(np.isnan(zurueck['z'][1]))


class LoeserTest(unittest.TestCase):
    """Eine Punktreihe (Nachbarn links/rechts), Enden fest: eine Vorgabe in der Mitte hebt glatt an."""

    def _reihe(self, n=41):
        a = sparse.lil_matrix((n, n))
        for i in range(n):
            nb = [j for j in (i - 1, i + 1) if 0 <= j < n]
            for j in nb:
                a[i, j] = 1.0 / len(nb)
        frei = np.ones(n, dtype=bool)
        frei[[0, 1, n - 2, n - 1]] = False
        return a.tocsr(), frei

    def test_vorgabe_wird_getroffen_und_laeuft_glatt_aus(self):
        m, frei = self._reihe()
        s = G9schnittloeser(m, frei).loesen([([20], [1.0], 0.003, 50.0)])
        self.assertAlmostEqual(s[20], 0.003, delta=2e-4)
        self.assertEqual(s[0], 0.0)
        self.assertTrue(np.all(np.diff(s[:21]) >= -1e-9))  # steigt zur Mitte, ohne Delle

    def test_feste_punkte_fallen_aus_der_zeile(self):
        m, frei = self._reihe()
        s = G9schnittloeser(m, frei).loesen([([0], [1.0], 0.01, 50.0)])
        np.testing.assert_allclose(s, 0.0)

    def test_nan_ist_keine_vorgabe(self):
        m, frei = self._reihe()
        np.testing.assert_allclose(G9schnittloeser(m, frei).loesen([([20], [1.0], np.nan, 50.0)]), 0.0)


class VorgabenTest(unittest.TestCase):
    def test_werte_nur_nahe_gueltigen_proben(self):
        u = np.arange(0, 0.010, 0.001)
        z = np.where(u < 0.005, u, np.nan)
        aus = G9schnittvorgaben.werte(u, z, [0.0025, 0.0035, 0.0045, 0.008])
        np.testing.assert_allclose(aus[:2], [0.0025, 0.0035])
        self.assertTrue(np.isnan(aus[2]))  # hinter der letzten gültigen Probe: keine Vorgabe
        self.assertTrue(np.isnan(aus[3]))

    def test_paare_ueber_art_und_lage(self):
        ist = {'schnitte': [{'art': 'waagerecht', 'lage': 0.0200}, {'art': 'senkrecht', 'lage': 0.0}]}
        ziel = {'schnitte': [{'art': 'waagerecht', 'lage': 0.02001}]}
        self.assertEqual(len(G9schnittvorgaben.paare(ist, ziel)), 1)


class AbschnittTest(unittest.TestCase):
    """Der Reglerabschnitt „Kopf-Eigen" zeigt nur Eigenmorphe mit Art „kopf" — und steht immer da."""

    def test_nur_kopfmorphe(self):
        import tempfile
        from pathlib import Path

        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.schnittmorph import G9schnittmorph

        with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[2] / 'tests')) as ordner:
            with mock.patch.object(G9eigenmorphe, 'ordner', classmethod(lambda cls: Path(ordner))):
                self.assertEqual(G9schnittmorph.bereich()['regler'], [])
                G9eigenmorphe.ablegen('Rest', [1], [[0.001, 0, 0]], {'quelle': 'mesh to 3d'})
                brief = {'art': 'kopf', 'anzeige': 'Kopf-Eigen · Probe'}
                G9eigenmorphe.ablegen('kopf_Probe', [1], [[0.001, 0, 0]], brief)
                regler = G9schnittmorph.bereich()['regler']
        self.assertEqual([r['name'] for r in regler], ['eigen:kopf_probe'])
        self.assertEqual(regler[0]['anzeige'], 'Kopf-Eigen · Probe')

    def test_ziel_aus_der_seite(self):
        from Genesis9.schnittmorph import G9schnittmorph

        seite = {
            'schnitte': [{'art': 'senkrecht', 'lage': 10, 'u': [0, 1], 'z': [5, None]}],
            'punkte': {'33': [-45.0, 0.0], '263': [None, 1]},
        }
        ziel = G9schnittmorph.ziel_aus_seite(seite)
        self.assertEqual(list(ziel['punkte']), [33])
        np.testing.assert_allclose(ziel['punkte'][33], [-0.045, 0.0])
        self.assertAlmostEqual(ziel['schnitte'][0]['lage'], 0.01)


if __name__ == '__main__':
    unittest.main()
