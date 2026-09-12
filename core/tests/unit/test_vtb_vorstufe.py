# -*- coding: utf-8 -*-
u"""Die bildweise Vorstufe fuer GVHMR und GEM — der Teil ohne Grafikkarte
(12.09.2026).

Anlass: Auftrag e40a6521 (005_DanceLang, 7.538 Bilder) brach in GVHMRs
HMR2-Stufe mit `Unable to allocate 4.85 GiB` ab — die Demos lesen das ganze
Video in den Speicher. Die `Vorstufe` rechnet Spur, ViTPose und HMR2 in
Bloecken und legt die Dateien dort ab, wo die Demos sie suchen. Was sich
hier pruefen laesst:

* **Die Kommandozeile** der Vorstufe und der beiden Laeufe.
* **Die Dateinamen** stimmen mit dem ueberein, was GVHMRs Konfiguration und
  GEMs `demo_utils` lesen — sonst rechnet das Demo still alles noch einmal,
  im Speicher, und der Auftrag scheitert wie zuvor.
* **Die Stuetzstellen** der Kameraverfolgung sind die von SimpleVO
  (`arange(0, F, 8)` plus das letzte Bild).
* **`Gemvorhersage`** bricht ohne Vorstufe ab, statt selbst zu rechnen.
"""
import os
import re
import sys
import unittest

from ._wrappersuchpfad import TOOLS, Wrappersuchpfad
from ._pruefablage import Pruefablage

Wrappersuchpfad.setzen()

from gem_vorhersage import Gemvorhersage                    # noqa: E402
from gemlauf import Gemlauf                                 # noqa: E402
from gvhmrlauf import Gvhmrlauf                             # noqa: E402
from kameraverfolgung import Kameraverfolgung               # noqa: E402
from vorstufe import Vorstufe                               # noqa: E402

GVHMR = TOOLS / 'VideoToBVH' / 'GVHMR'
GEM = TOOLS / 'VideoToBVH' / 'GEM'


class DieKommandozeile(unittest.TestCase):

    def test_vorstufe_mit_format_und_kameraverfolgung(self):
        befehl = Vorstufe.befehl('tanz.mp4', 'aus', 'gem', True, 24.0)
        self.assertEqual(befehl[0], sys.executable)
        self.assertEqual(befehl[1], Vorstufe.SKRIPT)
        self.assertEqual(befehl[befehl.index('--format') + 1], 'gem')
        self.assertIn('--kamera_verfolgen', befehl)
        self.assertEqual(befehl[befehl.index('--f_mm') + 1], '24')

    def test_brennweite_null_bleibt_weg(self):
        """Django sendet `focal_length_mm: 0` — SimpleVO nimmt dann 24 mm,
        wie das Demo ohne `--f_mm`."""
        befehl = Vorstufe.befehl('tanz.mp4', 'aus', 'gvhmr', True, 0)
        self.assertNotIn('--f_mm', befehl)
        self.assertNotIn('--kamera_verfolgen',
                         Vorstufe.befehl('tanz.mp4', 'aus'))

    def test_unbekanntes_format_wird_abgewiesen(self):
        with self.assertRaises(ValueError):
            Vorstufe('tanz.mp4', 'aus', 'wham')

    def test_gem_faehrt_gem_vorhersage_statt_des_demos(self):
        lauf = Gemlauf('tanz.mp4', os.path.join('aus', 'tanz.bvh'))
        befehl = lauf.befehl('aus')
        self.assertTrue(befehl[1].endswith('gem_vorhersage.py'), befehl[1])
        self.assertEqual(lauf.vorstufenordner('aus'),
                         os.path.join('aus', 'tanz', 'preprocess'))

    def test_gvhmr_vorstufenordner_liegt_neben_dem_ergebnis(self):
        lauf = Gvhmrlauf('tanz.mp4', os.path.join('aus', 'tanz.bvh'))
        self.assertEqual(lauf.vorstufenordner(),
                         os.path.join('aus', 'tanz', 'preprocess'))
        self.assertEqual(os.path.dirname(lauf.ergebnisdatei('aus')),
                         os.path.dirname(lauf.vorstufenordner()))


class DieDateien(unittest.TestCase):

    def test_fehlende_werden_genannt_slam_nur_mit_verfolgung(self):
        with Pruefablage.ordner() as ordner:
            ohne = Vorstufe('tanz.mp4', ordner)
            self.assertEqual(sorted(ohne.fehlende()),
                             ['bbx', 'vit_features', 'vitpose'])
            mit = Vorstufe('tanz.mp4', ordner, kamera_verfolgen=True)
            self.assertIn('slam', mit.fehlende())
            open(os.path.join(ordner, 'bbx.pt'), 'wb').close()
            self.assertNotIn('bbx', mit.fehlende())

    def test_namen_sind_die_der_gvhmr_konfiguration(self):
        konfiguration = GVHMR / 'hmr4d' / 'configs' / 'demo.yaml'
        if not konfiguration.is_file():
            self.skipTest('GVHMR nicht eingelagert')
        text = konfiguration.read_text(encoding='utf-8')
        for name in Vorstufe.DATEINAMEN.values():
            self.assertTrue('/%s' % name in text, name)
        self.assertIn('preprocess_dir: ${output_dir}/preprocess', text)

    def test_namen_sind_die_von_gems_demo(self):
        """`bbx.pt` und `vit_features.pt` stehen in `demo_utils.py`,
        `vitpose.pt` im Demo-Skript selbst."""
        demo = GEM / 'scripts' / 'demo'
        if not demo.is_dir():
            self.skipTest('GEM nicht eingelagert')
        text = ''.join((demo / d).read_text(encoding='utf-8')
                       for d in ('demo_utils.py', 'demo_smpl_hpe.py'))
        for name in Gemvorhersage.DATEIEN:
            self.assertTrue('"%s"' % name in text, name)
        # GEM liest bbx.pt als nackten Tensor: `return torch.load(cache_path…)`
        self.assertRegex(text, r'bbx\.pt.*\n(.*\n){0,4}.*return torch\.load')

    def test_gem_vorhersage_bricht_ohne_vorstufe_ab(self):
        with Pruefablage.ordner() as ordner:
            with self.assertRaises(SystemExit):
                Gemvorhersage('tanz.mp4', ordner, 'x.ckpt').vorstufe_laden()


class DieStuetzstellen(unittest.TestCase):

    def test_wie_simplevo(self):
        import numpy as np
        for laenge in (1, 7, 8, 9, 16, 17, 298, 7538):
            erwartet = np.arange(0, laenge, 8).tolist()
            if erwartet[-1] != laenge - 1:
                erwartet.append(laenge - 1)
            gewaehlt = [i for i in range(laenge)
                        if Kameraverfolgung.ist_stuetzstelle(i, laenge)]
            self.assertEqual(gewaehlt, erwartet, laenge)

    def test_der_schritt_ist_der_von_simplevo(self):
        demo = GVHMR / 'tools' / 'demo' / 'demo.py'
        if not demo.is_file():
            self.skipTest('GVHMR nicht eingelagert')
        treffer = re.search(r'SimpleVO\(cfg\.video_path, scale=([\d.]+), '
                            r'step=(\d+)', demo.read_text(encoding='utf-8'))
        self.assertIsNotNone(treffer)
        self.assertEqual(float(treffer.group(1)), Vorstufe.MASSSTAB)
        self.assertEqual(int(treffer.group(2)), Kameraverfolgung.SCHRITT)
