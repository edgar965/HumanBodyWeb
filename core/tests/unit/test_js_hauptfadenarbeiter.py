# -*- coding: utf-8 -*-
"""`Hauptfadenarbeiter`: der Wächter, der ins Seitenlog schreibt, WÄHREND der Hauptfaden der Seite steht.

Edgar, 05.10.2026: „warum sind keine Logs sichtbar, wenn ich auf den Tab Iterationen klicke?" — Jede Log-Zeile geht vom Hauptfaden ab; steht er, schweigt das Log, und der
Beobachter für lange Aufgaben meldet erst nach deren Ende.

Geprüft wird die Logik mit einer simulierten Uhr, ohne Worker und ohne Netz: antwortet der Hauptfaden, bleibt es still; nach `STILL_MS` ohne Antwort EINE Meldung, danach
höchstens alle `WIEDERHOLEN_MS`; die Antwort meldet das Ende mit der Dauer; ein verdeckter Tab und das Sichtbarwerden melden nichts.

Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `tick` die Zeile `if (!this.sichtbar || …)` auf `if (still < …)` kürzen → Fall 5 rot; in `gehoert` die Zeile mit `haenger_ende` streichen → Fall 4 rot; in `sichtbarWert`
`this.antwort = …` streichen → Fall 6 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hauptfadenarbeiter.js')

SKRIPT = """
const { Hauptfadenarbeiter } = await import(MODUL);
const pruefe = (was, ok) => { if (!ok) throw new Error(was); };

let jetzt = 0;
const takte = [], meldungen = [], anHaupt = [];
const arbeiter = new Hauptfadenarbeiter({
    jetzt: () => jetzt,
    takt: (rueckruf, ms) => { takte.push({ rueckruf, ms }); },
    anfragen: (adresse, optionen) => { meldungen.push({ jetzt, adresse, ...JSON.parse(optionen.body) }); return { catch: () => {} }; },
    anHaupt: nachricht => anHaupt.push(nachricht),
});
const weiter = (ms, antwortet) => {
    for (const ende = jetzt + ms; jetzt < ende;) {
        jetzt += 500;
        takte.forEach(t => t.rueckruf());
        if (antwortet) arbeiter.behandeln({ typ: 'pong' });
    }
};
arbeiter.behandeln({ typ: 'start', adresse: 'http://x/api/log/', seite: 'engine2d3dkleider', kennung: 'abcd' });

// --- 1. Der Takt steht, und jeder Takt fragt den Hauptfaden an ----------------
pruefe('1 ein Takt zu 500 ms', takte.length === 1 && takte[0].ms === Hauptfadenarbeiter.TAKT_MS);
weiter(10000, true);
pruefe('1 jeder Takt ein ping', anHaupt.length === 20 && anHaupt.every(n => n.typ === 'ping'));

// --- 2. Antwortet der Hauptfaden, bleibt es still -----------------------------
pruefe('2 still', meldungen.length === 0);

// --- 3. Ohne Antwort: nach STILL_MS EINE Meldung, dann erst nach WIEDERHOLEN_MS wieder
weiter(1000, false);
pruefe('3 nach 1 s noch nichts', meldungen.length === 0);
weiter(1000, false);
pruefe('3 nach 2 s eine Meldung', meldungen.length === 1 && meldungen[0].action === 'haenger_live' && meldungen[0].level === 'warning');
pruefe('3 Adresse, Seite, Kennung', meldungen[0].adresse === 'http://x/api/log/' && meldungen[0].page === 'engine2d3dkleider' && meldungen[0].detail.startsWith('[abcd] '));
weiter(3000, false);
pruefe('3 nach 5 s nicht noch einmal', meldungen.length === 1);
weiter(3000, false);
pruefe('3 nach 8 s die Wiederholung', meldungen.length === 2);

// --- 4. Die Antwort meldet das Ende mit der Dauer (letzte Antwort 10.000 ms, jetzt 18.000 ms)
arbeiter.behandeln({ typ: 'pong' });
pruefe('4 Ende gemeldet', meldungen.length === 3 && meldungen[2].action === 'haenger_ende' && /nach 8\\.0 s/.test(meldungen[2].detail));
weiter(5000, true);
pruefe('4 danach wieder still', meldungen.length === 3);

// --- 5. Ein verdeckter Tab wird nicht gemeldet -------------------------------
arbeiter.behandeln({ typ: 'sicht', wert: false });
weiter(10000, false);
pruefe('5 verdeckt: still', meldungen.length === 3);

// --- 6. Beim Sichtbarwerden beginnt die Zählung neu --------------------------
arbeiter.behandeln({ typ: 'sicht', wert: true });
weiter(1000, false);
pruefe('6 keine Meldung für die Pause im verdeckten Zustand', meldungen.length === 3);
weiter(1000, false);
pruefe('6 ein echter Stillstand danach wird gemeldet', meldungen.length === 4 && meldungen[3].action === 'haenger_live');

console.log(JSON.stringify({ ok: true }));
"""


class DerHauptfadenarbeiter(SimpleTestCase):
    databases = set()

    def test_meldet_den_stillstand_waehrend_er_dauert_und_dessen_ende(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))
