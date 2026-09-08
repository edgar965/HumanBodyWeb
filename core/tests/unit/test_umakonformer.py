# -*- coding: utf-8 -*-
u"""Der portierte `Kleidungskonformer` — bindet, hält Ruhe, folgt der Form.

Gerechnet wird auf einem Zylinder mit einer Hülle darum: klein genug für
einen Test, und mit bekannter Wahrheit — wer den Zylinder um 20 % weitet,
weiss, wohin die Hülle gehört.

DIE SCHARFE PROBE IST DIE RUHE
==============================
Derselbe Körper, unveränderte Form: Der Stoff MUSS liegenbleiben. Das ist
die Prüfung, die bei jedem Bezugs-, Einheiten- oder Rahmenfehler fällt —
und sie ist beim Bau dieses Ports dreimal gefallen (Einheit Meter gegen
Zentimeter, zwei verschiedene Normalen in einer Zerlegung, und UMAs
absolute Entartungsschwelle).
"""
import sys
import unittest
from pathlib import Path

import numpy as np

from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT)))

from UMA_Python import (Bindung, Einstellungen,               # noqa: E402
                        Kleidungskonformer)


def zylinder(radius, hoehe=1.0, ringe=24, stufen=16):
    u"""Ein geschlossener Zylindermantel als Dreiecksnetz."""
    winkel = np.linspace(0, 2 * np.pi, ringe, endpoint=False)
    y = np.linspace(0, hoehe, stufen)
    punkte = np.array([[radius * np.cos(w), h, radius * np.sin(w)]
                       for h in y for w in winkel])
    dreiecke = []
    for stufe in range(stufen - 1):
        for ring in range(ringe):
            a = stufe * ringe + ring
            b = stufe * ringe + (ring + 1) % ringe
            c = a + ringe
            d = b + ringe
            dreiecke += [[a, b, c], [b, d, c]]
    return punkte, np.array(dreiecke, dtype=np.int64)


class Bindenprobe(unittest.TestCase):

    databases = []

    def setUp(self):
        self.koerper, self.k_tri = zylinder(0.20)
        # Der "Stoff" sitzt 1 cm über der Haut, mit eigener Auflösung.
        self.stoff, self.s_tri = zylinder(0.21, ringe=18, stufen=12)

    def test_alles_wird_gebunden_und_der_abstand_stimmt(self):
        k = Kleidungskonformer(self.koerper, self.k_tri)
        b = k.binden('huelle', self.stoff, self.s_tri)
        bilanz = b.bilanz()

        self.assertEqual(bilanz['ungebunden'], 0)
        self.assertEqual(bilanz['gebunden'], len(self.stoff))
        # 10 mm nominal; der Zylinder ist ein Vieleck, deshalb etwas weniger.
        self.assertGreater(bilanz['abstand_median_mm'], 5.0)
        self.assertLess(bilanz['abstand_median_mm'], 12.0)

    def test_zu_weit_entferntes_wird_nicht_gebunden(self):
        u"""UMAs `maxTriangleDistance`: Was weit weg ist, gehört nicht an die
        Haut geheftet. Unsere `DreiecksProjektion` bindet dagegen immer."""
        weit, weit_tri = zylinder(0.90, ringe=18, stufen=12)
        k = Kleidungskonformer(self.koerper, self.k_tri,
                               Einstellungen(hoechstabstand_m=0.05,
                                             suchradius_m=0.05))
        b = k.binden('weit', weit, weit_tri)
        self.assertEqual(b.bilanz()['gebunden'], 0)

    def test_ruhe_ist_exakt_null_mit_tangentialem_anteil(self):
        k = Kleidungskonformer(self.koerper, self.k_tri,
                               Einstellungen(tangential_halten=True,
                                             glaetten=False))
        b = k.binden('huelle', self.stoff, self.s_tri)
        ruhe = k.anwenden(b)
        self.assertLess(np.abs(ruhe - self.stoff).max(), 1e-12)

    def test_der_stoff_folgt_dem_geweiteten_koerper(self):
        k = Kleidungskonformer(self.koerper, self.k_tri,
                               Einstellungen(tangential_halten=True,
                                             glaetten=False))
        b = k.binden('huelle', self.stoff, self.s_tri)

        weiter = self.koerper.copy()
        weiter[:, [0, 2]] *= 1.2
        neu = k.anwenden(b, weiter)

        # Der Abstand zur Achse muss um denselben Faktor gewachsen sein wie
        # der Körper, plus die unveränderte Stoffdicke.
        vorher = np.linalg.norm(self.stoff[:, [0, 2]], axis=1).mean()
        nachher = np.linalg.norm(neu[:, [0, 2]], axis=1).mean()
        self.assertGreater(nachher, vorher * 1.15)
        self.assertLess(nachher, vorher * 1.25)

    def test_zusatzabstand_lockert_das_stueck(self):
        u"""UMAs `additionalNormalOffset` — enger oder weiter ohne neue
        Simulation."""
        k = Kleidungskonformer(self.koerper, self.k_tri,
                               Einstellungen(glaetten=False))
        b = k.binden('huelle', self.stoff, self.s_tri)
        eng = k.anwenden(b)

        k.einstellungen.zusatzabstand_m = 0.02
        locker = k.anwenden(b)

        r_eng = np.linalg.norm(eng[:, [0, 2]], axis=1).mean()
        r_locker = np.linalg.norm(locker[:, [0, 2]], axis=1).mean()
        self.assertAlmostEqual(r_locker - r_eng, 0.02, places=2)


class SchutzGegenFalscheBindung(unittest.TestCase):
    u"""Die Prüfungen, die verhindern, dass etwas stumm falsch läuft."""

    databases = []

    def setUp(self):
        self.koerper, self.k_tri = zylinder(0.20)
        self.stoff, self.s_tri = zylinder(0.21, ringe=18, stufen=12)

    def test_bindung_an_falscher_einheit_wird_gemeldet(self):
        u"""Der Fehler, der beim Bau dieses Ports zuerst zuschlug: Körper in
        Metern, Stoff in Zentimetern. Damals lief die Rechnung durch und
        lieferte Zahlen — die Glättung verformte auch ungebundene Punkte."""
        k = Kleidungskonformer(self.koerper, self.k_tri)
        b = k.binden('falsch', self.stoff * 100.0, self.s_tri)

        taugt, grund = b.taugt()
        self.assertFalse(taugt)
        self.assertIn('Einheit', grund)
        with self.assertRaises(ValueError):
            k.anwenden(b)

    def test_bindung_eines_anderen_koerpers_wird_abgewiesen(self):
        u"""Der Fingerabdruck — UMAs `baseTopologyHash`, und dieselbe Lehre
        wie in `~/.claude/rules/artefakte-benennen.md`."""
        k1 = Kleidungskonformer(self.koerper, self.k_tri)
        b = k1.binden('huelle', self.stoff, self.s_tri)

        anderer, anderer_tri = zylinder(0.20, ringe=20)
        k2 = Kleidungskonformer(anderer, anderer_tri)
        with self.assertRaises(ValueError):
            k2.anwenden(b)

    def test_fingerabdruck_ist_zwischen_laeufen_gleich(self):
        u"""Pythons `hash()` auf Zeichenketten ist es NICHT (PYTHONHASHSEED);
        eine gespeicherte Bindung muss ihre Prüfung überleben."""
        einmal = Bindung.fingerabdruck(len(self.stoff), self.s_tri, 'huelle')
        nochmal = Bindung.fingerabdruck(len(self.stoff), self.s_tri, 'huelle')
        anders = Bindung.fingerabdruck(len(self.stoff), self.s_tri, 'hose')
        self.assertEqual(einmal, nochmal)
        self.assertNotEqual(einmal, anders)

    def test_koerper_mit_anderer_punktzahl_wird_abgewiesen(self):
        k = Kleidungskonformer(self.koerper, self.k_tri)
        b = k.binden('huelle', self.stoff, self.s_tri)
        with self.assertRaises(ValueError):
            k.anwenden(b, self.koerper[:-5])

    def test_unbekannte_einstellung_faellt_auf(self):
        with self.assertRaises(AttributeError):
            Einstellungen(glaetten_bitte=True)


class KollisionUndNaehte(unittest.TestCase):

    databases = []

    def test_eingesunkener_punkt_kommt_heraus(self):
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        k = Kleidungskonformer(koerper, k_tri,
                               Einstellungen(glaetten=False, schub_m=0.002))
        b = k.binden('huelle', stoff, s_tri)

        # Den Körper so weiten, dass er durch den Stoff tritt.
        dicker = koerper.copy()
        dicker[:, [0, 2]] *= 1.5
        with_korrektur = k.anwenden(b, dicker)

        k.einstellungen.kollision_beheben = False
        ohne = k.anwenden(b, dicker)

        r_mit = np.linalg.norm(with_korrektur[:, [0, 2]], axis=1).mean()
        r_ohne = np.linalg.norm(ohne[:, [0, 2]], axis=1).mean()
        self.assertGreaterEqual(r_mit, r_ohne)

    def _nahtfall(self, naehte_halten):
        u"""Ein Stoffnetz mit einer echten UV-Naht: derselbe Ort, zwei
        Punkte, keine Kante dazwischen.

        Damit die Naht überhaupt aufreissen KANN, wird die Bindung des
        Zwillings danach auf ein anderes Körperdreieck gelegt — im echten
        Netz passiert das von selbst, wenn der Fusspunkt auf einer Kante
        liegt und die Auswahl zwischen zwei gleich weiten Dreiecken kippt.
        """
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        stoff = np.vstack([stoff, stoff[0:1] + 1e-6])
        k = Kleidungskonformer(koerper, k_tri,
                               Einstellungen(glaetten=False,
                                             tangential_halten=False,
                                             naehte_halten=naehte_halten))
        b = k.binden('huelle', stoff, s_tri)
        nachbar_dreieck = int(np.flatnonzero(
            (k_tri == k_tri[b.dreieck[0]][0]).any(axis=1))[-1])
        b.dreieck[-1] = nachbar_dreieck
        b.bary[-1] = [1 / 3, 1 / 3, 1 / 3]

        weiter = koerper.copy()
        weiter[:, [0, 2]] *= 1.3
        neu = k.anwenden(b, weiter)
        return float(np.linalg.norm(neu[0] - neu[-1]))

    def test_naht_bleibt_geschlossen(self):
        u"""Die Gruppe bekommt EINE Verschiebung, der ursprüngliche Abstand
        der beiden Punkte (1,73 µm) bleibt also erhalten."""
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        stoff = np.vstack([stoff, stoff[0:1] + 1e-6])
        b = Kleidungskonformer(koerper, k_tri).binden('huelle', stoff, s_tri)
        self.assertEqual(b.nahtgruppen[0], b.nahtgruppen[-1])
        self.assertGreaterEqual(b.nahtgruppen[0], 0)

        self.assertLess(self._nahtfall(naehte_halten=True), 1e-5)

    def test_ohne_nahtgruppen_reisst_dieselbe_naht_auf(self):
        u"""Die Gegenprobe. Ohne sie prüfte der Test darüber nichts: Zwei
        Punkte 1 µm auseinander landen fast immer ohnehin zusammen."""
        offen = self._nahtfall(naehte_halten=False)
        self.assertGreater(offen, 1e-3,
                           'Die Naht müsste ohne Gruppen sichtbar aufgehen')
