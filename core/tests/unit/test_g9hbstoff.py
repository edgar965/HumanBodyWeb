# -*- coding: utf-8 -*-
u"""Daz-Kleidung auf einer HumanBody-Figur: Fläche und Stofflänge (30.09.2026).

Edgar mit Bild (GC T-Shirt auf Female_Caucasian): „die Drapierung ist bei den Brüsten
fehlerhaft, und die Brustwarzen schimmern durch". Zwei Bausteine, beide mit Kunstdaten geprüft:
`G9hbstoffkorrektur` (die GarmentCode-Stoffkorrektur, auch gegen die FLÄCHE — zwischen drei
Stoffpunkten stand die Brustwarze durch) und `G9hbstoffbruecke` (Position Based Dynamics: gedehnte
Kanten ziehen, gestauchte nicht, danach wieder aus der Haut). Der Körper ist hier eine Ebene
z = 0 mit Normalen +z; der Stoff ein Gitter darüber.
"""
import numpy as np
from django.test import SimpleTestCase
from scipy.spatial import cKDTree

from core.dienste.g9hbstoffbruecke import G9hbstoffbruecke
from core.dienste.g9hbstoffkorrektur import G9hbstoffkorrektur

ABSTAND = 0.006


class Ebene:
    u"""Attrappe eines `G9aufhumanbody`: `koerperflaeche()` = eine dicht besetzte Ebene z = 0."""

    def __init__(self, hoeckermitte=None, hoehe=0.0, radius=0.03):
        g = np.linspace(-0.2, 0.2, 161)
        x, y = np.meshgrid(g, g)
        z = np.zeros_like(x)
        if hoeckermitte is not None:
            r = np.hypot(x - hoeckermitte[0], y - hoeckermitte[1])
            z = np.where(r < radius, hoehe * np.cos(np.pi / 2 * r / radius) ** 2, 0.0)
        self.punkte = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
        self.normalen = np.tile([0.0, 0.0, 1.0], (len(self.punkte), 1))
        self.baum = cKDTree(self.punkte)

    def koerperflaeche(self):
        return self.punkte, self.normalen, self.baum


def gitter(n=11, abstand=0.01, z=ABSTAND):
    u"""(Punkte, Vierecke als Daz-`polylist` `[Gruppe, Material, a, b, c, d]`)."""
    g = (np.arange(n) - (n - 1) / 2) * abstand
    x, y = np.meshgrid(g, g)
    punkte = np.column_stack([x.ravel(), y.ravel(), np.full(n * n, z)])
    polys = []
    for i in range(n - 1):
        for j in range(n - 1):
            a = i * n + j
            polys.append([0, 0, a, a + 1, a + n + 1, a + n])
    return punkte, polys


class Signatur(SimpleTestCase):
    databases = set()

    def test_0_die_ebene_hat_die_signatur_des_traegers(self):
        import inspect

        from core.dienste.g9aufhumanbody import G9aufhumanbody
        self.assertEqual(set(inspect.signature(G9aufhumanbody.koerperflaeche).parameters),
                         set(inspect.signature(Ebene.koerperflaeche).parameters))


class Flaechen(SimpleTestCase):
    databases = set()

    def test_1_vierecke_werden_zwei_dreiecke_und_minus_eins_faellt_weg(self):
        f = np.array([[0, 1, 2, 3], [4, 5, 6, -1], [0, 1, 9, 2]])
        d = G9hbstoffkorrektur.dreiecke(f, anzahl=7)
        # [0,1,9,2] zeigt auf Punkt 9 von 7 — beide Hälften fallen weg; [4,5,6,-1] ist EIN Dreieck.
        self.assertEqual(sorted(map(tuple, d.tolist())), [(0, 1, 2), (0, 2, 3), (4, 5, 6)])

    def test_2_dreiecke_bleiben_dreiecke(self):
        d = G9hbstoffkorrektur.dreiecke(np.array([[0, 1, 2], [2, 1, 3]]), anzahl=4)
        np.testing.assert_array_equal(d, [[0, 1, 2], [2, 1, 3]])

    def test_3_umkreis_nimmt_nur_koerperpunkte_um_das_stueck(self):
        koerper = np.array([[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.05, 0.02, 0.0]])
        stoff = np.array([[0.0, 0.0, 0.01], [0.02, 0.0, 0.01]])
        np.testing.assert_array_equal(G9hbstoffkorrektur.umkreis(koerper, stoff, 0.05),
                                      [True, False, True])


class Laenge(SimpleTestCase):
    databases = set()

    def test_4_kanten_aus_der_polylist(self):
        _punkte, polys = gitter(3)
        k = G9hbstoffbruecke.kanten(polys, 9)
        self.assertEqual(len(k), 12)                  # 3×3 Punkte: 6 waagrecht + 6 senkrecht
        self.assertTrue((k[:, 0] < k[:, 1]).all())

    def test_5_gedehnter_stoff_zieht_sich_zusammen_und_bleibt_ueber_der_haut(self):
        ruhe, polys = gitter()
        kanten = G9hbstoffbruecke.kanten(polys, len(ruhe))
        gehoben = ruhe.copy()
        mitte = len(ruhe) // 2
        gehoben[mitte, 2] += 0.03                     # ein Punkt 3 cm hinausgedrückt: Kanten gedehnt
        aus = G9hbstoffbruecke.spannen(Ebene(), gehoben, ruhe, kanten, ABSTAND)
        vorher = G9hbstoffbruecke._gedehnt(gehoben, kanten[:, 0], kanten[:, 1],
                                           np.linalg.norm(ruhe[kanten[:, 1]] - ruhe[kanten[:, 0]], axis=1))
        nachher = G9hbstoffbruecke._gedehnt(aus, kanten[:, 0], kanten[:, 1],
                                            np.linalg.norm(ruhe[kanten[:, 1]] - ruhe[kanten[:, 0]], axis=1))
        self.assertGreater(vorher, 0)
        self.assertLess(nachher, vorher)
        self.assertLess(aus[mitte, 2], gehoben[mitte, 2])              # die Spitze gibt nach
        self.assertGreaterEqual(float(aus[:, 2].min()), ABSTAND - 1e-9)  # nichts in die Haut

    def test_6_ueber_einem_hoecker_spannt_der_stoff_die_nachbarn_mit(self):
        u"""Wie an der Brust: Der Körper hat einen Höcker, die Punkte darüber stehen gehoben.
        Die Nachbarn daneben, noch auf Ruhehöhe, ziehen mit — der Stoff spannt, statt am
        Höckerrand abzuknicken."""
        ruhe, polys = gitter(15)
        kanten = G9hbstoffbruecke.kanten(polys, len(ruhe))
        koerper = Ebene(hoeckermitte=(0.0, 0.0), hoehe=0.03, radius=0.025)
        _ab, idx = koerper.baum.query(ruhe)
        gehoben = ruhe.copy()
        gehoben[:, 2] = np.maximum(ruhe[:, 2], koerper.punkte[idx, 2] + ABSTAND)
        rand = np.hypot(ruhe[:, 0], ruhe[:, 1])
        ring = (rand > 0.03) & (rand < 0.045)         # gleich neben dem Höcker
        aus = G9hbstoffbruecke.spannen(koerper, gehoben, ruhe, kanten, ABSTAND)
        self.assertGreater(float(aus[ring, 2].mean()), float(gehoben[ring, 2].mean()) + 0.001)

    def test_7_gestauchter_stoff_bleibt_liegen(self):
        u"""Stoff wirft Falten, er drückt nicht auseinander: Ist jede Kante KÜRZER als in Ruhe,
        bewegt sich nichts."""
        ruhe, polys = gitter()
        kanten = G9hbstoffbruecke.kanten(polys, len(ruhe))
        gestaucht = ruhe * [0.9, 0.9, 1.0]
        aus = G9hbstoffbruecke.spannen(Ebene(), gestaucht, ruhe, kanten, ABSTAND)
        np.testing.assert_allclose(aus, gestaucht, atol=1e-12)

    def test_8_ohne_kanten_oder_mit_fremder_ruhe_unveraendert(self):
        ruhe, _polys = gitter(3)
        leer = np.zeros((0, 2), dtype=np.int64)
        np.testing.assert_array_equal(G9hbstoffbruecke.spannen(Ebene(), ruhe, ruhe, leer, ABSTAND), ruhe)
        kanten = G9hbstoffbruecke.kanten(gitter(3)[1], 9)
        np.testing.assert_array_equal(
            G9hbstoffbruecke.spannen(Ebene(), ruhe, ruhe[:4], kanten, ABSTAND), ruhe)
