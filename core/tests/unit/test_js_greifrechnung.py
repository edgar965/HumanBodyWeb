# -*- coding: utf-8 -*-
u"""`Greifrechnung`: was eine Mausbewegung beim Greifen (G/R/S) bedeutet.

WARUM (06.09.2026, Edgar: „ich verstehe nicht G zum Translate, bei Klick auf G
und dann Maus tut sich nichts"): G schaltete nur den Modus des Gizmos um. Jetzt
folgt die Figur der Maus. Geprüft werden die Entscheidungen darin, nicht die
Three.js-Geometrie:

1. X, Y, Z beschränken auf eine Achse — alles andere ist keine Achse.
2. Der Drehwinkel läuft gegen den Uhrzeigersinn positiv (Bildschirm-y zeigt
   nach unten) und springt am Halbkreis nicht um.
3. Direkt auf der Figurmitte ist der Winkel Zufall: dort bleibt es bei 0, sonst
   spränge die Figur beim ersten Pixel um 180 Grad.
3b. Die Größe hängt am WAAGRECHTEN Mausweg, nicht am Abstand zur Figurmitte.
   Gemessen am 06.09.2026: Mit dem Abstand als Maß änderten 200 Bildpunkte nach
   rechts die Größe um 0,2 % — die Bewegung lief auf einem Kreis um die Mitte
   (Edgar: „auch s funktioniert nicht richtig").
4. Ein Skalierfaktor ist nie 0, NaN oder Unendlich — ein `scale` von NaN macht
   die Figur unsichtbar, ohne einen Fehler zu werfen.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'greifrechnung.js')

SKRIPT = """
const { Greifrechnung } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const rund = (x) => Math.round(x * 10000) / 10000;
const grad = (x) => Math.round(x * 180 / Math.PI * 10) / 10;

// --- 1. Achsen -------------------------------------------------------------
pruefe('x', Greifrechnung.achse('x'), 'x');
pruefe('gross geschrieben', Greifrechnung.achse('Z'), 'z');
for (const t of ['a', '', ' ', 'Enter', 'Escape', null, undefined, 1]) {
    if (Greifrechnung.achse(t) !== null) throw new Error('achse(' + t + ') ist keine Achse');
}
pruefe('frei laesst alles', Greifrechnung.maskieren({x: 1, y: 2, z: 3}, null),
       {x: 1, y: 2, z: 3});
pruefe('nur y', Greifrechnung.maskieren({x: 1, y: 2, z: 3}, 'y'), {x: 0, y: 2, z: 0});
pruefe('unsinn wird 0', Greifrechnung.maskieren({x: NaN, y: 'a', z: 3}, null),
       {x: 0, y: 0, z: 3});

// --- 2. Drehwinkel ---------------------------------------------------------
const m = {x: 100, y: 100};
// rechts -> oben ist gegen den Uhrzeigersinn, also positiv
pruefe('Viertelkreis', grad(Greifrechnung.winkel(m, {x: 200, y: 100}, {x: 100, y: 0})), 90);
pruefe('andersherum', grad(Greifrechnung.winkel(m, {x: 100, y: 0}, {x: 200, y: 100})), -90);
// Ueber den Halbkreis hinaus wird der kuerzere Weg genommen, nicht +350 Grad.
const knapp = grad(Greifrechnung.winkel(m, {x: 200, y: 99}, {x: 200, y: 101}));
if (Math.abs(knapp) > 5) throw new Error('Sprung am Halbkreis: ' + knapp);

// --- 3. Auf der Mitte gibt es keinen Winkel ---------------------------------
pruefe('Start auf der Mitte', Greifrechnung.winkel(m, {x: 100, y: 100}, {x: 200, y: 100}), 0);
pruefe('Ziel auf der Mitte', Greifrechnung.winkel(m, {x: 200, y: 100}, {x: 102, y: 100}), 0);

// --- 4. Die Groesse haengt am WAAGRECHTEN Weg -------------------------------
// 300 Bildpunkte nach rechts verdoppeln, nach links halbieren.
pruefe('doppelt', rund(Greifrechnung.faktor({x: 100, y: 100}, {x: 400, y: 100})), 2);
pruefe('halb', rund(Greifrechnung.faktor({x: 400, y: 100}, {x: 100, y: 100})), 0.5);
pruefe('halber Weg', rund(Greifrechnung.faktor({x: 0, y: 0}, {x: 150, y: 0})), 1.4142);
// Senkrecht bewegt sich nichts an der Groesse.
pruefe('nur hoch', Greifrechnung.faktor({x: 100, y: 100}, {x: 100, y: 900}), 1);
// Unsinn ergibt 1, nie NaN: ein `scale` von NaN macht die Figur unsichtbar.
for (const [von, nach] of [[{x: 200, y: 100}, {x: NaN, y: 100}],
                           [{x: NaN, y: 100}, {x: 200, y: 100}],
                           [{x: 0, y: 0}, {x: 1e9, y: 0}],
                           [{x: 0, y: 0}, {x: -1e9, y: 0}],
                           [null, undefined]]) {
    const f = Greifrechnung.faktor(von, nach);
    if (f !== 1) throw new Error('Faktor ' + f + ' statt 1');
}

// --- 5. Die Zeile im Bild --------------------------------------------------
pruefe('Verschieben', Greifrechnung.anzeige('translate', {x: 0.5, y: 0, z: -1.25}, null),
       'Verschieben: 0.50 / 0.00 / -1.25 m');
pruefe('mit Achse', Greifrechnung.anzeige('translate', {x: 0.5, y: 0, z: 0}, 'x'),
       'Verschieben X: 0.50 / 0.00 / 0.00 m');
pruefe('Drehen', Greifrechnung.anzeige('rotate', Math.PI / 2, 'y'), 'Drehen Y: 90.0\\u00b0');
pruefe('Groesse', Greifrechnung.anzeige('scale', 1.5, null), 'Gr\\u00f6\\u00dfe: \\u00d71.500');

console.log(JSON.stringify({ok: true}));
"""


class GreifrechnungTest(SimpleTestCase):

    databases = set()

    def test_achse_winkel_und_faktor(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
