# -*- coding: utf-8 -*-
u"""`Knochenkette`: aus einer Serverliste eine Three.js-Hierarchie.

WARUM (Edgar, 07.09.2026: „jedes Hinzufuegen eines Modells soll auch das
Skeleton dazu erzeugen"): SMPL und MakeHuman bekommen ihre Knochen vom
Server als Weltpunkte. Der Browser muss daraus RELATIVE Positionen machen,
und dabei kann zweierlei schiefgehen, ohne dass irgendwo ein Fehler
entsteht:

1. **Weltpunkte unveraendert setzen.** Dann addiert jede Ebene den Weg
   ihrer Eltern noch einmal. Bei MakeHuman (sieben Ebenen tief) landet der
   Kopf bei mehrfacher Koerperhoehe — sichtbar nur im Bild.
2. **Kinder vor ihren Eltern bauen.** Die Datei `default.mhskel` ist
   alphabetisch sortiert (`breast.L` vor `spine02`); wer diese Reihenfolge
   uebernimmt, haengt Knochen an noch nicht gebaute Eltern.

Dazu der dritte Punkt, der im Bild als „das Rig ist unvollstaendig"
erscheint: Ein `SkeletonHelper` zeichnet Linien von jedem Knochen zu seinem
ELTERNTEIL. Ein Blatt zeichnet damit nichts — Fingerspitzen, Haende, Fuesse
und Kopf blieben unsichtbar. Deshalb der Endknochen am `schwanz`.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'knochenkette.js')

SKRIPT = """
const { Knochenkette: K } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const nach = (plan, name) => plan.find(k => k.name === name);
// Punkte werden gerechnet (kopf - elternKopf), nicht kopiert: 1.2 - 1.0
// ergibt 0.19999999999999996. Ein exakter Vergleich waere hier nur eine
// Aussage ueber Fliesskomma, nicht ueber die Kette.
const nahe = (was, ist, soll) => {
    const weit = ist.some((w, i) => Math.abs(w - soll[i]) > 1e-9);
    if (weit) throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
};

// Eine Kette wie sie der Server liefert: Weltpunkte, Eltern benannt.
const kette = [
    { name: 'wurzel', eltern: null,     kopf: [0, 1.0, 0], schwanz: [0, 1.2, 0] },
    { name: 'mitte',  eltern: 'wurzel', kopf: [0, 1.2, 0], schwanz: [0, 1.5, 0] },
    { name: 'spitze', eltern: 'mitte',  kopf: [0, 1.5, 0], schwanz: [0, 1.7, 0] },
];

// --- 1. Positionen sind RELATIV zum Elternteil ----------------------------
const plan = K.bauplan(kette);
nahe('Wurzel absolut', nach(plan, 'wurzel').pos, [0, 1.0, 0]);
nahe('Mitte relativ',  nach(plan, 'mitte').pos,  [0, 0.2, 0]);
nahe('Spitze relativ', nach(plan, 'spitze').pos, [0, 0.3, 0]);
// Genau das ist der Fehler, den man nicht sieht: 1.2 statt 0.2.
if (nach(plan, 'mitte').pos[1] > 1) throw new Error('Weltpunkt unveraendert uebernommen');
// Die Weltlage bleibt zum Nachrechnen erhalten.
pruefe('Welt bleibt', nach(plan, 'spitze').welt, [0, 1.5, 0]);

// --- 2. Eltern vor Kindern, auch bei verdrehter Eingabe -------------------
const verdreht = [kette[2], kette[0], kette[1]];      // Kind zuerst
const plan2 = K.bauplan(verdreht);
const reihe = plan2.filter(k => !k.ende).map(k => k.name);
pruefe('sortiert', reihe, ['wurzel', 'mitte', 'spitze']);
nahe('und die Positionen stimmen trotzdem', nach(plan2, 'spitze').pos, [0, 0.3, 0]);

// --- 3. Endknochen fuer das letzte Stueck --------------------------------
const enden = plan.filter(k => k.ende);
pruefe('genau ein Blatt', enden.map(k => k.name), ['spitze_ende']);
pruefe('haengt am Blatt', enden[0].eltern, 'spitze');
nahe('zeigt zum Schwanz', enden[0].pos, [0, 0.2, 0]);
// Ein Schwanz auf dem Gelenk waere eine Linie der Laenge null.
const ohneLaenge = K.bauplan([
    { name: 'a', eltern: null, kopf: [0, 1, 0], schwanz: [0, 1, 0] }]);
pruefe('kein Nullknochen', ohneLaenge.filter(k => k.ende).length, 0);
// Ohne `schwanz` gibt es schlicht keinen Endknochen.
const ohneSchwanz = K.bauplan([{ name: 'a', eltern: null, kopf: [0, 1, 0] }]);
pruefe('ohne Schwanz kein Ende', ohneSchwanz.length, 1);

// --- 4. Unbekannte Eltern machen eine Wurzel, keinen Absturz -------------
const verwaist = K.bauplan([
    { name: 'kind', eltern: 'gibtsnicht', kopf: [1, 1, 1], schwanz: [1, 2, 1] }]);
pruefe('verwaist wird Wurzel', nach(verwaist, 'kind').eltern, null);
nahe('und steht absolut', nach(verwaist, 'kind').pos, [1, 1, 1]);

// --- 5. Ein Kreis darf nichts verschlucken -------------------------------
const kreis = K.bauplan([
    { name: 'a', eltern: 'b', kopf: [0, 0, 0], schwanz: [0, 1, 0] },
    { name: 'b', eltern: 'a', kopf: [0, 1, 0], schwanz: [0, 2, 0] },
]);
pruefe('beide bleiben', kreis.filter(k => !k.ende).map(k => k.name).sort(), ['a', 'b']);

// --- 6. Wurzelname und leere Eingaben ------------------------------------
pruefe('Wurzelname', K.wurzelname(plan), 'wurzel');
pruefe('leer', K.bauplan([]), []);
pruefe('nichts', K.bauplan(null), []);
pruefe('Muell faellt raus', K.bauplan([{ name: 'x' }, null, { kopf: [0,0,0] }]), []);
pruefe('Wurzelname von nichts', K.wurzelname([]), null);

// --- 7. Zwei Wurzeln: die erste gewinnt, beide bleiben -------------------
const zwei = K.bauplan([
    { name: 'p', eltern: null, kopf: [0, 1, 0], schwanz: [0, 1.1, 0] },
    { name: 'q', eltern: null, kopf: [1, 1, 0], schwanz: [1, 1.1, 0] },
]);
pruefe('beide Wurzeln bleiben', zwei.filter(k => !k.ende).length, 2);
pruefe('erste ist die Wurzel', K.wurzelname(zwei), 'p');

// --- 8. `pos` und `quat` vom Server werden UEBERNOMMEN -------------------
// Seit dem 07.09.2026 rechnet der Server die lokale Lage samt Ruhedrehung
// (`gelenkskelett.py`) — hier darf sie nicht ein zweites Mal entstehen.
// Zwei Rechnungen, die auseinanderlaufen koennen, waeren genau der Fehler,
// bei dem die Figur sich beim Abspielen wegdreht.
const vomServer = K.bauplan([
    { name: 'a', eltern: null, kopf: [0, 1, 0], schwanz: [0, 1.2, 0],
      pos: [7, 7, 7], quat: [0, 0.7071, 0, 0.7071], ende: false },
]);
pruefe('pos kommt vom Server',  nach(vomServer, 'a').pos,  [7, 7, 7]);
pruefe('quat kommt vom Server', nach(vomServer, 'a').quat, [0, 0.7071, 0, 0.7071]);

// Ohne Angabe die Vorgaben — eine aeltere Liste bleibt zeichenbar.
pruefe('Einheitsdrehung als Vorgabe', nach(plan, 'mitte').quat, [0, 0, 0, 1]);

// Liefert der Server die Endknochen selbst mit, entstehen sie nicht doppelt.
const mitEnde = K.bauplan([
    { name: 'a', eltern: null, kopf: [0, 1, 0], schwanz: [0, 1.2, 0],
      pos: [0, 1, 0], quat: [0, 0, 0, 1], ende: false },
    { name: 'a_ende', eltern: 'a', kopf: [0, 1.2, 0], schwanz: null,
      pos: [0, 0.2, 0], quat: [0, 0, 0, 1], ende: true },
]);
pruefe('keine doppelten Enden', mitEnde.filter(k => k.ende).map(k => k.name),
       ['a_ende']);

console.log(JSON.stringify({ok: true}));
"""


class KnochenketteTest(SimpleTestCase):

    databases = []

    def test_bauplan(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
