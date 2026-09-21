# -*- coding: utf-8 -*-
u"""Texturmischung (21.09.2026, Edgar: „«Textur» mit allen Texturen die du hast,
und Regler dazu in %") — ohne Bibliothek, ohne Browser.

1. Der Endpunkt liefert je Gruppe nur Albedo/Normalen/Rauheit und laesst
   Gruppen ohne Albedo weg (Sabotage: `ARTEN` um `detailnormalen` erweitern
   -> Fall 1 rot).
2. Das Feld `hautmischung` geht durch ALLE Schichten — Modell (JS), Figur-JSON,
   Server-Eintrag, UI (`artefakte-benennen.md`: ein neues Feld, das die
   Fassung waehlt, geht durch alle Schichten, mit einem Test, der die Deckung
   prueft). Sabotage: `hautmischung` aus `toJSON` streichen -> Fall 2 rot.
3. Die Uniform-Objekte der Mischung bleiben je Material dieselben und haengen
   IMMER am Shader — Three haelt je Programmschluessel die Uniforms des zuletzt
   kompilierten Programms fest (gemessen: nach 1 -> 0 -> 1 Schichten kam Rot mit
   Gewicht 1 nicht an). Sabotage: `mischungSchichten` je Aufruf neu anlegen
   -> Fall 3 rot.
"""
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse

from core.api.g9hautmischung import G9hautmischungapi


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class HautmischungTest(SimpleTestCase):
    databases = set()

    def test_1_endpunkt_nur_tragbare_bilder_je_gruppe(self):
        haut = {
            'Head': {'albedo': 'a/Head_D.jpg', 'normalen': 'a/Head_N.jpg',
                     'rauheit': 'a/Head_R.jpg', 'detailnormalen': 'a/8k.jpg',
                     'farbe': [1, 1, 1], 'durchlicht': {'gewicht': 0.85}},
            'EyeMoisture': {'rauheitwert': 0.05},
        }
        with mock.patch('core.api.g9hautmischung.G9hautpresets.haut', return_value=haut), \
                mock.patch('core.api.g9hautmischung.G9browserbilder.fuer', side_effect=lambda b: dict(b)):
            gruppen = G9hautmischungapi.gruppen('x:y')
        self.assertEqual(list(gruppen), ['Head'])
        self.assertEqual(gruppen['Head'], {'albedo': 'a/Head_D.jpg', 'normalen': 'a/Head_N.jpg',
                                           'rauheit': 'a/Head_R.jpg'})
        self.assertEqual(reverse('g9_figur_hautbilder', args=['x:y']),
                         '/api/character/genesis9-figur/haut/x:y/bilder/')

    def test_2_feld_hautmischung_in_allen_schichten(self):
        modell = quelltext('gemeinsam', 'genesis9modell.js')
        self.assertIn('this.hautmischung = { ...(daten.hautmischung || {}) };', modell)
        self.assertIn('eintrag.hautmischung', modell, 'gespeichertes Modell: Vorgabe uebernehmen')
        self.assertIn('Genesis9hautmischung.anwenden(this)', modell, 'nach jedem Koerperbau neu einhaengen')
        figur = quelltext('scene', 'genesis9', 'genesis9figur.js')
        self.assertIn('hautmischung: { ...this.hautmischung },', figur, 'Undo und Speichern')
        server = (Path(settings.BASE_DIR) / 'core' / 'api' / 'g9figur.py').read_text(encoding='utf-8')
        self.assertEqual(server.count("'hautmischung'"), 2, 'gespeicherte Liste UND Eintrag')
        ui = quelltext('scene', 'genesis9', 'genesis9texturmischung.js')
        self.assertIn('inst.hautmischungSetzen(satz.id, neu)', ui)
        vorlage = (Path(settings.BASE_DIR) / 'templates' / '_genesis9_eigenschaften.html').read_text(encoding='utf-8')
        self.assertIn('id="prop-genesis9-textur"', vorlage)
        self.assertTrue(vorlage.rstrip().endswith('</details>\n</div>'), 'der Bereich steht ganz unten')

    def test_3_uniforms_bleiben_und_haengen_immer(self):
        haut = quelltext('gemeinsam', 'genesis9haut.js')
        self.assertIn('zusatz.mischungSchichten = zusatz.mischungSchichten || [];', haut)
        self.assertIn('for (const s of zusatz.mischungSchichten || []) Object.assign(shader.uniforms, s);', haut)
        self.assertIn("-m${\n            zusatz.mischung?.anzahl || 0}", haut, 'die Zahl der Schichten im Programmschluessel')
        glsl = quelltext('gemeinsam', 'genesis9hautglsl.js')
        self.assertIn('static mischungFarbe(anzahl)', glsl)
        self.assertIn('static normalen(mitGlitzer, mitDetail, mischung = 0)', glsl)
