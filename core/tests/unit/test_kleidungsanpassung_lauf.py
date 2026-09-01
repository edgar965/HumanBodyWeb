# -*- coding: utf-8 -*-
u"""`Anpassungslauf` — und der Körper, den er nicht anfassen darf.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`fit_garment` war 347 Zeilen lang. Beim Zerlegen in `Anpassungslauf`,
`Armmaske`, `Koerperpolster` und `Schrittboden` kam ein Fehler zum
Vorschein, der seit jeher darin steckte:

    inflated_body = body_verts            # KEINE Kopie
    ...
    inflated_body[crotch_body_mask] += ...

Bei `min_dist_mm = 0` zeigen beide Namen auf dasselbe Array, und die
Schrittvertiefung schreibt damit in die Körpervertices des Aufrufers.
Gemessen an `underwear/elvs_bow_bottom_panty`: **144 Vertices, bis zu
4 mm**. Erreichbar war das über `spurzubehoer.js`, das `min_dist` auf 0
setzt, wenn die Szene keinen Wert nennt — und weil `Kleidungsanpassung`
für jedes Stück derselben Szene dasselbe Körperarray weiterreicht,
addierte sich die Verformung von Stück zu Stück.

Der Test prüft das an einem kleinen künstlichen Körper, nicht an den
Produktionsdaten: Er soll auch dann noch laufen, wenn die Bibliothek
gerade nicht da ist.

Aufruf:  python manage.py test core.tests.unit.test_kleidungsanpassung_lauf
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from GarmentFitter.fitter import (Anpassungslauf, Armmaske,  # noqa: E402
                                  Koerperpolster, Schrittboden)


def _koerper(hoehe=1.7, ringe=24, ecken=16):
    u"""Eine stehende Röhre als Ersatzkörper: Vertices und Vierecke."""
    winkel = np.linspace(0, 2 * np.pi, ecken, endpoint=False)
    punkte, flaechen = [], []
    for i in range(ringe):
        z = hoehe * i / (ringe - 1)
        # Etwas Taille, damit die Normalen nicht alle gleich zeigen.
        r = 0.16 - 0.04 * np.sin(np.pi * i / (ringe - 1))
        for w in winkel:
            punkte.append([r * np.cos(w), r * np.sin(w), z])
    for i in range(ringe - 1):
        for j in range(ecken):
            a = i * ecken + j
            b = i * ecken + (j + 1) % ecken
            flaechen.append([a, b, b + ecken, a + ecken])
    return np.array(punkte, dtype=np.float64), np.array(flaechen)


def _kleid(koerper):
    u"""Ein grobes Netz um die untere Körperhälfte."""
    punkte = koerper[koerper[:, 2] < 0.9].copy()
    punkte *= np.array([1.25, 1.25, 1.0])
    n = len(punkte)
    flaechen = np.array([[i, (i + 1) % n, (i + 2) % n, (i + 3) % n]
                         for i in range(0, n - 4, 2)])
    return punkte, flaechen


class KoerperBleibtUnberuehrtTest(SimpleTestCase):
    u"""Der Aufrufer bekommt sein Körperarray unverändert zurück."""

    def _lauf(self, min_dist_mm, crotch_depth_mm):
        body, body_faces = _koerper()
        vorher = body.copy()
        verts, faces = _kleid(body)
        Anpassungslauf(verts, faces, body, body_faces=body_faces,
                       coordinate_system='blender',
                       min_dist_mm=min_dist_mm,
                       crotch_depth_mm=crotch_depth_mm).fahren()
        return np.abs(body - vorher)

    def test_ohne_polster_mit_schritttiefe(self):
        u"""DER FALL, DER FRÜHER SCHIEFGING: kein Polster, aber Schritttiefe."""
        abweichung = self._lauf(min_dist_mm=0.0, crotch_depth_mm=4.0)
        self.assertEqual(abweichung.max(), 0.0,
                         'fit_garment hat den Körper des Aufrufers verändert')

    def test_mit_polster(self):
        self.assertEqual(self._lauf(2.0, 4.0).max(), 0.0)

    def test_ohne_beides(self):
        self.assertEqual(self._lauf(0.0, 0.0).max(), 0.0)


class KoerperpolsterTest(SimpleTestCase):
    u"""Das Polster ist immer ein eigenes Array — auch bei Dicke 0."""

    def setUp(self):
        self.body, self.faces = _koerper()

    def test_eigenes_array_ohne_dicke(self):
        polster = Koerperpolster(self.body, self.faces,
                                 self.body[:, 0].mean(), min_dist_mm=0.0)
        self.assertIsNot(polster.netz, self.body)

    def test_dicke_wirkt_nach_aussen(self):
        u"""3 mm Polster heben jeden Punkt um genau 3 mm an."""
        polster = Koerperpolster(self.body, self.faces,
                                 self.body[:, 0].mean(), min_dist_mm=3.0)
        weg = np.linalg.norm(polster.netz - self.body, axis=1)
        self.assertAlmostEqual(float(weg.max()), 0.003, places=9)
        self.assertAlmostEqual(float(weg.min()), 0.003, places=9)

    def test_ohne_flaechen_zeigt_es_vom_schwerpunkt_weg(self):
        polster = Koerperpolster(self.body, None, self.body[:, 0].mean())
        laengen = np.linalg.norm(polster.normalen, axis=1)
        self.assertTrue(np.allclose(laengen, 1.0))


class ArmmaskeTest(SimpleTestCase):
    u"""Die beiden Mischrichtungen sind wirklich gegenläufig."""

    def setUp(self):
        self.body, _ = _koerper()

    def test_leere_maske_laesst_alles_liegen(self):
        maske = Armmaske.keine(self.body)
        self.assertFalse(maske.betroffen)
        verts = np.array([[1.0, 2.0, 3.0]])
        self.assertIs(maske.schuetzen(verts, None), verts)
        self.assertIs(maske.uebernehmen(verts, None), verts)
        self.assertIsNone(maske.sichern(verts))

    def test_roehre_hat_keine_arme(self):
        u"""Ein Körper ohne abstehende Arme darf keine Armmaske ergeben."""
        verts = self.body.copy()
        self.assertFalse(Armmaske(verts, self.body,
                                  self.body[:, 0].mean()).betroffen)

    def test_schuetzen_und_uebernehmen_sind_gegenlaeufig(self):
        u"""Dieselben Eingaben, entgegengesetztes Ergebnis.

        Genau diese Verwechslung sollte der Umbau ausschließen: In der
        alten Funktion standen beide Formeln sechsmal im Fließtext, mit
        vertauschten Operanden.
        """
        maske = Armmaske.keine(self.body)
        maske.betroffen = True
        maske.maske = np.array([True, False])
        maske.gewicht_3d = np.array([[0.25]])

        alt = np.array([[0.0, 0.0, 0.0]])
        neu = np.array([[4.0, 0.0, 0.0], [9.0, 9.0, 9.0]])
        geschuetzt = maske.schuetzen(neu.copy(), alt)
        uebernommen = maske.uebernehmen(neu.copy(), alt)
        # schuetzen: 0,25·alt + 0,75·neu = 3,0   (das Neue setzt sich durch)
        # uebernehmen: 0,25·neu + 0,75·alt = 1,0 (das Alte setzt sich durch)
        self.assertAlmostEqual(float(geschuetzt[0, 0]), 3.0)
        self.assertAlmostEqual(float(uebernommen[0, 0]), 1.0)
        # Was nicht in der Maske liegt, bleibt in beiden Fällen unberührt.
        self.assertAlmostEqual(float(geschuetzt[1, 0]), 9.0)
        self.assertAlmostEqual(float(uebernommen[1, 0]), 9.0)


class SchrittbodenTest(SimpleTestCase):
    u"""Boden bestimmen, anheben, halten."""

    def setUp(self):
        self.body, _ = _koerper()

    def test_kein_boden_ausserhalb_der_hoehenspanne(self):
        u"""Ein Stück weit über dem Körper bekommt keinen Schrittboden."""
        weit_oben = self.body.copy()
        weit_oben[:, 2] += 5.0
        boden = Schrittboden.bestimmen(weit_oben, self.body,
                                       self.body[:, 0].mean(), 6.0)
        self.assertFalse(boden.vorhanden)

    def test_leerer_boden_laesst_die_vertices_liegen(self):
        verts = np.array([[0.0, 0.0, -1.0]])
        boden = Schrittboden()
        self.assertIs(boden.anheben(verts, 0.006), verts)
        self.assertIs(boden.halten(verts), verts)

    def test_hoehe_liegt_ueber_dem_damm(self):
        boden = Schrittboden.bestimmen(self.body, self.body,
                                       self.body[:, 0].mean(), 6.0)
        self.assertTrue(boden.vorhanden)
        self.assertAlmostEqual(boden.hoehe - boden.damm_z, 0.006, places=9)

    def test_anheben_zieht_haengende_vertices_nach_oben(self):
        boden = Schrittboden(hoehe=0.5, koerpermitte_x=0.0, damm_z=0.494)
        verts = np.array([[0.0, 0.0, 0.30],     # mittig, tief → wird gehoben
                          [0.30, 0.0, 0.30]])   # weit außen  → bleibt liegen
        gehoben = boden.anheben(verts.copy(), 0.006)
        self.assertGreater(gehoben[0, 2], verts[0, 2])
        self.assertAlmostEqual(float(gehoben[1, 2]), 0.30)
        # 80 % der Lücke bis Boden+offset: 0,30 + 0,8·(0,506−0,30) = 0,4648
        self.assertAlmostEqual(float(gehoben[0, 2]), 0.4648, places=6)
