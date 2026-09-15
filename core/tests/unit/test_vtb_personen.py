# -*- coding: utf-8 -*-
u"""Mehrere Personen im Video: ein BVH je Person, synchron (14.09.2026).

Edgar: „Ich habe öfter 2 oder mehr Personen im Video, dann ist die BVH
kaputt. bei mehreren Personen brauche ich mehrere BVHs, die aber synchron
sein sollen, damit ich auch 2 Modelle haben kann."

Bisher nahm `get_one_track` die Spur mit der größten Kastenfläche — bei zwei
Tänzern eine Mischung aus beiden, sobald der Tracker beim Kreuzen die
Kennung wechselt. Jetzt: `Spurwahl` behält alle Spuren, `Vorstufe --person n`
nimmt die n-te, `Personenlauf` fährt GVHMR/GEM je Person unter eigenem
Ordner, `Personenergebnisse` trägt `<stamm>_p2.bvh` … am Auftrag ein.
Geprüft ohne Grafikkarte:

1. `Spurwahl`: Rangfolge nach Flächensumme (GVHMRs Maß — Rang 1 ist die
   Spur von bisher), Deckung, ab Rang 2 nur Spuren mit 50 % Deckung (Dance1:
   eine Spur mit 2 Bildern von 125 wäre sonst eine Person aus Interpolation),
   Ablage `.npz` hin und zurück; Bruchstücke einer Spur verkettet (002_Dance:
   zwei Kennungen für eine Tänzerin, die ersten 272 Bilder hatten bisher den
   Kasten von Bild 273).
2. `Personenlauf`: Namen (`_p2`, Ordner `p2/`, Spurablage), ein Lauf je
   Person mit `person`/`spuren`, SimpleVO von Person 1 übernommen, und nach
   Person 1 höchstens so viele Personen, wie die Spurablage hergibt.
3. Die Kommandozeile: `Vorstufe --person --spuren`, `Gvhmrlauf`/`Gemlauf`
   rechnen ab Person 2 unter `p<n>/`, `lift_3d --persons`, `Lifterwahl`.
4. Django: `Smplbefehl` sendet `--persons` nur ab 2 und nur für GVHMR/GEM,
   `Pipelineparameter` liest das Feld, `Personenergebnisse` findet und
   trägt ein, `Pipelinefelder.js`/Karten/URL kennen das Feld.

Sabotage-Gegenproben: `rangfolge` ohne `reverse` → Fall 1 rot; `wurzel`
ohne `p<n>` → Fall 2/3 rot; `MIT_PERSONEN` ohne `gem` → Fall 4 rot.
"""
import os
import re
import sys
import unittest

import numpy as np
from django.test import SimpleTestCase, override_settings

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import TOOLS, Wrappersuchpfad
from ..attrappen import AuftragsAttrappe

Wrappersuchpfad.setzen()

from gemlauf import Gemlauf                                 # noqa: E402
from gvhmrlauf import Gvhmrlauf                             # noqa: E402
from lifterwahl import Lifterwahl                           # noqa: E402
from personenlauf import Personenlauf                       # noqa: E402
from spurwahl import Spurwahl                               # noqa: E402
from vorstufe import Vorstufe                               # noqa: E402

WRAPPERS = TOOLS / 'VideoToBVH' / 'wrappers'
WEB = TOOLS / 'HumanBodyWeb'


def verlauf():
    u"""Zehn Bilder: A groß und immer da, B mittel in acht Bildern, C klein
    in zwei (läuft durchs Bild)."""
    bilder = []
    for i in range(10):
        bild = [{'id': 1, 'bbx_xyxy': np.array([10, 10, 110, 310], float)}]
        if i < 8:
            bild.append({'id': 2, 'bbx_xyxy': np.array([200, 20, 280, 260], float)})
        if 4 <= i < 6:
            bild.append({'id': 3, 'bbx_xyxy': np.array([500, 100, 540, 220], float)})
        bilder.append(bild)
    return bilder


class DieSpurwahl(unittest.TestCase):

    def setUp(self):
        self.wahl = Spurwahl(verlauf(), 10, 640, 360)

    def test_rangfolge_nach_flaechensumme(self):
        self.assertEqual(self.wahl.rangfolge(), [1, 2, 3])
        self.assertAlmostEqual(self.wahl.flaechensumme(1), 10 * 100 * 300 / 640 / 360)
        self.assertEqual(self.wahl.kennung(1), 1)
        self.assertEqual(self.wahl.kennung(2), 2)

    def test_deckung_und_personen(self):
        self.assertAlmostEqual(self.wahl.deckung(2), 0.8)
        self.assertAlmostEqual(self.wahl.deckung(3), 0.2)
        self.assertEqual(self.wahl.personen(), [1, 2])
        self.assertEqual(self.wahl.personen(0.1), [1, 2, 3])

    def test_ab_rang_2_nur_gedeckte_spuren(self):
        self.assertEqual(self.wahl.weitere(), [2])
        self.assertEqual(self.wahl.anzahl(), 2)
        with self.assertRaises(ValueError):
            self.wahl.kennung(3)                    # Spur 3: 20 % Deckung
        with self.assertRaises(ValueError):
            self.wahl.kennung(0)
        # Rang 1 bleibt die groesste Spur, auch ohne Deckung (wie bisher)
        kurz = Spurwahl(verlauf()[:4] + [[] for _ in range(6)], 10, 640, 360)
        self.assertEqual(kurz.personen(), [])
        self.assertEqual(kurz.kennung(1), 1)
        self.assertEqual(kurz.anzahl(), 1)

    def test_bericht_nennt_jede_spur(self):
        zeilen = self.wahl.bericht()
        self.assertEqual(len(zeilen), 3)
        self.assertIn('Spur 2: Kennung 2, 8 von 10 Bildern (80 %)', zeilen[1])

    def test_ablage_hin_und_zurueck(self):
        with Pruefablage.ordner('spuren_') as ordner:
            pfad = os.path.join(ordner, 'tanz_spuren.npz')
            self.wahl.speichern(pfad)
            geladen = Spurwahl.laden(pfad)
        self.assertEqual(geladen.rangfolge(), [1, 2, 3])
        self.assertEqual(geladen.laenge, 10)
        self.assertEqual(geladen.bilder[2].tolist(), list(range(8)))
        np.testing.assert_array_equal(geladen.kaesten[3], self.wahl.kaesten[3])

    def test_bruchstuecke_werden_verkettet(self):
        u"""002_Dance: eine Taenzerin, zwei Kennungen (0-271 und 273-1003, ein
        Bild Luecke, Sprung 0,44 Hoehen). Hier: Spur 4 (Bilder 0-3) und Spur 5
        (Bilder 5-9) am selben Ort -> eine; Spur 2 (0-7) ueberlappt beide
        und bleibt getrennt; ein Sprung ueber eine Kastenhoehe trennt."""
        bilder = verlauf()
        for i in range(10):
            bilder[i] = [e for e in bilder[i] if e['id'] != 1]
            if i < 4:
                bilder[i].append({'id': 4, 'bbx_xyxy': np.array([300, 50, 380, 250], float)})
            if i >= 5:
                bilder[i].append({'id': 5, 'bbx_xyxy': np.array([330, 60, 410, 260], float)})
        wahl = Spurwahl(bilder, 10, 640, 360)
        self.assertEqual(wahl.verketten(), 1)
        self.assertEqual(sorted(wahl.bilder), [2, 3, 4])
        self.assertEqual(wahl.bilder[4].tolist(), [0, 1, 2, 3, 5, 6, 7, 8, 9])
        self.assertEqual(len(wahl.kaesten[4]), 9)
        self.assertEqual(wahl.verketten(), 0)
        # Zu weit: Spur 5 eine ganze Kastenhoehe darunter
        weit = verlauf()
        for i in range(10):
            weit[i] = [e for e in weit[i] if e['id'] != 1]
            if i < 4:
                weit[i].append({'id': 4, 'bbx_xyxy': np.array([300, 50, 380, 250], float)})
            if i >= 5:
                weit[i].append({'id': 5, 'bbx_xyxy': np.array([300, 300, 380, 500], float)})
        self.assertEqual(Spurwahl(weit, 10, 640, 360).verketten(), 0)

    def test_leerer_verlauf(self):
        leer = Spurwahl([[] for _ in range(5)], 5, 640, 360)
        self.assertEqual(leer.rangfolge(), [])
        with Pruefablage.ordner('spuren_') as ordner:
            pfad = leer.speichern(os.path.join(ordner, 'leer.npz'))
            self.assertEqual(Spurwahl.laden(pfad).rangfolge(), [])


class LaufAttrappe:
    u"""Merkt sich, womit `Personenlauf` sie baut; `fahren` gibt das BVH."""
    gebaut = []

    def __init__(self, video_pfad, ziel_bvh, person=1, spuren=None, **rest):
        self.video_pfad, self.ziel_bvh = video_pfad, ziel_bvh
        self.person, self.spuren, self.rest = person, spuren, rest
        self.wurzel = Personenlauf.wurzel(ziel_bvh, person)
        LaufAttrappe.gebaut.append(self)

    def vorstufenordner(self):
        return os.path.join(self.wurzel, 'tanz', 'preprocess')

    def fahren(self):
        return self.ziel_bvh


class DerPersonenlauf(unittest.TestCase):

    def test_namen(self):
        self.assertEqual(Personenlauf.bvh_name('aus/gvhmr_tanz.bvh', 1), 'aus/gvhmr_tanz.bvh')
        self.assertEqual(Personenlauf.bvh_name('aus/gvhmr_tanz.bvh', 2), 'aus/gvhmr_tanz_p2.bvh')
        self.assertEqual(Personenlauf.wurzel('aus/gvhmr_tanz.bvh', 1), 'aus')
        self.assertEqual(Personenlauf.wurzel('aus/gvhmr_tanz.bvh', 3), os.path.join('aus', 'p3'))
        self.assertEqual(Personenlauf.spuren_datei('aus/x.bvh', 'ein/tanz.mp4'),
                         os.path.join('aus', 'tanz_spuren.npz'))

    def test_ein_lauf_je_person_mit_gemeinsamer_spurablage(self):
        LaufAttrappe.gebaut = []
        fertig = Personenlauf(LaufAttrappe, 'ein/tanz.mp4', 'aus/gvhmr_tanz.bvh', 3,
                              geraet='cuda').fahren()
        self.assertEqual(fertig, ['aus/gvhmr_tanz.bvh', 'aus/gvhmr_tanz_p2.bvh',
                                  'aus/gvhmr_tanz_p3.bvh'])
        self.assertEqual([l.person for l in LaufAttrappe.gebaut], [1, 2, 3])
        self.assertEqual({l.spuren for l in LaufAttrappe.gebaut},
                         {os.path.join('aus', 'tanz_spuren.npz')})
        self.assertEqual(LaufAttrappe.gebaut[0].rest, {'geraet': 'cuda'})

    def test_weniger_personen_als_bestellt(self):
        u"""Nach Person 1 liegt die Spurablage: das Video hat zwei Personen,
        bestellt sind drei — zwei BVHs, kein Abbruch."""
        LaufAttrappe.gebaut = []
        with Pruefablage.ordner('personen_') as ordner:
            ziel = os.path.join(ordner, 'gvhmr_tanz.bvh')
            Spurwahl(verlauf(), 10, 640, 360).speichern(
                Personenlauf.spuren_datei(ziel, 'ein/tanz.mp4'))
            fertig = Personenlauf(LaufAttrappe, 'ein/tanz.mp4', ziel, 3).fahren()
        self.assertEqual([os.path.basename(f) for f in fertig],
                         ['gvhmr_tanz.bvh', 'gvhmr_tanz_p2.bvh'])
        self.assertEqual(Personenlauf.verfuegbar('gibt/es/nicht.npz', 3), 3)

    def test_eine_person_laeuft_wie_bisher(self):
        LaufAttrappe.gebaut = []
        fertig = Personenlauf(LaufAttrappe, 'ein/tanz.mp4', 'aus/gvhmr_tanz.bvh').fahren()
        self.assertEqual(fertig, ['aus/gvhmr_tanz.bvh'])
        self.assertIsNone(LaufAttrappe.gebaut[0].spuren)
        self.assertEqual(LaufAttrappe.gebaut[0].person, 1)

    def test_kameraverfolgung_wird_uebernommen(self):
        with Pruefablage.ordner('personen_') as ordner:
            ziel = os.path.join(ordner, 'gvhmr_tanz.bvh')
            erster = LaufAttrappe('tanz.mp4', ziel, 1)
            zweiter = LaufAttrappe('tanz.mp4', Personenlauf.bvh_name(ziel, 2), 2)
            self.assertFalse(Personenlauf.kamera_uebernehmen(erster, zweiter))
            os.makedirs(erster.vorstufenordner())
            quelle = os.path.join(erster.vorstufenordner(), 'slam_results.pt')
            with open(quelle, 'wb') as f:
                f.write(b'kamera')
            self.assertTrue(Personenlauf.kamera_uebernehmen(erster, zweiter))
            kopie = os.path.join(zweiter.vorstufenordner(), 'slam_results.pt')
            self.assertTrue(os.path.isfile(kopie))
            self.assertIn(os.path.join('p2', 'tanz', 'preprocess'), kopie)
            # Schon da: nicht noch einmal
            self.assertFalse(Personenlauf.kamera_uebernehmen(erster, zweiter))


class DieKommandozeile(unittest.TestCase):

    def test_vorstufe_mit_person_und_spuren(self):
        befehl = Vorstufe.befehl('tanz.mp4', 'aus', 'gvhmr', person=2, spuren='s.npz')
        self.assertEqual(befehl[befehl.index('--person') + 1], '2')
        self.assertEqual(befehl[befehl.index('--spuren') + 1], 's.npz')
        # Person 1 ohne Ablage: die Kommandozeile von bisher
        self.assertNotIn('--person', Vorstufe.befehl('tanz.mp4', 'aus', 'gvhmr', person=1))
        self.assertNotIn('--spuren', Vorstufe.befehl('tanz.mp4', 'aus'))

    def test_vorstufe_parst_person_und_spuren(self):
        quelle = (WRAPPERS / 'vorstufe.py').read_text(encoding='utf-8')
        self.assertIn("'--person'", quelle)
        self.assertIn("'--spuren'", quelle)
        self.assertIn('spur_nach_rang', quelle)

    def test_gvhmr_rechnet_ab_person_2_im_eigenen_ordner(self):
        eins = Gvhmrlauf('ein/tanz.mp4', 'aus/gvhmr_tanz.bvh')
        zwei = Gvhmrlauf('ein/tanz.mp4', 'aus/gvhmr_tanz_p2.bvh', person=2, spuren='aus/tanz_spuren.npz')
        self.assertEqual(eins.ausgabewurzel, 'aus')
        self.assertEqual(zwei.ausgabewurzel, os.path.join('aus', 'p2'))
        self.assertEqual(zwei.befehl()[zwei.befehl().index('--output_root') + 1],
                         os.path.join('aus', 'p2'))
        self.assertEqual(zwei.vorstufenordner(),
                         os.path.join('aus', 'p2', 'tanz', 'preprocess'))
        self.assertEqual(zwei.ergebnisdatei(zwei.ausgabewurzel),
                         os.path.join('aus', 'p2', 'tanz', Gvhmrlauf.ERGEBNISDATEI))
        vorstufe = zwei.vorstufenbefehl(True)
        self.assertEqual(vorstufe[vorstufe.index('--person') + 1], '2')
        self.assertEqual(vorstufe[vorstufe.index('--spuren') + 1], 'aus/tanz_spuren.npz')
        self.assertIn('--kamera_verfolgen', vorstufe)
        self.assertNotIn('--kamera_verfolgen', zwei.vorstufenbefehl())

    def test_gem_rechnet_ab_person_2_im_eigenen_ordner(self):
        zwei = Gemlauf('ein/tanz.mp4', 'aus/gem_tanz_p2.bvh', person=2, spuren='s.npz')
        self.assertEqual(zwei.ausgabewurzel, os.path.join('aus', 'p2'))
        self.assertEqual(zwei.vorstufenordner(),
                         os.path.join('aus', 'p2', 'tanz', 'preprocess'))
        self.assertEqual(Gemlauf('ein/tanz.mp4', 'aus/gem_tanz.bvh').ausgabewurzel, 'aus')

    def test_lifterwahl_und_lift_3d_kennen_persons(self):
        for name in ('gvhmr', 'gem'):
            self.assertIn('persons', Lifterwahl.LIFTER[name][1], name)
        self.assertNotIn('persons', Lifterwahl.LIFTER['duomo'][1])
        quelle = (WRAPPERS / 'lift_3d.py').read_text(encoding='utf-8')
        self.assertIn("'--persons'", quelle)
        self.assertIn('persons=a.persons', quelle)
        for modul in ('gvhmr_lift', 'gem_lift'):
            lift = __import__(modul).lift
            self.assertIn('persons', lift.__code__.co_varnames[:lift.__code__.co_argcount], modul)


class EinstellungenAttrappe:
    smpl_device = 'cuda'
    gvhmr_static_cam = True
    gvhmr_focal_length_mm = 24.0
    gvhmr_smooth_sigma = 2.0
    gvhmr_joint_limits = True
    gvhmr_use_dpvo = False
    gvhmr_verbose = False
    gvhmr_render = False
    gem_static_cam = True
    gem_smooth_sigma = 2.0
    gem_joint_limits = True
    gem_render = False
    duomo_static_cam = True
    duomo_smooth_sigma = 2.0
    duomo_joint_limits = True


class Post(dict):
    def getlist(self, feld):
        return []


class DieDjangoSeite(SimpleTestCase):

    def befehl(self, pipeline, **params):
        from core.pipelines.smplbefehl import Smplbefehl
        with override_settings(PIPELINE_PYTHON='py.exe'):
            return Smplbefehl(AuftragsAttrappe(pipeline, params),
                              EinstellungenAttrappe()).bauen('lift_3d.py', 'tanz.mp4', 'out.bvh')

    def test_smplbefehl_sendet_persons_nur_ab_zwei(self):
        self.assertNotIn('--persons', self.befehl('gvhmr'))
        self.assertNotIn('--persons', self.befehl('gvhmr', persons=1))
        befehl = self.befehl('gvhmr', persons=2)
        self.assertEqual(befehl[befehl.index('--persons') + 1], '2')
        befehl = self.befehl('gem', persons='3')
        self.assertEqual(befehl[befehl.index('--persons') + 1], '3')
        self.assertNotIn('--persons', self.befehl('duomo', persons=2))
        self.assertNotIn('--persons', self.befehl('gvhmr', persons='x'))

    def test_pipelineparameter_liest_personen(self):
        from core.api.pipelineparameter import Pipelineparameter
        self.assertEqual(Pipelineparameter.lesen(Post(gvhmr_persons='2'), 'gvhmr')['persons'], 2)
        self.assertEqual(Pipelineparameter.lesen(Post(gem_persons='0'), 'gem')['persons'], 1)
        self.assertEqual(Pipelineparameter.lesen(Post(gem_persons='x'), 'gem')['persons'], 1)
        self.assertEqual(Pipelineparameter.lesen(Post(), 'gvhmr')['persons'], 1)
        self.assertEqual(Pipelineparameter.vorgaben(EinstellungenAttrappe2())['gem_persons'], 1)

    def test_personenergebnisse_finden_und_eintragen(self):
        from core.pipelines.personenergebnisse import Personenergebnisse
        with Pruefablage.ordner('personen_') as ordner:
            erste = os.path.join(ordner, 'gvhmr_tanz.bvh')
            for name in ('gvhmr_tanz.bvh', 'gvhmr_tanz_p3.bvh', 'gvhmr_tanz_p2.bvh',
                         'gvhmr_tanz_p2_keypoints2d.json'):
                with open(os.path.join(ordner, name), 'w') as f:
                    f.write('HIERARCHY')
            with open(os.path.join(ordner, 'gvhmr_tanz_p4.bvh'), 'w'):
                pass                                          # leer: kein Ergebnis
            gefunden = Personenergebnisse.finden(erste)
            self.assertEqual([os.path.basename(p) for p in gefunden],
                             ['gvhmr_tanz_p2.bvh', 'gvhmr_tanz_p3.bvh'])
            self.assertEqual(Personenergebnisse.nummer(gefunden[1]), 3)
            self.assertEqual(Personenergebnisse.finden(''), [])
            job = AuftragsAttrappe('gvhmr', name='tanz.mp4')
            eintraege = []
            ablage = os.path.join(ordner, 'A_Results')
            with override_settings(BVH_RESULTS_DIR=ablage):
                Personenergebnisse.eintragen(
                    job, erste, 'gvhmr', lambda pfad, quelle, zusatz: eintraege.append((pfad, quelle, zusatz)))
            self.assertEqual(job.bvh_file_personen, gefunden)
            self.assertEqual([os.path.basename(e[0]) for e in eintraege],
                             ['tanz_gvhmr_p2.bvh', 'tanz_gvhmr_p3.bvh'])
            self.assertEqual([e[2] for e in eintraege], ['_p2', '_p3'])
            self.assertTrue(os.path.isfile(os.path.join(ablage, 'tanz_gvhmr_p3.bvh')))

    def test_formular_karten_und_adresse(self):
        felder = (WEB / 'static' / 'js' / 'auftraege' / 'pipelinefelder.js').read_text(encoding='utf-8')
        gvhmr = re.search(r'\n        gvhmr: \[(.*?)\n        \],', felder, re.S).group(1)
        gem = re.search(r'\n        gem: \[(.*?)\n        \],', felder, re.S).group(1)
        self.assertIn("['persons', 'int']", gvhmr)
        self.assertIn("['persons', 'int']", gem)
        for karte, name in (('_pipeline_gvhmr.html', 'gvhmr_persons'),
                            ('_pipeline_gem.html', 'gem_persons')):
            quelle = (WEB / 'templates' / karte).read_text(encoding='utf-8')
            self.assertIn('name="%s"' % name, quelle, karte)
            self.assertIn('defaults.%s' % name, quelle, karte)
        urls = (WEB / 'core' / 'urls.py').read_text(encoding='utf-8')
        self.assertIn("name='serve_bvh_person'", urls)
        downloads = (WEB / 'templates' / '_ergebnis_downloads.html').read_text(encoding='utf-8')
        self.assertIn('serve_bvh_person', downloads)


class EinstellungenAttrappe2(EinstellungenAttrappe):
    u"""Alles, was `Pipelineparameter.vorgaben` liest."""
    def __getattr__(self, name):
        return 0
