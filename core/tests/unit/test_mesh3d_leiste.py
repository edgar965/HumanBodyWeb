# -*- coding: utf-8 -*-
"""Die drei Fehler der Jobseite „Mesh-3D“ vom 13.10.2026 (Edgar: „Animationsleiste ist wieder weg bei den 3D Views, der Greifer zum Verkleinern des Views ist weg, play mit Pause taste der
Animation scrollt die Seite“).

Ursachen (im Chrome gemessen, nicht vermutet):
* **Greifer:** der des Browsers (`resize: both`) ist ein 15-px-Zeichen, dunkelgrau auf dem schwarzen Grund der Leinwand — da, aber nicht zu sehen. Jetzt ein eigener Griff (`Mesh3dbuehnengriff`).
* **Leiste:** sie war `hidden`, bis eine Bewegung geladen war, und verschwand bei jedem Umbau der Figur (Skelett weg → versteckt). Der Klick auf Play schaltete „Haltung“ aus, die Figur wurde neu
  gebaut, die neue Aktion stand auf Anfang: der Klick ging verloren. Jetzt steht die Leiste immer da, und ein Bedienbefehl läuft nach dem Umbau (`Engine2d3dKleideranimation.bedienen`).
* **Leertaste:** `taste()` kehrte zurück, solange keine Aktion geladen war (oder der Fokus auf dem Schieber lag) — ohne `preventDefault`, also scrollte die Seite.

Sabotagen, die diese Fälle rot machen müssen: in `taste` das `ereignis.preventDefault()` VOR dem `if (this.a.action)` streichen (Fall 1); `schieber &&` aus der Bedingung nehmen (Fall 4);
in `Mesh3dbuehne` die Zeile `immerSichtbar = true` streichen (Quelltext-Fall); in der Vorlage `hidden` an die Leiste setzen (Quelltext-Fall); in `.mesh3d-griff` `z-index` streichen (Quelltext-Fall).
Nicht gelaufen: der Rest (Umbau der Figur und Weiterlaufen) ist im Chrome geprüft, nicht hier.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

BEDIENUNG = Jsmodul('engine2d3dkleider', 'engine2d3dkleideranimationsbedienung.js')
GRIFF = Jsmodul('mesh3d', 'mesh3dbuehnengriff.js')

SKRIPT_TASTEN = """
const { Engine2d3dKleideranimationsbedienung: Bedienung } = await import(MODUL);
let taste = null;
globalThis.document = { getElementById: () => null, addEventListener: (art, f) => { if (art === 'keydown') taste = f; } };

function aufbau({ hidden = false, action = {} } = {}) {
    const log = [];
    const a = { karte: { hidden }, action, scrubber: { addEventListener() {} },
        bedienen(tun) { log.push('bedienen'); tun(); }, umschalten() { log.push('umschalten'); },
        bild(r) { log.push('bild' + r); }, springen(e) { log.push('springen' + e); } };
    new Bedienung(a);
    return log;
}
const ereignis = (code, ziel = { tagName: 'BODY' }) => ({ code, target: ziel, verhindert: false, preventDefault() { this.verhindert = true; } });

// 1. Die Leiste steht da, die Bewegung ist (noch) nicht geladen: die Leertaste scrollt die Seite NICHT, es geschieht nichts.
let log = aufbau({ action: null }); let e = ereignis('Space'); taste(e);
pruefe('1 verhindert', e.verhindert, true); pruefe('1 nichts bedient', log, []);

// 2. Mit geladener Bewegung läuft der Befehl durch `bedienen`.
log = aufbau(); e = ereignis('Space'); taste(e);
pruefe('2 verhindert', e.verhindert, true); pruefe('2 Befehl', log, ['bedienen', 'umschalten']);

// 3. Ein Knopf behält seine Leertaste (der Browser löst den Klick selbst aus): nicht abfangen.
log = aufbau(); e = ereignis('Space', { tagName: 'BUTTON' }); taste(e);
pruefe('3 nicht abgefangen', e.verhindert, false); pruefe('3 nichts', log, []);

// 4. Ein Schieber nimmt Pfeile selbst, die Leertaste nicht (sie scrollte die Seite).
log = aufbau(); e = ereignis('Space', { tagName: 'INPUT', type: 'range' }); taste(e);
pruefe('4 Leertaste am Schieber', [e.verhindert, log], [true, ['bedienen', 'umschalten']]);
log = aufbau(); e = ereignis('ArrowLeft', { tagName: 'INPUT', type: 'range' }); taste(e);
pruefe('4 Pfeil am Schieber bleibt dem Schieber', [e.verhindert, log], [false, []]);

// 5. Ein Textfeld behält alle Tasten.
log = aufbau(); e = ereignis('Space', { tagName: 'INPUT', type: 'text' }); taste(e);
pruefe('5 Textfeld', [e.verhindert, log], [false, []]);

// 6. Ohne Leiste (versteckt, „2D3D Kleider“ ohne Bewegung) scrollt die Leertaste wie immer.
log = aufbau({ hidden: true }); e = ereignis('Space'); taste(e);
pruefe('6 versteckt', [e.verhindert, log], [false, []]);

// 7. Andere Tasten gehen durch `bedienen` und verhindern das Scrollen mit.
log = aufbau(); e = ereignis('ArrowRight'); taste(e);
pruefe('7 Pfeil rechts', [e.verhindert, log], [true, ['bedienen', 'bild1']]);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_GRIFF = """
const { Mesh3dbuehnengriff } = await import(MODUL);

// Ohne Dokument (die Größen-Tests laufen mit Attrappen): kein Absturz, kein Griff.
new Mesh3dbuehnengriff({ feld: { clientHeight: 500, clientWidth: 800 }, _setzen() { throw new Error('nicht gerufen'); } });

const ereignisse = {};
const element = { className: '', setAttribute() {}, addEventListener(art, f) { ereignisse[art] = f; }, setPointerCapture() {}, releasePointerCapture() {} };
globalThis.document = { createElement: () => element };
const gesetzt = [];
const feld = { clientHeight: 500, clientWidth: 800, kinder: [], appendChild(k) { this.kinder.push(k); } };
const groesse = { feld, breite: { regler: {} }, _setzen: h => gesetzt.push(['h', h]), _breiteSetzen: b => gesetzt.push(['b', b]) };
new Mesh3dbuehnengriff(groesse);
pruefe('Klasse', element.className, 'mesh3d-griff'); pruefe('im Feld', feld.kinder.length, 1);

// Anfassen bei (100, 100), ziehen nach (150, 80): Höhe 500 + (80 − 100), Breite 800 + (150 − 100).
ereignisse.pointerdown({ button: 0, clientX: 100, clientY: 100, pointerId: 1, preventDefault() {} });
ereignisse.pointermove({ clientX: 150, clientY: 80 });
pruefe('gezogen', gesetzt, [['h', 480], ['b', 850]]);
// Nach dem Loslassen bewegt sich nichts mehr.
ereignisse.pointerup({ pointerId: 1 }); ereignisse.pointermove({ clientX: 400, clientY: 400 });
pruefe('losgelassen', gesetzt.length, 2);
// Die rechte Maustaste zieht nicht.
ereignisse.pointerdown({ button: 2, clientX: 0, clientY: 0, pointerId: 2, preventDefault() {} }); ereignisse.pointermove({ clientX: 50, clientY: 50 });
pruefe('rechte Taste', gesetzt.length, 2);
console.log(JSON.stringify({ ok: true }));
"""


class LeisteTastenTest(SimpleTestCase):
    databases = set()

    def test_1_leertaste_scrollt_die_seite_nicht_solange_die_leiste_da_ist(self):
        ausgabe = BEDIENUNG.laufen(SKRIPT_TASTEN)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class GriffTest(SimpleTestCase):
    databases = set()

    def test_2_der_griff_zieht_hoehe_und_breite(self):
        ausgabe = GRIFF.laufen(SKRIPT_GRIFF)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class LeisteQuelltextTest(SimpleTestCase):
    databases = set()

    def _lesen(self, *teile):
        return Jsmodul(*teile).pfad.read_text(encoding='utf-8')

    def _datei(self, *teile):
        return (Path(settings.BASE_DIR).joinpath(*teile)).read_text(encoding='utf-8')

    def test_3_die_leiste_steht_immer_da(self):
        vorlage = self._datei('templates', 'mesh3d_auftrag.html')
        zeile = next(z for z in vorlage.splitlines() if 'id="animations-leiste"' in z)
        self.assertNotIn('hidden', zeile)
        buehne = self._lesen('mesh3d', 'mesh3dbuehne.js')
        self.assertIn('this.animation.immerSichtbar = true', buehne)
        self.assertIn('this.animation.vorBedienung = () => this.buehne.haltungAus()', buehne)
        # Kein Hörer mehr, der den Umbau an der Leiste vorbei anstößt (er ließ den Klick auf Play verloren gehen).
        self.assertNotIn("addEventListener(ereignis, () => this.buehne.haltungAus(), true)", buehne)

    def test_4_ein_befehl_laeuft_nach_dem_umbau_und_der_spielzustand_bleibt(self):
        text = self._lesen('engine2d3dkleider', 'engine2d3dkleideranimation.js')
        for stueck in ('bedienen(tun)', 'this._anstehend = tun', '_wiederaufnehmen()', 'this._merk = {', 'immerSichtbar ? false'):
            self.assertIn(stueck, text, stueck)
        bedienung = self._lesen('engine2d3dkleider', 'engine2d3dkleideranimationsbedienung.js')
        self.assertIn("this.a.bedienen(tun)", bedienung)
        buehne = self._lesen('meshfigur', 'meshfigurbuehne.js')
        # Der Umbau meldet, ob er einer war — sonst wüsste die Leiste nicht, dass sie warten muss.
        self.assertIn('return true;', buehne[buehne.index('haltungAus() {'):buehne.index('_objekteZeigen')])

    def test_5_der_griff_ist_sichtbar_und_in_beiden_ansichten(self):
        css = self._datei('static', 'css', 'mesh3d.css')
        import re
        regel = re.search(r'\.mesh3d-griff \{([^}]*)\}', css)
        self.assertIsNotNone(regel)
        for stueck in ('position: absolute', 'z-index', 'cursor: nwse-resize', 'width: 28px', 'height: 28px'):
            self.assertIn(stueck, regel.group(1), stueck)
        groesse = self._lesen('mesh3d', 'mesh3dbuehnengroesse.js')
        self.assertIn('new Mesh3dbuehnengriff(this)', groesse)   # die Klasse für BEIDE Ansichten
