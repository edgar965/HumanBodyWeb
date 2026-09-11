# -*- coding: utf-8 -*-
u"""`Bereichsgriff`: die Breite, die aus einem Mausweg wird.

WARUM (11.09.2026, Edgar: „möchte den rechten Bereich verschieben können,
die Griffe fehlen"): Der Griff der Szene-Seite kannte nur ein Feld LINKS im
Fenster (Breite wächst mit der Maus nach rechts). Die rechte Leiste des
Theatre wächst nach LINKS — dasselbe Ziehen, umgekehrtes Vorzeichen. Geprüft
wird genau diese Entscheidung, ohne DOM:

1. Feld links: Maus nach rechts = breiter.
2. Feld rechts: Maus nach links = breiter.
3. Grenzen halten, in beide Richtungen.
4. Kaputte Werte ergeben `min`, nie NaN — eine Breite von NaN lässt das Feld
   verschwinden, ohne einen Fehler zu werfen.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'bereichsgriff.js')

SKRIPT = """
const { Bereichsgriff } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const B = Bereichsgriff.naechsteBreite;

// 1. Feld links (Richtung +1): 120 px nach rechts gezogen
pruefe('links breiter', B(300, 120, 1, 200, 600), 420);
pruefe('links schmaler', B(300, -50, 1, 200, 600), 250);
// 2. Feld rechts (Richtung -1): 120 px nach LINKS gezogen = breiter
pruefe('rechts breiter', B(300, -120, -1, 240, 720), 420);
pruefe('rechts schmaler', B(300, 40, -1, 240, 720), 260);
// 3. Grenzen
pruefe('max', B(300, 1000, 1, 200, 600), 600);
pruefe('min', B(300, -1000, 1, 200, 600), 200);
pruefe('min rechts', B(300, 1000, -1, 240, 720), 240);
// 4. Kaputte Werte
pruefe('NaN', Bereichsgriff.begrenzen(NaN, 200, 600), 200);
pruefe('Text', Bereichsgriff.begrenzen('abc', 200, 600), 200);
pruefe('Rundung', Bereichsgriff.begrenzen(333.7, 200, 600), 334);
pruefe('Text-Zahl', Bereichsgriff.begrenzen('420', 200, 600), 420);
console.log(JSON.stringify({ok: true}));
"""


class BereichsgriffTest(SimpleTestCase):

    databases = []

    def test_breite_aus_mausweg(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
