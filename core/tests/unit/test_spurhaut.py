# -*- coding: utf-8 -*-
u"""BVH Studio: Die Haut unter der Kleidung wird auch dort nicht gezeichnet.

WARUM (Edgar, 11.09.2026: „die haut ist immer noch sichtbar im BVH Studio,
spiele die Animation ab"): Die Hautmaske vom selben Tag hing am
`Stueckereignis` der Szene-Seite; das Studio baut seine Figur über
`Spurfigur`/`Spurzubehoer` und zeichnete den ganzen Körper.

Geprüft am Quelltext (die Rechnung selbst prüfen `test_js_hautmaske`,
`test_js_lagenmaske`, `test_hautverdeckung`):

1. `Spurfigur` ruft `Spurhaut.anwenden` NACH dem Zubehör — vorher gäbe es
   keine Stücke, und die Maske wäre leer, ohne Fehler.
2. `Spurhaut` rechnet mit denselben Bausteinen wie die Szene (Hautmaske,
   Lagenmaske, Hauteinzug) und liest die Stücke an `isGarment`.
3. MakeHuman-Stücke tragen `isGarment` (GarmentCode-Stücke tun es schon);
   Haare nicht — sie sind kein Stoff.
4. `Hauteinzug` liegt in `gemeinsam/` und holt Three.js direkt, nicht über
   den Szene-Zustand — sonst zöge das Studio die halbe Szene-Seite mit.

Sabotage-Gegenprobe: Aufruf in `Spurfigur` entfernt → Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STUDIO = Jsmodul.VIEWER / 'bvh_studio'
GEMEINSAM = Jsmodul.VIEWER / 'gemeinsam'
SZENE = Jsmodul.VIEWER / 'scene'


def _lies_modul(ordner, name):
    return (ordner / name).read_text(encoding='utf-8')


class SpurhautTest(SimpleTestCase):

    databases = set()

    def test_die_figur_wird_nach_dem_zubehoer_maskiert(self):
        figur = _lies_modul(STUDIO, 'spurfigur.js')
        self.assertIn("import { Spurhaut } from './spurhaut.js';", figur)
        zubehoer = figur.index('new Spurzubehoer(this.spur, vorgabe).laden()')
        maske = figur.index('Spurhaut.anwenden(this.spur)')
        self.assertLess(zubehoer, maske, 'die Maske muss NACH dem Zubehör laufen')

    def test_spurhaut_rechnet_wie_die_szene(self):
        haut = _lies_modul(STUDIO, 'spurhaut.js')
        for baustein in ('Hautmaske.verdeckt(', 'Hautmaske.indexOhne(',
                         'Lagenmaske.verdeckt(', 'Hauteinzug.setzen(', 'Hauteinzug.patchen(',
                         'userData.indexVoll', 'userData?.isGarment'):
            self.assertIn(baustein, haut, baustein)
        self.assertIn("from '../gemeinsam/hauteinzug.js'", haut)

    def test_makehuman_stuecke_tragen_isgarment_haare_nicht(self):
        zubehoer = _lies_modul(STUDIO, 'spurzubehoer.js')
        anhaengen = zubehoer[zubehoer.index('_anhaengen(geo, stoff'):]
        anhaengen = anhaengen[:anhaengen.index('_binden(geo, stoff, indizes')]
        self.assertIn('netz.userData.isGarment = true', anhaengen)
        haar = zubehoer[zubehoer.index('_haarteil(geo, stoff)'):zubehoer.index('_kopfknochenNummer()')]
        self.assertNotIn('isGarment', haar)
        stueck = _lies_modul(GEMEINSAM, 'garmentcodestueck.js')
        self.assertIn('isGarment: true', stueck)

    def test_hauteinzug_liegt_in_gemeinsam_ohne_szenenzustand(self):
        self.assertFalse((SZENE / 'hauteinzug.js').exists())
        einzug = _lies_modul(GEMEINSAM, 'hauteinzug.js')
        self.assertIn("import * as THREE from 'three';", einzug)
        self.assertNotIn("from './state.js'", einzug)
        self.assertNotIn("from '../scene/", einzug)
        for name in ('hautverdeckung.js', 'lagenverdeckung.js'):
            self.assertIn("from '../gemeinsam/hauteinzug.js'", _lies_modul(SZENE, name), name)
