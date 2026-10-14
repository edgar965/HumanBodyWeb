# -*- coding: utf-8 -*-
"""Die zweite 3D-Ansicht der Jobseite „Mesh-3D“: nur das Netz, dasselbe Licht, mittig, Höhe einstellbar (12.10.2026).

Edgar: „mach eine zweite 3D View im Job wo ich NUR das Mesh sehen kann, mit der gleichen Beleuchtung wie das 3D Modell, das Mesh soll in die Mitte kommen. die neue 3D View soll darunter
kommen, auch einstellbar in Größe“. Gebaut: `Mesh3dnetzbuehne` (Leinwand, Szene, Kamera, Einpassen), `Meshfigurlicht` (das Licht für BEIDE Ansichten), `Mesh3dbuehnengroesse` (Regler und
Ziehgriff), die Karte `#netz-karte` unter `#buehne-karte`.

Zwei Arten von Prüfung:

* **Node**, `Mesh3dbuehnengroesse` mit Attrappen für Feld, Regler, `ResizeObserver` und `localStorage`: Vorgabe wird nicht geschrieben, der Regler setzt die Höhe und merkt sie, die Grenzen
  halten, der Ziehgriff stellt den Regler nach, ein gemerkter Wert gilt beim Start (ein unsinniger nicht), gesperrter Speicher wirft nicht, eine ausgeblendete Ansicht lässt alles stehen.
* **Quelltext** (kein Browser, kein three.js in Node): beide Bühnen holen ihr Licht aus `Meshfigurlicht` und führen selbst keins; die Vorlage hat die Karte hinter der 3D-Ansicht und
  vor „Quelle“, jede Kennung, die die neuen Module suchen, steht in der Vorlage; `Mesh3dbuehne` füttert die Ansicht; nur die Mesh-Ansicht lädt das Netz `diffus`.

Gesehen im Chrome (Edgars Auftrag `2026.10.11.21.18.17`, Tab verdeckt, Bild von Hand gezeichnet): Netz mittig, Metall im Material 0 (die erste Ansicht 1), Höhe 560 → 800 → 400 → 560.
Nicht gesehen: das Ziehen mit der Maus (der verdeckte Tab liefert keine `ResizeObserver`-Aufrufe, die Anzeige wurde von Hand nachgezogen).

Breite (12.10.2026, Edgar: „die 3D Views sind in der Höhe einstellbar, nicht aber in der Breite, fixe“): beide Ansichten (`#buehne`, `#netz-buehne`) haben Regler und Ziehgriff für Höhe UND Breite
(`resize: both`). Ohne gewählte Breite füllt die Ansicht die Karte und wächst mit dem Fenster (nichts wird gespeichert); eine gewählte Breite wird gemerkt, bis an den Rand gezogen ist es wieder
„volle Breite“. `test_1b` hält das mit Attrappen in Node. Sabotage dazu: in `_breiteSetzen` die Zeile `if (voll) this._schreiben(…, null)` streichen → Fall 4 rot (die Zahl bleibt gemerkt);
in `_breiteAnzeigen` die Bedingung `if (this.feld.style.width)` vor dem Schreiben streichen → Fall 6 rot (ein wachsendes Fenster würde als Wahl gespeichert); `resize: both` zu `resize: vertical` → `test_7` rot.

Sabotage-Gegenprobe: in `mesh3dbuehnengroesse.js` die Zeile `if (h !== this._zuletzt)` streichen → Fall 1 rot (die Vorgabe wird geschrieben); `Math.min(this.max, …)` in `_setzen` entfernen → Fall 3
rot; in `meshfigurbuehne.js` wieder eine `HemisphereLight` einsetzen → `test_2_das_licht_steht_nur_in_meshfigurlicht` rot; `{ diffus: true }` aus `mesh3dnetzbuehne.js` nehmen → Fall 5 rot.

Ohne Datenbank. Geschrieben am 12.10.2026.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

GROESSE = Jsmodul('mesh3d', 'mesh3dbuehnengroesse.js')

SKRIPT = """
const { Mesh3dbuehnengroesse } = await import(MODUL);

function aufbau(speicher, hoehe = 560) {
    const beobachter = [];
    globalThis.ResizeObserver = class { constructor(f) { beobachter.push(f); } observe() {} };
    globalThis.window = { localStorage: speicher };
    const feld = { _h: hoehe, style: {}, get clientHeight() { return this._h; } };
    // Ein gesetzter Stil macht das Feld so hoch: wie der Browser es mit `style.height` täte.
    Object.defineProperty(feld.style, 'height', { set(v) { feld._h = parseInt(v, 10); }, get() { return feld._h + 'px'; } });
    const regler = { min: '240', max: '1600', value: String(hoehe), addEventListener(art, f) { this.rueckruf = f; } };
    const wert = { textContent: '' };
    new Mesh3dbuehnengroesse(feld, regler, wert, 'schluessel');
    return { feld, regler, wert, beobachter };
}
const speicher = (start = {}) => {
    const daten = { ...start };
    return { daten, schreibungen: 0, getItem(k) { return k in daten ? daten[k] : null; }, setItem(k, v) { daten[k] = String(v); this.schreibungen++; } };
};

// --- 1. Die Vorgabe wird angezeigt, aber nicht gespeichert
let s = speicher(); let a = aufbau(s);
pruefe('1 Regler', a.regler.value, '560'); pruefe('1 Anzeige', a.wert.textContent, '560 px');
pruefe('1 nichts geschrieben', s.schreibungen, 0);

// --- 2. Der Regler setzt die Höhe und merkt sie
a.regler.value = '800'; a.regler.rueckruf();
pruefe('2 Höhe', a.feld._h, 800); pruefe('2 Anzeige', a.wert.textContent, '800 px'); pruefe('2 gemerkt', s.daten.schluessel, '800');

// --- 3. Die Grenzen halten (der Regler eines echten Browsers klemmt selbst; hier wirkt die Klasse allein)
a.regler.value = '5000'; a.regler.rueckruf(); pruefe('3 oben', a.feld._h, 1600);
a.regler.value = '10'; a.regler.rueckruf(); pruefe('3 unten', a.feld._h, 240);

// --- 4. Der Ziehgriff stellt den Regler nach
a.feld._h = 420; a.beobachter.forEach(f => f());
pruefe('4 Regler', a.regler.value, '420'); pruefe('4 Anzeige', a.wert.textContent, '420 px'); pruefe('4 gemerkt', s.daten.schluessel, '420');

// --- 5. Ein gemerkter Wert gilt beim Start; ein unsinniger nicht
a = aufbau(speicher({ schluessel: '700' })); pruefe('5 gemerkt', a.feld._h, 700); pruefe('5 Regler', a.regler.value, '700');
a = aufbau(speicher({ schluessel: '9999' })); pruefe('5 unsinnig', a.feld._h, 560);
a = aufbau(speicher({ schluessel: 'abc' })); pruefe('5 Text', a.feld._h, 560);

// --- 6. Gesperrter Speicher wirft nicht
const gesperrt = { getItem() { throw new Error('gesperrt'); }, setItem() { throw new Error('gesperrt'); } };
a = aufbau(gesperrt); a.regler.value = '900'; a.regler.rueckruf(); pruefe('6 Höhe trotzdem', a.feld._h, 900);

// --- 7. Ausgeblendet (Höhe 0): Regler, Anzeige und Speicher bleiben
s = speicher({ schluessel: '600' }); a = aufbau(s);
const vorher = [a.regler.value, a.wert.textContent, s.schreibungen];
a.feld._h = 0; a.beobachter.forEach(f => f());
pruefe('7 unverändert', [a.regler.value, a.wert.textContent, s.schreibungen], vorher);
console.log(JSON.stringify({ ok: true }));
"""


SKRIPT_BREITE = """
const { Mesh3dbuehnengroesse } = await import(MODUL);

// Karte 1220 px breit, 10 px Rand je Seite: die Ansicht kann höchstens 1200 px breit werden (`max-width: 100%` des Stils).
function aufbau(speicher, { platz = 1200, hoehe = 560 } = {}) {
    const beobachter = [];
    globalThis.ResizeObserver = class { constructor(f) { beobachter.push(f); } observe() {} };
    globalThis.window = { localStorage: speicher };
    globalThis.getComputedStyle = () => ({ paddingLeft: '10px', paddingRight: '10px' });
    const eltern = { clientWidth: platz + 20 };
    const feld = { _h: hoehe, _w: platz, _breite: '', style: {}, parentElement: eltern,
        get clientHeight() { return this._h; }, get clientWidth() { return this._w; } };
    Object.defineProperty(feld.style, 'height', { set(v) { feld._h = parseInt(v, 10); }, get() { return feld._h + 'px'; } });
    // Ein gesetzter Stil macht die Ansicht so breit, höchstens so breit wie die Karte; ohne Stil füllt sie die Karte.
    Object.defineProperty(feld.style, 'width', {
        set(v) { feld._breite = v; feld._w = v === '' ? eltern.clientWidth - 20 : Math.min(parseInt(v, 10), eltern.clientWidth - 20); },
        get() { return feld._breite; } });
    const h = { min: '240', max: '1600', value: String(hoehe), addEventListener(art, f) { this.rueckruf = f; } };
    const b = { min: '320', max: '1600', value: '1600', addEventListener(art, f) { this.rueckruf = f; } };
    const hWert = { textContent: '' }, bWert = { textContent: '' };
    new Mesh3dbuehnengroesse(feld, h, hWert, 'hoehe', { regler: b, wert: bWert, schluessel: 'breite' });
    return { feld, eltern, h, b, hWert, bWert, beobachter };
}
const speicher = (start = {}) => {
    const daten = { ...start };
    return { daten, schreibungen: 0, getItem(k) { return k in daten ? daten[k] : null; },
        setItem(k, v) { daten[k] = String(v); this.schreibungen++; }, removeItem(k) { delete daten[k]; } };
};

// --- 1. Ohne Wahl: volle Breite, der Regler steht am Rand der Karte, nichts wird gespeichert
let s = speicher(); let a = aufbau(s);
pruefe('1 Regler', a.b.value, '1200'); pruefe('1 Grenze', a.b.max, '1200'); pruefe('1 Anzeige', a.bWert.textContent, 'volle Breite (1200 px)');
pruefe('1 kein Stil', a.feld.style.width, ''); pruefe('1 nichts geschrieben', s.schreibungen, 0);

// --- 2. Der Regler macht die Ansicht schmaler und merkt es; die Höhe bleibt, wie sie war
a.b.value = '800'; a.b.rueckruf();
pruefe('2 Breite', a.feld._w, 800); pruefe('2 Stil', a.feld.style.width, '800px'); pruefe('2 Anzeige', a.bWert.textContent, '800 px');
pruefe('2 gemerkt', s.daten.breite, '800'); pruefe('2 Höhe', a.feld._h, 560); pruefe('2 Höhe nicht gemerkt', 'hoehe' in s.daten, false);

// --- 3. Nicht unter die Mindestbreite
a.b.value = '100'; a.b.rueckruf(); pruefe('3 unten', a.feld._w, 320);

// --- 4. Bis an den Rand der Karte (oder darüber) ist wieder volle Breite: kein Stil, die Zahl ist vergessen
a.b.value = '800'; a.b.rueckruf();
a.b.value = '1600'; a.b.rueckruf();
pruefe('4 Stil weg', a.feld.style.width, ''); pruefe('4 breit', a.feld._w, 1200); pruefe('4 vergessen', 'breite' in s.daten, false);
pruefe('4 Anzeige', a.bWert.textContent, 'volle Breite (1200 px)');

// --- 4b. Ein Regler mit Schrittweite rastet nicht auf den Endwert ein (Chrome: 2030 von 2032 bei Schritt 10): bis auf einen Schritt an den Rand ist der Rand
a.b.step = '10'; a.b.value = '1195'; a.b.rueckruf();
pruefe('4b Stil weg', a.feld.style.width, ''); pruefe('4b breit', a.feld._w, 1200);
a.b.value = '1180'; a.b.rueckruf(); pruefe('4b eine Stufe weiter innen bleibt eine Wahl', a.feld.style.width, '1180px');
a.b.step = undefined; a.b.value = '1600'; a.b.rueckruf();

// --- 5. Der Ziehgriff setzt den Stil selbst: Regler und Anzeige ziehen nach, die Breite wird gemerkt
a.feld.style.width = '640px'; a.beobachter.forEach(f => f());
pruefe('5 Regler', a.b.value, '640'); pruefe('5 Anzeige', a.bWert.textContent, '640 px'); pruefe('5 gemerkt', s.daten.breite, '640');
// … und bis an den Rand gezogen heißt wieder: volle Breite
a.feld.style.width = '1199px'; a.beobachter.forEach(f => f());
pruefe('5 Rand', a.feld.style.width, ''); pruefe('5 Rand vergessen', 'breite' in s.daten, false);

// --- 6. Wächst bei voller Breite das Fenster, wächst die Ansicht mit — das ist keine Wahl und wird nicht gespeichert
s = speicher(); a = aufbau(s);
a.eltern.clientWidth = 1620; a.feld._w = 1600; a.beobachter.forEach(f => f());
pruefe('6 Regler-Grenze', a.b.max, '1600'); pruefe('6 Anzeige', a.bWert.textContent, 'volle Breite (1600 px)'); pruefe('6 kein Stil', a.feld.style.width, '');
pruefe('6 nichts geschrieben', s.schreibungen, 0);

// --- 7. Eine gemerkte Breite gilt beim Start; eine unsinnige nicht
a = aufbau(speicher({ breite: '700' })); pruefe('7 gemerkt', a.feld._w, 700); pruefe('7 Stil', a.feld.style.width, '700px'); pruefe('7 Regler', a.b.value, '700');
a = aufbau(speicher({ breite: '100' })); pruefe('7 zu schmal', a.feld.style.width, '');
a = aufbau(speicher({ breite: 'abc' })); pruefe('7 Text', a.feld.style.width, '');

// --- 8. Ist das Fenster schmaler als die gemerkte Breite, füllt die Ansicht die Karte (Stil weg, Zahl vergessen)
s = speicher({ breite: '900' }); a = aufbau(s, { platz: 700 });
pruefe('8 Stil', a.feld.style.width, ''); pruefe('8 breit', a.feld._w, 700); pruefe('8 vergessen', 'breite' in s.daten, false);

// --- 9. Gesperrter Speicher wirft nicht
const gesperrt = { getItem() { throw new Error('gesperrt'); }, setItem() { throw new Error('gesperrt'); }, removeItem() { throw new Error('gesperrt'); } };
a = aufbau(gesperrt); a.b.value = '900'; a.b.rueckruf(); pruefe('9 Breite trotzdem', a.feld._w, 900);
a.b.value = '1600'; a.b.rueckruf(); pruefe('9 voll trotzdem', a.feld.style.width, '');

// --- 10. Ausgeblendet (Breite 0): nichts ändert sich
s = speicher({ breite: '600' }); a = aufbau(s);
const vorher = [a.b.value, a.bWert.textContent, s.schreibungen, a.feld.style.width];
a.feld._w = 0; a.beobachter.forEach(f => f());
pruefe('10 unverändert', [a.b.value, a.bWert.textContent, s.schreibungen, a.feld.style.width], vorher);
console.log(JSON.stringify({ ok: true }));
"""


class MeshAnsichtGroessenTest(SimpleTestCase):
    databases = set()

    def test_1_regler_ziehgriff_grenzen_und_speicher(self):
        ausgabe = GROESSE.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_1b_die_breite_ist_einstellbar_und_ohne_wahl_die_volle_karte(self):
        ausgabe = GROESSE.laufen(SKRIPT_BREITE)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class MeshAnsichtQuelltextTest(SimpleTestCase):
    databases = set()

    def _lesen(self, *teile):
        return Jsmodul(*teile).pfad.read_text(encoding='utf-8')

    def _vorlage(self):
        return (Path(settings.BASE_DIR) / 'templates' / 'mesh3d_auftrag.html').read_text(encoding='utf-8')

    def test_2_das_licht_steht_nur_in_meshfigurlicht(self):
        licht = self._lesen('meshfigur', 'meshfigurlicht.js')
        self.assertIn('HemisphereLight', licht)
        self.assertIn('DirectionalLight', licht)
        for teile in (('meshfigur', 'meshfigurbuehne.js'), ('mesh3d', 'mesh3dnetzbuehne.js')):
            text = self._lesen(*teile)
            self.assertIn('Meshfigurlicht.einrichten(this.szene, this.kamera)', text, teile)
            self.assertNotIn('HemisphereLight', text, teile)
            self.assertNotIn('DirectionalLight', text, teile)

    def test_3_die_karte_steht_hinter_der_3d_ansicht_und_vor_der_quelle(self):
        text = self._vorlage()
        ids = [text.index(f'id="{k}"') for k in ('buehne-karte', 'netz-karte', 'quelle-karte')]
        self.assertEqual(ids, sorted(ids))

    def test_4_jede_kennung_der_neuen_module_steht_in_der_vorlage(self):
        vorlage = self._vorlage()
        gefunden = set()
        for teile in (('mesh3d', 'mesh3dnetzbuehne.js'), ('mesh3d', 'mesh3dbuehnengroesse.js'), ('mesh3d', 'mesh3dbuehne.js')):
            gefunden |= set(re.findall(r"getElementById\('([^']+)'\)", self._lesen(*teile)))
        self.assertGreaterEqual(len(gefunden), 4, gefunden)
        # Regler und Anzeige für Höhe UND Breite, an beiden Ansichten.
        for kennung in ('buehne-groesse', 'buehne-groesse-wert', 'buehne-breite', 'buehne-breite-wert', 'netz-groesse', 'netz-groesse-wert', 'netz-breite', 'netz-breite-wert'):
            self.assertIn(kennung, gefunden)
        for kennung in sorted(gefunden):
            self.assertIn(f'id="{kennung}"', vorlage, kennung)

    def test_5_die_3d_ansicht_fuettert_die_mesh_ansicht(self):
        text = self._lesen('mesh3d', 'mesh3dbuehne.js')
        self.assertIn('new Mesh3dnetzbuehne(this.adapter, this.seite)', text)       # die Seite (Kennung, Endpunkte) gehört seit 13.10.2026 dazu: „Netz bearbeiten“ ruft den Server
        # Zustand des Auftrags „Mesh to 3D“ UND der Fall ohne Figur (dort steht der Hinweis).
        self.assertIn('this.netzbuehne.zeigen(m)', text)
        # … und ohne Figur das Netz des Imports selbst, oder `null` (leere Karte), solange es nicht da ist (`_netzOhneFigur`, seit 13.10.2026)
        self.assertIn('this.netzbuehne.zeigen(bereit ?', text)
        self.assertIn(": null);", text)

    def test_6_nur_die_mesh_ansicht_laedt_das_netz_diffus(self):
        netzbuehne = self._lesen('mesh3d', 'mesh3dnetzbuehne.js')
        self.assertIn('{ diffus: true }', netzbuehne)
        netze = self._lesen('meshfigur', 'meshfigurnetze.js')
        self.assertIn('m.metalness = 0', netze)
        self.assertIn('!!optionen.diffus', netze)
        # Die erste Ansicht zeigt das Netz wie bisher.
        self.assertNotIn('diffus', self._lesen('meshfigur', 'meshfigurbuehne.js'))

    def test_7_beide_behaelter_lassen_sich_in_hoehe_und_breite_ziehen(self):
        """Edgar, 12.10.2026: „die 3D Views sind in der Höhe einstellbar, nicht aber in der Breite“ — `resize: vertical` ließ die Breite fest."""
        css = (Path(settings.BASE_DIR) / 'static' / 'css' / 'mesh3d.css').read_text(encoding='utf-8')
        for auswahl in (r'#netz-karte \.mesh3d-netzbetrachter', r'#buehne-karte \.meshfigur-buehnenspalte \.mesh-betrachter'):
            regel = re.search(auswahl + r' \{([^}]*)\}', css)
            self.assertIsNotNone(regel, auswahl)
            self.assertIn('resize: both', regel.group(1), auswahl)
            self.assertNotIn('resize: vertical', regel.group(1), auswahl)
            self.assertIn('overflow: hidden', regel.group(1), auswahl)
            self.assertIn('max-width: 100%', regel.group(1), auswahl)       # schmaler ja, breiter als die Karte nie
            self.assertIn('min-width: 320px', regel.group(1), auswahl)

    def test_8_beide_ansichten_bekommen_die_breitenregler(self):
        self.assertIn('SCHLUESSEL_BREITE', self._lesen('mesh3d', 'mesh3dnetzbuehne.js'))
        buehne = self._lesen('mesh3d', 'mesh3dbuehne.js')
        self.assertIn('new Mesh3dbuehnengroesse(document.getElementById(\'buehne\')', buehne)
        self.assertIn('SCHLUESSEL_BREITE', buehne)
