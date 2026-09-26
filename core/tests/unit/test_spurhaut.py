# -*- coding: utf-8 -*-
"""BVH Studio: Die Haut unter der Kleidung wird auch dort nicht gezeichnet.

WARUM (Edgar, 11.09.2026: „die haut ist immer noch sichtbar im BVH Studio,
spiele die Animation ab"): Die Hautmaske vom selben Tag hing am
`Stueckereignis` der Szene-Seite; das Studio baut seine Figur über
`Spurfigur`/`Spurzubehoer` und zeichnete den ganzen Körper.

Geprüft am Quelltext (die Rechnung selbst prüfen `test_js_hautmaske`,
`test_js_lagenmaske`, `test_hautverdeckung`):

1. `Modellzubehoer` (seit 13.09.2026 das Zubehör JEDER Seite, Studio wie
   Theatre) ruft `Figurhaut.anwenden` NACH dem Zubehör — vorher gäbe es
   keine Stücke, und die Maske wäre leer, ohne Fehler.
2. `Figurhaut` rechnet mit denselben Bausteinen wie die Szene (Hautmaske,
   Lagenmaske, Hauteinzug) und liest die Stücke an `isGarment`; das
   Studio baut über `HumanbodyModell`, das dieses Zubehör nimmt.
3. MakeHuman-Stücke tragen `isGarment` (GarmentCode-Stücke tun es schon);
   Haare nicht — sie sind kein Stoff.
4. `Hauteinzug` liegt in `gemeinsam/` und holt Three.js direkt, nicht über
   den Szene-Zustand — sonst zöge das Studio die halbe Szene-Seite mit.

Sabotage-Gegenprobe: `Figurhaut.anwenden` in `Modellzubehoer.laden` vor
`this.haare()` → Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STUDIO = Jsmodul.VIEWER / 'studio'
GEMEINSAM = Jsmodul.VIEWER / 'gemeinsam'
SZENE = Jsmodul.VIEWER / 'scene'


class SpurhautTest(SimpleTestCase):
    databases = set()

    def test_die_figur_wird_nach_dem_zubehoer_maskiert(self):
        zubehoer = SpurhautTest._lies_modul(GEMEINSAM, 'modellzubehoer.js')
        self.assertIn("import { Figurhaut } from './figurhaut.js';", zubehoer)
        laden = zubehoer.index('async laden() {')
        rumpf = zubehoer[laden : zubehoer.index('return this;', laden)]
        maske = rumpf.index('Figurhaut.anwenden(')
        for schritt in ('this.kleidungsstueck(', 'this.garmentcode()', 'this.haare()'):
            self.assertLess(rumpf.index(schritt), maske, 'die Maske muss NACH dem Zubehör laufen: ' + schritt)
        # Seit 15.09.2026 baut `spurfigurarten.js` die Figur je Art; HumanBody dort.
        figur = SpurhautTest._lies_modul(STUDIO, 'spurfigurarten.js')
        self.assertIn("import { HumanbodyModell } from '../gemeinsam/humanbodymodell.js';", figur)
        self.assertIn('await modell.bauen({', figur)

    def test_spurhaut_rechnet_wie_die_szene(self):
        """Die Rechnung liegt seit dem 12.09.2026 in `gemeinsam/figurhaut.js`
        (die Ergebnisseite braucht dieselbe Maske); `Spurhaut` erbt sie."""
        haut = SpurhautTest._lies_modul(GEMEINSAM, 'figurhaut.js')
        for baustein in (
            'Hautmaske.verdeckt(',
            'Hautmaske.indexOhne(',
            'Lagenmaske.verdeckt(',
            'Hauteinzug.setzen(',
            'Saumschnitt.kanten(',
            'userData.indexVoll',
            'userData?.isGarment',
        ):
            self.assertIn(baustein, haut, baustein)
        self.assertIn("from './hauteinzug.js'", haut)
        modell = SpurhautTest._lies_modul(GEMEINSAM, 'humanbodymodell.js')
        self.assertIn('new Modellzubehoer(this, haarfarben).laden()', modell)
        self.assertFalse((STUDIO / 'spurhaut.js').exists())
        self.assertFalse((STUDIO / 'spurzubehoer.js').exists())

    def test_die_ergebnisseite_maskiert_nach_dem_binden(self):
        """Edgar, 12.09.2026: „bei einer animation mit Female2 scheint die
        Haut durch das Kleid" — dieselbe Lücke wie im Studio am 11.09."""
        stuecke = SpurhautTest._lies_modul(Jsmodul.VIEWER / 'result_character', 'garmentcode_stuecke.js')
        self.assertIn("import { Figurhaut } from '../gemeinsam/figurhaut.js';", stuecke)
        binden = stuecke.index('.binden(gruppe, state.bodyMesh)')
        maske = stuecke.index('GarmentcodeStuecke.hautMaskieren();')
        self.assertLess(binden, maske, 'die Maske muss NACH dem Binden laufen')
        self.assertIn('Figurhaut.anwenden(GarmentcodeStuecke.figur())', stuecke)
        self.assertIn('Figurhaut.aufheben(GarmentcodeStuecke.figur())', stuecke)

    def test_makehuman_stuecke_tragen_isgarment_haare_nicht(self):
        zubehoer = SpurhautTest._lies_modul(GEMEINSAM, 'modellzubehoer.js')
        von = zubehoer.index('async kleidungsstueck(kleid) {')
        stueck = zubehoer[von : zubehoer.index('async garmentcode() {')]
        self.assertIn('netz.userData.isGarment = true', stueck)
        von = zubehoer.index('async haare() {')
        haar = zubehoer[von : zubehoer.index('_kopfknochen() {')]
        self.assertNotIn('isGarment', haar)
        self.assertIn('isHair = true', haar)
        stueck = SpurhautTest._lies_modul(GEMEINSAM, 'garmentcodestueck.js')
        self.assertIn('isGarment: true', stueck)

    def test_hauteinzug_liegt_in_gemeinsam_ohne_szenenzustand(self):
        self.assertFalse((SZENE / 'hauteinzug.js').exists())
        einzug = SpurhautTest._lies_modul(GEMEINSAM, 'hauteinzug.js')
        self.assertIn("import * as THREE from 'three';", einzug)
        self.assertNotIn("from './state.js'", einzug)
        self.assertNotIn("from '../charakter/", einzug)
        # `hautverdeckung.js` liegt seit dem 21.09.2026 in `gemeinsam/` (alle Seiten).
        self.assertIn("from './hauteinzug.js'", SpurhautTest._lies_modul(GEMEINSAM, 'hautverdeckung.js'))
        self.assertIn("from '../gemeinsam/hauteinzug.js'", SpurhautTest._lies_modul(SZENE, 'lagenverdeckung.js'))

    @staticmethod
    def _lies_modul(ordner, name):
        return (ordner / name).read_text(encoding='utf-8')
