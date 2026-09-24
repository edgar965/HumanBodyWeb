# -*- coding: utf-8 -*-
"""`Scriptzuschlag`: Was die Script-Clips eines Modells an einem Bild beitragen.

WARUM (Edgar, 15.09.2026: „Animation mit normaler Animation, Mimik und
Script"): Die Lebendigkeit hing als Einstellung an der Mimikspur — ohne
Anfang und Ende. Jetzt ist sie ein Clip auf der Script-Spur:

1. Nur aktive Clips zählen (`startFrame <= bild < startFrame + sichtbare
   Bilder`); außerhalb kein Zuschlag, `aktiv` false.
2. Die Zeit zählt ab dem Clipanfang: ein verschobener Clip liefert an
   seinem k-ten Bild dieselben Werte wie der unverschobene.
3. Nach einem Split setzt die zweite Hälfte die Folge fort (`trimIn`):
   Bild b der zweiten Hälfte = Bild (b − start₂ + trimIn) des ganzen Clips.
4. Zwei aktive Clips addieren sich.

Dazu die Verdrahtung als Quelltext (die Module importieren `three`): das
Modellmenü ist zweigeteilt (Modell / Animation → Animation, Mimik, Script),
die Script-Spur hat ihr Menü, `removeTrackAt` zieht `_modellIdx` nach, alte
Projekte mit `lebendigkeit` an der Mimikspur werden zum Script-Clip.

Sabotage-Gegenprobe: in `aktive` `bild < c.startFrame + …` → `true` →
Fall 1 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from ._studiovorlage import Studiovorlage

MODUL = Jsmodul('studio', 'scriptzuschlag.js')
STUDIO = Jsmodul.VIEWER / 'studio'

SKRIPT = """
const { Scriptzuschlag: S } = await import(MODUL);
const { Lebendigkeit: L } = await import(MODUL.replace('scriptzuschlag', 'lebendigkeit'));
const fps = 30;
const nah = (was, a, b) => { if (Math.abs(a - b) > 1e-9) throw new Error(was + ': ' + a + ' statt ' + b);
};
const clip = (start, bilder, extra = {}) => ({ type: 'script', startFrame: start, totalFrames: bilder,
    trimIn: 0, trimOut: 0, data: { ...L.vorgabe(), blick: { an: false }, ...extra } });
// Ein Blinzel-Bild finden: erster Zuschlag > 0 im Clip
const a = clip(0, 600);
let bild = -1;
for (let b = 0; b < 600; b++) {
    if ((S.gewichte([a], b, fps).zuschlag.eyeClosedL || 0) > 0) { bild = b; break; }
}
if (bild < 0) throw new Error('kein Blinzeln in 20 s');
const wert = S.gewichte([a], bild, fps).zuschlag.eyeClosedL;
// 1. außerhalb nichts
const ausserhalb = S.gewichte([clip(100, 50)], 20, fps);
if (ausserhalb.aktiv || Object.keys(ausserhalb.zuschlag).length) throw new Error('vor dem Clip aktiv');
if (S.gewichte([clip(0, 50)], 80, fps).aktiv) throw new Error('nach dem Clipende aktiv');
if (!S.gewichte([a], bild, fps).aktiv) throw new Error('innerhalb nicht aktiv');
// 2. verschoben: gleicher Wert am gleichen Clip-Bild
nah('verschoben', S.gewichte([clip(250, 600)], 250 + bild, fps).zuschlag.eyeClosedL, wert);
// 3. Split: zweite Hälfte ab 100 mit trimIn 100 setzt fort
const zweite = { ...clip(100, 600), trimIn: 100 };
nah('split', S.gewichte([zweite], bild, fps).zuschlag.eyeClosedL, wert);
// 4. zwei aktive addieren sich
nah('summe', S.gewichte([a, clip(0, 600)], bild, fps).zuschlag.eyeClosedL, 2 * wert);
// Ausgeschaltet: nichts
const aus = S.gewichte([clip(0, 600, { an: false })], bild, fps);
if (!aus.aktiv || Object.keys(aus.zuschlag).length) throw new Error('aus liefert Zuschlag');
console.log(JSON.stringify({ ok: true, bild }));
"""


class ScriptzuschlagTest(SimpleTestCase):
    def test_aktive_clips_zeit_ab_clipanfang_split_und_summe(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_modellmenue_zweigeteilt_und_scriptspur_verdrahtet(self):
        vorlage = Studiovorlage.text()
        modell = vorlage[vorlage.index('id="model-context-menu"') : vorlage.index('id="script-context-menu"')]
        self.assertIn('Modell hinzufügen', modell)
        self.assertIn('Animation hinzufügen', modell)
        for kennung in ('model-ctx-bvh-submenu', 'ctx-mimik-track', 'ctx-script-track'):
            self.assertIn(kennung, modell)
        self.assertNotIn('Mimikspur hinzufügen', modell)
        script = vorlage[vorlage.index('id="script-context-menu"') : vorlage.index('id="mimik-context-menu"')]
        for aktion in (
            'ctx-script-clip',
            'ctx-script-einstellungen',
            'ctx-laenge-sekunden',
            'ctx-delete',
            'ctx-mimik-einrechnen',
        ):
            self.assertIn('data-action="%s"' % aktion, script)
        menue = ScriptzuschlagTest._text(STUDIO / 'zeitleiste_menue.js')
        self.assertLess(menue.index("spur.type === 'script'"), menue.index('_leereSpur(e, spur'))
        # Fläche und Spurkopf teilen sich die Befehle (`Modellhinzufuegen`).
        gemeinsam = ScriptzuschlagTest._text(STUDIO / 'zeitleiste_modellhinzufuegen.js')
        self.assertIn('Mimikdialog.oeffnen(mimik, klickbild, null)', gemeinsam)
        self.assertIn('Scriptspur.hinzufuegen(spurNr, klickbild)', gemeinsam)
        modellmenue = ScriptzuschlagTest._text(STUDIO / 'zeitleiste_modellmenue.js')
        self.assertIn(
            'Modellhinzufuegen.binden(menue, state.selectedTrackIdx, Modellmenue.klickbild)', modellmenue
        )
        self.assertIn("bvh: 'model-ctx-bvh-submenu'", modellmenue)

    def test_anwendung_je_modell_und_nur_beteiligte_knochen_ohne_mimikspur(self):
        anwendung = ScriptzuschlagTest._text(STUDIO / 'mimikanwendung.js')
        self.assertIn('static gewichteModell(modellIdx, t)', anwendung)
        self.assertIn('if (!stand.mimik && !stand.script) return;', anwendung)
        self.assertIn('if (!ganz && !b) continue;', anwendung)
        self.assertIn(
            'Mimikanwendung.gewichteModell(spur._modellIdx, t)',
            ScriptzuschlagTest._text(STUDIO / 'mimikeinrechnen.js'),
        )
        # Eine neue Mimikspur bringt ihr Script mit (Lebendigkeit an, 13.09.2026).
        self.assertIn(
            'Scriptspur.clipSetzen(Scriptspur.anlegen(modellIdx), 0)',
            ScriptzuschlagTest._text(STUDIO / 'mimikspur.js'),
        )

    def test_loeschen_zieht_modellverweis_nach_und_nimmt_kindspuren_mit(self):
        modelle = ScriptzuschlagTest._text(STUDIO / 'models.js')
        self.assertIn("(t.type === 'mimik' || t.type === 'script') && t._modellIdx >= 0", modelle)
        abbau = ScriptzuschlagTest._text(STUDIO / 'spurabbau.js')
        self.assertIn('_kindspuren(spur, index)', abbau)
        self.assertLess(
            abbau.index('const kinder = Spurabbau._kindspuren'), abbau.index('Spurabbau._nachziehen(index);')
        )

    def test_alte_lebendigkeit_wird_script_clip(self):
        laden = ScriptzuschlagTest._text(STUDIO / 'projekt_wiederherstellung.js')
        self.assertIn('_alteLebendigkeit(eingang, angelegt)', laden)
        self.assertIn('Scriptspur.clipSetzen(Scriptspur.anlegen(modellIdx), 0, td.lebendigkeit)', laden)
        self.assertIn("td.type !== 'mimik' && td.type !== 'script'", laden)
        self.assertIn("|| c.type === 'script'", ScriptzuschlagTest._text(STUDIO / 'projekt_daten.js'))

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding='utf-8')
