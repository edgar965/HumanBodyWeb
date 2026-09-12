# -*- coding: utf-8 -*-
u"""Ein angepasstes Kleidungsstück muss in der Liste landen, die gespeichert wird.

DER BEFUND (Edgar, 09.09.2026: „habe gerade ein Modell mit Schuhen (von
Garment Fit) gespeichert, beim Neuladen waren die Schuhe weg")
=====================================================================
`Kleideranpassung.netzEinsetzen` schrieb die Ausgangspunkte der
Regionsregler aus einer Variablen `punkte`, die es seit dem 28.08.2026
nicht mehr gab: Commit 1b430d4 („Eine Netzgeometrie statt neun") entfernte
die Zeile `const punkte = base64ToFloat32(daten.vertices)` zusammen mit dem
alten Import — die Verwendung blieb stehen.

Der `ReferenceError` fiel NACH `group.add(netz)`. Das Stück hing also
sichtbar an der Figur, während `ausfuehren()` in seinen `catch` sprang und
den Rest übersprang:

    figur.garmentState[…] = zustand      nie gesetzt
    _computeGarmentRegionWeights         nie gerechnet
    danach(…)  ->  figur.garments.push   NIE — hier fehlte das Stück

Gespeichert wird `inst.garments`. Die Liste blieb leer, die Datei bekam
`"garments": []`, und beim Laden stand die Figur ohne Schuhe da. Zwölf Tage
lang, ohne eine einzige Zeile im Fehlerlog: `ausfuehren` meldete den Fehler
nur mit `console.error` auf die Browserkonsole.

Dieselbe Fehlerklasse wie am 08.09.2026 bei GarmentCode („beim neu laden
sind die Garment Code items weg") — das Netz hängt, die Liste kennt es
nicht.
"""
import io

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = settings.BASE_DIR


def _quelle(*teile):
    return io.open(WURZEL.joinpath(*teile), encoding='utf-8').read()


def _anpassung():
    return _quelle('static', 'viewer', 'scene', 'kleideranpassung.js')


class AusgangspunkteTest(SimpleTestCase):

    databases = set()

    def test_die_ausgangspunkte_kommen_aus_den_serverdaten(self):
        u"""Kein Rückgriff mehr auf eine Variable, die es nicht gibt."""
        quelle = _anpassung()
        self.assertIn('Netzgeometrie.punkte(daten.vertices)', quelle)
        self.assertNotIn('new Float32Array(punkte)', quelle)

    def test_netzgeometrie_ist_importiert(self):
        u"""Sonst wäre der Aufruf derselbe Fehler mit anderem Namen."""
        self.assertIn("import { Netzgeometrie } from "
                      "'../gemeinsam/netzgeometrie.js';", _anpassung())

    def test_netzgeometrie_kennt_punkte(self):
        u"""Die Gegenrichtung: Der gerufene Name muss dort auch stehen."""
        self.assertIn('static punkte(',
                      _quelle('static', 'viewer', 'gemeinsam',
                              'netzgeometrie.js'))


class FehlerWirdProtokolliertTest(SimpleTestCase):
    u"""Ein Fehler, der nur auf der Konsole steht, ist keiner, den jemand
    sieht — er hat hier zwölf Tage überlebt."""

    databases = set()

    def test_der_fang_schreibt_ins_protokoll(self):
        quelle = _anpassung()
        self.assertIn("Protokoll.fehler('kleideranpassung'", quelle)
        self.assertNotIn("console.error('Anpassen fehlgeschlagen:'", quelle)

    def test_protokoll_ist_importiert(self):
        self.assertIn("import { Protokoll } from "
                      "'../gemeinsam/protokoll.js';", _anpassung())


class ZweiterFehlerDerselbenArtTest(SimpleTestCase):
    u"""In `Charakterzubehoer.kleidung` stand dieselbe Sorte Fehler.

    `Kleidungszustand.ausJson({...g, color: g.color || [color.r, color.g,
    color.b]})` — eine Variable `color` gibt es in der Datei nicht. Sie wird
    nur ausgewertet, wenn `g.color` fehlt; dann warf die Zeile, wieder NACH
    `group.add`. Das Stück hing sichtbar, `garmentState` fehlte, und die
    Regler zeigten für dieses Stück die Vorgaben statt seiner Werte.
    """

    databases = set()

    def _zubehoer(self):
        return _quelle('static', 'viewer', 'scene', 'charakter_zubehoer.js')

    def test_keine_undefinierte_farbvariable_mehr(self):
        quelle = self._zubehoer()
        code = '\n'.join(z for z in quelle.splitlines()
                         if not z.strip().startswith('//'))
        self.assertNotIn('color.r', code)
        self.assertIn('Kleidungszustand.ausJson({ ...g })', code)

    def test_der_fang_schreibt_ins_protokoll(self):
        quelle = self._zubehoer()
        self.assertIn("Protokoll.fehler('charakter_zubehoer'", quelle)
        self.assertNotIn("console.error('Failed to load garment:'", quelle)


class KleiderLaufenNebeneinanderTest(SimpleTestCase):
    u"""Die Anpassungen liegen auf dem kritischen Pfad des Szenenaufbaus.

    Edgar, 09.09.2026: „laden der Szene dauert sehr lange, bis zu 10 s."
    Gemessen gegen den laufenden Server, drei Stücke, je zwei Läufe im
    Wechsel: nacheinander 1,85 / 2,00 s, nebeneinander 1,08 / 1,73 s.
    """

    databases = set()

    def test_die_anfragen_starten_zusammen(self):
        quelle = _quelle('static', 'viewer', 'scene', 'charakter_zubehoer.js')
        self.assertIn('await Promise.all(inst.garments.map(', quelle)
        # Kein `await` mehr in der Schleife über die Stücke.
        schleife = quelle[quelle.index('for (const { g, daten: data'):]
        self.assertNotIn('await ', schleife.split('static async haare')[0])

    def test_die_farbe_geht_nur_mit_wenn_es_eine_gibt(self):
        u"""Ohne `color_*` gilt die Materialfarbe des Stücks
        (`Anpassungsregler._farbe`). Wer ersatzweise eine Vorgabe schickt,
        färbt jedes Stück ohne eigene Farbe einheitlich ein."""
        frage = _quelle('static', 'viewer', 'gemeinsam', 'kleiderfrage.js')
        self.assertIn('if (kanaele) {', frage)
        self.assertIn('if (!farbe) return null;', frage)


class ListeWirdGepflegtTest(SimpleTestCase):
    u"""Die Kette, an deren Ende das Speichern hängt."""

    databases = set()

    def test_der_assets_weg_traegt_das_stueck_in_die_liste_ein(self):
        quelle = _quelle('static', 'viewer', 'scene', 'kleidung_anpassen.js')
        self.assertIn('figur.garments.push({ id: kennung', quelle)

    def test_die_liste_steht_im_gespeicherten_modell(self):
        u"""Beide Speicherwege der gewöhnlichen Figur führen `garments`."""
        charakter = _quelle('static', 'viewer', 'scene', 'character.js')
        self.assertIn('garments,', charakter)
        self.assertIn('garments',
                      _quelle('static', 'viewer', 'scene', 'szenenausgabe.js'))
