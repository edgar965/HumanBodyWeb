# -*- coding: utf-8 -*-
"""`Hautdicke`: der Einzug der Haut bleibt auf seiner Seite des Körpers —
geprüft an Kunstflächen, in Node, mit dem echten Modul.

WARUM (Edgar, 24.09.2026, mit Bild: zwei hautfarbene Flecken an der Kappe der
Angie Sneakers): Es waren Ursulas Zehennägel. Verdeckt unter dem Schuh
versenkte `Hauteinzug` sie um 10 mm — mehr als ein kleiner Zeh dick ist; der
Nagelrand trat drüben wieder aus, vor die Schuhwand. Seither misst `Hautdicke`
je verdecktem Punkt den Abstand zur Gegenseite, und der Einzug nimmt höchstens
`ANTEIL` davon.

1. Eine Platte, 10 mm dick (oben Normale +y, unten −y): Dicke oben 10 mm,
   Grenze 4 mm.
2. Eine einzelne Fläche ohne Gegenseite: Dicke unbegrenzt.
3. Nicht ausgewählte Punkte werden nicht gemessen (unbegrenzt).
4. Eine Platte, dicker als `REICHWEITE_M` (40 mm): unbegrenzt.
5. Zwei GLEICH gerichtete Flächen 1 mm übereinander (Nagel über Haut): Die
   untere ist keine Gegenseite, die obere bleibt unbegrenzt.

Sabotage-Gegenprobe: die Abgewandt-Bedingung (`>= 0`) weggelassen macht Fall 5
rot; `tiefe <= 0` → `tiefe < -1` macht Fall 2 rot (die Nachbarn derselben
Fläche zählten mit Tiefe 0).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautdicke.js')

SKRIPT = """
const { Hautdicke } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };

// Ein Gitter 11 x 11 im Abstand von 2 mm in der Hoehe y, Normale (0, ny, 0).
function flaeche(y, ny) {
    const P = [], N = [];
    for (let i = 0; i <= 10; i++) for (let k = 0; k <= 10; k++) { P.push(0.002 * i, y, 0.002 * k); N.push(0, ny, 0); }
    return { P, N };
}
function zusammen(...teile) {
    return { P: Float64Array.from(teile.flatMap((t) => t.P)), N: Float64Array.from(teile.flatMap((t) => t.N)) };
}
const alle = (n) => new Uint8Array(n).fill(1);

// --- 1. Platte 10 mm -------------------------------------------------------
{
    const k = zusammen(flaeche(0.010, 1), flaeche(0.0, -1));
    const d = Hautdicke.dicken(k.P, k.N, alle(k.P.length / 3));
    const mitte = 5 * 11 + 5;                        // oben, Mitte
    if (Math.abs(d[mitte] - 0.010) > 1e-6) fehl('Dicke oben ' + d[mitte] + ' statt 0,010');
    if (Math.abs(Hautdicke.grenze(d[mitte]) - 0.004) > 1e-6) fehl('Grenze ' + Hautdicke.grenze(d[mitte]));
    if (Math.abs(d[121 + mitte] - 0.010) > 1e-6) fehl('Dicke unten ' + d[121 + mitte]);
}

// --- 2. Eine Flaeche ohne Gegenseite ---------------------------------------
{
    const k = zusammen(flaeche(0.0, 1));
    const d = Hautdicke.dicken(k.P, k.N, alle(k.P.length / 3));
    if (d.some((v) => Number.isFinite(v))) fehl('einzelne Flaeche hat eine Dicke');
}

// --- 3. Nur die Auswahl wird gemessen --------------------------------------
{
    const k = zusammen(flaeche(0.010, 1), flaeche(0.0, -1));
    const auswahl = new Uint8Array(k.P.length / 3);
    auswahl[60] = 1;
    const d = Hautdicke.dicken(k.P, k.N, auswahl);
    if (!Number.isFinite(d[60])) fehl('ausgewaehlter Punkt ohne Dicke');
    if (Number.isFinite(d[61])) fehl('nicht ausgewaehlter Punkt gemessen');
}

// --- 4. Dicker als die Reichweite: unbegrenzt ------------------------------
{
    const k = zusammen(flaeche(0.040, 1), flaeche(0.0, -1));
    const d = Hautdicke.dicken(k.P, k.N, alle(k.P.length / 3));
    if (Number.isFinite(d[60])) fehl('40 mm Platte begrenzt: ' + d[60]);
}

// --- 5. Nagel ueber Haut: gleich gerichtet ist keine Gegenseite -----------
{
    const k = zusammen(flaeche(0.001, 1), flaeche(0.0, 1));
    const d = Hautdicke.dicken(k.P, k.N, alle(k.P.length / 3));
    if (Number.isFinite(d[60])) fehl('gleich gerichtete Flaeche als Gegenseite gezaehlt: ' + d[60]);
}

console.log(JSON.stringify({ ok: true }));
"""


class HautdickeTest(SimpleTestCase):
    databases = set()

    def test_platte_flaeche_auswahl_reichweite(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
