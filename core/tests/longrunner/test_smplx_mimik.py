# -*- coding: utf-8 -*-
"""Mimik auf SMPL-X: der Übertrag der MB-Lab-Einheiten auf den SMPL-X-Kopf.

WARUM (Edgar, 16.09.2026: „Mimik auch auf SMPL-X"): Die Felder in
`smplx_basis.json` sind ÜBERTRAGEN, nicht gezeichnet — ob sie an der
richtigen Stelle landen, sagt nur eine Messung am Ergebnis:

1. Die Landmarken beider Köpfe liegen nach dem Thin-Plate-Spline aufeinander
   (Rest unter 0,1 mm); die Zuordnung in der Ebene: Median unter 5 mm.
2. `eyeClosedL` senkt das linke Oberlid (Band 0…+12 mm über der Augenmitte
   im Mittel mehr als 4 mm nach unten), lässt das rechte Auge und beide
   Augäpfel unberührt; `eyeClosedR` ist das Spiegelbild (gleich viele Punkte
   ±20 %).
3. `mouthSmile` hebt den linken Mundwinkel (> 2 mm) und zieht ihn nach außen
   (> 1 mm); `mouthOpenLarge` bringt das Kinn mehr als 15 mm hinunter.
4. Zunge und Pupillen fehlen in den Feldern; die versionierte Datei entspricht
   dem aktuellen Übertrag (kein veralteter Stand im Repo).

Sabotage-Gegenprobe: in `SmplxKopf.__init__` die Augäpfel zur Haut zählen
(`HAUTGELENKE` um 23, 24 erweitern) → Fall 2 rot (Augapfel bewegt sich).
Über 1 s (Modelldateien) — deshalb LongRunner.
"""

import json
import unittest

import numpy as np
from django.conf import settings

from humanbody_core.mimik.mblab_ausdruecke import MblabAusdruecke

from ...dienste.mimiksmplx import Mimiksmplx


class SmplxMimikTest(unittest.TestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mblab = settings.TOOLS_ROOT / "tools" / "MB-Lab" / "data"
        cls.daten = settings.HUMANBODY_ROOT / "data" / "humanBody"
        if not mblab.is_dir() or not Mimiksmplx.vorhanden():
            raise unittest.SkipTest("MB-Lab-Daten oder SMPL-X-Modell fehlen")
        cls.einheiten = MblabAusdruecke(str(mblab)).einheiten()
        cls.uebertrag = Mimiksmplx.uebertrag(cls.einheiten, cls.daten)
        cls.ziel = cls.uebertrag.ziel
        cls.marken = cls.ziel.landmarken()

    def feld(self, einheit, richtung="plus"):
        idx, d = self.uebertrag.uebertragen(self.einheiten[einheit][richtung])
        voll = np.zeros((len(self.ziel.punkte), 3))
        voll[idx] = d
        return voll

    def test_landmarken_liegen_aufeinander_und_zuordnung_ist_eng(self):
        bericht = self.uebertrag.bericht()
        self.assertLess(bericht["landmarken_rest_mm"], 0.1)
        self.assertLess(bericht["abstand_median_mm"], 5.0)
        self.assertGreater(bericht["skala"][0], 0.9)
        self.assertLess(bericht["skala"][0], 1.2)

    def test_lidschluss_links_trifft_das_linke_oberlid_und_sonst_nichts(self):
        d = self.feld("eyeClosedL")
        p = self.ziel.punkte
        auge = self.marken["auge_l"]
        nah = np.linalg.norm(p - auge, axis=1) < 0.022
        hoehe = (p[:, 1] - auge[1]) * 1000
        oberlid = nah & (hoehe >= 0) & (hoehe < 12) & self.ziel.haut
        self.assertGreater(int(oberlid.sum()), 50)
        self.assertLess(float(d[oberlid, 1].mean() * 1000), -4.0, "Oberlid senkt sich")
        rechts = p[:, 0] < -0.01
        self.assertEqual(float(np.abs(d[rechts]).max()), 0.0, "rechte Seite still")
        for seite in ("L", "R"):
            self.assertEqual(float(np.abs(d[self.ziel.augen[seite]]).max()), 0.0, "Augapfel %s still" % seite)
        links = int((np.linalg.norm(self.feld("eyeClosedL"), axis=1) > 1e-4).sum())
        rechts_n = int((np.linalg.norm(self.feld("eyeClosedR"), axis=1) > 1e-4).sum())
        self.assertLess(abs(links - rechts_n), 0.2 * links, "Spiegelbild")

    def test_laecheln_hebt_den_mundwinkel_und_kiefer_senkt_das_kinn(self):
        def am(feld, marke):
            i = np.linalg.norm(self.ziel.punkte - self.marken[marke], axis=1).argmin()
            return feld[i] * 1000

        smile = am(self.feld("mouthSmile"), "ecke_l")
        self.assertGreater(smile[1], 2.0, "Mundwinkel hoch")
        self.assertGreater(smile[0], 1.0, "Mundwinkel nach aussen")
        kinn = am(self.feld("mouthOpenLarge"), "kinn")
        self.assertLess(kinn[1], -15.0, "Kinn hinunter")

    def test_felder_ohne_zunge_und_datei_auf_dem_stand_des_codes(self):
        felder = self.uebertrag.felder(self.einheiten)
        self.assertFalse([n for n in felder if n.startswith(("tongue", "pupils"))])
        self.assertIn("eyeClosedL", felder)
        pfad = settings.BASE_DIR / "static" / "mimik" / Mimiksmplx.DATEI
        with open(pfad, encoding="utf-8") as datei:
            datei_felder = json.load(datei)
        self.assertEqual(sorted(datei_felder), sorted(felder))
        for einheit in ("eyeClosedL", "mouthSmile", "browsMidVert"):
            self.assertEqual(datei_felder[einheit]["plus"]["i"], felder[einheit]["plus"]["i"])
            np.testing.assert_allclose(
                datei_felder[einheit]["plus"]["d"], felder[einheit]["plus"]["d"], atol=1e-4
            )
