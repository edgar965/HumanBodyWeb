# -*- coding: utf-8 -*-
u"""Prüfwerkzeug der Reglergliederung (18.10.2026, Konzept `Docu/konzepte/2026-10-18_genesis9-regler-vereinfachen-konzept.md`, Abschnitt 5):
die echte Bibliothek, die echte Zuordnungstabelle (`manage.py genesis9_reglerorte`), das echte Bedienfeld (`G9reglergliederung.bereiche()`).

Ein neuer oder portierter Regler muss gemessen sein, Wirkung haben (oder als Anhang, Korrektur, bedingt oder Steuerung gekennzeichnet stehen) und darf
kein gemessen gleiches sichtbares Gegenstück haben. Sonst stünde er wieder in einem Herkunftsbereich, „ohne Effekt“ oben in einer Liste oder doppelt —
genau die drei Klagen vom 18.10.2026 („Viele davon sind doppelt, haben keinen Effekt oder sind in der falschen Kategorie“).

Zusagen:
1. Jeder Regler des Plans außerhalb der festen Bereiche steht in der Tabelle (sonst: `manage.py genesis9_reglerorte`).
2. Jeder Regler genau einmal: Zeilen + Aliasse + Paar-Hälften = Plan; kein Herkunftsbereich (`hb_…`, `mh_…`, `sx_…`, `uma_…`, `verborgen_…`) bleibt übrig.
3. Von jedem gemessenen Alias-Paar steht nur EINER als Zeile im Bedienfeld.
4. Direkt im Bereich (ohne Gruppe) steht in den Körperteil-Bereichen nur, was am Käfig wirkt (≥ 0,1 mm) oder als Pose Knochen dreht.

Gegenprobe gefahren 18.10.2026 (`ProjektTemp/_wegwerf/regler_inventur/gegenprobe_stand.py`, sabotiert nur im eigenen Prozess): ohne Sabotage 4 grün;
`G9reglerzusammenlegung._aliase` abgeschaltet → Fall 3 rot (Paare wie NW Damira Abs II doppelt sichtbar); in `G9reglerplatz._ohne_wirkung` statt
„Daz-Steuerung“ `return herkunft, '', None` → Fall 2 rot (`verborgen_baseanime9`, `verborgen_people` …) und Fall 4 rot (`facs_ctrl_NeckSwallow` direkt
unter Hals). Ohne Daz-Bibliothek oder Tabelle übersprungen — mit Grund.
"""
import unittest

from django.test import SimpleTestCase
from Genesis9.pfade import G9pfade
from Genesis9.reglergliederung import G9reglergliederung
from Genesis9.reglerorte import G9reglerorte


def voraussetzungen():
    if not G9pfade.vorhanden():
        return 'keine Daz-Bibliothek'
    if not G9reglerorte.pfad().is_file():
        return 'Zuordnungstabelle fehlt (manage.py genesis9_reglerorte)'
    return None


GRUND = voraussetzungen()


@unittest.skipIf(GRUND, GRUND)
class ReglerorteStandTest(SimpleTestCase):
    databases = set()
    HERKUNFT = ('hb_', 'mh_', 'sx_', 'uma_', 'verborgen_')
    KOERPERTEILE = ('kopf', 'hals', 'brust', 'ruecken', 'taille', 'huefte', 'arme', 'haende', 'beine', 'fuesse')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from Genesis9.reglerplan import G9reglerplan
        cls.roh = G9reglerplan.bereiche()
        cls.orte = G9reglerorte.holen()
        cls.neu = G9reglergliederung.bereiche()

    def test_1_jeder_regler_gemessen(self):
        fehlt = [r['name'] for b in self.roh if b['schluessel'] not in G9reglergliederung.FEST for r in b['regler']
                 if r['name'] not in self.orte['regler']]
        self.assertEqual(fehlt[:20], [], '%d Regler ohne Messung — manage.py genesis9_reglerorte' % len(fehlt))

    def test_2_jeder_regler_genau_einmal(self):
        zeilen = sum(len(b['regler']) for b in self.neu)
        weitere = sum(len(r.get('aliase') or []) + (1 if r.get('paar') else 0) for b in self.neu for r in b['regler'])
        self.assertEqual(zeilen + weitere, sum(len(b['regler']) for b in self.roh))
        uebrig = [b['schluessel'] for b in self.neu if b['schluessel'].startswith(self.HERKUNFT)]
        self.assertEqual(uebrig, [], 'Herkunftsbereiche übrig')

    def test_3_alias_nur_einmal_sichtbar(self):
        zeilen = {r['name'] for b in self.neu for r in b['regler']}
        doppelt = [(x, y) for x, y, *_ in self.orte['aliase'] if x in zeilen and y in zeilen]
        self.assertEqual(doppelt, [])

    def test_4_oben_nur_was_wirkt(self):
        ohne = []
        for b in self.neu:
            if b['schluessel'] not in self.KOERPERTEILE:
                continue
            for r in b['regler']:
                e = self.orte['regler'].get(r['name']) or {}
                if not r.get('gruppe') and e.get('mm', 1.0) < G9reglerorte.WIRKUNG_MM and e.get('dreht', 0.0) <= 0.1:
                    ohne.append((b['schluessel'], r['name']))
        self.assertEqual(ohne[:20], [], '%d Regler ohne Wirkung direkt im Bereich' % len(ohne))
