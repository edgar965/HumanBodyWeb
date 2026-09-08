# -*- coding: utf-8 -*-
u"""`Laufwache`: wer den GarmentCode-Reiter besetzt, und wann er ihn freigibt.

WARUM (08.09.2026, Edgar: „Kleid erzeugen funktioniert gerade nicht (nach
T-Shirt Erzeugung)"): Die Wache war eine einzige stumme Zeile —
`if (reiter.laeuft) return;`. Kein Text, keine Anfrage, nichts. Im Serverlog
war der Befund eindeutig: Nach dem Wechsel auf das Kleid kam KEIN einziger
`/api/garmentcode/erzeugen/` mehr an, der Klick hat den Ablauf nie erreicht.

Dass `laeuft` haengen bleiben KANN, ist belegt: `Serverabruf.formular` sitzt
auf `fetch` ohne Frist (nachgesehen in djangoBase). Eine Antwort, die nie
kommt — Serverneustart mitten im Lauf, wie am 07.09.2026 um 18:57 — laesst das
`await` fuer immer stehen, und danach sind alle drei Knoepfe dauerhaft tot.

Geprueft wird:

1. Frei heisst frei — die Wache haelt niemanden ohne Grund auf.
2. Ein laufender Bau wird gemeldet, MIT seiner Dauer. Ohne die Dauer ist
   „besetzt" nicht von „haengt" zu unterscheiden.
3. Nach `FRIST_S` gilt ein Lauf als verloren und der naechste Klick uebernimmt.
   Das ist der Ausweg aus dem toten Knopf.
4. Die Laufnummer schuetzt den neuen Lauf: Ein verloren geglaubter Lauf, der
   doch noch zurueckkommt, gibt die Knoepfe NICHT frei und meldet nichts mehr.
   Ohne diese Probe waere die Frist eine neue Fehlerquelle statt einer
   Reparatur.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'laufwache.js')

SKRIPT = """
const { Laufwache: W } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const T0 = 1000000;
const S = (n) => n * 1000;

// --- 1. Ein freier Reiter laesst jeden durch ------------------------------
pruefe('frisches Objekt', W.pruefen({}, T0).darf, true);
pruefe('ausdruecklich frei', W.pruefen({laeuft: false}, T0).darf, true);
pruefe('Grund frei', W.pruefen({}, T0).grund, 'frei');

// --- 2. Ein laufender Bau wird gemeldet, mit Dauer ------------------------
const z = {};
const lauf1 = W.beginnen(z, T0);
pruefe('erste Laufnummer', lauf1, 1);
pruefe('besetzt', z.laeuft, true);
const nach30 = W.pruefen(z, T0 + S(30));
pruefe('darf nicht', nach30.darf, false);
pruefe('Grund besetzt', nach30.grund, 'besetzt');
pruefe('seit 30 s', nach30.seit, 30);

// --- 3. Nach der Frist gilt er als verloren -------------------------------
const knapp = W.pruefen(z, T0 + S(W.FRIST_S - 1));
pruefe('kurz vor der Frist noch besetzt', knapp.darf, false);
const drueber = W.pruefen(z, T0 + S(W.FRIST_S + 5));
pruefe('nach der Frist frei', drueber.darf, true);
pruefe('Grund verloren', drueber.grund, 'verloren');
pruefe('Dauer im Grund', drueber.seit, W.FRIST_S + 5);

// --- 4. Die Laufnummer schuetzt den neuen Lauf ----------------------------
// Der verlorene Lauf laeuft weiter; ein neuer uebernimmt.
const lauf2 = W.beginnen(z, T0 + S(W.FRIST_S + 5));
pruefe('zweite Laufnummer', lauf2, 2);
// Jetzt meldet sich der ALTE Lauf doch noch zurueck:
pruefe('alter Lauf gibt nicht frei', W.beenden(z, lauf1), false);
pruefe('Reiter bleibt besetzt', z.laeuft, true);
pruefe('alter Lauf darf nicht melden', W.aktuell(z, lauf1), false);
pruefe('neuer Lauf darf melden', W.aktuell(z, lauf2), true);
// Und der neue gibt korrekt frei:
pruefe('neuer Lauf gibt frei', W.beenden(z, lauf2), true);
pruefe('danach frei', z.laeuft, false);
pruefe('Zeitstempel zurueckgesetzt', z.laeuftSeit, 0);
pruefe('danach darf wieder', W.pruefen(z, T0 + S(400)).darf, true);

// --- 5. Gegenprobe: ohne Zustand faellt nichts um -------------------------
pruefe('kein Zustand', W.pruefen(null, T0).darf, true);
pruefe('beenden ohne Zustand', W.beenden(null, 1), false);
pruefe('aktuell ohne Zustand', W.aktuell(null, 1), false);

console.log(JSON.stringify({ok: true}));
"""


class LaufwacheTest(SimpleTestCase):
    u"""Ein besetzter Reiter sagt es — und gibt sich irgendwann selbst frei."""

    databases = []

    def test_laufwache(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
