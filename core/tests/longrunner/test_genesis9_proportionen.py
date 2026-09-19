# -*- coding: utf-8 -*-
"""Proportionen: messen, formen, abbilden — an der Daz-Bibliothek (19.09.2026).

1. `G9proportionen.messen` liefert alle 19 Maße der Grundfigur, mit
   Endpunkten, die das Maß tatsächlich aufspannen; Schulter > Hüfte > Taille.
2. `G9proportionsformung.formen`: Hüfte +3 cm, Oberarm +1 cm, Nase −1 cm,
   Kopfhöhe +1 cm, Augenabstand +0,5 cm, Brustvorsprung +1 cm werden auf 0,2 cm getroffen, das Kopfgelenk wandert mit
   (nach unten, es liegt unter der Augenlinie), Maße ohne Vorgabe bleiben (bis auf die Schulter, die den
   Oberarmrand teilt) unter 0,3 cm; Sabotage (keine Skalierung) → rot.
3. `G9proportionenbild.projizieren`: Scheitel und Sohle liegen im Bild
   `RAND` vom Rand, `px_je_m` passt zur gemessenen Figurhöhe.
"""

import unittest

import numpy as np
from django.test import SimpleTestCase
from Genesis9.formung import G9formung
from Genesis9.pfade import G9pfade
from Genesis9.proportionen import G9proportionen
from Genesis9.proportionenbild import G9proportionenbild
from Genesis9.proportionsformung import G9proportionsformung
from Genesis9.reglerableitung import G9reglerableitung


def grundfigur():
    f = G9formung({})
    p, _, _ = G9reglerableitung.lage(f)
    gelenke = {e['name']: np.asarray(e['kopf'], float) for e in f.skelett().gelenkknochen()}
    return np.asarray(p, float), gelenke


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek fehlt')
class ProportionenTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p, cls.g = grundfigur()
        cls.pr = G9proportionen()

    def test_1_alle_masse_mit_endpunkten(self):
        b = self.pr.messen(self.p, self.g)
        self.assertEqual(set(b), set(G9proportionen.NAMEN))
        for k, e in b.items():
            a, z = np.asarray(e['a']), np.asarray(e['b'])
            # Die Endpunkte spannen das Maß entlang seiner Achse auf.
            self.assertGreater(np.linalg.norm(z - a), 0.9 * e['m'], k)
            self.assertGreater(e['m'], 0.02, k)
        cm = G9proportionen.in_cm(b)
        self.assertGreater(cm['schulter_breite'], cm['huefte_breite'])
        self.assertGreater(cm['huefte_breite'], cm['taille_breite'])
        self.assertGreater(cm['oberschenkel_dicke'], cm['oberarm_dicke'])

    def test_2_formen_trifft_die_vorgaben(self):
        vorher = G9proportionen.in_cm(self.pr.messen(self.p, self.g))
        ziele = {
            'huefte_breite': (vorher['huefte_breite'] + 3.0) / 100,
            'oberarm_dicke': (vorher['oberarm_dicke'] + 1.0) / 100,
            'nase_breite': (vorher['nase_breite'] - 1.0) / 100,
            'kopf_hoehe': (vorher['kopf_hoehe'] + 1.0) / 100,
            'augen_abstand': (vorher['augen_abstand'] + 0.5) / 100,
            'brust_vorsprung': (vorher['brust_vorsprung'] + 1.0) / 100,
            'quatsch': 0.09,  # unbekannt — wird ignoriert
        }
        formung = G9proportionsformung(self.pr)
        p2, g2, bericht = formung.formen(self.p, self.g, ziele)
        self.assertNotIn('quatsch', bericht)
        for k, ziel in ziele.items():
            if k == 'quatsch':
                continue
            self.assertAlmostEqual(bericht[k]['nachher'] * 100, ziel * 100, delta=0.2, msg=k)
        nachher = G9proportionen.in_cm(self.pr.messen(p2, g2))
        # Brusttiefe waechst mit dem Vorsprung (dieselbe Spitze), sonst bleibt alles.
        for k in vorher:
            if k in ziele or k in ('schulter_breite', 'brust_tiefe'):
                continue
            self.assertLess(abs(nachher[k] - vorher[k]), 0.3, k)
        # Gelenke im Fenster wandern mit: das Kopfgelenk (Schädelbasis, unter der Augen-
        # linie) rückt mit der Kopfhöhe nach unten; die Hüftgelenke liegen 10 cm über dem
        # breitesten Band und bleiben; die Hand ist unberührt.
        self.assertLess(g2['head'][1], self.g['head'][1] - 0.002)
        self.assertGreaterEqual(abs(g2['l_thigh'][0]), abs(self.g['l_thigh'][0]))
        self.assertLess(np.linalg.norm(g2['l_hand'] - self.g['l_hand']), 1e-6)
        # Sabotage: ohne Skalierung bleibt alles, wie es war.
        alt = G9proportionsformung._skalieren
        try:
            G9proportionsformung._skalieren = lambda self, *a, **kw: None
            nur = {'huefte_breite': ziele['huefte_breite']}
            _, _, kaputt = G9proportionsformung(self.pr).formen(self.p, self.g, nur)
            self.assertGreater(abs(kaputt['huefte_breite']['nachher'] - ziele['huefte_breite']) * 100, 2.0)
        finally:
            G9proportionsformung._skalieren = alt

    def test_3_projektion_und_massstab(self):
        bild = G9proportionenbild(self.p)
        unten, oben = float(self.p[:, 1].min()), float(self.p[:, 1].max())
        uv = bild.projizieren('vorn', [[0.0, oben, 0.0], [0.0, unten, 0.0]])
        breite, hoehe = G9proportionenbild.GROESSE['vorn']
        self.assertAlmostEqual(uv[0][0], breite / 2, delta=1.0)
        self.assertAlmostEqual(uv[1][1] - uv[0][1], bild.px_je_m('vorn') * (oben - unten), delta=1.0)
        rand = G9proportionenbild.RAND / (1 + 2 * G9proportionenbild.RAND) * hoehe
        self.assertAlmostEqual(uv[0][1], rand, delta=1.0)
        self.assertAlmostEqual(uv[1][1], hoehe - rand, delta=1.0)
        # Seitenansicht: die z-Achse liegt waagrecht im Bild, +z nach links (Blick von +x).
        uv = bild.projizieren('seite', [[0.0, oben, 0.1], [0.0, oben, -0.1]])
        self.assertAlmostEqual(abs(uv[1][0] - uv[0][0]), bild.px_je_m('seite') * 0.2, delta=1.0)
