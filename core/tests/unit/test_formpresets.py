# -*- coding: utf-8 -*-
u"""Rock und Schuh als je EIN Katalogstueck, die Arten als Formen.

WARUM (11.09.2026, Edgar: „fasse die GarmenCodes zusammen: Alle Roecke zu
einem, und alles was bisher drin war z.B: Bleistiftrock zu einem Preset
(wie bei Hose - Leggins). alle Schuhe zu einem, und z.B: Slipper und die
anderen als Presets (mit Checkbox)")
======================================================================
Eine Form wechselt den Baustein (`meta.bottom`, `meta.feet`) — das geht
ueber denselben Weg wie jeder Reglerwert (`Regler.anwenden`), deshalb muss
der Entwurf mit den Werten einer Form derselbe sein wie frueher der
Katalogeintrag. Die alten Namen bleiben als Aliase, weil `vorbilder.json`,
die Schuhdeutung und gespeicherte Szenen sie nennen.
"""
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.formpresets import Formpresets      # noqa: E402
from GarmentCode.katalog import Katalog              # noqa: E402
from GarmentCode.regler import Regler                # noqa: E402
from GarmentCode.vorbildpresets import Vorbildpresets  # noqa: E402

ROECKE = {'bleistiftrock': ('PencilSkirt', 'FittedWB'),
          'kreisrock': ('SkirtCircle', 'StraightWB'),
          'stufenrock': ('SkirtLevels', 'StraightWB'),
          'godetrock': ('GodetSkirt', 'StraightWB'),
          'faltenrock': ('SkirtManyPanels', 'StraightWB'),
          'asymmetrischer-rock': ('AsymmSkirtCircle', 'StraightWB')}


class FormpresetsTest(SimpleTestCase):

    databases = []

    def test_der_katalog_fuehrt_einen_rock_und_die_alten_namen_als_aliase(self):
        namen = [e['name'] for e in Katalog.liste()]
        self.assertIn('rock', namen)
        for alt in ROECKE:
            self.assertNotIn(alt, namen)
            self.assertTrue(Katalog.kennt(alt))
        self.assertEqual(Katalog.aufloesen('kreisrock'),
                         ('rock', {'meta.bottom': 'SkirtCircle', 'meta.wb': 'StraightWB'}))
        with self.assertRaises(KeyError):
            Katalog.aufloesen('gibtsnicht')

    def test_jede_form_setzt_den_baustein_wie_der_alte_eintrag(self):
        for alt, (bottom, wb) in ROECKE.items():
            entwurf = Katalog.entwurf(alt)
            self.assertEqual(entwurf['meta']['bottom']['v'], bottom, alt)
            self.assertEqual(entwurf['meta']['wb']['v'], wb, alt)
            self.assertIsNone(entwurf['meta']['upper']['v'])
        # Und ueber den Reglerweg, wie das Kaestchen es tut:
        entwurf = Katalog.entwurf('rock', Formpresets.werte('form_faltenrock'))
        self.assertEqual(entwurf['meta']['bottom']['v'], 'SkirtManyPanels')

    def test_die_formen_stehen_vor_der_passform_und_eine_ist_gehakt(self):
        presets = Katalog.passform('rock')
        formen = [p for p in presets if p.get('form')]
        self.assertEqual([p['titel'] for p in formen],
                         ['Bleistiftrock', 'Kreisrock', 'Stufenrock', 'Godetrock',
                          'Faltenrock', 'Asymmetrischer Rock'])
        self.assertEqual([p['gehakt'] for p in formen],
                         [True, False, False, False, False, False])
        self.assertTrue(all(p['gruppe'] == 'passform' for p in formen))
        # Die Passform der Kreisroecke ist dabei, obwohl die Vorgabe der
        # Bleistiftrock ist — sie gilt fuer eine erreichbare Form.
        self.assertIn('Weit schwingend', [p['titel'] for p in presets])
        self.assertEqual(presets[:len(formen)], formen)

    def test_der_rock_zeigt_die_gruppen_aller_formen(self):
        gruppen = [g['gruppe'] for g in Katalog.regler('rock')]
        for gruppe in ('waistband', 'pencil-skirt', 'flare-skirt', 'godet-skirt',
                       'skirt', 'levels-skirt'):
            self.assertIn(gruppe, gruppen)
        # Ein Kleid bleibt, was es war: nur seine eigenen Gruppen.
        self.assertNotIn('flare-skirt', [g['gruppe'] for g in Katalog.regler('kleid')])
        self.assertEqual(Katalog.varianten('kleid'), [])

    def test_die_vorbilder_der_alten_eintraege_gehoeren_dem_stueck(self):
        eintraege = Vorbildpresets.alle()
        if not eintraege.get('stiefel') or not eintraege.get('bleistiftrock'):
            self.fail('vorbilder.json ohne stiefel/bleistiftrock — Messlauf noetig')
        schuhe = Vorbildpresets.fuer('schuh')
        self.assertGreaterEqual(len(schuhe), len(eintraege['stiefel']))
        stiefel = [p for p in schuhe if p['werte'].get('meta.feet') == 'Stiefel']
        self.assertTrue(stiefel)
        self.assertIn('boot.height', stiefel[0]['werte'])
        roecke = Vorbildpresets.fuer('rock')
        self.assertTrue(all(p['werte'].get('meta.bottom') for p in roecke))

    def test_die_schuhformen_nehmen_fremde_regler_zurueck(self):
        ballerina = next(p for p in Katalog.passform('schuh') if p['titel'] == 'Ballerina')
        for pfad in ('shoe.heel', 'shoe.platform', 'shoe.toe_spring', 'boot.height'):
            self.assertIn(pfad, ballerina['zurueck'])
        self.assertNotIn('shoe.opening', ballerina['zurueck'])
        # Werte einer Form greifen ueber `Regler.anwenden`, auch `meta.feet`.
        entwurf = Katalog.entwurf('schuh')
        self.assertEqual(Regler.anwenden(entwurf, Formpresets.werte('form_stiefel')), 3)
        self.assertEqual(entwurf['meta']['feet']['v'], 'Stiefel')
