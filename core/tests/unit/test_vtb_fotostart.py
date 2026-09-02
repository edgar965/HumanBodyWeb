# -*- coding: utf-8 -*-
u"""Der Start der beiden anderen Foto-Backends: HMR 2.0 und PyMAF-X.

DER ANLASS (02.09.2026)
=======================
In beiden Runnern lag der Modellstart mitten im Ablauf. `_run_hmr2.main`
hatte 70 Zeilen Vorbereitung, bevor das erste Bild gelesen wurde — drei
davon greifen in fremde Bibliotheken ein (torch.load umbiegen, pyrender
durch eine Attrappe ersetzen, Fremdprotokolle leiser stellen) und
standen nur als Kommentarblock da. `_run_pymafx.main` war mit 207
Zeilen und 28 Verzweigungen der komplexeste Rumpf im Baum; das Auslesen
der Modellausgabe machte davon 60 Zeilen aus, viermal fast dasselbe.

WAS DIESE PRUEFUNG NICHT IST
============================
Sie startet weder HMR 2.0 noch PyMAF-X — beide brauchen CUDA-torch,
Gewichte und in einem Fall eine eigene Python-Umgebung (python8ENV).
Geprueft wird, was ohne all das prueffaehig ist: die Eingriffe, die
Personenauswahl und das Herausziehen der Werte aus der Ausgabe.

BDD - GEGEBEN / DANN
====================
    DerHmr2Start     ... biegt torch.load um und waehlt die beste Person
    DiePymafxAusgabe ... zieht Form, Ausdruck, Kamera und Kasten heraus
    DerPymafxLauf    ... nimmt genau eine Person ueber der Guetegrenze
"""
import logging
import os
import sys
import types
import unittest

from ._erkennerattrappen import Detectronattrappe, Erkennungen
from ._pruefablage import Pruefablage
from ._tensorattrappe import Tensorattrappe
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402

from ganzkoerperpunkte import Ganzkoerperpunkte             # noqa: E402
from hmr2start import Hmr2start                             # noqa: E402
from pymafxausgabe import Pymafxausgabe                     # noqa: E402
from pymafxlauf import Pymafxlauf                           # noqa: E402


class DerHmr2Start(unittest.TestCase):
    u"""Drei Eingriffe in fremde Bibliotheken, benannt und begruendet."""

    #: Eine Person (Klasse 0), ein Hund (16), eine unsichere Person.
    KLASSEN = [0, 16, 0]
    GUETE = [0.72, 0.99, 0.31]
    KAESTEN = [[10.0, 20.0, 110.0, 220.0],
               [0.0, 0.0, 50.0, 50.0],
               [1.0, 1.0, 2.0, 2.0]]

    def _detektor(self, klassen=None, guete=None):
        return Detectronattrappe(Erkennungen(
            self.KLASSEN if klassen is None else klassen,
            self.GUETE if guete is None else guete,
            self.KAESTEN))

    # ------------------------------------------------------- torch.load

    def test_weights_only_wird_ueberschrieben_nicht_vorbelegt(self):
        u"""Der Befund: pytorch_lightning uebergibt den Schalter selbst.

        Eine Vorbelegung (`kwargs.setdefault`) waere wirkungslos — der
        HMR2-Gewichtssatz enthaelt omegaconf-Objekte, und das Laden
        braechte weiter ab.
        """
        gesehen = []
        attrappe = types.ModuleType('torch')
        attrappe.load = lambda pfad, **benannt: gesehen.append(benannt)
        self.addCleanup(sys.modules.pop, 'torch', None)
        sys.modules['torch'] = attrappe

        vorher = Hmr2start.torch_ohne_pruefung()
        attrappe.load('gewichte.pt', weights_only=True)
        self.assertEqual(gesehen, [{'weights_only': False}])
        self.assertIsNot(attrappe.load, vorher)

    # -------------------------------------------------------- pyrender

    def test_pyrender_wird_durch_leere_klassen_ersetzt(self):
        u"""`renderer.py` nennt sie auf Modulebene; OpenGL gibt es nicht."""
        vorher = sys.modules.get('pyrender')
        self.addCleanup(lambda: sys.modules.__setitem__('pyrender', vorher)
                        if vorher is not None
                        else sys.modules.pop('pyrender', None))
        attrappe = Hmr2start.ohne_pyrender()
        self.assertIs(sys.modules['pyrender'], attrappe)
        for name in Hmr2start.PYRENDER_NAMEN:
            with self.subTest(name=name):
                klasse = getattr(attrappe, name)
                self.assertIsNotNone(klasse(1, zwei=2))

    def test_die_namensliste_deckt_den_renderer(self):
        u"""Fehlt einer, scheitert erst der Import — nicht der Aufbau."""
        for name in ('Node', 'Mesh', 'Scene', 'OffscreenRenderer',
                     'IntrinsicsCamera', 'Viewer'):
            self.assertIn(name, Hmr2start.PYRENDER_NAMEN)

    # ------------------------------------------------------- Protokoll

    def test_die_lauten_bibliotheken_werden_leiser(self):
        for name in Hmr2start.LAUTE:
            logging.getLogger(name).setLevel(logging.DEBUG)
        Hmr2start.leiser()
        for name in Hmr2start.LAUTE:
            with self.subTest(name=name):
                self.assertEqual(logging.getLogger(name).level,
                                 logging.WARNING)

    # -------------------------------------------------------- Erkennung

    def test_die_zuversichtlichste_person_gewinnt(self):
        u"""Anders als bei SMPLest-X: HMR 2.0 bekommt EINEN Kasten."""
        kasten, guete = Hmr2start.beste_person(self._detektor(), None)
        self.assertEqual(kasten.shape, (1, 4))
        self.assertEqual(list(kasten[0]), [10.0, 20.0, 110.0, 220.0])
        self.assertAlmostEqual(guete, 0.72, places=5)

    def test_ein_hund_zaehlt_nicht_als_person(self):
        u"""Der Hund ist der sicherste Treffer — und der falsche."""
        kasten, _guete = Hmr2start.beste_person(self._detektor(), None)
        self.assertNotEqual(list(kasten[0]), [0.0, 0.0, 50.0, 50.0])

    def test_unter_der_schwelle_zaehlt_niemand(self):
        kasten, guete = Hmr2start.beste_person(
            self._detektor(guete=[0.3, 0.4, 0.1]), None)
        self.assertIsNone(kasten)
        self.assertEqual(guete, 0.0)

    def test_die_schwellen_liegen_wie_bisher(self):
        u"""Was der Detektor gar nicht meldet, rettet die zweite nicht."""
        self.assertEqual(Hmr2start.SCHWELLE_KOPF, 0.25)
        self.assertEqual(Hmr2start.SCHWELLE_PERSON, 0.5)
        self.assertLess(Hmr2start.SCHWELLE_KOPF, Hmr2start.SCHWELLE_PERSON)


class DiePymafxAusgabe(unittest.TestCase):
    u"""Vier Felder aus `mesh_out`, jedes frueher mit eigenem Vorspann."""

    THETA = [0.1] * 10

    def _felder(self, **abweichend):
        felder = {
            Pymafxausgabe.FORM: Tensorattrappe([[0.5] * 11]),
            Pymafxausgabe.AUSDRUCK: Tensorattrappe([[0.25, 0.5]]),
            Pymafxausgabe.KAMERA: Tensorattrappe([[0.9, 0.0, 0.5]]),
            Pymafxausgabe.NETZ: None,
        }
        felder.update(abweichend)
        return [felder]

    def _ausgabe(self, **abweichend):
        return Pymafxausgabe(self.THETA, self._felder(**abweichend),
                             np.array([[50.0, 60.0, 100.0, 200.0]]),
                             np.array([1.25]))

    def test_pred_shape_schlaegt_die_theta_betas(self):
        u"""Elf Werte aus dem SMPL-X-Kopf sind genauer als zehn aus theta."""
        self.assertEqual(len(self._ausgabe().betas()), 11)
        self.assertEqual(self._ausgabe().betas()[0], 0.5)

    def test_zu_wenige_werte_lassen_theta_stehen(self):
        u"""Weniger als zehn Parameter waeren ein Rueckschritt."""
        kurz = self._ausgabe(**{Pymafxausgabe.FORM: Tensorattrappe([[0.5] * 3])})
        self.assertEqual(kurz.betas(), self.THETA)

    def test_ohne_pred_shape_bleibt_theta(self):
        ohne = self._ausgabe(**{Pymafxausgabe.FORM: None})
        self.assertEqual(ohne.betas(), self.THETA)

    def test_der_ausdruck_kommt_als_liste(self):
        self.assertEqual(self._ausgabe().ausdruck(), [0.25, 0.5])

    def test_ohne_ausdruck_eine_leere_liste(self):
        ohne = self._ausgabe(**{Pymafxausgabe.AUSDRUCK: None})
        self.assertEqual(ohne.ausdruck(), [])

    def test_die_kameradaten_kommen_mit(self):
        self.assertEqual(self._ausgabe().kameradaten(), [0.9, 0.0, 0.5])

    def test_kasten_und_massstab_kommen_aus_dem_datensatz(self):
        ausgabe = self._ausgabe()
        self.assertEqual(ausgabe.kasten(), [50.0, 60.0, 100.0, 200.0])
        self.assertAlmostEqual(ausgabe.massstab(), 1.25, places=5)

    def test_ohne_datensatz_kein_kasten(self):
        u"""`Inference` kann leer ausgehen — das darf nicht abstuerzen."""
        ausgabe = Pymafxausgabe(self.THETA, self._felder())
        self.assertIsNone(ausgabe.kasten())
        self.assertIsNone(ausgabe.massstab())

    def test_ohne_felder_bleibt_alles_leer(self):
        leer = Pymafxausgabe(self.THETA, [])
        self.assertEqual(leer.betas(), self.THETA)
        self.assertEqual(leer.ausdruck(), [])
        self.assertIsNone(leer.kameradaten())
        self.assertIsNone(leer.netz_speichern('/egal/foto.jpg'))

    def test_das_netz_landet_neben_dem_bild(self):
        ausgabe = self._ausgabe(**{
            Pymafxausgabe.NETZ: Tensorattrappe(
                [np.zeros((7, 3), dtype=np.float32)])})
        with Pruefablage.ordner() as ordner:
            pfad = ausgabe.netz_speichern(os.path.join(ordner, 'foto.jpg'))
            self.assertEqual(os.path.basename(pfad),
                             Pymafxausgabe.VERTEXDATEI)
            self.assertEqual(np.load(pfad).shape, (7, 3))


class Personenattrappe:
    u"""Eine Erkennung von openpifpaf: 133 Punkte und eine Guete."""

    def __init__(self, guete, marke=0.0):
        self.score = guete
        self.data = np.full((133, 3), marke, dtype=np.float32)


class Vorhersageattrappe:
    u"""Ein openpifpaf-`Predictor`, der eine feste Antwort gibt."""

    def __init__(self, personen):
        self.personen = personen
        self.dateien = None

    def images(self, dateien):
        self.dateien = dateien
        yield self.personen, None, {'dataset_index': 7}


class DerPymafxLauf(unittest.TestCase):
    u"""Eine Person, ueber der Guetegrenze — mehr nimmt die Analyse nicht."""

    def test_die_erkannte_person_wird_uebernommen(self):
        vorhersage = Vorhersageattrappe([Personenattrappe(0.8, 1.0)])
        gefunden = Pymafxlauf.personen(vorhersage, 'foto.jpg', np)
        self.assertEqual(list(gefunden), ['person_0'])
        self.assertAlmostEqual(gefunden['person_0']['score'], 0.8, places=5)
        self.assertEqual(gefunden['person_0']['frames'], [7])

    def test_unter_der_guetegrenze_kommt_nichts(self):
        schwach = Ganzkoerperpunkte.SCHWELLE - 0.01
        vorhersage = Vorhersageattrappe([Personenattrappe(schwach)])
        self.assertEqual(
            Pymafxlauf.personen(vorhersage, 'foto.jpg', np), {})

    def test_nur_die_erste_person_zaehlt(self):
        u"""Die Fotoanalyse gilt einem Menschen; wer sonst waere gemeint?"""
        vorhersage = Vorhersageattrappe([Personenattrappe(0.8),
                                         Personenattrappe(0.9)])
        self.assertEqual(len(Pymafxlauf.personen(vorhersage, 'f.jpg', np)), 1)

    def test_der_predictor_bekommt_einen_absoluten_pfad(self):
        u"""`Inference` liest den Ordner selbst — ein relativer Pfad
        haengt am Arbeitsverzeichnis, das der Runner vorher wechselt.
        """
        vorhersage = Vorhersageattrappe([Personenattrappe(0.8)])
        Pymafxlauf.personen(vorhersage, 'foto.jpg', np)
        self.assertTrue(os.path.isabs(vorhersage.dateien[0]))

    def test_die_indexgrenzen_teilen_alle_133_punkte_auf(self):
        u"""Koerper, Fuesse, Gesicht, zwei Haende — nichts faellt weg."""
        vorhersage = Vorhersageattrappe([Personenattrappe(0.8)])
        eintrag = Pymafxlauf.personen(vorhersage, 'f.jpg', np)['person_0']
        self.assertEqual(len(eintrag['joints2d'][0]), 17)
        self.assertEqual(len(eintrag['joints2d_face'][0]), 68)
        self.assertEqual(len(eintrag['joints2d_lhand'][0]), 21)
        self.assertEqual(len(eintrag['joints2d_rhand'][0]), 21)

    def test_theta_traegt_kamera_und_form(self):
        u"""`theta[3:13]` sind die zehn Formparameter der SMPL-Konvention."""
        self.assertEqual((Pymafxlauf.BETAS.start, Pymafxlauf.BETAS.stop),
                         (3, 13))

    def test_die_letzte_verfeinerungsstufe_zaehlt(self):
        self.assertEqual(Pymafxlauf.STUFE, -1)
