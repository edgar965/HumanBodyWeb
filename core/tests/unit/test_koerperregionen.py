# -*- coding: utf-8 -*-
"""Regionen-Regler (`G9koerperregionen`, 08.10.2026): die Geometrie an Kunstdaten (Zylinder um eine Gliedachse), die Verdrahtung in Option, Lauf, Kette und Reglersatz am Quelltext.

Anlass: Hunyuan- und TRELLIS-Lauf desselben Fotos hatten je 9 Regler am Anschlag (Hals, Unterarm, Handgelenk, Oberschenkel, Unterschenkel, Knöchel); der Rest landete im namenlosen Eigenmorph. Sabotage-Gegenprobe:
in `_seite` das Vorzeichen der Seite (`vorzeichen`) vertauschen → `test_links_und_rechts_getrennt` muss rot werden.
"""

import sys
import unittest
from pathlib import Path

import numpy as np

WURZEL = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(WURZEL))

from Genesis9.koerperregionen import G9koerperregionen as R  # noqa: E402


def _zylinder(mitte_x, laenge=0.3, radius=0.04, n=40):
    """Punkte auf einem senkrechten Zylinder um die Achse bei x = `mitte_x` (y von 0 bis `laenge`), vier Ringe je Zentimeter; 4 cm liegen innerhalb des vollen Radius (6 cm minus 1,5 cm Rand)."""
    punkte = []
    for y in np.arange(-0.05, laenge + 0.05, 0.0025):
        w = np.linspace(0, 2 * np.pi, n, endpoint=False)
        punkte.append(np.c_[mitte_x + radius * np.cos(w), np.full(n, y), radius * np.sin(w)])
    return np.concatenate(punkte)


def _glied(x, bis=0.3):
    return {'l_forearm': np.array([x, 0.0, 0.0]), 'l_hand': np.array([x, bis, 0.0])}


E = {'kennung': 'probe', 'achse': ('forearm', 'hand'), 'seiten': ('l_',), 'fenster': (0.2, 0.8), 'anstieg': 0.1, 'abfall': 0.1,
     'radius_cm': 6.0, 'richtung': 'radial', 'weg_cm': 1.0}


class GeometrieTest(unittest.TestCase):
    def test_punkte_wandern_nach_aussen_und_nur_im_fenster(self):
        p = _zylinder(0.4)
        d = R._seite(E, 'l_', p, _glied(0.4))
        t = p[:, 1] / 0.3
        innen = (t > 0.2) & (t < 0.8)
        radial = (p - np.array([0.4, 0, 0])) * [1, 0, 1]
        radial /= np.linalg.norm(radial, axis=1, keepdims=True)
        self.assertAlmostEqual(float(np.linalg.norm(d[innen], axis=1).mean()), 0.01, places=4)         # 1,0 cm je Einheit
        self.assertGreater(float(((d[innen] * radial[innen]).sum(1) / np.linalg.norm(d[innen], axis=1)).min()), 0.999)   # genau radial nach außen
        self.assertEqual(float(np.linalg.norm(d[t < 0.05], axis=1).max()), 0.0)
        self.assertEqual(float(np.linalg.norm(d[t > 0.95], axis=1).max()), 0.0)

    def test_der_rand_faellt_weich_ab(self):
        p = _zylinder(0.4)
        d = np.linalg.norm(R._seite(E, 'l_', p, _glied(0.4)), axis=1)
        t = p[:, 1] / 0.3
        stufe = [float(d[(t > a) & (t < a + 0.02)].mean()) for a in np.arange(0.1, 0.2, 0.02)]
        self.assertEqual(stufe, sorted(stufe))                                  # steigt vor dem Fenster monoton
        self.assertLess(max(abs(np.diff(stufe))), 0.004)                        # keine Stufe (Hermite)

    def test_punkte_ausserhalb_des_radius_bleiben(self):
        p = _zylinder(0.4, radius=0.09)                                           # 9 cm: weiter als Radius 6 cm
        self.assertEqual(float(np.linalg.norm(R._seite(E, 'l_', p, _glied(0.4)), axis=1).max()), 0.0)

    def test_links_und_rechts_getrennt(self):
        """Die linke Region (x > 0) bewegt keinen Punkt der rechten Seite, auch wenn er innerhalb des Radius liegt (Oberschenkel liegen eng)."""
        rechts = _zylinder(-0.4)
        self.assertEqual(float(np.linalg.norm(R._seite(E, 'l_', rechts, _glied(0.4)), axis=1).max()), 0.0)
        mitte_rechts = _zylinder(-0.03)                                           # innerhalb 6 cm von einer Achse bei x = +0,03
        d = R._seite(E, 'l_', mitte_rechts, _glied(0.03))
        self.assertEqual(float(np.linalg.norm(d[mitte_rechts[:, 0] < -0.015], axis=1).max()), 0.0)

    def test_hinten_bewegt_nur_die_rueckseite_nach_hinten(self):
        e = dict(E, richtung='hinten')
        p = _zylinder(0.4)
        d = R._seite(e, 'l_', p, _glied(0.4))
        bewegt = np.linalg.norm(d, axis=1) > 1e-9
        self.assertTrue(bewegt.any())
        self.assertLessEqual(float(d[:, 2].max()), 0.0)                           # nie nach vorn (Genesis schaut nach +z)
        self.assertEqual(float(np.abs(d[:, [0, 1]]).max()), 0.0)
        self.assertTrue((p[bewegt, 2] < 0).all())                                 # nur Punkte der Rückseite

    def test_ohne_seitenpraefix_ist_die_achse_mittig(self):
        e = dict(E, achse=('neck1', 'head'), seiten=('',))
        gelenke = {'neck1': np.array([0.0, 0.0, 0.0]), 'head': np.array([0.0, 0.3, 0.0])}
        d = R._seite(e, '', _zylinder(0.0), gelenke)
        self.assertGreater(float(np.linalg.norm(d, axis=1).max()), 0.0099)


class KatalogTest(unittest.TestCase):
    def test_kennungen_bereich_und_grenzen(self):
        eintraege = R.eintraege()
        self.assertEqual(len(eintraege), len(R.KATALOG))
        namen = [e['name'] for e in eintraege]
        self.assertEqual(len(set(namen)), len(namen))
        for e in eintraege:
            self.assertTrue(e['name'].startswith('eigen:region_'), e)
            self.assertEqual((e['min'], e['max'], e['bereich'], e['art']), (-2.0, 2.0, 'region', 'form'))
            self.assertTrue(R.ist_standard(e['name'][len('eigen:'):]))
        self.assertFalse(R.ist_standard('region_quatsch'))
        self.assertFalse(R.ist_standard('ort_bauch'))

    def test_jeder_eintrag_hat_die_noetigen_felder(self):
        for e in R.KATALOG:
            self.assertEqual(len(e['achse']), 2)
            self.assertIn(e['richtung'], ('radial', 'hinten'))
            self.assertLess(e['fenster'][0], e['fenster'][1])
            self.assertGreater(e['radius_cm'], R.RAND_CM)
            self.assertTrue(all(s in ('', 'l_', 'r_') for s in e['seiten']))

    def test_bereich_fuer_das_bedienfeld(self):
        b = R.bereich()
        self.assertEqual((b['schluessel'], len(b['regler'])), ('region', len(R.KATALOG)))


class VerdrahtungTest(unittest.TestCase):
    """Die Kette ist erst dicht, wenn die letzte Schicht sie liest (`meshfigur.md`): Option → Lauf → Kette → Reglersatz → Ableitung."""

    def _text(self, *teile):
        return (WURZEL.joinpath(*teile)).read_text(encoding='utf-8')

    def test_option_im_katalog_und_in_pruefen(self):
        from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen as O

        katalog = {e['schluessel']: e for e in O.katalog()['optionen']}
        self.assertEqual(katalog['regionen']['vorgabe'], 'aus')
        self.assertEqual(O.pruefen({})['regionen'], 'aus')
        self.assertEqual(O.pruefen({'regionen': 'an'})['regionen'], 'an')
        self.assertEqual(O.pruefen({'regionen': 'unsinn'})['regionen'], 'aus')

    def test_lauf_kette_und_satz(self):
        self.assertIn("self.regionen_an = (koerperoptionen or {}).get('regionen') == 'an'",
                      self._text('HumanBodyWeb', 'core', 'dienste', 'engine2d3dkleiderkoerperlauf.py'))
        kette = self._text('HumanBodyWeb', 'core', 'dienste', 'meshfigurkette.py')
        self.assertIn("getattr(self.lauf, 'regionen_an', False)", kette)
        self.assertIn("Meshfigurregler(grund, gesperrt, satz, getattr(self.lauf, 'spielraum', 1.0))", kette)       # seit 08.10.2026 mit Spielraum
        regler = self._text('HumanBodyWeb', 'core', 'dienste', 'meshfigurregler.py')
        for stelle in ('G9reglerableitung.holen(self.satz,', 'G9reglerableitung.regler(self.satz,', 'G9reglerableitung.ablagepfad(self.satz,'):
            self.assertIn(stelle, regler)
        self.assertNotIn('self.SATZ,', regler)

    def test_ableitung_kennt_den_satz_und_fingert_die_kopfstufe_nicht_an(self):
        text = self._text('Genesis9', 'reglerableitung.py')
        self.assertIn("SATZ_REGIONEN = 'regionen'", text)
        self.assertIn("teil in (None, 'koerper')", text)                     # nur die Körperstufe bekommt die Regionen
        self.assertIn("'charaktere' if satz == cls.SATZ_REGIONEN and teil == 'kopf'", text)
        self.assertIn('G9koerperregionen.fassung()', text)                     # die Ablage trägt den Stand der Morphe im Namen

    def test_zweiseitig_in_der_formung_und_baubar_im_eigenmorph(self):
        self.assertIn("G9eigenmorphe.PRAEFIX + 'region_'", self._text('Genesis9', 'formung.py'))
        self.assertIn('G9koerperregionen', self._text('Genesis9', 'eigenmorphe.py'))


if __name__ == '__main__':
    unittest.main()
