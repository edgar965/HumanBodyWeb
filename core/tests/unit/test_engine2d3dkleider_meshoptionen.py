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

from mesh_trellismehrbild import Trellismehrbild  # noqa: E402  (erst nach dem Suchpfad)
from mesh_trellisregler import Trellisregler  # noqa: E402

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
        # Die Hauptfelder des Space in seiner Reihenfolge (Resolution, Seed, Randomize Seed, Decimation Target, Texture Size) mit
        # der Modellwahl davor, dahinter Multi-Image (Fork des Space) und die Felder von Pixal3D.
        rest = ['modell', 'aufloesung', 'seed', 'seed_zufall', 'flaechen', 'texturgroesse', 'mehrbild', 'mehrbild_textur',
                'pixal_fov', 'pixal_speicher', 'pixal_seite', 'pixal_formseite', 'pixal_abstand', 'pixal_remesh', 'fotopruefung']
        self.assertEqual([k for k in vorgaben if k not in erwartet], rest)
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
        self.assertEqual(len(felder), 27)
        # Sechs Hauptfelder sichtbar (Modell + die fünf des Space), die zwölf Sampler, die beiden Multi-Image-Felder, die fünf
        # von Pixal3D (Sichtfeld, Grafikspeicher, Rolle der Seitenfotos, Seitenfotos für die Form, Kameraabstand) und die Fotoprüfung
        # im zugeklappten Bereich („Advanced Settings").
        self.assertEqual([f['schluessel'] for f in felder if not f['fein']],
                         ['modell', 'aufloesung', 'seed', 'seed_zufall', 'flaechen', 'texturgroesse'])
        self.assertEqual(sum(1 for f in felder if f['fein']), 21)
        self.assertEqual(katalog['mesh']['gilt_nach'], 'modell')

    def test_die_felder_wechseln_mit_dem_modell(self):
        """TRELLIS.2 und Pixal3D haben verschiedene Regler: `gilt` sagt je Feld, zu welchem Modell es gehört; ohne `gilt`
        gilt es für alle (Auflösung, Seed, Flächen, Texturgröße). Das Formular blendet die übrigen aus (`_gilt`)."""
        felder = {f['schluessel']: f for f in Engine2d3dKleideroptionen.katalog()['mesh']['optionen']}
        for schluessel in ('modell', 'aufloesung', 'seed', 'seed_zufall', 'flaechen', 'texturgroesse'):
            self.assertNotIn('gilt', felder[schluessel], schluessel)
        trellis = [k for k in felder if k.split('_')[0] in ('ss', 'form', 'tex') or k.startswith('mehrbild')]
        self.assertEqual(len(trellis), 14)
        for schluessel in trellis:
            self.assertEqual(felder[schluessel]['gilt'], ['trellis2'], schluessel)
        for schluessel in ('pixal_fov', 'pixal_speicher', 'pixal_seite', 'pixal_formseite', 'pixal_abstand', 'pixal_remesh'):
            self.assertEqual(felder[schluessel]['gilt'], ['pixal3d', 'pixal3d_mv'], schluessel)
        self.assertNotIn('gilt', felder['fotopruefung'])  # gilt für jedes Modell

    def test_das_modell_ist_trellis2_pixal3d_hunyuan3d_und_sonst_die_vorgabe(self):
        felder = {f['schluessel']: f for f in Engine2d3dKleideroptionen.katalog()['mesh']['optionen']}
        self.assertEqual([w['wert'] for w in felder['modell']['werte']],
                         ['trellis2', 'pixal3d', 'pixal3d_mv', 'hunyuan3d_2', 'hunyuan3d_2mv'])
        # Hunyuan3D ist seit 07.10.2026 wählbar (Edgar: „Job mit der Hunyan Pipeline") und bleibt gespeichert.
        hunyuan = Engine2d3dKleideroptionen.pruefen({'mesh': {'modell': 'hunyuan3d_2mv'}})['mesh']
        self.assertEqual(hunyuan['modell'], 'hunyuan3d_2mv')
        self.assertEqual(Engine2d3dKleidermeshoptionen.vorgaben()['modell'], 'trellis2')
        gewaehlt = Engine2d3dKleideroptionen.pruefen({'mesh': {'modell': 'pixal3d_mv', 'pixal_fov': 0.2,
                                                               'pixal_speicher': 'sparsam'}})['mesh']
        self.assertEqual((gewaehlt['modell'], gewaehlt['pixal_fov'], gewaehlt['pixal_speicher']), ('pixal3d_mv', 0.2, 'sparsam'))
        kaputt = Engine2d3dKleideroptionen.pruefen({'mesh': {'modell': 'quatsch', 'pixal_fov': 5,
                                                             'pixal_speicher': 'alles'}})['mesh']
        self.assertEqual((kaputt['modell'], kaputt['pixal_fov'], kaputt['pixal_speicher']), ('trellis2', 0, 'auto'))

    def test_das_formular_blendet_nach_dem_modell_aus_und_liest_trotzdem_alles(self):
        pfad = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'mesh' / 'meshoptionenformular.js'
        text = pfad.read_text(encoding='utf-8')
        self.assertIn('static _gilt(behaelter, gilt_nach)', text)
        self.assertIn("zeile.dataset.gilt = feld.gilt.join(' ')", text)
        self.assertIn("toggle('hb-versteckt'", text)
        # `lesen` fragt ALLE Felder ab, ausgeblendete eingeschlossen — beim Wechsel des Modells gehen keine Werte verloren.
        self.assertNotIn('hb-versteckt', text.split('static lesen(behaelter)')[1])

    def test_multi_image_ist_aus_und_ein_unbekannter_wert_wird_aus(self):
        vorgaben = Engine2d3dKleidermeshoptionen.vorgaben()
        self.assertEqual((vorgaben['mehrbild'], vorgaben['mehrbild_textur']), ('aus', 'multidiffusion'))
        gueltig = Engine2d3dKleideroptionen.pruefen({'mesh': {'mehrbild': 'stochastic', 'mehrbild_textur': 'stochastic'}})['mesh']
        self.assertEqual((gueltig['mehrbild'], gueltig['mehrbild_textur']), ('stochastic', 'stochastic'))
        kaputt = Engine2d3dKleideroptionen.pruefen({'mesh': {'mehrbild': 'quatsch', 'mehrbild_textur': 'aus'}})['mesh']
        # „aus" gibt es nur für die Form; die Textur kennt stochastic und multidiffusion.
        self.assertEqual((kaputt['mehrbild'], kaputt['mehrbild_textur']), ('aus', 'multidiffusion'))

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
        """Die Formulare von „netz", „mesh" und „koerper" wurden bis 02.10.2026 gebaut, aber nie gespeichert. Seit 04.10.2026 liest
        `Engine2d3dKleidereinstellungen.GRUPPEN` (JS) die Behälter `engine2d3dkleider-optionen-<gruppe>` aus der Seite — eine Gruppe, die in
        `GRUPPEN` (Python) steht, braucht also ihren Behälter in der Vorlage, sonst wird sie nie gespeichert."""
        js = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'engine2d3dkleider' / 'engine2d3dkleidereinstellungen.js'
        self.assertIn('engine2d3dkleider-optionen-', js.read_text(encoding='utf-8'))
        vorlagen = Path(settings.BASE_DIR) / 'templates'
        seite = '\n'.join((vorlagen / name).read_text(encoding='utf-8') for name in ('engine2d3dkleider_auftrag.html', '_engine2d3dkleider_kopf.html'))
        for gruppe in Engine2d3dKleideroptionen.GRUPPEN:
            self.assertRegex(seite, r'id="engine2d3dkleider-optionen-%s"' % gruppe)


class NurTrellisTest(OhneDienste):
    def test_ein_gespeichertes_hunyuan_wird_beim_lesen_zu_trellis(self):
        netz = Engine2d3dKleideroptionen.pruefen(
            {'netz': {'formmodell': 'hunyuan3d_2mv', 'textur': 'malerei'}}
        )['netz']
        self.assertEqual((netz['formmodell'], netz['textur']), ('trellis2', 'fotos_ki'))

    def test_erlaubte_werte_bleiben(self):
        netz = Engine2d3dKleideroptionen.pruefen({'netz': {'textur': 'ki'}})['netz']
        self.assertEqual(netz['textur'], 'ki')

    def test_das_formular_zeigt_kein_formmodell_und_hunyuan_steht_nur_in_der_wahl_modell(self):
        katalog = Engine2d3dKleideroptionen.katalog()
        netz = {f['schluessel']: f for f in katalog['netz']['optionen']}
        self.assertEqual(sorted(netz), ['freistellen', 'licht', 'textur'])                  # kein `formmodell`; die Reihenfolge ist die von `Meshoptionen`, nicht Teil der Zusage
        self.assertEqual([w['wert'] for w in netz['textur']['werte']], ['fotos_ki', 'fotos', 'ki', 'keine'])
        mesh = {f['schluessel']: f for f in katalog['mesh']['optionen']}
        self.assertEqual([w['wert'] for w in mesh['aufloesung']['werte']], ['schnell', 'mittel', 'hoch'])
        # Hunyuan3D nennt nur noch die Wahl „Modell" der Gruppe `mesh` (07.10.2026); die Gruppe `netz` und alle anderen Felder nicht.
        self.assertNotIn('hunyuan', json.dumps(katalog['netz'], ensure_ascii=False).lower())
        uebrige = [f for f in katalog['mesh']['optionen'] if f['schluessel'] != 'modell']
        self.assertNotIn('hunyuan', json.dumps(uebrige, ensure_ascii=False).lower())


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


class TrellismehrbildTest(SimpleTestCase):
    """Die Auswahl der Fotos und der Modi (`mesh_trellismehrbild`). Das Verhalten der Sampler braucht torch und den Klon —
    dafür gibt es `ProjektTemp/_wegwerf/trellis_hf/mehrbild_probe.py` (CPU, Kunsttensoren, 14 Prüfungen)."""

    BILDER = [{'rolle': r, 'gewicht': g, 'freigestellt': r} for r, g in (
        ('hinten', 100), ('gesicht', 100), ('vorne', 100), ('rechts', 0), ('links', 40))]

    def test_aus_ist_die_vorgabe_und_gibt_keine_ansichten(self):
        self.assertEqual(Trellismehrbild.modi(Engine2d3dKleidermeshoptionen.vorgaben()), (None, None))
        self.assertEqual(Trellismehrbild.ansichten(Engine2d3dKleidermeshoptionen.vorgaben(), self.BILDER), [])

    def test_die_ansichten_kommen_in_der_reihenfolge_vorne_hinten_links_rechts(self):
        optionen = {'mehrbild': 'multidiffusion'}
        rollen = [b['rolle'] for b in Trellismehrbild.ansichten(optionen, self.BILDER)]
        # „gesicht" ist keine Ansicht des ganzen Körpers, Gewicht 0 schaltet ein Foto ab.
        self.assertEqual(rollen, ['vorne', 'hinten', 'links'])

    def test_eine_einzige_ansicht_bleibt_beim_einzelbild(self):
        self.assertEqual(Trellismehrbild.ansichten({'mehrbild': 'stochastic'}, self.BILDER[2:3]), [])

    def test_die_modi_und_die_vorgabe_der_textur(self):
        self.assertEqual(Trellismehrbild.modi({'mehrbild': 'stochastic'}), ('stochastic', 'multidiffusion'))
        self.assertEqual(Trellismehrbild.modi({'mehrbild': 'stochastic', 'mehrbild_textur': 'stochastic'}),
                         ('stochastic', 'stochastic'))
        self.assertEqual(Trellismehrbild.modi({'mehrbild': 'quatsch'}), (None, None))
