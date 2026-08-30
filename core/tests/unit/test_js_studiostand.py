# -*- coding: utf-8 -*-
u"""`Studiostand`: Der Schnappschuss des BVH-Studios, ein- und ausgepackt.

WARUM (28.08.2026, Befund `doppelcode` + „Datensatz mit mehr als drei
Feldern")
=========================================================================
Das Objekt `{label, data, playheadFrame, selectedTrackIdx, selectedClipIdx}`
wurde in `undo.js` an DREI Stellen von Hand gebaut und an ZWEI wieder
ausgepackt. Wer ein Feld ergänzt, muss es fünfmal nachtragen; vergisst er
eines, ist der Schnappschuss unvollständig — und das merkt niemand beim
Speichern, sondern erst beim Zurücknehmen.

DIE STELLE, DIE WEHTUT: `??` gegen `||` bei der Auswahl. Spur 0 ist eine
GÜLTIGE Auswahl. Mit `||` würde sie zu −1 („nichts ausgewählt"), und nach
einem Undo wäre die erste Spur abgewählt — ohne dass etwas schiefzugehen
scheint. Beim Abspielkopf ist `||` dagegen richtig: Bild 0 und „kein Wert"
sollen beide 0 ergeben.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'studiostand.js')

SKRIPT = """
const { Studiostand } = await import(MODUL);
// KEIN Import von `state.js` — das zieht die Three.js-Instanz der Seite
// nach, und Node findet das Paket `three` nicht. Die Klasse nimmt beides
// als Parameter; genau dafuer.
const state = {};
const fn = {};

const gerufen = [];
fn.buildProjectData = () => ({spuren: 3, marke: 'jetzt'});
fn.restoreProjectData = async (d) => { gerufen.push('restore:' + d.marke); };
for (const name of ['applyPlayhead', 'renderTimeline', 'updatePlaybackUI',
                    'updateProperties']) {
    fn[name] = () => gerufen.push(name);
}

// --- aufnehmen ------------------------------------------------------------
state.playheadFrame = 42;
state.selectedTrackIdx = 0;          // GUELTIG, nicht „nichts"
state.selectedClipIdx = 7;
const stand = Studiostand.jetzt('Clip geloescht', state, fn);

// --- Zustand veraendern, dann wiederherstellen -----------------------------
state.playheadFrame = 999;
state.selectedTrackIdx = 5;
state.selectedClipIdx = 5;
await stand.herstellen(state, fn);

const nachher = {playhead: state.playheadFrame,
                 spur: state.selectedTrackIdx, clip: state.selectedClipIdx};

// --- ein Stand OHNE Auswahl (Felder undefined) ----------------------------
const leer = new Studiostand('leer', {marke: 'leer'}, undefined,
                             undefined, undefined);
await leer.herstellen(state, fn);
const leerNachher = {playhead: state.playheadFrame,
                     spur: state.selectedTrackIdx, clip: state.selectedClipIdx};

console.log(JSON.stringify({
    label: stand.label, daten: stand.data.marke,
    aufgenommen: {playhead: stand.playheadFrame, spur: stand.selectedTrackIdx,
                  clip: stand.selectedClipIdx},
    nachher, leerNachher, gerufen,
}));
"""


class StudiostandTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.e = MODUL.laufen(SKRIPT)

    def test_der_stand_nimmt_alle_fuenf_felder_auf(self):
        self.assertEqual(self.e['label'], 'Clip geloescht')
        self.assertEqual(self.e['daten'], 'jetzt')
        self.assertEqual(self.e['aufgenommen'],
                         {'playhead': 42, 'spur': 0, 'clip': 7})

    def test_spur_null_ueberlebt_das_wiederherstellen(self):
        u"""Mit `||` statt `??` würde Spur 0 zu −1 — die erste Spur wäre nach
        einem Undo abgewählt, und nichts sähe kaputt aus."""
        self.assertEqual(self.e['nachher'],
                         {'playhead': 42, 'spur': 0, 'clip': 7})

    def test_ohne_auswahl_wird_minus_eins(self):
        u"""`-1` heißt „nichts ausgewählt" — das ist der Zustand, den ein
        Schnappschuss ohne Auswahl wiederherstellen muss."""
        self.assertEqual(self.e['leerNachher'],
                         {'playhead': 0, 'spur': -1, 'clip': -1})

    def test_die_anzeige_wird_nachgezogen(self):
        u"""Ohne diese vier Aufrufe stimmen die Daten, aber die Zeitleiste
        zeigt noch den alten Stand."""
        self.assertEqual(
            self.e['gerufen'],
            ['restore:jetzt', 'applyPlayhead', 'renderTimeline',
             'updatePlaybackUI', 'updateProperties',
             'restore:leer', 'applyPlayhead', 'renderTimeline',
             'updatePlaybackUI', 'updateProperties'])
