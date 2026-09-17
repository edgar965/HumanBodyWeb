# -*- coding: utf-8 -*-
u"""`Saumschnitt`: verdeckte Randecken der Haut wandern unter die Stoffkante.

WARUM (Edgar, 13.09.2026, Bild vom Bund der Hose von oben: „der Innensaum
der Kleider ist eckig, der soll so sein wie die Außenhaut"): Der `Hauteinzug`
zog die verdeckte Ecke jedes Randdreiecks 1 cm nach innen — das Dreieck
kippte in den Körper, von oben ein schwarzer Zahn je Dreieck. Geprüft mit
Attrappen:

1. `kanten` liefert die offenen Kanten eines Stücks als Strecken.
2. `randecken` markiert verdeckte Ecken GEZEICHNETER Dreiecke (eine oder
   zwei Ecken verdeckt), nicht die der ausgeblendeten (drei verdeckt).
3. `verschiebung` legt die Ecke in der Tangentialebene unter den nächsten
   Punkt der nächsten KantenSTRECKE (nicht den nächsten Kantenpunkt — die
   Bundpunkte liegen 11 mm auseinander) und `UNTERKANTE_M` nach innen: eine
   Kante 4 mm daneben und 2 mm darüber ergibt (+4, 0, −1) mm, auch wenn
   ihre Endpunkte 3 cm entfernt liegen; fern der Kante (2 cm) null.

Sabotage-Gegenprobe: in `verschiebung` die Projektion in die Tangentialebene
weglassen → z wird +1 statt −1 mm → Fall 3 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'saumschnitt.js')

SKRIPT = """
const { Saumschnitt: S } = await import(MODUL);
const { Hautmaskegeometrie: G } = await import(MODUL.replace('saumschnitt.js', 'hautmaskegeometrie.js'));
const nah = (was, a, b) => {
    if (Math.abs(a - b) > 1e-6) throw new Error(was + ': ' + a + ' statt ' + b);
};
// 1. Ein Stoffviereck aus zwei Dreiecken: alle vier Punkte sind Rand.
const stoff = { punkte: Float32Array.from([0,0,0, 1,0,0, 1,1,0, 0,1,0]),
                dreiecke: Uint32Array.from([0,1,2, 0,2,3]) };
const kanten = S.kanten([stoff]);
pruefe('kanten', kanten.length, 4 * 6);
pruefe('mitten', S.mitten(kanten).length, 4 * 3);
pruefe('kanten leer', S.kanten([{ punkte: new Float32Array(0), dreiecke: new Uint32Array(0) }]).length, 0);
// 2. Randecken: (0,1,2) gemischt, (3,4,5) ganz verdeckt, (2,5,6) gemischt.
const maske = Uint8Array.from([1,1,0, 1,1,1, 0]);
pruefe('randecken', Array.from(S.randecken(maske, Uint32Array.from([0,1,2, 3,4,5, 2,5,6]))),
       [1,1,0, 0,0,1, 0]);
// 3. Verschiebung: Kante 4 mm daneben, 2 mm ueber der Haut (Normale +z),
//    ihre Endpunkte 3 cm weit weg — zaehlt die Strecke, nicht der Punkt.
const kante = Float32Array.from([0.004, -0.03, 0.002,  0.004, 0.03, 0.002]);
const gitter = G.punktgitter(S.mitten(kante), S.ZELLE_M);
const v = S.verschiebung(0, 0, 0, 0, 0, 1, kante, gitter);
nah('x', v[0], 0.004); nah('y', v[1], 0); nah('z', v[2], -S.UNTERKANTE_M);
const fern = Float32Array.from([0.02, -0.03, 0.002,  0.02, 0.03, 0.002]);
pruefe('fern', S.verschiebung(0, 0, 0, 0, 0, 1, fern, G.punktgitter(S.mitten(fern), S.ZELLE_M)), null);
console.log(JSON.stringify({ ok: true }));
"""


class SaumschnittTest(SimpleTestCase):

    def test_randecken_wandern_unter_die_kante(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
