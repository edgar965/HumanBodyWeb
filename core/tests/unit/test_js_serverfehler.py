# -*- coding: utf-8 -*-
"""`Serverfehler` (gemeinsam/serverfehler.js): ist der Server nicht erreichbar, sagt die Meldung es (12.10.2026).

Edgar: „zauberer Fehler: Zustand nicht lesbar: 500 Internal Server Error bei /api/mesh3d/…/zustand/ — <html> <head> <title>500 …“ und „wenn Server nicht erreichbar, soll eine eindeutige
Fehlermeldung kommen, keine komische wie bisher“. Gemessen am Vorfall: Der Autoreload nach einer gespeicherten Python-Datei (15:23:26 bis 15:24:00) ließ den Server ~35–50 s lang entweder gar nicht
antworten (`TypeError: Failed to fetch`) oder mit der HTML-Seite eines 500 — beides stand als Rohtext im Fehlerband.

Das Modul läuft hier wirklich (Node), mit einem `fetch`, der spielt, was der Browser sah:
  1. `TypeError: Failed to fetch` (auch Firefox „NetworkError …“, Safari „Load failed“) → „Server nicht erreichbar (<Adresse>)“, die Klasse bleibt `TypeError`, der Browsertext steht in `technisch`;
  2. 500 mit HTML-Rumpf → „Server-Fehler 500 bei <Adresse>“ ohne `<html>`, `status`/`adresse`/`rumpf` bleiben;
  3. 502/503/504 → „Server nicht erreichbar“ (Vorrechner);
  4. Antworten mit JSON-Begründung (400, 404, 409, auch ein 500 mit `{"error": …}`) bleiben unberührt — dort sagt der Server selbst, was los ist;
  5. ein Fehler im eigenen Code (`TypeError: x is undefined`) und ein `AbortError` werden NICHT zu „Server nicht erreichbar“;
  6. zweimal aufgerufen ändert nichts mehr; durch `Serverabruf.json` (der Weg jeder Seite) kommt dieselbe Meldung an.

Sabotage-Gegenprobe: in `Serverfehler.text` die Zeile `!fehler.daten` streichen → Fall 4 rot (ein 500 mit JSON-Begründung würde überschrieben); `Serverfehler.verstaendlich` aus `_geloggt` nehmen → Fall 6 rot;
`VERBINDUNG` auf `/./` setzen → Fall 5 rot (jeder TypeError hieße „Server nicht erreichbar“).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'serverfehler.js')
ABRUF = Jsmodul('gemeinsam', 'serverabruf.js')

SKRIPT = """
const { Serverfehler: F } = await import(MODUL);
globalThis.location = { host: '127.0.0.1:8081' };
const mit = (status, rumpf, daten = null, adresse = '/api/mesh3d/2026.10.11.21.49.06/zustand/') => {
    const f = new Error(`${status} Internal Server Error bei ${adresse} — ${rumpf.slice(0, 200)}`);
    Object.assign(f, { status, adresse, rumpf, daten });
    return f;
};

// --- 1. Die Verbindung ist weg
for (const text of ['Failed to fetch', 'NetworkError when attempting to fetch resource.', 'Load failed']) {
    const f = F.verstaendlich(new TypeError(text));
    pruefe('1 Satz ' + text, f.message.startsWith('Server nicht erreichbar (127.0.0.1:8081)'), true);
    pruefe('1 Klasse ' + text, f instanceof TypeError, true);
    pruefe('1 technisch ' + text, f.technisch, text);
    pruefe('1 Browsertext bleibt lesbar ' + text, f.message.includes(text), true);
}

// --- 2. Ein 500 mit der HTML-Seite des Servers
const html = '<html> <head> <title>500 Internal Server Error</title> </head> <body> <h1>Internal Server Error</h1> </body> </html>';
let f = F.verstaendlich(mit(500, html));
pruefe('2 Satz', f.message.startsWith('Server-Fehler 500 bei /api/mesh3d/2026.10.11.21.49.06/zustand/'), true);
pruefe('2 kein HTML in der Meldung', f.message.includes('<'), false);
pruefe('2 sagt, wo die Ursache steht', f.message.includes('Hilfe → Logs → Exceptions'), true);
pruefe('2 Status bleibt', f.status, 500); pruefe('2 Rumpf bleibt', f.rumpf, html); pruefe('2 Adresse bleibt', f.adresse, '/api/mesh3d/2026.10.11.21.49.06/zustand/');

// --- 3. Ein Vorrechner, hinter dem niemand antwortet
for (const status of [502, 503, 504]) {
    f = F.verstaendlich(mit(status, '<html>Bad gateway</html>'));
    pruefe('3 ' + status, f.message.startsWith('Server nicht erreichbar'), true);
    pruefe('3 ' + status + ' Status', f.message.includes(`Antwort ${status}`), true);
}

// --- 4. Der Server begründet selbst: unberührt
for (const [status, daten] of [[400, { ok: false, error: 'Eigener Name fehlt' }], [404, { error: 'Kein Auftrag' }], [409, { error: 'Der Auftrag rechnet' }], [500, { error: 'Netz fehlt' }]]) {
    f = mit(status, JSON.stringify(daten), daten); const vorher = f.message;
    F.verstaendlich(f);
    pruefe('4 unberührt ' + status, [f.message, f.verstaendlich], [vorher, undefined]);
}
f = mit(404, '<html>Not Found</html>'); const vor = f.message; F.verstaendlich(f);
pruefe('4 404 ohne JSON bleibt wie es war', f.message, vor);

// --- 5. Eigener Fehler und Abbruch sind kein Serverproblem
f = F.verstaendlich(new TypeError("Cannot read properties of undefined (reading 'x')"));
pruefe('5 Codefehler', f.message, "Cannot read properties of undefined (reading 'x')");
const abbruch = new Error('The user aborted a request.'); abbruch.name = 'AbortError';
pruefe('5 Abbruch', F.verstaendlich(abbruch).message, 'The user aborted a request.');
pruefe('5 null und Text', [F.verstaendlich(null), F.verstaendlich('x')], [null, 'x']);

// --- 6. Zweimal ändert nichts; durch den Serverabruf der Seiten kommt dieselbe Meldung an
f = F.verstaendlich(new TypeError('Failed to fetch')); const einmal = f.message;
pruefe('6 zweimal', [F.verstaendlich(f).message, F.verstaendlich(f).technisch], [einmal, 'Failed to fetch']);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_ABRUF = """
const { Serverabruf: S } = await import(MODUL);
globalThis.location = { host: '127.0.0.1:8081' };
globalThis.document = { cookie: '', querySelector: () => null };
const adresse = '/api/mesh3d/2026.10.11.21.49.06/zustand/';
const versuche = async () => { try { await S.json(adresse); } catch (f) { return f; } return null; };

// 1. Der Server ist aus
globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
let f = await versuche();
pruefe('1 nicht erreichbar', f.message.startsWith('Server nicht erreichbar (127.0.0.1:8081)'), true);
pruefe('1 noch ein TypeError', f instanceof TypeError, true);

// 2. Der Server stirbt gerade und liefert die HTML-Seite
const html = '<html> <head> <title>500 Internal Server Error</title> </head></html>';
globalThis.fetch = async () => ({ ok: false, status: 500, statusText: 'Internal Server Error', clone() { return this; }, text: async () => html, json: async () => { throw new Error('kein JSON'); } });
f = await versuche();
pruefe('2 Server-Fehler', f.message.startsWith('Server-Fehler 500 bei ' + adresse), true);
pruefe('2 ohne HTML', f.message.includes('<html'), false);
pruefe('2 Status', f.status, 500);

// 3. Eine begründete Antwort bleibt, wie sie ist
const json = JSON.stringify({ ok: false, error: 'Kein Auftrag 2026.10.11.21.49.06' });
globalThis.fetch = async () => ({ ok: false, status: 404, statusText: 'Not Found', clone() { return this; }, text: async () => json, json: async () => JSON.parse(json) });
f = await versuche();
pruefe('3 Begründung bleibt', f.message.includes('Kein Auftrag 2026.10.11.21.49.06'), true);
pruefe('3 nicht umgeschrieben', f.verstaendlich, undefined);
console.log(JSON.stringify({ ok: true }));
"""


class ServerfehlerTest(SimpleTestCase):
    databases = set()

    def test_1_die_meldung_sagt_was_los_ist(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_2_jede_seite_bekommt_sie_ueber_den_serverabruf(self):
        ausgabe = ABRUF.laufen(SKRIPT_ABRUF)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
