# -*- coding: utf-8 -*-
"""`G9knochenfeld`: Knochenoperationen als Verschiebungsfeld auf dem Kaefig (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM: UMA formt mit Knochen (skalieren, verschieben, drehen), nicht mit Verschiebungen; `G9umamorphe` rechnet dieselben Operationen auf der Genesis-Haut. Ein Fehler in der
Reihenfolge der Knochen, im Drehpunkt oder im Weg der Haut verschiebt ein ganzes Glied, ohne dass eine Zahl auffaellt. Geprueft an einer Kette aus drei Knochen entlang x
(`hip` 0…1, `arm` 1…2, `fore` 2…3) mit drei Hautpunkten, je einer voll an einem Knochen, ohne Genesis-Daten:

1. Skalieren am Knochen wirkt um sein Gelenk auf ihn UND seine Nachfahren, nicht auf den Elternknochen; die Gelenkversaetze der Nachfahren sind exakt.
2. Die Reihenfolge der Operationen in der Liste ist egal — der Elternknochen kommt zuerst (`ordnen`), sonst stuende der Drehpunkt des Kinds am alten Gelenk.
3. `pivot` ueberschreibt den Drehpunkt; `wirkt` begrenzt auf eine Liste (Adjust-Knochen: die Haut des Knochens ohne Nachfahren).
4. Verschieben und Drehen im Weltrahmen; ein Faktor ≤ 0 wird auf `MIN_FAKTOR` angehoben (keine gefaltete Haut).
5. Der Rahmen eines Knochens ist orthonormal, y entlang des Knochens.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.knochenfeld import G9knochenfeld


def kette():
    f = G9knochenfeld.__new__(G9knochenfeld)
    f.namen = ['hip', 'arm', 'fore']
    f.eltern = {'hip': None, 'arm': 'hip', 'fore': 'arm'}
    f.kopf = {'hip': np.array([0.0, 0, 0]), 'arm': np.array([1.0, 0, 0]), 'fore': np.array([2.0, 0, 0])}
    f.schwanz = {'hip': np.array([1.0, 0, 0]), 'arm': np.array([2.0, 0, 0]), 'fore': np.array([3.0, 0, 0])}
    f.tiefe = {'hip': 0, 'arm': 1, 'fore': 2}
    f.kinder = {'hip': ['arm'], 'arm': ['fore']}
    f.basis = np.array([[2.5, 0, 0], [1.5, 0, 0], [0.5, 0, 0]])       # Punkt 0 am Unterarm, 1 am Arm, 2 an der Huefte
    f.hautnamen = ['fore', 'arm', 'hip']
    f.index = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0]])
    f.gewicht = np.array([[1.0, 0, 0, 0], [1.0, 0, 0, 0], [1.0, 0, 0, 0]])
    f._rahmen = {}
    return f


class KnochenfeldTest(SimpleTestCase):
    databases = set()

    def test_1_skalieren_wirkt_um_das_gelenk_auf_knochen_und_nachfahren(self):
        f = kette()
        delta, gelenke = f.feld([{'knochen': 'arm', 'art': 'skalieren', 'wert': (2.0, 1.0, 1.0), 'welt': True}])
        np.testing.assert_allclose(delta[0], [1.5, 0, 0], atol=1e-9)       # 2,5 → 4,0 um x = 1
        np.testing.assert_allclose(delta[1], [0.5, 0, 0], atol=1e-9)       # 1,5 → 2,0
        np.testing.assert_allclose(delta[2], [0, 0, 0], atol=1e-9)         # die Huefte bleibt
        np.testing.assert_allclose(gelenke['arm'][0], [0, 0, 0], atol=1e-9)     # das eigene Gelenk steht
        np.testing.assert_allclose(gelenke['arm'][1], [1, 0, 0], atol=1e-9)     # sein Ende 2 → 3
        np.testing.assert_allclose(gelenke['fore'][0], [1, 0, 0], atol=1e-9)    # das Gelenk des Unterarms 2 → 3
        np.testing.assert_allclose(gelenke['fore'][1], [2, 0, 0], atol=1e-9)    # sein Ende 3 → 5
        np.testing.assert_allclose(gelenke['hip'][0], [0, 0, 0], atol=1e-9)

    def test_2_die_reihenfolge_in_der_liste_ist_egal(self):
        a = {'knochen': 'arm', 'art': 'skalieren', 'wert': (2.0, 1.0, 1.0), 'welt': True}
        b = {'knochen': 'fore', 'art': 'skalieren', 'wert': (1.5, 1.0, 1.0), 'welt': True}
        d1, g1 = kette().feld([a, b])
        d2, g2 = kette().feld([b, a])
        np.testing.assert_allclose(d1, d2, atol=1e-12)
        np.testing.assert_allclose(g1['fore'][1], g2['fore'][1], atol=1e-12)
        # Kind-Drehpunkt nach dem Elternknochen: fore-Gelenk steht nach `arm` bei x = 3, die Skalierung 1,5 darum: Punkt 0 (2,5 → 4,0 → 3 + 1,5·1 = 4,5)
        np.testing.assert_allclose(d1[0], [2.0, 0, 0], atol=1e-9)

    def test_3_pivot_ueberschreibt_den_drehpunkt_und_wirkt_begrenzt(self):
        f = kette()
        delta, _g = f.feld([{'knochen': 'arm', 'art': 'skalieren', 'wert': (2.0, 1.0, 1.0), 'welt': True, 'pivot': (0.0, 0.0, 0.0), 'wirkt': ['arm']}])
        np.testing.assert_allclose(delta[1], [1.5, 0, 0], atol=1e-9)       # 1,5 → 3,0 um den Ursprung
        np.testing.assert_allclose(delta[0], [0, 0, 0], atol=1e-9)         # nur `arm`, nicht der Unterarm
        np.testing.assert_allclose(delta[2], [0, 0, 0], atol=1e-9)

    def test_4_verschieben_im_weltrahmen_nur_auf_die_liste(self):
        f = kette()
        delta, gelenke = f.feld([{'knochen': 'arm', 'art': 'verschieben', 'wert': (0.0, 0.1, 0.0), 'welt': True, 'wirkt': ['arm']}])
        np.testing.assert_allclose(delta[1], [0, 0.1, 0], atol=1e-9)
        np.testing.assert_allclose(delta[0], [0, 0, 0], atol=1e-9)
        np.testing.assert_allclose(gelenke['arm'][0], [0, 0.1, 0], atol=1e-9)
        np.testing.assert_allclose(gelenke['fore'][0], [0, 0, 0], atol=1e-9)

    def test_5_drehen_um_das_gelenk(self):
        f = kette()
        delta, _g = f.feld([{'knochen': 'arm', 'art': 'drehen', 'wert': ((0.0, 0.0, 1.0), 90.0), 'welt': True, 'wirkt': ['arm']}])
        np.testing.assert_allclose(delta[1], [-0.5, 0.5, 0.0], atol=1e-9)  # (1,5; 0) um (1; 0) um 90° → (1; 0,5)

    def test_6_ein_faktor_null_faltet_die_haut_nicht(self):
        f = kette()
        delta, _g = f.feld([{'knochen': 'arm', 'art': 'skalieren', 'wert': (0.0, 1.0, 1.0), 'welt': True, 'wirkt': ['arm']}])
        np.testing.assert_allclose(delta[1], [-0.5 * (1 - G9knochenfeld.MIN_FAKTOR), 0, 0], atol=1e-9)

    def test_7_der_rahmen_ist_orthonormal_und_y_liegt_am_knochen(self):
        f = kette()
        r = f.rahmen('arm')
        np.testing.assert_allclose(r.T @ r, np.eye(3), atol=1e-9)
        np.testing.assert_allclose(r[:, 1], [1, 0, 0], atol=1e-9)
        self.assertGreater(np.linalg.det(r), 0.0, 'rechtshaendig')

    def test_8_ein_unbekannter_knochen_wird_uebergangen(self):
        delta, gelenke = kette().feld([{'knochen': 'gibt_es_nicht', 'art': 'skalieren', 'wert': (2, 2, 2), 'welt': True}])
        np.testing.assert_allclose(delta, 0.0, atol=1e-12)
        self.assertEqual(set(gelenke), {'hip', 'arm', 'fore'})
