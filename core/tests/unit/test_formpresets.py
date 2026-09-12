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

    databases = set()

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
        # Eine Hose bleibt, was sie war: nur ihre eigenen Gruppen.
        self.assertNotIn('flare-skirt', [g['gruppe'] for g in Katalog.regler('hose')])
        self.assertEqual(Katalog.varianten('hose'), [])

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
        # Baustein, Schafthöhe, Weite, Fersenhöhe (der Stiefel braucht 0,6).
        self.assertEqual(Regler.anwenden(entwurf, Formpresets.werte('form_stiefel')), 4)
        self.assertEqual(entwurf['meta']['feet']['v'], 'Stiefel')

    # ---------------------------------------- Oberteil, Kleid, Anzug, Unterwäsche

    def test_oberteil_kleid_anzug_und_unterwaesche_sind_je_ein_stueck(self):
        u"""Edgar, 11.09.2026: „packe auch noch Kleid mit Sommerkleid,
        Abendkleid zusammen. Erstelle eine neue Kategorie: Anzug wo
        Jumpsuit hineinkommt. erstelle Oberteil wo T-Shirt, T-Shirt
        (anliegend) und Hemd hineinkommen, Trägertop. Erstelle
        Unterwäsche"."""
        namen = [e['name'] for e in Katalog.liste()]
        self.assertEqual(namen, ['oberteil', 'hose', 'shorts', 'rock', 'kleid',
                                 'anzug', 'unterwaesche', 'schuh'])
        erwartet = {
            'oberteil': ['T-Shirt', 'T-Shirt (anliegend)', 'Hemd (tailliert)',
                         u'Trägertop'],
            'kleid': ['Kleid', 'Sommerkleid', 'Abendkleid'],
            'anzug': ['Jumpsuit'],
            'unterwaesche': ['BH', u'Höschen', 'Body'],
        }
        for stueck, titel in erwartet.items():
            formen = [p for p in Katalog.passform(stueck) if p.get('form')]
            self.assertEqual([p['titel'] for p in formen], titel, stueck)
            self.assertEqual(sum(1 for p in formen if p['gehakt']), 1, stueck)

    def test_die_alten_namen_sind_aliase(self):
        namen = [e['name'] for e in Katalog.liste()]
        for alt in ('t-shirt', 't-shirt-anliegend', 'hemd', 'traegertop',
                    'sommerkleid', 'abendkleid', 'jumpsuit'):
            self.assertNotIn(alt, namen)
            self.assertTrue(Katalog.kennt(alt), alt)

    def test_die_aliase_bauen_denselben_entwurf_wie_vorher(self):
        hemd = Katalog.entwurf('hemd')
        self.assertEqual(hemd['meta']['upper']['v'], 'FittedShirt')
        self.assertEqual(hemd['collar']['f_collar']['v'], 'VNeckHalf')
        self.assertEqual(hemd['sleeve']['length']['v'], 1.0)
        sommer = Katalog.entwurf('sommerkleid')
        self.assertEqual((sommer['meta']['upper']['v'], sommer['meta']['bottom']['v'],
                          sommer['sleeve']['sleeveless']['v']),
                         ('Shirt', 'SkirtCircle', True))
        jumpsuit = Katalog.entwurf('jumpsuit')
        self.assertEqual((jumpsuit['meta']['wb']['v'], jumpsuit['meta']['bottom']['v'],
                          jumpsuit['pants']['length']['v']), ('FittedWB', 'Pants', 0.85))
        bh = Katalog.entwurf('unterwaesche')
        self.assertEqual((bh['meta']['upper']['v'], bh['meta']['bottom']['v'],
                          bh['shirt']['length']['v']), ('FittedShirt', None, 0.5))
        self.assertEqual(Katalog.entwurf('hoeschen')['meta']['bottom']['v'], 'Pants')
        # Ein Trägertop nimmt die Ärmellänge des Hemds zurück.
        top = next(p for p in Katalog.passform('oberteil') if p['titel'] == u'Trägertop')
        self.assertIn('sleeve.length', top['zurueck'])

    def test_die_vorbilder_folgen_dem_zweck_nicht_der_deutung(self):
        u"""Edgar: „Erstelle Unterwäsche, wo du alles mit Bra und Höschen
        hineinpackst … Unter Kleid sind Anzüge die dahin verschoben werden
        sollen, «Rei Ayanami», «Cyborg Suite», «Yoko Tsuno»"."""
        from GarmentCode.vorbildgruppen import Vorbildgruppen
        self.assertEqual(Vorbildgruppen.ziel('t-shirt', 'Sport-Bra01'),
                         ('unterwaesche', 'form_bh', ('shirt.length',)))
        self.assertEqual(Vorbildgruppen.ziel('bleistiftrock', 'Female Panties 01'),
                         ('unterwaesche', 'form_hoeschen', ()))
        self.assertEqual(Vorbildgruppen.ziel('kleid', 'F Bikini 01')[:2],
                         ('unterwaesche', 'form_body'))
        for titel in ('Rei Ayanami', 'Cyborg Suit', 'Yoko Tsuno'):
            self.assertEqual(Vorbildgruppen.ziel('bleistiftrock', titel)[:2],
                             ('anzug', 'form_jumpsuit'), titel)
        self.assertEqual(Vorbildgruppen.ziel('kleid', 'Fem Suit')[:2],
                         ('anzug', 'form_jumpsuit'))
        self.assertEqual(Vorbildgruppen.ziel('t-shirt', 'Polo T-Shirt'),
                         ('oberteil', 'form_t_shirt', ()))
        self.assertEqual(Vorbildgruppen.ziel('kleid', 'Dress Shift'),
                         ('kleid', 'form_kleid', ()))
        self.assertEqual(Vorbildgruppen.ziel('hose', 'Stockings')[0], 'hose')

    def test_der_bh_bekommt_die_laenge_der_form(self):
        u"""Nicht die der Deutung (1,0) — die kennt nur die Oberkante."""
        from GarmentCode.vorbildgruppen import Vorbildgruppen
        werte = Vorbildgruppen.werte('t-shirt', 'Sport-Bra01',
                                     {'shirt.length': 1.0, 'sleeve.sleeveless': True})
        self.assertEqual(werte['shirt.length'], 0.5)
        self.assertEqual(werte['meta.upper'], 'FittedShirt')

    def test_jedes_gemessene_vorbild_erscheint_genau_einmal(self):
        alle = Vorbildpresets.alle()
        if not alle:
            self.fail('vorbilder.json fehlt — Messlauf noetig')
        gezaehlt = sum(len([p for p in Vorbildpresets.fuer(e['name'])
                            if p['bild']]) for e in Katalog.liste())
        self.assertEqual(gezaehlt, sum(len(liste) for liste in alle.values()))
        titel = [p['titel'] for p in Vorbildpresets.fuer('unterwaesche')]
        for erwartet in ('Sport-Bra01', 'Female Panties 01', 'String2', 'Frenchbra'):
            self.assertIn(erwartet, titel)
        self.assertIn('Rei Ayanami', [p['titel'] for p in Vorbildpresets.fuer('anzug')])
        self.assertNotIn('Rei Ayanami', [p['titel'] for p in Vorbildpresets.fuer('rock')])
