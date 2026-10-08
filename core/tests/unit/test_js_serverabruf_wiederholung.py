# -*- coding: utf-8 -*-
"""`Serverabruf` (gemeinsam/serverabruf.js): eine Netzanfrage, deren VERBINDUNG abreißt, wird wiederholt (08.10.2026).

Edgar: „Edgar importiert, T-Shirt hinzugefügt – funktioniert nicht". Eine andere Sitzung speicherte eine Python-Datei, der
Autoreload startete den Server neu — mitten in `POST …/garderobe/g9_base_shirt/netz/` (`client.log` 22:27:07: `Failed to
fetch` nach 2,8 s). Das Stück kam nie, das Häkchen blieb.

Das Modul läuft hier wirklich, mit einem `fetch`, der spielt, was der Browser sah:
  1. die Verbindung reißt zweimal (`TypeError: Failed to fetch`), dann antwortet der Server: die Antwort kommt an, nach
     drei Abrufen, mit derselben Nutzlast;
  2. der Server antwortet mit Fehlerstatus (500): KEIN zweiter Versuch, der Fehler kommt sofort durch;
  3. der Server kommt nie zurück: nach `NETZ_VERSUCHE` Abrufen der ursprüngliche `TypeError`;
  4. ein Abbruch durch den Aufrufer (`AbortError`) wird nicht wiederholt.

Sabotage-Gegenprobe: `_mitWiederholung` durch einen einfachen Aufruf ersetzen → Fall 1 rot; die `TypeError`-Prüfung
weglassen und alles wiederholen → Fall 2 und 4 rot; `NETZ_VERSUCHE` ignorieren → Fall 3 hängt (Zeitgrenze von Node).

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'serverabruf.js')

SKRIPT = """
const { Serverabruf: S } = await import(MODUL);
S.NETZ_PAUSE_MS = 1;
globalThis.document = { cookie: '', querySelector: () => null };   // Serverabruf._csrfKopf liest Cookies
const antwortJson = (status, daten) => ({
    ok: status >= 200 && status < 300, status, statusText: String(status),
    clone() { return this; },
    headers: { get: () => 'application/json' },
    json: async () => daten, text: async () => JSON.stringify(daten),
});
const adresse = '/api/character/genesis9-figur/garderobe/g9_base_shirt/netz/';

// --- 1. gerissen, dann antwortet der Server -----------------------------
let abrufe = 0;
const nutzlasten = [];
globalThis.fetch = async (url, opts = {}) => {
    abrufe += 1;
    nutzlasten.push(opts.body);
    if (abrufe < 3) throw new TypeError('Failed to fetch');
    return antwortJson(200, { teile: [{ name: 'shirt' }] });
};
const antwort = await S.netzSenden(adresse, { regler: { a: 1 } });
pruefe('Antwort kam an', antwort.teile[0].name, 'shirt');
pruefe('beim dritten Abruf', abrufe, 3);
pruefe('dieselbe Nutzlast', nutzlasten.every(n => n === nutzlasten[0]) && nutzlasten[0].includes('"regler"'), true);

// --- 2. Fehlerstatus: kein zweiter Versuch ------------------------------
abrufe = 0;
globalThis.fetch = async () => { abrufe += 1; return antwortJson(500, { fehler: 'kaputt' }); };
let fehler = null;
try { await S.netzSenden(adresse, {}); } catch (f) { fehler = f; }
pruefe('Fehlerstatus kommt durch', fehler !== null, true);
pruefe('nur ein Abruf', abrufe, 1);

// --- 3. der Server kommt nie zurück -------------------------------------
abrufe = 0;
globalThis.fetch = async () => { abrufe += 1; throw new TypeError('Failed to fetch'); };
fehler = null;
try { await S.netzSenden(adresse, {}); } catch (f) { fehler = f; }
pruefe('ursprünglicher Fehler', fehler instanceof TypeError, true);
pruefe('alle Versuche genutzt', abrufe, S.NETZ_VERSUCHE);

// --- 4. Abbruch durch den Aufrufer --------------------------------------
abrufe = 0;
globalThis.fetch = async () => {
    abrufe += 1;
    const abbruch = new Error('The user aborted a request.'); abbruch.name = 'AbortError'; throw abbruch;
};
fehler = null;
try { await S.netzSenden(adresse, {}); } catch (f) { fehler = f; }
pruefe('Abbruch kommt durch', fehler?.name, 'AbortError');
pruefe('Abbruch nur einmal', abrufe, 1);

// --- 5. der GET-Weg (`netz`) wiederholt ebenso --------------------------
abrufe = 0;
globalThis.fetch = async () => {
    abrufe += 1;
    if (abrufe < 2) throw new TypeError('Failed to fetch');
    return antwortJson(200, { ok: 1 });
};
const geholt = await S.netz('/api/character/genesis9-figur/basis/netz/');
pruefe('GET nachgeholt', [geholt.ok, abrufe], [1, 2]);
console.log(JSON.stringify({ ok: true }));
"""


class ServerabrufWiederholungTest(SimpleTestCase):
    databases = set()

    def test_abgerissene_netzanfragen_werden_wiederholt_fehlerantworten_nicht(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
