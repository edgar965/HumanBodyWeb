# -*- coding: utf-8 -*-
"""`Antwortnachholen` (gemeinsam/antwortnachholen.js): ein gerissener POST
holt seine Antwort nach — ein Fehlercode und die Frist nicht.

Edgar, 20.09.2026: „Stoff drapieren — Failed to fetch" (Neustart des
Dev-Servers während der Drapierung). Das Modul läuft hier wirklich, mit
einem `fetch`, der spielt, was der Browser sah:
  1. der POST reißt (`TypeError: Failed to fetch`), der Server hat die
     Antwort später abgelegt: zweimal 404, dann 200 — die Antwort kommt an,
     und die Kennung ging mit dem Formular hinaus;
  2. der POST bekommt einen Fehlercode (500): kein Nachholen, der Fehler
     kommt durch;
  3. der POST reißt und der Server legt nie ab: nach der Frist der
     ursprüngliche Fehler, mit dem Zusatz, dass nichts abgelegt war.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'antwortnachholen.js')

SKRIPT = """
const { Antwortnachholen: A } = await import(MODUL);
A.TAKT_S = 0.01;
globalThis.document = { cookie: '', querySelector: () => null };   // Serverabruf.csrfToken liest Cookies
const antwortJson = (status, daten) => ({
    ok: status >= 200 && status < 300, status, statusText: String(status),
    clone() { return this; },
    headers: { get: () => 'application/json' },
    json: async () => daten, text: async () => JSON.stringify(daten),
});
const gesendet = [];

// --- 1. gerissen, dann nachgeholt ---------------------------------------
let abrufe = 0;
globalThis.fetch = async (url, opts = {}) => {
    if (opts.method === 'POST') { gesendet.push(opts.body); throw new TypeError('Failed to fetch'); }
    abrufe += 1;
    if (abrufe < 3) return antwortJson(404, { fehler: 'Noch keine Antwort' });
    return antwortJson(200, { punkte: 11805, rig_url: '/api/garmentcode/datei/x/y/' });
};
const daten = new FormData(); daten.append('spezifikation', 'x');
const ergebnis = await A.formular('/api/garmentcode/drapieren/', daten, 5, () => {});
pruefe('nachgeholt', ergebnis.punkte, 11805);
pruefe('erst beim dritten Abruf', abrufe, 3);
pruefe('Kennung ging mit', gesendet[0].has('anfrage'), true);
pruefe('Kennung sauber', /^[A-Za-z0-9_-]{8,64}$/.test(gesendet[0].get('anfrage')), true);

// --- 2. Fehlercode: kein Nachholen --------------------------------------
abrufe = 0;
globalThis.fetch = async (url, opts = {}) => {
    if (opts.method === 'POST') return antwortJson(500, { fehler: 'kaputt' });
    abrufe += 1; return antwortJson(200, { punkte: 1 });
};
let fehler = null;
try { await A.formular('/x/', new FormData(), 5); } catch (f) { fehler = f; }
pruefe('Fehlercode kommt durch', fehler !== null, true);
pruefe('kein Nachholen bei Fehlercode', abrufe, 0);

// --- 3. gerissen, nie abgelegt: nach der Frist der Ursprung -------------
globalThis.fetch = async (url, opts = {}) => {
    if (opts.method === 'POST') throw new TypeError('Failed to fetch');
    return antwortJson(404, {});
};
fehler = null;
try { await A.formular('/x/', new FormData(), 0.05); } catch (f) { fehler = f; }
pruefe('nach der Frist ein Fehler', fehler !== null, true);
pruefe('nennt den Ursprung', /Failed to fetch/.test(String(fehler.message)), true);
pruefe('nennt das Nachholen', /abgelegte Antwort/.test(String(fehler.message)), true);

// --- 4. Einordnung ---------------------------------------------------------
pruefe('TypeError ist gerissen', A.gerissen(new TypeError('Failed to fetch')), true);
pruefe('Frist ist nicht gerissen', A.gerissen(new Error('Keine Antwort binnen 180 s')), false);
pruefe('HTTP 500 ist nicht gerissen', A.gerissen(new Error('HTTP 500: kaputt')), false);
console.log(JSON.stringify({ok: true}));
"""


class AntwortnachholenTest(SimpleTestCase):
    databases = set()

    def test_gerissener_post_holt_die_antwort_nach_fehlercode_und_frist_nicht(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
