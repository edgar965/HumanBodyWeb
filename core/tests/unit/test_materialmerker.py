# -*- coding: utf-8 -*-
u"""Die Farbe eines Garment-Fit-Stücks muss dort ankommen, wo gespeichert wird.

DER BEFUND (Edgar, 09.09.2026: „farbe der Schuhe wird nicht gespeichert")
========================================================================
Ein Klick auf ein Stück aus Garment Fit (`gar_…`) öffnet den Reiter „Modell"
(`Reiterzuordnung.VORGABE`), und dort steht der Block „Garment Eigenschaften"
mit Farbe, Rauheit und Metallgrad. Die drei Bedienungen schrieben
ausschliesslich in `mesh.material` — nie in `inst.garmentState[key]`.

Gespeichert wird `garmentState` (`character.js toJSON` liest `st.color`). Die
eingestellte Farbe war also zu sehen und stand nirgends, wo das Speichern
hinsieht: kein Fehler, keine Meldung, und der Farbwähler zeigte sie beim
nächsten Anwählen wieder falsch an, weil auch er aus `garmentState` liest.

DER BELEG liegt in Edgars eigener Datei `HumanBody/data/models/
FemaleGarmentCode.json`. Die Schuhe (`shoes/toigo_mj_cloth_shoes`) tragen dort

    [0.07421356837213867, 0.09989872823822872, 0.21586050010324417]

und das ist nicht irgendeine Farbe: Es ist `#4d5980` — also
`Kleideranpassung.VORGABE_FARBE` — in linearem sRGB, auf zehn Stellen genau.
`test_die_gespeicherte_farbe_war_die_vorgabe` rechnet das nach, damit die
Aussage nicht auf einem Augenmass beruht.

Zwei andere Stellen hatten den Weg längst: der Assets-Reiter über
`Stueckbedienung.nachMaterial` -> `_saveSelectedGarmentState`, die Modell-Seite
über `Kleiderbedienung._farbe`. Nur dieser Block nicht.

Die Fälle prüfen den Quelltext, nicht das Verhalten im Browser: Das Modul hängt
an `three` und am DOM und ist in node nicht ladbar.
"""
import io

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = settings.BASE_DIR


def _quelle(*teile):
    return io.open(WURZEL.joinpath(*teile), encoding='utf-8').read()


def _merker():
    return _quelle('static', 'viewer', 'scene', 'materialmerker.js')


def _prop():
    return _quelle('static', 'viewer', 'scene', 'prop_garments.js')


def _linear(kanal):
    u"""sRGB-Kanal 0..1 in linearen Raum — die Umrechnung, die THREE.Color
    beim Setzen aus `#rrggbb` macht (ColorManagement, Three r152+)."""
    if kanal <= 0.04045:
        return kanal / 12.92
    return ((kanal + 0.055) / 1.055) ** 2.4


class DerZustandBekommtDieFarbeTest(SimpleTestCase):

    databases = set()

    def test_der_reiter_verdrahtet_den_merker(self):
        quelle = _prop()
        self.assertIn("new Materialmerker('prop-garment').verdrahten();", quelle)
        self.assertIn("import { Materialmerker } from './materialmerker.js';",
                      quelle)

    def test_kein_material_ohne_gedaechtnis_mehr(self):
        u"""Die drei alten Hörer schrieben ins Material und sonst nirgends.

        Solange eine solche Zeile dasteht, ist der Befund wieder möglich.
        """
        quelle = _prop()
        self.assertNotIn('sel.mesh.material.color.set(colorPicker.value)', quelle)
        self.assertNotIn("sel.mesh.material.roughness = _sliderVal(", quelle)
        self.assertNotIn("sel.mesh.material.metalness = _sliderVal(", quelle)

    def test_gemerkt_wird_in_den_zustand_des_stuecks(self):
        quelle = _merker()
        self.assertIn('auswahl.inst.garmentState[auswahl.key]', quelle)
        self.assertIn('Object.assign(zustand, werte);', quelle)

    def test_die_farbe_geht_als_drei_kanaele_mit(self):
        u"""`Kleidungszustand` führt sie so — ein Hexwort passte nicht dazu."""
        self.assertIn('color: [farbe.r, farbe.g, farbe.b]', _merker())

    def test_rauheit_und_metallgrad_gehen_denselben_weg(self):
        quelle = _merker()
        self.assertIn("static ANTEILE = [['roughness', 'roughness'], "
                      "['metalness', 'metalness']];", quelle)
        self.assertIn('this.merken({ [feld]: wert / 100 });', quelle)


class OhneAuswahlPassiertNichtsTest(SimpleTestCase):
    u"""Dieselbe Vorsicht wie bei den GarmentCode-Farben am selben Tag: Ein
    Feld, das ohne gewähltes Stück feuert, darf nichts anfassen."""

    databases = set()

    def test_ohne_stueck_wird_nichts_geschrieben(self):
        self.assertIn('if (!zustand) return false;', _merker())

    def test_das_nachziehen_der_anzeige_gilt_nicht_als_eingabe(self):
        self.assertIn('if (state._syncingSliders) return;', _merker())


class DerBefundIstBelegtTest(SimpleTestCase):

    databases = set()

    def test_die_gespeicherte_farbe_war_die_vorgabe(self):
        u"""#4d5980 in linear — auf drei Stellen genau der gespeicherte Wert.

        Ohne diese Rechnung wäre „die Schuhe trugen die Vorgabefarbe" eine
        Behauptung; mit ihr ist es eine Messung.
        """
        gespeichert = [0.07421356837213867, 0.09989872823822872,
                       0.21586050010324417]
        vorgabe = [_linear(kanal / 255.0) for kanal in (0x4d, 0x59, 0x80)]
        for war, soll in zip(gespeichert, vorgabe):
            self.assertAlmostEqual(war, soll, places=3)

    def test_der_befund_steht_im_modulkopf(self):
        quelle = _merker()
        self.assertIn('farbe der Schuhe wird nicht gespeichert', quelle)
        self.assertIn('0.0742', quelle)


class DieKetteZumSpeichernTest(SimpleTestCase):
    u"""Das Feld, das der Merker schreibt, ist genau das, was gespeichert wird.

    UND ES SIND ZWEI WEGE. „Szene speichern" ging über `character.js toJSON`
    und rechnete den Zustand ein; „Modell speichern" ging über
    `Szenenausgabe._zusammengestellt` und nahm `figur.garments` ROH. Im
    Browser gemessen (09.09.2026): Zustand [1, 0, 0], gespeicherte Datei
    [0.0742, 0.0999, 0.2159]. Beide nehmen jetzt `Garderobenstand`.
    """

    databases = set()

    def test_beide_speicherwege_rechnen_den_zustand_ein(self):
        charakter = _quelle('static', 'viewer', 'scene', 'character.js')
        ausgabe = _quelle('static', 'viewer', 'scene', 'szenenausgabe.js')
        self.assertIn('Garderobenstand.liste(this)', charakter)
        self.assertIn('garments: Garderobenstand.liste(figur),', ausgabe)
        self.assertNotIn('garments: figur.garments', ausgabe)

    def test_der_garderobenstand_liest_den_zustand(self):
        stand = _quelle('static', 'viewer', 'scene', 'garderobenstand.js')
        self.assertIn('zustaende[Garderobenstand.VORSILBE + stueck.id]', stand)
        self.assertIn('Kleidungszustand.ausJson(zustand).zuJson()', stand)

    def test_ein_stueck_ohne_zustand_bleibt_stehen(self):
        u"""Sonst überschriebe das Speichern die Werte einer älteren Datei
        mit Vorgaben, nur weil das Stück in dieser Sitzung nie gewählt war."""
        self.assertIn('if (!zustand) return stueck;',
                      _quelle('static', 'viewer', 'scene', 'garderobenstand.js'))

    def test_der_farbwaehler_zeigt_den_zustand_an(self):
        u"""Die Gegenrichtung — sonst stünde im Feld etwas anderes als im
        Netz, und genau daran war der Befund nicht zu sehen."""
        self.assertIn("const colorEl = document.getElementById('prop-garment-color');",
                      _prop())


class DieRegionsverschiebungKommtAnTest(SimpleTestCase):
    u"""Beim Laden reichte der Zustand allein nicht.

    `Charakterzubehoer.kleidung` rechnete die Regionsgewichte
    (`_computeGarmentRegionWeights`), wandte die Verschiebung aber nie an. Im
    Browser gemessen (09.09.2026): `regionBottom` 0,07 im Zustand, das Netz
    unverschoben — 0 statt 70 mm. Nach der Behebung 70 mm.

    Dazu kam die REIHENFOLGE: `_applyGarmentRegionOffsets` liest
    `inst.garmentState[key]`, das vorher erst DANACH gesetzt wurde.
    """

    databases = set()

    def _zubehoer(self):
        return _quelle('static', 'viewer', 'scene', 'charakter_zubehoer.js')

    def test_die_verschiebung_wird_angewandt(self):
        self.assertIn('_applyGarmentRegionOffsets(inst, key);', self._zubehoer())

    def test_der_zustand_steht_vor_der_verschiebung(self):
        quelle = self._zubehoer()
        zustand = quelle.index('inst.garmentState[key] = Kleidungszustand')
        anwenden = quelle.index('_applyGarmentRegionOffsets(inst, key);')
        self.assertLess(zustand, anwenden)

    def test_die_verschiebungen_werden_ueberhaupt_gespeichert(self):
        u"""Die feste Feldliste in `toJSON` führte die fünf Regionen NICHT.

        Über `Kleidungszustand.zuJson()` sind sie dabei — sonst wäre die
        Anwendung beim Laden wirkungslos, weil der Wert nie in der Datei
        stünde.
        """
        zustand = _quelle('static', 'viewer', 'scene', 'kleidungszustand.js')
        # Die Feldnamen entstehen als `'region' + region` — wörtlich steht
        # `regionTop` nirgends.
        self.assertIn("REGIONEN = ['Top', 'Upper', 'Mid', 'Lower', 'Bottom']",
                      zustand)
        self.assertIn("daten['region' + region] = this['region' + region];",
                      zustand)
        self.assertIn('Kleidungszustand.ausJson(zustand).zuJson()',
                      _quelle('static', 'viewer', 'scene', 'garderobenstand.js'))

    def test_kein_stiller_fang_mehr_in_dieser_datei(self):
        u"""`console.error` sieht niemand — genau daran hat der
        ReferenceError der Schuhe zwölf Tage überlebt."""
        self.assertNotIn('console.error', self._zubehoer())
