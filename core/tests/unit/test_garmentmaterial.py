# -*- coding: utf-8 -*-
u"""Farbe und Material eines GarmentCode-Stücks treffen genau eines.

WARUM DIESE FÄLLE (09.09.2026)
==============================
Edgar, zweimal am selben Tag: „Farben funktioniert immer noch nicht, setzen
die Farben von allen Garments statt einem" und „gerade modell gespeichert
(farbe rot des T-Shirt), neu geladen - Farbe ist weg … die farbe erscheint
im Tab, wird aber nicht auf das Garment angewandt!"

Beides war DERSELBE Fehler, und er sass nicht dort, wo man ihn sucht: Die
Auswahl funktioniert (im Browser über alle drei Wege nachgemessen — Klick
im Bild, Klick in der Teilnetzliste, Aufruf im Code). Der Schaden entstand
OHNE Auswahl.

`GarmentcodeMaterial.anwenden` legte den Reglerstand dann auf ALLE `gc_*`
-Netze der Figur. Und genau diesen Fall stellt das Reitergedächtnis bei
jedem Seitenstart her: Es schreibt den gemerkten Wert in `gc-color` und
feuert `input` (`reitergedaechtnis.js`), während nichts ausgewählt ist.

Im Browser gemessen, ein einziges solches `input`:

    aus der Szene geladen    #dcd8d0, Rauheit 0,85
    danach                   #ff0000, Rauheit 1,0

Die gespeicherte Farbe war weg, bevor sie jemand sehen konnte — kein
Fehler, keine Meldung. Der Regler zeigte sie trotzdem an, weil sein Wert
aus einer anderen Quelle kommt als das Material des Netzes.

Die Fälle prüfen den Quelltext, nicht das Verhalten im Browser: Das Modul
hängt an `three` und ist in node nicht ladbar. Sie halten deshalb genau
die zwei Zusagen fest, die den Befund beheben — dass es ohne Auswahl
aussteigt und dass der Bau ein einzelnes Stück meint.
"""
import io
import re

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = settings.BASE_DIR


def _quelle(*teile):
    return io.open(WURZEL.joinpath(*teile), encoding='utf-8').read()


def _material():
    return _quelle('static', 'viewer', 'scene', 'garmentcode_material.js')


def _drapieren():
    return _quelle('static', 'viewer', 'scene', 'garmentcode_drapieren.js')


class MaterialOhneAuswahlTest(SimpleTestCase):

    databases = set()

    def test_ohne_auswahl_wird_nichts_angefasst(self):
        u"""Der Kern: kein gewähltes Stück, kein Zugriff auf ein Material."""
        quelle = _material()
        self.assertIn('const gewaehlt = GarmentcodeMaterial.gewaehltesStueck',
                      quelle)
        self.assertIn('if (!gewaehlt) return 0;', quelle)

    def test_anwenden_nimmt_keinen_alle_schalter_mehr(self):
        u"""`anwenden(figur, false)` war der Weg in den Fehler.

        Solange die Signatur ihn anbietet, kann ihn jemand wieder benutzen —
        dieselbe Falle wie die Konstante `GLAETTUNG` am selben Tag.
        """
        quelle = _material()
        self.assertNotIn('nurGewaehltes', quelle)
        unterschrift = re.search(r'static anwenden\(([^)]*)\)', quelle)
        self.assertIsNotNone(unterschrift)
        self.assertEqual(unterschrift.group(1).strip(), 'figur')

    def test_es_gibt_keinen_sammler_ueber_alle_stuecke_mehr(self):
        u"""Ohne Sammelliste kann der Stand nicht mehr breit wirken."""
        quelle = _material()
        self.assertNotIn('static stuecke(', quelle)
        self.assertNotIn(".filter((k) => k.startsWith('gc_'))", quelle)

    def test_der_befund_steht_im_modulkopf(self):
        u"""Die gemessenen Werte, damit die nächste Fassung sie kennt."""
        quelle = _material()
        self.assertIn('#dcd8d0', quelle)
        self.assertIn('reitergedaechtnis', quelle)


class MaterialBeimBauenTest(SimpleTestCase):

    databases = set()

    def test_der_bau_faerbt_genau_sein_stueck(self):
        u"""Sonst zieht das zweite Stück die Farbe des ersten mit."""
        quelle = _drapieren()
        self.assertIn('GarmentcodeMaterial.aufStueck(figur, stueck)', quelle)
        self.assertNotIn('GarmentcodeMaterial.anwenden(figur, false)', quelle)

    def test_auf_stueck_greift_ueber_den_schluessel(self):
        u"""Über `clothMeshes` und den `gc_`-Schlüssel — nicht über den Namen
        im Szenengraphen, wo auch Körper und Haare hängen."""
        quelle = _material()
        self.assertIn('static aufStueck(figur, stueck, werte = null)', quelle)
        self.assertIn('GarmentcodeAnziehen.schluessel(stueck)', quelle)


class MaterialUeberlebtNeuEinhaengenTest(SimpleTestCase):
    u"""Der zweite, schwerere Teil desselben Befundes.

    `GarmentcodeAnziehen.einhaengen` baute bei jedem Aufruf ein frisches
    Material mit der Vorgabefarbe. Es läuft aber nicht nur beim Bauen:
    `nachbinden` ruft es für JEDES hängende Stück, sobald das Skelett
    entsteht — und beim Laden einer Szene passiert das direkt NACHDEM die
    gespeicherte Farbe gesetzt wurde.

    Im Browser gemessen: Das Einhängen eines ZWEITEN Stücks setzte das
    erste von #ff0000 auf die Vorgabe #dcd8d0 zurück. Genau das sah Edgar
    als „neu geladen - Farbe ist weg".
    """

    databases = set()

    def _anziehen(self):
        return _quelle('static', 'viewer', 'scene', 'garmentcode_anziehen.js')

    def test_das_bisherige_material_wird_vor_dem_entfernen_gelesen(self):
        u"""`entfernen` gibt das Material frei — danach ist nichts zu holen."""
        quelle = self._anziehen()
        stelle_lesen = quelle.index('Garmentstoff.werte(')
        stelle_entfernen = quelle.index('GarmentcodeAnziehen.entfernen(figur,')
        self.assertLess(stelle_lesen, stelle_entfernen)

    def test_das_neue_material_erbt_die_bisherigen_werte(self):
        quelle = self._anziehen()
        # Seit dem 10.09.2026 kommen die Stoffangaben als zweites Argument
        # dazu (UV und Massstab fuer das Gewebe) — geerbt wird weiter.
        self.assertIn('Garmentstoff.neu(bisher, stoff)', quelle)
        self.assertNotIn('GarmentcodeAnziehen._stoff()', quelle)

    def test_der_stoff_hat_eine_eigene_quelle(self):
        u"""Farbe, Rauheit und Metallanteil entstehen an EINER Stelle.

        Vorher an dreien — und zwei davon sind auseinandergelaufen.
        """
        stoff = _quelle('static', 'viewer', 'scene', 'garmentcode_stoff.js')
        self.assertIn('static FARBE = 0xdcd8d0;', stoff)
        self.assertIn('static neu(bisher = null, angaben = null)', stoff)
        self.assertIn('static werte(netz)', stoff)
        for datei in ('garmentcode_anziehen.js', 'garmentcode_ablage.js',
                      'garmentcode_material.js'):
            self.assertIn("from './garmentcode_stoff.js'",
                          _quelle('static', 'viewer', 'scene', datei), datei)


class EinhaengenNimmtBeideFormenTest(SimpleTestCase):
    u"""`einhaengen` löst `figur.inst` ODER die Instanz auf — und muss das
    dann auch benutzen. Mit `figur.inst` fiel der zweite Fall um
    (`undefined.group`), gemessen am 09.09.2026."""

    databases = set()

    def test_kein_direkter_zugriff_auf_figur_inst_mehr(self):
        quelle = _quelle('static', 'viewer', 'scene',
                         'garmentcode_drapieren.js')
        self.assertIn('const inst = figur?.inst || figur;', quelle)
        self.assertIn('GarmentcodeAnziehen.anziehen(\n                inst,',
                      quelle)
        self.assertNotIn('anziehen(\n                figur.inst,', quelle)


class MaterialAusDerSzeneTest(SimpleTestCase):

    databases = set()

    def test_die_ablage_setzt_das_gespeicherte_material(self):
        u"""Die andere Hälfte des Befundes: Beim Laden muss das Material aus
        der Szenendatei ankommen. Es kam an — und wurde danach überschrieben.
        """
        ablage = _quelle('static', 'viewer', 'scene', 'garmentcode_ablage.js')
        self.assertIn('GarmentcodeAblage._materialSetzen(', ablage)
        self.assertIn('eintrag.material', ablage)

    def test_die_ablage_liest_das_material_am_netz(self):
        u"""Gespeichert wird, was am Netz steht — nicht der Reglerstand."""
        ablage = _quelle('static', 'viewer', 'scene', 'garmentcode_ablage.js')
        self.assertIn('material: GarmentcodeAblage._material(netz)', ablage)
