# -*- coding: utf-8 -*-
"""Haarkappe und enge Hose des Standmodells (05.10.2026, Edgar: „Haar immer noch zu hoch in der Mitte", „Haare seitlich braun, ein Haarmodell, das alles beinhaltet und eine einheitliche Farbe hat",
„Unterhose ist viel zu weit, in der Vorlage ist sie eng anliegend") und der Lauf nach Runden von Hand (`Engine2d3dKleiderlauf._von_hand`).

Kleine Kunstdaten, keine Netze und keine Datenbank: eine Kugel als Kopf, eine Kugelhülle als Hülle des Fotohaars, ein Rohr als Bein. Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.haarkappe import Haarkappe
from core.dienste.haarklemme import Haarklemme
from core.dienste.hosenkoerper import Hosenkoerper
from core.dienste.standhose import Standhose

MITTE = np.array([0.0, 1.6, 0.0])


def _kopf(radius=0.10, n_az=48, n_el=24):
    """Eine Kugel um MITTE ohne Pole (UV-Kugel) als Kopf: (Punkte, Dreiecke, Haut)."""
    el = np.radians(np.linspace(-80.0, 80.0, n_el))
    az = np.radians(np.linspace(0.0, 360.0, n_az, endpoint=False))
    punkte = np.array([[radius * np.cos(e) * np.sin(a), radius * np.sin(e), radius * np.cos(e) * np.cos(a)] for e in el for a in az]) + MITTE
    d = []
    for i in range(n_el - 1):
        for j in range(n_az):
            a, b, c, e = i * n_az + j, i * n_az + (j + 1) % n_az, (i + 1) * n_az + j, (i + 1) * n_az + (j + 1) % n_az
            d += [[a, b, c], [b, e, c]]
    haut = {'knochen': ['head'], 'index': np.zeros(len(punkte) * 4, dtype=np.int64), 'gewicht': np.tile([1.0, 0.0, 0.0, 0.0], len(punkte))}
    return punkte, np.array(d, dtype=np.int64), haut


def _karte(huelle):
    """Hülle des Fotohaars rundum — nur das Gesicht (Azimut bis 60° von vorn, unter 42° Höhe) hat kein Netzhaar."""
    karte = np.full((36, 72), huelle)
    el = ((np.arange(36) + 0.5) * 5.0 - 90.0)[:, None]
    az = (np.arange(72) + 0.5) * 5.0
    karte[(np.minimum(az, 360.0 - az)[None, :] <= 60.0) & (el < 42.0)] = np.nan
    return karte


def _kappe(huelle, radius=0.10):
    punkte, dreiecke, haut = _kopf(radius)
    netz = {'punkte': punkte, 'dreiecke': dreiecke, 'haut': haut}
    klemme = Haarklemme(_karte(huelle), MITTE)
    with mock.patch.object(Haarklemme, 'fuer', return_value=klemme):
        return Haarkappe(SimpleNamespace(), netz).flaeche(), netz


class DieHaarkappe(SimpleTestCase):
    def test_die_kappe_liegt_um_die_dicke_des_netzhaars_ueber_der_haut(self):
        (punkte, dreiecke, _haut, _uv, _n, daten), _netz = _kappe(0.115)
        r = np.linalg.norm(punkte - MITTE, axis=1)
        self.assertAlmostEqual(float(r.max()), 0.115, places=3)               # oben: Hülle des Fotohaars
        self.assertGreater(float(r.min()), 0.10 + Haarkappe.RAND_DICKE - 0.0005)  # nirgends in der Haut (Schnittpunkte liegen auf den Kanten der Kugel, 0,2 mm innen)
        self.assertAlmostEqual(daten['dicke_oben_mm'], 15.0, places=0)
        self.assertGreater(len(dreiecke), 100)

    def test_die_dicke_ist_nach_unten_und_oben_begrenzt(self):
        (dünn, *_r1), _n1 = _kappe(0.09)
        (dick, *_r2), _n2 = _kappe(0.30)
        r_duenn = np.linalg.norm(dünn - MITTE, axis=1)
        r_dick = np.linalg.norm(dick - MITTE, axis=1)
        self.assertAlmostEqual(float(r_duenn.max()), 0.10 + Haarkappe.DICKE[0], places=3)
        self.assertAlmostEqual(float(r_dick.max()), 0.10 + Haarkappe.DICKE[1], places=3)

    def test_das_gesicht_und_der_nacken_bleiben_frei(self):
        (punkte, *_rest), _netz = _kappe(0.115)
        v = punkte - MITTE
        el = np.degrees(np.arcsin(v[:, 1] / np.linalg.norm(v, axis=1)))
        von_vorn = np.abs(np.degrees(np.arctan2(v[:, 0], v[:, 2])))
        self.assertGreater(float(el.min()), Haarkappe.UNTEN - 4.0)             # die Schnittpunkte folgen der Linie bis auf die Auflösung der Felder (5°; an Kunstdaten −40,5°)
        self.assertGreater(float(el[von_vorn < 40.0].min()), 38.0)             # Gesicht und Stirn: das Netz hat dort kein Haar (Grenze bei 42°)

    def test_die_ohren_bleiben_frei(self):
        (punkte, *_rest), _netz = _kappe(0.115)
        v = punkte - MITTE
        el = np.degrees(np.arcsin(v[:, 1] / np.linalg.norm(v, axis=1)))
        von_vorn = np.abs(np.degrees(np.arctan2(v[:, 0], v[:, 2])))
        ohr = (von_vorn > 62.0) & (von_vorn < Haarkappe.OHR[0] - 5.0)        # Schläfe und Ohr (das Gesicht darunter hat in der Kunstkarte kein Netzhaar)
        self.assertTrue(ohr.any())
        self.assertGreater(float(el[ohr].min()), Haarkappe.OHR[1] - 5.0)

    def test_die_dicke_laeuft_an_der_haarlinie_aus(self):
        (punkte, *_rest), _netz = _kappe(0.115)
        v = punkte - MITTE
        r = np.linalg.norm(v, axis=1)
        el = np.degrees(np.arcsin(v[:, 1] / r))
        hinten = (np.abs(np.degrees(np.arctan2(v[:, 0], v[:, 2]))) > 170.0)
        self.assertLess(float(r[hinten & (el < -36.0)].max()), 0.10 + 0.0115)   # am unteren Rand im Nacken kaum Auftrag
        self.assertGreater(float(r[hinten & (el > 40.0)].min()), 0.10 + 0.012)  # weiter oben die volle Dicke

    def test_das_linienfeld_ist_innen_positiv_und_aussen_negativ(self):
        feld = Haarkappe._linienfeld(_karte(0.115))
        self.assertGreater(float(feld[35, 0]), 0.0)                             # Scheitel
        self.assertGreater(float(feld[18, 36]), 0.0)                            # Hinterkopf auf Augenhöhe (Azimut 180°)
        self.assertLess(float(feld[18, 0]), 0.0)                                # Gesicht (Azimut 0°, Höhe 2,5°)
        self.assertLess(float(feld[18, 19]), 0.0)                               # Ohr (Azimut 97,5°)
        self.assertLess(float(feld[3, 36]), 0.0)                                # unter dem Nacken
        self.assertGreater(float(feld[30, 71]), 0.0)                            # der Azimut läuft um: 357,5° gehört zu 0° und liegt über dem Gesicht im Haar

    def test_jedes_dreieck_hat_eigene_eckpunkte_mit_uv_normale_und_haut(self):
        (punkte, dreiecke, haut, uv, normalen, _daten), _netz = _kappe(0.115)
        self.assertEqual(len(punkte), 3 * len(dreiecke))
        self.assertEqual(len(punkte), len(uv))
        self.assertEqual(len(punkte), len(normalen))
        self.assertEqual(np.asarray(haut['index']).reshape(-1, 4).shape[0], len(punkte))
        self.assertEqual(int(dreiecke.max()), len(punkte) - 1)
        self.assertGreater(float(uv.min()), 0.0)                                  # Würfelabbildung um die Mitte: keine Naht, keine Pole
        self.assertLess(float(uv.max()), 1.0)
        np.testing.assert_allclose(np.linalg.norm(normalen, axis=1), 1.0, atol=1e-6)

    def test_die_dreiecke_zeigen_nach_aussen_wie_die_haut(self):
        (punkte, dreiecke, *_rest), _netz = _kappe(0.115)
        fn = np.cross(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 0]])
        aussen = punkte[dreiecke].mean(axis=1) - MITTE
        nach_aussen = float(((fn * aussen).sum(axis=1) > 0.0).mean())
        self.assertGreater(nach_aussen, 0.9)                     # an Kunstdaten 97 %: die übrigen sind Streifen an der Haarlinie, wo die Dicke steil wächst

    def test_ohne_huelle_keine_kappe(self):
        punkte, dreiecke, haut = _kopf()
        netz = {'punkte': punkte, 'dreiecke': dreiecke, 'haut': haut}
        with mock.patch.object(Haarklemme, 'fuer', return_value=None):
            self.assertIsNone(Haarkappe(SimpleNamespace(), netz).flaeche())

    def test_leere_felder_der_huelle_werden_aus_den_nachbarn_gefuellt(self):
        karte = np.full((36, 72), 0.11)
        karte[10:14, 20:30] = np.nan
        voll = Haarkappe._fuellen(karte)
        self.assertFalse(np.isnan(voll).any())
        self.assertAlmostEqual(float(voll[12, 25]), 0.11, places=3)
        self.assertIsNone(Haarkappe._fuellen(np.full((36, 72), np.nan)))

    def test_das_bild_hat_eine_mittlere_farbe_und_kein_nahtsprung(self):
        ordner = Path(tempfile.mkdtemp(prefix='kappe_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')))
        try:
            from PIL import Image
            pfad = Haarkappe.bild([0.5, 0.5, 0.5], ordner / 'k.png')
            a = np.asarray(Image.open(pfad).convert('RGB'), dtype=np.float64)
            self.assertAlmostEqual(float(a.mean()) / 255.0, 0.5, delta=0.03)
            self.assertLess(float(np.abs(a[:, 0] - a[:, -1]).mean()), float(np.abs(a[:, 0] - a[:, 256]).mean()) + 5.0)   # links und rechts schließen aneinander an
            self.assertAlmostEqual(float(a[..., 0].std() / a[..., 0].mean()), Haarkappe.KONTRAST, delta=0.04)
        finally:
            shutil.rmtree(ordner, ignore_errors=True)

    def test_das_teil_ist_ein_haarteil_mit_einer_gruppe_und_einer_farbe(self):
        ordner = Path(tempfile.mkdtemp(prefix='kappe_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')))
        try:
            punkte, dreiecke, haut = _kopf()
            netz = {'punkte': punkte, 'dreiecke': dreiecke, 'haut': haut}
            ablage = SimpleNamespace(arbeit=lambda name='': ordner / name)
            with mock.patch.object(Haarklemme, 'fuer', return_value=Haarklemme(np.full((36, 72), 0.115), MITTE)):
                teil = Haarkappe(ablage, netz).teil([0.5, 0.5, 0.5])
            self.assertEqual((teil['art'], teil['sorte']), ('haar', Haarkappe.SORTE))
            self.assertEqual(len(teil['gruppen']), 1)
            self.assertEqual(teil['gruppen'][0]['index_anzahl'], len(teil['dreiecke']))
            self.assertTrue(Path(teil['textur'][0]['albedo']).is_file())
            self.assertIsNone(Haarkappe(ablage, netz).teil(None))
        finally:
            shutil.rmtree(ordner, ignore_errors=True)


class DieEngeHose(SimpleTestCase):
    @staticmethod
    def _bein(radius=0.09):
        """Zwei Rohre (Beine) und eine Hüfte darüber als Körper: (Punkte, Dreiecke)."""
        teile_p, teile_d, ab = [], [], 0
        for x in (-0.09, 0.09):
            hoehe = np.linspace(0.62, 0.95, 34)
            winkel = np.linspace(0.0, 2.0 * np.pi, 24, endpoint=False)
            p = np.array([[x + radius * np.cos(w), y, radius * np.sin(w)] for y in hoehe for w in winkel])
            d = []
            for i in range(len(hoehe) - 1):
                for j in range(len(winkel)):
                    a, b, c, e = i * 24 + j, i * 24 + (j + 1) % 24, (i + 1) * 24 + j, (i + 1) * 24 + (j + 1) % 24
                    d += [[a, b, c], [b, e, c]]
            teile_p.append(p)
            teile_d.append(np.array(d) + ab)
            ab += len(p)
        return np.vstack(teile_p), np.vstack(teile_d)

    def test_die_enge_hose_liegt_nur_wenige_millimeter_ueber_der_haut(self):
        p, d = self._bein()
        gebaut = Hosenkoerper(p, d).bauen(0.70, 0.90, eng=True)
        mitte_x = np.where(gebaut['punkte'][:, 0] >= 0.0, 0.09, -0.09)
        r = np.hypot(gebaut['punkte'][:, 0] - mitte_x, gebaut['punkte'][:, 2])
        self.assertGreater(float(np.median(r)), 0.09 + Hosenkoerper.ABSTAND_ENG - 0.003)
        self.assertLess(float(np.percentile(r, 90)), 0.09 + 0.008)

    def test_die_lockere_hose_steht_weiter_ab_als_die_enge(self):
        p, d = self._bein()
        eng = Hosenkoerper(p, d).bauen(0.70, 0.90, eng=True)['punkte']
        locker = Hosenkoerper(p, d).bauen(0.70, 0.90)['punkte']
        r = lambda q: np.median(np.hypot(q[:, 0] - np.where(q[:, 0] >= 0.0, 0.09, -0.09), q[:, 2]))  # noqa: E731
        self.assertGreater(float(r(locker)), float(r(eng)))

    def test_die_textur_der_engen_hose_ist_einfarbig(self):
        bild = Hosenkoerper.textur({}, farbe=(70, 60, 75))
        self.assertEqual(set(bild.getdata()), {(70, 60, 75)})

    def test_welche_hosen_aus_dem_koerper_kommen(self):
        self.assertTrue(Standhose.gilt('gc_hose_lang'))
        self.assertTrue(Standhose.gilt('eigen_foto_04111144_hose_f25'))
        self.assertFalse(Standhose.gilt('eigen_foto_04111144_socken_f25'))
        self.assertFalse(Standhose.gilt('g9_base_shirt'))
        self.assertFalse(Standhose.eng('gc_hose_lang'))
        self.assertTrue(Standhose.eng('eigen_foto_04111144_hose_f25'))

    def test_die_farbe_des_stuecks_ist_das_mittel_der_sichtbaren_pixel_mal_toenung(self):
        ordner = Path(tempfile.mkdtemp(prefix='hose_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')))
        try:
            from PIL import Image
            bild = Image.new('RGBA', (4, 4), (100, 80, 60, 255))
            bild.putpixel((0, 0), (255, 255, 255, 0))                          # durchsichtig: zählt nicht
            bild.save(ordner / 'h.png')
            t = {'textur': [{'albedo': str(ordner / 'h.png'), 'faktor': (0.5, 1.0, 1.0)}], 'farbe': (1.0, 1.0, 1.0)}
            np.testing.assert_allclose(Standhose.farbe(t), [50.0, 80.0, 60.0])
            np.testing.assert_allclose(Standhose.farbe({'farbe': (0.2, 0.4, 0.6)}), [51.0, 102.0, 153.0])
            self.assertIsNone(Standhose.farbe({}))
        finally:
            shutil.rmtree(ordner, ignore_errors=True)


class DerLaufNachRundenVonHand(SimpleTestCase):
    def test_nur_der_modus_begutachtung_mit_den_iterationen_im_lauf_zaehlt(self):
        von_hand = SimpleNamespace(optionen={'iterationen': {'modus': 'begutachtung'}})
        automatisch = SimpleNamespace(optionen={'iterationen': {'modus': 'automatisch'}})
        self.assertTrue(Engine2d3dKleiderlauf._von_hand(von_hand, ['iterationen']))
        self.assertFalse(Engine2d3dKleiderlauf._von_hand(von_hand, ['export', 'film']))
        self.assertFalse(Engine2d3dKleiderlauf._von_hand(automatisch, ['iterationen']))

    def test_ohne_gespeicherten_modus_gilt_die_vorgabe_begutachtung(self):
        self.assertTrue(Engine2d3dKleiderlauf._von_hand(SimpleNamespace(optionen={}), ['iterationen']))
