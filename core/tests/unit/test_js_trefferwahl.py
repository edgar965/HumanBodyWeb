# -*- coding: utf-8 -*-
u"""`Trefferwahl` (`scene/trefferwahl.js`): Haut, die durch den Stoff sticht, waehlt nicht
die Figur (24.09.2026, Edgar: „Flats löschen (GarmentCode) löscht das ganze Modell
stattdessen" — der Klick traf die Zehe, gewaehlt war die Figur, Entf loeschte sie).

1. Haut vorn, Schuh 1 cm dahinter: der Schuh.
2. Haut vorn, Schuh 5 cm dahinter (andere Koerperseite): kein Stueck, die Figur.
3. Schuh vorn: der Schuh, ohne weiter zu suchen.
4. Stoff einer ANDEREN Figur 1 cm dahinter: kein Stueck.

Sabotage: `DURCHSTICH_M` auf 0 -> Fall 1 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'trefferwahl.js')

SKRIPT = """
const { Trefferwahl: T } = await import(MODUL);
const haut = { name: 'haut', userData: { _parentCharId: 'a' } };
const schuh = { name: 'schuh', userData: { _parentCharId: 'a' } };
const fremd = { name: 'fremd', userData: { _parentCharId: 'b' } };
const ziele = [{ key: 'gc_schuh', charId: 'a', netz: schuh }, { key: 'x', charId: 'b', netz: fremd }];
const finden = (o, z) => z.find(t => t.netz === o) || null;
// Zwei Treffer: `vorn` bei 1 m, `hinten` bei 1 m + abstand; das gewaehlte Stueck oder null.
const wahl = (vorn, hinten, abstand) => T.waehlen(
    [{ object: vorn, distance: 1.0 }, { object: hinten, distance: 1.0 + abstand }], ziele, finden,
).ziel?.key ?? null;
pruefe('durchstich', wahl(haut, schuh, 0.01), 'gc_schuh');
pruefe('weit dahinter', wahl(haut, schuh, 0.05), null);
pruefe('schuh vorn', wahl(schuh, haut, 0.001), 'gc_schuh');
pruefe('fremde figur', wahl(haut, fremd, 0.01), null);
console.log(JSON.stringify({ ok: true }));
"""


class TrefferwahlTest(SimpleTestCase):
    databases = set()

    def test_durchstechende_haut_waehlt_den_stoff(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})
