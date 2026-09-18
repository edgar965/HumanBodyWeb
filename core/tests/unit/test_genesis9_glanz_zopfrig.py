# -*- coding: utf-8 -*-
"""Genesis 9, die Nachzuegler vom 18.09.2026 („noch was offen? … fixe alle
offenen Punkte"): Klarlack und Metall der Schminke (`G9glanz`), LIE-Grund-
ebenen und `invert` (`G9ebenen`), DirectX-Normalen (`G9browserbilder`),
HD-Morphs der Anhaenge (`G9anhangmorphe.hd`), eigene Knochen fuers Browser-
Skelett (`G9eigenknochen.gelenke` — in `test_genesis9_hd_props_eigenknochen`).

Abends dazu (Edgar: „Makeup-Reste: Mach"): die Blendmodi des LIE nach
W3C/Qt (`G9blendmodi`), Daz' zwei Makeup-Stapel (`G9makeupstapel`: die
Grundierung ist der Untergrund des Rouges), Glitzer-Normalen und Top Coat
Color/Bump als `werte` (`G9glanz`).

Sabotage-Gegenproben: `G9glanz.mit_glanz` -> False laesst Fall 2 und 4 rot
werden; `G9ebenen.GRUND = ()` Fall 3; `G9browserbilder.DIRECTX` auf ein
Muster ohne Treffer Fall 5; `_soft_light` durch `_multiply` ersetzt Fall 7;
`G9makeupstapel.rechnen` mit `farbe = Image.new(...)` je Ebene (kein Stapel)
Fall 8.
"""

import os
import tempfile
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.anhangmorphe import G9anhangmorphe
from Genesis9.blendmodi import G9blendmodi
from Genesis9.browserbilder import G9browserbilder
from Genesis9.dson import G9dson
from Genesis9.ebenen import G9ebenen
from Genesis9.glanz import G9glanz
from Genesis9.makeupstapel import G9makeupstapel
from Genesis9.pfade import G9pfade
from Genesis9.schminke import G9schminke
from PIL import Image


def _bild(farbe, alpha, groesse=(4, 4)):
    return Image.new('RGBA', groesse, farbe + (alpha,))


KANAL = 'name://@selection#materials/Head:?extra/studio_material_channels/channels/'


def _glossy_doc():
    """Amelias `MU 01 Lips-Glossy`: ZWEI leere Grundebenen, dann die
    Lippenmaske mit Deckkraft 0,35; Top Coat an, Rauheit 0."""
    return G9dson(
        'g.duf',
        {
            'image_library': [
                {
                    'id': 'TC 1',
                    'map': [
                        {'label': 'Blank', 'color': [0, 0, 0], 'transparency': 1},
                        {'label': 'Background', 'color': [0, 0, 0], 'transparency': 1},
                        {
                            'url': '/Runtime/Textures/x/Lips_MW.png',
                            'label': 'Lips',
                            'transparency': 0.35,
                            'operation': 'blend_source_over',
                        },
                    ],
                },
                {
                    'id': 'M 7',
                    'map': [
                        {'label': 'Background', 'color': [0, 0, 0], 'transparency': 1},
                        {'url': '/Runtime/Textures/x/E_M.png', 'transparency': 1},
                    ],
                },
                {
                    'id': 'R 2',
                    'map': [
                        {'label': 'Background', 'color': [0, 0, 0], 'transparency': 1},
                        {'url': '/Runtime/Textures/x/E_R.png', 'transparency': 1, 'invert': True},
                    ],
                },
            ],
            'scene': {
                'animations': [
                    {'url': KANAL + 'Top%20Coat%20Enable/value', 'keys': [[0, True]]},
                    {'url': KANAL + 'Top%20Coat%20Weight/image', 'keys': [[0, '#TC%201']]},
                    {'url': KANAL + 'Top%20Coat%20Roughness/value', 'keys': [[0, 0]]},
                ]
            },
        },
    )


class Genesis9Glanz(SimpleTestCase):
    databases = set()

    def test_1_glanzbild_r_klarlack_g_rauheit_b_metall(self):
        bilder = {'k': _bild((255, 255, 255), 255), 'm': _bild((255, 255, 255), 128)}
        aus = G9glanz.rechnen(
            [
                {'klarlack': 'k', 'klarlackdeckkraft': 0.35, 'klarlackrauheit': 0.2},
                {'metall': 'm', 'metalldeckkraft': 1.0},
            ],
            (4, 4),
            lambda p: bilder[p],
        )
        r, g, b = aus.getpixel((0, 0))
        self.assertEqual((r, g, b), (89, 51, 128))  # 255·0,35 · 0,2 · Alpha 128

    def test_2_lips_glossy_wird_eine_glanzebene(self):
        ebenen = G9schminke._ebenen_aus_preset(_glossy_doc())
        self.assertEqual(
            ebenen,
            [
                {
                    'gruppe': 'Head',
                    'ueber_schwarz': True,
                    'klarlack': '/Runtime/Textures/x/Lips_MW.png',
                    'klarlackdeckkraft': 0.35,
                    'klarlackrauheit': 0.0,
                }
            ],
        )
        self.assertEqual(G9schminke.kategorie_von('Amelia 9 MU 01 Lips-Glossy'), 'lipgloss')
        # Metallic Weight und eine invertierte Rauheitskarte am Lidschatten.
        doc = _glossy_doc()
        doc.daten['scene']['animations'] = [
            {'url': KANAL + 'Makeup%20Weight/image', 'keys': [[0, '#M%207']]},
            {'url': KANAL + 'Makeup%20Base%20Color/image', 'keys': [[0, '#M%207']]},
            {'url': KANAL + 'Metallic%20Weight/image', 'keys': [[0, '#M%207']]},
            {'url': KANAL + 'Specular%20Lobe%201%20Roughness/image', 'keys': [[0, '#R%202']]},
        ]
        ebene = G9schminke._ebenen_aus_preset(doc)[0]
        self.assertEqual(ebene['metall'], '/Runtime/Textures/x/E_M.png')
        self.assertEqual(ebene['metalldeckkraft'], 1.0)
        self.assertTrue(ebene['rauheitinvers'])
        self.assertNotIn('klarlack', ebene)

    def test_3_lie_ueberspringt_grundebenen_und_meldet_invert(self):
        lagen = G9ebenen.lie(_glossy_doc(), 'TC 1')
        self.assertEqual(
            [(e['url'], e['deckkraft'], e['invers']) for e in lagen],
            [('/Runtime/Textures/x/Lips_MW.png', 0.35, False)],
        )
        self.assertTrue(G9ebenen.lie(_glossy_doc(), 'R 2')[0]['invers'])
        # Invertiert gelegt: Ersatzwert 255 − 51.
        bilder = {'rot': _bild((255, 0, 0), 255), 'r': _bild((51, 51, 51), 255)}
        with mock.patch.object(G9ebenen, '_oeffnen', side_effect=lambda p: bilder[p]):
            aus = G9ebenen._rechnen(
                [{'farbe': 'rot', 'deckkraft': 1, 'rauheit': 'r', 'rauheitinvers': True}], True
            )
        self.assertEqual(aus['rauheit'].getpixel((0, 0)), (255, 204, 255))

    def test_4_komponieren_nur_glanz_als_png(self):
        bilder = {'k': _bild((255, 255, 255), 255)}
        oeffnen = mock.patch.object(G9ebenen, '_oeffnen', side_effect=lambda p: bilder[p])
        with (
            tempfile.TemporaryDirectory() as ordner,
            oeffnen,
            mock.patch.object(G9pfade, 'ablage', return_value=_Pfad(ordner)),
        ):
            aus = G9ebenen.komponieren(
                [{'gruppe': 'Head', 'klarlack': 'k', 'klarlackdeckkraft': 1.0, 'klarlackrauheit': 0.0}]
            )
            self.assertEqual(sorted(aus), ['glanz'])
            self.assertTrue(aus['glanz'].endswith('_k.png'))
            datei = os.path.join(ordner, 'schminke', aus['glanz'].split('/')[1])
            self.assertEqual(Image.open(datei).getpixel((0, 0)), (255, 0, 0))

    def test_5_directx_normalen_kehren_die_y_achse(self):
        with mock.patch.object(G9browserbilder, 'tragbar', return_value=True):
            aus = G9browserbilder.fuer(
                {'albedo': 'x/Dagger_MAT_D.png', 'normalen': 'x/Dagger_MAT_Normal_DirectX.png'}, hoch=False
            )
            self.assertEqual(aus['normalenachse'], -1)
            aus = G9browserbilder.fuer({'normalen': 'x/G9_Head_NM_1001.jpg'}, hoch=False)
            self.assertNotIn('normalenachse', aus)

    def test_6_anhangmorphe_kennen_ihre_hd_morphs(self):
        with tempfile.TemporaryDirectory() as ordner:
            morphs = os.path.join(ordner, 'Morphs')
            os.makedirs(morphs)
            G9dsonSchreiber.schreiben(
                os.path.join(morphs, 'HD Wrinkles.dsf'),
                {
                    'modifier_library': [
                        {
                            'id': 'HD Wrinkles',
                            'name': 'HD Wrinkles',
                            'channel': {'label': 'HD Wrinkles', 'visible': False},
                            'morph': {
                                'hd_url': '/x/HD%20Wrinkles.dhdm',
                                'deltas': {'values': [[0, 0, 1, 0]]},
                            },
                        }
                    ]
                },
            )
            morphe = G9anhangmorphe._lesen(morphs)
            deltas, _steckbriefe, hd = morphe
            self.assertEqual(hd, {'HD Wrinkles': '/x/HD Wrinkles.dhdm'})
            self.assertIn('HD Wrinkles', deltas)
            eigen = G9anhangmorphe(deltas, {}, hd)
            with mock.patch.object(G9pfade, 'bibliothek', return_value=_Pfad(ordner)):
                # Die .dhdm fehlt: kein aktiver Kanal.
                self.assertEqual(eigen.hd_aktive({'HD Wrinkles': 1.0}), {})
                with open(os.path.join(ordner, 'x'), 'w'):
                    pass
            self.assertEqual(eigen.hd_aktive({'HD Wrinkles': 0.0}), {})

    def test_7_blendmodi_nach_w3c(self):
        """Je Kanal `Co = Cb·(1−a) + B(Cb, Cs)·a`; Plus = min(1, Cb + Cs·a).
        Untergrund (0,2, 0,6, 0,8), Ebene 0,6 — von Hand gerechnet, ±1."""
        grund = Image.new('RGB', (2, 2), (51, 153, 204))
        ebene = _bild((153, 153, 153), 255, (2, 2))
        faelle = {
            'blend_multiply': (31, 92, 122),
            'blend_screen': (173, 214, 235),
            'blend_overlay': (61, 173, 214),
            'blend_color_burn': (0, 85, 170),
            'blend_plus': (204, 255, 255),
        }
        for modus, soll in faelle.items():
            with self.subTest(modus):
                self._nah(G9blendmodi.legen(grund, ebene, modus), soll)
        # Soft Light mit 50 % Grau laesst den Untergrund stehen.
        self._nah(
            G9blendmodi.legen(grund, _bild((128, 128, 128), 255, (2, 2)), 'blend_soft_light'), (51, 153, 204)
        )
        # Alpha × Deckkraft: Multiply zur Haelfte -> Mitte von Untergrund und Produkt.
        self._nah(G9blendmodi.legen(grund, ebene, 'blend_multiply', 0.5), (41, 122, 163))
        self.assertTrue(G9blendmodi.bekannt('blend_exclusion'))
        self.assertFalse(G9blendmodi.bekannt('blend_quatsch'))

    def _nah(self, bild, soll, stelle=(0, 0)):
        ist = bild.getpixel(stelle)
        ist = ist if isinstance(ist, tuple) else (ist,)
        for a, b in zip(ist, soll):
            self.assertLessEqual(abs(a - b), 1, '%s statt %s' % (ist, soll))

    def test_8_makeupstapel_grundierung_ist_der_untergrund_des_rouges(self):
        """Grundierung (Plus ueber Schwarz = das Bild, Maske 0,4) und darueber
        ein Rouge mit `soft_light` (50 % Grau: Farbe bleibt die Grundierung)
        und Maske 0,45: Gewicht 0,4 + 0,45·0,6 = 0,67 -> 171."""
        bilder = {
            'F': _bild((200, 150, 120), 255),
            'WF': _bild((255, 255, 255), 255),
            'R': _bild((128, 128, 128), 255),
            'WR': _bild((255, 255, 255), 255),
        }
        farbe, gewicht = G9makeupstapel.rechnen(
            [
                {'farbe': 'F', 'farbmodus': 'blend_plus', 'maske': 'WF', 'deckkraft': 0.4},
                {'farbe': 'R', 'farbmodus': 'blend_soft_light', 'maske': 'WR', 'deckkraft': 0.45},
            ],
            (4, 4),
            lambda p: bilder[p],
        )
        self._nah(farbe, (200, 150, 120))
        self._nah(gewicht, (171,))
        # Ohne Grundierung rechnet Daz ueber Schwarz: Multiply -> Schwarz.
        farbe, _gewicht = G9makeupstapel.rechnen(
            [{'farbe': 'F', 'farbmodus': 'blend_multiply', 'maske': 'WF', 'deckkraft': 1.0}],
            (4, 4),
            lambda p: bilder[p],
        )
        self.assertEqual(farbe.getpixel((0, 0)), (0, 0, 0))

    def test_9_glitzer_normalen_und_klarlackwerte(self):
        doc = _glossy_doc()
        doc.daten['image_library'].append(
            {
                'id': 'NM 3',
                'map': [
                    {'label': 'Background', 'color': [0, 0, 0], 'transparency': 1},
                    {'url': '/Runtime/Textures/x/E_NM.png', 'transparency': 1, 'operation': 'blend_overlay'},
                ],
            }
        )
        doc.daten['scene']['animations'] += [
            {'url': KANAL + 'Normal%20Map/image', 'keys': [[0, '#NM%203']]},
            {'url': KANAL + 'Top%20Coat%20Color/value', 'keys': [[0, [0.95, 0.77, 0.67]]]},
            {'url': KANAL + 'Top%20Coat%20Bump%20Weight/value', 'keys': [[0, 0.15]]},
        ]
        ebene = G9schminke._ebenen_aus_preset(doc)[0]
        self.assertEqual(ebene['normalen'], '/Runtime/Textures/x/E_NM.png')
        self.assertEqual(ebene['normalenmodus'], 'blend_overlay')
        self.assertEqual(
            G9glanz.werte([ebene]),
            {'klarlackfarbe': [0.95, 0.77, 0.67], 'klarlackbump': 0.15, 'normalenmodus': 'overlay'},
        )
        bilder = {'n': _bild((100, 140, 250), 200)}
        aus = G9glanz.normalen([{'normalen': 'n', 'normalendeckkraft': 0.5}], (4, 4), lambda p: bilder[p])
        self.assertEqual(aus.getpixel((0, 0)), (100, 140, 250, 100))
        # Weiss ist keine Klarlackfarbe (Vorgabe von Three).
        self.assertEqual(G9glanz.werte([{'klarlack': 'k', 'klarlackfarbe': [1, 1, 1]}]), {})


class _Pfad(str):
    """Ein `Path`-Ersatz, der `/` kann und `is_file` versteht."""

    def __truediv__(self, rest):
        return _Pfad(os.path.join(self, str(rest)))

    def is_file(self):
        return os.path.isfile(self)

    def mkdir(self, parents=False, exist_ok=False):
        os.makedirs(self, exist_ok=exist_ok)


class G9dsonSchreiber:
    @staticmethod
    def schreiben(pfad, daten):
        import json

        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f)
