# -*- coding: utf-8 -*-
u"""SMPL-X-Modell: Eltern, A-Haltung, Hautgewichte, Regler-Vorzeichen, Segmentierung.

WARUM (Edgar, 15.09.2026: „kannst du die SMPL Modelle auf SMPL-X umstellen
(also inkl. Gesichtsknochen)?"): Alles hier ist an den Modelldateien
GEMESSEN — das sind die Zahlen, die nicht geraten sein duerfen:

1. **Die Eltern der Datei sind die der Definition** (`Smplxskelett.ELTERN`
   gegen `kintree_table`), bei allen drei Geschlechtern.
2. **Die A-Haltung trifft GarmentCodes A40.** SMPL-X haelt die Arme in
   Ruhe schon 5,5 Grad gesenkt (SMPL 0,3); `Smplxkoerper.a40` dreht um die
   Differenz. Gemessen gegen `f_/m_smpl_average_A40.obj` (naechster Punkt,
   zentriert wie `Netzuebertrag`): Armwinkel 39,9/39,4 Grad, Median 4,9/5,5
   mm, p90 12,1/12,6 mm. Die Gegenprobe rechnet die 40 Grad OHNE die
   Differenz — dann p90 51/47 mm: das ist der Fehler, den der Test faengt.
3. **Vier von bis zu elf Gewichten je Punkt**: weggeschnittener Anteil
   Median 0, p99 0,7 %, max 4,6 %, 48 Punkte ueber 2 %.
4. **Regler-Vorzeichen**: b0 +1 macht die Frau +7,0 cm groesser, den Mann
   -7,7 cm kleiner (wie SMPL); b1 +1 macht BEIDE fuelliger (Taille +11,2 /
   +9,1 cm ueber `Smplmasse`) — bei SMPL war es umgekehrt.
5. **Die uebertragene Segmentierung** deckt alle 10.475 Punkte, hat die 24
   Teile des Tools, und Augaepfel wie Kiefer liegen im `head`.

Ohne Modelldateien (`SMPLX_MODELS_DIR`, eigene Lizenz, nicht im Repo) wird
uebersprungen. Ueber 1 s wegen der 121-MB-Dateien: deshalb LongRunner.
"""
import os
import unittest

import numpy as np
from django.conf import settings

from SMPL.xhaut import Smplxhaut
from SMPL.xkoerper import Smplxkoerper
from SMPL.xsegmentierung import Smplxsegmentierung
from SMPL.xskelett import Smplxskelett


def _obj_punkte(pfad):
    punkte = []
    with open(pfad, 'r', encoding='utf-8') as quelle:
        for zeile in quelle:
            if zeile.startswith('v '):
                t = zeile.split()
                punkte.append([float(t[1]), float(t[2]), float(t[3])])
    return np.asarray(punkte, dtype=np.float64)


def _zentriert(v):
    aus = np.asarray(v, dtype=np.float64).copy()
    aus[:, 1] -= aus[:, 1].min()
    aus[:, 0] -= (aus[:, 0].min() + aus[:, 0].max()) / 2.0
    aus[:, 2] -= (aus[:, 2].min() + aus[:, 2].max()) / 2.0
    return aus


def _naechste_mm(a, b):
    from scipy.spatial import cKDTree
    abstand, _ = cKDTree(_zentriert(b)).query(_zentriert(a), k=1)
    return abstand * 1000.0


class SmplxModellTest(unittest.TestCase):

    databases = set()
    _modelle = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = str(settings.SMPLX_MODELS_DIR)
        if not Smplxkoerper.vorhanden('female', cls.ordner):
            raise unittest.SkipTest('SMPL-X-Modelle fehlen (%s)' % cls.ordner)
        from GarmentCode.entwurf import Entwurf
        cls.bodies = os.path.join(Entwurf.REPO, 'assets', 'bodies')

    def modell(self, geschlecht):
        if geschlecht not in self._modelle:
            self._modelle[geschlecht] = Smplxkoerper.laden(geschlecht, self.ordner)
        return self._modelle[geschlecht]

    # ------------------------------------------------------------- 1. Eltern

    def test_eltern_der_datei_sind_die_der_definition(self):
        for geschlecht in ('female', 'male', 'neutral'):
            if not Smplxkoerper.vorhanden(geschlecht, self.ordner):
                continue
            modell = self.modell(geschlecht)
            self.assertEqual(tuple(int(e) for e in modell.parents), Smplxskelett.ELTERN)
            self.assertEqual(modell.J_regressor.shape, (55, 10475))
            self.assertEqual(modell.weights.shape, (10475, 55))
            self.assertEqual(modell.shapedirs.shape, (10475, 3, Smplxkoerper.BETAS))

    # ---------------------------------------------------------- 2. A-Haltung

    def _a40_pruefen(self, geschlecht, datei):
        pfad = os.path.join(self.bodies, datei)
        if not os.path.isfile(pfad):
            self.skipTest('GarmentCode-Klon ohne %s' % datei)
        modell = self.modell(geschlecht)
        eigen = modell.a40(None)
        fremd = _obj_punkte(pfad)
        gelenke = modell.J_regressor @ eigen
        for seite in ('l', 'r'):
            schulter, hand = gelenke[list(modell.ARM[seite])]
            d = hand - schulter
            winkel = np.degrees(np.arctan2(-d[1], abs(d[0])))
            self.assertAlmostEqual(winkel, 40.0, delta=1.0, msg='Armwinkel %s' % seite)
        abstand = _naechste_mm(eigen, fremd)
        self.assertLess(float(np.median(abstand)), 8.0)
        self.assertLess(float(np.percentile(abstand, 90)), 20.0)
        # Gegenprobe: 40 Grad OHNE die Ruhewinkel-Differenz (so rechnet SMPL)
        v_rest = modell.formen(None)
        rad = np.radians(40)
        falsch = modell.posieren(v_rest, {16: [0, 0, -rad], 17: [0, 0, rad]})
        falsch[:, 1] -= falsch[:, 1].min()
        self.assertGreater(float(np.percentile(_naechste_mm(falsch, fremd), 90)), 30.0,
                           'die Gegenprobe muesste danebenliegen')

    def test_weiblicher_a40_trifft_garmentcode(self):
        self._a40_pruefen('female', 'f_smpl_average_A40.obj')

    def test_maennlicher_a40_trifft_garmentcode(self):
        self._a40_pruefen('male', 'm_smpl_average_A40.obj')

    def test_kopf_zeigt_weiter_wie_der_hals_kiefer_und_augen_von_ihm_weg(self):
        u"""Sabotage: `Smplxgelenke._richtung` ohne den Kopf-Sonderfall ->
        der Kopf zeigt zum Mittel von Kiefer und Augen, nach vorn-unten."""
        from SMPL.xgelenke import Smplxgelenke
        gelenke = Smplxgelenke.aus_modell('female', self.ordner)
        a40 = self.modell('female').a40(None)
        knochen = {k['name']: k for k in gelenke.knochen(a40)}
        kopf = knochen['Head']
        self.assertGreater(kopf['schwanz'][1] - kopf['kopf'][1], 0.05, 'Kopf nach oben')
        vorn = abs(kopf['schwanz'][2] - kopf['kopf'][2])
        self.assertLess(vorn, 0.03, 'nicht nach vorn')
        kiefer = knochen['Jaw']
        self.assertLess(kiefer['schwanz'][1], kiefer['kopf'][1], 'Kiefer nach unten')
        self.assertEqual(knochen['Left_eye']['eltern'], 'Head')
        self.assertEqual(knochen['left_index1']['eltern'], 'Left_wrist')

    # ------------------------------------------------------------ 3. Gewichte

    def test_vier_gewichte_je_punkt_verlieren_wenig(self):
        haut = Smplxhaut.aus_modell('female', self.ordner)
        verlust = haut.verlust()
        self.assertLess(float(np.median(verlust)), 1e-6)
        self.assertLess(float(verlust.max()), 0.06)
        self.assertLess(int((verlust > 0.02).sum()), 100)
        index, gewicht = haut.fuer_punkte(10475)
        self.assertEqual(index.shape, (10475, 4))
        np.testing.assert_allclose(gewicht.sum(axis=1), 1.0, atol=1e-5)
        self.assertEqual(haut.knochennamen()[22], 'Jaw')

    # ------------------------------------------------- 4. Regler-Vorzeichen

    def _taille(self, geschlecht, v):
        from SMPL.masse import Smplmasse
        seg = Smplxsegmentierung.bauen(
            os.path.join(self.bodies, Smplxsegmentierung.DATEINAME), self.ordner)
        import yaml
        vorlage = {'female': 'f_smpl_average_A40',
                   'male': 'm_smpl_average_A40'}[geschlecht]
        pfad = os.path.join(self.bodies, vorlage + '.yaml')
        with open(pfad, 'r', encoding='utf-8') as q:
            masse = yaml.safe_load(q)['body']
        return Smplmasse(seg).roh(v, masse)['waist']

    def test_beta0_groesse_je_geschlecht_beta1_fuelle_bei_beiden(self):
        from SMPL.form import Smplform
        erwartet = {'female': +7.0, 'male': -7.7}
        for geschlecht, delta_cm in erwartet.items():
            modell = self.modell(geschlecht)

            def hoehe(betas):
                v = modell.formen(betas)
                return float(v[:, 1].max() - v[:, 1].min()) * 100.0
            self.assertAlmostEqual(hoehe([1.0]) - hoehe(None), delta_cm, delta=0.5)
            # der Regler „groesser" macht groesser — Vorzeichen aus Smplform
            gross = hoehe(Smplform.betas(geschlecht, 100, 0))
            self.assertGreater(gross, hoehe(None) + 10)
            taille0 = self._taille(geschlecht, modell.a40(None))
            taille1 = self._taille(geschlecht, modell.a40([0.0, 1.0]))
            self.assertGreater(taille1 - taille0, 5.0, 'b1 +1 fuelliger ' + geschlecht)
            betas = Smplform.betas(geschlecht, 0, 100)
            fuellig = self._taille(geschlecht, modell.a40(betas))
            self.assertGreater(fuellig, taille0 + 10, 'Fuelle +100 (%s)' % geschlecht)

    # ------------------------------------------------------ 5. Segmentierung

    def test_segmentierung_deckt_alle_punkte_und_gesicht_liegt_im_kopf(self):
        seg = Smplxsegmentierung.bauen(
            os.path.join(self.bodies, Smplxsegmentierung.DATEINAME), self.ordner)
        self.assertEqual(len(seg), 24)
        alle = set()
        for punkte in seg.values():
            alle.update(punkte)
        self.assertEqual(len(alle), 10475)
        gewichte = self.modell('female').weights
        kopf = set(seg['head'])
        for gelenk in ('Jaw', 'Left_eye', 'Right_eye'):
            nummer = Smplxskelett.index(gelenk)
            punkte = np.nonzero(gewichte.argmax(axis=1) == nummer)[0]
            im_kopf = sum(1 for p in punkte if int(p) in kopf)
            self.assertGreater(im_kopf, 0.95 * len(punkte), gelenk)
