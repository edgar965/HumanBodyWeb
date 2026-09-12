# -*- coding: utf-8 -*-
u"""`Reglerabbildung`: ein gemeinsamer Reglerwert, übersetzt in beide Welten.

Die Umrechnung steht zweimal — in Python (`humanbody_core.regler`, weil
HumanBody auf dem Server rechnet) und in JS (weil UMA im Browser rechnet).
Dieser Test benutzt DIESELBEN Beispielwerte wie `test_reglertabelle.py`;
laufen die beiden Seiten auseinander, wird hier oder dort einer rot.

Zusätzlich geprüft: `gilt` blendet Regler aus, die eine Figur gar nicht hat —
darunter die Gruppe „Nur UMA", die bei einer HumanBody-Figur nie erscheinen darf —
der Latin-Körpertyp führt keine Gesichtsmorphs, männliche Typen keine
Brustposition, und nicht jede UMA-Rasse kennt jeden DNA-Namen. Ohne diese
Prüfung stünde dort ein Regler, der sich ziehen lässt und nichts tut.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'reglerabbildung.js')

SKRIPT = """
const { Reglerabbildung } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const bauch = {name: 'bauch', uma: ['belly'], humanbody: ['Stomach_Volume']};
const lippen = {name: 'lippen', uma: ['lipsSize'],
                humanbody: ['Mouth_UpperlipVolume', 'Mouth_LowerlipVolume']};
const ohren = {name: 'ohren_groesse', uma: ['earsSize'],
               humanbody: ['Ears_SizeX', 'Ears_SizeY', 'Ears_SizeZ']};
const groesse = {name: 'groesse', einheit: 'cm', uma: ['height'], meta: 'height'};

// --- Mitte laesst beide Welten unveraendert ---------------------------------
pruefe('uma mitte', Reglerabbildung.umaWerte(bauch, 0), {belly: 0.5});
pruefe('hb mitte', Reglerabbildung.humanbodyWerte(bauch, 0), {Stomach_Volume: 0});

// --- Ausschlag nach beiden Seiten (wie test_reglertabelle.py) ---------------
pruefe('uma +50', Reglerabbildung.umaWerte(bauch, 50), {belly: 0.75});
pruefe('uma -100', Reglerabbildung.umaWerte(bauch, -100), {belly: 0});
pruefe('uma +100', Reglerabbildung.umaWerte(bauch, 100), {belly: 1});
pruefe('hb -30', Reglerabbildung.humanbodyWerte(bauch, -30), {Stomach_Volume: -0.3});

// --- ueber die Grenze wird geklemmt, nicht verworfen ------------------------
pruefe('uma 500', Reglerabbildung.umaWerte(bauch, 500), {belly: 1});
pruefe('hb -500', Reglerabbildung.humanbodyWerte(bauch, -500), {Stomach_Volume: -1});

// --- ein Regler stellt ALLE seine Ziele -------------------------------------
pruefe('lippen', Reglerabbildung.humanbodyWerte(lippen, -30),
       {Mouth_UpperlipVolume: -0.3, Mouth_LowerlipVolume: -0.3});

// --- Rueckweg ---------------------------------------------------------------
pruefe('aus uma', Reglerabbildung.ausUma(bauch, {belly: 0.75}), 50);
pruefe('aus uma mitte', Reglerabbildung.ausUma(bauch, {belly: 0.5}), 0);
pruefe('aus uma ohne Namen', Reglerabbildung.ausUma(bauch, {height: 0.5}), null);
// Drei Ziele, eines gestellt: der Regler steht bei einem Drittel.
pruefe('aus hb', Reglerabbildung.ausHumanbody(ohren, {Ears_SizeX: 0.6}), 20);

// --- gilt: was die Figur nicht hat, kommt nicht auf die Seite ---------------
pruefe('uma kennt den Regler', Reglerabbildung.gilt(bauch, {dna: {belly: 0.5}}), true);
pruefe('uma kennt ihn nicht', Reglerabbildung.gilt(bauch, {dna: {height: 0.5}}), false);
pruefe('hb hat alle Morphs', Reglerabbildung.gilt(
    ohren, {dna: null, morphnamen: new Set(['Ears_SizeX', 'Ears_SizeY', 'Ears_SizeZ'])}), true);
pruefe('hb fehlt einer', Reglerabbildung.gilt(
    ohren, {dna: null, morphnamen: new Set(['Ears_SizeX', 'Ears_SizeY'])}), false);
// Die Groesse haengt am Metaregler, nicht an Morphs — sie gilt immer.
pruefe('groesse gilt', Reglerabbildung.gilt(groesse, {dna: null, morphnamen: new Set()}), true);

// --- Nur-UMA-Regler: bei UMA ja, bei HumanBody NIE ------------------------
// `[].every(…)` ist true — ohne die Laengenpruefung stuende der Regler
// ausgerechnet dort, wo er nichts bewirkt (06.09.2026).
const nurUma = {name: 'nase_schief', anzeige: 'Nase schief', gruppe: 'Nur UMA',
                uma: ['noseBroken']};
pruefe('nur UMA bei UMA', Reglerabbildung.gilt(nurUma, {dna: {noseBroken: 0.5}}), true);
pruefe('nur UMA nicht bei HumanBody',
       Reglerabbildung.gilt(nurUma, {dna: null, morphnamen: new Set(['Nose_Curve'])}), false);
pruefe('nur UMA stellt keine Morphs', Reglerabbildung.humanbodyWerte(nurUma, 40), {});
pruefe('nur UMA hat keinen HumanBody-Stand',
       Reglerabbildung.ausHumanbody(nurUma, {}), null);

console.log(JSON.stringify({ok: true}));
"""


class ReglerabbildungTest(SimpleTestCase):

    databases = set()

    def test_umrechnung_und_filter(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
