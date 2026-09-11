# -*- coding: utf-8 -*-
u"""`Figurkataloge`: aus einer Serverantwort die Zeilen des Figurwahl-Dialogs.

WARUM (11.09.2026): Der Dialog „Charakter hinzufügen" der Szene-Seite las
seine fünf Listen über Klassen, die an `scene/state.js` hängen; für das
Theatre (Edgar: „mit dem gleichen Popup") mussten die Abrufe raus aus der
Szene. Geprüft wird die ÜBERSETZUNG der Antwort in Zeilen — die Texte sind
die der Szene-Seite, und wer sie ändert, ändert beide Dialoge.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'figurkataloge.js')

SKRIPT = """
const { Figurkataloge } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};

// --- Reihenfolge der Reiter nach Ansage (07.09.2026) -----------------------
pruefe('Reihenfolge', Figurkataloge.REIHENFOLGE,
       ['modell', 'smpl', 'makehuman', 'uma', 'umapython']);

// --- HumanBody: label vor name, Unterzeile leer -----------------------------
pruefe('modell', Figurkataloge.zeilen('modell', {
    presets: [{ name: 'Female1', label: 'Female 1' }, { name: 'Rig' }],
}), [{ name: 'Female1', anzeige: 'Female 1', unterzeile: '' },
     { name: 'Rig', anzeige: 'Rig', unterzeile: '' }]);

// --- UMA: Endung weg, Groesse in MB -----------------------------------------
pruefe('uma', Figurkataloge.zeilen('uma', {
    figuren: [{ name: 'Elf.glb', geschlecht: 'weiblich', bytes: 2621440, stand: '08.09.' }],
}), [{ name: 'Elf.glb', anzeige: 'Elf', unterzeile: 'weiblich · 2.5 MB · 08.09.' }]);

// --- SMPL: Masse ja/nein ---------------------------------------------------
pruefe('smpl', Figurkataloge.zeilen('smpl', {
    figuren: [{ name: 'mean_all', geschlecht: 'neutral', smpl: true, masse_vorhanden: true },
              { name: 'f_body', anzeige: 'Frau', geschlecht: 'weiblich', smpl: false }],
}), [{ name: 'mean_all', anzeige: 'mean_all', unterzeile: 'neutral · SMPL · Maße vorgegeben' },
     { name: 'f_body', anzeige: 'Frau', unterzeile: 'weiblich · GarmentCode-Modell · ohne Maße' }]);

// --- MakeHuman: Punkte und Hoehe in cm --------------------------------------
pruefe('makehuman', Figurkataloge.zeilen('makehuman', {
    figuren: [{ name: 'base', punkte: 13380, hoehe: 1.7 }],
}).map(z => z.unterzeile.startsWith('13') && z.unterzeile.includes('170.0 cm')), [true]);

// --- UMA Python: Rassennamen -----------------------------------------------
pruefe('umapython', Figurkataloge.zeilen('umapython', { rassen: ['Human Male 3.0'] })
       .map(z => [z.name, z.anzeige]), [['Human Male 3.0', 'Human Male 3.0']]);

// --- Leer und unbekannt ------------------------------------------------------
pruefe('leer', Figurkataloge.zeilen('uma', {}), []);
pruefe('null', Figurkataloge.zeilen('modell', null), []);
pruefe('unbekannt', Figurkataloge.zeilen('gibtesnicht', { presets: [{ name: 'x' }] }), []);
let geworfen = false;
try { await Figurkataloge.liste('gibtesnicht'); } catch (e) { geworfen = /Unbekannte Figurart/.test(e.message); }
pruefe('liste unbekannt wirft', geworfen, true);
console.log(JSON.stringify({ok: true}));
"""


class FigurkatalogeTest(SimpleTestCase):

    databases = []

    def test_zeilen_je_quelle(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
