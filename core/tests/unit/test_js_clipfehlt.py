# -*- coding: utf-8 -*-
"""`Clipfehlt`: Ein Clip, dessen BVH es nicht mehr gibt, fliegt aus der Zeitleiste.

Edgar (13.09.2026, BVH Studio): „Falls in der Timeline etwas ist was es
nicht gibt, dann entfernen." Vorher blieb er rot markiert stehen
(`_loadError`), und der Server suchte die Datei in anderen Ordnern.

1. `entfernen` nimmt ALLE Bewegungsclips der Datei aus allen Spuren — auch
   zwei nebeneinander (von hinten gelöscht, sonst überspringt `splice` den
   Nachbarn), auch einen, der auf einer Kameraspur gelandet ist — und lässt
   andere Clips und den Modellclip gleichen Namens in Ruhe.
2. Der Mixer gibt die Animation frei (`uncacheClip`), die leere Spur wird
   unsichtbar, Dauer/Zeitleiste/Eigenschaften werden nachgezogen.
3. Bleibt auf keiner Spur ein Clip, hält die Wiedergabe an.
4. `verschwunden` fragt (24.09.2026: „Fehlermeldung, mit Abfrage ob die
   gelöscht werden sollen" — vorher entfernte es ohne Rückfrage), meldet, was
   fehlt, und schreibt ins Serverprotokoll.
5. Bei „Nein" bleibt der Clip stehen (`_loadError`), nichts wird entfernt.
6. Dieselbe Datei wird in derselben Sitzung nur EINMAL gefragt.
7. NACHGEBESSERT, noch am 24.09.2026 (Edgar: „Popup kommt, aber die
   Animationen sind immer noch drin ... 'keine Bewegung hier' - was soll
   das??"): mehrere VERSCHIEDENE fehlende Dateien, die kurz nacheinander
   auftauchen (ein Projekt lädt mehrere Clips parallel), landen in EINEM
   gesammelten Dialog (`WARTE_MS`) statt in mehreren `confirm()`
   nacheinander — die hatte Chrome nach ein paar Stück automatisch als
   „Abbrechen" unterdrückt, und die betroffenen Clips blieben unbemerkt bei
   „Nein" hängen.

Sabotage-Gegenprobe: `i--` in `_spurRaeumen` zu `i++` → Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('studio', 'clipfehlt.js')

SKRIPT = """
const { Clipfehlt } = await import(MODUL);
const fehler = [];
const fehl = (t) => fehler.push(t);

const mixer = { gestoppt: 0, frei: [], stopAllAction() { this.gestoppt++; }, uncacheClip(c) { this.frei.push(c); } };
const clip = (category, name, type = 'bvh') => ({ type, category, name, animClip: { name: category + '/' + name } });
const spurA = { type: 'bvh', mixer, group: { visible: true }, _activeClip: 1, _activeAction: 1,
                clips: [clip('Results', 'tanz'), clip('Results', 'tanz'), clip('Mixamo', 'gehen')] };
const spurB = { type: 'bvh', mixer: null, group: { visible: true },
                clips: [clip('Results', 'tanz')] };
const modell = { type: 'model', clips: [clip('Results', 'tanz', 'model')] };   // Modellclip, kein Bewegungsclip
const kamera = { type: 'camera', clips: [clip(null, 'Kameraposition 1', 'camera_kf'), clip('Results', 'tanz')] };
const state = { project: { tracks: [spurA, spurB, modell, kamera] }, selectedClipIdx: 1, playing: true };
const gerufen = [];
const fn = { updateDuration: () => gerufen.push('dauer'), renderTimeline: () => gerufen.push('leiste'),
             updateProperties: () => gerufen.push('eigenschaften'), serverLog: (a, t) => gerufen.push('log:' + a) };

// `verschwunden` fragt jetzt (24.09.2026) statt stillschweigend zu entfernen —
// gesammelt (`WARTE_MS`), damit mehrere verschiedene fehlende Dateien nicht in
// mehreren `confirm()` nacheinander landen. Kurzes Fenster fuer den Test.
Clipfehlt.WARTE_MS = 10;
let confirmAntwort = true;
let confirmAufrufe = 0;
let confirmText = '';
globalThis.confirm = (text) => { confirmAufrufe++; confirmText = text; return confirmAntwort; };
const warten = (ms = 40) => new Promise((weiter) => setTimeout(weiter, ms));

// --- 1. alle Clips der Datei, sonst nichts --------------------------------
const weg = Clipfehlt.entfernen('Results', 'tanz', state, fn);
if (weg !== 4) fehl('entfernt: ' + weg + ' statt 4');
if (spurA.clips.length !== 1 || spurA.clips[0].name !== 'gehen') fehl('Spur A: ' + JSON.stringify(spurA.clips.map(c => c.name)));
if (spurB.clips.length !== 0) fehl('Spur B nicht leer');
if (modell.clips.length !== 1) fehl('Modellclip angefasst');
if (kamera.clips.length !== 1 || kamera.clips[0].type !== 'camera_kf') fehl('Kameraspur: ' + JSON.stringify(kamera.clips.map(c => c.name)));

// --- 2. Mixer frei, leere Spur unsichtbar, Ansichten nachgezogen ----------
if (mixer.frei.length !== 2 || mixer.gestoppt < 1) fehl('Mixer: frei ' + mixer.frei.length + ', gestoppt ' + mixer.gestoppt);
if (spurA.group.visible !== true) fehl('Spur A mit Rest-Clip unsichtbar');
if (spurB.group.visible !== false) fehl('leere Spur B sichtbar');
if (spurA._activeClip !== null || spurA._activeAction !== null) fehl('aktiver Clip nicht geloescht');
if (state.selectedClipIdx !== -1) fehl('Auswahl steht noch');
for (const n of ['dauer', 'leiste', 'eigenschaften']) if (!gerufen.includes(n)) fehl('nicht nachgezogen: ' + n);
if (state.playing !== true) fehl('Wiedergabe angehalten, obwohl ein Clip bleibt');

// --- 3. kein Clip mehr auf keiner Spur -> Wiedergabe aus -------------------
modell.clips.length = 0; kamera.clips.length = 0;
Clipfehlt.entfernen('Mixamo', 'gehen', state, fn);
if (state.playing !== false) fehl('Wiedergabe laeuft ohne Clips weiter');

// --- 4. verschwunden markiert sofort, fragt erst nach dem Sammelfenster ----
spurA.clips.push(clip('A_Results', 'gem'));
const gemClip = spurA.clips[spurA.clips.length - 1];
const meldungen = [];
Clipfehlt.verschwunden(gemClip, state, fn, t => meldungen.push(t));
if (gemClip._loadError !== true) fehl('nicht sofort als Fehler markiert');
if (confirmAufrufe !== 0) fehl('confirm zu frueh gerufen: ' + confirmAufrufe);
await warten();
if (confirmAufrufe !== 1) fehl('confirm nicht gerufen: ' + confirmAufrufe);
if (!/A_Results\\/gem/.test(confirmText)) fehl('Dialogtext nennt die Datei nicht: ' + confirmText);
if (spurA.clips.includes(gemClip)) fehl('Clip nach Ja nicht entfernt');
if (meldungen.length !== 1 || !/1 Clip.*entfernt/.test(meldungen[0])) fehl('Meldung: ' + meldungen);
if (!gerufen.includes('log:clip_removed_missing')) fehl('kein Serverprotokoll');

// --- 5. Nein laesst den Clip stehen, rot markiert --------------------------
confirmAntwort = false;
spurB.clips.push(clip('A_Results', 'bleibt'));
const bleibtClip = spurB.clips[spurB.clips.length - 1];
const aufrufeVorNein = confirmAufrufe;
Clipfehlt.verschwunden(bleibtClip, state, fn, t => meldungen.push(t));
await warten();
if (aufrufeVorNein + 1 !== confirmAufrufe) fehl('confirm bei Nein nicht gerufen');
if (spurB.clips.indexOf(bleibtClip) === -1) fehl('Clip bei Nein aus der Spur genommen');
if (bleibtClip._loadError !== true) fehl('Clip bei Nein nicht als Fehler markiert');

// --- 6. dieselbe fehlende Datei wird nur einmal gefragt --------------------
Clipfehlt.verschwunden({ category: 'A_Results', name: 'bleibt' }, state, fn, t => meldungen.push(t));
await warten();
if (confirmAufrufe !== aufrufeVorNein + 1) fehl('dieselbe Datei fragt zweimal: ' + confirmAufrufe);

// --- 7. mehrere VERSCHIEDENE fehlende Dateien kurz hintereinander: EIN Dialog
confirmAntwort = false;
const aufrufeVorSammlung = confirmAufrufe;
const x1 = clip('A_Results', 'x1'), x2 = clip('A_Results', 'x2'), x3 = clip('A_Results', 'x3');
spurA.clips.push(x1, x2);
spurB.clips.push(x3);
Clipfehlt.verschwunden(x1, state, fn, t => meldungen.push(t));
Clipfehlt.verschwunden(x2, state, fn, t => meldungen.push(t));
Clipfehlt.verschwunden(x3, state, fn, t => meldungen.push(t));
if (confirmAufrufe !== aufrufeVorSammlung) fehl('confirm lief schon vor dem Sammelfenster');
await warten();
if (confirmAufrufe !== aufrufeVorSammlung + 1) fehl('mehrere Dateien fragten mehrfach: ' + confirmAufrufe);
if (!/3 Animationen/.test(confirmText)) fehl('Sammeltext nennt nicht alle drei: ' + confirmText);
for (const c of [x1, x2, x3]) if (c._loadError !== true) fehl(c.name + ' nicht markiert');
if (!spurA.clips.includes(x1) || !spurA.clips.includes(x2) || !spurB.clips.includes(x3)) {
    fehl('bei Nein trotzdem entfernt');
}

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class ClipfehltTest(SimpleTestCase):
    databases = set()

    def test_clips_ohne_datei_verlassen_die_zeitleiste(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
