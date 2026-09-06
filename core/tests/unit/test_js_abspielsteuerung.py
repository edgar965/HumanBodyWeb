# -*- coding: utf-8 -*-
u"""`Abspielsteuerung`: Play meint die ausgewählte Figur.

WARUM (06.09.2026, Edgar: „Animationen funktionieren nicht auf die ausgewählte
Person"): Beide Play-Knöpfe der Szene-Seite schalteten nur `state.currentAction`
um — die Aktion der Figur, die gerade lief. HumanBody animieren, UMA auswählen,
Play: HumanBody hielt an, UMA rührte sich nicht. Dazu band `loadAnimationUI`
die Knöpfe bei jedem Aufruf neu — zwei Zuhörer, zwei Umschaltungen, kein
sichtbarer Effekt.

Die vier Fälle, die hier durchgespielt werden:

1. Läuft die Animation auf der AUSGEWÄHLTEN Figur → Pause/Weiter.
2. Läuft sie auf einer ANDEREN Figur → die für die ausgewählte Figur gemerkte
   Animation wird auf sie geladen (`fn.loadBVHAnimation`), ersatzweise die
   laufende, ersatzweise `ersatz`.
3. Keine Figur ausgewählt, aber etwas läuft → umschalten wie früher.
4. Nichts gewählt und kein Ersatz → Meldung, kein Aufruf.

Dazu: `verdrahten` hängt beim zweiten Aufruf KEINE zweiten Zuhörer an.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'abspielsteuerung.js')

#: DOM-Attrappe: die Knöpfe, die Meldungszeile, der Bibliotheksbaum.
DOM = """
class Knoten {
    constructor(id) {
        this.id = id; this.innerHTML = ''; this.textContent = ''; this.dataset = {};
        this.zuhoerer = {}; this.klassen = new Set(); this.value = '100';
        this.classList = {
            toggle: (k, an) => { if (an) this.klassen.add(k); else this.klassen.delete(k); },
            contains: (k) => this.klassen.has(k),
        };
    }
    addEventListener(art, f) { (this.zuhoerer[art] = this.zuhoerer[art] || []).push(f); }
    klick() { for (const f of this.zuhoerer.click || []) f(); }
}
const knoten = {};
for (const id of ['anim-play', 'play-demo-anim', 'anim-stop', 'anim-info', 'anim-timeline',
                  'anim-speed', 'speed-label', 'scene-delta-norm', 'scene-ground-fix', 'anim-save-btn']) {
    knoten[id] = new Knoten(id);
}
let aktiverEintrag = null;
globalThis.document = {
    getElementById: (id) => knoten[id] || null,
    querySelector: (sel) => sel.includes('.anim-item.active') ? aktiverEintrag : null,
};
globalThis.sessionStorage = { _w: {}, getItem(k) { return this._w[k] ?? null; }, setItem(k, v) { this._w[k] = v; } };
"""

SKRIPT = DOM + """
const { Abspielsteuerung } = await import(MODUL);
const { Figurmerker } = await import(new URL('./figurmerker.js', MODUL).href);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const aktion = () => ({ paused: false, laeuft: true, isRunning() { return this.laeuft; }, play() { this.laeuft = true; } });
const geladen = [];
const fn = { loadBVHAnimation: (url, name) => geladen.push(name + '@' + url), stopAnimation: () => {} };
const state = { characters: new Map([['hb', {id: 'hb'}], ['uma', {id: 'uma'}]]),
                selectedCharacterId: 'hb', _animatedCharId: 'hb', currentAction: aktion(),
                playing: true, currentAnimUrl: '/bvh/x/', currentAnimName: 'X' };
const st = new Abspielsteuerung(state, fn);

// 1. laeuft auf der ausgewaehlten Figur → Pause, dann weiter ------------------
pruefe('1 pause', st.abspielen(), 'umgeschaltet');
pruefe('1 paused', [state.playing, state.currentAction.paused], [false, true]);
pruefe('1 Symbol', knoten['anim-play'].innerHTML.includes('fa-play'), true);
pruefe('1 Kopfleiste', knoten['play-demo-anim'].klassen.has('active'), false);
pruefe('1 weiter', st.abspielen(), 'umgeschaltet');
pruefe('1 laeuft', [state.playing, state.currentAction.paused], [true, false]);
pruefe('1 nichts geladen', geladen, []);

// 2. andere Figur ausgewaehlt → deren gemerkte Animation laden -----------------
state.selectedCharacterId = 'uma';
Figurmerker.animationMerken('uma', {name: 'Tanz', url: '/bvh/tanz/', category: 'Aist'});
pruefe('2 geladen', st.abspielen(), 'geladen');
pruefe('2 was', geladen, ['Tanz@/bvh/tanz/']);
pruefe('2 Name', state.currentAnimName, 'Tanz');
// … ohne Merkzettel: die laufende Animation wandert auf die Figur — und
// steht danach auf deren Zettel, wie nach einem Klick in der Bibliothek
Figurmerker.vergessen('uma');
state.currentAnimUrl = '/bvh/x/'; state.currentAnimName = 'X';
st.abspielen();
pruefe('2b laufende', geladen[1], 'X@/bvh/x/');
pruefe('2b gemerkt', Figurmerker.animation('uma').url, '/bvh/x/');
// … ohne beides: der Eintrag, der in der Bibliothek markiert ist
Figurmerker.vergessen('uma');
state.currentAnimUrl = ''; state.currentAnimName = '';
aktiverEintrag = { dataset: { url: '/bvh/markiert/', name: 'Markiert' } };
st.abspielen();
pruefe('2c markierter Eintrag', geladen[2], 'Markiert@/bvh/markiert/');
// … ohne alles: der Ersatz (Beispielanimation der Kopfleiste)
Figurmerker.vergessen('uma');
aktiverEintrag = null;
st.abspielen({ url: '/bvh/demo/', name: 'Demo' });
pruefe('2d Ersatz', geladen[3], 'Demo@/bvh/demo/');

// 4. nichts gewaehlt, kein Ersatz → Meldung, kein Aufruf -----------------------
Figurmerker.vergessen('uma');
pruefe('4 keine', st.abspielen(), 'keine-animation');
pruefe('4 Meldung', knoten['anim-info'].textContent.includes('Keine Animation'), true);
pruefe('4 nichts geladen', geladen.length, 4);

// 3. keine Figur, aber etwas laeuft → umschalten wie frueher ------------------
state.selectedCharacterId = null;
pruefe('3 um', st.abspielen(), 'umgeschaltet');
state.currentAction = null;
pruefe('3 ohne alles', st.abspielen(), 'keine-figur');

// verdrahten: einmal, nicht zweimal -------------------------------------------
pruefe('verdrahtet', st.verdrahten(), true);
pruefe('nicht nochmal', st.verdrahten(), false);
pruefe('ein Zuhoerer', knoten['anim-play'].zuhoerer.click.length, 1);
state.selectedCharacterId = 'uma'; state.currentAction = aktion(); state._animatedCharId = 'uma'; state.playing = true;
knoten['anim-play'].klick();
pruefe('Klick pausiert genau einmal', state.playing, false);

console.log(JSON.stringify({ok: true}));
"""


class AbspielsteuerungTest(SimpleTestCase):

    def test_play_meint_die_ausgewaehlte_figur(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
