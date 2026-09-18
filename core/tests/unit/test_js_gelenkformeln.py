# -*- coding: utf-8 -*-
u"""`Gelenkformeln` (`gemeinsam/gelenkformeln.js`): Daz' JCM-Formelgraph im
Browser, ohne Three.js (18.09.2026, Edgar: „Mach Daz' JCMs").

Derselbe Kunstgraph wie in `test_genesis9_gelenke_lipsync` (Python): ein
JCM `clamp(rot/35) × Schalter`, ein Zwei-Achsen-JCM ueber zwei Zwischen-
kanaele, ein Spline-JCM mit Knoten auf dem Stapel. Python und JS muessen
dieselben Werte liefern — das ist die Deckungsprobe der beiden Rechner.

Sabotage-Gegenproben: `clamped` im JS ignorieren -> Fall 1 rot (1,4 statt 1);
`zahlen[0]` durch `zahlen[zahlen.length - 1]` (die Knotenzahl) ersetzen ->
Fall 2 rot; Kreis-Schutz (`offen`) weg -> Fall 3 haengt/rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'gelenkformeln.js')

SKRIPT = """
const { Gelenkformeln: G } = await import(MODUL);
const rot = (achse) => ({ op: 'push', kanal: 'l_thigh?rotation/' + achse });
const graph = {
    kanaele: {
        cbs_x35p: { vorgabe: 0, min: 0, max: 1, clamped: true, formeln: [
            { stufe: 'sum', ops: [rot('x'), { op: 'push', val: 1 / 35 },
                                  { op: 'mult' }] },
            { stufe: 'mult', ops: [{ op: 'push', kanal: 'schalter' }] }] },
        cbs_zwei: { vorgabe: 0, min: 0, max: 1, clamped: true, formeln: [
            { stufe: 'sum', ops: [{ op: 'push', kanal: 'l_thigh:CTRLMD_X' }] },
            { stufe: 'mult', ops: [{ op: 'push', kanal: 'l_thigh:CTRLMD_Z' }] }] },
        cbs_spline: { vorgabe: 0, min: 0, max: 1, clamped: true, formeln: [
            { stufe: 'sum', ops: [rot('x'), { op: 'push', val: [-135, 1, 0, 0, 0] },
                                  { op: 'push', val: [-75, 0, 0, 0, 0] },
                                  { op: 'push', val: 3 }, { op: 'spline_tcb' }] }] },
        'l_thigh:CTRLMD_X': { vorgabe: 0, min: 0, max: 1, clamped: true, formeln: [
            { stufe: 'sum', ops: [rot('x'), { op: 'push', val: -1 / 115 },
                                  { op: 'mult' }] }] },
        'l_thigh:CTRLMD_Z': { vorgabe: 0, min: 0, max: 1, clamped: true, formeln: [
            { stufe: 'sum', ops: [rot('z'), { op: 'push', val: 1 / 90 },
                                  { op: 'mult' }] }] },
        schalter: { vorgabe: 1, min: 0, max: 1, clamped: true, formeln: [] },
        kreis: { vorgabe: 0.25, min: 0, max: 1, clamped: true, formeln: [
            { stufe: 'sum', ops: [{ op: 'push', kanal: 'kreis' },
                                  { op: 'push', val: 2 }, { op: 'mult' }] }] },
    },
    morphe: ['cbs_x35p', 'cbs_zwei', 'cbs_spline', 'kreis'],
    knochen: ['l_thigh'],
};
const w1 = G.werte(graph, G.eingaben({ l_thigh: [17.5, 0, 0] }));
const w2 = G.werte(graph, G.eingaben({ l_thigh: [49, 0, 0] }));
const w3 = G.werte(graph, G.eingaben({ l_thigh: [-115, 0, 45] }));
const w4 = G.werte(graph, G.eingaben({ l_thigh: [-110, 0, 0] }));
const w5 = G.werte(graph, G.eingaben({ l_thigh: [-20, 0, 0] }));
console.log(JSON.stringify({
    halb: w1.cbs_x35p, voll: w2.cbs_x35p, zwei: w3.cbs_zwei, spline: w4.cbs_spline,
    negativ: w5.cbs_x35p ?? 0, kreis: w1.kreis, zweiOhneZ: w2.cbs_zwei ?? 0,
}));
"""


class GelenkformelnTest(SimpleTestCase):

    databases = set()

    def test_1_clamp_und_schalter(self):
        aus = MODUL.laufen(SKRIPT)
        self.assertAlmostEqual(aus['halb'], 0.5, places=6)
        self.assertAlmostEqual(aus['voll'], 1.0, places=6)
        self.assertEqual(aus['negativ'], 0)

    def test_2_zwei_achsen_und_spline(self):
        aus = MODUL.laufen(SKRIPT)
        self.assertAlmostEqual(aus['zwei'], 0.5, places=6)
        self.assertEqual(aus['zweiOhneZ'], 0)
        self.assertAlmostEqual(aus['spline'], 35 / 60, places=6)

    def test_3_kreis_bricht_ab(self):
        u"""Ein Kanal, der sich selbst liest, bekommt beim zweiten Betreten
        seine Vorgabe: (0,25 + 0,25 · 2) = 0,75, kein Endlosrekurs."""
        aus = MODUL.laufen(SKRIPT)
        self.assertAlmostEqual(aus['kreis'], 0.75, places=6)
