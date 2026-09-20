# -*- coding: utf-8 -*-
"""`GarmentcodeAbbruch` (scene/garmentcode_abbruch.js) mit `Antwortnachholen`:
der Abbrechen-Knopf beendet den wartenden POST, das Nachholen, und meldet
die Kennung dem Server.

Edgar, 20.09.2026: „bei 2D+3D bauen soll es einen Abbrechen-Button geben".
  1. ein POST, der nie antwortet: `abbrechen()` laesst ihn mit dem Fehler
     „Abgebrochen" (Name, nicht Text) enden, und der Server bekommt die
     Kennung der Anfrage an `/api/garmentcode/abbrechen/`;
  2. beim Nachholen (Verbindung gerissen) beendet der Abbruch die Schleife;
  3. ein normaler Fehler ist kein Abbruch (`istAbbruch`).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

import json

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'garmentcode_abbruch.js')
NACHHOLEN = Jsmodul('gemeinsam', 'antwortnachholen.js')

SKRIPT = """
const { GarmentcodeAbbruch: G } = await import(MODUL);
const { Antwortnachholen: A } = await import(%(nachholen)s);
A.TAKT_S = 0.01;
globalThis.document = { cookie: '', querySelector: () => null };
const antwortJson = (status, daten) => ({
    ok: status >= 200 && status < 300, status, statusText: String(status),
    clone() { return this; },
    headers: { get: () => 'application/json' },
    json: async () => daten, text: async () => JSON.stringify(daten),
});
const beendet = [];

// --- 1. POST ohne Antwort, dann Abbrechen ---------------------------------
globalThis.fetch = (url, opts = {}) => new Promise((ok, nein) => {
    if (url === G.ADRESSE) {
        beendet.push(opts.body.get('anfrage'));
        return ok(antwortJson(200, { ergebnis: 'beendet' }));
    }
    opts.signal?.addEventListener('abort', () => nein(opts.signal.reason));
});
let abbruch = new G();
const daten = new FormData(); daten.append('spezifikation', 'x');
const lauf = A.formular('/api/garmentcode/drapieren/', daten, 5, null, abbruch)
    .then(() => 'antwort', (f) => f);
await new Promise((w) => setTimeout(w, 20));
pruefe('Kennung gemerkt', abbruch.kennungen.length, 1);
const ergebnisse = await abbruch.abbrechen();
const fehler = await lauf;
pruefe('der Abruf endet mit Abgebrochen', G.istAbbruch(fehler), true);
pruefe('Server bekam die Kennung', beendet, [daten.get('anfrage')]);
pruefe('Ergebnis des Servers', ergebnisse, ['beendet']);

// --- 2. Nachholen wird abgebrochen ------------------------------------------
let abrufe = 0;
globalThis.fetch = async (url, opts = {}) => {
    if (url === G.ADRESSE) return antwortJson(200, { ergebnis: 'kein_lauf' });
    if (opts.method === 'POST') throw new TypeError('Failed to fetch');
    abrufe += 1; return antwortJson(404, {});
};
abbruch = new G();
const lauf2 = A.formular('/x/', new FormData(), 5, null, abbruch).then(() => 'antwort', (f) => f);
await new Promise((w) => setTimeout(w, 60));
const vorher = abrufe;
await abbruch.abbrechen();
const fehler2 = await lauf2;
await new Promise((w) => setTimeout(w, 60));
pruefe('das Nachholen endet mit Abgebrochen', G.istAbbruch(fehler2), true);
pruefe('es wurde nachgefragt', vorher > 0, true);
pruefe('danach nicht mehr', abrufe <= vorher + 1, true);

// --- 3. Einordnung ------------------------------------------------------------
pruefe('normaler Fehler ist kein Abbruch', G.istAbbruch(new Error('HTTP 500')), false);
pruefe('TypeError ist kein Abbruch', G.istAbbruch(new TypeError('Failed to fetch')), false);
console.log(JSON.stringify({ok: true}));
"""


class GarmentcodeAbbruchTest(SimpleTestCase):
    databases = set()

    def test_abbrechen_beendet_abruf_und_nachholen_und_meldet_dem_server(self):
        ausgabe = MODUL.laufen(SKRIPT % {'nachholen': json.dumps(NACHHOLEN.pfad.as_uri())})
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_der_knopf_haengt_an_beiden_wegen(self):
        statik = settings.BASE_DIR / 'static' / 'viewer' / 'scene'
        for modul in ('garmentcode_drapieren.js', 'garmentcode_schnitt.js',
                      'garmentcode_gemeinsam.js'):
            quelle = open(statik / modul, encoding='utf-8').read()
            self.assertIn('reiter.abbruch);', quelle, modul)
        vorlage = open(settings.BASE_DIR / 'templates' / '_garmentcode_panel.html',
                       encoding='utf-8').read()
        self.assertIn('id="gc-abbrechen"', vorlage)
        self.assertIn('disabled', vorlage.split('id="gc-abbrechen"')[1][:80])
        reiter = open(statik / 'garmentcode.js', encoding='utf-8').read()
        self.assertIn('GarmentcodeLauf.abbrechen(this)', reiter)
