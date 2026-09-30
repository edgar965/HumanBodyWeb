# -*- coding: utf-8 -*-
u"""`Netzstufe` (Strg+Alt+H): Keks lesen und schreiben, Taste erkennen, umschalten.

In Node mit Attrappen für `document`, `window` und `location`:

1. `gewaehlt` liest `netzstufen=3` aus dem Keks-Text, auch hinter anderen
   Keksen; 0, 4, Text und Fehlen → null.
2. `keksText` setzt ein Jahr, null löscht (`max-age=0`), beide mit `path=/`.
3. `istTaste`: Strg+Alt+H ja, ohne Strg / mit Shift / andere Taste nein.
4. `naechste`: null → 3, 3 → null, 2 → 3.
5. `einrichten` fängt die Taste in der Fangphase, setzt den Keks, zeigt das
   Abzeichen mit „lädt" und lädt die Seite neu; andere Tasten tun nichts;
   der zweite Druck löscht den Keks; ohne Keks verschwindet das Abzeichen.
6. `umschalten(umbauen)` (18.09.2026 abends): liefert `umbauen` true, bleibt
   die Seite stehen (kein `reload`, Abzeichen ohne „lädt"); liefert es false
   oder wirft es, lädt die Seite neu wie bisher.
7. Einmal-Keks (30.09.2026, „per default lade die modelle nicht in der hohen
   auflösung"): Vor dem Neuladen auf die hohe Stufe steht `netzstufen_neuladen=1`
   (der Server behält nur dann die Stufe, `Netzstufenwahl.seite_zuruecksetzen`);
   beim Zurückschalten und beim Umbau ohne Neuladen nicht.

`document.cookie` ist eine Keksdose wie im Browser (jede Zuweisung setzt EINEN
Keks, `max-age=0` löscht ihn) — die frühere Attrappe ersetzte bei jeder Zuweisung
den ganzen Text und hätte den Einmal-Keks mit dem Stufen-Keks verwechselt.

Sabotage-Gegenprobe: `ereignis.code === TASTE` weg → Fall 3 rot; die Zeile mit
`NEULADEN` in `umschalten` weg → Fall 7 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'netzstufe.js')

SKRIPT = """
const elemente = [];
const element = () => ({ style: {}, textContent: '', id: '', entfernt: false,
                         remove() { this.entfernt = true; } });
const glas = new Map();
const gesetzt = [];
globalThis.document = {
    get cookie() { return [...glas].map(([k, v]) => `${k}=${v}`).join('; '); },
    set cookie(text) {
        gesetzt.push(text);
        const [paar] = text.split(';');
        const [name, wert = ''] = paar.split('=');
        if (wert === '' || /max-age=0(;|$)/.test(text)) glas.delete(name.trim());
        else glas.set(name.trim(), wert);
    },
    getElementById: (id) => elemente.find(e => e.id === id && !e.entfernt) || null,
    createElement: () => element(),
    body: { appendChild: (e) => elemente.push(e) },
};
let neugeladen = 0;
globalThis.location = { reload() { neugeladen += 1; } };
const { Netzstufe: N } = await import(MODUL);

pruefe('keks 3', N.gewaehlt('a=1; netzstufen=3; b=2'), 3);
pruefe('keks vorn', N.gewaehlt('netzstufen=1'), 1);
pruefe('keks 0', N.gewaehlt('netzstufen=0'), null);
pruefe('keks 4', N.gewaehlt('netzstufen=4'), null);
pruefe('keks text', N.gewaehlt('netzstufen=x'), null);
pruefe('kein keks', N.gewaehlt('andere=3'), null);
pruefe('leer', N.gewaehlt(''), null);
pruefe('setzen', N.keksText(3),
       'netzstufen=3; path=/; max-age=31536000; SameSite=Lax');
pruefe('loeschen', N.keksText(null),
       'netzstufen=; path=/; max-age=0; SameSite=Lax');

const taste = (extra) => ({ ctrlKey: true, altKey: true, shiftKey: false,
                            code: 'KeyH', ...extra });
pruefe('strg alt h', N.istTaste(taste({})), true);
pruefe('ohne strg', N.istTaste(taste({ ctrlKey: false })), false);
pruefe('mit shift', N.istTaste(taste({ shiftKey: true })), false);
pruefe('andere taste', N.istTaste(taste({ code: 'KeyG' })), false);
pruefe('naechste', [N.naechste(null), N.naechste(3), N.naechste(2)], [3, null, 3]);
pruefe('text', N.text(3),
       'Netz: hohe Auflösung (3 Stufen) · Strg+Alt+H schaltet um');
pruefe('text laedt', N.text(null, true), 'Netz: Einstellung — lädt …');

const horcher = [];
const fenster = {
    addEventListener: (art, f, fang) => horcher.push({ art, f, fang }) };
N.einrichten(fenster);
pruefe('fangphase', [horcher.length, horcher[0].art, horcher[0].fang],
       [1, 'keydown', true]);
pruefe('kein abzeichen ohne keks', elemente.length, 0);
let verhindert = 0, gestoppt = 0;
const druck = (extra) => horcher[0].f({
    ...taste(extra), preventDefault() { verhindert += 1; },
    stopImmediatePropagation() { gestoppt += 1; } });
druck({ code: 'KeyG' });
pruefe('andere taste tut nichts', [verhindert, neugeladen], [0, 0]);
druck({});
pruefe('verhindert und gestoppt', [verhindert, gestoppt], [1, 1]);
pruefe('keks gesetzt', [gesetzt.includes(N.keksText(3)), N.gewaehlt()], [true, 3]);
pruefe('einmal-keks vor dem neuladen', gesetzt.at(-1).startsWith('netzstufen_neuladen=1; path=/;'), true);
pruefe('beide in der dose', document.cookie, 'netzstufen=3; netzstufen_neuladen=1');
pruefe('abzeichen laedt', elemente[0].textContent,
       'Netz: hohe Auflösung (3 Stufen) — lädt …');
pruefe('neu geladen', neugeladen, 1);

glas.clear();
document.cookie = 'netzstufen=3';
pruefe('abzeichen mit keks', N.abzeichen().textContent, N.text(3));
druck({});
pruefe('zurueck: keks geloescht', [N.gewaehlt(), gesetzt.at(-1)], [null, N.keksText(null)]);
pruefe('zurueck: kein einmal-keks', document.cookie.includes('netzstufen_neuladen'), false);
pruefe('zurueck: abzeichen', elemente[0].textContent, N.text(null, true));
glas.clear();
pruefe('ohne keks weg', N.abzeichen(), null);
pruefe('entfernt', elemente[0].entfernt, true);

// --- 6. Umbau ohne Neustart ---------------------------------------------
glas.clear();
let gebaut = [];
const vorher = neugeladen;
pruefe('umbau erledigt', await N.umschalten(async (s) => { gebaut.push(s); return true; }), false);
pruefe('umbau gerufen mit 3', gebaut, [3]);
pruefe('kein reload', neugeladen, vorher);
pruefe('umbau: kein einmal-keks', document.cookie.includes('netzstufen_neuladen'), false);
pruefe('abzeichen ohne laedt', N.abzeichen().textContent, N.text(3));
pruefe('umbau verweigert -> reload', await N.umschalten(async () => false), true);
pruefe('reload gezaehlt', neugeladen, vorher + 1);
pruefe('umbau wirft -> reload', await N.umschalten(async () => { throw new Error('x'); }), true);
pruefe('reload gezaehlt 2', neugeladen, vorher + 2);
console.log(JSON.stringify({ ok: true }));
"""


class NetzstufeTest(SimpleTestCase):

    def test_keks_taste_und_umschalten(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
