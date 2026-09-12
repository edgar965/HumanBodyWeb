# -*- coding: utf-8 -*-
u"""BVH Studio: „Modell hinzufügen" über den Figurwahl-Dialog, und die
verknüpfte Animation unter ihrer Modellspur.

WARUM (Edgar, 11.09.2026): „beim Hinzufügen eines Modells bitte den gleichen
Popup dialog wie bei /humanbody/scene/, wo ich das Modell und die Position
auswähle, default die gleichen Meter" — und: „die Animation die dafür
zugeordnet ist, darunter sehen, etwas eingeklappt z.B. wie bei dem Licht".

Geprüft wird die Rechnung ohne DOM, in Node:

1. `Modellplatz` — Vorgabe X ist 1,5 m rechts neben der zuletzt angelegten
   Figur; eine Modellspur, deren Figur noch lädt, zählt als Figur; ohne
   Figur der Ursprung. Die Trägerspur ist die gewählte, wenn frei, sonst die
   erste freie, sonst keine.
2. `Modellgruppen` — die verknüpfte Animation folgt ihrer Modellspur
   eingerückt, zugeklappt fehlt sie, eine unverknüpfte bleibt an ihrem
   Platz, und bei zwei Modellspuren auf einer Animation trägt die erste sie.

Dazu die Verdrahtung am Quelltext: der Menüpunkt öffnet den Dialog, die
Vorlage lädt sein CSS, der Dialog kann ohne „Größe angleichen", und
`zugeklappt` überlebt Speichern und Laden.

Sabotage-Gegenprobe gemacht: `traeger` immer -1 → Fälle 2 rot;
`vorgabeX` ohne Abstand → Fälle 1 rot.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

WURZEL = Path(settings.BASE_DIR)
STUDIO = Jsmodul.VIEWER / 'bvh_studio'
GEMEINSAM = Jsmodul.VIEWER / 'gemeinsam'

PLATZ = Jsmodul('bvh_studio', 'modellplatz.js')
GRUPPEN = Jsmodul('bvh_studio', 'modellgruppen.js')

PRUEFE = """
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const bvh = (x, extra = {}) => ({ type: 'bvh', clips: [], position: [x, 0, 0], ...extra });
const modell = (ziel) => ({ type: 'model', clips: [], _linkedAnimIdx: ziel });
"""

PLATZ_SKRIPT = PRUEFE + """
const { Modellplatz } = await import(MODUL);
// Leere Zeitleiste: Ursprung, keine Trägerspur.
pruefe('leer x', Modellplatz.vorgabeX([]), 0);
pruefe('leer frei', Modellplatz.freieAnimation([]), null);
// Eine Figur bei 0,4 m: die nächste 1,5 m rechts davon.
const a = bvh(0.4, { mesh: {} });
pruefe('neben Figur', Modellplatz.vorgabeX([a]), 1.9);
// Eine Animationsspur ohne Clips und ohne Modell ist FREI und kein Vorbild.
const leer = bvh(2.0);
pruefe('leere Spur kein Vorbild', Modellplatz.vorgabeX([a, leer]), 1.9);
pruefe('leere Spur ist frei', Modellplatz.freieAnimation([a, leer]) === leer, true);
// Eine Modellspur, die auf die leere zeigt, besetzt sie — Figur lädt noch.
const m = modell(1);
pruefe('besetzt durch Modell', Modellplatz.besetzt(leer, [a, leer, m]), true);
pruefe('Vorbild ist die letzte besetzte', Modellplatz.vorgabeX([a, leer, m]), 3.5);
pruefe('keine freie', Modellplatz.freieAnimation([a, leer, m]), null);
// Clips besetzen ebenfalls.
pruefe('Clips besetzen', Modellplatz.besetzt(bvh(0, { clips: [{}] }), []), true);
// Die gewählte Spur gewinnt, wenn sie frei ist; sonst die erste freie.
const f1 = bvh(0), f2 = bvh(0);
pruefe('gewählte frei', Modellplatz.freieAnimation([f1, f2], 1) === f2, true);
pruefe('gewählte besetzt -> erste freie', Modellplatz.freieAnimation([a, f1, f2], 0) === f1, true);
pruefe('gewählt ist ein Modell -> erste freie', Modellplatz.freieAnimation([modell(-1), f1], 0) === f1, true);
// Abstand ist ein Parameter, die Vorgabe 1,5 m.
pruefe('ABSTAND_M', Modellplatz.ABSTAND_M, 1.5);
pruefe('Abstand', Modellplatz.vorgabeX([a], 0.5), 0.9);
console.log(JSON.stringify({ok: true}));
"""

GRUPPEN_SKRIPT = PRUEFE + """
const { Modellgruppen } = await import(MODUL);
const R = (spuren) => Modellgruppen.reihen(spuren).map(r =>
    [r.trackIdx, r.indent ? 'ein' : '', r.unterreihe ?? '', r.collapsed ?? '']);
// Unverknüpfte Animation bleibt an ihrem Platz; Licht und Szene fehlen hier.
pruefe('unverknüpft', R([bvh(0), { type: 'light' }, { type: 'scene_object' }, { type: 'camera' }]),
       [[0, '', '', ''], [3, '', '', '']]);
// Modell auf Animation 0: Modell zuerst, Animation eingerückt darunter.
pruefe('unter dem Modell', R([bvh(0), modell(0)]),
       [[1, '', 0, false], [0, 'ein', '', '']]);
// Zugeklappt: die Animation fehlt, das Modell weiß es.
pruefe('zugeklappt', R([bvh(0), { ...modell(0), zugeklappt: true }]),
       [[1, '', 0, true]]);
// Zwei Modelle auf einer Animation: die ERSTE trägt sie, die zweite steht allein.
pruefe('zwei Modelle', R([bvh(0), modell(0), modell(0)]),
       [[1, '', 0, false], [0, 'ein', '', ''], [2, '', '', '']]);
// Modell ohne Verknüpfung: kein Pfeil, keine Unterreihe.
pruefe('ohne Verknüpfung', R([modell(-1), bvh(0)]),
       [[0, '', '', ''], [1, '', '', '']]);
// Verknüpfung auf etwas, das keine Animation ist: wie unverknüpft.
pruefe('auf Kamera', R([{ type: 'camera' }, modell(0)]),
       [[0, '', '', ''], [1, '', '', '']]);
// Träger
pruefe('traeger', Modellgruppen.traeger([bvh(0), modell(0)], 0), 1);
pruefe('traeger ohne', Modellgruppen.traeger([bvh(0)], 0), -1);
console.log(JSON.stringify({ok: true}));
"""


class ModellplatzTest(SimpleTestCase):

    databases = set()

    def test_lage_und_traegerspur(self):
        ausgabe = PLATZ.laufen(PLATZ_SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class ModellgruppenTest(SimpleTestCase):

    databases = set()

    def test_animation_unter_ihrer_modellspur(self):
        ausgabe = GRUPPEN.laufen(GRUPPEN_SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class ModellwahlVerdrahtungTest(SimpleTestCase):

    databases = set()

    def test_der_menuepunkt_oeffnet_den_dialog(self):
        leiste = (STUDIO / 'werkzeugleiste.js').read_text(encoding='utf-8')
        self.assertIn("['dd-add-model', () => Modellwahl.oeffnen()]", leiste)
        self.assertNotIn("['dd-add-model', () => fn.addModelTrack()]", leiste)
        wahl = (STUDIO / 'modellwahl.js').read_text(encoding='utf-8')
        self.assertIn("angleichen: false", wahl)
        self.assertIn("Modellplatz.vorgabeX(state.project.tracks", wahl)
        # Die drei Bausteine merken je einen Undo-Schritt — hier ist es EINER.
        self.assertIn("state._undoSuppressed = true", wahl)
        self.assertIn("pushUndo('Modell hinzufügen')", wahl)

    def test_die_vorlage_laedt_das_dialog_css(self):
        html = (WURZEL / 'templates' / 'bvh_studio.html').read_text(encoding='utf-8')
        self.assertIn("{% fassungspfad 'css/figurwahldialog.css' %}", html)

    def test_der_dialog_kann_ohne_groessenangleich(self):
        felder = (GEMEINSAM / 'figurlagefelder.js').read_text(encoding='utf-8')
        self.assertIn('{ angleichen = true } = {}', felder)
        self.assertIn('this.mitAngleichen ?', felder)
        dialog = (GEMEINSAM / 'figurwahldialog.js').read_text(encoding='utf-8')
        self.assertIn('new Figurlagefelder(kennung, this.vorgaben, { angleichen })', dialog)

    def test_zugeklappt_ueberlebt_speichern_und_laden(self):
        daten = (STUDIO / 'projekt_daten.js').read_text(encoding='utf-8')
        self.assertIn('td.zugeklappt = Boolean(t.zugeklappt)', daten)
        laden = (STUDIO / 'projekt_wiederherstellung.js').read_text(encoding='utf-8')
        self.assertIn('track.zugeklappt = Boolean(td.zugeklappt)', laden)
        reihen = (STUDIO / 'zeitleiste_reihen.js').read_text(encoding='utf-8')
        self.assertIn('Modellgruppen.reihen(spuren)', reihen)
        kopf = (STUDIO / 'zeitleiste_spurkopf.js').read_text(encoding='utf-8')
        self.assertIn('spur.zugeklappt = !spur.zugeklappt', kopf)
