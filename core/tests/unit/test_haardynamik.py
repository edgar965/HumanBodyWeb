# -*- coding: utf-8 -*-
"""Die Haar-Dynamik als Rezeptzeile `m.haar_dynamik(…)` (02.10.2026): Blenders Haar-Dynamik als Stoffsolver (GPU) auf das
Stranghaar einer Frisur.

WARUM: Der Solver (`Stoffsolver/haarsimulation.py`) war nirgends in die Pipeline „2D3D Kleider“ eingehängt. Die Tests halten fest,
was auf der Pipeline-Seite steht, ohne GPU, ohne Bibliothek und ohne Prozess (`_laufen` ist eine Attrappe, die ein Ergebnis
schreibt, `Haarablauf`): der Auftrag (Schwerkraft −Y, Körper, Mindestabstand, durchgereichte Argumente), die Wurzeln ohne Delta,
Kartenhaar als klarer Fehler, nichts abgelegt bei einem Fehler, die Rezeptzeile und dass die Automatik sie nie wählt. Die
Strähnen selbst (Index-Rückabbildung, Wurzel zuerst) prüft `test_haarstraehnen.py`.

Sabotage-Gegenproben: in `Haardynamik._abstand_m` den Faktor 9/8 weglassen → „Mindestabstand“ rot; `'haar_dynamik'` aus
`Begutachtungskritik.VERBOTEN` nehmen → „die Prüf-KI darf sie nicht“ rot; in `Haardynamik.simulieren` `ablegen` vor die Schleife
ziehen → „bleibt die Bibliothek unberührt“ rot."""

import json
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from Genesis9.rezeptumgebung import Rezeptumgebung

from core.dienste.begutachtungskritik import Begutachtungskritik
from core.dienste.begutachtungswerkzeug import Begutachtungswerkzeug
from core.dienste.haardynamik import Haardynamik

from ._haarablauf import Haarablauf
from ._haardaten import Haardaten

STRANG, KARTE = Haardaten.Strang, Haardaten.Karte


class HaardynamikTest(SimpleTestCase):
    def ordner(self):
        o = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(o.cleanup)
        return o.name

    def test_der_auftrag_hat_schwerkraft_minus_y_den_koerper_und_rechnet_auf_dem_geraet(self):
        a = Haarablauf([(STRANG(), None)])
        a.ausfuehren(self.ordner(), bilder=12)
        auftrag = a.auftraege[0]
        self.assertEqual(auftrag['schwerkraft'], [0.0, -9.81, 0.0])
        self.assertEqual((auftrag['bilder'], auftrag['rechner'], auftrag['material'], auftrag['dicke']),
                         (12, 'warp', 'vorgabe', 0.0))
        with np.load(auftrag['straehnen']) as d:
            np.testing.assert_allclose(d['punkte'], Haardaten.punkte()[[4, 1, 7, 2, 9, 0, 5]], atol=1e-6)   # Wurzel zuerst
            self.assertEqual(d['laengen'].tolist(), [4, 3])
            np.testing.assert_allclose(d['normalen'], [(0.0, 1.0, 0.0)] * 2, atol=1e-6)
        with np.load(auftrag['koerper']) as d:
            self.assertEqual(d['dreiecke'].shape, (2, 3))
        self.assertEqual(a.abgelegt[0][2], ['geometry'])

    def test_der_mindestabstand_ist_abstand_plus_dicke_mal_acht_neuntel(self):
        """Die Dicke des Körpers steht auf 0; `distance_min` ist so gewählt, dass `(abstand + dicke) · 8/9` die 2 mm ergibt."""
        a = Haarablauf([(STRANG(), None)])
        a.ausfuehren(self.ordner())
        auftrag = a.auftraege[0]
        mindest = (auftrag['haarargumente']['abstand'] + auftrag['dicke']) * 8.0 / 9.0
        self.assertAlmostEqual(mindest, Haardynamik.MINDESTABSTAND_MM * 1e-3, places=12)
        a3 = Haarablauf([(STRANG(), None)])
        a3.ausfuehren(self.ordner(), mindestabstand_mm=3.0)
        self.assertAlmostEqual(a3.auftraege[0]['haarargumente']['abstand'] * 8.0 / 9.0, 0.003, places=12)

    def test_haarargumente_und_material_gehen_unveraendert_in_den_auftrag_ein_eigener_abstand_gewinnt(self):
        a = Haarablauf([(STRANG(), None)])
        a.ausfuehren(self.ordner(), material='seide', material_felder={'biegung': 2.0}, biegung_zufall=0.3,
                     kontinuum={'zellgroesse': 0.01}, abstand=0.0025)
        auftrag = a.auftraege[0]
        self.assertEqual((auftrag['material'], auftrag['material_felder']), ('seide', {'biegung': 2.0}))
        self.assertEqual(auftrag['haarargumente'],
                         {'biegung_zufall': 0.3, 'kontinuum': {'zellgroesse': 0.01}, 'abstand': 0.0025})

    def test_die_wurzeln_bekommen_kein_delta_die_anderen_ihre_verschiebung_an_den_kaefigpunkten(self):
        a = Haarablauf([(STRANG(), None)])
        a.ausfuehren(self.ordner())
        delta = a.abgelegt[0][3][0]
        np.testing.assert_array_equal(delta[[4, 9]], 0.0)
        np.testing.assert_allclose(delta[[1, 7, 2, 0, 5]], (0.0, -0.02, 0.0), atol=1e-6)
        np.testing.assert_array_equal(delta[[3, 6, 8]], 0.0)

    def test_der_steckbrief_nennt_motor_schwerkraft_und_was_der_lauf_fand(self):
        brief = Haarablauf([(STRANG(), None)]).ausfuehren(self.ordner(), bilder=5)
        self.assertEqual((brief['art'], brief['motor'], brief['bilder'], brief['schwerkraft']),
                         ('haardynamik', 'stoffsolver', 5, 'Y unten'))
        self.assertEqual((brief['straehnen'], brief['umgedreht'], brief['wurzel_fern']), (2, 0, 0))
        self.assertEqual(brief['kopfhaut']['quelle'], 'kappe:Attrappe')
        self.assertEqual(brief['stoffsolver'][0]['wurzel_abstand_max_mm'], 4.0)

    def test_ein_teil_ohne_strang_bekommt_ein_leeres_delta_und_die_reihenfolge_der_teile_bleibt(self):
        a = Haarablauf([(KARTE(), None), (STRANG(), None)])
        a.ausfuehren(self.ordner())
        deltas = a.abgelegt[0][3]
        self.assertEqual(a.abgelegt[0][2], ['kappe', 'geometry'])
        np.testing.assert_array_equal(deltas[0], 0.0)
        self.assertEqual(deltas[0].shape, deltas[1].shape)
        self.assertGreater(float(np.abs(deltas[1]).max()), 0.01)

    def test_kartenhaar_ist_ein_klarer_fehler_und_es_wird_nichts_abgelegt(self):
        a = Haarablauf([(KARTE(), None)])
        with self.assertRaises(ValueError) as fehler:
            a.ausfuehren(self.ordner())
        self.assertIn('Stranghaar', str(fehler.exception))
        self.assertIn('haar_trim', str(fehler.exception))
        self.assertEqual((a.abgelegt, a.auftraege), ([], []))

    def test_eine_kleidung_ist_keine_frisur(self):
        a = Haarablauf([(STRANG(), None)], eintrag={'art': 'kleidung'})
        with self.assertRaises(ValueError) as fehler:
            a.ausfuehren(self.ordner())
        self.assertIn('keine Frisur', str(fehler.exception))

    def test_scheitert_der_solver_bei_einem_teil_bleibt_die_bibliothek_unberuehrt(self):
        a = Haarablauf([(STRANG(), None), (STRANG(), None)], fehler_im_teil=1)
        with self.assertRaises(RuntimeError):
            a.ausfuehren(self.ordner())
        self.assertEqual(a.abgelegt, [])                                            # abgelegt wird erst nach allen Teilen

    def test_der_prozess_ohne_bericht_oder_mit_fehler_ist_ein_runtime_error_mit_dem_grund(self):
        ordner = Path(self.ordner())
        auftrag, bericht = ordner / 'a_auftrag.json', ordner / 'a_bericht.json'
        prozess = mock.Mock()
        prozess.communicate.return_value = (b'Traceback\nboom', None)
        prozess.returncode = 1
        with mock.patch('core.dienste.haardynamik.subprocess.Popen', return_value=prozess):
            with self.assertRaises(RuntimeError) as fehler:
                Haardynamik(ordner)._laufen(auftrag, bericht)
            self.assertIn('ohne Bericht', str(fehler.exception))
            self.assertIn('boom', str(fehler.exception))

            def schreibt_fehler(timeout):
                bericht.write_text(json.dumps({'fehler': 'RuntimeError: keine CUDA-GPU'}), encoding='utf-8')
                return b'', None                                      # `_laufen` löscht den alten Bericht vor dem Start
            prozess.communicate.side_effect = schreibt_fehler
            with self.assertRaises(RuntimeError) as fehler:
                Haardynamik(ordner)._laufen(auftrag, bericht)
            self.assertIn('keine CUDA-GPU', str(fehler.exception))

    def test_der_erfolgsbericht_traegt_die_zeit_des_prozesses_und_die_der_zeitschritte(self):
        ordner = Path(self.ordner())
        auftrag, bericht = ordner / 'a_auftrag.json', ordner / 'a_bericht.json'
        prozess = mock.Mock()
        prozess.returncode = 0

        def schreibt_bericht(timeout):
            bericht.write_text(json.dumps({'sekunden': 2.2, 'rechner': 'warp-motor:cuda:0'}), encoding='utf-8')
            return b'', None
        prozess.communicate.side_effect = schreibt_bericht
        with mock.patch('core.dienste.haardynamik.subprocess.Popen', return_value=prozess):
            daten = Haardynamik(ordner)._laufen(auftrag, bericht)
        self.assertEqual(daten['sim_s'], 2.2)                                         # nur die Zeitschritte des Solvers
        self.assertNotEqual(daten['sekunden'], 2.2)                                   # der ganze Prozess, hier fast 0

    def test_das_skript_der_haar_dynamik_ist_in_den_einstellungen_und_gibt_es(self):
        skript = Path(settings.STOFFSOLVER_HAARSKRIPT)
        self.assertEqual(skript.name, 'haar_lauf.py')
        self.assertTrue(skript.is_file(), skript)
        self.assertEqual(skript.parent, Path(settings.STOFFSOLVER_SKRIPT).parent)


class RezeptzeileTest(SimpleTestCase):
    def test_die_rezeptumgebung_kennt_den_arbeiter_und_lehnt_ohne_ihn_klar_ab(self):
        arbeiter = object()
        self.assertIs(Rezeptumgebung(haardynamik=arbeiter).haardynamik(), arbeiter)
        with self.assertRaises(ValueError) as fehler:
            Rezeptumgebung().haardynamik()
        self.assertIn('Haar-Dynamik', str(fehler.exception))

    def test_die_zeile_steht_in_der_liste_der_erlaubten_rezeptzeilen_und_ein_woerterbuch_geht_durch(self):
        self.assertIn('haar_dynamik', G9rezept.funktionen())
        aufrufe = G9rezept.pruefen("m.haar_dynamik('hair', bilder=12, material='seide', kontinuum={'zellgroesse': 0.01})")
        self.assertEqual(aufrufe[0][3], {'bilder': 12, 'material': 'seide', 'kontinuum': {'zellgroesse': 0.01}})
        text = {n: t for n, _s, t in ModellMitKleidern.hilfe()}['haar_dynamik']
        self.assertIn('STRANGHAAR', text)

    def test_ohne_runde_ist_die_zeile_ein_klarer_fehler(self):
        with self.assertRaises(ValueError) as fehler:
            ModellMitKleidern().haar_dynamik('hair')
        self.assertIn('Haar-Dynamik', str(fehler.exception))

    def test_die_zeile_ruft_den_arbeiter_mit_auftragsnamen_und_stellt_den_morph(self):
        arbeiter = mock.Mock()
        m = ModellMitKleidern()
        m.umgebung = Rezeptumgebung(haardynamik=arbeiter, auftrag='j1')
        G9rezept.anwenden(m, "m.haar_dynamik('hair', bilder=12, material='seide', mindestabstand_mm=3.0, biegung_zufall=0.3)")
        arbeiter.simulieren.assert_called_once_with('hair', 'dynamik_j1', 12, material='seide', mindestabstand_mm=3.0,
                                                    biegung_zufall=0.3)
        self.assertEqual(m.haar['hair.eigen.dynamik_j1'], 1.0)
        G9rezept.anwenden(m, "m.haar_dynamik('hair', name='fall', wert=0.5)")
        self.assertEqual(m.haar['hair.eigen.fall_j1'], 0.5)

    def test_die_pruef_ki_darf_sie_nicht(self):
        self.assertIn('haar_dynamik', Begutachtungskritik.VERBOTEN)
        grund = Begutachtungskritik({}, None)._pruefen("m.haar_dynamik('hair')", None, None, set(), {'hair'})
        self.assertIn('regelt die Automatik', grund)

    def test_die_automatik_schreibt_sie_nirgends(self):
        """Quelltext der Automatik (`Iteration*`, Rundenauswahl): kein `haar_dynamik` — Sache der Rezeptzeile von Hand."""
        ordner = Path(settings.TOOLS_ROOT) / '2d3DIterationen' / 'iterationen2d3d'
        dateien = sorted(ordner.glob('*.py'))
        self.assertGreater(len(dateien), 10)
        for datei in dateien:
            self.assertNotIn('haar_dynamik', datei.read_text(encoding='utf-8'), datei.name)

    def test_das_werkzeug_baut_den_arbeiter_im_ordner_des_auftrags(self):
        ablage = mock.Mock()
        ablage.arbeit.side_effect = lambda name: Path('A:/nirgends') / name
        arbeiter = Begutachtungswerkzeug(None, ablage).haardynamik()
        self.assertIsInstance(arbeiter, Haardynamik)
        self.assertEqual(arbeiter.ordner, Path('A:/nirgends') / 'haardynamik')


class BaumTest(SimpleTestCase):
    def test_der_baum_steht_im_workflow_mit_klassenkarten_und_gemessenen_zeiten(self):
        from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
        from core.dienste.architektur2d3dworkflow import Architektur2d3dworkflow
        baeume = {b.kennung: b for b in Architektur2d3dworkflow.baeume()}
        baum = baeume['haardynamik']
        katalog = {k for _m, k in Architektur2d3dklassen.alle()}
        self.assertTrue({'Haardynamik', 'Haarstraehnen', 'Haarauftrag', 'Haarsimulation'} <= baum.klassen())
        self.assertTrue(baum.klassen() <= katalog, baum.klassen() - katalog)
        for knoten in baum.wurzel.alle():
            for _name, zeit in knoten.teile:
                self.assertTrue(zeit.gemessen)
                self.assertIn('nicht in der Pipeline gemessen', zeit.quelle)
