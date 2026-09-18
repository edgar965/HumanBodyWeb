# -*- coding: utf-8 -*-
u"""`Netzstufe` (Strg+Alt+H): Keks lesen und schreiben, Taste erkennen, umschalten.

In Node mit Attrappen für `document`, `window` und `location`:

1. `gewaehlt` liest `netzstufen=3` aus dem Keks-Text, auch hinter anderen
   Keksen; 0, 4, Text und Fehlen → null.
2. `keksText` setzt ein Jahr, null löscht (`max-age=0`), beide mit `path=/`.
3. `istTaste`: Strg+Alt+H ja, ohne Strg / mit Shift / andere Taste nein.
4. `naechste`: null → 3, 3 → null, 2 → 3.
5. `einrichten` fängt die Taste in der Fangphase, setzt den Keks, zeigt das
   Abzeichen mit „lädt neu" und lädt die Seite neu; andere Tasten tun nichts;
   der zweite Druck löscht den Keks; ohne Keks verschwindet das Abzeichen.

Sabotage-Gegenprobe: `ereignis.code === TASTE` weg → Fall 3 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'netzstufe.js')

SKRIPT = """
const elemente = [];
const element = () => ({ style: {}, textContent: '', id: '', entfernt: false,
                         remove() { this.entfernt = true; } });
globalThis.document = {
    cookie: '',
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
pruefe('text laedt', N.text(null, true), 'Netz: Einstellung — Seite lädt neu …');

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
pruefe('keks gesetzt', document.cookie.startsWith('netzstufen=3; path=/;'), true);
pruefe('abzeichen laedt', elemente[0].textContent,
       'Netz: hohe Auflösung (3 Stufen) — Seite lädt neu …');
pruefe('neu geladen', neugeladen, 1);

document.cookie = 'netzstufen=3';
pruefe('abzeichen mit keks', N.abzeichen().textContent, N.text(3));
druck({});
pruefe('zurueck: keks geloescht', document.cookie, N.keksText(null));
pruefe('zurueck: abzeichen', elemente[0].textContent, N.text(null, true));
document.cookie = '';
pruefe('ohne keks weg', N.abzeichen(), null);
pruefe('entfernt', elemente[0].entfernt, true);
console.log(JSON.stringify({ ok: true }));
"""


class NetzstufeTest(SimpleTestCase):

    def test_keks_taste_und_umschalten(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
