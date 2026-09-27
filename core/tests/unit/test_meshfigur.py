# -*- coding: utf-8 -*-
"""Reiter „Mesh to 3D" — Reglerstufen, Optionen, Symmetrie des Eigenmorphs, Triangulation.

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
