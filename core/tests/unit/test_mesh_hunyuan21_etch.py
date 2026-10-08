# -*- coding: utf-8 -*-
"""Mesh: Hunyuan3D-2.1-Malerei (`textur = malerei21`) und ETCH-X als Entkleider (`Etchentkleider`), 07.10.2026.

Edgar: „mach 1 bis 4" (Prüfung von Hilfe → Architektur → Andere Modelle). Ohne Modelle und ohne GPU: nur das, was sich ohne `python10_h21`/`python10_etch`
prüfen lässt — Katalog, Durchreichen, Verdrahtung. Die Prozesse selbst laufen in den eigenen Umgebungen (`.claude/rules/mesh-hunyuan21.md`).
Sabotage-Gegenprobe: in `_run_mesh.py` die Zeile `form = malen_21(` entfernen → `test_runner_ruft_die_21_malerei` muss rot werden.
"""

import unittest

from core.dienste.meshoptionen import Meshoptionen

from ._wrappersuchpfad import WRAPPERS, Wrappersuchpfad

Wrappersuchpfad.setzen()


class MalereiKatalogTest(unittest.TestCase):
    def test_textur_kennt_malerei21(self):
        eintrag = next(e for e in Meshoptionen.KATALOG if e['schluessel'] == 'textur')
        self.assertIn('malerei21', [wert for wert, _ in eintrag['werte']])
        self.assertEqual(Meshoptionen.pruefen({'textur': 'malerei21'})['textur'], 'malerei21')

    def test_ansichten_sind_geklemmt(self):
        self.assertEqual(Meshoptionen.pruefen({'malansichten21': 3})['malansichten21'], 6)
        self.assertEqual(Meshoptionen.pruefen({'malansichten21': 12})['malansichten21'], 9)
        self.assertEqual(Meshoptionen.pruefen({})['malansichten21'], 6)

    def test_alte_wahl_bleibt_vorgabe(self):
        self.assertEqual(Meshoptionen.pruefen({})['textur'], 'fotos_ki')


class MalereiRunnerTest(unittest.TestCase):
    def test_ohne_wahl_bleibt_die_form_unberuehrt(self):
        from mesh_hunyuan21 import malen_21

        form = {'objekt': 'trellis2', 'vertices': [], 'faces': [], 'texturiertes_mesh': None}
        self.assertIs(malen_21({'textur': 'malerei'}, form, [], '.'), form)
        self.assertIs(malen_21({'textur': 'fotos_ki'}, form, [], '.'), form)

    def test_gemalte_form_wird_nicht_ueberschrieben(self):
        from mesh_hunyuan21 import malen_21

        form = {'objekt': 'hunyuan', 'vertices': [], 'faces': [], 'texturiertes_mesh': object()}
        self.assertIs(malen_21({'textur': 'malerei21'}, form, [], '.'), form)

    def test_runner_ruft_die_21_malerei(self):
        quelle = (WRAPPERS / '_run_mesh.py').read_text(encoding='utf-8')
        self.assertIn('form = malen_21(', quelle)
        self.assertLess(quelle.index('form = malen_21('), quelle.index('form_cachen(self.ordner, form)'))

    def test_export_benennt_die_textur_quelle(self):
        quelle = (WRAPPERS / 'mesh_export.py').read_text(encoding='utf-8')
        self.assertIn("textur_quelle = form['textur_art']", quelle)

    def test_prozess_baut_kein_bpy_und_kein_basicsr_ein(self):
        quelle = (WRAPPERS / '_run_hunyuan21_paint.py').read_text(encoding='utf-8')
        self.assertIn("sys.modules.setdefault('bpy'", quelle)
        self.assertNotIn('import basicsr', quelle)
        self.assertNotIn('from realesrgan', quelle)
        self.assertIn('use_remesh=False', quelle)


class EntkleiderTest(unittest.TestCase):
    def test_unbekannte_variante_wird_abgelehnt(self):
        from etch_entkleider import Etchentkleider

        with self.assertRaises(ValueError):
            Etchentkleider.entkleiden('gibt-es-nicht.glb', '.', variante='4d-dressed')

    def test_vorgabe_ist_cape_nicht_4d_dress(self):
        """Gemessen: `4d-dress` versagt auf Genesis-Körpern (Rumpf immer ~22 mm zu tief) — die Vorgabe darf es nicht sein."""
        import inspect

        from etch_entkleider import Etchentkleider

        vorgabe = inspect.signature(Etchentkleider.entkleiden).parameters['variante'].default
        self.assertEqual(vorgabe, 'cape')


if __name__ == '__main__':
    unittest.main()
