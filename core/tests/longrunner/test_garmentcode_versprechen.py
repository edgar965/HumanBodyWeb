# -*- coding: utf-8 -*-
u"""Jedes GarmentCode-Stück liefert, was es verspricht — gemessen an Kin.

Edgar, 20.09.2026: „alle tests zu allen Items des Garment Code, ob sie das
liefern was sie versprechen? Hast du alle tests laufen lassen und sind sie
alle grün???" — bis dahin prüften die Knopf-Tests nur, dass die Endpunkte
antworten; die FORM eines Stücks prüfte niemand, und so wurde aus jedem
Höschen eine Boxershorts.

Zwei Stufen:
  1. SCHNITT (2D, je ~1 s): jede Form jeder Vorlage baut ohne Fehler und
     ohne Selbstschnitt, mit den Panelfamilien, die sie verspricht (ein BH
     hat keine Ärmel, ein Slip keine Hosenbeine, ein Kleid Rumpf und Rock).
  2. SITZ (3D, je 6–40 s): das drapierte Stück sitzt am Körper, wo es hin
     soll — Bund, Saum, Schritt gegen die Landmarken des Kin-Netzes
     (`kinlandmarken.py`), links und rechts gleich hoch.

Die Grenzen sind das VERSPRECHEN, nicht der heutige Stand. Was hier rot ist,
ist ein Befund (Konzept `Docu/konzepte/2026-09-20_garmentcode-genesis9-konzept.md`).
"""

import json
import os

from django.test import Client, TestCase

from .kinlandmarken import Kinlandmarken, Rigmasse

#: Vorlage, Form (None = Vorgabe des Katalogs) -> Panelfamilien, die da sein
#: MÜSSEN, und die NICHT da sein dürfen.
SCHNITTE = [
    ('oberteil', 't-shirt', {'torso', 'sleeve'}, {'pant', 'skirt', 'briefs'}),
    ('oberteil', 't-shirt-anliegend', {'torso', 'sleeve'}, {'pant', 'skirt'}),
    ('oberteil', 'hemd', {'torso', 'sleeve'}, {'pant', 'skirt'}),
    ('oberteil', 'traegertop', {'torso'}, {'sleeve', 'pant', 'skirt'}),
    ('hose', None, {'pant', 'wb'}, {'torso', 'skirt', 'briefs'}),
    ('shorts', None, {'pant', 'wb'}, {'torso', 'skirt', 'briefs'}),
    ('rock', 'bleistiftrock', {'skirt', 'wb'}, {'pant', 'torso'}),
    ('rock', 'kreisrock', {'skirt', 'wb'}, {'pant', 'torso'}),
    ('rock', 'stufenrock', {'skirt', 'wb'}, {'pant', 'torso'}),
    ('rock', 'godetrock', {'skirt', 'wb'}, {'pant', 'torso'}),
    ('rock', 'faltenrock', {'skirt', 'wb'}, {'pant', 'torso'}),
    ('rock', 'asymmetrischer-rock', {'skirt', 'wb'}, {'pant', 'torso'}),
    ('kleid', 'kleid', {'torso', 'sleeve', 'skirt'}, {'pant', 'briefs'}),
    ('kleid', 'sommerkleid', {'torso', 'skirt'}, {'sleeve', 'pant'}),
    ('kleid', 'abendkleid', {'torso', 'skirt'}, {'sleeve', 'pant'}),
    ('anzug', 'jumpsuit', {'torso', 'sleeve', 'pant'}, {'skirt', 'briefs'}),
    ('unterwaesche', 'bh', {'torso'}, {'sleeve', 'pant', 'skirt', 'briefs'}),
    ('unterwaesche', 'hoeschen', {'briefs', 'wb'}, {'pant', 'torso', 'skirt'}),
    ('unterwaesche', 'body', {'torso', 'briefs'}, {'sleeve', 'pant', 'skirt'}),
    ('schuh', 'ballerina', {'sohle', 'blatt'}, {'schaft', 'torso', 'pant'}),
    ('schuh', 'pumps', {'sohle', 'blatt'}, {'schaft'}),
    ('schuh', 'stiefel', {'sohle', 'blatt', 'schaft'}, {'torso', 'pant'}),
    ('schuh', 'socke', {'sohle', 'blatt', 'schaft'}, {'torso'}),
]
FAMILIEN = ('torso', 'sleeve', 'pant', 'skirt', 'briefs', 'wb', 'sohle', 'blatt', 'schaft')

CM = 0.01


class GarmentcodeVersprechenTest(TestCase):
    u"""Kin (Genesis 9), Fixture `Assets/GarmentCode/test/gemeinsam_kin`."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.regler_figur = Kinlandmarken.regler()
        cls.mark = Kinlandmarken.holen()
        cls.klient = Client()

    # ------------------------------------------------------------ Helfer

    def _figur(self, **mehr):
        daten = {'figurart': 'genesis9', 'geschlecht': 'female', 'morphs': '{}',
                 'regler_figur': json.dumps(self.regler_figur)}
        daten.update(mehr)
        return daten

    def _schnitt(self, vorlage, form, name):
        from GarmentCode.formpresets import Formpresets
        werte = {}
        if form:
            werte = next(f['werte'] for f in Formpresets.FORMEN[vorlage] if f['alias'] == form)
        antwort = self.klient.post('/api/garmentcode/erzeugen/', self._figur(
            vorlage=vorlage, regler=json.dumps(dict(werte)), name=name)).json()
        self.assertNotIn('fehler', antwort, (vorlage, form, antwort))
        return antwort

    def _drape(self, vorlage, regler, name, **fein):
        schnitt = self.klient.post('/api/garmentcode/erzeugen/', self._figur(
            vorlage=vorlage, regler=json.dumps(regler), name=name)).json()
        self.assertNotIn('fehler', schnitt, (vorlage, schnitt))
        daten = self._figur(spezifikation=schnitt['spezifikation'],
                            hautabstand_mm='1.0', aufloesung='1.0',
                            anfrage='versprechen-%s' % name)
        daten.update({k: str(v) for k, v in fein.items()})
        antwort = self.klient.post('/api/garmentcode/drapieren/', daten)
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        netz = antwort.json()
        self.assertNotIn('fehler', netz, (vorlage, netz))
        datei = self.klient.get(netz['rig_url'])
        rig = json.loads(b''.join(datei.streaming_content))
        return Rigmasse(rig['punkte'])

    def _zwischen(self, wert, unten, oben, was):
        self.assertIsNotNone(wert, was)
        self.assertTrue(unten <= wert <= oben,
                        '%s: %.3f m, erwartet %.3f..%.3f' % (was, wert, unten, oben))

    # --------------------------------------------------- 1. Schnitte (2D)

    def test_jede_form_baut_die_versprochenen_panels(self):
        befunde = []
        for vorlage, form, muss, darf_nicht in SCHNITTE:
            antwort = self._schnitt(vorlage, form, 'versprechen_%s_%s' % (vorlage, form or 'vorgabe'))
            if antwort.get('selbstdurchdringend'):
                befunde.append('%s/%s: Selbstschnitt' % (vorlage, form))
            ordner = antwort['ordner']
            spez = [d for d in os.listdir(ordner) if d.endswith('_specification.json')]
            panels = json.load(open(os.path.join(ordner, spez[0]), encoding='utf-8'))['pattern']['panels']
            familien = {f for f in FAMILIEN if any(f in name for name in panels)}
            if not muss <= familien:
                befunde.append('%s/%s: fehlt %s (hat %s)'
                               % (vorlage, form, sorted(muss - familien), sorted(familien)))
            if familien & darf_nicht:
                befunde.append('%s/%s: zu viel %s' % (vorlage, form, sorted(familien & darf_nicht)))
        self.assertEqual(befunde, [], '\n'.join(befunde))

    # ------------------------------------------------------- 2. Sitz (3D)

    def test_hose_bund_an_der_taille_saum_ueber_dem_knoechel_beide_beine_gleich(self):
        rig = self._drape('hose', {}, 'versprechen_hose')
        m = self.mark
        self._zwischen(rig.bund(), m['taille'] - 4 * CM, m['taille'] + 4 * CM, 'Bund der Hose')
        self._zwischen(rig.saum(), m['knoechel'], m['knie'], 'Saum der Hose (pants.length 0,85)')
        self.assertLess(abs(rig.saum('links') - rig.saum('rechts')), 1.5 * CM,
                        'Säume ungleich: links %.3f, rechts %.3f' % (rig.saum('links'), rig.saum('rechts')))

    def test_shorts_enden_ueber_dem_knie(self):
        rig = self._drape('shorts', {}, 'versprechen_shorts')
        m = self.mark
        self._zwischen(rig.saum(), m['knie'] + 3 * CM, m['schritt'], 'Saum der Shorts (pants.length 0,35)')
        self.assertLess(abs(rig.saum('links') - rig.saum('rechts')), 1.5 * CM)

    def test_leggings_saum_am_knoechel_beide_beine_gleich(self):
        rig = self._drape('hose', {'pants.length': 0.9, 'pants.flare': 0.5},
                          'versprechen_leggings', anliegen_mm=2.0)
        m = self.mark
        self._zwischen(rig.saum(), m['knoechel'] - 2 * CM, m['knoechel'] + 8 * CM, 'Saum der Leggings')
        self.assertLess(abs(rig.saum('links') - rig.saum('rechts')), 1.5 * CM,
                        'Säume ungleich: links %.3f, rechts %.3f' % (rig.saum('links'), rig.saum('rechts')))
        self._zwischen(rig.bund(), m['taille'] - 4 * CM, m['taille'] + 4 * CM, 'Bund der Leggings')

    def test_hoeschen_ist_ein_slip_am_schritt(self):
        rig = self._drape('unterwaesche', {'meta.upper': None, 'meta.wb': 'StraightWB',
                                           'meta.bottom': 'Briefs', 'briefs.rise': 0.5,
                                           'briefs.leg_cut': 0.6}, 'versprechen_hoeschen')
        m = self.mark
        self._zwischen(rig.mitte_unten(), m['schritt'] - 2 * CM, m['schritt'] + 4 * CM, 'Zwickel des Slips')
        # Kein Hosenbein: neben der Mitte (|x| > 9 cm) haengt nichts unter den
        # Schritt — ein Bein der kuerzesten Hose reichte dort 5 cm tiefer —,
        # und der Beinausschnitt steigt zur Seite (|x| 15-18 cm) um mindestens
        # 3 cm ueber den Zwickel. Gemessen 20.09.2026 an Kin: Seite 0,860,
        # Zwickel 0,815 (4,5 cm), tiefster Punkt neben der Mitte 0,827.
        self.assertGreater(rig.seite_unten(0.09), m['schritt'] - 2 * CM,
                           'neben der Mitte hängt Stoff unter den Schritt — ein Hosenbein')
        self.assertGreater(rig.streifen_unten(0.15, 0.18) - rig.mitte_unten(), 3 * CM,
                           'der Beinausschnitt steigt zur Seite nicht an')
        self._zwischen(rig.bund(), m['schritt'] + 8 * CM, m['taille'] - 3 * CM, 'Bund des Slips (Hüfte)')

    def test_bh_endet_unter_der_brust(self):
        rig = self._drape('unterwaesche', {}, 'versprechen_bh')
        m = self.mark
        self._zwischen(rig.saum(), m['taille'], m['brust'], 'Unterkante des BH')
        self.assertLess(rig.bund(), m['schulter'] + 2 * CM, 'der BH reicht über die Schulter')

    def test_tshirt_endet_zwischen_schritt_und_taille(self):
        rig = self._drape('oberteil', {}, 'versprechen_tshirt')
        m = self.mark
        self._zwischen(rig.saum(), m['schritt'], m['taille'] + 2 * CM, 'Saum des T-Shirts')

    def test_bleistiftrock_bund_taille_saum_am_knie(self):
        rig = self._drape('rock', {}, 'versprechen_rock')
        m = self.mark
        self._zwischen(rig.bund(), m['taille'] - 4 * CM, m['taille'] + 4 * CM, 'Bund des Rocks')
        self._zwischen(rig.saum(), m['knie'] - 12 * CM, m['knie'] + 12 * CM, 'Saum des Bleistiftrocks')

    def test_kleid_reicht_von_der_schulter_bis_zum_knie(self):
        rig = self._drape('kleid', {}, 'versprechen_kleid')
        m = self.mark
        self.assertGreater(rig.bund(), m['brust'], 'das Kleid reicht nicht bis über die Brust')
        self._zwischen(rig.saum(), m['knie'] - 12 * CM, m['knie'] + 12 * CM, 'Saum des Kleids')
