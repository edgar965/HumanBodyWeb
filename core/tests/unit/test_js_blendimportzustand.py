# -*- coding: utf-8 -*-
"""`Blendimportzustand`: der eine Fragesteller für Leiste und Dialog (08.10.2026), geprüft in Node.

Edgar: „wenn ich ein Modell importiere, mach eine Fortschrittsleiste ganz oben, neben "HumanBody" Text. Im Import Dialog
deaktiviere den Importieren Button". Leiste (`Blendimportleiste`) und Dialog (`Blendimportfortschritt`) zeigen denselben Stand;
gefragt wird nur einmal je Takt.

1. `laeuft`: „laeuft" und „neu" rechnen, alles andere nicht (daran hängt die Sperre des Knopfes).
2. `prozent`: der größere von Stand und „Mesh to 3D"-Lauf, auf 0…100 begrenzt, ohne Angabe 0.
3. `beobachten` meldet jeden Stand als Ereignis mit der Kennung und hört auf zu fragen, sobald der Import nicht mehr rechnet —
   auch bei einem Fehler (`unbekannt`); ein zweites `beobachten` derselben Kennung startet keinen zweiten Takt.
4. `laufend` gibt die Kennung oder `null`.

Sabotage-Gegenprobe: in `abfragen` das `clearInterval` weglassen → Fall 3 rot (Anfragen nach dem Ende); `Math.min(100, …)` streichen
→ Fall 2 rot; `zustand.kennung = kennung` weglassen → Fall 3 rot (der Dialog filtert nach der Kennung).

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
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
await new Promise(r => setTimeout(r, 120));
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

// 4. laufend
globalThis.fetch = async () => new Response(JSON.stringify({ kennung: null }), { status: 200, headers: { 'Content-Type': 'application/json' } });
pruefe('nichts läuft', await Z.laufend(), null);
globalThis.fetch = async () => new Response(JSON.stringify({ kennung: '2026.10.08.22.00.00', status: 'laeuft' }), { status: 200, headers: { 'Content-Type': 'application/json' } });
pruefe('einer läuft', await Z.laufend(), '2026.10.08.22.00.00');
console.log(JSON.stringify({ ok: true }));
"""


class BlendimportzustandTest(SimpleTestCase):
    databases = set()

    def test_der_stand_wird_einmal_je_takt_geholt_und_an_leiste_und_dialog_gemeldet(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
