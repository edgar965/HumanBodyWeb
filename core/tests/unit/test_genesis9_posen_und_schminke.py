# -*- coding: utf-8 -*-
u"""Genesis 9, 18.09.2026: Bestandsschluessel, Schminke-Ebenen, Posen-Leser,
Kleidungsregler, Brauenstile, Hautwahl-Klassen, Reglerplan-Bereiche —
alles OHNE Daz-Bibliothek (synthetische Dokumente und Bilder).

Sabotage-Gegenproben (je ein Fall): `G9ebenen._gewicht` ohne Deckkraft ->
Fall 2 rot; `G9knochenmatrizen.euler` mit umgekehrter Reihenfolge -> Fall 4
rot; `G9posen._lesen` ohne `rstrip(':')` -> Fall 6 rot.
"""
import os
import tempfile
import time
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from Genesis9.anhangmorphe import G9anhangmorphe
from Genesis9.bestand import G9bestand
from Genesis9.brauen import G9brauen
from Genesis9.dson import G9dson
from Genesis9.ebenen import G9ebenen
from Genesis9.hautwahl import G9hautwahl
from Genesis9.knochenmatrizen import G9knochenmatrizen
from Genesis9.posen import G9posen
from Genesis9.reglerplan import G9reglerplan
from Genesis9.schminke import G9schminke


def _bild(farbe, alpha, groesse=(4, 4)):
    bild = Image.new('RGBA', groesse, farbe + (alpha,))
    return bild


class Genesis9Bestand(SimpleTestCase):

    databases = set()

    def test_1_schluessel_aendert_sich_mit_inhalt_und_neuer_datei(self):
        with tempfile.TemporaryDirectory() as ordner:
            a = os.path.join(ordner, 'a.dsf')
            with open(a, 'w') as f:
                f.write('x')
            eins = G9bestand.ordner(ordner, '*.dsf')
            self.assertEqual(eins, G9bestand.ordner(ordner, '*.dsf'))
            with open(a, 'w') as f:
                f.write('xy')            # andere Groesse
            os.utime(a, (time.time() - 100, time.time() - 100))
            zwei = G9bestand.ordner(ordner, '*.dsf')
            self.assertNotEqual(eins, zwei)
            with open(os.path.join(ordner, 'b.dsf'), 'w') as f:
                f.write('x')             # neue Datei (Ursula-Fall)
            self.assertNotEqual(zwei, G9bestand.ordner(ordner, '*.dsf'))
            self.assertEqual(G9bestand.anzahl(ordner, '*.dsf'), 2)


class Genesis9Ebenen(SimpleTestCase):

    databases = set()

    def test_2_farbe_und_gewicht_mit_deckkraft(self):
        bilder = {'rot': _bild((255, 0, 0), 128), 'blau': _bild((0, 0, 255), 255),
                  'maske': _bild((255, 255, 255), 64)}
        with mock.patch.object(G9ebenen, '_oeffnen', side_effect=lambda p: bilder[p]):
            aus = G9ebenen._rechnen([{'farbe': 'rot', 'deckkraft': 0.5}], False)
            self.assertEqual(aus['farbe'].getpixel((0, 0)), (255, 0, 0))
            self.assertEqual(aus['gewicht'].getpixel((0, 0)), 64)    # 0,5 · 0,5
            # Maske statt Alpha: weiss mit Alpha 64 auf Schwarz -> 64.
            aus = G9ebenen._rechnen([{'farbe': 'blau', 'maske': 'maske',
                                      'deckkraft': 1}],
                                    False)
            self.assertEqual(aus['gewicht'].getpixel((0, 0)), 64)
            # Zwei Ebenen: blau (voll) ueber rot -> blau, Gewicht 255.
            aus = G9ebenen._rechnen([{'farbe': 'rot', 'deckkraft': 1},
                                     {'farbe': 'blau', 'deckkraft': 1}], False)
            self.assertEqual(aus['farbe'].getpixel((0, 0)), (0, 0, 255))
            self.assertEqual(aus['gewicht'].getpixel((0, 0)), 255)

    def test_3_rauheitsfaktor_aus_mult_und_ersatzkarte(self):
        u"""Drittes Bild: R = Faktor (`mult`, Ursula), G/B = Ersatzwert und
        -gewicht einer Rauheitskarte mit Alpha (Makeup-System)."""
        bilder = {'rot': _bild((255, 0, 0), 255), 'r': _bild((51, 51, 51), 128)}
        with mock.patch.object(G9ebenen, '_oeffnen', side_effect=lambda p: bilder[p]):
            aus = G9ebenen._rechnen([{'farbe': 'rot', 'deckkraft': 1, 'mult': 0.5}],
                                    True)
            self.assertEqual(aus['rauheit'].getpixel((0, 0)), (128, 0, 0))
            aus = G9ebenen._rechnen([{'farbe': 'rot', 'deckkraft': 1, 'rauheit': 'r',
                                      'rauheitdeckkraft': 0.5}], True)
            self.assertEqual(aus['rauheit'].getpixel((0, 0)), (255, 51, 64))

    def test_3b_makeup_farbe_ueber_schwarz_und_farbflaeche(self):
        u"""Das Makeup-System legt die Farbe ueber Schwarz (Alpha mal Deckkraft
        dunkelt); eine Farbflaeche ohne Bild kommt aus `farbwert`."""
        bilder = {'d': _bild((200, 100, 0), 128), 'm': _bild((255, 255, 255), 255)}
        with mock.patch.object(G9ebenen, '_oeffnen', side_effect=lambda p: bilder[p]):
            aus = G9ebenen._rechnen([{'farbe': 'd', 'maske': 'm', 'deckkraft': 1,
                                      'farbdeckkraft': 0.5, 'ueber_schwarz': True}],
                                    False)
            r, g, b = aus['farbe'].getpixel((0, 0))
            self.assertTrue(abs(r - 50) <= 1 and abs(g - 25) <= 1 and b == 0, (r, g, b))
            self.assertEqual(aus['gewicht'].getpixel((0, 0)), 255)
            aus = G9ebenen._rechnen([{'farbwert': [1, 0.5, 0], 'maske': 'm',
                                      'deckkraft': 0.6, 'ueber_schwarz': True}], False)
            self.assertEqual(aus['farbe'].getpixel((0, 0)), (255, 128, 0))
            self.assertEqual(aus['gewicht'].getpixel((0, 0)), 153)


class Genesis9Rotation(SimpleTestCase):

    databases = set()

    def test_4_eulerfolge_erste_achse_zuerst(self):
        k = G9knochenmatrizen
        erwartet = k._achse('Z', 30) @ k._achse('Y', 20) @ k._achse('X', 10)
        self.assertTrue(np.allclose(k.euler((10, 20, 30), 'XYZ'), erwartet))
        umgekehrt = k._achse('X', 10) @ k._achse('Y', 20) @ k._achse('Z', 30)
        self.assertTrue(np.allclose(k.euler((10, 20, 30), 'ZYX'), umgekehrt))

    def test_5_pose_dreht_kindgelenk_um_knochenachse(self):
        roh = [{'name': 'a', 'eltern': None, 'kopf': np.array([0., 0., 0.]),
                'schwanz': np.array([0., 10., 0.]), 'erbt': False,
                'orientation': np.zeros(3), 'reihenfolge': 'XYZ'},
               {'name': 'b', 'eltern': 'a', 'kopf': np.array([0., 10., 0.]),
                'schwanz': np.array([0., 20., 0.]), 'erbt': False,
                'orientation': np.zeros(3), 'reihenfolge': 'XYZ'}]
        m = G9knochenmatrizen({}, roh=roh, drehung={'a': {'rotation/z': 90.0}})
        kopf, schwanz = m.gelenk('b', roh[1]['kopf'], roh[1]['schwanz'])
        # 90° um Z am Elternknochen: das Kindgelenk (0,10,0) landet bei (−10,0,0).
        self.assertTrue(np.allclose(kopf, [-10, 0, 0], atol=1e-9), kopf)
        self.assertTrue(np.allclose(schwanz, [-20, 0, 0], atol=1e-9), schwanz)
        self.assertFalse(m.leer)


class Genesis9Posenleser(SimpleTestCase):

    databases = set()

    def test_6_knochen_und_regler_aus_animationen(self):
        doc = G9dson('x.duf', {'scene': {'animations': [
            {'url': 'name://@selection/l_upperarm:?rotation/x/value',
             'keys': [[0, -38.2]]},
            {'url': 'name://@selection/l_upperarm:?rotation/y/value', 'keys': [[0, 0]]},
            {'url': 'name://@selection/hip:?translation/y/value', 'keys': [[0, 6.5]]},
            {'url': 'name://@selection#body_ctrl_ArmsUpDwn:?value/value',
             'keys': [[0, 0.5]]},
            {'url': 'name://@selection#body_bs_Null:?value/value', 'keys': [[0, 0]]},
        ]}})
        knochen, regler = G9posen._lesen(doc)
        self.assertEqual(knochen, {'l_upperarm': {'rotation/x': -38.2},
                                   'hip': {'translation/y': 6.5}})
        self.assertEqual(regler, {'body_ctrl_ArmsUpDwn': 0.5})


class Genesis9Schminkekatalog(SimpleTestCase):

    databases = set()

    def test_7_kategorien_und_bildnamen(self):
        art = G9schminke.kategorie_von
        self.assertEqual(art('LIE Blush/P3D Ursula Blush Pink'), 'rouge')
        self.assertEqual(art('LIE Eye Make Up/P3D Ursula Eyeliner'), 'eyeliner')
        self.assertEqual(G9schminke.kategorie_von('Eyeshadow'), 'lidschatten')
        self.assertEqual(G9schminke.kategorie_von('Lips/P3D Ursula Lips Red'), 'lippen')
        self.assertIsNone(G9schminke.kategorie_von('Nail Polish'))
        self.assertEqual(G9schminke.kategorie_von('Amelia 9 MU 01 Foundation'),
                         'grundierung')
        self.assertEqual(G9schminke._systemname('Amelia 9 Makeup',
                                                'Amelia 9 MU 01 Blush'),
                         ('Amelia 9', u'Amelia 9 · Blush 01'))
        self.assertEqual(G9schminke._systemname('Daz Anime', 'G9AnimeAllFace02'),
                         ('Anime', u'Anime · All Face 02'))

    def test_8_makeup_kanaele_werden_zur_ebene(self):
        doc = G9dson('x.duf', {'scene': {'animations': [
            {'url': 'name://@selection#materials/Head:?extra/studio_material_channels/'
                    'channels/Makeup%20Weight/image_file',
             'keys': [[0, '/Runtime/Textures/x/LipsMW.jpg']]},
            {'url': 'name://@selection#materials/Head:?extra/studio_material_channels/'
                    'channels/Makeup%20Base%20Color/image_file',
             'keys': [[0, '/Runtime/Textures/x/LipsRe.jpg']]},
            {'url': 'name://@selection#materials/Head:?extra/studio_material_channels/'
                    'channels/Makeup%20Roughness%20Mult/value', 'keys': [[0, 0.7]]},
        ]}})
        ebenen = G9schminke._ebenen_aus_preset(doc)
        self.assertEqual(ebenen, [{'gruppe': 'Head', 'ueber_schwarz': True,
                                   'farbe': '/Runtime/Textures/x/LipsRe.jpg',
                                   'farbdeckkraft': 1.0,
                                   'maske': '/Runtime/Textures/x/LipsMW.jpg',
                                   'deckkraft': 1.0, 'mult': 0.7}])

    def test_8b_script_load_preset_mit_lie_stapeln(self):
        u"""Amelias `MU 02 Eyeshadow`: Maske 0,9, Farbe 0,7, Rauheitskarte —
        die Deckkraft kommt aus den Ebenen, nicht mehr aus einer Vermutung."""
        def lie(kennung, url, deck):
            return {'id': kennung, 'map': [
                {'label': 'Background', 'color': [0, 0, 0], 'transparency': 1},
                {'url': url, 'transparency': deck, 'operation': 'blend_source_over'}]}
        kanal = ('name://@selection#materials/Head:?extra/'
                 'studio_material_channels/channels/')
        doc = G9dson('x.duf', {
            'image_library': [lie('W 7', '/Runtime/Textures/x/E_WM.png', 0.9),
                              lie('C 6', '/Runtime/Textures/x/E_D.png', 0.7),
                              lie('R 2', '/Runtime/Textures/x/E_R.png', 1)],
            'scene': {'animations': [
                {'url': kanal + 'Makeup%20Weight/image', 'keys': [[0, '#W%207']]},
                {'url': kanal + 'Makeup%20Base%20Color/image', 'keys': [[0, '#C%206']]},
                {'url': kanal + 'Specular%20Lobe%201%20Roughness/image',
                 'keys': [[0, '#R%202']]},
            ]}})
        ebenen = G9schminke._ebenen_aus_preset(doc)
        self.assertEqual(ebenen, [{'gruppe': 'Head', 'ueber_schwarz': True,
                                   'maske': '/Runtime/Textures/x/E_WM.png',
                                   'deckkraft': 0.9,
                                   'farbe': '/Runtime/Textures/x/E_D.png',
                                   'farbdeckkraft': 0.7,
                                   'rauheit': '/Runtime/Textures/x/E_R.png',
                                   'rauheitdeckkraft': 1.0}])
        # Farbflaeche (Basic Foundations) und Ebenenmaske (Anime-Nase).
        doc = G9dson('y.duf', {
            'image_library': [
                {'id': 'C', 'map': [{'label': 'Background', 'color': [0, 0, 0],
                                     'transparency': 1},
                                    {'label': 'F', 'color': [1, 0.5, 0.25],
                                     'transparency': 1}]},
                {'id': 'A', 'map': [{'url': '/Runtime/Textures/x/Head.png',
                                     'transparency': 1},
                                    {'label': 'Nase', 'color': [0.8, 0.6, 0.5],
                                     'transparency': 1,
                                     'mask': {'url': '/Runtime/Textures/x/CM.jpg'}}]}],
            'scene': {'animations': [
                {'url': kanal + 'Makeup%20Weight/image', 'keys': [[0, '#W']]},
                {'url': kanal + 'Makeup%20Base%20Color/image', 'keys': [[0, '#C']]},
            ]}})
        self.assertEqual(G9schminke._ebenen_aus_preset(doc), [])   # ohne Maske nichts
        self.assertEqual(G9ebenen.aus_stapel(doc, 'A', 'Head'), [
            {'gruppe': 'Head', 'farbe': None, 'farbwert': [0.8, 0.6, 0.5],
             'maske': '/Runtime/Textures/x/CM.jpg', 'deckkraft': 1.0}])


class Genesis9Kleidungsregler(SimpleTestCase):

    databases = set()

    def test_9_nur_eigene_sichtbare_kanaele(self):
        morphe = G9anhangmorphe({}, {
            'Adj Inflate Collar': {'label': 'Adj Inflate Collar',
                                   'gruppe': '/Adjustments',
                                   'min': -1, 'max': 1, 'sichtbar': True},
            'Angela9_body_bs_Body': {'label': 'x',
                                     'gruppe': '/Full Body/People/Feminine',
                                     'min': -1, 'max': 1, 'sichtbar': True},
            'FIX': {'label': 'FIX', 'gruppe': '/Actor/Hair Morphs',
                    'min': 1, 'max': 1, 'sichtbar': False},
            'body_bs_BodyLithe': {'label': 'x', 'gruppe': '/Adjustments',
                                  'min': -1, 'max': 1, 'sichtbar': True},
        })
        regler = morphe.regler(koerperkanaele={'body_bs_BodyLithe'})
        self.assertEqual([r['name'] for r in regler], ['Adj Inflate Collar'])
        self.assertEqual(regler[0]['gruppe'], 'Adjustments')


class Genesis9BrauenUndHautwahl(SimpleTestCase):

    databases = set()

    def test_10_brauenstil_kennung(self):
        self.assertEqual(G9brauen.stil('fiber03'), ('fiber', '03'))
        self.assertEqual(G9brauen.stil('quatsch'), ('card', '01'))
        self.assertEqual(G9brauen.stil(None), ('card', '01'))

    def test_11_hautwahl_klassen(self):
        haut = {g: {'albedo': 'x'} for g in ('Head', 'Body', 'Arms', 'Legs')}
        haut['Eye Left'] = haut['Eye Right'] = {'albedo': 'y'}
        self.assertEqual(G9hautwahl.kategorie_von(haut), 'haut')
        augen = {'Eye Left': {'albedo': 'y'}, 'Eye Right': {'albedo': 'y'}}
        self.assertEqual(G9hautwahl.kategorie_von(augen), 'augen')
        self.assertEqual(G9hautwahl.kategorie_von({'Eyelashes Lower': {'farbe': [0, 0,
                                                                                 0]}}),
                         'wimpern')
        naegel = {'Fingernails': {'farbe': [0, 0, 0]}, 'Toenails': {'farbe': [0, 0, 0]}}
        self.assertEqual(G9hautwahl.kategorie_von(naegel), 'nagellack')
        naegel['Head'] = {'farbe': [1, 1, 1]}      # Anime Skin Tone: kein Lack
        self.assertIsNone(G9hautwahl.kategorie_von(naegel))

    def test_12_reglerplan_bereiche(self):
        self.assertEqual(G9reglerplan.bereich({'gruppe': '/Pose Controls/Head/Mouth',
                                               'label': 'Jaw Open'}), 'mimik')
        self.assertIsNone(G9reglerplan.bereich({'gruppe': '/Pose Controls/Arms',
                                                'label': 'Arms Up'}))
        self.assertIsNone(G9reglerplan.bereich({'gruppe': '/Pose Controls/Head/Mouth/'
                                                          'Base Anime', 'label': 'x'}))
        self.assertEqual(G9reglerplan.bereich({'gruppe': '/Morphs',
                                               'label': 'Nails Oval'}),
                         'koerper')
