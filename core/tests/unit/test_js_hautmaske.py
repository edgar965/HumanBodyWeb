# -*- coding: utf-8 -*-
u"""`Hautmaske`: welche Körperpunkte unter dem Stoff liegen — geprüft am
Kunstkörper, in Node, mit dem echten Modul.

WARUM (Edgar, 11.09.2026, mit Bild: „natürlich ist es die Haut die durch die
Verformung durchkommt!!!"): Eine 2-mm-Leggings lässt in Dance1 an Bund,
Schritt und Knie Haut heraus, und kein Gewichtssatz ändert das. Deshalb wird
die Haut unter dem Stoff nicht mehr gezeichnet (`delete_verts` bei MakeHuman).
Hier wird die Entscheidung geprüft, WAS als „unter dem Stoff" gilt:

1. Ein anliegendes Stoffrohr (2 mm) um einen Körperzylinder verdeckt die
   Punkte darunter bis zur Kante — und NUR die: darüber und darunter bleibt
   die Haut. Ein lockeres Rohr (10 mm) lässt an jeder offenen Kante zwei
   Ringe frei (`RANDRINGE`, nur an Kanten über `ENG_M`) — Edgars zweiter
   Befund vom selben Abend: Der freie Streifen am Bund der 2-mm-Leggings war
   genau die Haut, die weiter herauskam.
2. Stoff, der 30 mm entfernt steht, verdeckt nichts (`ABSTAND_M` 25 mm).
3. Stoff IM Körper (10 mm unter der Haut) verdeckt nichts — bis 5 mm gilt er
   noch als „darüber" (`TIEFE_M`), genau die Fälle, um die es geht.
4. Die Wicklung des Körpers ist gleichgültig: rückwärts gewickelt kommt
   dieselbe Maske heraus (signiertes Volumen, nicht Mehrheit).
5. `indexOhne` wirft nur Dreiecke, deren DREI Ecken verdeckt sind, und zieht
   die Materialgruppen nach — Start, Anzahl und Materialnummer.
6. Eine freie Insel im Verdeckten (Haut unter einem Loch im Stoff, ringsum
   verdeckt) wird geschlossen (`Maskeninseln`); mit `inseln: 0` bleibt sie —
   der Fall der Achselfalte, in der die Hautnormale keinen Stoff trifft.

Sabotage-Gegenprobe: `t >= -tiefe` → `true` in `_einStueck` macht Fall 3 rot;
`Math.abs(d) > eng` → `true` in `lockereRandpunkte` macht Fall 1 rot (Streifen
am anliegenden Rohr); `vol >= 0 ? 1 : -1` → `1` (`hautmaskegeometrie.js`)
macht Fall 4 rot; `maske[a] && maske[b] && maske[c]` → `maske[a] || ...`
macht Fall 5 rot; `g <= hoechstens && g < groesste` → `false` (`maskeninseln.js`)
macht Fall 6 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautmaske.js')

SKRIPT = """
const { Hautmaske } = await import(MODUL);
const fehl = (was) => { throw new Error(was); };

// Ein Zylinder um die y-Achse: `ringe` Reihen, `n` Punkte je Reihe, mit
// Dreiecken (Wicklung: nach aussen, wenn `aussen`).
function zylinder(radius, y0, y1, ringe, n, aussen = true) {
    const P = [], T = [];
    for (let r = 0; r < ringe; r++) {
        const y = y0 + (y1 - y0) * r / (ringe - 1);
        for (let i = 0; i < n; i++) {
            const w = 2 * Math.PI * i / n;
            P.push(radius * Math.cos(w), y, radius * Math.sin(w));
        }
    }
    for (let r = 0; r + 1 < ringe; r++) for (let i = 0; i < n; i++) {
        const a = r * n + i, b = r * n + (i + 1) % n, c = (r + 1) * n + i, d = (r + 1) * n + (i + 1) % n;
        // Nach aussen: gegen den Uhrzeigersinn von aussen gesehen.
        if (aussen) T.push(a, c, b, b, c, d); else T.push(a, b, c, b, d, c);
    }
    return { P: Float32Array.from(P), T: Uint32Array.from(T), n, ringe, y0, y1 };
}
const yVon = (k, i) => k.y0 + (k.y1 - k.y0) * Math.floor(i / k.n) / (k.ringe - 1);
const als = (k) => ({ punkte: k.P, dreiecke: k.T });

// Koerper: Radius 10 cm, y 0..1, Reihen alle 2 cm.
const koerper = zylinder(0.10, 0.0, 1.0, 51, 36, true);
// Stoff: Radius 10,2 cm (2 mm ueber der Haut), y 0,30..0,70, Reihen alle 1 cm.
const stoff = zylinder(0.102, 0.30, 0.70, 41, 36, true);

// --- 1. Das anliegende Rohr verdeckt, was darunter liegt — bis zur Kante --
let maske = Hautmaske.verdeckt(koerper.P, koerper.T, [als(stoff)]);
let unter = 0, frei = 0, falsch = [];
for (let i = 0; i < maske.length; i++) {
    const y = yVon(koerper, i);
    // 2 mm ueber der Haut: die Kante liegt AN, kein freier Randstreifen.
    const soll = (y > 0.30 + 0.005 && y < 0.70 - 0.005) ? 1 : (y < 0.30 - 0.005 || y > 0.70 + 0.005) ? 0 : null;
    if (soll === null) continue;                      // genau auf der Kante: beides erlaubt
    if (maske[i] !== soll) falsch.push([+y.toFixed(2), maske[i]]);
    if (soll) unter++; else frei++;
}
if (falsch.length) fehl('Maske (anliegend) falsch bei ' + JSON.stringify(falsch.slice(0, 6)));
if (unter < 500 || frei < 1000) fehl('Kunstkoerper zu klein: ' + unter + ' / ' + frei);

// --- 1b. Das lockere Rohr (10 mm) laesst zwei Ringe an der Kante frei ------
const locker = zylinder(0.110, 0.30, 0.70, 41, 36, true);
const maskeLocker = Hautmaske.verdeckt(koerper.P, koerper.T, [als(locker)]);
falsch = [];
for (let i = 0; i < maskeLocker.length; i++) {
    const y = yVon(koerper, i);
    // Zwei Ringe bei 1 cm Reihenabstand: bis 2 cm hinter der Kante bleibt die Haut.
    const soll = (y > 0.30 + 0.025 && y < 0.70 - 0.025) ? 1 : (y < 0.30 + 0.015 || y > 0.70 - 0.015) ? 0 : null;
    if (soll === null) continue;
    if (maskeLocker[i] !== soll) falsch.push([+y.toFixed(3), maskeLocker[i]]);
}
if (falsch.length) fehl('Maske (locker) falsch bei ' + JSON.stringify(falsch.slice(0, 6)));
let lockerUnter = 0; for (const v of maskeLocker) lockerUnter += v;
if (lockerUnter < 500) fehl('10 mm Abstand muss verdecken: ' + lockerUnter);

// --- 2. Stoff 30 mm entfernt verdeckt nichts -------------------------------
const weit = zylinder(0.13, 0.30, 0.70, 41, 36, true);
maske = Hautmaske.verdeckt(koerper.P, koerper.T, [als(weit)]);
if (maske.some((v) => v)) fehl('30 mm Abstand gilt als verdeckt');

// --- 3. Stoff IM Koerper (10 mm) verdeckt nichts, 3 mm darin schon ---------
const innen = zylinder(0.090, 0.30, 0.70, 41, 36, true);
maske = Hautmaske.verdeckt(koerper.P, koerper.T, [als(innen)]);
if (maske.some((v) => v)) fehl('Stoff 10 mm in der Haut gilt als darueber');
const knapp = zylinder(0.097, 0.30, 0.70, 41, 36, true);
maske = Hautmaske.verdeckt(koerper.P, koerper.T, [als(knapp)]);
let mitte = 0; for (let i = 0; i < maske.length; i++) { const y = yVon(koerper, i); if (y > 0.4 && y < 0.6 && maske[i]) mitte++; }
if (mitte < 300) fehl('Stoff 3 mm in der Haut muss noch verdecken: ' + mitte);

// --- 4. Rueckwaerts gewickelt: dieselbe Maske ------------------------------
// Mit 10 mm Abstand, nicht 2: Bei 2 mm deckt die Tiefentoleranz (5 mm) ein
// falsches Vorzeichen zu — die Sabotage `vz = 1` blieb damit gruen.
const rueckwaerts = zylinder(0.10, 0.0, 1.0, 51, 36, false);
const maskeVor = maskeLocker;
const maskeRueck = Hautmaske.verdeckt(rueckwaerts.P, rueckwaerts.T, [als(locker)]);
for (let i = 0; i < maskeVor.length; i++) if (maskeVor[i] !== maskeRueck[i]) fehl('Wicklung aendert die Maske bei ' + i);

// --- 5. Index ohne verdeckte Dreiecke, Gruppen nachgezogen -----------------
const T = koerper.T;
const gruppen = [{ start: 0, count: 600, materialIndex: 0 },
                 { start: 600, count: T.length - 600, materialIndex: 3 }];
const neu = Hautmaske.indexOhne(T, gruppen, maskeVor);
let erwartetWeg = 0;
for (let k = 0; k < T.length; k += 3) if (maskeVor[T[k]] && maskeVor[T[k + 1]] && maskeVor[T[k + 2]]) erwartetWeg++;
if (neu.entfernt !== erwartetWeg) fehl('entfernt ' + neu.entfernt + ' statt ' + erwartetWeg);
if (neu.index.length !== T.length - 3 * erwartetWeg) fehl('Indexlaenge ' + neu.index.length);
if (neu.gruppen.length !== 2 || neu.gruppen[0].start !== 0 || neu.gruppen[1].start !== neu.gruppen[0].count
    || neu.gruppen[0].count + neu.gruppen[1].count !== neu.index.length
    || neu.gruppen[1].materialIndex !== 3) fehl('Gruppen ' + JSON.stringify(neu.gruppen));
// Kein Dreieck mit einer freien Ecke ist verschwunden.
let teilweise = 0; for (let k = 0; k < T.length; k += 3) { const m = maskeVor[T[k]] + maskeVor[T[k + 1]] + maskeVor[T[k + 2]]; if (m > 0 && m < 3) teilweise++; }
if (teilweise === 0) fehl('Kunstkoerper hat keine Randdreiecke');
// Ohne Gruppen: ein Index, keine Gruppen.
const ohne = Hautmaske.indexOhne(T, [], maskeVor);
if (ohne.gruppen.length !== 0 || ohne.index.length !== neu.index.length) fehl('ohne Gruppen: ' + ohne.index.length);

// --- 6. Eine freie Insel im Verdeckten wird geschlossen ------------------
// Loch im Stoff: alle Dreiecke um einen Stoffpunkt in der Mitte entfallen.
{
    const mitte = 20 * stoff.n + 7;
    const T6 = [];
    for (let k = 0; k < stoff.T.length; k += 3) if (stoff.T[k] !== mitte && stoff.T[k+1] !== mitte && stoff.T[k+2] !== mitte) T6.push(stoff.T[k], stoff.T[k+1], stoff.T[k+2]);
    const loch = { punkte: stoff.P, dreiecke: Uint32Array.from(T6) };
    // Das Loch ist auch eine offene Kante — anliegend (2 mm), also ohne Randstreifen.
    const roh = Hautmaske.verdeckt(koerper.P, koerper.T, [loch], { inseln: 0 });
    const zu = Hautmaske.verdeckt(koerper.P, koerper.T, [loch]);
    let frei = 0, geschlossen = 0;
    for (let i = 0; i < roh.length; i++) { const y = yVon(koerper, i); if (y > 0.35 && y < 0.65) { if (!roh[i]) frei++; if (!roh[i] && zu[i]) geschlossen++; } }
    if (frei === 0) fehl('Kunstloch laesst keine Haut frei');
    if (geschlossen !== frei) fehl('Insel nicht geschlossen: ' + geschlossen + ' von ' + frei);
}

console.log(JSON.stringify({ ok: true, unter, frei, entfernt: neu.entfernt }));
"""


class HautmaskeTest(SimpleTestCase):

    databases = set()

    def test_rohr_abstand_tiefe_wicklung_und_index(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe['entfernt'], 0)
