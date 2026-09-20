# -*- coding: utf-8 -*-
"""`G9hbmorphe`: die HumanBody-Regler als zweiseitige Morphs auf Genesis 9.

WARUM (20.09.2026, Edgar: „fang schon mal an mit dem Bau der HumanBody
Regler fuer Genesis … Kennzeichne die HumanBody Regler im Tool als HB-Morphs"):
Ein `hb:`-Regler laeuft von -1 bis 1 mit EIGENEN Deltas je Richtung — wie
MB-Labs `MinMaxMorph`, anders als `eigen:` (einseitig, 0..2). Geprueft mit
Kunstdaten in einem Wegwerf-Ordner, ohne Daz-Bibliothek:

1. Ablegen und Lesen: `plus` bei positivem, `minus` bei negativem Wert, mal
   |Wert|; Nullzeilen beider Richtungen fliegen raus, einseitig belegte bleiben.
2. Anzeige und Bereich: `Torso_BreastPosZ` -> „Torso Breast Pos Z" im Bereich
   `hb_koerper`; `Nose_SizeY` -> Gesicht; `Fantasy_ElfEars` -> Fantasie;
   Unbekanntes -> Koerper (sichtbar, nicht verschluckt).
3. `bereiche()` nennt nur belegte Bereiche, mit den Namen „HB-Morphs …".
4. `G9formung` nimmt einen `hb:`-Regler aus der Anfrage (begrenzt auf -1..1),
   haelt ihn aus dem Daz-Formelgraphen heraus und addiert die Deltas der
   richtigen Seite in `morphpunkte()` — gegen eine Attrappe des Basisnetzes.
5. `G9reglerplan.bereiche()` haengt die HB-Bereiche hinter die Daz-Bereiche.

FEHLERBILD OHNE DIESE TESTS: Ein negativer Wert nahm die Plus-Deltas mit
Vorzeichen — halb richtig, unauffaellig, falsch.
"""
import shutil
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.formung import G9formung
from Genesis9.hbmorphe import G9hbmorphe
from Genesis9.reglerplan import G9reglerplan


class _Ordner:
    """Den Ablageordner fuer die Dauer eines Tests umlenken."""

    def __init__(self, test):
        self.pfad = Path(__file__).parent / 'tmp_hbmorphe'
        self.alt = G9hbmorphe.ordner
        self.test = test

    def __enter__(self):
        shutil.rmtree(self.pfad, ignore_errors=True)
        G9hbmorphe.ordner = classmethod(lambda cls: self.pfad)
        G9hbmorphe.vergessen()
        return self.pfad

    def __exit__(self, *_):
        G9hbmorphe.ordner = self.alt
        G9hbmorphe.vergessen()
        shutil.rmtree(self.pfad, ignore_errors=True)


class HbmorpheTest(SimpleTestCase):
    databases = set()

    def test_1_ablegen_und_lesen_zweiseitig(self):
        with _Ordner(self):
            nummern = [3, 7, 9, 12]
            plus = [[0.01, 0, 0], [0, 0.02, 0], [0, 0, 0], [0, 0, 0.005]]
            minus = [[-0.03, 0, 0], [0, 0, 0], [0, 0, 0], [0, -0.001, 0]]
            name = G9hbmorphe.ablegen('Torso_BreastPosZ', nummern, plus, minus)
            self.assertEqual(name, 'hb:Torso_BreastPosZ')
            self.assertTrue(G9hbmorphe.vorhanden(name))
            self.assertFalse(G9hbmorphe.vorhanden('eigen:x'))
            n, d = G9hbmorphe.deltas(name, 0.5)
            self.assertEqual(list(n), [3, 7, 12])            # Zeile 9 (beidseitig null) weg
            np.testing.assert_allclose(d, np.array(plus)[[0, 1, 3]] * 0.5, atol=1e-7)
            n, d = G9hbmorphe.deltas(name, -1.0)
            np.testing.assert_allclose(d, np.array(minus)[[0, 1, 3]], atol=1e-7)
            self.assertIsNone(G9hbmorphe.deltas(name, 0.0))
            self.assertIsNone(G9hbmorphe.deltas('hb:gibt_es_nicht', 1.0))
            brief = G9hbmorphe.steckbrief('Torso_BreastPosZ')
            self.assertEqual((brief['kategorie'], brief['punkte']), ('Torso', 3))
            self.assertEqual((brief['plus_mm'], brief['minus_mm']), (20.0, 30.0))

    def test_2_anzeige_und_bereich(self):
        self.assertEqual(G9hbmorphe.anzeige('Torso_BreastPosZ'), 'Torso Breast Pos Z')
        self.assertEqual(G9hbmorphe.anzeige('Eyes_innerSinus'), 'Eyes inner Sinus')
        self.assertEqual(G9hbmorphe.anzeige('Shoulders_SizeX2'), 'Shoulders Size X2')
        self.assertEqual(G9hbmorphe.bereich('Torso'), 'hb_koerper')
        self.assertEqual(G9hbmorphe.bereich('Nose'), 'hb_gesicht')
        self.assertEqual(G9hbmorphe.bereich('Fantasy'), 'hb_fantasie')
        self.assertEqual(G9hbmorphe.bereich('Quatsch'), 'hb_koerper')
        self.assertEqual(G9hbmorphe.kennung('a b/c'), 'a_b_c')

    def test_3_liste_und_bereiche_nur_belegt(self):
        with _Ordner(self):
            self.assertEqual(G9hbmorphe.bereiche(), [])
            G9hbmorphe.ablegen('Waist_Size', [1], [[0.01, 0, 0]], [[0, 0, 0]])
            G9hbmorphe.ablegen('Nose_SizeY', [2], [[0, 0.01, 0]], [[0, 0, 0]])
            G9hbmorphe.ablegen('Abdomen_Mass', [3], [[0, 0, 0.01]], [[0, 0, 0]])
            bereiche = G9hbmorphe.bereiche()
            self.assertEqual([b['schluessel'] for b in bereiche], ['hb_koerper', 'hb_gesicht'])
            self.assertEqual(bereiche[0]['name'], 'HB-Morphs Körper')
            self.assertEqual([r['name'] for r in bereiche[0]['regler']],
                             ['hb:Abdomen_Mass', 'hb:Waist_Size'])       # nach Kategorie
            regler = bereiche[1]['regler'][0]
            self.assertEqual((regler['min'], regler['max'], regler['vorgabe']), (-1.0, 1.0, 0.0))
            self.assertEqual(regler['anzeige'], 'Nose Size Y')

    def test_4_formung_nimmt_hb_regler(self):
        with _Ordner(self):
            G9hbmorphe.ablegen('Waist_Size', [0, 2], [[0.01, 0, 0], [0, 0.02, 0]],
                               [[-0.05, 0, 0], [0, 0, 0]])
            basis = mock.Mock()
            basis.punkte = np.zeros((4, 3))
            ablage = mock.Mock()
            ablage.kanaele = {}
            with mock.patch('Genesis9.formung.G9basisnetz.holen', return_value=basis), \
                    mock.patch('Genesis9.formung.G9morphablage.holen', return_value=ablage), \
                    mock.patch('Genesis9.formung.G9formeln') as formeln:
                formeln.return_value.morphwerte.return_value = {}
                formeln.return_value.ablage = ablage
                # Aus der Anfrage: begrenzt auf -1..1, Unbekanntes uebergangen
                f = G9formung.aus_abfrage({'hb:Waist_Size': -3, 'hb:nix': 1, 'quatsch': 2})
                self.assertEqual(f.regler, {'hb:Waist_Size': -1.0})
                self.assertTrue(G9formung.fremd('hb:Waist_Size'))
                self.assertTrue(G9formung.fremd('eigen:x'))
                self.assertFalse(G9formung.fremd('body_ctrl_WaistBend'))
                # Der Formelgraph sieht den hb:-Regler nicht
                _ = f.formeln
                self.assertEqual(formeln.call_args[0][0], {})
                punkte = f.morphpunkte()
                np.testing.assert_allclose(punkte[0], [-0.05, 0, 0], atol=1e-7)   # minus-Seite
                np.testing.assert_allclose(punkte[2], [0, 0, 0], atol=1e-7)
                G9formung._gemerkt.clear()

    def test_6_uebergangener_morph_hat_nur_steckbrief(self):
        u"""Rig-Morphs (20.09.2026): Steckbrief ja, Deltas nein — nicht in der Liste,
        nicht `vorhanden`, `deltas` None, aber in `uebergangene()` nachlesbar."""
        with _Ordner(self):
            G9hbmorphe.ablegen('Waist_Size', [1], [[0.01, 0, 0]], [[0, 0, 0]])
            G9hbmorphe.steckbrief_schreiben('Body_Size', {'rig': True, 'kopf_mm': 477.3,
                                                          'laenge_mm': 167.2})
            self.assertEqual([r['name'] for r in G9hbmorphe.liste()], ['hb:Waist_Size'])
            self.assertFalse(G9hbmorphe.vorhanden('hb:Body_Size'))
            self.assertIsNone(G9hbmorphe.deltas('hb:Body_Size', -1.0))
            weg = G9hbmorphe.uebergangene()
            self.assertEqual([u['kennung'] for u in weg], ['Body_Size'])
            self.assertEqual((weg[0]['rig'], weg[0]['kopf_mm'], weg[0]['punkte'],
                              weg[0]['anzeige']), (True, 477.3, 0, 'Body Size'))

    def test_5_reglerplan_haengt_hb_bereiche_an(self):
        with _Ordner(self):
            G9hbmorphe.ablegen('Fantasy_ElfEars', [1], [[0.01, 0, 0]], [[0, 0, 0]])
            with mock.patch.object(G9reglerplan, 'holen', return_value=[]):
                schluessel = [b['schluessel'] for b in G9reglerplan.bereiche()]
            self.assertEqual(schluessel[:len(G9reglerplan.BEREICHE)], list(G9reglerplan.BEREICHE))
            self.assertEqual(schluessel[len(G9reglerplan.BEREICHE):], ['hb_fantasie'])
