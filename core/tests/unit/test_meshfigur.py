# -*- coding: utf-8 -*-
"""Reiter „Mesh to 3D" — Reglerstufen, Optionen, Symmetrie des Eigenmorphs, Triangulation, Kopfnetz
(Abgleich, Halsschnitt, Farbangleich, Zielnetz).

Edgar (27.09.2026): „erst die Regler … Größe, Gewicht usw., dann die Feinregler", „beim Gesicht eine
eigene Kette". Ohne Daz-Bibliothek, ohne Grafikkarte: die Stufen hängen nur an den Reglernamen, die
Triangulation rechnet mit Kunstkameras (`Meshfiguransichten.kamera` ist reine Geometrie).
"""

import unittest
from unittest import mock

import numpy as np

from core.dienste.meshfigurende import Meshfigurende
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.meshfigurregler import Meshfigurregler as R

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


class ReglerstufenTest(unittest.TestCase):
    """Die Prioritätsliste: Größe → Körpertyp → Bereiche; Kopf: Schädel → Züge → Rest."""

    def test_proportionen_und_masse_kommen_zuerst(self):
        for name in (
            'body_bs_ProportionHeight',
            'body_bs_ProportionLegsLength',
            'head_bs_ProportionNeckLength',
            'body_bs_BodyMass',
        ):
            self.assertEqual(R.stufe(name, 'koerper', 'koerper'), 1, name)

    def test_charaktere_und_koerpertypen_sind_stufe_zwei(self):
        self.assertEqual(R.stufe('NWDamira_figure_ctrl_Character-0xa3f2ca6', 'figur', 'koerper'), 2)
        self.assertEqual(R.stufe('body_bs_BodyHeavy', 'koerper', 'koerper'), 2)
        # Die Bauchmuskel-Details einer Figur sind Feinregler, kein Körpertyp.
        self.assertEqual(R.stufe('NW Damira Abs I-0xa55e627', 'koerper', 'koerper'), 3)
        self.assertEqual(R.stufe('body_bs_GluteSize', 'huefte', 'koerper'), 3)

    def test_ausgeschlossen_sind_verkleinern_und_grundfigur(self):
        for name in (
            'body_bs_ProportionSmaller',
            'body_bs_ProportionLarger',
            'body_bs_ProportionSmallerBO',
            'BaseFeminine_figure_ctrl_Character',
            'BaseFeminine_body_bs_Body',
        ):
            self.assertEqual(R.stufe(name, 'koerper', 'koerper'), 0, name)
        self.assertEqual(R.stufe('200_head_bs_Mouth Cavity Depth-0xa0f81c0', 'kopf', 'kopf'), 0)
        self.assertEqual(R.stufe('200_head_bs_Ears Gone-0xa0f8141', 'kopf', 'kopf'), 0)

    def test_kopf_schaedel_und_charakterkoepfe_vor_den_zuegen(self):
        for name in (
            'head_ctrl_ProportionHeadSize_scl',
            'NW Damira Head-0xa451edb',
            'DF-200KumikoHead',
            'Kin9_head_bs_Head',
            'MB_Olesia_Head_bs_head-0xa3c8d22',
            '200_head_bs_Cranium Height-0xa0f8173',
            '200_head_bs_Face Length-0xa0f818f',
        ):
            self.assertEqual(R.stufe(name, 'kopf', 'kopf'), 11, name)
        for name in (
            '200_head_bs_Nose Length-0xa0f81e1',
            '200_head_bs_Lip Upper Thin-0xa0f81bf',
            '200_head_bs_Chin Width-0xa0f81a7',
            '200_head_bs_Brows Height-0xa0f819c',
        ):
            self.assertEqual(R.stufe(name, 'kopf', 'kopf'), 12, name)
        self.assertEqual(R.stufe('200_head_bs_Ears_Size-0xa0f8142', 'kopf', 'kopf'), 13)

    def test_blinder_testfall_sperrt_alle_regler_der_referenzfigur(self):
        marken = R.sperrmarken({'NWDamira_figure_ctrl_Character-0xa3f2ca6': 1.0, 'body_bs_Navel_HD3': 1.0})
        self.assertEqual(marken, ['nwdamira'])
        regler = R({'BaseFeminine_figure_ctrl_Character': 1.0}, marken)
        for name in (
            'NW Damira Body-0xa451edb',
            'NW Damira Head-0xa451edb',
            'NW Damira Abs II-0xa55e627',
            'NWDamira_figure_ctrl_Character-0xa3f2ca6',
        ):
            self.assertEqual(regler.stufe_fuer(name, 'koerper', 'koerper'), 0, name)
        self.assertEqual(regler.stufe_fuer('P3DUrsula_body_bs_Body', 'koerper', 'koerper'), 2)

    def test_geaendert_nach_betrag_ohne_grundfigur(self):
        regler = R({'BaseFeminine_figure_ctrl_Character': 1.0})
        liste = regler.geaendert({'BaseFeminine_figure_ctrl_Character': 1.0, 'a': 0.2, 'b': -0.7, 'c': 0.005})
        self.assertEqual([k for k, _ in liste], ['b', 'a'])


class OptionenTest(unittest.TestCase):
    def setUp(self):
        self.referenzen = mock.patch.object(
            Meshfiguroptionen, '_referenzen', return_value=[('', '—'), ('nw_damira_8k', 'NW Damira 8K')]
        )
        self.referenzen.start()
        self.addCleanup(self.referenzen.stop)

    def test_vorgaben_ohne_eingabe(self):
        o = Meshfiguroptionen.pruefen({})
        self.assertEqual(
            (o['basis'], o['runden'], o['gesicht'], o['eigenmorph'], o['textur'], o['hoehe_cm']),
            ('feminine', '2', 'an', 'an', 'mesh', 0),
        )

    def test_unbekannte_werte_fallen_auf_die_vorgabe(self):
        o = Meshfiguroptionen.pruefen(
            {'basis': 'alien', 'runden': '9', 'referenz': 'gibt_es_nicht', 'hoehe_cm': 'viel', 'fremd': 1}
        )
        self.assertEqual((o['basis'], o['runden'], o['referenz'], o['hoehe_cm']), ('feminine', '2', '', 0))
        self.assertNotIn('fremd', o)

    def test_koerpergroesse_wird_geklemmt_und_referenz_angenommen(self):
        o = Meshfiguroptionen.pruefen({'hoehe_cm': 400, 'referenz': 'nw_damira_8k', 'daempfung': 'fest'})
        self.assertEqual((o['hoehe_cm'], o['referenz']), (250, 'nw_damira_8k'))
        self.assertEqual(Meshfiguroptionen.daempfung(o), 0.05)


class SymmetrieTest(unittest.TestCase):
    """Eigenmorph symmetrisch: gemittelt, wo beide Seiten getroffen sind, sonst die getroffene Seite."""

    def test_mitteln_und_fehlende_seite_uebernehmen(self):
        rest = np.array([[0.01, 0.0, 0.0], [-0.03, 0.0, 0.0], [0.0, 0.02, 0.0], [0.0, 0.0, 0.0]])
        gewicht = np.array([1.0, 1.0, 1.0, 0.0])
        spiegel = np.array([1, 0, 3, 2])  # 0 ↔ 1, 2 ↔ 3
        with mock.patch('Genesis9.netzbereiche.G9netzbereiche.spiegel', return_value=spiegel):
            aus, g = Meshfigurende.symmetrisch(rest, gewicht)
        # 0 und 1 gemittelt (x gespiegelt): (0,01 + 0,03) / 2 = 0,02 und −0,02
        np.testing.assert_allclose(aus[0], [0.02, 0.0, 0.0])
        np.testing.assert_allclose(aus[1], [-0.02, 0.0, 0.0])
        # 3 war nicht getroffen: bekommt den gespiegelten Wert von 2
        np.testing.assert_allclose(aus[3], [0.0, 0.02, 0.0])
        np.testing.assert_allclose(g, [1.0, 1.0, 1.0, 1.0])


class TriangulationTest(unittest.TestCase):
    """RANSAC-DLT über bekannte Kameras; Seitentausch einer Rückansicht wird erkannt."""

    def setUp(self):
        from meshfigur_ansichten import Meshfiguransichten
        from meshfigur_triangulation import Meshfigurtriangulation

        ziel = np.array([0.0, 0.9, 0.0])
        self.kameras = [
            Meshfiguransichten.kamera(ziel, a, 0.0, 4.0, 768, 1152) for a in (0, 45, 90, 180, 270)
        ]
        self.tri = Meshfigurtriangulation(self.kameras)
        self.projizieren = Meshfiguransichten.projizieren

    def _befunde(self, punkte):
        aus = []
        for k in self.kameras:
            u, v, _ = self.projizieren(k, punkte)
            aus.append(np.stack([u, v, np.ones(len(punkte))], 1))
        return aus

    def test_punkt_wird_exakt_wiedergefunden(self):
        punkte = np.array([[0.1, 1.4, 0.05], [-0.12, 0.5, -0.02]])
        ergebnis, treffer, fehler = self.tri.alle(self._befunde(punkte))
        np.testing.assert_allclose(ergebnis, punkte, atol=1e-6)
        self.assertTrue((treffer == 5).all())
        self.assertLess(float(np.max(fehler)), 1e-3)

    def test_ausreisser_einer_ansicht_faellt_heraus(self):
        punkte = np.array([[0.1, 1.4, 0.05]])
        befunde = self._befunde(punkte)
        befunde[2][0, :2] += 80.0  # eine Ansicht liegt 80 px daneben
        ergebnis, treffer, _ = self.tri.alle(befunde)
        np.testing.assert_allclose(ergebnis, punkte, atol=1e-5)
        self.assertEqual(int(treffer[0]), 4)

    def test_vertauschte_seiten_einer_ansicht_werden_getauscht(self):
        links, rechts = np.array([0.15, 1.35, 0.0]), np.array([-0.15, 1.35, 0.0])
        punkte = np.array([links, rechts])
        befunde = self._befunde(punkte)
        befunde[3] = befunde[3][[1, 0]]  # Rückansicht: links und rechts verwechselt
        gerichtet, getauscht = self.tri.seiten(befunde, punkte, ((0, 1),))
        self.assertEqual(getauscht, [3])
        np.testing.assert_allclose(gerichtet[3], self._befunde(punkte)[3])


class KopfabgleichTest(unittest.TestCase):
    """Eigenes Kopfnetz → Körper: Ähnlichkeit aus 478 Gesichtspunkten, Ausreißer, Halsschnitt, Farbe."""

    def setUp(self):
        from meshfigur_kopfabgleich import Meshfigurkopfabgleich

        self.k = Meshfigurkopfabgleich
        self.kopf = np.random.default_rng(3).normal(0.0, 0.05, (478, 3))
        w = np.radians(35.0)
        self.r = np.array([[np.cos(w), 0, np.sin(w)], [0, 1, 0], [-np.sin(w), 0, np.cos(w)]])
        self.s, self.t = 0.12, np.array([0.01, 1.6, 0.04])
        self.koerper = self.s * self.kopf @ self.r.T + self.t

    def test_massstab_drehung_verschiebung_exakt(self):
        m, befund = self.k.abgleichen(self.kopf, self.koerper)
        np.testing.assert_allclose(m[:3, :3], self.s * self.r, atol=1e-9)
        np.testing.assert_allclose(m[:3, 3], self.t, atol=1e-9)
        self.assertEqual(befund['genutzt'], 468, 'alle Punkte ohne die zehn der Iris')

    def test_ausreisser_fallen_heraus(self):
        koerper = self.koerper.copy()
        koerper[:40] += 0.05
        m, befund = self.k.abgleichen(self.kopf, koerper)
        np.testing.assert_allclose(m[:3, 3], self.t, atol=1e-6)
        self.assertEqual(befund['genutzt'], 428)

    def _schnitt(self, hals_unten, ohren=False, alles=False):
        koerper33 = np.full((33, 3), np.nan)
        koerper33[11], koerper33[12] = [0.18, 1.40, 0.0], [-0.18, 1.40, 0.0]
        if ohren:
            koerper33[7], koerper33[8] = [0.07, 1.62, -0.01], [-0.07, 1.62, -0.01]
        gesicht = np.tile([0.0, 1.62, 0.10], (478, 1))
        gesicht[152] = [0.0, 1.50, 0.06]
        hals = np.stack([np.zeros(50), np.linspace(hals_unten, 1.75, 50), np.zeros(50)], 1)
        ergebnis = self.k.schnitt(koerper33, gesicht, hals)
        return ergebnis if alles else ergebnis[2]

    def test_halsachse_durch_die_ohren_nicht_durchs_gesicht(self):
        _, achse, _ = self._schnitt(1.41, ohren=True, alles=True)
        self.assertGreater(achse[1], 0.99, 'Ohrenmitte über der Schulter: Achse fast senkrecht')
        _, achse, _ = self._schnitt(1.41, alles=True)
        self.assertLess(achse[1], 0.95, 'ohne Ohren die Gesichtsmitte (vorn am Kopf) — gekippt')

    def test_schnitt_halbe_halshoehe_ueber_dem_deckel(self):
        lang = self._schnitt(1.41)
        self.assertAlmostEqual(lang['ueber_schulter_cm'], 0.5 * lang['kinn_ueber_schulter_cm'], delta=0.1)
        kurz = self._schnitt(1.47)
        self.assertAlmostEqual(kurz['ueber_schulter_cm'], kurz['kopfnetz_unten_cm'] + 2.0, delta=0.1)
        self.assertIsNone(kurz['hinweis'])
        self.assertIsNotNone(self._schnitt(1.52)['hinweis'], 'Maske ohne Hals: Kinn kommt vom Körper')

    def test_farbangleich_linear_je_kanal(self):
        n = 400
        punkte = np.tile([0.0, 1.45, 0.0], (n, 1))
        normalen = np.tile([0.0, 0.0, 1.0], (n, 1))
        koerper = (punkte, normalen, np.tile([200, 150, 120], (n, 1)))
        # Weiße Strähnen vor dem Hals (Damira-Kopfnetz) zählen nicht: nur Hautfarbe geht ein.
        kopf = (
            np.tile(punkte, (2, 1)),
            np.tile(normalen, (2, 1)),
            np.array([[180, 150, 140]] * n + [[200, 200, 200]] * n),
        )
        ebene = (np.array([0.0, 1.45, 0.0]), np.array([0.0, 1.0, 0.0]))
        faktor, _ = self.k.farbfaktor(koerper, kopf, *ebene)
        erwartet = self.k._linear(np.array([200, 150, 120])) / self.k._linear(np.array([180, 150, 140]))
        np.testing.assert_allclose(faktor, erwartet, rtol=1e-9)
        # Zuerst dieselben Hautstellen im Gesicht (Wange 50), sonst der Hals.
        gesicht = np.full((478, 3), np.nan)
        gesicht[50] = [0.0, 1.45, 0.0]
        faktor, befund = self.k.farbfaktor(koerper, kopf, *ebene, gesicht)
        self.assertEqual(befund['quelle'], 'gesicht')
        np.testing.assert_allclose(faktor, erwartet, rtol=1e-9)
        gesicht[50] = [0.0, 1.70, 0.1]
        self.assertEqual(self.k.farbfaktor(koerper, kopf, *ebene, gesicht)[1]['quelle'], 'hals')
        faktor, befund = self.k.farbfaktor(tuple(x[:10] for x in koerper), kopf, *ebene)
        np.testing.assert_allclose(faktor, 1.0)
        self.assertIn('hinweis', befund)


class ZielnetzTest(unittest.TestCase):
    """Körper- und Kopfnetz am Hals verbunden: oben der Kopf, unten der Körper, erhobene Hand bleibt."""

    @staticmethod
    def _dreiecke(mitten, farbe):
        from meshfigur_scan import Meshfigurscan

        ecke = np.array([[0.0, 0, 0], [0.01, 0, 0], [0, 0.01, 0]])
        punkte = np.concatenate([np.asarray(m, dtype=float) + ecke for m in mitten])
        farben = np.tile(np.asarray(farbe, dtype=np.uint8), (len(punkte), 1))
        return Meshfigurscan(punkte, np.arange(len(punkte)).reshape(-1, 3), punktfarben=farben)

    def test_schnitt_und_farbe_je_netz(self):
        from meshfigur_zielnetz import Meshfigurzielnetz

        koerper = self._dreiecke([[0, 1.0, 0], [0, 1.6, 0], [0.5, 1.7, 0]], (200, 150, 120))
        kopf = self._dreiecke([[0, 1.3, 0], [0, 1.65, 0]], (100, 100, 100))
        ziel = Meshfigurzielnetz(koerper, kopf, [0, 1.5, 0], [0, 1, 0], 0.25, farbfaktor=[4.0, 1.0, 1.0])
        np.testing.assert_array_equal(ziel.index_koerper, [0, 2])
        np.testing.assert_array_equal(ziel.index_kopf, [1])
        self.assertEqual(len(ziel.punkte), 9, 'Punkte weggefallener Flächen fallen mit')
        farben = ziel.farben(np.array([0, 1, 2]), np.full((3, 3), 1 / 3))
        # Der Körper wird an den Kopf angeglichen (Rot linear / 4), der Kopf bleibt wie im Kopfnetz —
        # TRELLIS-Körper, Hunyuan-Kopf (27.09.2026): sonst würde das Gesicht so dunkel wie der Körper.
        self.assertLess(int(farben[0, 0]), 120, 'Körper rot angeglichen')
        np.testing.assert_array_equal(farben[0], farben[1])
        np.testing.assert_array_equal(farben[0, 1:], [150, 120])
        np.testing.assert_array_equal(farben[2], [100, 100, 100])

    def test_naht_zieht_den_untersten_kopf_auf_den_koerper(self):
        """Hunyuans Kopfnetz trägt am unteren Hals den Kinnschatten — an der Naht stand ein braunes Band.
        Der unterste Kopf wird auf den Körper darunter gezogen, weiter oben bleibt er, wie er ist."""
        from meshfigur_zielnetz import Meshfigurzielnetz

        vorn = [(x, 0.05) for x in (-0.02, 0.0, 0.02)]
        koerper = self._dreiecke([[x, y, z] for x, z in vorn for y in (1.47, 1.48)], (220, 160, 125))
        mitten = [[x, y, z] for x, z in vorn for y in (1.51, 1.52)] + [[0, 1.62, 0.05]]
        kopf = self._dreiecke(mitten, (190, 120, 85))
        ziel = Meshfigurzielnetz(koerper, kopf, [0, 1.5, 0], [0, 1, 0], 0.25)
        self.assertGreater(ziel.angleich.naht[1], 1.2, 'Kopf unten dunkler als der Körper')
        mitte = np.full((1, 3), 1 / 3)
        unten = ziel.farben(np.array([len(ziel.index_koerper)]), mitte)[0].astype(int)
        oben = ziel.farben(np.array([len(ziel.flaechen) - 1]), mitte)[0]
        self.assertLess(np.abs(unten - (220, 160, 125)).max(), 12, 'an der Naht wie der Körper')
        np.testing.assert_array_equal(oben, [190, 120, 85])

    def test_koerper_am_rumpf_auf_das_gesicht_des_kopfes(self):
        """Gemessen wird der Körper am Rumpf, nicht an seinem Gesicht: TRELLIS „fotos" war dort verschattet,
        der Körper wurde × 2,1 aufgehellt und lief über. Der Rückfall (`farbfaktor`) greift hier nicht."""
        from meshfigur_zielnetz import Meshfigurzielnetz

        rumpf = [[x, y, 0.1] for x in (-0.05, 0.0, 0.05) for y in (1.2, 1.25, 1.3)]
        gesicht = [[x, y, 0.08] for x in (-0.03, 0.0, 0.03) for y in (1.6, 1.63)]
        koerper = self._dreiecke(rumpf, (150, 100, 80))
        kopf = self._dreiecke(gesicht, (205, 145, 120))
        ziel = Meshfigurzielnetz(koerper, kopf, [0, 1.5, 0], [0, 1, 0], 0.25, farbfaktor=[4.0, 4.0, 4.0])
        self.assertEqual(ziel.angleich.befund['ton']['quelle'], 'rumpf gegen gesicht')
        farbe = ziel.farben(np.array([0]), np.full((1, 3), 1 / 3))[0].astype(int)
        self.assertLess(np.abs(farbe - (205, 145, 120)).max(), 3, 'Rumpf im Hautton des Gesichts')
