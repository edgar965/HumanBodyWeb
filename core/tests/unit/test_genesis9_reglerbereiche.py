# -*- coding: utf-8 -*-
u"""G9reglerbereiche (20.09.2026, Genesis 9 Body Shapes): Region schlaegt Gruppe.

Gemessen mit `_wegwerf/mess_g9bodyshapes.py`: 63 der 130 sichtbaren,
wirksamen Body-Shapes-Kanaele standen unter „Kopf", weil `/Base` als
Gesicht galt; „Nipples Depth Feminine HD" (nur `.dhdm`, 0 Deltas) fehlte
ganz. Kunstdaten, keine Bibliothek.

Sabotage-Gegenproben:
- `REGIONEN['Waist'] = 'kopf'` → `test_1_form_nach_region` rot.
- `_pose`: `TORSO` leer → `test_2_pose_nach_teil_und_label` rot (Waist Bend
  landet im Ruecken).
- `wirksame`: `hd` nicht gezaehlt → `test_4_hd_allein_ist_wirksam` rot.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.morphablage import G9morphablage
from Genesis9.reglerbereiche import G9reglerbereiche
from Genesis9.reglerplan import G9reglerplan


def kanal(gruppe, label, region='', **mehr):
    k = {'id': label.replace(' ', ''), 'label': label, 'gruppe': gruppe,
         'region': region, 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0,
         'sichtbar': True, 'formeln': [], 'datei': 'x.dsf', 'hd': ''}
    k.update(mehr)
    return k


class Reglerbereiche(SimpleTestCase):
    databases = set()

    def test_1_form_nach_region(self):
        b = G9reglerbereiche.bereich
        self.assertEqual(b(kanal('/Base', 'Waist Width', 'Waist')), 'taille')
        self.assertEqual(b(kanal('/Base', 'Glute Size', 'Hip')), 'huefte')
        self.assertEqual(b(kanal('/Base', 'Lats Size', 'Back')), 'ruecken')
        self.assertEqual(b(kanal('/Base', 'Mass Thighs', 'Legs')), 'beine')
        self.assertEqual(b(kanal('/Base', 'Mass Forearms', 'Arms')), 'arme')
        self.assertEqual(b(kanal('/Base', 'Fingers Width', 'Hands')), 'haende')
        self.assertEqual(b(kanal('/Base', 'Foot Arch Depth', 'Feet')), 'fuesse')
        self.assertEqual(b(kanal('/Base', 'Sternum Width', 'Chest')), 'brust')
        self.assertEqual(b(kanal('/Feminine', 'Breasts Cleavage', 'Chest')), 'brust')
        self.assertEqual(b(kanal('/Masculine', 'Pectorals Size', 'Chest')), 'brust')
        self.assertEqual(b(kanal('/Base', 'Nose Width', 'Nose')), 'kopf')
        self.assertEqual(b(kanal('/Base', 'Eyes Height', 'Eyes')), 'kopf')
        self.assertEqual(b(kanal('/Full Body/Base', 'Body Heavy', 'Actor')), 'koerper')
        self.assertEqual(b(kanal('/Base', 'Proportion Legs Length', 'Legs')), 'beine')
        # Der Hals traegt bei Daz die Region `Head` — die Gruppe entscheidet.
        self.assertEqual(b(kanal('/Neck/Base', 'Mass Neck', 'Head')), 'hals')
        # Ohne Region: Rueckfall auf die Gruppe (Fremdanbieter, Kunstdaten).
        self.assertEqual(b(kanal('/Base', 'Spline')), 'kopf')
        self.assertEqual(b(kanal('/Morphs', 'Nails Oval')), 'koerper')
        self.assertEqual(b(kanal('/Morphs', 'Nails Oval', 'Hands')), 'haende')
        self.assertIsNone(b(kanal('/Hidden/x', 'Klon', 'Actor')))
        self.assertIsNone(b(kanal('/Tools', 'x')))
        self.assertIsNone(b(kanal('', 'x')))

    def test_2_pose_nach_teil_und_label(self):
        b = G9reglerbereiche.bereich
        self.assertEqual(b(kanal('/Pose Controls/Torso/Feminine', 'Breasts Up-Down')),
                         'brust')
        self.assertEqual(b(kanal('/Pose Controls/Torso', 'Waist Twist')), 'taille')
        self.assertEqual(b(kanal('/Pose Controls/Torso', 'Hip Bend Forward')), 'huefte')
        self.assertEqual(b(kanal('/Pose Controls/Torso', 'Torso Slump')), 'ruecken')
        self.assertEqual(b(kanal('/Pose Controls/Torso/Base',
                                 'Flex Shoulder Upper Back Left')), 'ruecken')
        self.assertEqual(b(kanal('/Pose Controls/Hip', 'Flex Glute Clench Left')),
                         'huefte')
        self.assertEqual(b(kanal('/Pose Controls/Neck', 'Neck Flex')), 'hals')
        self.assertEqual(b(kanal('/Pose Controls/Head/Mouth', 'Jaw Open')), 'mimik')
        self.assertIsNone(b(kanal('/Pose Controls/Head/Eyes/Base Anime', 'x')))
        self.assertIsNone(b(kanal('/Pose Controls/Quatsch', 'x')))

    def test_3_people_figur_kopf_koerper(self):
        b = G9reglerbereiche.bereich
        self.assertEqual(b(kanal('/People/Feminine', 'MB Olesia', 'Actor')), 'figur')
        self.assertEqual(b(kanal('/People/Feminine', 'MB Olesia Head', 'Head')), 'kopf')
        # Kopf-HD ohne „ Head" am Ende — die Region sagt es (stand unter Figur).
        self.assertEqual(b(kanal('/People/Feminine', 'MB Olesia Head HD Details',
                                 'Head')), 'kopf')
        self.assertEqual(b(kanal('/Full Body/People/Feminine', 'MB Olesia Body',
                                 'Actor')), 'koerper')
        self.assertEqual(b(kanal('/People/Masculine', 'Ty Body')), 'koerper')
        for schluessel in G9reglerbereiche.BEREICHE:
            self.assertIn(schluessel, G9reglerbereiche.NAMEN)
        self.assertEqual(G9reglerplan.BEREICHE, G9reglerbereiche.BEREICHE)

    def test_4_hd_allein_ist_wirksam(self):
        kanaele = {'nurhd': kanal('/Feminine', 'Nipples Depth Feminine HD', 'Chest',
                                  id='nurhd', hd='/x.dhdm'),
                   'leer': kanal('/Feminine', 'Leer', 'Chest', id='leer'),
                   'pose': kanal('/Pose Controls/Arms', 'Arms Up', id='pose',
                                 formeln=[{'ziel': ['pose', 'l_upperarm', 'rotation/z'],
                                           'stufe': 'sum',
                                           'ops': [{'op': 'push', 'kanal': 'pose'},
                                                   {'op': 'push', 'val': 30.0},
                                                   {'op': 'mult'}]}])}
        ablage = G9morphablage(kanaele, np.zeros(0, dtype=np.int32),
                               np.zeros((0, 3), dtype=np.float32),
                               {'nurhd': 0, 'leer': 0, 'pose': 0},
                               {'nurhd': 0, 'leer': 0, 'pose': 0})
        plan = G9reglerplan.bauen(ablage)
        je = {r['name']: r for r in plan}
        self.assertIn('nurhd', je)
        self.assertNotIn('leer', je)
        self.assertEqual(je['nurhd']['bereich'], 'brust')
        self.assertEqual(je['nurhd']['art'], 'form')
        self.assertEqual(je['pose']['art'], 'pose')
        self.assertEqual(je['pose']['bereich'], 'arme')
