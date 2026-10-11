# -*- coding: utf-8 -*-
"""`Dazgeograftanpassung` — das Daz-Geograft auf die vorgegebene Scham eines Blender-Imports anpassen (10.10.2026), an Kunstflächen ohne Daz-Bibliothek.

Edgar: „im Blender-File war die Scham ja vorgegeben, die sollst du mit Hilfe der Scham aus Genesis nachbauen". Gemessen am cute girl: die Haut der Figur des Imports liegt anders als die Grundfigur
(1,749 gegen 1,701 m), das Original steht bis 28 mm vor ihrer Haut.

Kunstwelt: Grundfigur = Platte z = 0, Figur des Imports = dieselbe Platte bei z = +10 mm (41 × 41 Punkte, Abstand 2 mm); das Stück ein Quadrat von 40 mm mit 11 × 11 Punkten (Abstand 4 mm) auf der
Grundfigur, dessen Rand der Ring ist; das Original eine Platte bei z = +20 mm.

1. `verlegen`: das Stück folgt der Verschiebung der Haut (z + 10 mm), mit und ohne Glättung der Verschiebung über das Netz.
2. `hoehe`: die Höhe über der Haut der Figur ist der Abstand entlang deren Normale.
3. `anpassen` (ohne Verfeinerung): die Mitte wird in Richtung des Originals gezogen (mindestens 60 % der 10 mm, nie darüber hinaus), die Ränder (Ring) bleiben auf der Haut (bis 0,3 mm).
4. Je steifer (`steifigkeit`), desto weniger folgt die Mitte: a = 12 bleibt hinter a = 1 zurück. Ohne Treffer des Strahls (Original weit weg, `SUCHE_M`) bleibt alles stehen.
5. `_laplace`: Zeilensummen null, symmetrisch, Grad = Zahl der Nachbarn.
6. Der Bericht von `anpassen` nennt Steifigkeit, Zahl der Treffer und die Verschiebung.

Sabotage-Gegenprobe (11.10.2026 im Speicher gelaufen, `ProjektTemp/_wegwerf/sabotage.py`: mit der Sabotage rot, ohne grün — Wortlaut als Quelltext-Änderung ungelaufen): `RAND_GEWICHT` auf 0 setzen macht Fall 3 rot (der Rand wandert mit); die Zeile `w[rand], ziel[rand] = …` entfernen ebenso.
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.dazgeograftanpassung import Dazgeograftanpassung


class DazgeograftanpassungTest(SimpleTestCase):
    databases = set()

    N, ABSTAND = 41, 0.002

    @classmethod
    def _platte(cls, z):
        """`{punkte, dreiecke}`: Gitter 41 × 41 (Abstand 2 mm, mittig) in der Ebene `z`."""
        n = cls.N
        punkte = np.array([[(i - n // 2) * cls.ABSTAND, (j - n // 2) * cls.ABSTAND, z] for j in range(n) for i in range(n)])
        dreiecke = []
        for j in range(n - 1):
            for i in range(n - 1):
                a = j * n + i
                dreiecke += [[a, a + 1, a + n + 1], [a, a + n + 1, a + n]]
        return {'punkte': punkte, 'dreiecke': np.array(dreiecke, dtype=np.int64)}

    @staticmethod
    def _stueck():
        """`(punkte, dreiecke, ring_punkte_haut)`: 11 × 11 Punkte (Abstand 4 mm, ±20 mm) in z = 0; der Ring: die 40 Randpunkte, als Hautpunkte der Platte (Gitterstellen)."""
        k = 11
        punkte = np.array([[(i - 5) * 0.004, (j - 5) * 0.004, 0.0] for j in range(k) for i in range(k)])
        dreiecke = []
        for j in range(k - 1):
            for i in range(k - 1):
                a = j * k + i
                dreiecke += [[a, a + 1, a + k + 1], [a, a + k + 1, a + k]]
        rand = [j * k + i for j in range(k) for i in range(k) if i in (0, k - 1) or j in (0, k - 1)]
        haut_n = DazgeograftanpassungTest.N
        ring = [int((round(punkte[r, 1] / 0.002) + haut_n // 2) * haut_n + round(punkte[r, 0] / 0.002) + haut_n // 2) for r in rand]
        return punkte, np.array(dreiecke, dtype=np.int64), ring

    def _anpassung(self, original_z=0.020):
        figur0, figur1 = self._platte(0.0), self._platte(0.010)
        punkte, dreiecke, ring = self._stueck()
        ziel = SimpleNamespace(punkte=self._platte(original_z)['punkte'], dreiecke=self._platte(original_z)['dreiecke'])
        return Dazgeograftanpassung(figur0, figur1, ring, ziel), punkte, dreiecke

    def test_1_das_stueck_folgt_der_verschiebung_der_haut(self):
        anpassung, punkte, dreiecke = self._anpassung()
        for d in (None, dreiecke):
            with self.subTest(glatt=d is not None):
                verlegt = anpassung.verlegen(punkte, d)
                self.assertLess(float(np.abs(verlegt[:, 2] - 0.010).max()), 1e-6)
                self.assertLess(float(np.abs(verlegt[:, :2] - punkte[:, :2]).max()), 1e-6)
        self.assertEqual(anpassung.bericht['verlegt_mm']['glaettung'], Dazgeograftanpassung.GLAETTUNG)

    def test_2_die_hoehe_ist_der_abstand_entlang_der_hautnormale(self):
        anpassung, _p, _d = self._anpassung()
        h = anpassung.hoehe(np.array([[0.0, 0.0, 0.030], [0.011, -0.007, 0.010], [0.0, 0.0, 0.004]]))
        self.assertLess(float(np.abs(h - [0.020, 0.0, -0.006]).max()), 1e-9)

    def _angepasst(self, steifigkeit=None, original_z=0.020):
        anpassung, punkte, dreiecke = self._anpassung(original_z)
        verlegt = anpassung.verlegen(punkte, dreiecke)
        return anpassung, verlegt, anpassung.anpassen(verlegt, dreiecke, steifigkeit, verfeinern=False)

    def test_3_die_mitte_geht_zum_original_und_der_ring_bleibt_auf_der_haut(self):
        _a, vorher, nachher = self._angepasst()
        mitte = 5 * 11 + 5
        gewinn = nachher[mitte, 2] - vorher[mitte, 2]
        self.assertGreater(float(gewinn), 0.6 * 0.010)
        self.assertLessEqual(float(gewinn), 0.010 + 1e-6, 'nie über das Original hinaus')
        rand = np.array([j * 11 + i for j in range(11) for i in range(11) if i in (0, 10) or j in (0, 10)])
        self.assertLess(float(np.abs(nachher[rand, 2] - vorher[rand, 2]).max()), 0.0003, 'der Ring bleibt auf der Haut')

    def test_3b_ohne_rand_gewicht_wanderte_der_rand_mit(self):
        with mock.patch.object(Dazgeograftanpassung, 'RAND_GEWICHT', 0.0), mock.patch.object(Dazgeograftanpassung, 'BAND_GEWICHT', 0.0):
            _a, vorher, nachher = self._angepasst()
        rand = np.array([j * 11 + i for j in range(11) for i in range(11) if i in (0, 10) or j in (0, 10)])
        self.assertGreater(float(np.abs(nachher[rand, 2] - vorher[rand, 2]).max()), 0.0003, 'die Gegenprobe: ohne Gewicht ist der Test rot')

    def test_4_je_steifer_desto_weniger_folgt_die_mitte(self):
        mitte = 5 * 11 + 5
        gewinn = {}
        for a in (1.0, 12.0):
            _x, vorher, nachher = self._angepasst(steifigkeit=a)
            gewinn[a] = float(nachher[mitte, 2] - vorher[mitte, 2])
        self.assertGreater(gewinn[1.0], gewinn[12.0])
        _x, vorher, nachher = self._angepasst(original_z=0.200)             # weiter als SUCHE_M (30 mm): kein Treffer
        self.assertLess(float(np.abs(nachher - vorher).max()), 1e-6)

    def test_5_der_laplace_hat_zeilensumme_null(self):
        _p, dreiecke, _r = self._stueck()
        laplace = Dazgeograftanpassung._laplace(dreiecke, 121)
        self.assertLess(float(np.abs(np.asarray(laplace.sum(axis=1))).max()), 1e-12)
        self.assertEqual(float(abs(laplace - laplace.T).max()), 0.0)
        grad = np.asarray(laplace.diagonal())
        self.assertEqual(int(grad[5 * 11 + 5]), 6, 'ein innerer Punkt mit Diagonalen hat sechs Nachbarn')

    def test_6_der_bericht_nennt_steifigkeit_treffer_und_weg(self):
        anpassung, _v, _n = self._angepasst(steifigkeit=3.0)
        b = anpassung.bericht['anpassen']
        self.assertEqual(b['steifigkeit'], 3.0)
        self.assertGreater(b['treffer_original'], 50)
        self.assertGreater(b['verschiebung_mm']['max'], 3.0)

    def test_7_feineres_netz_halbiert_steifigkeit_und_glaettung_und_vervierfacht_die_toleranz(self):
        """Stufe 2 (Punktabstand ≈ 2 mm statt 4 mm): `STUFE_STEIF` ×0,5 und `STUFE_TOLERANZ` ×4 je Stufe (gemessen 11.10.2026, Tabelle in `Dazgeograftanpassung`); Stufe 1 bleibt unverändert."""
        figur0, figur1 = self._platte(0.0), self._platte(0.010)
        punkte, dreiecke, ring = self._stueck()
        ziel = SimpleNamespace(punkte=self._platte(0.020)['punkte'], dreiecke=self._platte(0.020)['dreiecke'])
        eins = Dazgeograftanpassung(figur0, figur1, ring, ziel)
        zwei = Dazgeograftanpassung(figur0, figur1, ring, ziel, stufe=2)
        self.assertEqual((eins.steif_faktor, eins.toleranz_faktor), (1.0, 1.0))
        self.assertEqual((zwei.steif_faktor, zwei.toleranz_faktor), (0.5, 4.0))
        self.assertEqual((eins.ring_faktor, zwei.ring_faktor), (1.0, 1.0), 'seit 11.10.2026 keine Skalierung der Ringbreite: Absatz und Erhebung wurden damit nicht besser')
        zwei.verlegen(punkte, dreiecke)
        self.assertEqual(zwei.bericht['verlegt_mm']['glaettung'], Dazgeograftanpassung.GLAETTUNG * 0.5)
        zwei.anpassen(punkte, dreiecke, verfeinern=False)
        self.assertEqual(zwei.bericht['anpassen']['steifigkeit'], Dazgeograftanpassung.STEIFIGKEIT * 0.5)

    def test_8_der_ringfaktor_macht_die_festgehaltene_reihe_frei(self):
        """`RING_AN_M` ist in Metern gesetzt; `STUFE_RING` (Vorgabe 1: keine Skalierung, die Probe vom 11.10.2026 war kein Gewinn, Tabelle in `Dazgeograftanpassung`) skaliert es je Stufe. Mit ×0,5 bleibt
        die Reihe 4 mm vom Ring bei Stufe 1 mit Radius 4,5 mm festgehalten, bei Stufe 2 (2,25 mm) ist sie frei."""
        figur0, figur1 = self._platte(0.0), self._platte(0.010)
        punkte, dreiecke, ring = self._stueck()
        ziel = SimpleNamespace(punkte=self._platte(0.020)['punkte'], dreiecke=self._platte(0.020)['dreiecke'])
        reihe1 = 5 * 11 + 1                                              # Mitte der linken Seite, eine Reihe (4 mm) vom Ring
        weg = {}
        with mock.patch.object(Dazgeograftanpassung, 'RING_AN_M', 0.0045), mock.patch.object(Dazgeograftanpassung, 'BAND_GEWICHT', 0.0), mock.patch.object(Dazgeograftanpassung, 'STUFE_RING', 0.5):
            for stufe in (1, 2):
                anpassung = Dazgeograftanpassung(figur0, figur1, ring, ziel, stufe=stufe)
                verlegt = anpassung.verlegen(punkte, dreiecke)
                weg[stufe] = float(anpassung.anpassen(verlegt, dreiecke, verfeinern=False)[reihe1, 2] - verlegt[reihe1, 2])
        self.assertLess(abs(weg[1]), 0.0005, 'Stufe 1: die Reihe bleibt festgehalten (%.2f mm)' % (weg[1] * 1000))
        self.assertGreater(weg[2], 0.002, 'Stufe 2: die Reihe folgt dem Original (%.2f mm)' % (weg[2] * 1000))

    def test_9_ohne_fest_folgt_auch_der_rand_dem_original(self):
        """Am Umriss des Blender-Stücks zugeschnitten (`Dazgeograftumriss`) liegt der Rand IM Geograft, nicht auf der Haut: `fest=False` hält weder Ring noch Randband (11.10.2026)."""
        anpassung, punkte, dreiecke = self._anpassung()
        verlegt = anpassung.verlegen(punkte, dreiecke)
        rand = np.array([j * 11 + i for j in range(11) for i in range(11) if i in (0, 10) or j in (0, 10)])
        fest = anpassung.anpassen(verlegt, dreiecke, verfeinern=False)
        frei = anpassung.anpassen(verlegt, dreiecke, verfeinern=False, fest=False)
        self.assertLess(float(np.abs(fest[rand, 2] - verlegt[rand, 2]).max()), 0.0003, 'fest: der Ring bleibt auf der Haut')
        self.assertGreater(float(np.median(frei[rand, 2] - verlegt[rand, 2])), 0.006, 'frei: der Rand geht mit der Mitte zum Original (10 mm entfernt)')
