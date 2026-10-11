# -*- coding: utf-8 -*-
"""`Schammessung` — das Urteil und der Lauf an einer Kunsthaut (`_nahtwelt.Nahtwelt`); `Schammessungzeilen` — der Bericht als Zeilen (10./11.10.2026).

Edgar, 10.10.2026: „mach kein Raten und Bildvergleich, sondern Messungen … Mach das auch bei dem Importprozess." Die Messung läuft bei jedem Bau eines Scham-Stücks, ohne Schalter, und ein Fehler
in ihr beendet den Import nie.

1. `abweichungen` ist leer, wenn alles innerhalb der Schwellen liegt, und nennt jede Überschreitung mit Zahl und Schwelle: Form (Median, p90), Tiefenkarte, Fläche (Kanten über 90°), Naht (Rand ↔ Ring),
   Knick über die Naht (neu 11.10.2026: Ringkanten über `NAHT_KNICK_GRAD` mit den schlimmsten Ringecken), Farbe am Ring, Farbe gegen das Original.
2. `zeilen` führt den Knick über die Naht als eigene Zeile und meldet einen gescheiterten Lauf als solchen.
3. Ganzer Lauf an der Kunsthaut mit flachem Stück: Naht gemessen (16 Kanten, kein Knick), keine Abweichung; mit zurückgeklapptem Stück (innerer Ring 0,5 mm auf der Hautseite) meldet `abweichungen`
   16 Ringkanten über 60° — die Messung sieht die Falte, die die Punktnormalen verdeckten.
4. `sicher` wirft nie: bei unbrauchbaren Eingaben kommt `{'fehler': …}` zurück und der Fehler steht im Log; mit `ordner` entsteht `messung.json`.

Sabotage-Gegenprobe (nicht gelaufen): in `messen` die Zeile `aus['naht']['knick_ueber_naht'] = …` entfernen macht Fall 3 rot; in `abweichungen` den Zweig `k.get('ueber_60')` entfernen macht Fälle 1 und 3 rot.
"""
import json
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

from core.dienste.schammessung import Schammessung
from core.dienste.schammessungzeilen import Schammessungzeilen

from ._nahtwelt import Nahtwelt
from ._pruefablage import Pruefablage


class SchammessungUrteilTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _gut():
        """Eine Messung, die überall innerhalb der Schwellen liegt."""
        return {'geometrie': {'original_zu_modell': {'gesamt': {'n': 10, 'median': 0.5, 'p90': 2.0, 'max': 4.0}}, 'tiefenkarte': {'betrag': {'median': 0.3}},
                              'flaeche': {'ueber_90': 0.01, 'ueber_90_original': 0.008}},
                'naht': {'rand_zu_ring_mm': {'max': 0.0}, 'ring_zu_rand_mm': {'max': 0.0}, 'knick_ueber_naht': {'kanten': 97, 'ueber_60': 0, 'max_grad': 45.0, 'schlimmste': []}},
                'farbe_am_ring': {'baender': [{'n': 100, 'leuchtdichte_prozent': -1.0, 'band_mm': '0–6'}]}, 'farbe_gegen_original': {'mittel': 2.0}}

    def _abw(self, aenderung):
        m = self._gut()
        aenderung(m)
        return Schammessung([[0, 0, 0]], [[0, 0, 0]], np.zeros((1, 3, 2)), {}, None).abweichungen(m)

    def test_1_innerhalb_der_schwellen_ist_alles_leer(self):
        self.assertEqual(self._abw(lambda m: None), [])

    def test_1b_jede_ueberschreitung_wird_mit_zahl_und_schwelle_genannt(self):
        def form(m):
            m['geometrie']['original_zu_modell']['gesamt'].update(median=1.2, p90=4.0)

        def tiefe(m):
            m['geometrie']['tiefenkarte']['betrag']['median'] = 2.5

        def flaeche(m):
            m['geometrie']['flaeche']['ueber_90'] = 0.05

        def naht(m):
            m['naht']['rand_zu_ring_mm']['max'] = 0.8

        def knick(m):
            m['naht']['knick_ueber_naht'] = {'kanten': 97, 'ueber_60': 3, 'max_grad': 147.0, 'schlimmste': [[16, 147.0], [17, 143.0], [58, 90.0], [59, 40.0]]}

        def ring(m):
            m['farbe_am_ring']['baender'][0]['leuchtdichte_prozent'] = -9.0

        def farbe(m):
            m['farbe_gegen_original']['mittel'] = 30.0

        erwartet = {form: ('Form', '1.20', '4.00'), tiefe: ('Tiefenkarte', '2.50'), flaeche: ('Fläche', '5.0 %'), naht: ('rand_zu_ring_mm', '0.80'),
                    knick: ('3 Ringkanten knicken über 60°', '147°', '16, 17, 58'), ring: ('Farbe am Ring', '-9.0'), farbe: ('Farbe gegen Original', '30.0')}
        for aenderung, teile in erwartet.items():
            with self.subTest(aenderung=aenderung.__name__):
                text = ' | '.join(self._abw(aenderung))
                for teil in teile:
                    self.assertIn(teil, text)

    def test_2_die_zeilen_fuehren_den_knick_und_den_gescheiterten_lauf(self):
        null = {'n': 100, 'median': 0.0, 'p90': 0.0, 'max': 0.0}
        m = {'stueck': {'punkte': 10, 'dreiecke': 12},
             'naht': {'randpunkte': 100, 'ringecken': 100, 'rand_zu_ring_mm': null, 'ring_zu_rand_mm': null, 'normalen_grad': {'median': 9.0, 'p90': 28.0, 'max': 53.0, 'umgekehrt': 0.0},
                      'knick_ueber_naht': {'kanten': 97, 'median_grad': 10.9, 'p90_grad': 36.1, 'max_grad': 55.0, 'ueber_30': 13, 'ueber_60': 0, 'ueber_90': 0, 'schlimmste': [[64, 55.0]]}},
             'abweichungen': []}
        zeilen = Schammessungzeilen.zeilen(m)
        knick = [z for z in zeilen if 'Knick über die Naht' in z]
        self.assertEqual(len(knick), 1)
        self.assertIn('97 Kanten', knick[0])
        self.assertIn('über 30°: 13', knick[0])
        self.assertEqual(Schammessungzeilen.zeilen({'fehler': 'ValueError: kaputt'}), ['MESSUNG GESCHEITERT: ValueError: kaputt'])

    def _lauf(self, abstand_mm):
        figur, loch = Nahtwelt.haut()
        punkte, dreiecke = Nahtwelt.stueck(abstand_mm)
        return Schammessung(punkte, dreiecke, np.zeros((len(dreiecke), 3, 2)), figur, loch).messen()

    def test_3_der_ganze_lauf_sieht_die_falte_an_der_naht(self):
        flach = self._lauf(5.0)
        self.assertEqual(flach['naht']['knick_ueber_naht']['kanten'], 16)
        self.assertEqual(flach['naht']['knick_ueber_naht']['ueber_60'], 0)
        self.assertFalse([a for a in flach['abweichungen'] if 'Ringkanten knicken' in a])
        falte = self._lauf(-0.5)
        self.assertEqual(falte['naht']['knick_ueber_naht']['ueber_60'], 16)
        meldung = [a for a in falte['abweichungen'] if 'Ringkanten knicken' in a]
        self.assertEqual(len(meldung), 1)
        self.assertIn('zurückgeklappt', meldung[0])

    def test_4_sicher_wirft_nie_und_schreibt_die_messung_ab(self):
        with self.assertLogs('core', level='ERROR'):
            kaputt = Schammessung.sicher(punkte='kein Netz', dreiecke=None, uv_ecken=None, figur=None, loch=None)
        self.assertIn('fehler', kaputt)
        figur, loch = Nahtwelt.haut()
        punkte, dreiecke = Nahtwelt.stueck(5.0)
        with Pruefablage.ordner('messung_') as ordner:
            bericht = Schammessung.sicher(ordner=Path(ordner), punkte=punkte, dreiecke=dreiecke, uv_ecken=np.zeros((len(dreiecke), 3, 2)), figur=figur, loch=loch)
            gelesen = json.loads((Path(ordner) / 'messung.json').read_text(encoding='utf-8'))
        self.assertNotIn('fehler', bericht)
        self.assertEqual(gelesen['naht']['knick_ueber_naht']['kanten'], 16)
