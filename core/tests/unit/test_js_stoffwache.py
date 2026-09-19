# -*- coding: utf-8 -*-
u"""`Stoffwache` (`gemeinsam/stoffwache.js`): ein toter oder stummer
Stoff-Worker gibt das Stueck an die GPU-Haeutung zurueck (19.09.2026 spaet,
Edgar: „hose animiert noch nicht").

Der Stoffschwung zeigt beim Abspielen ein Anzeigenetz mit den Punkten des
Workers und blendet die `SkinnedMesh` aus. Stirbt der Worker danach oder
antwortet er nicht mehr, blieb das Anzeigenetz mit seinen letzten Punkten
stehen — die Hose stand still, der Koerper tanzte. Ohne Three.js, in Node:

1. Ein Worker mit gemeldetem Fehler ist ausgefallen; einer, der nicht
   beschaeftigt ist, nicht; einer, der seit WARTEZEIT_MS keine Antwort gab,
   ist es — knapp darunter noch nicht.
2. `zurueck` blendet das Anzeigenetz aus, das Stueck ein, beendet den Worker
   und meldet das Stueck ab (`ausgefallen`, `bereit` false) — ein zweiter
   Aufruf ohne Worker wirft nicht.

Sabotage-Gegenprobe: `ausgefallen` ohne den `gesendet`-Vergleich -> Fall 1
rot (der stumme Worker gilt als gesund).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffwache.js')

SKRIPT = """
const { Stoffwache: W } = await import(MODUL);
// --- 1. ausgefallen ----------------------------------------------------------
pruefe('Fehler', W.ausgefallen({ fehler: 'kaputt', beschaeftigt: false }, 0), true);
pruefe('nicht beschaeftigt', W.ausgefallen({ beschaeftigt: false, gesendet: 0 }, 99999), false);
pruefe('kurz beschaeftigt', W.ausgefallen({ beschaeftigt: true, gesendet: 1000 }, 1000 + W.WARTEZEIT_MS - 1), false);
pruefe('stumm', W.ausgefallen({ beschaeftigt: true, gesendet: 1000 }, 1000 + W.WARTEZEIT_MS + 1), true);
pruefe('nie gesendet', W.ausgefallen({ beschaeftigt: true }, 99999), false);
// --- 2. zurueck --------------------------------------------------------------
let beendet = 0;
const e = { bereit: true, beschaeftigt: true, anzeige: { visible: true }, netz: { visible: false },
            worker: { terminate() { beendet++; } } };
W.zurueck(e);
pruefe('Anzeige aus', e.anzeige.visible, false);
pruefe('Netz an', e.netz.visible, true);
pruefe('Worker beendet', beendet, 1);
pruefe('Worker weg', e.worker, null);
pruefe('abgemeldet', [e.bereit, e.beschaeftigt, e.ausgefallen], [false, false, true]);
W.zurueck(e);                                   // ohne Worker: kein Fehler
pruefe('bleibt', e.ausgefallen, true);
console.log(JSON.stringify({ ok: true, beendet }));
"""


class StoffwacheTest(SimpleTestCase):
    databases = set()

    def test_wache(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True, 'beendet': 1})
