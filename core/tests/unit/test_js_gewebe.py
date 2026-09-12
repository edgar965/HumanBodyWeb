# -*- coding: utf-8 -*-
u"""`Gewebe`: die Bindung, die einem Kleidungsstück Struktur gibt.

WARUM (Edgar, 10.09.2026: „Meine Kleider sehen mir noch zu schlecht aus"):
Ein GarmentCode-Stück war eine einfarbige Fläche. Die Normalkarte, die das
ändert, wird gerechnet statt geladen — und ist deshalb prüfbar.

GEPRÜFT WIRD, WAS FALSCH SEIN KANN, ohne dass es auffällt:

1. **Die Kachel muss kacheln.** Sie läuft rund fünfzigmal über ein T-Shirt;
   eine Fuge am Rand ergäbe ein Gitter über das ganze Stück. Der Prüfpunkt
   ist nicht „Rand gleich Rand" — die beiden Ränder gehören zu
   verschiedenen Fäden und sind zu Recht verschieden. Er ist: Der Sprung
   über den Rand darf nicht größer sein als der größte Sprung im Inneren.
   (Der erste Anlauf prüfte das Falsche und meldete 0,434 „Randsprung" für
   eine völlig saubere Kachel — `~/.claude/rules/analysewerkzeuge.md`.)
2. **Es muss eine Leinwandbindung sein, kein Waffelmuster.** Bei
   Leinwandbindung wiederholt sich das Bild erst nach ZWEI Fäden: Kettfaden
   0 läuft über Schuss 0 und unter Schuss 1, Kettfaden 1 umgekehrt. Ein
   Feld mit Periode 1 wäre ein Gitter aus gleichen Hügeln — es sähe von
   weitem ähnlich aus und wäre kein Gewebe.
3. **Die Kachelgröße hängt am Stoffmaß, nicht am UV-Bereich.** Jedes
   Schnittmuster legt sein UV auf 0..1; gemessen sind das beim T-Shirt
   1,07 m Stoff und bei der Hose 1,70 m. Ohne die Umrechnung bekäme die
   Hose ein um zwei Drittel gröberes Gewebe.
4. **Die Normalkarte muss geneigt sein.** Ein Feld aus lauter (128,128,255)
   ist eine gültige Normalkarte, die nichts tut — der stille Fehlerfall.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'gewebe.js')

SKRIPT = """
const { Gewebe } = await import(MODUL);
const pruefe = (was, bedingung, zusatz) => {
    if (!bedingung) throw new Error(was + (zusatz === undefined ? '' : ': ' + zusatz));
};
const g = 128, f = 8, b = g / f;
const h = Gewebe.hoehenfeld(g, f);

// --- 1. Die Kachel kachelt --------------------------------------------------
let innen = 0, rand = 0;
for (let y = 0; y < g; y++) {
    for (let x = 1; x < g; x++) {
        innen = Math.max(innen, Math.abs(h[y * g + x] - h[y * g + x - 1]));
    }
    rand = Math.max(rand, Math.abs(h[y * g] - h[y * g + g - 1]));
}
pruefe('Randsprung groesser als im Inneren', rand <= innen + 1e-9,
       rand.toFixed(4) + ' gegen ' + innen.toFixed(4));

// --- 2. Leinwandbindung: das Schachbrett ------------------------------------
// Drei Eigenschaften, die genau die Leinwandbindung beschreiben:
//   a) nach ZWEI Faeden wiederholt sich alles (die Kachel darf dort trennen),
//   b) eine DIAGONALE Verschiebung um einen Faden aendert nichts — sie fuehrt
//      auf eine Kreuzung derselben Parität,
//   c) x und y sind vertauschbar: Kette und Schuss sind gleichwertig
//      verschraenkt.
// b) und c) sind die scharfen. Ein erster Versuch prueft nur „Periode 1 gilt
// nicht" — der bleibt gruen, wenn die Verschraenkung ganz fehlt (gemessen:
// 368 von 1.064 statt 1.064 von 1.064), also wenn immer dieselbe Fadenschar
// oben liegt.
let nachZwei = 0, diagonal = 0, getauscht = 0, faelle = 0;
for (let x = 0; x < 4 * b; x += 1.7) {
    for (let y = 0; y < 4 * b; y += 2.3) {
        faelle++;
        const hier = Gewebe.hoehe(x, y, b);
        if (Math.abs(hier - Gewebe.hoehe(x + 2 * b, y, b)) < 1e-9) nachZwei++;
        if (Math.abs(hier - Gewebe.hoehe(x + b, y + b, b)) < 1e-9) diagonal++;
        if (Math.abs(Gewebe.hoehe(x + b, y, b)
                     - Gewebe.hoehe(x, y + b, b)) < 1e-9) getauscht++;
    }
}
pruefe('Periode ist nicht zwei Faeden', nachZwei === faelle, nachZwei + '/' + faelle);
pruefe('Die Kreuzungen wechseln nicht ab', diagonal === faelle,
       diagonal + '/' + faelle);
pruefe('Kette und Schuss sind nicht gleichwertig', getauscht === faelle,
       getauscht + '/' + faelle);

// --- 3. Werte bleiben im Bereich, und es gibt Taeler -------------------------
let min = Infinity, max = -Infinity;
for (const v of h) { min = Math.min(min, v); max = Math.max(max, v); }
pruefe('Hoehe verlaesst 0..1', min >= 0 && max <= 1, min + '..' + max);
pruefe('Hoehenfeld ist flach', max - min > 0.3, (max - min).toFixed(3));

// --- 4. Die Kachelgroesse folgt dem Stoffmass -------------------------------
const tshirt = Gewebe.wiederholung(1.067);
const hose = Gewebe.wiederholung(1.702);
pruefe('Hose kachelt nicht oefter als das T-Shirt', hose > tshirt,
       hose.toFixed(1) + ' gegen ' + tshirt.toFixed(1));
pruefe('Verhaeltnis stimmt nicht mit den Massen ueberein',
       Math.abs(hose / tshirt - 1.702 / 1.067) < 1e-6);
// Ohne Mass darf sie nicht 0, NaN oder Unendlich werden - eine Wiederholung
// von 0 legt die ganze Kachel auf einen Punkt, und die Flaeche ist einfarbig.
for (const unsinn of [0, -1, null, undefined, NaN, 'a']) {
    const w = Gewebe.wiederholung(unsinn);
    pruefe('Wiederholung unbrauchbar bei ' + unsinn, Number.isFinite(w) && w > 0, w);
}

// --- 5. Die Normalkarte ist wirklich geneigt --------------------------------
const n = Gewebe.normalfeld(g, f);
pruefe('Normalfeld hat die falsche Groesse', n.length === g * g * 4, n.length);
let flach = 0, geneigt = 0;
for (let i = 0; i < g * g; i++) {
    const dx = Math.abs(n[i * 4] - 128), dy = Math.abs(n[i * 4 + 1] - 128);
    if (dx < 2 && dy < 2) flach++;
    if (dx > 20 || dy > 20) geneigt++;
    if (n[i * 4 + 2] < 128) throw new Error('Normale zeigt nach hinten bei ' + i);
    if (n[i * 4 + 3] !== 255) throw new Error('Alpha nicht deckend bei ' + i);
}
pruefe('Normalkarte ist fast ueberall flach', flach < g * g * 0.1, flach);
pruefe('Normalkarte hat kaum Neigung', geneigt > g * g * 0.5, geneigt);

console.log(JSON.stringify({ok: true, rand: rand, innen: innen, geneigt: geneigt}));
"""


class GewebeTest(SimpleTestCase):

    databases = set()

    def test_kachel_bindung_und_normalen(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
