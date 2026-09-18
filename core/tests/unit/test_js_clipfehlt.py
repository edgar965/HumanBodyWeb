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
4. `verschwunden` meldet, was fehlt und wie viele Clips weg sind, und
   schreibt ins Serverprotokoll; ohne Treffer meldet es 0.

Sabotage-Gegenprobe: `i--` in `_spurRaeumen` zu `i++` → Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul("bvh_studio", "clipfehlt.js")

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

// --- 4. verschwunden meldet -----------------------------------------------
spurA.clips.push(clip('A_Results', 'gem'));
const meldungen = [];
const anzahl = Clipfehlt.verschwunden({ category: 'A_Results', name: 'gem' }, state, fn, t => meldungen.push(t));
if (anzahl !== 1) fehl('verschwunden: ' + anzahl);
if (meldungen.length !== 1 || !/A_Results\\/gem gibt es nicht mehr — 1 Clip aus der Zeitleiste entfernt/.test(meldungen[0])) fehl('Meldung: ' + meldungen);
if (!gerufen.includes('log:clip_removed_missing')) fehl('kein Serverprotokoll');
const keiner = Clipfehlt.verschwunden({ category: 'X', name: 'y' }, state, fn, t => meldungen.push(t));
if (keiner !== 0 || !/0 Clips/.test(meldungen[1])) fehl('ohne Treffer: ' + keiner + ' / ' + meldungen[1]);

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class ClipfehltTest(SimpleTestCase):
    databases = set()

    def test_clips_ohne_datei_verlassen_die_zeitleiste(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get("ok"), ausgabe)
