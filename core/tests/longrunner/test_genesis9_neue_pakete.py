# -*- coding: utf-8 -*-
u"""Die drei Daz-Pakete vom 20.09.2026 gegen die installierte Bibliothek (Edgar:
„importiere die neuen Pakete aus Daz3D … baue das Haar, das neue Modell und
die Genesis Shape Builder"):

1. Genesis 9 Body Shapes (SKU 86961): 225 Morphdateien unter
   `Base/Morphs/Daz 3D/Body*` (125 sichtbar, 100 Korrektive); die Regler
   stehen nach Daz' `region` in
   Brust, Taille, Huefte, Ruecken, Arme, Haende, Beine, Fuesse — keiner
   mehr unter Kopf (vorher 63), auch die HD-Brustwarze (nur `.dhdm`).
2. MB Olesia HD (SKU 101220): Katalogeintrag `mb_olesia_hd` mit Preset-
   Reglern, Haut aus dem Preset, eigenes Brauennetz, fuenf Augen, Hautsaetze
   und Schminke in der Hautwahl — `!Off`-Presets nicht.
3. HS Viola Hair (SKU 110848): Straenge verdichtet (477.720 statt
   3.582.900 Punkte, 418.005 Segmente), die unsichtbare Kappe bleibt
   Geruest und nicht im Browser, OmniHair-Wurzel/Spitze je Variante.

LongRunner (Viola kalt 10 s). Ohne die Pakete uebersprungen.

Sabotage-Gegenproben: `G9reglerbereiche.REGIONEN['Waist'] = 'kopf'` →
Fall 1 rot; `G9brauen.charakterbrauen` wieder `*Eyebrows*.duf` → Fall 2 rot;
`G9strangverdichtung.behalten = None` → Fall 3 rot (1.981.080 Punkte).
"""
import unittest

from django.test import Client, SimpleTestCase
from Genesis9.brauen import G9brauen
from Genesis9.charaktere import G9charaktere
from Genesis9.garderobe import G9garderobe
from Genesis9.hautwahl import G9hautwahl
from Genesis9.morphablage import G9morphablage
from Genesis9.pfade import G9pfade
from Genesis9.reglerplan import G9reglerplan


def pakete_da():
    if not G9pfade.vorhanden():
        return False
    return ((G9pfade.morphs() / 'Daz 3D' / 'Body').is_dir()
            and (G9pfade.people() / 'Characters' / 'MB Olesia HD for Genesis 9 Feminine.duf').is_file()
            and (G9pfade.people() / 'Hair' / 'Daz Originals' / 'HS Viola Hair').is_dir())


@unittest.skipUnless(pakete_da(), 'Body Shapes, MB Olesia oder HS Viola Hair fehlen')
class NeuePaketeTest(SimpleTestCase):
    databases = set()

    def test_1_body_shapes_nach_region(self):
        ablage = G9morphablage.holen()
        neu = {k: v for k, v in ablage.kanaele.items()
               if v['datei'].replace('\\', '/').startswith('Daz 3D/Body')}
        self.assertEqual(len(neu), 225)
        plan = {r['name']: r for r in G9reglerplan.holen()}
        je = {}
        for kennung, kanal in neu.items():
            if kanal['sichtbar']:
                self.assertIn(kennung, plan, kanal['label'])
                je.setdefault(plan[kennung]['bereich'], set()).add(kanal['label'])
        self.assertNotIn('kopf', je)
        self.assertNotIn('figur', je)
        self.assertTrue({'Breasts Cleavage', 'Pectorals Size', 'Sternum Width',
                         'Nipples Depth Feminine HD'} <= je['brust'], je['brust'])
        self.assertTrue({'Waist Width', 'Abdominals Width', 'Pregnant',
                         'Navel Depth HD'} <= je['taille'], je['taille'])
        self.assertTrue({'Glute Size', 'Hip Size', 'Hip Pelvic Tilt'} <= je['huefte'])
        self.assertTrue({'Lats Size', 'Scapula Size'} <= je['ruecken'])
        self.assertTrue({'Mass Neck', 'Traps Size'} <= je['hals'])
        self.assertTrue({'Mass Upper Arms', 'Taper Forearm A'} <= je['arme'])
        self.assertTrue({'Fingers Width', 'Nails Length Round'} <= je['haende'])
        self.assertTrue({'Mass Thighs', 'Calves Size'} <= je['beine'])
        self.assertTrue({'Foot Arch Depth', 'Mass Ankles'} <= je['fuesse'])
        self.assertTrue({'Body Heavy', 'Body Fitness', 'Body Pear Figure'} <= je['koerper'])
        # Gemessen 20.09.2026 (`_wegwerf/mess_g9bodyshapes.py`): 125 sichtbare.
        self.assertEqual(sum(len(s) for s in je.values()), 125)
        for r in plan.values():
            self.assertIn(r['art'], ('form', 'pose'))
        self.assertEqual(plan['CTRLArmsUpDwn']['art'], 'pose')
        self.assertEqual(plan['body_bs_WaistWidth']['art'], 'form')

    def test_2_olesia_im_katalog(self):
        e = G9charaktere.eintrag('mb_olesia_hd')
        self.assertIsNotNone(e)
        self.assertEqual(e['anzeige'], 'MB Olesia HD')
        self.assertEqual(e['geschlecht'], u'weiblich')
        self.assertIn('MB_Olesia_figure_ctrl_Character-0xa3c8d22', e['regler'])
        self.assertIn('MB_Olesia_Head_D.jpg', e['bilder']['Head']['albedo'])
        self.assertEqual(e.get('brauenstil'), 'charakter:mb_olesia_brows_apply')
        braue = G9brauen.charakterbraue('charakter:mb_olesia_brows_apply')
        self.assertIsNotNone(braue)
        self.assertTrue(braue['geometrie'].is_file())
        katalog = G9hautwahl.katalog()
        namen = {kat: {x['name'] for x in liste if 'Olesia' in x['name']}
                 for kat, liste in katalog.items()}
        self.assertEqual(len(namen['augen']), 5)
        self.assertEqual(len(namen['wimpern']), 1)
        self.assertEqual(len(namen['nagellack']), 4)          # ohne `Nails !Off`
        self.assertEqual({n.split(u' · ')[1] for n in namen['haut']},
                         {'!All MAT', 'Skin MAT'})
        self.assertFalse(namen.get('kopf'))                    # keine `!Off`
        # Ursulas Hautsatz steht wieder in der Hautwahl (fiel bis 20.09. heraus).
        self.assertTrue(any('Complete Texture' in x['name'] for x in katalog['haut']))
        r = Client().get('/api/character/genesis9-figur/').json()
        self.assertIn('mb_olesia_hd', [f['name'] for f in r['figuren']])

    def test_3_viola_straenge_kappe_farben(self):
        eintrag = G9garderobe.eintrag('hs_viola_hair_g9')
        self.assertIsNotNone(eintrag)
        self.assertEqual(eintrag['art'], 'haar')
        self.assertTrue(eintrag['zeigbar'])
        self.assertEqual(len(eintrag['varianten']), 25)
        self.assertEqual({r['name'] for r in eintrag['regler']}, {'Move Front', 'Move Side'})
        teile = G9garderobe.teile('hs_viola_hair_g9')
        # Die unsichtbare Kappe (`Visible: false`) geht nicht an den Browser.
        self.assertEqual([f.name for f, _lage in teile], ['Hair R', 'Hair L'])
        rechts, links = (f for f, _lage in teile)
        self.assertEqual(len(rechts.punkte), 264_144)
        self.assertEqual(len(links.punkte), 213_576)
        self.assertEqual(len(rechts.segmente) + len(links.segmente), 418_005)
        self.assertTrue(rechts.verdichtung.noetig)
        self.assertIsNotNone(rechts.haut)          # Haut von der Kappe
        self.assertEqual(sorted(rechts.morphe.namen()), ['Move Front', 'Move Side'])
        # OmniHair nach Daz' eigener Rechnung (`G9haarfarben`): Amber = dark
        # blonde × Tint, Light Blonde = Melanin 0,25 allein, Grund fast schwarz.
        amber = G9garderobe.bilder('hs_viola_hair_g9', 'hs_vh_g9_omni_amber')['Hair']
        self.assertEqual(amber['farbe'], [0.5405, 0.3405, 0.2268])
        self.assertEqual(amber['farbe_spitze'], [0.4764, 0.2803, 0.1934])
        blond = G9garderobe.bilder('hs_viola_hair_g9', 'hs_vh_g9_omni_light_blonde')['Hair']
        self.assertEqual(blond['farbe'], [0.5085, 0.3941, 0.2362])
        grund = G9garderobe.bilder('hs_viola_hair_g9')['Hair']
        self.assertEqual(grund['farbe'], [0.0314, 0.0036, 0.0001])
        # Ein Preset mit eigener Ansichtsfarbe behaelt sie (Black Blue; Pixie Ash).
        blau = G9garderobe.bilder('hs_viola_hair_g9', 'hs_vh_g9_omni_black_blue')['Hair']
        self.assertEqual(blau['farbe'], [0.0902, 0.1529, 0.2039])
        self.assertNotIn('farbe_spitze', blau)
        pixie = G9garderobe.bilder('g9_base_dforce_pixie_hair',
                                   'g9_base_dforce_pixie_omnihair_ash')['Hair01']
        self.assertEqual(pixie['farbe'], [0.8784, 0.8784, 0.8784])
