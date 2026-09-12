# -*- coding: utf-8 -*-
u"""`Groessenangleich`: der Faktor, mit dem eine neue Figur auf die Höhe der
vorhandenen kommt.

WARUM (06.09.2026, Edgar: „beim Laden eines neuen Modells, immer mit der
gleichen Größe wie das andere"): Eine UMA-Figur von 2,05 m stand neben einer
HumanBody-Figur von 1,75 m. Geprüft wird die ENTSCHEIDUNG, nicht die Messung:

1. Ein echter Unterschied wird ausgeglichen.
2. Ein Unterschied unter 2 % ist Messrauschen und bleibt — sonst wackelte
   jede Figur beim Laden um ein Prozent.
3. Ein absurder Faktor (Figur zehnmal so groß) heißt kaputte Messung, nicht
   „jetzt kräftig skalieren".
4. Fehlende oder unsinnige Werte ergeben 1, nie NaN oder Unendlich — ein
   `scale` von NaN macht die Figur unsichtbar, ohne einen Fehler zu werfen.

Die Messung selbst steht in `figurplatzierung.js` und ist Three.js-Sache;
sie unterscheidet die Figurarten, weil die Bounding-Box das Skinning einer
UMA-Figur nicht sieht.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'groessenangleich.js')

SKRIPT = """
const { Groessenangleich } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const rund = (x) => Math.round(x * 10000) / 10000;

// --- 1. Der Fall, um den es geht: 2,05 m neben 1,75 m ----------------------
pruefe('gross auf klein', rund(Groessenangleich.faktor(2.05, 1.75)), 0.8537);
pruefe('klein auf gross', rund(Groessenangleich.faktor(1.68, 2.07)), 1.2321);
pruefe('greift', Groessenangleich.greift(2.05, 1.75), true);

// --- 2. Unter 2 % bleibt es, wie es ist ------------------------------------
// Echter Messwert vom 06.09.2026: 1,680 m neben 1,689 m.
pruefe('Messrauschen', Groessenangleich.faktor(1.680, 1.6894), 1);
pruefe('greift nicht', Groessenangleich.greift(1.680, 1.6894), false);
pruefe('knapp darunter', Groessenangleich.faktor(1.0, 1.019), 1);
pruefe('knapp darueber', rund(Groessenangleich.faktor(1.0, 1.021)), 1.021);

// --- 3. Absurdes heisst kaputte Messung ------------------------------------
pruefe('zehnfach', Groessenangleich.faktor(0.2, 2.0), 1);
pruefe('ein Zehntel', Groessenangleich.faktor(2.0, 0.1), 1);

// --- 4. Unsinnige Werte ergeben 1, nie NaN ---------------------------------
for (const [a, b] of [[0, 1.7], [1.7, 0], [-1, 1.7], [NaN, 1.7], [1.7, NaN],
                      [null, 1.7], [undefined, undefined], [Infinity, 1.7]]) {
    const f = Groessenangleich.faktor(a, b);
    if (f !== 1) throw new Error(`faktor(${a}, ${b}) = ${f} statt 1`);
}

console.log(JSON.stringify({ok: true}));
"""


class GroessenangleichTest(SimpleTestCase):

    databases = set()

    def test_der_faktor_gleicht_aus_ohne_zu_zappeln(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
