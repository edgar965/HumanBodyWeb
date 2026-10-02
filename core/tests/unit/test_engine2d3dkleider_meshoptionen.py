# -*- coding: utf-8 -*-
"""Die Gruppe `mesh` von „2D3D Kleider" (02.10.2026): die Regler von TRELLIS.2 wie im Hugging-Face-Space
`microsoft/TRELLIS.2`, und „nur TRELLIS, kein Hunyuan" (`Engine2d3dKleidernurtrellis`). Rein rechnend: keine Datenbank, keine
Grafikkarte, kein torch — der Runner-Teil (`mesh_trellisregler`) ist absichtlich frei von schweren Importen.
"""

import glob
import io
import json
import re
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.engine2d3dkleidermeshoptionen import Engine2d3dKleidermeshoptionen
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.ollamamodelle import Ollamamodelle

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from mesh_trellisregler import Trellisregler  # noqa: E402  (erst nach dem Suchpfad)

STUFEN = ('ss', 'form', 'tex')
REGLER = ('fuehrung', 'rescale', 'schritte', 'rescale_t')


class OhneDienste(SimpleTestCase):
    """Die Figurkataloge fragen die Daz-Bibliothek, die Prüf-KIs Ollama — hier geht es nur um die Kataloge."""

    def setUp(self):
        for ziel, name, wert in (
            (Meshfiguroptionen, '_referenzen', [('', '—')]),
            (Ollamamodelle, 'mit_bildern', [('qwen3.8:27b', 'qwen3.8:27b (Q4_K_M)')]),
        ):
            patcher = mock.patch.object(ziel, name, return_value=wert)
            patcher.start()
            self.addCleanup(patcher.stop)


class Engine2d3dKleidermeshoptionenTest(OhneDienste):
    def test_jede_stufe_hat_die_vier_regler_des_space(self):
        vorgaben = Engine2d3dKleidermeshoptionen.vorgaben()
        erwartet = {'%s_%s' % (vor, regler) for vor in STUFEN for regler in REGLER}
        # Die Hauptfelder des Space in seiner Reihenfolge: Resolution, Seed, Randomize Seed, Decimation Target, Texture Size.
        haupt = ['aufloesung', 'seed', 'seed_zufall', 'flaechen', 'texturgroesse']
        self.assertEqual([k for k in vorgaben if k not in erwartet], haupt)
        self.assertLessEqual(erwartet, set(vorgaben))

    def test_die_vorgaben_sind_die_der_pipeline_json_von_trellis2(self):
        pfade = glob.glob(str(Path(settings.HF_HOME_DIR) / 'hub' / 'models--microsoft--TRELLIS.2-4B' / 'snapshots' / '*'
                              / 'pipeline.json'))
        if not pfade:
            self.skipTest('TRELLIS.2-4B liegt nicht in der HF-Ablage')
        args = json.loads(Path(pfade[0]).read_text(encoding='utf-8'))['args']
        quelle = {'ss': args['sparse_structure_sampler']['params'], 'form': args['shape_slat_sampler']['params'],
                  'tex': args['tex_slat_sampler']['params']}
        vorgaben = Engine2d3dKleidermeshoptionen.vorgaben()
        for vor, params in quelle.items():
            for regler, name in zip(REGLER, ('guidance_strength', 'guidance_rescale', 'steps', 'rescale_t'),
                                    strict=True):
                self.assertEqual(vorgaben['%s_%s' % (vor, regler)], params[name], '%s %s' % (vor, name))

    def test_werte_ausserhalb_des_bereichs_oder_kaputt_werden_zur_vorgabe(self):
        vorgaben = Engine2d3dKleidermeshoptionen.vorgaben()
        aus = Engine2d3dKleidermeshoptionen.pruefen({
            'ss_schritte': 99,             # Space: 1–50
            'ss_rescale': 1.5,             # Space: 0–1
            'form_fuehrung': 'viel',       # keine Zahl
            'tex_rescale_t': 7,            # Space: 1–6
            'seed_zufall': 'vielleicht',   # nur aus/an
            'unbekannt': 1,
        })
        for schluessel in ('ss_schritte', 'ss_rescale', 'form_fuehrung', 'tex_rescale_t', 'seed_zufall'):
            self.assertEqual(aus[schluessel], vorgaben[schluessel], schluessel)
        self.assertNotIn('unbekannt', aus)

    def test_gueltige_werte_bleiben_und_schritte_sind_ganze_zahlen(self):
        aus = Engine2d3dKleidermeshoptionen.pruefen({'ss_schritte': '20', 'tex_rescale': 0, 'seed_zufall': 'an', 'seed': 5})
        self.assertEqual(aus['ss_schritte'], 20)
        self.assertIsInstance(aus['ss_schritte'], int)
        self.assertEqual((aus['tex_rescale'], aus['seed_zufall'], aus['seed']), (0, 'an', 5))

    def test_die_gruppe_ist_im_katalog_der_seite_mit_der_ueberschrift_des_zugeklappten_bereichs(self):
        katalog = Engine2d3dKleideroptionen.katalog()
        self.assertEqual(katalog['mesh']['fein_titel'], Engine2d3dKleidermeshoptionen.FEIN_TITEL)
        felder = katalog['mesh']['optionen']
        self.assertEqual(len(felder), 17)
        # Fünf Hauptfelder sichtbar, die zwölf Sampler im zugeklappten Bereich („Advanced Settings").
        self.assertEqual([f['schluessel'] for f in felder if not f['fein']],
                         ['aufloesung', 'seed', 'seed_zufall', 'flaechen', 'texturgroesse'])
        self.assertEqual(sum(1 for f in felder if f['fein']), 12)

    def test_ein_neuer_auftrag_hat_100000_flaechen_und_texturgroesse_4096(self):
        mesh = Engine2d3dKleideroptionen.pruefen({})['mesh']
        self.assertEqual((mesh['flaechen'], mesh['texturgroesse'], mesh['aufloesung']), (100000, '4096', 'hoch'))

    def test_was_bis_02_10_2026_unter_netz_gespeichert_war_bleibt_gueltig(self):
        """Auflösung, Flächen und Texturgröße zogen von der Gruppe `netz` in die Gruppe `mesh` um — ein gespeicherter Auftrag
        behält seine Werte (`Engine2d3dKleideroptionen.UEBERNAHME`), ein eigener Wert der Gruppe `mesh` geht vor."""
        roh = {'netz': {'aufloesung': 'mittel', 'flaechen': '500000', 'texturgroesse': '2048'}}
        mesh = Engine2d3dKleideroptionen.pruefen(roh)['mesh']
        self.assertEqual((mesh['aufloesung'], mesh['flaechen'], mesh['texturgroesse']), ('mittel', 500000, '2048'))
        roh['mesh'] = {'flaechen': 300000}
        self.assertEqual(Engine2d3dKleideroptionen.pruefen(roh)['mesh']['flaechen'], 300000)
        # Ein Wert, den die Gruppe `mesh` nicht kennt (Octree 768 gibt es nur bei Hunyuan3D), wird zur Vorgabe.
        self.assertEqual(Engine2d3dKleideroptionen.pruefen({'netz': {'aufloesung': 'sehr_hoch'}})['mesh']['aufloesung'], 'hoch')

    def test_die_seite_speichert_jede_gruppe(self):
        """Die Formulare von „netz", „mesh" und „koerper" wurden bis 02.10.2026 gebaut, aber nie gespeichert — eine
        Gruppe, die in `GRUPPEN` (Python) steht, muss auch in `Engine2d3dKleidereinstellungen.GRUPPEN` (JS) stehen."""
        pfad = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'engine2d3dkleider' / 'engine2d3dkleidereinstellungen.js'
        block = re.search(r'static GRUPPEN = \{(.*?)\};', pfad.read_text(encoding='utf-8'), re.S).group(1)
        for gruppe in Engine2d3dKleideroptionen.GRUPPEN:
            self.assertRegex(block, r"\b%s: 'engine2d3dkleider-optionen-%s'" % (gruppe, gruppe))


class NurTrellisTest(OhneDienste):
    def test_ein_gespeichertes_hunyuan_wird_beim_lesen_zu_trellis(self):
        netz = Engine2d3dKleideroptionen.pruefen(
            {'netz': {'formmodell': 'hunyuan3d_2mv', 'textur': 'malerei'}}
        )['netz']
        self.assertEqual((netz['formmodell'], netz['textur']), ('trellis2', 'fotos_ki'))

    def test_erlaubte_werte_bleiben(self):
        netz = Engine2d3dKleideroptionen.pruefen({'netz': {'textur': 'ki'}})['netz']
        self.assertEqual(netz['textur'], 'ki')

    def test_das_formular_zeigt_kein_formmodell_und_nennt_hunyuan_nirgends(self):
        katalog = Engine2d3dKleideroptionen.katalog()
        netz = {f['schluessel']: f for f in katalog['netz']['optionen']}
        self.assertEqual(list(netz), ['textur', 'freistellen', 'licht'])
        self.assertEqual([w['wert'] for w in netz['textur']['werte']], ['fotos_ki', 'fotos', 'ki', 'keine'])
        mesh = {f['schluessel']: f for f in katalog['mesh']['optionen']}
        self.assertEqual([w['wert'] for w in mesh['aufloesung']['werte']], ['schnell', 'mittel', 'hoch'])
        self.assertNotIn('hunyuan', json.dumps([katalog['netz'], katalog['mesh']], ensure_ascii=False).lower())


class TrellisreglerTest(SimpleTestCase):
    def test_die_katalogvorgaben_ergeben_die_sampler_der_pipeline_json(self):
        stufen = Trellisregler.sampler(Engine2d3dKleidermeshoptionen.vorgaben())
        self.assertEqual(stufen[0], {'steps': 12, 'guidance_strength': 7.5, 'guidance_rescale': 0.7, 'rescale_t': 5.0})
        self.assertEqual(stufen[1], {'steps': 12, 'guidance_strength': 7.5, 'guidance_rescale': 0.5, 'rescale_t': 3.0})
        self.assertEqual(stufen[2], {'steps': 12, 'guidance_strength': 1.0, 'guidance_rescale': 0.0, 'rescale_t': 3.0})

    def test_auftraege_der_seite_mesh_behalten_das_alte_paar_fuer_stage_1_und_2(self):
        stufen = Trellisregler.sampler({'schritte': 20, 'fuehrung': 8.5})
        self.assertEqual(stufen, [{'steps': 20, 'guidance_strength': 8.5}, {'steps': 20, 'guidance_strength': 8.5}, {}])

    def test_guidance_rescale_null_ist_ein_wert_kein_fehlt(self):
        self.assertEqual(Trellisregler.sampler({'ss_rescale': 0.0})[0], {'guidance_rescale': 0.0})

    def test_die_neuen_regler_gehen_dem_alten_paar_vor(self):
        stufen = Trellisregler.sampler({'schritte': 20, 'ss_schritte': 30})
        self.assertEqual((stufen[0]['steps'], stufen[1]['steps']), (30, 20))

    def test_der_zufallsseed_wird_gewuerfelt_gemeldet_und_der_feste_bleibt(self):
        with redirect_stdout(io.StringIO()) as ausgabe:
            fest = Trellisregler.seed({'seed': 7})
            wuerfel = Trellisregler.seed({'seed': 7, 'seed_zufall': 'an'})
        self.assertEqual(fest, 7)
        self.assertTrue(0 <= wuerfel < 2 ** 31)
        self.assertEqual(ausgabe.getvalue().splitlines(), ['[seed] 7', '[seed] %d' % wuerfel])
