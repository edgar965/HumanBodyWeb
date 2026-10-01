# -*- coding: utf-8 -*-
u"""Die sechs Punkte „vom Foto zum Modell" (01.10.2026) — Kunstdaten, keine echten Netze, keine Grafikkarte.

1. Fotoprüfung: ein Foto mit anderem Shirt fällt heraus, ein dunkleres (Schatten) nicht; Nahaufnahmen zählen nicht.
2. Gesamtnote: Foto + Farbe je Teil + Gesicht, ohne Netznote — die Reihenfolge der `.51`-Runden 5 und 39.
3. Rundenauswahl: besser → beste; ohne Umbau schlechter → verworfen und gesperrt; Umbau → Probe, nach drei Runden
   ohne Besserung verworfen; das Filtern gesperrter Zeilen.
4. Messprüfung: Masken, die den Körper enthalten → gültig; um 20 Bildpunkte versetzt → ungültig.
5. Rezepte vergleichen: `Begutachtungsstand.normalisieren` schreibt Aufrufe wie `G9rezept.text`.

Sabotage: in `Rundenauswahl.nach_runde` die Toleranz weglassen und `<=` statt `<` → Fall 3 rot (gleich gut zählt als
besser); in `Fotopruefung._band` die Helligkeit nicht durch `HELL_FAKTOR` teilen → Fall 1 rot (Schatten fällt heraus).
"""
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from iterationen2d3d.gesamtnote import Gesamtnote
from iterationen2d3d.messpruefung import Messpruefung
from iterationen2d3d.rundenauswahl import Rundenauswahl

from core.dienste.begutachtungsstand import Begutachtungsstand


class SechsPunkteTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _figur(shirt, hose, breite=40, hoehe=200):
        bild = np.zeros((hoehe + 20, breite + 20, 4), np.uint8)
        bild[10:10 + hoehe, 10:10 + breite, 3] = 255
        bild[10:10 + hoehe // 2, 10:10 + breite, :3] = shirt
        bild[10 + hoehe // 2:10 + hoehe, 10:10 + breite, :3] = hose
        return bild

    def test_1_fotopruefung(self):
        sys.path.insert(0, str(settings.BASE_DIR.parent / 'VideoToBVH' / 'wrappers'))
        from mesh_fotopruefung import Fotopruefung
        grau, schwarz = (96, 98, 106), (40, 40, 44)
        fotos = [('vorne.jpg', 'vorne', self._figur(grau, schwarz)),
                 ('hinten.jpg', 'hinten', self._figur((64, 66, 72), (28, 28, 30))),          # Schatten: dunkler
                 ('seite.jpg', 'rechts', self._figur((140, 125, 100), (150, 110, 170)))]      # anderes Shirt, lila
        befund = Fotopruefung.pruefen(fotos)
        self.assertEqual(befund['ausgelassen'], ['seite.jpg'])
        nah = np.zeros((120, 100, 4), np.uint8)
        nah[10:110, 10:90] = (200, 150, 120, 255)                                             # breiter als hoch
        befund = Fotopruefung.pruefen(fotos[:2] + [('gesicht.jpg', 'auto', nah)])
        self.assertEqual((befund['ausgelassen'], befund['nicht_geprueft']), ([], ['gesicht.jpg']))

    def test_2_gesamtnote(self):
        teil = {'art': 'kleidung', 'foto_farbe': [0.35, 0.34, 0.37], 'render_farbe': [0.15, 0.15, 0.15], 'pixel': 100}
        note = Gesamtnote.berechnen({'foto': 0.6, 'abweichung': 1.9}, {'teile': {'s': teil},
                                                                        'gesicht': {'verhaeltnis': {'mund': 1.05}}})
        self.assertEqual(note, {'gesamt': 0.8533, 'foto': 0.6, 'farbe_teile': 0.2033, 'gesicht': 0.05})
        runde5 = Gesamtnote.berechnen({'foto': 0.6179, 'abweichung': 1.799}, {})['gesamt'] + 0.166 + 0.091
        runde39 = Gesamtnote.berechnen({'foto': 0.6046, 'abweichung': 1.904}, {})['gesamt'] + 0.185 + 0.051
        self.assertLess(runde39, runde5)                    # die kurze Frisur vor der langen — die Netznote zählt nicht

    def test_3_rundenauswahl(self):
        a = Rundenauswahl()
        self.assertEqual(a.nach_runde(1, 0.90, [])[0], 'besser')
        erste = {'runde': 1, 'gesamt': 0.9}
        self.assertEqual(a.nach_runde(2, 0.95, ['m.passform(weite_cm=1.0)']), ('verworfen', erste))
        self.assertEqual(a.verboten(), ['m.passform(weite_cm=1.0)'])
        self.assertEqual(a.nach_runde(3, 0.901, []), ('verworfen', {'runde': 1, 'gesamt': 0.9}))   # in der Toleranz
        self.assertEqual(a.nach_runde(4, 0.97, ["m.kleid_nur('shirt')"])[0], 'probe')
        self.assertEqual(a.verboten(), [])                                                         # Probe: frei
        self.assertEqual(a.nach_runde(5, 0.96, [])[0], 'probe')
        self.assertEqual(a.nach_runde(6, 0.93, []), ('probe_verworfen', {'runde': 1, 'gesamt': 0.9}))
        self.assertIn("m.kleid_nur('shirt')", a.verboten())
        self.assertEqual(a.nach_runde(7, 0.80, [])[0], 'besser')
        self.assertEqual(a.verboten(), [])                                                         # neue Lage
        self.assertEqual(Rundenauswahl.filtern('# kopf\nm.a(1)\n', ['m.a(1)']), '')
        self.assertEqual(Rundenauswahl.filtern('# kopf\nm.a(1)\nm.b(2)\n', ['m.a(1)']), '# kopf\nm.b(2)\n')

    def test_4_messpruefung(self):
        y = np.linspace(0.0, 1.0, 60)
        koerper = np.vstack([np.column_stack([np.full(60, x), y, np.full(60, z)])
                             for x in (-0.1, 0.0, 0.1) for z in (-0.05, 0.05)])
        maske = np.zeros((192, 128), bool)
        maske[4:189, 42:86] = True                          # 180 px/m: ±0,1 m = ±18 px um die Mitte 64
        gut = Messpruefung.pruefen([(0.0, maske, maske), (90.0, maske, maske)], 1.0, koerper)
        self.assertTrue(gut['gueltig'] and gut['huelle_gueltig'], gut)
        versetzt = np.roll(maske, 20, axis=1)
        schlecht = Messpruefung.pruefen([(0.0, maske, versetzt), (90.0, maske, versetzt)], 1.0, koerper)
        self.assertFalse(schlecht['gueltig'], schlecht)
        self.assertTrue(Messpruefung.erlaubt({}, 'gueltig'))
        self.assertFalse(Messpruefung.erlaubt({'messguete': schlecht}, 'gueltig'))

    def test_5_rezepte_normalisieren(self):
        text = "# automatisch\nm.passform( weite_cm = 1.0 )\nm.haar_farbe(\"#4b403c\")\n"
        self.assertEqual(Begutachtungsstand.normalisieren(text),
                         "# automatisch\nm.passform(weite_cm=1.0)\nm.haar_farbe('#4b403c')\n")
