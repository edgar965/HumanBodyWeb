# -*- coding: utf-8 -*-
u"""Regler, die die Figur wirklich aendern — Daz Body Shapes und HB-Morphs.

WARUM (Edgar, 20.09.2026: „mach testcases fuer mindestens 10 Regler, beide
Bereiche und schau nach, ob die Figuren geaendert sind"): Am selben Tag kamen
zwei Reglersaetze auf Genesis 9 — die gekauften „Genesis 9 Body Shapes" (Daz,
`body_bs_…`, nach Daz-Region in Brust/Taille/Huefte/Arme/Beine/Hals) und die
aus HumanBody uebertragenen HB-Morphs (`hb:…`, `G9hbmorphe`, zweiseitig). Ein
Regler, der im Bedienfeld steht, aber nichts bewegt, faellt niemandem auf —
deshalb hier je Regler DREI Fragen an die Punkte der Stellung (`G9formung.
punkte()`, Kaefig, Meter, Y oben):

1. WIRKUNG: die groesste Verschiebung gegen die Grundfigur liegt ueber MIN_MM.
2. ORT: der Schwerpunkt der Verschiebung (Betrag als Gewicht) liegt in der
   Hoehe des Koerperteils, den der Name verspricht — Bruste bei den
   Pectoral-Knochen (1,25 m), Taille um spine2 (1,07), Po um die Huefte (0,97),
   Oberschenkel 0,89 → 0,48, Unterarm 1,17 → 1,0, Hals 1,41 → 1,53, Kopf ab 1,5;
   die Knochenlagen kommen aus `G9formung({}).skelett()`.
3. LOKAL: hoechstens LOKAL_ANTEIL der Kaefigpunkte bewegen sich um mehr als
   1 mm — ein Bruste-Regler formt nicht den ganzen Koerper.

Bei den HB-Morphs dazu: die Minus-Seite ist eine EIGENE Form (nicht die
negierte Plus-Seite) — MB-Labs `MinMaxMorph`, `plus`/`minus` in der Ablage.

ALLE HB-MORPHS, NICHT 14 (Edgar, 20.09.2026, mit Bild: „HB Cheeks Mass
zerstoert den ganzen Koerper. Deine Testcases meldeten gruen??? wie kann das
sein"): Die 14 handverlesenen waren gruen, `hb:Body_Size` daneben in derselben
Liste bewegte 535 mm und blaehte die projizierten Anhaenge auf (Mund 6,8 ->
94 cm). Deshalb jetzt JEDER angebotene HB-Morph, beide Seiten: hoechstens
HB_MAX_MM, hoechstens HB_ANTEIL der Punkte, Gesichtsmorphe ueber 1,4 m, und
KEINE Gelenkverschiebung (`Hbmorphrig`: Kopfgelenk < 5 mm, Knochenabstand
< 7,5 mm). Und die Rig-Morphs (Body Size, Laengen, Winkel) sind DRAUSSEN:
nicht in der Liste, nicht `vorhanden`, vom Endpunkt ignoriert.

Und der ganze Weg, den der Browser nimmt (`/netz/`, Stufe 1, 104.480
Browserpunkte, `vertices` als base64-float32, `anhaenge`): Regler gestellt →
andere Punkte als ohne, in derselben Hoehe — und die Anhaenge (Mund, Augen,
Wimpern) bleiben, wo und wie gross sie waren.

Ohne Daz-Bibliothek, ohne Body Shapes oder ohne gebaute HB-Morphs
(`manage.py hbmorphe_bauen`) uebersprungen — mit Grund, nicht gruen.

Sabotage-Gegenproben: `G9hbmorphe.deltas` gibt immer `plus` zurueck →
Fall `hb_minus_ist_eigene_form` rot; in `Hbmorpheaufgenesis.bauen` den
Rig-Ausschluss entfernen und neu bauen → `hb_alle_morphs_sind_harmlos` UND
`hb_rig_morphs_sind_draussen` rot; in `G9reglerbereiche` Waist → 'kopf'
aendert an diesem Test nichts (er prueft die Geometrie, nicht die
Einteilung — dafuer `test_genesis9_neue_pakete`).
"""
import base64
import json
import unittest

import numpy as np
from django.test import Client, SimpleTestCase
from Genesis9.formung import G9formung
from Genesis9.hbmorphe import G9hbmorphe
from Genesis9.morphablage import G9morphablage
from Genesis9.pfade import G9pfade

from core.dienste.hbmorphrig import Hbmorphrig

MIN_MM = 3.0
LOKAL_ANTEIL = 0.45
#: Fuer den Lauf ueber ALLE HB-Morphs: Torso SizeX bewegt 47 % der Punkte
#: (Arme wandern mit), Torso Mass 93 mm — beides Form, kein Rig.
HB_MAX_MM = 150.0
HB_ANTEIL = 0.60
GESICHT_AB_M = 1.4
RIG = ('hb:Body_Size', 'hb:Legs_LowerlegLength', 'hb:Torso_Length', 'hb:Head_Size')

#: (Regler, Wert, Hoehenband des Schwerpunkts in Metern, Mindestwirkung mm)
DAZ = [
    ('body_bs_BreastsDiameter', 1.0, (1.15, 1.36), MIN_MM),
    ('body_bs_BreastSize', 1.0, (1.15, 1.36), MIN_MM),           # „Breasts Large"
    ('body_bs_BreastsGone', 1.0, (1.15, 1.36), MIN_MM),
    ('body_bs_LoveHandles', 1.0, (0.92, 1.18), MIN_MM),
    ('body_bs_AbdominalsWidth', 1.0, (0.95, 1.25), MIN_MM),
    ('body_bs_Pregnant', 1.0, (0.88, 1.22), 10.0),
    ('body_bs_GluteSize', 1.0, (0.78, 1.02), MIN_MM),
    ('body_bs_HipSize', 1.0, (0.78, 1.06), MIN_MM),
    ('body_bs_MassThighs', 1.0, (0.55, 0.95), MIN_MM),
    ('body_bs_CalvesSize', 1.0, (0.22, 0.58), MIN_MM),
    ('body_bs_MassUpperarms', 1.0, (1.12, 1.42), MIN_MM),
    ('body_bs_MassForearms', 1.0, (0.98, 1.22), MIN_MM),
    ('body_bs_MassNeck', 1.0, (1.34, 1.58), MIN_MM),
]
HB = [
    ('hb:Torso_BreastMass', 1.0, (1.12, 1.36), 10.0),
    ('hb:Torso_BreastPosZ', -1.0, (1.12, 1.36), MIN_MM),
    ('hb:Chest_Girth', 1.0, (1.05, 1.40), MIN_MM),
    ('hb:Waist_Size', -1.0, (0.92, 1.18), MIN_MM),
    ('hb:Stomach_Volume', 1.0, (0.88, 1.20), MIN_MM),
    ('hb:Pelvis_GluteusSize', 1.0, (0.76, 1.02), MIN_MM),
    ('hb:Pelvis_Girth', 1.0, (0.76, 1.06), MIN_MM),
    ('hb:Legs_UpperlegsMass', 1.0, (0.55, 0.95), MIN_MM),
    ('hb:Legs_CalfGirth', 1.0, (0.22, 0.60), MIN_MM),
    ('hb:Arms_UpperarmMass', 1.0, (1.10, 1.42), MIN_MM),
    ('hb:Neck_Mass', 1.0, (1.32, 1.58), MIN_MM),
    ('hb:Nose_SizeY', 1.0, (1.50, 1.72), MIN_MM),
    ('hb:Chin_Prominence', 1.0, (1.44, 1.62), MIN_MM),
    ('hb:Head_SizeX', 1.0, (1.48, 1.75), MIN_MM),
]


def voraussetzungen():
    u"""Grund fuers Ueberspringen — oder None."""
    if not G9pfade.vorhanden():
        return 'keine Daz-Bibliothek'
    if not (G9pfade.morphs() / 'Daz 3D' / 'Body').is_dir():
        return 'Genesis 9 Body Shapes nicht installiert'
    if not G9hbmorphe.liste():
        return 'HB-Morphs nicht gebaut (manage.py hbmorphe_bauen)'
    return None


GRUND = voraussetzungen()


@unittest.skipIf(GRUND, GRUND)
class ReglerWirkenTest(SimpleTestCase):
    databases = set()
    _basis = None

    @classmethod
    def basis(cls):
        if cls._basis is None:
            cls._basis = np.asarray(G9formung({}).punkte(), dtype=np.float64)
        return cls._basis

    @classmethod
    def verschiebung(cls, regler, wert):
        u"""(N, 3) Meter gegen die Grundfigur — ueber `aus_abfrage`, also den
        Weg der Browser-Anfrage (begrenzt auf min..max, Unbekanntes uebergangen)."""
        formung = G9formung.aus_abfrage({regler: wert})
        if regler not in formung.regler:
            raise AssertionError('%s kennt die Formung nicht' % regler)
        return np.asarray(formung.punkte(), dtype=np.float64) - cls.basis()

    def pruefen(self, regler, wert, band, mindestens_mm):
        d = self.verschiebung(regler, wert)
        betrag = np.linalg.norm(d, axis=1)
        groesste = float(betrag.max() * 1000.0)
        self.assertGreaterEqual(groesste, mindestens_mm,
                                '%s=%g bewegt nur %.2f mm' % (regler, wert, groesste))
        schwerpunkt = float((betrag * self.basis()[:, 1]).sum() / betrag.sum())
        self.assertTrue(band[0] <= schwerpunkt <= band[1],
                        '%s: Schwerpunkt der Verschiebung bei %.3f m, erwartet %s'
                        % (regler, schwerpunkt, band))
        anteil = float((betrag > 0.001).mean())
        self.assertLessEqual(anteil, LOKAL_ANTEIL,
                             '%s bewegt %.0f %% der Punkte um mehr als 1 mm'
                             % (regler, anteil * 100))
        return groesste

    def test_daz_body_shapes_wirken(self):
        kanaele = G9morphablage.holen().kanaele
        fehlend = [r for r, *_ in DAZ if r not in kanaele]
        self.assertEqual(fehlend, [], 'Body-Shapes-Kanaele fehlen in der Ablage')
        bericht = {r: round(self.pruefen(r, w, band, mm), 1) for r, w, band, mm in DAZ}
        self.assertEqual(len(bericht), 13, bericht)

    def test_hb_morphs_wirken(self):
        vorhanden = {r['name'] for r in G9hbmorphe.liste()}
        fehlend = [r for r, *_ in HB if r not in vorhanden]
        self.assertEqual(fehlend, [], 'HB-Morphs fehlen in der Ablage')
        bericht = {r: round(self.pruefen(r, w, band, mm), 1) for r, w, band, mm in HB}
        self.assertEqual(len(bericht), 14, bericht)

    def test_hb_minus_ist_eigene_form(self):
        u"""Plus- und Minus-Seite sind zwei Formen: HumanBodys `BreastMass` −1 ist
        nicht das Spiegelbild von +1 (gemessen: 62 mm gegen 19 mm)."""
        for regler in ('hb:Torso_BreastMass', 'hb:Waist_Size', 'hb:Nose_SizeY'):
            plus = self.verschiebung(regler, 1.0)
            minus = self.verschiebung(regler, -1.0)
            self.assertGreater(np.linalg.norm(plus, axis=1).max(), 0.002, regler)
            self.assertGreater(np.linalg.norm(minus, axis=1).max(), 0.002, regler)
            self.assertGreater(np.abs(plus + minus).max(), 0.001,
                               '%s: Minus ist nur das negierte Plus' % regler)
            halb = self.verschiebung(regler, 0.5)
            np.testing.assert_allclose(halb, plus * 0.5, atol=1e-6,
                                       err_msg='%s: 0,5 ist nicht die halbe Plus-Seite' % regler)

    def test_hb_alle_morphs_sind_harmlos(self):
        u"""Jeder angebotene HB-Morph, beide Seiten — begrenzt, oertlich, ohne Rig."""
        rig = Hbmorphrig(G9formung({}))
        befunde = []
        for r in G9hbmorphe.liste():
            for wert in (1.0, -1.0):
                d = self.verschiebung(r['name'], wert)
                betrag = np.linalg.norm(d, axis=1)
                if betrag.max() < 1e-6:
                    continue                          # einseitig belegt (Ears Lobe -1)
                mm = betrag.max() * 1000.0
                anteil = float((betrag > 0.001).mean())
                schwer = float((betrag * self.basis()[:, 1]).sum() / betrag.sum())
                nummern = np.nonzero(betrag > 0)[0]
                mass = rig.messen(nummern, d[nummern])
                if mm > HB_MAX_MM or anteil > HB_ANTEIL or Hbmorphrig.braucht_rig(mass) \
                        or (r['bereich'] == 'hb_gesicht' and schwer < GESICHT_AB_M):
                    befunde.append('%s %+g: %.0f mm, %.0f %%, y %.2f, Kopf %.1f, Laenge %.1f'
                                   % (r['name'], wert, mm, anteil * 100, schwer,
                                      mass['kopf_mm'], mass['laenge_mm']))
        self.assertEqual(befunde, [])
        self.assertGreaterEqual(len(G9hbmorphe.liste()), 150)

    def test_hb_rig_morphs_sind_draussen(self):
        u"""Body Size, Laengen, Kopfgroesse: Steckbrief mit Millimetern, keine Deltas."""
        angeboten = {r['name'] for r in G9hbmorphe.liste()}
        weg = {'hb:' + u['kennung'] for u in G9hbmorphe.uebergangene() if u.get('rig')}
        for name in RIG:
            self.assertNotIn(name, angeboten, name)
            self.assertIn(name, weg, name)
            self.assertFalse(G9hbmorphe.vorhanden(name), name)
            self.assertIsNone(G9hbmorphe.deltas(name, -1.0), name)
        brief = G9hbmorphe.steckbrief('Body_Size')
        self.assertTrue(brief['rig'])
        self.assertGreater(brief['kopf_mm'], 100.0)
        self.assertEqual(G9formung.aus_abfrage({'hb:Body_Size': -1.0}).regler, {})
        self.assertTrue({n[3:] for n in RIG} <= set(G9hbmorphe.bestand()['rig_uebergangen']))

    # ----------------------------------------------------- der Browser-Weg

    @staticmethod
    def dekodieren(d):
        return np.frombuffer(base64.b64decode(d['vertices']),
                             dtype=np.float32).reshape(-1, 3).astype(np.float64)

    @classmethod
    def browserantwort(cls, client, regler):
        u"""(Koerperpunkte, {anhang: Punkte}) der Netzantwort."""
        antwort = client.post('/api/character/genesis9-figur/feminine/netz/',
                              data=json.dumps({'regler': regler}),
                              content_type='application/json')
        assert antwort.status_code == 200, antwort.content[:200]
        d = antwort.json()
        return cls.dekodieren(d), {a['schluessel']: cls.dekodieren(a) for a in d.get('anhaenge', [])}

    def test_netz_endpunkt_zeigt_die_regler(self):
        c = Client()
        ohne, anhaenge = self.browserantwort(c, {})
        self.assertIn('mund', anhaenge)
        for regler, wert, band in (('body_bs_BreastsDiameter', 1.0, (1.15, 1.36)),
                                   ('hb:Waist_Size', -1.0, (0.92, 1.18)),
                                   ('hb:Nose_SizeY', 1.0, (1.50, 1.72))):
            mit, mit_anhaengen = self.browserantwort(c, {regler: wert})
            self.assertEqual(mit.shape, ohne.shape)
            betrag = np.linalg.norm(mit - ohne, axis=1)
            self.assertGreaterEqual(betrag.max() * 1000.0, MIN_MM, regler)
            schwerpunkt = float((betrag * ohne[:, 1]).sum() / betrag.sum())
            self.assertTrue(band[0] <= schwerpunkt <= band[1],
                            '%s im Browsernetz bei %.3f m' % (regler, schwerpunkt))
            # Die Anhaenge folgen dem Koerper per Projektion — und bleiben dabei,
            # was sie sind: gleich gross (±10 %), Mitte hoechstens 5 mm versetzt.
            for schluessel, alt in anhaenge.items():
                neu = mit_anhaengen[schluessel]
                self.assertLess(abs(np.ptp(neu, axis=0).max() / np.ptp(alt, axis=0).max() - 1.0),
                                0.10, '%s: Anhang %s aufgeblaeht' % (regler, schluessel))
                self.assertLess(np.linalg.norm(neu.mean(axis=0) - alt.mean(axis=0)) * 1000.0,
                                5.0, '%s: Anhang %s verschoben' % (regler, schluessel))
        # Ein Rig-Morph kommt am Endpunkt nicht an: dieselben Punkte wie ohne.
        egal, _ = self.browserantwort(c, {'hb:Body_Size': -1.0})
        np.testing.assert_allclose(egal, ohne, atol=1e-6)
