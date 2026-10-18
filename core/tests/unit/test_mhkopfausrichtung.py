# -*- coding: utf-8 -*-
"""`Mhkopfanker` und `Mhkopfausrichtung`: MakeHumans Kopf auf Genesis' Kopf legen (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM: Der Klon der Kleiderbibliothek legte MakeHumans Gesicht 26–30 mm hinter Genesis' Gesicht (gemessen an Nasenspitze und Kinn). Fuer Kleider fiel das nie auf, fuer
Nasen-, Mund- und Augenregler schon (Wangenregler wirkten zu 26 % an der Wange). Die Ausrichtung braucht Anker, die in beiden Netzen dasselbe meinen, und eine Abbildung, die am
Hals auf null ausläuft. Geprueft mit einem kuenstlichen Kopf (kein Netz, keine MakeHuman-Daten, Millisekunden):

1. Die sechs Anker (Nase, Kinn, Scheitel, Hinterkopf, Ohren) werden gefunden — das Kinn ist die Unterseite VOR der Halsflucht, nicht der tiefste Punkt des Halses.
2. Ist die Quelle eine bekannte Affinabbildung der Zielform (gestaucht, nach hinten verschoben), legt `berechnen` die Anker auf wenige Millimeter aufeinander.
3. Das Gewicht ist 0 am Hals, 1 ab Kinnhoehe, glatt dazwischen; `anwenden` und `linear` rechnen mit diesem Gewicht (Punkte mit Matrix und Versatz, Verschiebungen nur mit der Matrix).
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.mhkopfanker import Mhkopfanker
from core.dienste.mhkopfausrichtung import Mhkopfausrichtung


def kopf(y_mal=1.0, z_versatz=0.0):
    u"""Ein Koerper-Punkthaufen mit bekannten Ankern (Meter, y oben); `y_mal`/`z_versatz` verformen ihn."""
    punkte = {
        'scheitel': (0.0, 1.70, 0.00), 'nase': (0.0, 1.55, 0.12), 'kinn': (0.0, 1.48, 0.09), 'hinterkopf': (0.0, 1.62, -0.10),
        'ohr_l': (0.07, 1.58, 0.00), 'ohr_r': (-0.07, 1.58, 0.00),
        # Hals und Rumpf: duerfen kein Anker werden (Hals liegt unter dem Kinn und hinter der Nase, Schulter weit unterhalb)
        'hals': (0.0, 1.40, -0.03), 'brust': (0.0, 1.30, 0.10), 'huefte': (0.15, 0.95, 0.0), 'fuss': (0.1, 0.0, 0.05),
    }
    return {k: np.array([x, y * y_mal, z + z_versatz]) for k, (x, y, z) in punkte.items()}


class MhkopfankerTest(SimpleTestCase):
    databases = set()

    def test_1_die_sechs_anker_werden_gefunden(self):
        p = kopf()
        anker = Mhkopfanker.finden(np.array(list(p.values())))
        for name in Mhkopfanker.NAMEN:
            np.testing.assert_allclose(anker[name], p[name], atol=1e-9, err_msg=name)

    def test_1b_das_kinn_ist_nicht_der_hals(self):
        p = kopf()
        anker = Mhkopfanker.finden(np.array(list(p.values())))
        self.assertGreater(anker['kinn'][1], p['hals'][1])
        self.assertGreater(anker['kinn'][2], p['hals'][2])


class MhkopfausrichtungTest(SimpleTestCase):
    databases = set()

    def test_2_bekannte_abbildung_legt_die_anker_aufeinander(self):
        ziel = kopf()
        quelle = kopf(y_mal=0.9, z_versatz=-0.03)
        augen_ziel = [(0.03, 1.60, 0.07), (-0.03, 1.60, 0.07)]
        augen_quelle = [(0.03, 1.60 * 0.9, 0.07 - 0.03), (-0.03, 1.60 * 0.9, 0.07 - 0.03)]
        a = Mhkopfausrichtung.berechnen(np.array(list(quelle.values())), np.array(list(ziel.values())), augen_quelle, augen_ziel, y_null=1.20)
        rest = a.rest_mm()
        self.assertEqual(set(rest), set(Mhkopfanker.NAMEN))
        self.assertLess(max(rest.values()), 3.0, rest)

    def test_3_gewicht_null_am_hals_eins_ab_kinn_glatt_dazwischen(self):
        a = Mhkopfausrichtung(np.diag([1.1, 1.2, 1.0]), [0.0, 0.01, -0.02], y_null=1.4, y_voll=1.5)
        np.testing.assert_allclose(a.gewicht([1.3, 1.4, 1.45, 1.5, 1.6]), [0.0, 0.0, 0.5, 1.0, 1.0], atol=1e-12)

    def test_3b_anwenden_nimmt_punkte_mit_matrix_und_versatz_mit(self):
        a = Mhkopfausrichtung(np.diag([1.1, 1.2, 1.0]), [0.0, 0.01, -0.02], y_null=1.4, y_voll=1.5)
        oben = a.anwenden([[0.02, 1.6, 0.1]])
        np.testing.assert_allclose(oben, [[0.022, 1.6 * 1.2 + 0.01, 0.08]], atol=1e-12)
        unten = a.anwenden([[0.02, 1.3, 0.1]])
        np.testing.assert_allclose(unten, [[0.02, 1.3, 0.1]], atol=1e-12)

    def test_3c_verschiebungen_gehen_nur_mit_der_matrix_mit(self):
        a = Mhkopfausrichtung(np.diag([1.1, 1.2, 1.0]), [0.0, 0.01, -0.02], y_null=1.4, y_voll=1.5)
        delta = np.array([[0.01, 0.01, 0.01], [0.01, 0.01, 0.01]])
        neu = a.linear(delta, np.array([1.6, 1.3]))
        np.testing.assert_allclose(neu[0], [0.011, 0.012, 0.010], atol=1e-12)      # am Kopf: Matrix, KEIN Versatz
        np.testing.assert_allclose(neu[1], [0.010, 0.010, 0.010], atol=1e-12)      # am Hals: unveraendert
