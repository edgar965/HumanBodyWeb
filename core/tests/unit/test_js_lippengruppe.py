# -*- coding: utf-8 -*-
u"""`Lippengruppe`: Lippendreiecke aus der Haut in eine eigene Materialgruppe.

WARUM (Edgar, 12.09.2026: „es fehlen noch die Lippen (farbe usw.)"): Das
Netz hat keine Lippengruppe; der Server nennt die Lippenpunkte, der
Browser sortiert die Hautdreiecke um. Geprüft an einem kleinen Index —
Haut mit vier Dreiecken (zwei davon ganz aus Lippenpunkten, eines nur
teilweise), dahinter eine Sklera-Gruppe:

1. Die zwei Lippendreiecke wandern ans Ende des Hautbereichs, die Haut
   schrumpft um sechs Einträge, die Sklera behält ihren Bereich, die neue
   Gruppe 11 liegt genau dazwischen — und KEIN Dreieck geht verloren.
2. Ein Dreieck, dessen Ecken nur teilweise Lippe sind, bleibt Haut.
3. Ohne Lippenpunkte, ohne Hautgruppe oder mit schon vorhandener Gruppe 11
   kommt alles unverändert zurück (`dreiecke` 0).

Sabotage-Gegenprobe: `&& menge.has(index[k + 2])` weg → Fall 2 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'lippengruppe.js')

SKRIPT = """
const { Lippengruppe: L } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};
// Haut: (0,1,2) (3,4,5) (6,7,8) (2,3,9); Sklera: (10,11,12). Lippen: 3,4,5,6,7,8,9
const index = Uint32Array.from([0,1,2, 3,4,5, 6,7,8, 2,3,9, 10,11,12]);
const gruppen = [{ start: 0, count: 12, materialIndex: 0 },
                 { start: 12, count: 3, materialIndex: 4 }];
const aus = L.abspalten(index, gruppen, [3, 4, 5, 6, 7, 8, 9]);
pruefe('dreiecke', aus.dreiecke, 2);
pruefe('index', Array.from(aus.index), [0,1,2, 2,3,9, 3,4,5, 6,7,8, 10,11,12]);
pruefe('gruppen', aus.gruppen, [
    { start: 0, count: 6, materialIndex: 0 }, { start: 12, count: 3, materialIndex: 4 },
    { start: 6, count: 6, materialIndex: 11 }]);
pruefe('original unberuehrt', Array.from(index),
       [0,1,2, 3,4,5, 6,7,8, 2,3,9, 10,11,12]);
// alle Dreiecke noch da
const sortiert = (a) => {
    const t = [];
    for (let k = 0; k < a.length; k += 3) t.push([a[k], a[k + 1], a[k + 2]].join('-'));
    return t.sort();
};
pruefe('vollstaendig', sortiert(aus.index), sortiert(index));
// nichts zu tun
pruefe('ohne lippen', L.abspalten(index, gruppen, []).dreiecke, 0);
pruefe('ohne haut', L.abspalten(index, [gruppen[1]], [3, 4, 5]).dreiecke, 0);
pruefe('schon abgespalten', L.abspalten(aus.index, aus.gruppen, [3, 4, 5]).dreiecke, 0);
pruefe('teilweise bleibt haut', L.abspalten(index, gruppen, [0, 1]).dreiecke, 0);
console.log(JSON.stringify({ ok: true }));
"""


class LippengruppeTest(SimpleTestCase):

    def test_abspalten(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
