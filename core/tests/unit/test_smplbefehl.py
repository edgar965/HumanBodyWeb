# -*- coding: utf-8 -*-
"""Smplbefehl — welche Schalter bei welcher Pipeline mitgehen.

WARUM (17.08.2026)
=================
`_run_smpl_pipeline` war 95 Zeilen, davon die Hälfte Befehlsaufbau für drei
Pipelines — ungedeckt, weil der Lauf eine Grafikkarte braucht. Die Falle ist die
Vorrang-Regel: Der Auftrag schlägt die Einstellung. Wer im Formular „feste
Kamera: nein" wählt, während in den Einstellungen „ja" steht, muss `--static_cam`
NICHT bekommen. Ein `or` an dieser Stelle (statt `get` mit Vorgabe) würde die
Abwahl verschlucken — und die Pipeline rechnet etwas anderes, als auf dem
Bildschirm stand.

Dazu der eine umgekehrte Schalter: Gelenkgrenzen sind AN; `--no_joint_limits`
erscheint nur, wenn sie ausdrücklich abgewählt sind.
"""

from django.test import SimpleTestCase, override_settings

from core.pipelines.smplbefehl import Smplbefehl
from core.tests.attrappen import AuftragsAttrappe


class EinstellungenAttrappe:
    smpl_device = 'cuda'
    gvhmr_static_cam = True
    gvhmr_focal_length_mm = 35.0
    gvhmr_smooth_sigma = 1.5
    gvhmr_joint_limits = False
    gvhmr_use_dpvo = False
    gvhmr_verbose = True
    gvhmr_render = True
    wham_estimate_local_only = True
    wham_run_smplify = False
    prompthmr_static_camera = True
    gem_static_cam = True
    # Vorgaben der neuen Pipelines (12.09.2026) — absichtlich NICHT die
    # Modellvorgaben, damit ein Rueckfall auf 2.0 / True / False auffaellt.
    gem_smooth_sigma = 3.5
    gem_joint_limits = True
    gem_render = False
    duomo_static_cam = True
    duomo_smooth_sigma = 2.0
    duomo_joint_limits = False
    gemx_static_cam = False
    gemx_smooth_sigma = 2.0


class SmplbefehlTest(SimpleTestCase):

    def befehl(self, pipeline, **params):
        auftrag = AuftragsAttrappe(pipeline, params)
        with override_settings(PIPELINE_PYTHON='py.exe'):
            return Smplbefehl(auftrag, EinstellungenAttrappe()).bauen(
                'lift_3d.py', 'tanz.mp4', 'out.bvh')

    # ------------------------------------------------------------- Grundgerüst

    def test_grundargumente_stehen_immer(self):
        befehl = self.befehl('gvhmr')
        for erwartet in ('--pipeline', 'gvhmr', '--video', 'tanz.mp4',
                         '--output', 'out.bvh', '--device', 'cuda'):
            self.assertIn(erwartet, befehl)

    def test_geraet_kommt_aus_dem_auftrag(self):
        self.assertIn('cpu', self.befehl('gvhmr', device='cpu'))

    # --------------------------------------------------------------- Vorrang

    def test_einstellung_gilt_ohne_auftragswert(self):
        self.assertIn('--static_cam', self.befehl('gvhmr'))

    def test_auftrag_schlaegt_die_einstellung(self):
        """Der Fall, der ohne Test durchfällt: ausdrücklich ABGEWÄHLT."""
        self.assertNotIn('--static_cam', self.befehl('gvhmr', static_cam=False))

    def test_dpvo_und_verbose_folgen_der_einstellung_auftrag_schlaegt(self):
        """Seit 12.09.2026 mit Einstellungsfeld (Attrappe: DPVO aus, Verbose
        an); vorher galten beide ohne Auftragswert als aus."""
        befehl = self.befehl('gvhmr')
        self.assertNotIn('--use_dpvo', befehl)
        self.assertIn('--verbose', befehl)
        self.assertIn('--use_dpvo', self.befehl('gvhmr', use_dpvo=True))
        self.assertNotIn('--verbose', self.befehl('gvhmr', verbose=False))

    # ---------------------------------------------------------- Je Pipeline

    def test_gvhmr_werte(self):
        befehl = self.befehl('gvhmr', focal_length_mm=50.0, smooth_sigma=1.5)
        self.assertEqual(befehl[befehl.index('--focal_length_mm') + 1], '50.0')
        self.assertEqual(befehl[befehl.index('--smooth_sigma') + 1], '1.5')

    def test_gvhmr_rendert_von_sich_aus_no_render_nur_bei_abwahl(self):
        """Der Lifter rendert wie das Demo; `--no_render` geht nur mit, wenn
        Auftrag oder Einstellung (Attrappe: an) es abwaehlen (12.09.2026).
        Der Hybrid-Lauf schickt keinen Wert und bekommt die Einstellung."""
        self.assertNotIn('--no_render', self.befehl('gvhmr'))
        self.assertNotIn('--render', self.befehl('gvhmr'))
        self.assertIn('--no_render', self.befehl('gvhmr', render=False))
        self.assertNotIn('--no_render', self.befehl('gem'))

    def test_gelenkgrenzen_sind_umgekehrt(self):
        """Grenzen AN heisst: kein Schalter. Die Attrappe hat sie fuer GVHMR
        ausgeschaltet — der Auftrag darf sie wieder einschalten."""
        self.assertNotIn('--no_joint_limits',
                         self.befehl('gvhmr', joint_limits=True))
        self.assertIn('--no_joint_limits',
                      self.befehl('gvhmr', joint_limits=False))
        self.assertIn('--no_joint_limits', self.befehl('gvhmr'))

    def test_wham_hat_eigene_schalter(self):
        befehl = self.befehl('wham')
        self.assertIn('--estimate_local_only', befehl)
        self.assertNotIn('--run_smplify', befehl)
        self.assertNotIn('--static_cam', befehl, 'gvhmr-Schalter gehören nicht dazu')

    def test_prompthmr_hat_eigenen_kameraschalter(self):
        befehl = self.befehl('prompthmr')
        self.assertIn('--static_camera', befehl)
        self.assertNotIn('--static_cam', befehl)

    def test_gem_teilt_glaettung_mit_gvhmr_aber_nicht_die_brennweite(self):
        """GEM (11.09.2026): --static_cam, --smooth_sigma, Gelenkgrenzen wie
        GVHMR; --focal_length_mm kennt es nicht, --render nur auf Wunsch."""
        befehl = self.befehl('gem', smooth_sigma=1.5)
        self.assertIn('--static_cam', befehl)
        self.assertEqual(befehl[befehl.index('--smooth_sigma') + 1], '1.5')
        self.assertNotIn('--focal_length_mm', befehl)
        self.assertNotIn('--render', befehl)
        self.assertNotIn('--no_joint_limits', befehl)
        mit = self.befehl('gem', static_cam=False, render=True, joint_limits=False)
        self.assertNotIn('--static_cam', mit)
        self.assertIn('--render', mit)
        self.assertIn('--no_joint_limits', mit)

    def test_duomo_feste_kamera_aus_der_einstellung_auftrag_schlaegt_sie(self):
        """DuoMo (12.09.2026): `duomo_static_cam` ist die Vorgabe (hier an),
        der Auftrag darf sie abwaehlen; Glaettung und Gelenkgrenzen wie GVHMR."""
        ohne = self.befehl('duomo', smooth_sigma=1.5, joint_limits=True)
        self.assertIn('--static_cam', ohne)
        self.assertEqual(ohne[ohne.index('--smooth_sigma') + 1], '1.5')
        self.assertNotIn('--focal_length_mm', ohne)
        mit = self.befehl('duomo', static_cam=False, joint_limits=False)
        self.assertNotIn('--static_cam', mit)
        self.assertIn('--no_joint_limits', mit)

    def test_gemx_glaettet_und_kennt_keine_brennweite(self):
        """GEM-X (12.09.2026): `gemx_static_cam` ist die Vorgabe (hier aus),
        Glaettung wie GVHMR; der Gelenkgrenzen-Schalter wird gesendet, der
        Wrapper ignoriert ihn (SOMA-Gelenke sind keine SMPL-Indizes)."""
        befehl = self.befehl('gemx', static_cam=True, smooth_sigma=3.0)
        self.assertIn('--static_cam', befehl)
        self.assertEqual(befehl[befehl.index('--smooth_sigma') + 1], '3.0')
        self.assertNotIn('--focal_length_mm', befehl)
        self.assertNotIn('--static_cam', self.befehl('gemx'))

    def test_glaettung_faellt_auf_die_einstellung_der_pipeline_zurueck(self):
        """Ohne Auftragswert gilt `<pipeline>_smooth_sigma` und
        `<pipeline>_joint_limits` (12.09.2026) — auch fuer GVHMR und damit
        fuer den Koerper-Durchlauf des Hybrid-Laufs, dessen Karte keine
        Glaettung anbietet. GEM-X hat keine Gelenkgrenzen: nie `--no_…`."""
        gem = self.befehl('gem')
        self.assertEqual(gem[gem.index('--smooth_sigma') + 1], '3.5')
        self.assertNotIn('--no_joint_limits', gem)
        duomo = self.befehl('duomo')
        self.assertEqual(duomo[duomo.index('--smooth_sigma') + 1], '2.0')
        self.assertIn('--no_joint_limits', duomo)
        gvhmr = self.befehl('gvhmr')
        self.assertEqual(gvhmr[gvhmr.index('--smooth_sigma') + 1], '1.5')
        self.assertIn('--no_joint_limits', gvhmr)
        self.assertNotIn('--no_joint_limits', self.befehl('gemx'))

    def test_jedes_einstellungsfeld_der_schalter_steht_im_modell(self):
        """Die Attrappe prueft den Aufrufer, nicht das Modell: Ein Feldname in
        `SCHALTER`, den `AppSettings` nicht hat, faellt erst im Betrieb auf."""
        from core.models import AppSettings
        felder = {f.name for f in AppSettings._meta.get_fields()}
        for pipeline, schalter in Smplbefehl.SCHALTER.items():
            for _schluessel, feld, _argument in schalter:
                if feld:
                    self.assertIn(feld, felder, '%s: %s' % (pipeline, feld))
                    self.assertTrue(hasattr(EinstellungenAttrappe, feld),
                                    'Attrappe ohne %s' % feld)
        for name in Smplbefehl.MIT_GLAETTUNG:
            self.assertIn(name + '_smooth_sigma', felder, name)
            self.assertTrue(hasattr(EinstellungenAttrappe, name + '_smooth_sigma'),
                            'Attrappe ohne %s_smooth_sigma' % name)

    def test_unbekannte_pipeline_bekommt_nur_das_grundgeruest(self):
        befehl = self.befehl('smplest_x')
        self.assertEqual([a for a in befehl if a.startswith('--')],
                         ['--pipeline', '--video', '--output', '--device'])
