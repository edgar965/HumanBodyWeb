# -*- coding: utf-8 -*-
u"""`Reiterinhalt`: Ein Reiter bekommt seinen Inhalt, wenn er aufgeht.

WARUM (10.09.2026, Edgar: „die ladezeit … ist bei mehr als 15 Sekunden,
alleine mehr als 10 s bis das UI ohne modell aufgebaut wird" und „Die Leiste
links kann z.B. asynchron aufgebaut werden"): Der Szeneaufbau rief acht
Panel-Aufbauten beim Start auf — für Reiter, von denen genau einer offen ist.
Der teuerste baute 21.334 DOM-Elemente (80 % des ganzen Dokuments) für den
Animationsbaum, den niemand ansah. Im Browser gemessen fiel die Seite damit
von 26.688 auf 3.611 Elemente beim Start.

Die Fälle, die hier durchgespielt werden:

1. Beim Start wird NICHTS von den acht gebaut.
2. Wer einen Reiter öffnet, bekommt genau dessen Aufbauten.
3. Ein zweites Öffnen baut NICHT noch einmal — sonst hingen die Zuhörer
   doppelt (derselbe Fehler wie früher bei `loadAnimationUI`, siehe
   `test_js_abspielsteuerung`).
4. Ein fehlender Aufbau wird gemeldet und nimmt die Geschwister nicht mit.
5. Ein WERFENDER Aufbau nimmt die Geschwister ebenfalls nicht mit — sonst
   bliebe ein halber Reiter ohne Meldung stehen.
6. `offenen()` füllt den beim Start aktiven Reiter; mit `?alleReiter=1`
   (dem Messschalter) wieder alle.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'reiterinhalt.js')

#: Attrappen für alles, was das Modul beim Laden anfasst.
UMGEBUNG = """
globalThis.window = globalThis;
let aktiverReiter = 'eigenschaften';
let suche = '';
globalThis.location = { get search() { return suche; } };
globalThis.document = {
    querySelector: (sel) => sel.includes('.panel-tab.active')
        ? { dataset: { tab: aktiverReiter } } : null,
    querySelectorAll: () => [],
    visibilityState: 'visible',
};
globalThis.localStorage = {
    _w: {},
    getItem(k) { return this._w[k] ?? null; },
    setItem(k, v) { this._w[k] = v; },
};
const warnungen = [];
"""

SKRIPT = UMGEBUNG + """
const { Reiterinhalt } = await import(MODUL);
const { fn } = await import(new URL('../gemeinsam/registrierung.js', MODUL).href);
const { Protokoll } = await import(new URL('../gemeinsam/protokoll.js', MODUL).href);
Protokoll.warnung = (...teile) => warnungen.push(teile.join(' '));

const gerufen = [];
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(`${was}: ${JSON.stringify(ist)} statt ${JSON.stringify(soll)}`);
    }
};

// Alle bekannten Aufbauten durch Attrappen ersetzen, die sich merken lassen.
for (const namen of Object.values(Reiterinhalt.AUFBAUTEN)) {
    for (const name of namen) {
        fn[name] = async () => { gerufen.push(name); };
    }
}

// 1. Beim Start wird nichts gebaut - `offenen()` nimmt den aktiven Reiter,
//    und „eigenschaften" hat keinen dieser Aufbauten.
await Reiterinhalt.offenen();
pruefe('beim Start nichts gebaut', gerufen, []);

// 2. Wer „animation" oeffnet, bekommt genau dessen Aufbauten — seit dem
//    11.09.2026 auch den Videobereich (`initFigurvideo`).
await Reiterinhalt.bauen('animation');
pruefe('Animation gebaut', gerufen, ['loadAnimationUI', 'initFigurvideo']);

// 3. Ein zweites Oeffnen baut nicht erneut.
await Reiterinhalt.bauen('animation');
pruefe('kein zweiter Bau', gerufen, ['loadAnimationUI', 'initFigurvideo']);

// 4. „assets" fuehrt fuenf Aufbauten - einer fehlt in der Registrierung.
delete fn.loadClothUI;
await Reiterinhalt.bauen('assets');
pruefe('Assets ohne den fehlenden',
       gerufen.slice(2).sort(),
       ['loadCharmorphAssets', 'loadGarmentUI', 'loadHairUI', 'loadMHProxyUI']);
if (!warnungen.some(w => w.includes('loadClothUI'))) {
    throw new Error('fehlender Aufbau wurde nicht gemeldet: ' + warnungen.join(' | '));
}

// 5. Ein werfender Aufbau nimmt seine Geschwister nicht mit.
Reiterinhalt.vergessen();
gerufen.length = 0;
fn.loadClothUI = () => { throw new Error('Absicht'); };
fn.loadGarmentUI = async () => { gerufen.push('loadGarmentUI'); };
await Reiterinhalt.bauen('assets');
if (!gerufen.includes('loadGarmentUI')) {
    throw new Error('ein werfender Aufbau hat die Geschwister mitgenommen');
}

// 6. Der Messschalter baut wieder alles auf einmal.
Reiterinhalt.vergessen();
gerufen.length = 0;
fn.loadClothUI = async () => { gerufen.push('loadClothUI'); };
suche = '?alleReiter=1';
await Reiterinhalt.offenen();
// Neun seit dem 11.09.2026: die acht Reiteraufbauten plus der
// Videobereich des Animations-Reiters.
pruefe('Messschalter baut alle neun', gerufen.length, 9);

console.log(JSON.stringify({ok: true, gerufen: gerufen.length}));
"""


class ReiterinhaltTest(SimpleTestCase):
    u"""Der Inhalt entsteht beim Öffnen — genau einmal, und Fehler sind laut."""

    def test_reiter_werden_erst_beim_oeffnen_gefuellt(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
