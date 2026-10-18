# -*- coding: utf-8 -*-
"""Die Knöpfe für die Bestandteile des Netzes (14.10.2026, `Meshfigurteile.schalten`, `Meshfigurteileleiste`) — Edgar: „der kleine weiße Flügel am Arm … das möchte ich auch löschen“. Nicht gelaufen — läuft nur auf Ansage.

    SchaltenTest   ein Bestandteil lässt sich einzeln ausblenden, unabhängig von „Haare“ und „Kleider“; die Wahl wird je Seite gemerkt und beim nächsten Laden gelesen
    LeisteTest     je Bestandteil ein Knopf, `active` zeigt den Zustand, ein Klick schaltet; ohne Bestandteile bleibt die Leiste versteckt; ohne Behälter (Seiten ohne die Leiste) wirft nichts
    DrahtTest      Quelltext: Behälter in der Vorlage, die Bühne ruft `teileleiste.zeigen()` nach `teile.zeigen(…)`

Sabotage: in `anwenden` den Teil `&& !this.aus.has(name)` streichen → `SchaltenTest` rot; in `Meshfigurteileleiste._knopf` den Aufruf `this.teile.schalten` streichen → `LeisteTest` rot.
"""

import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

LEISTE = Jsmodul('meshfigur', 'meshfigurteileleiste.js')
WEB = Path(settings.BASE_DIR)
# `meshfigurteile.js` importiert `Meshfigurhaarobjekt` und damit `three/addons/loaders/GLTFLoader.js` — das löst der Spiegel (`Webmodul`) nicht auf
# (WebmodulFehler in der Suite, 18.10.2026). Das Skript liest die Klasse deshalb von ihrem echten Ort ohne ihre Importe, wie `test_js_posenaufnahme`;
# `Meshfigurhaarobjekt` braucht der Fall nicht (er legt die Einträge selbst an). Einstieg ist die Leiste, sie importiert nichts.
TEILE = LEISTE
TEILE_QUELLE = str(Jsmodul.VIEWER / 'meshfigur' / 'meshfigurteile.js')

VORSPANN = """
const speicher = {};
globalThis.location = { pathname: '/mesh-3D/zauberer_2026.10.13.10.47.52/' };
globalThis.localStorage = { getItem: k => (k in speicher ? speicher[k] : null), setItem: (k, v) => { speicher[k] = v; } };
"""

SKRIPT_SCHALTEN = VORSPANN + """
const { readFileSync } = await import('node:fs');
const quelle = readFileSync(__QUELLE__, 'utf8').replace(/^import .*$/gm, '').replace(/^export class/m, 'class');
const Meshfigurteile = new Function('Meshfigurhaarobjekt', quelle + '\\nreturn Meshfigurteile;')(class {});
const sicht = {};
const objekt = name => ({ sichtbar: an => { sicht[name] = an; } });
const bau = () => {
    const t = new Meshfigurteile({}, () => {});
    t.eintraege.set('hat', { gruppe: 'kopf', objekt: objekt('hat') });
    t.eintraege.set('beard', { gruppe: 'haar', objekt: objekt('beard') });
    t.eintraege.set('angel wing', { gruppe: 'anhang', objekt: objekt('angel wing') });
    return t;
};
let t = bau();
t.anwenden();
pruefe('alle an', sicht, { hat: true, beard: true, 'angel wing': true });
t.schalten('angel wing', false);
pruefe('Flügel aus', sicht, { hat: true, beard: true, 'angel wing': false });
t.kleider = false; t.anwenden();
pruefe('Kleider aus: Hut und Flügel weg, Bart bleibt (Gruppe haar)', sicht, { hat: false, beard: true, 'angel wing': false });
t.kleider = true; t.haare = false; t.anwenden();
pruefe('Haare aus: nur der Bart', sicht, { hat: true, beard: false, 'angel wing': false });
t.schalten('angel wing', true);
pruefe('Flügel wieder an (Haare noch aus)', sicht['angel wing'], true);
pruefe('liste', t.liste(), [{ name: 'hat', gruppe: 'kopf', an: true }, { name: 'beard', gruppe: 'haar', an: true }, { name: 'angel wing', gruppe: 'anhang', an: true }]);
// Gemerkt: ein neues Objekt für dieselbe Seite liest die Wahl
t.schalten('hat', false);
t = bau();
pruefe('gemerkt', [...t.aus], ['hat']);
// Ohne Speicher (Datenschutzmodus) geht es trotzdem
globalThis.localStorage = { getItem: () => { throw new Error('gesperrt'); }, setItem: () => { throw new Error('gesperrt'); } };
t = bau();
t.schalten('beard', false);
pruefe('ohne Speicher', [...t.aus], ['beard']);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_LEISTE = VORSPANN + """
const { Meshfigurteileleiste } = await import(MODUL);
const knopfElement = () => {
    const klassen = new Set();
    return { type: '', className: '', dataset: {}, title: '', children: [], _klick: null,
        classList: { toggle: (n, an) => { an ? klassen.add(n) : klassen.delete(n); }, contains: n => klassen.has(n), add: n => klassen.add(n) },
        append(...k) { this.children.push(...k); }, addEventListener(art, f) { if (art === 'click') this._klick = f; } };
};
globalThis.document = { createElement: () => { const e = knopfElement(); e.className = ''; return e; } };
const behaelter = (() => {
    const e = knopfElement();
    e.replaceChildren = function () { this.children = []; };
    e.querySelectorAll = function () { return this.children; };
    return e;
})();
let liste = [{ name: 'hat', gruppe: 'kopf', an: true }, { name: 'angel wing', gruppe: 'anhang', an: true }];
const geschaltet = [];
const teile = { liste: () => liste, schalten: (n, an) => { geschaltet.push([n, an]); liste = liste.map(t => (t.name === n ? { ...t, an } : t)); } };
const leiste = new Meshfigurteileleiste(behaelter, teile);
behaelter.classList.add('hb-versteckt');
leiste.zeigen();
pruefe('zwei Knöpfe', behaelter.children.map(k => k.dataset.teil), ['hat', 'angel wing']);
pruefe('Leiste sichtbar', behaelter.classList.contains('hb-versteckt'), false);
// `classList.add('active')` setzt der Konstruktor über className — hier zählt, was `zeigen` aus `an` macht
pruefe('beide aktiv', behaelter.children.map(k => k.classList.contains('active')), [true, true]);
behaelter.children[1].classList.add('active');
behaelter.children[1]._klick();
pruefe('Klick schaltet aus', geschaltet, [['angel wing', false]]);
pruefe('Knopf nicht mehr aktiv', behaelter.children.map(k => k.classList.contains('active')), [true, false]);
// neue Liste ohne Bestandteile: die Leiste wird versteckt
liste = [];
leiste.zeigen();
pruefe('leer: Knöpfe weg', behaelter.children.length, 0);
pruefe('leer: versteckt', behaelter.classList.contains('hb-versteckt'), true);
// ohne Behälter (Seiten ohne die Leiste) wirft nichts
new Meshfigurteileleiste(null, teile).zeigen();
console.log(JSON.stringify({ ok: true }));
"""


class SchaltenTest(SimpleTestCase):
    databases = set()

    def test_ein_bestandteil_laesst_sich_einzeln_ausblenden_und_wird_gemerkt(self):
        ausgabe = TEILE.laufen(SKRIPT_SCHALTEN.replace('__QUELLE__', json.dumps(TEILE_QUELLE)))
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class LeisteTest(SimpleTestCase):
    databases = set()

    def test_je_bestandteil_ein_knopf_der_schaltet(self):
        ausgabe = LEISTE.laufen(SKRIPT_LEISTE)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class DrahtTest(SimpleTestCase):
    databases = set()

    def _text(self, *teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_behaelter_und_aufruf(self):
        self.assertIn('id="bestandteile-leiste"', self._text('templates', 'mesh3d_auftrag.html'))
        buehne = self._text('static', 'viewer', 'meshfigur', 'meshfigurbuehne.js')
        self.assertIn("new Meshfigurteileleiste(document.getElementById('bestandteile-leiste'), this.teile)", buehne)
        self.assertLess(buehne.index('this.teile.zeigen(z, gruppe, posiert);'), buehne.index('this.teileleiste.zeigen();'))
