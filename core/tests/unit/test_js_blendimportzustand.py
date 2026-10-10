# -*- coding: utf-8 -*-
"""`Blendimportzustand`: der eine Fragesteller für Leiste und Dialog (08.10.2026), geprüft in Node.

Edgar: „wenn ich ein Modell importiere, mach eine Fortschrittsleiste ganz oben, neben "HumanBody" Text. Im Import Dialog
deaktiviere den Importieren Button". Leiste (`Blendimportleiste`) und Dialog (`Blendimportfortschritt`) zeigen denselben Stand;
gefragt wird nur einmal je Takt.

1. `laeuft`: „laeuft" und „neu" rechnen, alles andere nicht (daran hängt die Sperre des Knopfes).
2. `prozent`: der größere von Stand und „Mesh to 3D"-Lauf, auf 0…100 begrenzt, ohne Angabe 0.
3. `beobachten` meldet jeden Stand als Ereignis mit der Kennung und hört auf zu fragen, sobald der Import nicht mehr rechnet —
   auch bei einem Fehler (`unbekannt`); ein zweites `beobachten` derselben Kennung startet keinen zweiten Takt.
3b. Reißt die VERBINDUNG ab (`TypeError`, der Server lädt nach einer gespeicherten Datei neu), meldet er `verbindung: 'getrennt'`
   mit dem letzten bekannten Stand und fragt weiter — nie „unbekannt" (09.10.2026, „Zustand nicht lesbar", Import lief weiter).
3c. Ein Fehlerstatus ab 500 (der alte Serverprozess beim Beenden: „500 … cannot schedule new futures after interpreter shutdown", 10.10.2026)
   gilt wie ein Verbindungsabbruch: `verbindung: 'getrennt'` mit „Fehler 500" im Hinweis, letzter Stand bleibt, Takt läuft weiter — nie
   „unbekannt". Ein Status unter 500 (404) bleibt ein echter Fehler.
4. `laufend` gibt die Kennung oder `null`.
5. `aufnehmen` (beim Laden der Seite) meldet den Kurzstand von `laufend` (Kennung, Name, Schritt) SOFORT als Ereignis `VORLAEUFIG` — vor dem ersten
   Zustand, der bei belegtem Server über eine Minute braucht; läuft nichts, kommt weder ein Ereignis noch ein Zustandsabruf (10.10.2026, Edgar:
   „ich sehe den job nicht im UI"; `client.log`: `laufend` 1,2 s, der Zustand danach 75,7 s).
6. Sperre: der Takt fragt nicht nach, solange die vorige Abfrage aussteht (nie zwei zugleich), und danach weiter, bis der Import fertig ist.
7. Hängt eine Abfrage länger als `FRIST_MS`, geht eine neue los — die Leiste bleibt nicht für immer auf dem alten Stand.
8. Die späte Antwort eines Imports, den niemand mehr beobachtet (anderer gewählt, gelöscht), wird verworfen und stoppt den Takt des neuen nicht.

Sabotage-Gegenprobe: in `abfragen` das `clearInterval` weglassen → Fall 3 rot (Anfragen nach dem Ende); `Math.min(100, …)` streichen
→ Fall 2 rot; `zustand.kennung = kennung` weglassen → Fall 3 rot (der Dialog filtert nach der Kennung); die Zeile
`if (fehler instanceof TypeError || fehler.status >= 500) return …_getrennt(kennung, fehler.status)` auf `fehler instanceof TypeError` kürzen →
Fall 3c rot (3b bleibt grün); sie ganz streichen → Fall 3b UND 3c rot. Fall 5: das `dispatchEvent(… VORLAEUFIG …)` in `aufnehmen` hinter das
`beobachten` setzen → „Kurzstand vor dem ersten Zustand" rot; es ganz streichen → „Kurzstand gemeldet" rot. Fall 6: in `abfragen` die Zeile `if (Blendimportzustand._unterwegs && …)` samt
Rückgabe streichen → „nie zwei Abfragen zugleich" rot; Fall 7: `Date.now() - …_unterwegsSeit < …FRIST_MS` durch `true` ersetzen → „nach der Frist …" rot (hängt); Fall 8: die zweite
Zeile `if (Blendimportzustand._kennung !== kennung) return null;` in `_holen` streichen → „die späte Antwort … verworfen" rot.

Nicht über `manage.py test` gelaufen (Stand 10.10.2026) — läuft nur auf Ansage. Trockenlauf ohne Django (`ProjektTemp/_wegwerf/import_serie/
js_trocken_web.py`, `Webmodul` direkt): alle Fälle grün; die Kürzung auf `TypeError` macht Fall 3c rot, die gestrichene Zeile Fall 3b. Fall 3b im
Chrome am echten Import gesehen (Ausfall per `fetch`-Attrappe); Fall 3c im Browser nicht gesehen.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter', 'blendimportzustand.js')

SKRIPT = """
globalThis.document = new EventTarget();
const { Blendimportzustand: Z } = await import(MODUL);

// 1. laeuft
pruefe('läuft', ['laeuft', 'neu', 'fertig', 'gescheitert', 'angehalten', 'unbekannt'].map(s => Z.laeuft({ status: s })),
       [true, true, false, false, false, false]);

// 2. prozent
pruefe('nur Stand', Z.prozent({ fortschritt: 30 }), 30);
pruefe('Lauf größer', Z.prozent({ fortschritt: 20, figur_lauf: { fortschritt: 45 } }), 45);
pruefe('Stand größer', Z.prozent({ fortschritt: 60, figur_lauf: { fortschritt: 45 } }), 60);
pruefe('über 100', Z.prozent({ fortschritt: 250 }), 100);
pruefe('ohne Angabe', Z.prozent({}), 0);

// 3. beobachten
Z.TAKT_MS = 5;
// Auf eine Bedingung warten statt feste Zeiten abzusitzen: bei voller CPU (Import, Virenscan) stocken die Timer, und ein 60-ms-Fenster mit „mehr als
// ein Tick" wurde zufällig rot (10.10.2026, im Trockenlauf einzeln auf rot, ohne dass der Code sich geändert hatte)
const warte = async (bedingung, ms = 3000) => { for (let t = 0; t < ms && !bedingung(); t += 10) await new Promise(r => setTimeout(r, 10)); };
const folge = [{ status: 'laeuft', fortschritt: 10 }, { status: 'laeuft', fortschritt: 50 }, { status: 'fertig', fortschritt: 100 }];
let anfragen = 0;
globalThis.fetch = async () => {
    const stand = folge[Math.min(anfragen, folge.length - 1)];
    anfragen += 1;
    return new Response(JSON.stringify(stand), { status: 200, headers: { 'Content-Type': 'application/json' } });
};
const gesehen = [];
document.addEventListener(Z.EREIGNIS, e => gesehen.push([e.detail.kennung, e.detail.status]));
const erster = Z.beobachten('k1');
Z.beobachten('k1');                                   // dieselbe Kennung: kein zweiter Takt
await erster;
await warte(() => gesehen.some(g => g[1] === 'fertig'));
const nachDemEnde = anfragen;
await new Promise(r => setTimeout(r, 60));
pruefe('keine Anfrage nach dem Ende', anfragen, nachDemEnde);
pruefe('letzter Stand', gesehen[gesehen.length - 1], ['k1', 'fertig']);
pruefe('Kennung an jedem Stand', gesehen.every(g => g[0] === 'k1'), true);
pruefe('alle drei Stände gemeldet', gesehen.some(g => g[1] === 'laeuft') && gesehen.some(g => g[1] === 'fertig'), true);

// … und bei einem Fehler: Stand „unbekannt", Takt aus
globalThis.fetch = async () => { throw new Error('Netz weg'); };
const fehler = [];
document.addEventListener(Z.EREIGNIS, e => { if (e.detail.kennung === 'k2') fehler.push(e.detail.status); });
await Z.beobachten('k2');
pruefe('Fehler gemeldet', fehler, ['unbekannt']);

// 3b. Die VERBINDUNG reißt (der Server lädt neu, `TypeError: Failed to fetch`): kein „unbekannt", der Takt läuft weiter,
// der letzte Stand bleibt stehen (09.10.2026: früher blieb die Leiste rot auf „Zustand nicht lesbar", der Import rechnete weiter)
const json = daten => new Response(JSON.stringify(daten), { status: 200, headers: { 'Content-Type': 'application/json' } });
let aus = false;
globalThis.fetch = async () => {
    if (aus) throw new TypeError('Failed to fetch');
    return json({ status: 'laeuft', fortschritt: 40, schritt: 'figur' });
};
const k3 = [];
document.addEventListener(Z.EREIGNIS, e => { if (e.detail.kennung === 'k3') k3.push(e.detail); });
await Z.beobachten('k3');
aus = true;
await warte(() => k3.filter(d => d.verbindung === 'getrennt').length > 1);
const getrennt = k3.filter(d => d.verbindung === 'getrennt');
pruefe('getrennt gemeldet, Takt läuft weiter', getrennt.length > 1, true);
pruefe('letzter Stand bleibt', [getrennt[0].status, getrennt[0].fortschritt, getrennt[0].schritt], ['laeuft', 40, 'figur']);
pruefe('nie „unbekannt"', k3.some(d => d.status === 'unbekannt'), false);
pruefe('Hinweis nennt den Import', getrennt[0].detail.includes('Import rechnet im Hintergrund weiter'), true);
aus = false;
await warte(() => k3[k3.length - 1]?.verbindung === undefined);
pruefe('wieder normal', k3[k3.length - 1].verbindung, undefined);
globalThis.fetch = async () => json({ status: 'fertig', fortschritt: 100 });        // Takt beenden
await warte(() => Z._uhr === null);

// 3c. Der Server antwortet mit einem Fehlerstatus ab 500 (10.10.2026: der alte Prozess lieferte beim Beenden „500 … cannot schedule new
// futures after interpreter shutdown", der Dialog zeigte die ganze HTML-Seite und fragte nie wieder): auch das ist „getrennt" — Hinweis mit dem
// Status, der Takt läuft weiter, nie „unbekannt"; ein Fehlerstatus unter 500 (hier 404) bleibt ein echter Fehler.
let status = 500;
globalThis.fetch = async () => status === 200 ? json({ status: 'laeuft', fortschritt: 55, schritt: 'haut' })
    : new Response('<html><head><title>500 Internal Server Error</title></head></html>', { status, headers: { 'Content-Type': 'text/html' } });
const k4 = [];
document.addEventListener(Z.EREIGNIS, e => { if (e.detail.kennung === 'k4') k4.push(e.detail); });
status = 200;
await Z.beobachten('k4');
status = 500;
await warte(() => k4.filter(d => d.verbindung === 'getrennt').length > 1);
const getrennt500 = k4.filter(d => d.verbindung === 'getrennt');
pruefe('500: getrennt gemeldet, Takt läuft weiter', getrennt500.length > 1, true);
pruefe('500: letzter Stand bleibt', [getrennt500[0].status, getrennt500[0].fortschritt, getrennt500[0].schritt], ['laeuft', 55, 'haut']);
pruefe('500: Hinweis nennt den Status', getrennt500[0].detail.includes('Fehler 500'), true);
pruefe('500: nie „unbekannt"', k4.some(d => d.status === 'unbekannt'), false);
status = 404;
await warte(() => k4[k4.length - 1]?.status === 'unbekannt');
pruefe('404 bleibt ein echter Fehler', k4[k4.length - 1].status, 'unbekannt');
globalThis.fetch = async () => json({ status: 'fertig', fortschritt: 100 });        // Takt beenden
await warte(() => Z._uhr === null);

// 4. laufend
globalThis.fetch = async () => new Response(JSON.stringify({ kennung: null }), { status: 200, headers: { 'Content-Type': 'application/json' } });
pruefe('nichts läuft', await Z.laufend(), null);
globalThis.fetch = async () => new Response(JSON.stringify({ kennung: '2026.10.08.22.00.00', status: 'laeuft' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
pruefe('einer läuft', await Z.laufend(), '2026.10.08.22.00.00');

// 5. aufnehmen (10.10.2026, „ich sehe den job nicht im UI"): der Kurzstand von `laufend` kommt SOFORT — der erste Zustandsabruf
// wartete beim Laden der Szene 75 s auf den einen Faden des Servers, und so lange fehlte die Leiste
const vor = [];
const echt = [];
document.addEventListener(Z.VORLAEUFIG, e => vor.push([Date.now(), e.detail]));
document.addEventListener(Z.EREIGNIS, e => { if (e.detail.kennung === 'k5') echt.push(Date.now()); });
globalThis.fetch = async url => {
    if (String(url).includes('/laufend/')) return json({ kennung: 'k5', status: 'laeuft', schritt: 'haut', name: 'Rainy' });
    await new Promise(r => setTimeout(r, 80));              // der belegte Server
    return json({ status: 'fertig', fortschritt: 100 });
};
await Z.aufnehmen();
pruefe('Kurzstand gemeldet', vor.length, 1);
pruefe('Kurzstand: Kennung, Name, Schritt, vorläufig', [vor[0][1].kennung, vor[0][1].quelle.name, vor[0][1].schritt, vor[0][1].vorlaeufig],
       ['k5', 'Rainy', 'haut', true]);
pruefe('Kurzstand vor dem ersten Zustand', echt.length > 0 && vor[0][0] + 50 <= echt[0], true);
vor.length = 0;
let zustandsabrufe = 0;
globalThis.fetch = async url => { if (!String(url).includes('/laufend/')) zustandsabrufe += 1; return json({ kennung: null }); };
pruefe('nichts läuft: null', await Z.aufnehmen(), null);
pruefe('nichts läuft: kein Kurzstand, kein Zustandsabruf', [vor.length, zustandsabrufe], [0, 0]);

// 6. Sperre (10.10.2026): der Takt (5 ms hier, 2 s in der Seite) fragt nicht nach, solange die vorige Abfrage aussteht
let offen6 = 0;
let gleichzeitig = 0;
let abrufe6 = 0;
globalThis.fetch = async () => {
    offen6 += 1; abrufe6 += 1; gleichzeitig = Math.max(gleichzeitig, offen6);
    await new Promise(r => setTimeout(r, 40));              // der belegte Server
    offen6 -= 1;
    return json({ status: abrufe6 < 3 ? 'laeuft' : 'fertig', fortschritt: 10 * abrufe6 });
};
await Z.beobachten('k6');
for (let i = 0; i < 100 && abrufe6 < 3; i += 1) await new Promise(r => setTimeout(r, 20));
await new Promise(r => setTimeout(r, 80));                  // nach dem Ende kommt nichts mehr
pruefe('nie zwei Abfragen zugleich', gleichzeitig, 1);
pruefe('der Takt fragt nach jeder Antwort weiter, bis der Import fertig ist', abrufe6, 3);

// 7. Hängt eine Abfrage länger als FRIST_MS, darf eine neue los — sonst bliebe die Leiste für immer auf dem alten Stand
Z.FRIST_MS = 40;
let abrufe7 = 0;
globalThis.fetch = async () => {
    abrufe7 += 1;
    if (abrufe7 === 1) return new Promise(() => {});        // die erste Antwort kommt nie
    return json({ status: 'fertig', fortschritt: 100 });
};
const gesehen7 = [];
document.addEventListener(Z.EREIGNIS, e => { if (e.detail.kennung === 'k7') gesehen7.push(e.detail.status); });
Z.beobachten('k7');
for (let i = 0; i < 100 && !gesehen7.length; i += 1) await new Promise(r => setTimeout(r, 20));
pruefe('nach der Frist kommt der Stand trotz hängender erster Abfrage', gesehen7, ['fertig']);
Z.FRIST_MS = 30000;

// 8. Die späte Antwort eines Imports, den niemand mehr beobachtet, zählt nicht und stoppt den Takt des neuen nicht
let abrufeB = 0;
const gesehen8 = [];
document.addEventListener(Z.EREIGNIS, e => { if (['ka', 'kb'].includes(e.detail.kennung)) gesehen8.push([e.detail.kennung, e.detail.status]); });
globalThis.fetch = async url => {
    if (String(url).includes('/ka/')) { await new Promise(r => setTimeout(r, 60)); return json({ status: 'fertig', fortschritt: 100 }); }
    abrufeB += 1;
    return json({ status: 'laeuft', fortschritt: 20 });
};
const alt = Z.beobachten('ka');
Z.beobachten('kb');
await alt;
await new Promise(r => setTimeout(r, 80));
const vorherB = abrufeB;
await warte(() => abrufeB > vorherB);
pruefe('die späte Antwort des alten Imports wird verworfen', gesehen8.some(g => g[0] === 'ka'), false);
pruefe('der Takt des neuen läuft weiter', abrufeB > vorherB, true);
globalThis.fetch = async () => json({ status: 'fertig', fortschritt: 100 });        // Takt beenden
await warte(() => Z._uhr === null);
console.log(JSON.stringify({ ok: true }));
"""


class BlendimportzustandTest(SimpleTestCase):
    databases = set()

    def test_der_stand_wird_einmal_je_takt_geholt_und_an_leiste_und_dialog_gemeldet(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
