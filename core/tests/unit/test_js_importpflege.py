# -*- coding: utf-8 -*-
"""`Importpflege`: die Rückfragen beim Löschen eines Blender-Imports sagen, WAS bleibt und WARUM (Edgar, 10.10.2026), geprüft in Node.

Edgar am Dialog „Import „cute girl" löschen?" („Bleibt: 3 Stücke, die noch ein Modell oder ein anderer Import braucht"): „warum wird nicht alles
gelöscht? Mach eindeutige Meldung für den Grund, möglichst aber alles weg". Gemessen: die drei Stücke (Haar, Shirt, Shorts) hat der spätere Import
19.31.50 unter derselben Kennung neu geschrieben, und das Modell „cute girl" trägt sie.

1. `text`: nennt jedes bleibende Stück beim Namen und den Grund — nicht nur die Zahl — und weist auf die zweite Frage hin; ohne bleibende Stücke
   steht dort nichts davon.
2. `gruppiert`: Stücke mit demselben Grund stehen in EINER Zeile; dieselbe Kennung zählt nur einmal (mehrere alte Importe nennen dieselben Stücke).
3. `textTrotzdem`: die zweite Frage nennt Zahl, Papierkorb (zurückholbar), wer die Stücke verliert, und was „Abbrechen" tut (Stücke bleiben,
   Import wird trotzdem gelöscht).
4. `loeschen`: bleibt etwas stehen, kommt eine zweite Frage; „OK" schickt `stuecke_trotzdem: true`, „Abbrechen" `false` (der Import wird trotzdem
   gelöscht); ohne bleibende Stücke gibt es nur EINE Frage und `false`; sagt der Nutzer schon zum ersten Fenster „Abbrechen", wird nichts gesendet.

Sabotage-Gegenprobe: in `text` die Zeile mit `Importpflege.gruppiert(plan.behalten)` streichen → Fall 1 rot; in `gruppiert` die Prüfung `gesehen.has`
streichen → Fall 2 rot; in `loeschen` `stuecke_trotzdem: trotzdem` auf `false` setzen → Fall 4 rot; die zweite `window.confirm`-Zeile ungeprüft
immer `true` → Fall 4 rot (Abbrechen löscht trotzdem).

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter', 'importpflege.js')

SKRIPT = """
globalThis.window = globalThis;
globalThis.document = Object.assign(new EventTarget(), { cookie: '', querySelector: () => null });
const { Importpflege: P } = await import(MODUL);

const modell = 'Modell „cute girl"';
const spaeter = 'Import 2026.10.08.19.31.50';
const grund = 'Das Modell „cute girl" trägt sie; der Import 2026.10.08.19.31.50 hat sie unter derselben Kennung neu geschrieben';
const haar = { kennung: 'cute_girl_haar', name: 'cute girl Haar', benutzer: [modell, spaeter], grund };
const shirt = { kennung: 'cute_girl_shirt', name: 'cute girl Shirt', benutzer: [modell, spaeter], grund };
const hose = { kennung: 'cute_girl_shorts', name: 'cute girl Shorts', benutzer: [modell, spaeter], grund };
const plan = { kennung: 'k', name: 'cute girl', mb: 454.6, laeuft: false, schritt: 'modell', auftrag: { kennung: 'A1' },
               stuecke: [], modelle: [], behalten: [haar, shirt, hose] };

// 1. text nennt Namen und Grund
const text = P.text(plan, false);
pruefe('Name des Stücks', text.includes('cute girl Haar') && text.includes('cute girl Shorts'), true);
pruefe('Grund steht da', text.includes('trägt sie') && text.includes('derselben Kennung'), true);
pruefe('Hinweis auf die zweite Frage', text.includes('zweites Fenster'), true);
pruefe('nicht nur eine Zahl', text.includes('die noch ein Modell oder ein anderer Import braucht'), false);
const ohne = P.text({ ...plan, behalten: [] }, false);
pruefe('ohne bleibende Stücke keine Meldung', ohne.includes('Bleibt') || ohne.includes('zweites Fenster'), false);

// 2. gruppiert
pruefe('gleicher Grund, eine Zeile', P.gruppiert([haar, shirt, hose]).length, 1);
pruefe('Namen in der Zeile', P.gruppiert([haar, shirt, hose])[0].startsWith('• cute girl Haar, cute girl Shirt, cute girl Shorts: '), true);
pruefe('andere Gründe, zwei Zeilen', P.gruppiert([haar, { ...shirt, grund: 'anderer Grund' }]).length, 2);
pruefe('dieselbe Kennung nur einmal', P.gruppiert([haar, haar, haar])[0].split('cute girl Haar').length - 1, 1);

// 3. textTrotzdem
const frage = P.textTrotzdem(plan);
pruefe('Zahl', frage.includes('auch diese 3 Stücke'), true);
pruefe('Papierkorb', frage.includes('Papierkorb') && frage.includes('zurückholbar'), true);
pruefe('wer sie verliert, je einmal', frage.includes(modell + ' und ' + spaeter + ' verliert sie'), true);
pruefe('Abbrechen: Stücke bleiben, Import weg', frage.includes('Abbrechen: die Stücke bleiben') && frage.includes('trotzdem gelöscht'), true);

// 4. loeschen: der Ablauf der Fenster und was gesendet wird
const json = daten => new Response(JSON.stringify(daten), { status: 200, headers: { 'Content-Type': 'application/json' } });
async function lauf(planDaten, antworten) {
    const gesendet = [];
    const fragen = [];
    globalThis.fetch = async (adresse, wahl = {}) => {
        if ((wahl.method || 'GET') === 'POST') { gesendet.push(JSON.parse(wahl.body)); return json({ ok: true }); }
        return json(planDaten);
    };
    globalThis.confirm = text => { fragen.push(text); return antworten.shift(); };
    const ergebnis = await P.loeschen('k');
    return { ergebnis, gesendet, fragen };
}
let a = await lauf(plan, [true, true]);
pruefe('zwei Fragen, wenn etwas bleibt', a.fragen.length, 2);
pruefe('OK: Stücke trotzdem', [a.ergebnis, a.gesendet.map(g => g.stuecke_trotzdem)], [true, [true]]);
a = await lauf(plan, [true, false]);
pruefe('Abbrechen in der zweiten Frage: Stücke bleiben, Import weg', [a.ergebnis, a.gesendet.map(g => g.stuecke_trotzdem)], [true, [false]]);
a = await lauf({ ...plan, behalten: [] }, [true]);
pruefe('nichts bleibt: eine Frage, kein Trotzdem', [a.fragen.length, a.gesendet.map(g => g.stuecke_trotzdem)], [1, [false]]);
a = await lauf(plan, [false]);
pruefe('erste Frage abgelehnt: nichts gesendet', [a.ergebnis, a.gesendet.length, a.fragen.length], [false, 0, 1]);
console.log(JSON.stringify({ ok: true }));
"""


class ImportpflegeTest(SimpleTestCase):
    databases = set()

    def test_die_rueckfrage_nennt_den_grund_und_fragt_ob_die_stuecke_auch_weg_sollen(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
