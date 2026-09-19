# -*- coding: utf-8 -*-
u"""`Reihenfolge` (Platznummern der Vergleichsseite, 19.09.2026).

Auftrag Edgar: „eine Spalte mit der Nummer, was die Reihenfolge der Anzeige
sein soll. Wenn ich die Nummer ändere, ändern sich alle anderen entsprechend
nach hinten. DEF ist immer das erste."

1. `verschoben`: das Skelett kommt auf die Nummer, die anderen rücken nach
   hinten; `def` bleibt 1 — auch wenn jemand ihn verschieben oder ein anderes
   auf 1 setzen will; Nummern außerhalb 1..9 werden eingefangen.
2. `plaetze`: Platz 1 ist links vorn (−3, 0), Platz 7 hinten (−3, −2).
3. `ausText`: nur eine vollständige Folge mit `def` vorn zählt, sonst Vorgabe.

Sabotage-Gegenprobe: `platz = ziel - 1` statt `ziel - 2` -> Fall 1 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('skelett_test', 'reihenfolge.js')

SKRIPT = """
const { Reihenfolge } = await import(MODUL);
const V = Reihenfolge.VORGABE;
pruefe('Vorgabe', V, ['def', 'cmu', 'mixamo', 'mocapnet', 'bandai', 'openpose', 'smpl', 'uma', 'genesis9']);

// 1. verschoben
pruefe('genesis9 auf 2', Reihenfolge.verschoben(V, 'genesis9', 2),
       ['def', 'genesis9', 'cmu', 'mixamo', 'mocapnet', 'bandai', 'openpose', 'smpl', 'uma']);
pruefe('cmu auf 5', Reihenfolge.verschoben(V, 'cmu', 5),
       ['def', 'mixamo', 'mocapnet', 'bandai', 'cmu', 'openpose', 'smpl', 'uma', 'genesis9']);
pruefe('uma auf 1 landet auf 2', Reihenfolge.verschoben(V, 'uma', 1)[0], 'def');
pruefe('uma auf 1 landet auf 2 (b)', Reihenfolge.verschoben(V, 'uma', 1)[1], 'uma');
pruefe('def bleibt', Reihenfolge.verschoben(V, 'def', 5), V);
pruefe('zu gross', Reihenfolge.verschoben(V, 'cmu', 99).at(-1), 'cmu');
pruefe('unbekannt', Reihenfolge.verschoben(V, 'x', 3), V);
pruefe('NaN ans Ende', Reihenfolge.verschoben(V, 'cmu', NaN).at(-1), 'cmu');

// 2. plaetze
const p = Reihenfolge.plaetze(Reihenfolge.verschoben(V, 'genesis9', 2));
pruefe('def Platz 1', p.def, { nummer: 1, x: -3, z: 0 });
pruefe('genesis9 Platz 2', p.genesis9, { nummer: 2, x: -1.5, z: 0 });
pruefe('smpl Platz 8 hinten', p.smpl, { nummer: 8, x: -1.5, z: -2 });

// 3. ausText
pruefe('gemerkt', Reihenfolge.ausText(JSON.stringify(['def', 'uma', 'cmu', 'mixamo', 'mocapnet', 'bandai', 'openpose', 'smpl', 'genesis9']))[1], 'uma');
pruefe('def nicht vorn', Reihenfolge.ausText(JSON.stringify(['uma', 'def', 'cmu', 'mixamo', 'mocapnet', 'bandai', 'openpose', 'smpl', 'genesis9'])), V);
pruefe('unvollstaendig', Reihenfolge.ausText('["def","cmu"]'), V);
pruefe('kein JSON', Reihenfolge.ausText(null), V);
pruefe('gueltig', Reihenfolge.gueltig(V), true);
pruefe('ungueltig doppelt', Reihenfolge.gueltig(['def', 'cmu', 'cmu', 'mixamo', 'mocapnet', 'bandai', 'openpose', 'smpl', 'uma']), false);
console.log(JSON.stringify({ ok: true }));
"""


class ReihenfolgeTest(SimpleTestCase):
    databases = set()

    def test_platznummern(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})
