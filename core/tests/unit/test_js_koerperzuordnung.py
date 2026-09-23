# -*- coding: utf-8 -*-
"""`Koerperzuordnung`: welche Gliedmaße ein Körperpunkt trägt.

Herausgelöst aus `stoffkapseln.js` (22.09.2026, Fund Edgar: „bei Animation
Spagat geht der Arm in den Körper" / „die Hose ist zerrissen"): Ein an die
Beinoberfläche gebundener Jeans-Punkt (Schicht 2) wurde nie gegen die
Kapsel eines FREMDEN Körperteils (Arm) geprüft. Die Gruppen-Zuordnung ist
die Grundlage des Filters in `oberflaecheglsl.js`.

1. `seite`: Daz (`l_`/`r_`-Präfix) und Rigify (`.L`/`.R`-Suffix), beides.
2. `gruppenindex`: Arm/Bein je Seite, alles andere (Rumpf, Kopf, Finger ohne
   Seite — kommt nicht vor, aber sicherheitshalber) 0.
3. `staerksterKnochen`: der Index mit dem größten `skinWeight` je Punkt.
4. `gruppeJePunkt`: kombiniert beides, gecacht an der Geometrie.

Sabotage-Gegenprobe: `abs(ka.w - bindgruppe) < 0.5` im Shader vergleicht
Gruppen-IDs als float — `gruppenindex` muss deshalb GANZE Zahlen liefern,
sonst vergleicht der Shader nie exakt.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('..', 'viewer', 'gemeinsam', 'koerperzuordnung.js')

SKRIPT = """
const { Koerperzuordnung } = await import(MODUL);
const fehler = [];
const fehl = (t) => fehler.push(t);

// --- 1. Seite -----------------------------------------------------------
if (Koerperzuordnung.seite('l_upperarm') !== 'l') fehl('Daz links: ' + Koerperzuordnung.seite('l_upperarm'));
if (Koerperzuordnung.seite('r_thigh') !== 'r') fehl('Daz rechts: ' + Koerperzuordnung.seite('r_thigh'));
if (Koerperzuordnung.seite('DEF-forearm.L') !== 'l') fehl('Rigify links: ' + Koerperzuordnung.seite('DEF-forearm.L'));
if (Koerperzuordnung.seite('DEF-thigh.R') !== 'r') fehl('Rigify rechts: ' + Koerperzuordnung.seite('DEF-thigh.R'));
if (Koerperzuordnung.seite('spine1') !== '') fehl('Rumpf hat eine Seite: ' + Koerperzuordnung.seite('spine1'));

// --- 2. Gruppenindex ------------------------------------------------------
const G = Koerperzuordnung.GRUPPEN;
const faelle = [
    ['l_upperarm', G.l_arm], ['l_forearm', G.l_arm], ['l_hand', G.l_arm],
    ['l_forearmtwist1', G.l_arm], ['r_thumb1', G.r_arm],
    ['l_thigh', G.l_bein], ['l_shin', G.l_bein], ['l_foot', G.l_bein], ['l_thightwist1', G.l_bein],
    ['DEF-upper_arm.L', G.l_arm], ['DEF-thigh.R', G.r_bein],
    ['spine1', 0], ['hip', 0], ['head', 0], ['neck1', 0],
];
for (const [name, soll] of faelle) {
    const ist = Koerperzuordnung.gruppenindex(name);
    if (ist !== soll) fehl(`${name}: erwartet ${soll}, war ${ist}`);
    if (!Number.isInteger(ist)) fehl(`${name}: keine ganze Zahl (${ist}) — der Shader vergleicht als float`);
}
// Kein Doppelvergabe: jede Nicht-Null-Gruppe ist eindeutig.
const werte = new Set(Object.values(G));
if (werte.size !== Object.values(G).length) fehl('Gruppen-IDs nicht eindeutig: ' + JSON.stringify(G));
if (werte.has(0)) fehl('0 ist "keine Gruppe" und darf nicht vergeben sein');

// --- 3. staerksterKnochen -------------------------------------------------
// Zwei Punkte, vier Gewichte je Punkt (skinIndex/skinWeight wie im echten Netz).
const netz = {
    geometry: {
        attributes: {
            position: { count: 2 },
            skinIndex: { array: new Float32Array([0, 1, 2, 3,  5, 2, 0, 1]) },
            skinWeight: { array: new Float32Array([0.1, 0.7, 0.15, 0.05,  0.2, 0.6, 0.1, 0.1]) },
        },
    },
};
const knochen = Koerperzuordnung.staerksterKnochen(netz);
if (knochen[0] !== 1) fehl('Punkt 0, staerkstes Gewicht bei index[1]=1: ' + knochen[0]);
if (knochen[1] !== 2) fehl('Punkt 1, staerkstes Gewicht bei index[1]=2: ' + knochen[1]);

// --- 4. gruppeJePunkt, gecacht ---------------------------------------------
const bones = [{ name: 'hip' }, { name: 'l_upperarm' }, { name: 'l_thigh' }];
const netz2 = {
    skeleton: { bones },
    geometry: {
        userData: {},
        attributes: {
            position: { count: 2 },
            skinIndex: { array: new Float32Array([1, 0, 0, 0,  2, 0, 0, 0]) },
            skinWeight: { array: new Float32Array([1, 0, 0, 0,  1, 0, 0, 0]) },
        },
    },
};
const g1 = Koerperzuordnung.gruppeJePunkt(netz2);
if (g1[0] !== G.l_arm) fehl('Punkt 0 an l_upperarm: ' + g1[0]);
if (g1[1] !== G.l_bein) fehl('Punkt 1 an l_thigh: ' + g1[1]);
const g2 = Koerperzuordnung.gruppeJePunkt(netz2);
if (g2 !== g1) fehl('nicht gecacht — zweiter Aufruf liefert ein neues Array');
if (netz2.geometry.userData.gruppeJePunkt !== g1) fehl('Cache haengt nicht an userData');

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class KoerperzuordnungTest(SimpleTestCase):
    databases = set()

    def test_seite_gruppe_staerkster_knochen_und_cache(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
