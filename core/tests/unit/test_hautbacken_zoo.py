# -*- coding: utf-8 -*-
"""Der lokale Backer (`core/dienste/hautbacken/graph`) gegen Blender: der Hautbackenzoo (Edgar, 10.10.2026: „mache tests, ob das gleiche herauskommt wie bei Blender").

296 kleine Materialien (`hautbacken_zoo_materialien.py`) — jeder Knotentyp und jede Einstellung, die der Backer kennt: Bildknoten (Interpolation, Erweiterung, Farbraum, Alpha, Kanäle,
8 und 16 Bit), Mapping, Mix, Math, Vektor-Math, Map Range, Clamp, Farbe (HSV, Helligkeit, Gamma, Invertieren), Trennen, Verlauf, Kurven, Farbattribute, UV-Karten, Normal Map (alle Räume,
beide Basen, Stärke, Konvention, zweite UV), Bump und das Principled BSDF selbst (Metall, Glanz, Lack, Sheen, Untergrund, Anisotropie, Verteilung, Alpha, Transmission, verbundene Coat-Normale
und Tangente). Blender 5.2.2 hat sie mit Cycles „Selected to Active" gebacken (CPU, eine Probe je Texel, PNG ohne Verlust); die Bilder liegen in `hautbacken_daten/zoo/` (6,8 MB). Der Test
rechnet dieselben Materialien lokal auf der GPU und vergleicht je Material auf den Texeln, die es trifft (ohne den Rand zum Nachbarn).

Gemessen am 11.10.2026 (alle 296 Materialien, `ProjektTemp/_wegwerf/blendimport_massstab/zoo_schwellen.py`): mittlere Abweichung (Stufen von 255, über alle drei Kanäle) bei Farbe höchstens 0,02,
bei Rauheit 0,00, bei Normalen 0,05; p99 höchstens 1; Anteil der Texel über 6 Stufen höchstens 0,0002. Ausreißer sind einzelne Texel an Sprungstellen (Round, Wrap, Snap: 1 von rund 5.000 Texeln —
ein Texel liegt auf der anderen Seite der Stufe; `bake.cc` rechnet die Schwerpunkte in `double`, der Backer in `float`). 49 Materialien (`korrektur_*`, `glanz_*`) backt Blender mit „Bump Map
Correction": dort ist die gebackene Normale das gewichtete Mittel der Closure-Normalen (`hautbacken/closure`), und der Backer rechnet es nach (`glanz_gerechnet`); die übrigen 247 backt Blender
mit ausgeschalteter Korrektur (`hautbacken_zoo_blender.py`), damit ihr Vergleich die Knoten prüft und nicht das Closure-Modell.
Vor dem Abtastversatz von Blender (`Hautbackenkachel.VERSATZ`, 0,001 / 0,002 Texel, `RE_bake_pixels_populate`) lagen 18 Materialien über 3 Stufen größter Abweichung (bis 255).

Sabotage-Gegenprobe: am Ende der Datei.
"""

import os

import numpy as np
from django.test import SimpleTestCase

from core.tests.unit.hautbacken_zoo import Hautbackenzoo
from core.tests.unit.hautbacken_zoo_golden import Hautbackenzoogolden
from core.tests.unit.hautbacken_zoo_materialien import definitionen

DATEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hautbacken_daten', 'zoo')
#: Mittlere Abweichung (von 255) je Kanal, p99 und der Anteil der Texel über 6 Stufen — mit Luft über dem Gemessenen (0,02 / 0,00 / 0,05; p99 1; 0,02 %).
GRENZE = {'farbe': 0.1, 'rauheit': 0.1, 'normalen': 0.15}
P99_MAX = 2.0
SPRUNG_ANTEIL_MAX = 0.0005


class ZooGegenBlenderTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.zoo = Hautbackenzoogolden(DATEN)
        cls.ergebnisse = {}
        for satz in range(cls.zoo.saetze()):
            lokal = cls.zoo.lokal(satz)
            gold = cls.zoo.golden(satz)
            for i, name in enumerate(lokal['namen']):
                cls.ergebnisse[name] = cls.vergleich(lokal, gold, i, name)

    @staticmethod
    def vergleich(lokal, gold, i, name):
        """Je Kanal `mittel`, `p99`, `max` (`Hautbackenzoo.statistik`) und `sprung` (Anteil der Texel, in denen ein Kanal um mehr als 6 Stufen abweicht) auf dem Inneren der Region."""
        import cv2

        region = lokal['material'] == i
        innen = cv2.erode(region.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        aus = {'texel': int(innen.sum()), 'fehler': lokal['fehler'].get(i), 'ungerechnet': lokal['glanz_korrektur'].get(name), 'gerechnet': int(lokal['glanz_gerechnet'].get(name, 0))}
        for kanal in Hautbackenzoo.KANAELE:
            aus[kanal] = Hautbackenzoo.statistik(gold[kanal], lokal[kanal], innen)
            d = np.abs(gold[kanal].astype(np.int16) - lokal[kanal].astype(np.int16)).max(axis=2)[innen]
            aus[kanal]['sprung'] = float((d > 6).mean())
        return aus

    @staticmethod
    def zeile(name, kanal, k):
        return '%s %s: mittel %.2f p99 %.0f sprung %.4f max %d' % (name, kanal, k['mittel'], k['p99'], k['sprung'], k['max'])

    # ------------------------------------------------------------------ 1. Abdeckung

    def test_1_jedes_material_des_zoos_ist_verglichen(self):
        namen = [n for n, _ in definitionen()]
        self.assertEqual(len(namen), len(set(namen)), 'Namen der Zoo-Materialien sind nicht eindeutig')
        self.assertEqual(sorted(self.ergebnisse), sorted(namen))
        self.assertGreaterEqual(len(namen), 290)
        wenig = [n for n, e in self.ergebnisse.items() if e['texel'] < 1000]
        self.assertEqual(wenig, [], 'Materialien mit zu wenig Texeln im Vergleich: %s' % wenig)

    def test_2_kein_graph_wird_abgelehnt(self):
        fehler = {n: e['fehler'] for n, e in self.ergebnisse.items() if e['fehler']}
        self.assertEqual(fehler, {})

    # ------------------------------------------------------------------ 2. Gleich wie Blender

    def test_3_farbe_und_rauheit_gleich_blender(self):
        schlecht = []
        for name, e in sorted(self.ergebnisse.items()):
            for kanal in ('farbe', 'rauheit'):
                k = e[kanal]
                if k['mittel'] > GRENZE[kanal] or k['p99'] > P99_MAX or k['sprung'] > SPRUNG_ANTEIL_MAX:
                    schlecht.append(self.zeile(name, kanal, k))
        self.assertEqual(schlecht, [], '\n'.join(schlecht))

    def test_4_normalen_gleich_blender(self):
        schlecht = []
        for name, e in sorted(self.ergebnisse.items()):
            k = e['normalen']
            if k['mittel'] > GRENZE['normalen'] or k['p99'] > P99_MAX or k['sprung'] > SPRUNG_ANTEIL_MAX:
                schlecht.append(self.zeile(name, 'normalen', k))
        self.assertEqual(schlecht, [], '\n'.join(schlecht))

    def test_5_das_closure_modell_rechnet_die_materialien_mit_bump_map_correction(self):
        """Die 49 Materialien, die Blender mit „Bump Map Correction" backt, rechnet der Backer mit dem Closure-Modell nach (nichts bleibt ungerechnet); alle anderen laufen ohne."""
        ungerechnet = {n: e['ungerechnet'] for n, e in self.ergebnisse.items() if e['ungerechnet']}
        self.assertEqual(ungerechnet, {})
        gerechnet = sorted(n for n, e in self.ergebnisse.items() if e['gerechnet'])
        erwartet = sorted(n for n in self.ergebnisse if n.startswith(('korrektur_', 'glanz_')))
        self.assertGreaterEqual(len(erwartet), 49)
        self.assertEqual(gerechnet, erwartet)

    # ------------------------------------------------------------------ 3. Der Vergleich kann rot werden

    def test_6_ein_verschobenes_bild_ist_rot(self):
        """Gegenprobe des Vergleichs selbst: dasselbe Material, Blenders Bild um acht Texel versetzt, überschreitet die Grenzen (sonst prüfte der Test nichts)."""
        lokal = self.zoo.lokal(0)
        gold = self.zoo.golden(0)
        gold['farbe'] = np.roll(gold['farbe'], 8, axis=1)
        e = self.vergleich(lokal, gold, 0, lokal['namen'][0])
        self.assertTrue(e['farbe']['mittel'] > GRENZE['farbe'] or e['farbe']['p99'] > P99_MAX, e['farbe'])

    def test_7_die_golden_bilder_haben_inhalt(self):
        gold = self.zoo.golden(5)
        for kanal, bild in gold.items():
            self.assertEqual(bild.shape, (256, 256, 3), kanal)
            self.assertGreater(int(bild.max()) - int(bild.min()), 20, kanal)


# Sabotage-Gegenprobe (11.10.2026, je eine Änderung, danach rückgängig, Zoo-Test ~10 s):
# * `hautumwandlung.py` `GRAU` Rot und Blau vertauscht            → Test 3 rot: `farbe_zu_zahl` (Mittel 9,6), `rgb_zu_grau` (15,5) — sonst keines
# * `hautschattungbau.py` Tangenten immer aus `uv_0`              → Test 4 rot: `normalkarte_original_uv2` (26,4), `normalkarte_displaced_uv2` (21,4) — sonst keines
# * `hautknotennormalkarte.py` Stärke ohne `clamp(s, 0, 1)`       → Test 4 rot: `normalkarte_original_2.0` (1,4), `normalkarte_displaced_2.0` (2,4) — sonst keines
# * `hautglanzkernel.py` Schwelle 0,01 → 0,5                      → hier grün (die Schwelle weitet nur aus), rot in `test_hautbacken_glanz.py` (Fall 1 und 3)
# * `hautalpha.py` `SCHWELLE` 0,5 → 0,0                           → Test 4 rot: `glanz_alpha_unter_schwelle` (Mittel 64,7), `glanz_alpha_textur` (36,6) — sonst keines
# * Coat-Normale `n` statt `sd->N` (`hautclosurekernel.py`)       → Test 4 rot (gemessen vor der Korrektur: `glanz_lack` 25,4, `glanz_lack_halb_tint` 19,6, `glanz_sheen_lack` 34,5, `glanz_alles` 23,2)
# Sabotage-Gegenproben vom 11.10.2026 (`ProjektTemp/_wegwerf/cycles_vergleich/sabotage.py <fall>`, je eine Änderung, danach rückgängig):
# * `Hautbackenkachel.VERSATZ` (0,001; −0,002) → (0; 0)           → Test 3 und 4 rot: `vektor_wrap` und `farbattribut_standard` (Sprunganteil 0,0010), `bereich_vektor_stepped` (0,0005),
#                                                                    `bump_1.0_0.1_normal_0.01` (Normalen, Sprunganteil 0,0017) — mit dem Versatz alle unter 0,0002
# * Transmission-Gewicht mit 0 multipliziert (Kern)               → Test 4 rot: `glanz_transmission_*` 2,4–15,7 Stufen Mittel (außer `_schwarz`: schwarze Basis, nur das Glas bleibt)
# * verbundene Coat-Normale ignoriert (`sd->N`, `hautclosure.py`) → Test 4 rot: `glanz_lack_normale_bump` 20,2, `_halb_tint` 14,3, `_sheen` 5,8
# * Tangente immer ungültig (`tang_gueltig` 0)                    → Test 4 rot: `glanz_aniso_rauh_ohne_tangente` 5,1, `glanz_aniso_rauh_tangente` 4,7 (nur bei Rauheit 1 klemmt `alpha_x`)
# * Energieerhaltung des Glases aus (Faktor 1)                    → Test 4 rot: `glanz_transmission_rauh_dunkel` 0,39 Mittel (Grenze 0,15)
