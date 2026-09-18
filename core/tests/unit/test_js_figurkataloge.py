# -*- coding: utf-8 -*-
u"""`Figurkataloge`: aus einer Serverantwort die Zeilen des Figurwahl-Dialogs.

WARUM (11.09.2026): Der Dialog „Charakter hinzufügen" der Szene-Seite las
seine Listen über Klassen, die an `scene/state.js` hängen; für das
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

// --- Reihenfolge der Reiter nach Ansage (07.09.2026) -----------------------
pruefe('Reihenfolge', Figurkataloge.REIHENFOLGE,
       ['modell', 'smpl', 'makehuman', 'uma', 'umapython', 'genesis9']);

// --- HumanBody: Koerpertypen als Standard, Dateien als gespeichert; eine
// Datei mit fremder `quelle` (gespeichertes Genesis-9-Modell) bleibt draussen
// (Edgar, 17.09.2026: „NUR bei den Genesis9 hinzufuegen") ------------------
pruefe('bereiche', Figurkataloge.BEREICHE.map(b => b[0]), ['standard', 'gespeichert']);
pruefe('modell', Figurkataloge.zeilen('modell', {
    koerpertypen: [{ name: 'Female_Anime', anzeige: 'Female Anime', geschlecht: 'weiblich' }],
    presets: [{ name: 'Female1', label: 'Female 1' }, { name: 'Rig', quelle: 'modell' },
              { name: 'Genesis01', quelle: 'genesis9' }],
}).map(z => [z.name, z.anzeige, z.bereich]),
       [['Female_Anime', 'Female Anime', 'standard'],
        ['Female1', 'Female 1', 'gespeichert'], ['Rig', 'Rig', 'gespeichert']]);

// --- UMA: Endung weg, Groesse in MB -----------------------------------------
pruefe('uma', Figurkataloge.zeilen('uma', {
    figuren: [{ name: 'Elf.glb', geschlecht: 'weiblich', bytes: 2621440, stand: '08.09.' }],
}), [{ name: 'Elf.glb', anzeige: 'Elf', unterzeile: 'weiblich · 2.5 MB · 08.09.',
       bereich: 'gespeichert' }]);

// --- SMPL: Masse ja/nein ---------------------------------------------------
pruefe('smpl', Figurkataloge.zeilen('smpl', {
    figuren: [{ name: 'mean_all', geschlecht: 'neutral', smpl: true, masse_vorhanden: true },
              { name: 'f_body', anzeige: 'Frau', geschlecht: 'weiblich', smpl: false }],
}), [{ name: 'mean_all', anzeige: 'mean_all', unterzeile: 'neutral · SMPL-X · Maße vorgegeben',
       bereich: 'standard' },
     { name: 'f_body', anzeige: 'Frau', unterzeile: 'weiblich · GarmentCode-Modell · ohne Maße',
       bereich: 'standard' }]);

// --- MakeHuman: Punkte und Hoehe in cm --------------------------------------
pruefe('makehuman', Figurkataloge.zeilen('makehuman', {
    figuren: [{ name: 'base', punkte: 13380, hoehe: 1.7 }],
}).map(z => z.unterzeile.startsWith('13') && z.unterzeile.includes('170.0 cm')), [true]);

// --- UMA Python: Rassennamen -----------------------------------------------
pruefe('umapython', Figurkataloge.zeilen('umapython', { rassen: ['Human Male 3.0'] })
       .map(z => [z.name, z.anzeige]), [['Human Male 3.0', 'Human Male 3.0']]);

// --- Genesis 9 (17.09.2026): Geschlecht, Punktzahl des Netzes, gesetzte Regler;
// ein gespeichertes Modell (`gespeichert: true`) in den zweiten Bereich -----
pruefe('genesis9', Figurkataloge.zeilen('genesis9', {
    figuren: [{ name: 'amala', anzeige: 'Amala', geschlecht: 'weiblich',
                regler: { Amala_figure_ctrl_Character: 1, body_bs_Navel_HD3: 1 } },
              { name: 'Meine', geschlecht: 'weiblich', regler: { a: 1 },
                kleidung: { g9_base_bikini: {} }, gespeichert: true }],
    punkte: { punkte: 25182 },
}).map(z => [z.name, z.anzeige, z.bereich,
             z.unterzeile.includes('25') && z.unterzeile.endsWith('2 Regler gesetzt'),
             z.unterzeile]),
       [['amala', 'Amala', 'standard', true, 'weiblich · 25.182 Punkte · 2 Regler gesetzt'],
        ['Meine', 'Meine', 'gespeichert', false, 'gespeichert · 1 Regler · 1 Stücke']]);

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

    databases = set()

    def test_zeilen_je_quelle(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
