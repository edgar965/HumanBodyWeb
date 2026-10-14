# -*- coding: utf-8 -*-
"""„Bereich per Hover“ im Netzwerkzeug der Jobseite Mesh-3D (14.10.2026): der Bereich ähnlicher Farbe unter dem Zeiger leuchtet, der Regler „Granularität“ stellt ihn fein oder grob, ein Klick wählt ihn.

Edgar: „per Hover im 3D View, wenn ich über das Mesh fahre, werden einzelne Bereiche highlightet … eine Einstellung über einen Slider, mit dem ich die Granularität anpassen kann … bei der Ballerina möchte ich den Flügel
auswählen können (weiß, Hintergrund schwarz, Figur gelblich)“. Die älteren Werkzeuge (Teil wählen, Rahmen, Farbe im Umkreis) bleiben als Rückfall.

    PraedikatTest   `Mesh3dnetzwahl.farbPraedikat` (das EINE Urteil für Vorschau und Auswahl): Umkreis und ΔE trennen das Weiße vom Gelblichen und vom fernen Weißen
    HoverTest       `Mesh3dnetzhover` in Node mit three-Attrappe: Fläche → Index der Hülle und `setDrawRange`, entfernte Flächen leuchten nicht, Mindestbewegung, `neu`, `weg`, `aktiv(false)`, kein Treffer, keine Textur
    ReglerTest      Regler „Granularität“ und Zahlenfeld „Farbabstand ΔE“ sind EIN Wert (beide Richtungen), `bei` meldet jede Änderung, der Regler endet bei 60, Felder ohne `addEventListener` (der alte Test) werfen nicht
    DrahtTest       Quelltext: Knopf, Regler, Textzeile, Cursor, Modus und der Klick über `wahl.farbe`; die drei alten Knöpfe stehen noch

Sabotage: in `farbPraedikat` `<= toleranz` durch `< 0` ersetzen → `PraedikatTest` rot; in `Mesh3dnetzhover._rechnen` die Prüfung `w.entfernt[f]` streichen → `HoverTest.test_entfernte_flaechen_leuchten_nicht` rot; in
`Mesh3dnetzfarbwahl._binden` den Hörer des Reglers entfernen → `ReglerTest` rot. Im Chrome gesehen (14.10.2026, Spiralballerina ohne Zweitarm): Flügel am Daumen leuchtet orange, ΔE 3 → 72, 14 → 283, 30 → 1.963 Flächen,
Klick wählt dieselben 283 (Server 298), nach „Entfernen“ leuchtet die Hand darunter mit anderem Bereich.
"""

import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

from ..jsmodul import Jsmodul

WEB = Path(settings.BASE_DIR)
VIEWER = WEB / 'static' / 'viewer' / 'mesh3d'
FARBWAHL = Jsmodul('mesh3d', 'mesh3dnetzfarbwahl.js')

DREI = """
export const DynamicDrawUsage = 35048;
export const DoubleSide = 2;
export class BufferAttribute {
    constructor(array, size) { this.array = array; this.itemSize = size; this.needsUpdate = false; }
    setUsage(u) { this.usage = u; return this; }
}
export class BufferGeometry {
    constructor() { this.attributes = {}; this.index = null; this.drawRange = { start: 0, count: Infinity }; }
    setAttribute(name, a) { this.attributes[name] = a; return this; }
    setIndex(i) { this.index = i; return this; }
    setDrawRange(start, count) { this.drawRange = { start, count }; }
    dispose() { this.entsorgt = true; }
}
export class MeshBasicMaterial { constructor(o) { Object.assign(this, o); } dispose() { this.entsorgt = true; } }
export class Mesh { constructor(geometry, material) { this.geometry = geometry; this.material = material; this.visible = true; } }
export class Raycaster {}
"""

PROBE = r"""
import { Mesh3dnetzhover } from './mesh3dnetzhover.js';
import { Mesh3dnetzwahl } from './mesh3dnetzwahl.js';
globalThis.window = globalThis;
const warte = ms => new Promise(r => setTimeout(r, ms));
const aus = {};

// Sechs Flächen: 0–2 weiß und dicht beisammen, 3–4 gelblich daneben, 5 weiß, aber einen Meter weg.
const labs = new Float32Array([90, 0, 0, 88, 1, 1, 91, 0, -1, 70, 5, 30, 72, 4, 28, 90, 0, 0]);
const mitten = new Float32Array([0, 0, 0, 0.01, 0, 0, 0.02, 0, 0, 0.03, 0, 0, 0.04, 0, 0, 1, 0, 0]);
const index0 = Uint32Array.from({ length: 18 }, (_, i) => i);
const baue = () => {
    const netz = { kinder: [], add(m) { this.kinder.push(m); }, remove(m) { this.kinder = this.kinder.filter(k => k !== m); } };
    const wahl = { flaechen: 6, index0, entfernt: new Uint8Array(6), geometrie: { attributes: { position: { name: 'position' } } }, netz, wurzel: {},
        labfarben: () => labs, mitten: () => mitten, farbPraedikat: Mesh3dnetzwahl.prototype.farbPraedikat, aufrufe: 0 };
    wahl.treffer = () => { wahl.aufrufe++; return wahl.ziel === undefined ? { flaeche: 0, punkt: { x: 0, y: 0, z: 0 } } : wahl.ziel; };
    const einstellung = { radius: 0.5, de: 14 };
    const farbwahl = { radiusSzene: () => einstellung.radius, farbabstand: () => einstellung.de };
    const texte = [];
    const hover = new Mesh3dnetzhover(wahl, { kamera: {}, takt: { wach() { aus.wach = (aus.wach || 0) + 1; } } }, farbwahl, t => texte.push(t));
    return { wahl, hover, einstellung, texte, netz };
};
const faelle = hover => Array.from(hover._mesh.geometry.index.array.slice(0, 9));
const zeiger = async (h, x = 100, y = 100) => { h.hover.bewegt({ x: 0, y: 0 }, x, y); await warte(120); };

// 1. Das Urteil (Umkreis und ΔE) — dieselbe Funktion wie beim Schritt `farbe`
{
    const { wahl } = baue();
    const menge = (r, de) => { const p = wahl.farbPraedikat(0, { x: 0, y: 0, z: 0 }, r, de); return [0, 1, 2, 3, 4, 5].filter(f => p(f)); };
    aus.p_fein = menge(0.5, 14);
    aus.p_weit = menge(2.0, 14);
    aus.p_grob = menge(0.5, 40);
    aus.p_sehrfein = menge(0.5, 1);
    wahl.labfarben = () => null;
    aus.p_ohne_textur = wahl.farbPraedikat(0, { x: 0, y: 0, z: 0 }, 0.5, 14);
}

// 2. Hover: Fläche → Index der Hülle
{
    const h = baue();
    h.hover.aktiv(true);
    await zeiger(h);
    aus.n = h.hover.bereich?.n;
    aus.index = faelle(h.hover);
    aus.drawRange = h.hover._mesh.geometry.drawRange;
    aus.sichtbar = h.hover._mesh.visible;
    aus.text = h.texte.at(-1);
    aus.kinder = h.netz.kinder.length;
    aus.position_geteilt = h.hover._mesh.geometry.attributes.position === h.wahl.geometrie.attributes.position;
    aus.raycast_aus = h.hover._mesh.raycast() === undefined;
    // Regler: ΔE 40 → fünf Flächen; `neu` rechnet dieselbe Stelle noch einmal
    const vorher = h.wahl.aufrufe;
    h.einstellung.de = 40;
    h.hover.neu();
    await warte(120);
    aus.n_grob = h.hover.bereich?.n;
    aus.neu_rechnet = h.wahl.aufrufe - vorher;
    aus.drawRange_grob = h.hover._mesh.geometry.drawRange.count;
    // Mindestbewegung: 1 px zählt nicht, 50 px schon
    const a = h.wahl.aufrufe;
    await zeiger(h, 101, 100);
    aus.ein_pixel = h.wahl.aufrufe - a;
    await zeiger(h, 150, 100);
    aus.fuenfzig_pixel = h.wahl.aufrufe - a;
    // weg: nichts leuchtet, Text leer
    h.hover.weg();
    aus.weg = { sichtbar: h.hover._mesh.visible, count: h.hover._mesh.geometry.drawRange.count, bereich: h.hover.bereich, text: h.texte.at(-1) };
    // aktiv(false): keine Rechnung mehr
    h.hover.aktiv(false);
    const b = h.wahl.aufrufe;
    await zeiger(h, 300, 100);
    aus.ausgeschaltet = h.wahl.aufrufe - b;
    h.hover.freigeben();
    aus.freigegeben = h.netz.kinder.length;
}

// 3. Entfernte Flächen leuchten nicht
{
    const h = baue();
    h.wahl.entfernt[1] = 1;
    h.hover.aktiv(true);
    await zeiger(h);
    aus.n_entfernt = h.hover.bereich?.n;
    aus.index_entfernt = faelle(h.hover).slice(0, 6);
}

// 4. Kein Treffer, keine Textur
{
    const h = baue();
    h.wahl.ziel = null;
    h.hover.aktiv(true);
    await zeiger(h);
    aus.kein_treffer = { bereich: h.hover.bereich, text: h.texte.at(-1) };
    const k = baue();
    k.wahl.labfarben = () => null;
    k.hover.aktiv(true);
    await zeiger(k);
    aus.keine_textur = { bereich: k.hover.bereich, text: k.texte.at(-1) };
}

// 5. Ein langsamer Treffertest (60 ms, wie der Raycast über 200.000 Flächen: 38–56 ms gemessen) bekommt eine Pause von 120 ms — nicht Test an Test
{
    const h = baue();
    const schnell = h.wahl.treffer;
    h.wahl.treffer = () => { const t = performance.now(); while (performance.now() - t < 60); return schnell(); };
    h.hover.aktiv(true);
    const ende = performance.now() + 500;
    let x = 100;
    while (performance.now() < ende) { h.hover.bewegt({ x: 0, y: 0 }, x += 5, 100); await warte(10); }
    aus.gedrosselt = { aufrufe: h.wahl.aufrufe, dauer: Math.round(h.hover._dauer) };
}
console.log(JSON.stringify(aus));
"""

SKRIPT_REGLER = """
const { Mesh3dnetzfarbwahl } = await import(MODUL);
const ereignisse = {};
const feld = (wert, mitHoerer = true) => {
    const f = { value: wert, textContent: '', max: '', hoerer: {} };
    if (mitHoerer) f.addEventListener = (art, tat) => { f.hoerer[art] = tat; };
    return f;
};
const felder = { 'netz-wz-farbradius': feld('18'), 'netz-wz-farbtoleranz': feld('14'), 'netz-wz-granularitaet': feld('14'), 'netz-wz-granularitaet-wert': feld('') };
globalThis.document = { getElementById: id => felder[id] || null };
const w = new Mesh3dnetzfarbwahl();
let meldungen = 0;
w.bei(() => { meldungen++; });
pruefe('Anzeige am Anfang', felder['netz-wz-granularitaet-wert'].textContent, 'ΔE 14');
pruefe('Regler endet bei 60', felder['netz-wz-granularitaet'].max, '60');
// Regler → Zahlenfeld
felder['netz-wz-granularitaet'].value = '25'; felder['netz-wz-granularitaet'].hoerer.input();
pruefe('Zahlenfeld folgt dem Regler', felder['netz-wz-farbtoleranz'].value, 25);
pruefe('farbabstand folgt dem Regler', w.farbabstand(), 25);
pruefe('Anzeige folgt dem Regler', felder['netz-wz-granularitaet-wert'].textContent, 'ΔE 25');
pruefe('bei() nach dem Regler', meldungen, 1);
// Zahlenfeld → Regler
felder['netz-wz-farbtoleranz'].value = '9'; felder['netz-wz-farbtoleranz'].hoerer.input();
pruefe('Regler folgt dem Zahlenfeld', felder['netz-wz-granularitaet'].value, '9');
pruefe('Anzeige folgt dem Zahlenfeld', felder['netz-wz-granularitaet-wert'].textContent, 'ΔE 9');
pruefe('bei() nach dem Zahlenfeld', meldungen, 2);
// Über 60 (das Feld darf bis 80): der Regler bleibt am Ende, der Wert gilt
felder['netz-wz-farbtoleranz'].value = '75'; felder['netz-wz-farbtoleranz'].hoerer.change();
pruefe('Regler am Ende', felder['netz-wz-granularitaet'].value, '60');
pruefe('Wert über dem Reglerende gilt', w.farbabstand(), 75);
// Umkreis meldet auch
felder['netz-wz-farbradius'].hoerer.input();
pruefe('bei() nach dem Umkreis', meldungen, 4);
// Felder ohne addEventListener (alte Attrappe) und fehlende Felder werfen nicht
globalThis.document = { getElementById: id => (id.startsWith('netz-wz-farb') ? feld('14', false) : null) };
const ohne = new Mesh3dnetzfarbwahl();
pruefe('ohne Hörer: ΔE', ohne.farbabstand(), 14);
console.log(JSON.stringify({ ok: true }));
"""


def quelltext(*teile):
    return WEB.joinpath(*teile).read_text(encoding='utf-8')


class _Probe(SimpleTestCase):
    databases = set()

    @classmethod
    def _laufen(cls):
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — ohne node kein Ergebnis (jsmodul.py).')
        ordner = Path(ProjektTemp.ordner(prefix='netzhover_'))
        try:
            for name in ('mesh3dnetzhover.js', 'mesh3dnetzwahl.js', 'mesh3dnetzfarbe.js', 'mesh3dnetzinseln.js'):
                text = (VIEWER / name).read_text(encoding='utf-8').replace("from 'three'", "from './three.js'")
                (ordner / name).write_text(text, encoding='utf-8')
            (ordner / 'three.js').write_text(DREI, encoding='utf-8')
            (ordner / 'probe.mjs').write_text(PROBE, encoding='utf-8')
            lauf = subprocess.run(['node', str(ordner / 'probe.mjs')], capture_output=True, text=True, encoding='utf-8', timeout=60)
        finally:
            shutil.rmtree(ordner, ignore_errors=True)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        return json.loads(lauf.stdout.strip().splitlines()[-1])


class PraedikatTest(_Probe):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aus = cls._laufen()

    def test_umkreis_und_farbabstand_trennen_weiss_von_gelblich_und_fern(self):
        self.assertEqual(self.aus['p_fein'], [0, 1, 2], 'ΔE 14, Umkreis 0,5: nur das Weiße nebenan')
        self.assertEqual(self.aus['p_weit'], [0, 1, 2, 5], 'Umkreis 2: auch das ferne Weiße')
        self.assertEqual(self.aus['p_grob'], [0, 1, 2, 3, 4], 'ΔE 40: auch das Gelbliche, nicht das ferne Weiße')
        self.assertEqual(self.aus['p_sehrfein'], [0], 'ΔE 1: nur die Fläche selbst')

    def test_ohne_textur_gibt_es_kein_urteil(self):
        self.assertIsNone(self.aus['p_ohne_textur'])


class HoverTest(_Probe):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aus = cls._laufen()

    def test_der_bereich_geht_in_den_index_der_huelle(self):
        a = self.aus
        self.assertEqual(a['n'], 3)
        self.assertEqual(a['index'], list(range(9)), 'die Ecken der Flächen 0–2 aus dem Index des Netzes')
        self.assertEqual(a['drawRange']['count'], 9)
        self.assertTrue(a['sichtbar'])
        self.assertIn('3 Flächen', a['text'])
        self.assertEqual(a['kinder'], 1, 'eine Hülle am Netz')
        self.assertTrue(a['position_geteilt'], 'die Hülle teilt die Punkte des Netzes')
        self.assertTrue(a['raycast_aus'], 'die Hülle darf den Treffertest nicht stören')

    def test_der_regler_wirkt_beim_naechsten_rechnen(self):
        self.assertEqual(self.aus['n_grob'], 5)
        self.assertEqual(self.aus['drawRange_grob'], 15)
        self.assertEqual(self.aus['neu_rechnet'], 1, '`neu` rechnet dieselbe Stelle einmal')

    def test_mindestbewegung(self):
        self.assertEqual(self.aus['ein_pixel'], 0)
        self.assertEqual(self.aus['fuenfzig_pixel'], 1)

    def test_weg_und_aus_und_freigeben(self):
        weg = self.aus['weg']
        self.assertEqual(weg, {'sichtbar': False, 'count': 0, 'bereich': None, 'text': ''})
        self.assertEqual(self.aus['ausgeschaltet'], 0, 'ohne Modus keine Rechnung')
        self.assertEqual(self.aus['freigegeben'], 0)

    def test_entfernte_flaechen_leuchten_nicht(self):
        self.assertEqual(self.aus['n_entfernt'], 2)
        self.assertEqual(self.aus['index_entfernt'], [0, 1, 2, 6, 7, 8], 'Fläche 1 fehlt')

    def test_ein_langsamer_treffertest_verlaengert_die_pause(self):
        g = self.aus['gedrosselt']
        self.assertGreaterEqual(g['dauer'], 55, 'die Dauer des Tests wird gemessen')
        # In 500 ms: ein 60-ms-Test bekommt 120 ms Pause (Test, Pause, Test …): höchstens vier Tests; ohne die Verlängerung liefen sie hintereinander (rund acht)
        self.assertLessEqual(g['aufrufe'], 4, g)
        self.assertGreaterEqual(g['aufrufe'], 2, g)

    def test_kein_treffer_und_keine_textur(self):
        self.assertIsNone(self.aus['kein_treffer']['bereich'])
        self.assertEqual(self.aus['kein_treffer']['text'], '')
        self.assertIsNone(self.aus['keine_textur']['bereich'])
        self.assertIn('keine lesbare Farbtextur', self.aus['keine_textur']['text'])


class ReglerTest(SimpleTestCase):
    databases = set()

    def test_regler_und_zahlenfeld_sind_ein_wert(self):
        ausgabe = FARBWAHL.laufen(SKRIPT_REGLER)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class DrahtTest(SimpleTestCase):
    databases = set()

    def test_vorlage_und_css(self):
        vorlage = quelltext('templates', 'mesh3d_auftrag.html')
        for kennung in ('netz-wz-hover', 'netz-wz-granularitaet', 'netz-wz-granularitaet-wert', 'netz-wz-hover-info', 'netz-wz-teil', 'netz-wz-rahmen', 'netz-wz-farbe'):
            self.assertIn('id="%s"' % kennung, vorlage, kennung)
        css = quelltext('static', 'css', 'mesh3d.css')
        self.assertIn('.mesh3d-netzbetrachter.wz-hover canvas', css)
        self.assertIn('.mesh3d-hover-info', css)

    def test_das_werkzeug_hat_den_modus_und_klickt_ueber_die_farbauswahl(self):
        werkzeug = quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzwerkzeug.js')
        self.assertIn("this.modus = 'hover';", werkzeug, 'der Hover ist die Vorgabe')
        self.assertIn("this.knoepfe.hover.addEventListener('click', () => this._umschalten('hover'))", werkzeug)
        self.assertIn("['hover', 'teil', 'farbe'].includes(this.modus)", werkzeug, 'der Klick im Hover-Modus wählt wie „Farbe im Umkreis“')
        self.assertIn('this.wahl.farbe(t.flaeche, t.punkt,', werkzeug)
        for alt in ("this.knoepfe.teil.addEventListener('click', () => this._umschalten('teil'))", "this.knoepfe.rahmen.addEventListener('click', () => this._umschalten('rahmen'))",
                    "this.knoepfe.farbe.addEventListener('click', () => this._umschalten('farbe'))"):
            self.assertIn(alt, werkzeug, 'die alten Werkzeuge bleiben als Rückfall')
        self.assertIn("c.addEventListener('pointerleave', () => this.hover?.weg())", werkzeug)

    def test_vorschau_und_auswahl_benutzen_dasselbe_urteil(self):
        wahl = quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzwahl.js')
        self.assertIn('const enthaelt = this.farbPraedikat(flaeche, punkt, radius, toleranz);', wahl)
        hover = quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzhover.js')
        self.assertIn('this.wahl.farbPraedikat(t.flaeche, t.punkt,', hover)
        self.assertIn('w.entfernt[f]', hover)
