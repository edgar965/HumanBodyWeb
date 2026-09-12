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
die Zusagen fest, die den Befund beheben — und die vom 12.09.2026.

NACHTRAG (12.09.2026, Edgar: „ändere ich das Gewebe, oder andere
Einstellungen, tut sich nichts"): „Ohne Auswahl nichts" war zu viel des
Guten — die Überschrift des Bereichs versprach „ohne Auswahl für alle
GarmentCode-Stücke dieser Figur", und wer ihr folgte, sah nichts. Die
Grenze liegt jetzt beim URHEBER, nicht bei der Auswahl: Ein Ereignis vom
Nutzer (`isTrusted`) wirkt ohne Auswahl auf alle `gc_*`-Stücke der Figur;
eines aus `dispatchEvent` (Reitergedächtnis, Vorbild) nur auf ein
gewähltes. Die Entscheidung liegt in `materialziel.js` und wird in Node
geprüft (`test_js_materialziel`); hier steht, dass die Handler den
Urheber durchreichen.
"""
import io
import re

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = settings.BASE_DIR


def _modultext(*teile):
    return io.open(WURZEL.joinpath(*teile), encoding='utf-8').read()


def _material():
    return _modultext('static', 'viewer', 'scene', 'garmentcode_material.js')


def _drapieren():
    return _modultext('static', 'viewer', 'scene', 'garmentcode_drapieren.js')


class MaterialOhneAuswahlTest(SimpleTestCase):

    databases = set()

    def test_die_ziele_kommen_aus_materialziel(self):
        u"""Der Kern: WELCHE Netze den Stand bekommen, entscheidet die
        geprüfte Klasse — nicht eine Schleife im Modul."""
        quelle = _material()
        self.assertIn("import { Materialziel } from './materialziel.js';", quelle)
        self.assertIn('Materialziel.netze({', quelle)
        self.assertIn('gewaehlt: GarmentcodeMaterial.gewaehltesStueck(inst)', quelle)
        self.assertNotIn(".filter((k) => k.startsWith('gc_'))", quelle)

    def test_anwenden_kennt_den_urheber(self):
        u"""`anwenden(figur, nutzer)`: breit nur, wenn der Nutzer es war."""
        quelle = _material()
        unterschrift = re.search(r'static anwenden\(([^)]*)\)', quelle)
        self.assertIsNotNone(unterschrift)
        self.assertEqual(unterschrift.group(1).strip(),
                         'figur, nutzer = false, werte = null')

    def test_ein_regler_bringt_nur_seine_eigenschaft_mit(self):
        u"""Gemessen: ein Gewebewechsel ohne Auswahl färbte beide Stücke
        der Figur auf das Farbfeld um. Jeder Handler liefert deshalb nur
        die Eigenschaft, die er bewegt hat."""
        quelle = _material()
        self.assertIn('return { farbe: wert };', quelle)
        self.assertIn('return { rauheit: wert / 100 };', quelle)
        self.assertIn('return { metall: wert / 100 };', quelle)
        self.assertEqual(quelle.count('ereignis.isTrusted, werte);'), 2)
        gewebe = _modultext('static', 'viewer', 'scene', 'garmentcode_gewebe.js')
        self.assertEqual(gewebe.count('return { gewebe: material.stand.gewebe };'), 2)
        self.assertIn('{ gewebe: material.stand.gewebe });', gewebe)

    def test_die_handler_reichen_istrusted_durch(self):
        u"""Reitergedächtnis und Vorbild schreiben per `dispatchEvent` —
        das darf nie breit wirken. Der Nutzer am Feld schon."""
        quelle = _material()
        self.assertEqual(quelle.count('ereignis.isTrusted, werte);'), 2,
                         '_feld und _schieber')
        gewebe = _modultext('static', 'viewer', 'scene', 'garmentcode_gewebe.js')
        self.assertIn('material.anwenden(material.figur(), ereignis.isTrusted,',
                      gewebe)
        self.assertNotIn('material.anwenden(material.figur());', gewebe)

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
        return _modultext('static', 'viewer', 'scene', 'garmentcode_anziehen.js')

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
        stoff = _modultext('static', 'viewer', 'scene', 'garmentcode_stoff.js')
        self.assertIn('static FARBE = 0xdcd8d0;', stoff)
        self.assertIn('static neu(bisher = null, angaben = null)', stoff)
        self.assertIn('static werte(netz)', stoff)
        for datei in ('garmentcode_anziehen.js', 'garmentcode_ablage.js',
                      'garmentcode_material.js'):
            self.assertIn("from './garmentcode_stoff.js'",
                          _modultext('static', 'viewer', 'scene', datei), datei)


class EinhaengenNimmtBeideFormenTest(SimpleTestCase):
    u"""`einhaengen` löst `figur.inst` ODER die Instanz auf — und muss das
    dann auch benutzen. Mit `figur.inst` fiel der zweite Fall um
    (`undefined.group`), gemessen am 09.09.2026."""

    databases = set()

    def test_kein_direkter_zugriff_auf_figur_inst_mehr(self):
        quelle = _modultext('static', 'viewer', 'scene',
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
        ablage = _modultext('static', 'viewer', 'scene', 'garmentcode_ablage.js')
        self.assertIn('GarmentcodeAblage._materialSetzen(', ablage)
        self.assertIn('eintrag.material', ablage)

    def test_die_ablage_liest_das_material_am_netz(self):
        u"""Gespeichert wird, was am Netz steht — nicht der Reglerstand."""
        ablage = _modultext('static', 'viewer', 'scene', 'garmentcode_ablage.js')
        self.assertIn('material: GarmentcodeAblage._material(netz)', ablage)
