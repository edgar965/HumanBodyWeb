# -*- coding: utf-8 -*-
u"""Der SMPLest-X-Weg: ein Bild, ein Video, dieselben fuenf Schritte.

DER ANLASS (02.09.2026)
=======================
`_run_smplest_x.py` (ein Foto) und `_run_smplest_x_video.py` (jedes
Bild eines Videos) taten je Bild dasselbe — YOLO fragen, groessten
Kasten nehmen, zuschneiden, Tensor bauen, Netz rechnen — und hatten das
zweimal ausgeschrieben, einmal in Schluesselwort-, einmal in
Positionsschreibweise. Wer den Ausschnitt aendert, muss beide finden.

Dazu lagen im Videolauf zwei Dinge, die weder OpenCV noch eine
Grafikkarte brauchen: die Abtastrechnung (welche Bildnummern bei einer
Ziel-Bildrate gelesen werden) und das Einsammeln der Ausdruecke. Beide
waren im Ablauf nicht pruefbar; als eigene Klassen sind sie es.

WAS DIESE PRUEFUNG NICHT IST
============================
Sie startet SMPLest-X nicht. Ob das Netz gute Formparameter liefert,
sagt sie nicht — sie sagt, dass der Weg dorthin fuer Bild und Video
derselbe ist und dass aus der Modellausgabe die richtigen Felder
kommen.

BDD - GEGEBEN / DANN
====================
    DerBefund         ... liest Form, Ausdruck und Kamera aus der Ausgabe
    DasBild           ... nimmt den groessten Kasten und meldet den Grund
    DieAbtastung      ... rechnet die Bildnummern zur Ziel-Bildrate
    DieAusdrucksreihe ... haelt je Bild zehn Werte, auch ohne Person
"""
import json
import os
import unittest

from ._erkennerattrappen import Yoloattrappe
from ._pruefablage import Pruefablage
from ._smplestxeinstellungen import Smplestxeinstellungen
from ._tensorattrappe import Tensorattrappe
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402

from ausdrucksreihe import Ausdrucksreihe                   # noqa: E402
from bildabtastung import Bildabtastung                     # noqa: E402
from smplestxbefund import Smplestxbefund                   # noqa: E402
from smplestxbild import Smplestxbild                       # noqa: E402


class DerBefund(unittest.TestCase):
    u"""Was das Modell sagt, kommt als Python-Werte heraus."""

    def _ausgabe(self):
        return {
            Smplestxbefund.FORM: Tensorattrappe([[0.5, -0.25, 1.0]]),
            Smplestxbefund.AUSDRUCK: Tensorattrappe([[0.125, 0.25]]),
            Smplestxbefund.KAMERA: Tensorattrappe([[0.0, 0.0, 3.0]]),
        }

    def _befund(self):
        kasten = np.array([1.0, 2.0, 3.0, 4.0])
        return Smplestxbefund(self._ausgabe(), kasten, kasten, 0.875)

    def test_die_formparameter_kommen_als_liste(self):
        self.assertEqual(self._befund().betas(), [0.5, -0.25, 1.0])

    def test_der_ausdruck_kommt_als_liste(self):
        self.assertEqual(self._befund().ausdruck(), [0.125, 0.25])

    def test_die_kameraverschiebung_kommt_mit(self):
        self.assertEqual(self._befund().kameraverschiebung(), [0.0, 0.0, 3.0])

    def test_ein_fehlendes_feld_gibt_keine_ausnahme(self):
        u"""Nicht jedes Modell liefert `cam_trans`."""
        befund = Smplestxbefund({Smplestxbefund.FORM: Tensorattrappe([[1.0]])})
        self.assertIsNone(befund.kameraverschiebung())
        self.assertEqual(befund.ausdruck(), [])

    def test_ein_befund_ohne_person_nennt_seinen_grund(self):
        befund = Smplestxbefund.ohne(Smplestxbefund.KEINE_PERSON)
        self.assertFalse(befund.gefunden)
        self.assertEqual(befund.grund, 'No person detected in image')

    def test_die_meldungstexte_bleiben_wie_bisher(self):
        u"""Beide standen so in den Runnern — Protokolle bleiben lesbar."""
        self.assertEqual(Smplestxbefund.KEINE_PERSON,
                         'No person detected in image')
        self.assertEqual(Smplestxbefund.KEIN_AUSSCHNITT,
                         'Bbox processing failed')

    def test_die_zuversicht_ist_immer_eine_zahl(self):
        self.assertIsInstance(self._befund().guete, float)
        self.assertEqual(Smplestxbefund.ohne('x').guete, 0.0)

    def test_das_netz_landet_neben_dem_bild(self):
        ausgabe = self._ausgabe()
        ausgabe[Smplestxbefund.NETZ] = Tensorattrappe(
            [np.zeros((5, 3), dtype=np.float32)])
        with Pruefablage.ordner() as ordner:
            bild = os.path.join(ordner, 'foto.jpg')
            pfad = Smplestxbefund(ausgabe).netz_speichern(bild)
            self.assertEqual(os.path.dirname(pfad), ordner)
            self.assertEqual(np.load(pfad).shape, (5, 3))

    def test_ohne_netz_kein_dateiname(self):
        self.assertIsNone(self._befund().netz_speichern('/egal/foto.jpg'))


class DasBild(unittest.TestCase):
    u"""Ein Weg fuer Foto und Video — und er nimmt den groessten Kasten."""

    #: Erster Kasten klein und sehr sicher, zweiter gross und weniger.
    KAESTEN = [[0.0, 0.0, 10.0, 10.0],
               [0.0, 0.0, 100.0, 200.0]]
    GUETE = [0.99, 0.55]

    def _bild(self, kaesten=None, guete=None):
        detektor = Yoloattrappe(
            self.KAESTEN if kaesten is None else kaesten,
            self.GUETE if guete is None else guete)
        return Smplestxbild(Smplestxeinstellungen(), detektor, None, 'cuda')

    @staticmethod
    def _rgb():
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def test_der_groesste_kasten_gewinnt_nicht_der_sicherste(self):
        u"""Ein sicher erkannter Passant im Hintergrund zaehlt nicht."""
        self.assertEqual(Smplestxbild.groesste(np.array(self.KAESTEN)), 1)

    def test_die_einstellungen_werden_gelesen(self):
        bild = self._bild()
        self.assertEqual(bild.zuversicht, 0.42)
        self.assertEqual(bild.verhaeltnis, 1.5)
        self.assertEqual(bild.eingabeform, (256, 192))

    def test_der_detektor_bekommt_die_werte_aus_der_konfiguration(self):
        bild = self._bild()
        bild.personen(self._rgb())
        self.assertEqual(bild.detektor.aufrufe[0]['conf'], 0.42)
        self.assertEqual(bild.detektor.aufrufe[0]['classes'], 0)

    def test_ein_gespiegelter_kasten_bekommt_positive_masse(self):
        u"""YOLO liefert gelegentlich rechts vor links."""
        xywh = Smplestxbild.als_xywh(np.array([100.0, 200.0, 40.0, 150.0]))
        self.assertEqual(list(xywh), [100.0, 200.0, 60.0, 50.0])

    def test_ohne_person_kommt_der_grund_zurueck(self):
        bild = self._bild(kaesten=np.zeros((0, 4)), guete=[])
        befund = bild.auswerten(self._rgb())
        self.assertFalse(befund.gefunden)
        self.assertEqual(befund.grund, Smplestxbefund.KEINE_PERSON)

    def test_ein_gescheiterter_ausschnitt_ist_ein_eigener_grund(self):
        u"""`process_bbox` gibt `None`, wenn der Kasten unbrauchbar ist."""
        bild = self._bild()
        bild.ausschnitt = lambda *args: None
        self.assertEqual(bild.auswerten(self._rgb()).grund,
                         Smplestxbefund.KEIN_AUSSCHNITT)

    def test_der_befund_traegt_die_guete_des_groessten_kastens(self):
        bild = self._bild()
        bild.ausschnitt = lambda *args: np.array([0.0, 0.0, 100.0, 200.0])
        bild.netzeingabe = lambda *args: 'eingabe'
        bild.durchrechnen = lambda eingabe: {
            Smplestxbefund.FORM: Tensorattrappe([[1.0]])}
        befund = bild.auswerten(self._rgb())
        self.assertTrue(befund.gefunden)
        self.assertAlmostEqual(befund.guete, 0.55, places=5)
        self.assertEqual(list(befund.kasten), [0.0, 0.0, 100.0, 200.0])


class DieAbtastung(unittest.TestCase):
    u"""Welche Bildnummern eine Ziel-Bildrate braucht."""

    def test_gleiche_rate_liest_jedes_bild(self):
        abtastung = Bildabtastung(300, 30.0, 30.0)
        self.assertTrue(abtastung.unveraendert)
        self.assertEqual(abtastung.nummern(), list(range(300)))

    def test_ohne_zielrate_gilt_die_quelle(self):
        self.assertEqual(Bildabtastung(120, 25.0, None).rate, 25.0)
        self.assertEqual(Bildabtastung(120, 25.0, 0).rate, 25.0)

    def test_die_haelfte_der_bildrate_liest_jedes_zweite(self):
        nummern = Bildabtastung(300, 60.0, 30.0).nummern()
        self.assertEqual(len(nummern), 150)
        self.assertEqual(nummern[:4], [0, 2, 4, 6])

    def test_ntsc_gilt_als_dieselbe_rate(self):
        u"""29,97 ist nicht 30 — ohne Toleranz nimmt jedes NTSC-Video den
        Umweg ueber die Zeitachse, obwohl es Bild fuer Bild gemeint ist.
        """
        self.assertTrue(Bildabtastung(100, 29.995, 30.0).unveraendert)
        self.assertFalse(Bildabtastung(100, 29.9, 30.0).unveraendert)

    def test_keine_nummer_zeigt_ueber_das_ende(self):
        u"""Beim Hochrechnen zeigt die Rundung ueber das letzte Bild.

        DIESE PRUEFUNG WAR ZUERST ZAHNLOS (Sabotageprobe 02.09.2026):
        Sie stand auf `(10, 25, 30)` — dort greift die Deckelung gar
        nicht, und die Sabotage „Deckelung entfernt" blieb gruen. Eine
        Suche ueber die ueblichen Bildraten findet 1.644 Faelle, in
        denen sie greift; alle liegen beim HOCHrechnen (Ziel > Quelle)
        auf kurzen Abschnitten. Zwei davon stehen hier.
        """
        for gesamt, quelle, ziel in ((2, 30.0, 60.0), (1, 15.0, 60.0)):
            with self.subTest(gesamt=gesamt, quelle=quelle, ziel=ziel):
                nummern = Bildabtastung(gesamt, quelle, ziel).nummern()
                self.assertLessEqual(max(nummern), gesamt - 1,
                                     'liest ein Bild, das es nicht gibt')

    def test_das_hochrechnen_liefert_mehr_bilder_als_die_quelle(self):
        u"""Sonst waere die Deckelung nur deshalb erfuellt, weil gar
        nicht hochgerechnet wird."""
        self.assertEqual(len(Bildabtastung(2, 30.0, 60.0).nummern()), 4)
        self.assertEqual(len(Bildabtastung(10, 25.0, 30.0).nummern()), 12)

    def test_ein_leeres_video_ergibt_keine_nummern(self):
        self.assertEqual(Bildabtastung(0, 30.0, 30.0).nummern(), [])

    def test_ohne_bildrate_wird_mit_dreissig_gerechnet(self):
        u"""Manche Container nennen keine Bildrate — `cap.get` gibt 0."""
        self.assertEqual(Bildabtastung(60, 0, None).quellrate, 30.0)

    def test_mindestens_ein_bild(self):
        self.assertEqual(len(Bildabtastung(1, 30.0, 1.0).nummern()), 1)


class DieAusdrucksreihe(unittest.TestCase):
    u"""Je Bild zehn Werte — auch dort, wo niemand zu sehen war."""

    def test_ein_bild_ohne_person_bekommt_nullen(self):
        reihe = Ausdrucksreihe(30.0)
        reihe.leer()
        self.assertEqual(reihe.bilder, [[0.0] * 10])
        self.assertEqual(reihe.erkannt, 0)

    def test_zu_lange_ausdruecke_werden_gekuerzt(self):
        u"""SMPLest-X liefert 50 Parameter, weiter gehen zehn."""
        reihe = Ausdrucksreihe(30.0)
        reihe.dazu([float(i) for i in range(50)])
        self.assertEqual(len(reihe.bilder[0]), 10)
        self.assertEqual(reihe.erkannt, 1)

    def test_alle_zeilen_sind_gleich_lang(self):
        u"""Sonst brechen die Blendshapes mitten im Video ab."""
        reihe = Ausdrucksreihe(24.0)
        reihe.dazu(range(50))
        reihe.leer()
        reihe.dazu(range(50))
        self.assertEqual({len(z) for z in reihe.bilder}, {10})

    def test_das_woerterbuch_traegt_die_vier_felder(self):
        reihe = Ausdrucksreihe(24.0)
        reihe.leer()
        self.assertEqual(reihe.als_dict(),
                         {'fps': 24.0, 'frame_count': 1,
                          'expression_frames': [[0.0] * 10],
                          'detected_count': 0})

    def test_die_datei_ist_lesbares_json(self):
        reihe = Ausdrucksreihe(30.0)
        reihe.dazu(range(10))
        with Pruefablage.ordner() as ordner:
            ziel = os.path.join(ordner, 'tief', 'ausdruck.json')
            reihe.schreiben(ziel)
            with open(ziel) as datei:
                self.assertEqual(json.load(datei)['detected_count'], 1)
