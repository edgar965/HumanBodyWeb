# -*- coding: utf-8 -*-
"""`Zielnetzlive`: eine Anfrage je Zug, für alle Sichten (20.09.2026).

Edgar: „Modell-View mit 3D links, 2D rechts … Wenn ich die Regler ändere, dann
ändert sich gleich das 3D Modell links." Das Zielnetz holt EINE Klasse für die
Modellsicht oben und das 3D-Popup im Dialog — geprüft ohne Server, `Serverabruf.senden`
ist eine Attrappe:

1. Ohne Zuhörer keine Anfrage (`nachziehen` ist ein Leerlauf).
2. Drei `nachziehen()` innerhalb der Bündelzeit → EINE Anfrage, mit den Werten
   des Dialogs; die erste mit `netz: true`, jede weitere ohne (Dreiecke bleiben
   in `netz`).
3. Beide Zuhörer bekommen dieselbe Antwort, samt Dreiecken und Text; ein später
   angemeldeter Zuhörer bekommt die letzte Antwort sofort.
4. Läuft eine Anfrage, wartet die nächste (kein Stau): zwei Züge während der
   Antwort → genau eine Anfrage danach.
5. Sabotage: ohne die Bündelung (`WARTEN_MS = 0` und je Zug ein `holen()`) wären
   es drei Anfragen — der Test würde rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bildmodell', 'zielnetzlive.js')

SKRIPT = """
const { Zielnetzlive: Z } = await import(MODUL);
const { Serverabruf } = await import('/static/djangobase/js/serverabruf.js');
globalThis.performance = globalThis.performance || { now: () => Date.now() };
const anfragen = [];
let bremse = null;                                     // Promise, die eine Antwort zurückhält
Serverabruf.senden = async (adresse, rumpf) => {
    anfragen.push({ adresse, rumpf: JSON.parse(JSON.stringify(rumpf)) });
    if (bremse) await bremse;
    const aus = { ok: true, punkte: 'AAAA', anzahl: 4, hoehe_cm: 170, dauer_ms: 5,
                  bericht: { taille_breite: { nachher: 20 } } };
    if (rumpf.netz) { aus.dreiecke = 'BBBB'; aus.gewicht = 'CCCC'; }
    return aus;
};
const warte = ms => new Promise(r => setTimeout(r, ms));
let werte = { taille_breite: 20 };
const live = new Z({ adresse: p => '/api/x/' + p }, () => werte);
Z.WARTEN_MS = 20;

// 1. ohne Zuhörer keine Anfrage
live.nachziehen(); live.nachziehen(true);
await warte(60);
pruefe('ohne Zuhörer keine Anfrage', anfragen.length, 0);

// 2. Bündelung: drei Züge, eine Anfrage — mit netz
const a = [], b = [];
live.zuhoeren((antwort, netz, text) => a.push({ antwort, netz, text }));
live.zuhoeren((antwort, netz, text) => b.push({ antwort, netz, text }));
live.nachziehen(); live.nachziehen(); werte = { taille_breite: 19.5 }; live.nachziehen();
await warte(80);
pruefe('eine Anfrage', anfragen.length, 1);
pruefe('Adresse', anfragen[0].adresse, '/api/x/zielnetz3d/');
pruefe('Werte des Dialogs', anfragen[0].rumpf, { proportionen: { taille_breite: 19.5 }, netz: true });

// 3. beide Zuhörer, Dreiecke bleiben, Text
pruefe('Zuhörer a', a.length, 1);
pruefe('Zuhörer b', b.length, 1);
pruefe('Netz gemerkt', live.netz, { dreiecke: 'BBBB', gewicht: 'CCCC' });
pruefe('Netz an den Zuhörer', a[0].netz.dreiecke, 'BBBB');
pruefe('Bericht', live.bericht.taille_breite.nachher, 20);
pruefe('Text nennt Punkte', a[0].text.includes('4 Punkte'), true);
const c = [];
live.zuhoeren(antwort => c.push(antwort));
pruefe('Später Zuhörer bekommt die letzte Antwort sofort', c.length, 1);
live.nachziehen(true);
await warte(40);
pruefe('zweite Anfrage ohne netz', anfragen[1].rumpf.netz, false);

// 4. eine in der Luft: zwei Züge währenddessen → genau eine danach
let frei;
bremse = new Promise(r => { frei = r; });
live.nachziehen(true);
await warte(10);
pruefe('dritte läuft', anfragen.length, 3);
live.nachziehen(true); await warte(5); live.nachziehen(true); await warte(5);
pruefe('währenddessen keine weitere', anfragen.length, 3);
frei(); bremse = null;
await warte(40);
pruefe('danach genau eine nachgeholt', anfragen.length, 4);
pruefe('Zuhörer a hat alle Antworten', a.length, 4);

// 5. Sabotage: ohne Bündelung wären es drei
const vorher = anfragen.length;
await live.holen(); await live.holen(); await live.holen();
if (anfragen.length - vorher !== 3) {
    throw new Error('Sabotage nicht erkannt: holen() ohne Bündelung muss je Aufruf fragen');
}
console.log(JSON.stringify({ ok: true }));
"""


class ZielnetzliveTest(SimpleTestCase):
    databases = set()

    def test_eine_anfrage_je_zug_fuer_alle_sichten(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
