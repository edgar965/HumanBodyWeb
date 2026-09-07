# -*- coding: utf-8 -*-
u"""`Fortschrittsrechnung`: was der Balken beim Kleidungsbau anzeigt.

WARUM (06.09.2026, Edgar: „mach einen Fortschrittsbalken"): Echten Fortschritt
meldet der Server nicht — die Simulation läuft in einem eigenen Prozess und
schweigt bis zum Ende. Der Balken schätzt also, und eine Schätzung, die niemand
nachprüft, ist eine Behauptung. Geprüft wird:

1. Der Balken läuft nie voll, solange ein Schritt läuft. Ein Balken, der bei
   100 % steht und trotzdem weiterrechnet, sagt genau das Falsche.
2. Er steht nie still: Auch beim Vierfachen der erwarteten Dauer wächst er
   weiter — sonst liest sich ein langer Lauf wie ein Absturz.
3. Er springt nicht zurück, wenn ein Schritt scheitert.
4. Die Schritte sind nach ihrer Dauer GEWICHTET. Ohne das wäre der Schnitt
   (4 s) so breit wie die Drapierung (22 s), und der Balken spränge sofort auf
   ein Drittel, um dann eine halbe Minute zu stehen.
5. Die Restzeit kommt aus den erwarteten Dauern, nicht aus dem Balkenstand —
   die Kurve ist asymptotisch, zurückgerechnet ergäbe sie Unsinn.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'fortschrittsrechnung.js')

SKRIPT = """
const { Fortschrittsrechnung: F } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const proz = (x) => Math.round(x * 100);

// --- 1. Ein laufender Schritt wird nie voll --------------------------------
if (F.anteil(0, 20) !== 0) throw new Error('Beginn ist nicht 0');
for (const t of [1, 20, 100, 10000]) {
    const a = F.anteil(t, 20);
    if (a >= 1) throw new Error('anteil(' + t + ') erreicht 1');
    if (a > F.DECKEL) throw new Error('anteil(' + t + ') ueber dem Deckel');
}

// --- 2. Und er steht nie still ---------------------------------------------
let vorher = -1;
for (const t of [5, 10, 20, 40, 80]) {
    const a = F.anteil(t, 20);
    if (a <= vorher) throw new Error('anteil waechst bei t=' + t + ' nicht mehr');
    vorher = a;
}
// Bei der erwarteten Dauer rund 80 % — die Kurve aus dem Modulkopf.
pruefe('bei erwarteter Dauer', proz(F.anteil(20, 20)), 80);

// --- 3. Gescheitert springt nicht zurueck ----------------------------------
const gescheitert = [{stand: 'fertig', erwartet: 4},
                     {stand: 'fehler', erwartet: 22}];
pruefe('alles abgeschlossen', proz(F.gesamt(gescheitert)), 100);

// --- 4. Gewichtung nach Dauer ----------------------------------------------
const schritte = [{stand: 'fertig', erwartet: 4},
                  {stand: 'wartet', erwartet: 22},
                  {stand: 'wartet', erwartet: 4}];
// 4 von 30 Sekunden erledigt — nicht ein Drittel, weil ein Schritt von drei.
pruefe('gewichtet', proz(F.gesamt(schritte)), 13);
const gleich = [{stand: 'fertig', erwartet: 10}, {stand: 'wartet', erwartet: 10}];
pruefe('gleiche Gewichte', proz(F.gesamt(gleich)), 50);
pruefe('leere Liste', F.gesamt([]), 0);
pruefe('kein Feld', F.gesamt(null), 0);

// --- 5. Restzeit -----------------------------------------------------------
pruefe('Rest offener Schritte', F.rest(schritte), 26);
pruefe('laufender zaehlt anteilig',
       F.rest([{stand: 'laeuft', erwartet: 20, verstrichen: 8}]), 12);
// Ueberzogen heisst 0, nie negativ — „noch -14 s" waere Unsinn.
pruefe('nie negativ',
       F.rest([{stand: 'laeuft', erwartet: 20, verstrichen: 34}]), 0);
pruefe('nichts mehr offen', F.rest([{stand: 'fertig', erwartet: 4}]), null);

// --- 6. Zeitangabe ---------------------------------------------------------
pruefe('unter einer Minute', F.zeit(43), '43 s');
pruefe('Minute', F.zeit(60), '1:00');
pruefe('mit Sekunden', F.zeit(95), '1:35');
pruefe('unbrauchbar wird 0', F.zeit(NaN), '0 s');

console.log(JSON.stringify({ok: true}));
"""


class FortschrittsrechnungTest(SimpleTestCase):
    u"""Der Balken schätzt — hier steht, was die Schätzung zusagt."""

    databases = []

    def test_fortschrittsrechnung(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
