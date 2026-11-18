"""Daz-Stücke so laden, wie Daz sie lädt (17.11.2026, Edgar: „die Defaults nicht richtig gesetzt“,
„See-through-Kleid gar nicht durchsichtig“, „kein Icon für den Tab“) — an Kunst-Dokumenten, ohne Bibliothek
und ohne Karte.

1. `G9materialgrund.kanaele`: die Bibliothek der Datei unter der Szene — `Cutout Opacity` 0,7 nur in der
   Bibliothek kommt an, die Szene überschreibt Kanal für Kanal.
2. `G9materialgrund.werte`: nur Abweichungen von Daz' Vorgabe (Durchsicht 1 und Metall 0 gehen nicht mit).
3. Wiederholung: Material 4 und Bild 0,25 getrennt (`wiederholung`, `bildwiederholung`), Presetzeilen
   beider Formen (`aus_animation`).
4. `G9materialteile`: dieselbe Gruppe in zwei Netzen mit verschiedenem Bild → `<Gruppe>@<Netz>`, `teil`
   gibt jedem Teil seins; ein Preset (`ueberlagern`) trifft beide.
5. `G9stueckvorgaben`: Vorgabe des Morphs (Fix1 = 1), die Szene hebt sie auf (0) oder stellt über Daz'
   Kennung (`#Fix2-0xabc`).
6. `G9simulationsform.formen`: das letzte Bild der Simulation, nur bei passender Punktzahl.
7. `G9garderobeeintrag.vorschaudatei`: `<Name>.duf.png` wird gefunden.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from Genesis9.dson import G9dson  # noqa: E402
from Genesis9.garderobeeintrag import G9garderobeeintrag  # noqa: E402
from Genesis9.materialgrund import G9materialgrund  # noqa: E402
from Genesis9.materialteile import G9materialteile  # noqa: E402
from Genesis9.simulationsform import G9simulationsform  # noqa: E402
from Genesis9.stueckvorgaben import G9stueckvorgaben  # noqa: E402


def kanal(kennung, wert=None, bild=None, **mehr):
    ch = {'id': kennung}
    if wert is not None:
        ch['current_value'] = wert
    if bild:
        ch['image_file'] = bild
    ch.update(mehr)
    return {'channel': ch}


def material(kennung, url, *kanaele, diffuse=None, geometrie='#geometry', gruppen=None):
    m = {
        'id': kennung,
        'url': url,
        'geometry': geometrie,
        'groups': gruppen or [kennung],
        'extra': [{'type': 'studio_material_channels', 'channels': list(kanaele)}],
    }
    if diffuse is not None:
        m['diffuse'] = diffuse
    return m


class Materialgrundprobe(unittest.TestCase):
    def _doc(self, szene, bibliothek):
        return G9dson('kunst.duf', {'material_library': bibliothek, 'scene': {'materials': szene}})

    def test_1_bibliothek_unter_der_szene(self):
        basis = material(
            'fablic',
            None,
            kanal('Cutout Opacity', 0.7),
            kanal('Horizontal Tiles', 4),
            diffuse=kanal('diffuse', [0.7, 0.7, 0.7]),
        )
        szene = material(
            'fablic-1', '#fablic', diffuse=kanal('diffuse', [0.5, 0.5, 0.5], '/Runtime/Textures/x/fablic.jpg')
        )
        k = G9materialgrund.kanaele(self._doc([szene], [basis]), szene)
        self.assertEqual(G9materialgrund.wert(k['Cutout Opacity']), 0.7)
        self.assertEqual(G9materialgrund.wert(k['diffuse']), [0.5, 0.5, 0.5])
        self.assertEqual(k['diffuse']['image_file'], '/Runtime/Textures/x/fablic.jpg')

    def test_2_nur_abweichungen(self):
        tabelle = {'Cutout Opacity': 'alphawert', 'Metallic Weight': 'metallgewicht'}
        self.assertEqual(
            G9materialgrund.werte(
                {'Cutout Opacity': {'current_value': 1}, 'Metallic Weight': {'value': 0}}, tabelle
            ),
            {},
        )
        self.assertEqual(
            G9materialgrund.werte({'Cutout Opacity': {'current_value': 0.5}}, tabelle), {'alphawert': 0.5}
        )

    def test_3_wiederholung(self):
        k = {
            'Horizontal Tiles': {'current_value': 4},
            'Vertical Tiles': {'current_value': 4},
            'Normal Map': {
                'image_file': '/Runtime/Textures/n.png',
                'image_modification': {'horizontal_tiles': 0.25, 'vertical_tiles': 0.25},
            },
        }
        self.assertEqual(G9materialgrund.wiederholung(k), [4.0, 4.0, 0.0, 0.0])
        self.assertEqual(
            G9materialgrund.bildwiederholung(k, {'Normal Map': 'normalen'}),
            {'normalen': [0.25, 0.25, 0.0, 0.0]},
        )
        self.assertIsNone(G9materialgrund.wiederholung({}))
        tabelle = {'diffuse': 'albedo', 'Normal Map': 'normalen'}
        kanal_pfad = 'extra/studio_material_channels/channels/'
        self.assertEqual(
            G9materialgrund.aus_animation(kanal_pfad + 'Vertical Tiles/value', tabelle), ('wiederholung', 1)
        )
        self.assertEqual(
            G9materialgrund.aus_animation('diffuse/image_modification/horizontal_tiling_offset', tabelle),
            ('bild', 'albedo', 2),
        )
        self.assertIsNone(G9materialgrund.aus_animation(kanal_pfad + 'Glossy Roughness/value', tabelle))


class Materialteileprobe(unittest.TestCase):
    def test_4_gruppen_je_netz(self):
        doc = G9dson(
            'kunst.duf',
            {
                'scene': {
                    'nodes': [
                        {
                            'id': 'Knopf',
                            'geometries': [{'id': 'Knopf-1', 'url': '/data/k/Knopf.dsf#Knopf-1'}],
                        },
                        {'id': 'Cami', 'geometries': [{'id': 'geometry-2', 'url': '/data/k/Cami.dsf#Cami'}]},
                    ]
                }
            },
        )
        fertig = {'inner': {'albedo': 'a.jpg'}}
        einzeln = {('inner', '#Knopf-1'): {'albedo': 'a.jpg'}, ('inner', '#geometry-2'): {'albedo': 'b.jpg'}}
        with mock.patch(
            'Genesis9.materialteile.G9pfade.aufloesen', side_effect=lambda url: tuple(url.rsplit('#', 1))
        ):
            G9materialteile.eintragen(fertig, einzeln, doc)
        self.assertEqual(len([k for k in fertig if '@' in k]), 2)
        cami = type('Teil', (), {'pfad': '/data/k/Cami.dsf', 'kennung': 'Cami'})()
        knopf = type('Teil', (), {'pfad': '/data/k/Knopf.dsf', 'kennung': 'Knopf-1'})()
        self.assertEqual(G9materialteile.teil(fertig, cami), {'inner': {'albedo': 'b.jpg'}})
        self.assertEqual(G9materialteile.teil(fertig, knopf), {'inner': {'albedo': 'a.jpg'}})
        G9materialteile.ueberlagern(fertig, 'inner', {'farbe': [1, 0, 0]})
        self.assertTrue(all(v.get('farbe') == [1, 0, 0] for v in fertig.values()))


class Stueckvorgabenprobe(unittest.TestCase):
    def test_5_vorgabe_des_morphs_und_szene(self):
        steckbriefe = {
            'Fix1': {'vorgabe': 1.0, 'id': 'Fix1'},
            'Fix2': {'vorgabe': 0.0, 'id': 'Fix2-0xabc'},
            'Open': {'vorgabe': 0.0, 'id': 'Open'},
        }
        morphe = type('Morphe', (), {'steckbriefe': steckbriefe, 'hd': {}})()
        doc = G9dson(
            'kunst.duf',
            {
                'scene': {
                    'modifiers': [
                        {
                            'id': 'Fix1',
                            'url': '/data/k/Morphs/Fix1.dsf#Fix1',
                            'channel': {'current_value': 0},
                        },
                        {
                            'id': 'Fix2-1',
                            'url': '/data/k/Morphs/Fix2.dsf#Fix2-0xabc',
                            'channel': {'current_value': 1},
                        },
                        {'id': 'SkinBinding', 'url': '/data/k/x.dsf#SkinBinding'},
                    ]
                }
            },
        )
        with mock.patch('Genesis9.stueckvorgaben.G9anhangmorphe.fuer', return_value=morphe):
            self.assertEqual(G9stueckvorgaben.lesen(doc, [('x.dsf', 'x')]), {'Fix2': 1.0})
        doc_leer = G9dson('kunst.duf', {'scene': {}})
        with mock.patch('Genesis9.stueckvorgaben.G9anhangmorphe.fuer', return_value=morphe):
            self.assertEqual(G9stueckvorgaben.lesen(doc_leer, [('x.dsf', 'x')]), {'Fix1': 1.0})


class Simulationsformprobe(unittest.TestCase):
    def test_6_letztes_bild(self):
        sim = {
            'type': 'studio/modifier/dynamic_simulation',
            'vertex_count': 2,
            'simulation_data': [
                {'time': 0, 'count': 2, 'values': [[0, 0, 0], [0, 0, 0]]},
                {'time': 1.5, 'count': 2, 'values': [[1, 2, 3], [0, -1, 0]]},
            ],
        }
        doc = G9dson(
            'kunst.duf',
            {'scene': {'modifiers': [{'id': 'dForce Simulation', 'parent': '#Hemd', 'extra': [sim]}]}},
        )
        self.assertEqual(G9simulationsform.formen(doc), {'Hemd': (2, [[1, 2, 3], [0, -1, 0]])})
        self.assertEqual(G9simulationsform.kanal('shirt_open'), 'dforce:shirt_open')


class Vorschauprobe(unittest.TestCase):
    def test_7_icon_duf_png(self):
        with tempfile.TemporaryDirectory(dir=str(settings.TOOLS_ROOT / 'ProjektTemp')) as ordner:
            duf = Path(ordner) / 'Kleid.duf'
            duf.write_text('{}', encoding='utf-8')
            (Path(ordner) / 'Kleid.duf.png').write_bytes(b'png')
            self.assertEqual(G9garderobeeintrag.vorschaudatei(duf).name, 'Kleid.duf.png')


if __name__ == '__main__':
    unittest.main()
