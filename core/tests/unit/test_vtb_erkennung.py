# -*- coding: utf-8 -*-
u"""Die 2D-Erkennung von VideoToBVH: CSV-Format, Modellgroesse, Verteiler.

DER ANLASS (01.09.2026)
=======================
`VideoToBVH/wrappers` hatte keinen einzigen Test — 3.883 eigene Zeilen,
darunter der Weg, ueber den jede Videoerkennung laeuft. Zwei Fehler in
derselben Datei sind deshalb lange unbemerkt geblieben:

* `rtmpose_det` bildete die groesste Modellstufe (`x`) auf
  `lightweight` ab, also auf das KLEINSTE Netz von rtmlib.
* `vitpose_det` nahm `model_size` entgegen und benutzte es nie — die
  Einstellung `vitpose_model_size` stand im Formular und wirkte nicht.

Beides faellt in keinem Betriebslauf auf: Die Erkennung liefert ja
Ergebnisse, nur schlechtere als bestellt.

WAS DIESE PRUEFUNG NICHT IST
============================
Sie startet keine Erkennung. Ob rtmlib gute Punkte liefert, sagt sie
nicht — sie sagt, dass die Kette vom Formular bis zum Modell
zusammenpasst und die CSV die Form hat, die MocapNET erwartet.

BDD - GEGEBEN / DANN
====================
    DasCsvFormat        ... hat 417 Spalten in fester Ordnung
    DieModellgroesse    ... bildet die groesste Wahl aufs groesste Netz
    DerVerteiler        ... kennt genau die Namen, die Django schickt
    DerVideolauf        ... meldet TOTAL und PROGRESS je Bild
"""
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402

from csvschreiber import Csvschreiber                       # noqa: E402
from erkennerwahl import Erkennerwahl                       # noqa: E402
from koerperpunkte import Koerperpunkte                     # noqa: E402
from lifterwahl import Lifterwahl                           # noqa: E402
from modellgroesse import Modellgroesse                     # noqa: E402
from videolauf import Videolauf                             # noqa: E402


class DasCsvFormat(unittest.TestCase):
    u"""MocapNET liest die Spalten nach POSITION, nicht nach Name."""

    #: 3 Vorspalten + (26 + 21 + 21 + 70) Gelenke x 3 Werte.
    SPALTEN = 3 + (26 + 21 + 21 + 70) * 3

    def test_kopfzeile_hat_417_spalten(self):
        self.assertEqual(len(Csvschreiber.kopf().split(',')), self.SPALTEN)

    def test_datenzeile_ist_genauso_breit(self):
        punkte = np.zeros((26, 3), dtype=np.float32)
        zeile = Csvschreiber.zeile(0, punkte, 1920, 1080)
        self.assertEqual(len(zeile.split(',')), self.SPALTEN)

    def test_abschnittslaengen_stehen_fest(self):
        u"""Eine Zeile mehr oder weniger verschiebt alles dahinter."""
        laengen = tuple(len(n) for n in Koerperpunkte.abschnitte())
        self.assertEqual(laengen, Koerperpunkte.LAENGEN)

    def test_koordinaten_werden_auf_die_bildgroesse_normiert(self):
        punkte = np.zeros((26, 3), dtype=np.float32)
        punkte[0] = [960.0, 540.0, 0.9]
        teile = Csvschreiber.zeile(0, punkte, 1920, 1080).split(',')
        self.assertEqual(teile[3:6], ['0.500000', '0.500000', '0.900000'])

    def test_bildgroesse_null_ergibt_keine_division(self):
        u"""Ein Video ohne lesbare Masse darf nicht abstuerzen."""
        punkte = np.ones((26, 3), dtype=np.float32)
        teile = Csvschreiber.zeile(0, punkte, 0, 0).split(',')
        self.assertEqual(teile[3:5], ['0.000000', '0.000000'])

    def test_haende_und_gesicht_bleiben_leer(self):
        u"""Keiner dieser Erkenner sieht Haende oder Gesicht."""
        punkte = np.ones((26, 3), dtype=np.float32)
        teile = Csvschreiber.zeile(0, punkte, 100, 100).split(',')
        self.assertEqual(set(teile[3 + 26 * 3:]), {'0'})

    def test_die_errechneten_gelenke(self):
        u"""Hals und Huefte kommen aus je zwei anderen Punkten."""
        coco = np.zeros((17, 3), dtype=np.float32)
        coco[5] = [100, 200, 0.9]     # linke Schulter
        coco[6] = [200, 200, 0.7]     # rechte Schulter
        body25 = Koerperpunkte.aus_coco(coco, np)
        self.assertEqual(list(body25[1]), [150.0, 200.0, 0.7])

    def test_ohne_zuversicht_kein_errechnetes_gelenk(self):
        u"""Zwei unerkannte Schultern ergeben keinen Hals bei (0,0)."""
        coco = np.zeros((17, 3), dtype=np.float32)
        coco[5] = [100, 200, 0.0]
        coco[6] = [200, 200, 0.0]
        self.assertEqual(list(Koerperpunkte.aus_coco(coco, np)[1]),
                         [0.0, 0.0, 0.0])


class DieModellgroesse(unittest.TestCase):
    u"""Die groesste Wahl muss das groesste Netz laden."""

    def test_x_ist_die_groesste_stufe(self):
        u"""Der Befund: `x` fuehrte auf `lightweight`, das kleinste Netz."""
        self.assertEqual(Modellgroesse.modus('x'), Modellgroesse.GROSS)

    def test_die_stufen_sind_geordnet(self):
        stufen = [Modellgroesse.modus(g) for g in ('n', 's', 'm', 'l', 'x')]
        self.assertEqual(stufen, [Modellgroesse.KLEIN, Modellgroesse.KLEIN,
                                  Modellgroesse.MITTEL, Modellgroesse.GROSS,
                                  Modellgroesse.GROSS])

    def test_vitpose_stufen_wirken(self):
        u"""b/l/h aus `vitpose_model_size` ergeben drei Antworten."""
        self.assertEqual(Modellgroesse.modus('b'), Modellgroesse.KLEIN)
        self.assertEqual(Modellgroesse.modus('h'), Modellgroesse.GROSS)
        self.assertNotEqual(Modellgroesse.modus('b'), Modellgroesse.modus('h'))

    def test_unbekanntes_faellt_auf_die_mitte(self):
        u"""Ein Tippfehler darf nicht heimlich das kleinste Netz waehlen."""
        for wert in ('', None, 'quatsch', 'L '):
            with self.subTest(wert=wert):
                self.assertIn(Modellgroesse.modus(wert),
                              (Modellgroesse.MITTEL, Modellgroesse.GROSS))
        self.assertEqual(Modellgroesse.modus('quatsch'), Modellgroesse.VORGABE)

    def test_grossbuchstaben_zaehlen_gleich(self):
        self.assertEqual(Modellgroesse.modus('X'), Modellgroesse.modus('x'))


class DerVerteiler(unittest.TestCase):
    u"""Die Namensliste stand frueher zweimal — hier nur noch einmal."""

    def test_erkenner_decken_die_django_seite(self):
        from core.pipelines.erkennung2d import Erkennung2d
        self.assertLessEqual(set(Erkennung2d.MODELLFELD),
                             set(Erkennerwahl.namen()))

    def test_jeder_erkenner_hat_ein_modul(self):
        for name in Erkennerwahl.namen():
            with self.subTest(name=name):
                modul = __import__(Erkennerwahl.ERKENNER[name][0])
                self.assertTrue(hasattr(modul, 'detect'))

    def test_lifter_kennen_die_schalter_der_django_seite(self):
        u"""`Smplbefehl` baut die Kommandozeile, `Lifterwahl` liest sie."""
        from core.pipelines.smplbefehl import Smplbefehl
        for pipeline, schalter in Smplbefehl.SCHALTER.items():
            with self.subTest(pipeline=pipeline):
                self.assertIn(pipeline, Lifterwahl.LIFTER)
                erlaubt = set(Lifterwahl.LIFTER[pipeline][1])
                gesendet = {arg.lstrip('-') for _s, _f, arg in schalter}
                self.assertLessEqual(gesendet, erlaubt)

    def test_jeder_lifter_hat_ein_modul(self):
        for name in Lifterwahl.namen():
            with self.subTest(name=name):
                modul = __import__(Lifterwahl.LIFTER[name][0])
                self.assertTrue(hasattr(modul, 'lift'))

    def test_fremde_schalter_fallen_weg(self):
        u"""Der Verteiler nimmt die Schalter ALLER Pipelines entgegen."""
        gvhmr = set(Lifterwahl.LIFTER['gvhmr'][1])
        self.assertNotIn('run_smplify', gvhmr)
        self.assertIn('static_cam', gvhmr)


class DerVideolauf(unittest.TestCase):
    u"""TOTAL und PROGRESS liest der Django-Prozess Zeile fuer Zeile."""

    def _lauf(self, bilder, ziel):
        lauf = Videolauf('Probe', 'egal.mp4', str(ziel))
        lauf.breite, lauf.hoehe, lauf.anzahl = 640, 480, bilder
        return lauf

    def test_meldet_gesamtzahl_und_fortschritt(self):
        import io
        from contextlib import redirect_stdout
        with Pruefablage.ordner() as ordner:
            ziel = '%s/punkte.csv' % ordner
            leer = Videolauf.leere_punkte(np)
            ausgabe = io.StringIO()
            with redirect_stdout(ausgabe):
                anzahl = self._lauf(3, ziel).schreiben(leer for _ in range(3))
            zeilen = ausgabe.getvalue().strip().split('\n')
        self.assertEqual(anzahl, 3)
        self.assertEqual(zeilen[0], 'TOTAL:3')
        self.assertEqual([z for z in zeilen if z.startswith('PROGRESS:')],
                         ['PROGRESS:1/3', 'PROGRESS:2/3', 'PROGRESS:3/3'])

    def test_die_csv_bekommt_kopf_und_je_bild_eine_zeile(self):
        import io
        from contextlib import redirect_stdout
        with Pruefablage.ordner() as ordner:
            ziel = '%s/punkte.csv' % ordner
            leer = Videolauf.leere_punkte(np)
            with redirect_stdout(io.StringIO()):
                self._lauf(4, ziel).schreiben(leer for _ in range(4))
            with open(ziel) as datei:
                zeilen = datei.read().strip().split('\n')
        self.assertEqual(len(zeilen), 5)
        self.assertTrue(zeilen[0].startswith('frameNumber,'))

    def test_rtmlib_ergebnisse_in_allen_formen(self):
        u"""rtmlib liefert je nach Modell (Punkte, Guete) oder nur Punkte."""
        punkte = np.zeros((1, 17, 3), dtype=np.float32)
        punkte[0, 0] = [10, 20, 0.9]
        for name, ergebnis in (('Tupel', (punkte, None)),
                               ('nur Punkte', punkte),
                               ('ohne Personenachse', punkte[0])):
            with self.subTest(form=name):
                aus = Videolauf.aus_rtmlib(ergebnis, np)
                self.assertEqual(aus.shape, (26, 3))
                self.assertEqual(list(aus[0]), [10.0, 20.0, 0.9])

    def test_ohne_zuversichtsspalte_wird_eins_ergaenzt(self):
        punkte = np.zeros((17, 2), dtype=np.float32)
        punkte[0] = [10, 20]
        self.assertEqual(Videolauf.aus_rtmlib(punkte, np)[0][2], 1.0)

    def test_kein_ergebnis_gibt_leere_punkte(self):
        for leer in (None, np.zeros((0, 17, 3), dtype=np.float32)):
            with self.subTest(wert=type(leer).__name__):
                aus = Videolauf.aus_rtmlib(leer, np)
                self.assertEqual(aus.shape, (26, 3))
                self.assertEqual(float(np.abs(aus).sum()), 0.0)
