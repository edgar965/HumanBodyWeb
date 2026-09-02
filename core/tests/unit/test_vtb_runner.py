# -*- coding: utf-8 -*-
u"""Die Runner-Bausteine von VideoToBVH — der Teil ohne Grafikkarte.

Die vier `_run_*`-Skripte laufen in eigenen Python-Umgebungen mit CUDA
und lassen sich hier nicht starten. Was sich sehr wohl pruefen laesst,
ist alles, was sie an reiner Umformung tun — und genau dort lagen zwei
Befunde:

* **`_run_pymafx` meldete jedes Foto mit 90 % Zuversicht.**
  `'confidence': 0.9` stand fest im Ergebnis, waehrend die beiden
  anderen Runner den echten Detektorwert durchreichen. Ein halb
  verdecktes Foto sah damit so sicher aus wie ein gutes.
* **Die Punktaufteilung stand mitten im ML-Teil.** openpifpaf liefert
  133 Zeilen, PyMAF-X will sie nach Koerperteilen getrennt — reine
  Indexarithmetik, die niemand prueffen konnte, weil sie zwischen
  Modellstart und Ausgabe eingebettet war.

BDD - GEGEBEN / DANN
====================
    DerRunnerrahmen       ... prueft Argumente und meldet als JSON
    DasFotoergebnis       ... traegt dieselben Pflichtfelder ueberall
    DieGanzkoerperpunkte  ... schneiden an den COCO-WholeBody-Grenzen
    DieSmplestxKonfiguration ... findet die Datei an beiden Orten
"""
import json
import os
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402

from fotoergebnis import Fotoergebnis                       # noqa: E402
from ganzkoerperpunkte import Ganzkoerperpunkte             # noqa: E402
from runnerrahmen import Runnerrahmen                       # noqa: E402
from smplestxkonfiguration import Smplestxkonfiguration     # noqa: E402


class DerRunnerrahmen(unittest.TestCase):
    u"""Argumente pruefen, Fremdprojekt einbinden, Ergebnis melden."""

    def _rahmen(self, ordner='.'):
        return Runnerrahmen('Probe', ordner)

    def _abfangen(self, rufen):
        u"""Die JSON-Zeile eines abbrechenden Aufrufs."""
        import io
        from contextlib import redirect_stdout
        ausgabe = io.StringIO()
        with redirect_stdout(ausgabe):
            with self.assertRaises(SystemExit) as beendet:
                rufen()
        return json.loads(ausgabe.getvalue().strip()), beendet.exception.code

    def test_ohne_argument_ein_fehler(self):
        daten, code = self._abfangen(
            lambda: self._rahmen().bildpfad(['_run_x.py']))
        self.assertIn('Aufruf', daten['error'])
        self.assertEqual(code, 1)

    def test_ein_fehlendes_bild_ist_ein_fehler(self):
        daten, code = self._abfangen(
            lambda: self._rahmen().bildpfad(['_run_x.py', '/gibt/es/nicht']))
        self.assertIn('nicht gefunden', daten['error'])
        self.assertEqual(code, 1)

    def test_ein_vorhandenes_bild_kommt_durch(self):
        with Pruefablage.datei('x', endung='.jpg') as pfad:
            self.assertEqual(
                self._rahmen().bildpfad(['_run_x.py', pfad]), pfad)

    def test_der_traceback_kommt_mit(self):
        u"""Ohne ihn steht im Protokoll „ImportError" und sonst nichts."""
        def werfen():
            try:
                raise ValueError('etwas ging schief')
            except ValueError as fehler:
                Runnerrahmen.abbrechen(str(fehler), mit_traceback=True)
        daten, _code = self._abfangen(werfen)
        self.assertEqual(daten['error'], 'etwas ging schief')
        self.assertIn('ValueError', daten['traceback'])

    def test_das_fremdprojekt_landet_im_suchpfad(self):
        import sys
        with Pruefablage.ordner() as ordner:
            Runnerrahmen('Probe', ordner).einbinden()
            self.assertIn(ordner, sys.path)
            sys.path.remove(ordner)

    def test_kein_zweiter_eintrag_fuer_denselben_pfad(self):
        import sys
        with Pruefablage.ordner() as ordner:
            rahmen = Runnerrahmen('Probe', ordner)
            rahmen.einbinden()
            rahmen.einbinden()
            try:
                self.assertEqual(sys.path.count(ordner), 1)
            finally:
                sys.path.remove(ordner)


class DasFotoergebnis(unittest.TestCase):
    u"""Acht Pflichtfelder, vorher dreimal von Hand gebaut."""

    def _ergebnis(self, **kw):
        werte = dict(backend='hmr2', modellart='smpl',
                     betas=[0.1] * 10, zuversicht=0.87)
        werte.update(kw)
        return Fotoergebnis(**werte)

    def test_die_pflichtfelder_sind_da(self):
        daten = self._ergebnis().als_dict()
        for feld in ('betas', 'expression', 'gender', 'confidence', 'mock',
                     'measurements', 'skin_color', 'backend', 'model_type',
                     'num_betas', 'num_expression'):
            with self.subTest(feld=feld):
                self.assertIn(feld, daten)

    def test_die_zuversicht_kommt_vom_aufrufer(self):
        u"""Der Befund: PyMAF-X meldete fest 0,9 statt des Messwerts."""
        self.assertEqual(self._ergebnis(zuversicht=0.31).als_dict()
                         ['confidence'], 0.31)

    def test_masse_und_hautfarbe_bleiben_leer(self):
        u"""Diese Backends messen nichts — `Morphzuordnung` rechnet."""
        daten = self._ergebnis().als_dict()
        self.assertIsNone(daten['measurements'])
        self.assertIsNone(daten['skin_color'])
        self.assertFalse(daten['mock'])

    def test_hoechstens_zehn_parameter(self):
        daten = self._ergebnis(betas=[0.1] * 30,
                               ausdruck=[0.2] * 30).als_dict()
        self.assertEqual(daten['num_betas'], 10)
        self.assertEqual(daten['num_expression'], 10)

    def test_ohne_ausdruck_eine_leere_liste(self):
        self.assertEqual(self._ergebnis().als_dict()['expression'], [])

    def test_zusatzfelder_kommen_dazu(self):
        daten = self._ergebnis().dazu(image_width=1920,
                                      pred_cam=[1.0, 0.0, 0.0]).als_dict()
        self.assertEqual(daten['image_width'], 1920)
        self.assertEqual(daten['pred_cam'], [1.0, 0.0, 0.0])

    def test_leere_zusatzfelder_fallen_weg(self):
        u"""Sonst stand `if x: result['x'] = x` hinter jedem Feld."""
        daten = self._ergebnis().dazu(posed_vertices_path=None).als_dict()
        self.assertNotIn('posed_vertices_path', daten)

    def test_das_geschlecht_bleibt_neutral(self):
        u"""Diese Backends schaetzen keins — das macht `Morphzuordnung`."""
        self.assertEqual(self._ergebnis().als_dict()['gender'], 'neutral')

    def test_die_antwort_ist_json_faehig(self):
        u"""Sie geht als eine Zeile ueber stdout."""
        daten = self._ergebnis().dazu(image_width=1920).als_dict()
        self.assertEqual(json.loads(json.dumps(daten))['image_width'], 1920)


class DieGanzkoerperpunkte(unittest.TestCase):
    u"""133 Punkte, an festen Grenzen geschnitten."""

    def _punkte(self):
        u"""Ein Feld, in dem x den Index verraet."""
        punkte = np.zeros((133, 3), dtype=np.float32)
        punkte[:, 0] = np.arange(133)
        punkte[:, 2] = 0.5
        return punkte

    def test_die_teile_haben_die_erwarteten_groessen(self):
        eintrag = Ganzkoerperpunkte.person(self._punkte(), 0.9, 0, np)
        self.assertEqual(eintrag['joints2d'][0].shape, (17, 3))
        self.assertEqual(eintrag['joints2d_lhand'][0].shape, (21, 3))
        self.assertEqual(eintrag['joints2d_rhand'][0].shape, (21, 3))
        self.assertEqual(eintrag['joints2d_face'][0].shape, (68, 3))

    def test_die_grenzen_liegen_richtig(self):
        eintrag = Ganzkoerperpunkte.person(self._punkte(), 0.9, 0, np)
        self.assertEqual(eintrag['joints2d'][0][0, 0], 0.0)
        self.assertEqual(eintrag['joints2d_lhand'][0][0, 0], 91.0)
        self.assertEqual(eintrag['joints2d_rhand'][0][0, 0], 112.0)

    def test_das_gesicht_wird_umsortiert(self):
        u"""FLAME will die Kinnlinie hinten, COCO-WholeBody fuehrt sie vorn."""
        eintrag = Ganzkoerperpunkte.person(self._punkte(), 0.9, 0, np)
        gesicht = eintrag['joints2d_face'][0]
        self.assertEqual(gesicht[0, 0], 40.0)      # 23 + 17
        self.assertEqual(gesicht[-1, 0], 39.0)     # 23 + 16
        self.assertEqual(sorted(gesicht[:, 0]),
                         [float(i) for i in range(23, 91)])

    def test_die_erkennungsguete_wird_uebernommen(self):
        self.assertEqual(
            Ganzkoerperpunkte.person(self._punkte(), 0.42, 0, np)['score'],
            0.42)

    def test_sammeln_gibt_drei_listen(self):
        eintrag = Ganzkoerperpunkte.person(self._punkte(), 0.9, 7, np)
        gelenke, bilder, teile = Ganzkoerperpunkte.sammeln([eintrag])
        self.assertEqual(len(gelenke), 1)
        self.assertEqual(bilder, [7])
        self.assertEqual(set(teile), set(Ganzkoerperpunkte.TEILE))

    def test_mehrere_personen_werden_aneinandergehaengt(self):
        eintraege = [Ganzkoerperpunkte.person(self._punkte(), 0.9, i, np)
                     for i in range(3)]
        gelenke, bilder, teile = Ganzkoerperpunkte.sammeln(eintraege)
        self.assertEqual(len(gelenke), 3)
        self.assertEqual(bilder, [0, 1, 2])
        self.assertEqual(len(teile['vis_face']), 3)


class DieSmplestxKonfiguration(unittest.TestCase):
    u"""Die Datei liegt an zwei moeglichen Stellen."""

    def test_beide_orte_werden_gesucht(self):
        kandidaten = Smplestxkonfiguration('/wurzel').kandidaten()
        self.assertEqual(len(kandidaten), 2)
        self.assertIn('pretrained_models', kandidaten[0])
        self.assertIn('configs', kandidaten[1])

    def test_ohne_datei_kommt_nichts(self):
        self.assertIsNone(Smplestxkonfiguration('/gibt/es/nicht').pfad())

    def test_die_zweite_stelle_zaehlt_auch(self):
        with Pruefablage.ordner() as wurzel:
            ordner = os.path.join(wurzel, 'configs')
            os.makedirs(ordner)
            pfad = os.path.join(ordner, 'config_smplest_x_h.py')
            open(pfad, 'w').close()
            self.assertEqual(Smplestxkonfiguration(wurzel).pfad(), pfad)

    def test_die_erste_stelle_gewinnt(self):
        with Pruefablage.ordner() as wurzel:
            erste = os.path.join(wurzel, 'pretrained_models', 'smplest_x_h')
            zweite = os.path.join(wurzel, 'configs')
            os.makedirs(erste)
            os.makedirs(zweite)
            open(os.path.join(erste, 'config_base.py'), 'w').close()
            open(os.path.join(zweite, 'config_smplest_x_h.py'), 'w').close()
            self.assertIn('pretrained_models',
                          Smplestxkonfiguration(wurzel).pfad())

    def test_die_laufnamen_bleiben_wie_bisher(self):
        u"""Der Ordner in `outputs/` soll erkennbar bleiben."""
        k = Smplestxkonfiguration('/wurzel')
        self.assertEqual(k.laufname('C:/b/portrait.jpg', '20260902_0010'),
                         'inference_portrait_20260902_0010')
        self.assertEqual(
            k.laufname('', '20260902_0010', vorsatz=k.VORSATZ_VIDEO),
            'video_expr_20260902_0010')

    def test_die_laufeinstellungen_nennen_gewicht_und_protokoll(self):
        einstellungen = Smplestxkonfiguration('/wurzel').laufeinstellungen(
            'bild.jpg', '20260902_0010')
        self.assertIn('pth.tar',
                      einstellungen['model']['pretrained_model_path'])
        self.assertIn('inference_bild_20260902_0010',
                      einstellungen['log']['log_dir'])
