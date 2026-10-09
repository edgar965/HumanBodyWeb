# -*- coding: utf-8 -*-
"""`Serverprotokoll` (gemeinsam/serverprotokoll.js): Meldungen aus dem Browser überleben einen Serverausfall (09.10.2026).

Edgar: „Fehler beim Importieren … siehe logs", „Failed to fetch" ca. eine Minute, „warum erscheint das nicht in dem Error
log??". Djangos Autoreload hatte den Server neu gestartet (09:59:22 → 10:00:11); die Meldung des Browsers ging an denselben
Server und ging ins Leere (`.catch(() => {})`). Im Fehlerlog stand nichts.

Das Modul läuft hier wirklich, mit einem `fetch`, der den Server spielt:
  1. Server da: die Meldung geht sofort raus, nichts bleibt liegen;
  2. Server weg: Meldungen bleiben liegen (und es geht keine zweite Anfrage in die Leere, solange der Ausfall dauert);
  3. Server wieder da: alle kommen nach, in der Reihenfolge, mit der Browser-Uhrzeit, und danach genau EINE
     Zusammenfassung `verbindung_unterbrochen` — bei langem Ausfall auf Stufe `error` (das allein erreicht `error.log`),
     bei kurzem als `warning`;
  4. eine Antwort mit Fehlerstatus (500) ist kein Ausfall;
  5. mehr als `MAX_WARTEND` Meldungen: die ältesten fallen weg, die Zusammenfassung zählt sie.

Sabotage-Gegenprobe: in `melden` das `.then(…, () => { _ausfall })` durch ein stummes `.catch(() => {})` ersetzen → Fall 2 und 3
rot; die Stufe der Zusammenfassung fest auf `info` setzen → Fall 3 rot; den Status der Antwort als Ausfall zählen → Fall 4 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`. Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage. Im Chrome
am echten Import gesehen: 12 Meldungen nachgeliefert, `error.log` trägt die Zusammenfassung.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'serverprotokoll.js')

SKRIPT = """
const { Serverprotokoll: P } = await import(MODUL);
P.PRUEFEN_MS = 5;
const kommen = [];
let da = true;
let status = 200;
globalThis.fetch = async (url, opts) => {
    if (!da) throw new TypeError('Failed to fetch');
    kommen.push(JSON.parse(opts.body));
    return { ok: status < 400, status };
};
const warte = ms => new Promise(r => setTimeout(r, ms));

// --- 1. Server da -------------------------------------------------------
await P.melden('scene', 'a1', 'eins', 'info');
pruefe('sofort gesendet', kommen.map(k => k.action), ['a1']);
pruefe('nichts liegt', P.wartend(), 0);

// --- 2. Server weg ------------------------------------------------------
da = false;
await P.melden('scene', 'a2', 'zwei', 'warnung');
await P.melden('scene', 'a3', 'drei', 'info');
await P.melden('scene', 'a4', 'vier', 'info');
pruefe('drei liegen', P.wartend(), 3);
pruefe('beim Ausfall nichts mehr gesendet', kommen.length, 1);

// --- 3. Server wieder da -----------------------------------------------
await warte(30);
pruefe('weiter weg: nichts gesendet', kommen.length, 1);
P._seit -= 12000;                                   // der Ausfall dauerte „12 s"
da = true;
await warte(60);
pruefe('Reihenfolge', kommen.slice(1, 4).map(k => k.action), ['a2', 'a3', 'a4']);
pruefe('mit Browser-Uhrzeit', /\\[Browser \\d\\d:\\d\\d:\\d\\d, nachgeliefert\\]/.test(kommen[1].detail), true);
pruefe('Stufe bleibt', kommen[1].level, 'warnung');
const zusammenfassung = kommen[kommen.length - 1];
pruefe('eine Zusammenfassung', kommen.filter(k => k.action === 'verbindung_unterbrochen').length, 1);
pruefe('als Fehler (langer Ausfall)', zusammenfassung.level, 'error');
pruefe('nennt Dauer und Anzahl', /Server 1[23] s nicht erreichbar/.test(zusammenfassung.detail) && zusammenfassung.detail.includes('3 Meldungen nachgeliefert'), true);
pruefe('nichts liegt mehr', P.wartend(), 0);

// kurzer Ausfall: nur eine Warnung
kommen.length = 0;
da = false;
await P.melden('scene', 'b1', '', 'info');
da = true;
await warte(60);
pruefe('kurzer Ausfall: Warnung', kommen[kommen.length - 1].level, 'warning');

// --- 4. Fehlerstatus ist kein Ausfall -----------------------------------
kommen.length = 0;
status = 500;
await P.melden('scene', 'c1', '', 'info');
pruefe('500: gesendet, nichts liegt', [kommen.length, P.wartend()], [1, 0]);
status = 200;

// --- 5. Obergrenze --------------------------------------------------------
kommen.length = 0;
P.MAX_WARTEND = 3;
da = false;
for (let i = 0; i < 6; i++) await P.melden('scene', `d${i}`, '', 'info');
pruefe('nur die letzten drei', P.wartend(), 3);
da = true;
await warte(60);
pruefe('die neuesten kommen nach', kommen.slice(0, 3).map(k => k.action), ['d3', 'd4', 'd5']);
pruefe('Zusammenfassung zählt die verworfenen', kommen[kommen.length - 1].detail.includes('3 verworfen'), true);
console.log(JSON.stringify({ ok: true }));
"""


class ServerprotokollTest(SimpleTestCase):
    databases = set()

    def test_meldungen_ueberleben_einen_serverausfall_und_der_ausfall_steht_im_fehlerlog(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
