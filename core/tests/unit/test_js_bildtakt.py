# -*- coding: utf-8 -*-
"""`Bildtakt`: das Abspieltempo hängt nicht mehr an der Bildwiederholrate.

WARUM (Edgar, 13.09.2026: „die Play-Geschwindigkeit stimmt nicht, die
Normalgeschwindigkeit ist viel zu schnell, bei 0,5 ist es viel zu langsam"):
`Studioschleife.abspielen` rundete jeden Schritt einzeln —
`Math.round(dt · fps · Tempo)`. Bei 60 Hz und 30 fps sind das 0,5 Bilder je
Schritt, JavaScript rundet 0,5 auf: 60 Bilder je Sekunde, doppeltes Tempo.
Bei Tempo 0,5 ergab 0,25 → 0, der Kopf stand.

1. Eine Sekunde bei 60 Hz, Tempo 1: genau 30 Bilder; Tempo 0,5: 15; Tempo 2: 60.
2. Bei 144 Hz und 30 Hz kommt dasselbe heraus — der Rest wird mitgeführt.
3. Der Rest liegt immer in [0, 1); `zuruecksetzen()` löscht ihn.
4. Die Studioschleife rechnet über `this.takt.bilder(...)`, nicht mehr mit
   `Math.round`.

Sabotage-Gegenprobe: in `bilder` `Math.floor` → `Math.round` → Fall 1 rot
(60 statt 30 bei 60 Hz).
"""

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('studio', 'bildtakt.js')
SCHLEIFE = settings.BASE_DIR / 'static' / 'viewer' / 'studio' / 'studioschleife.js'

SKRIPT = """
const { Bildtakt } = await import(MODUL);
const gleich = (was, a, b) => {
    if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b);
};
const sekunde = (hz, fps, tempo) => {
    const takt = new Bildtakt();
    let summe = 0;
    for (let i = 0; i < hz; i++) {
        summe += takt.bilder(1 / hz, fps, tempo);
        if (takt.rest < 0 || takt.rest >= 1) throw new Error('Rest ' + takt.rest);
    }
    return summe;
};
// 1. 60 Hz
gleich('60 Hz, Tempo 1', sekunde(60, 30, 1), 30);
gleich('60 Hz, Tempo 0.5', sekunde(60, 30, 0.5), 15);
gleich('60 Hz, Tempo 2', sekunde(60, 30, 2), 60);
// 2. andere Bildwiederholraten
gleich('144 Hz, Tempo 1', sekunde(144, 30, 1), 30);
gleich('30 Hz, Tempo 1', sekunde(30, 30, 1), 30);
gleich('144 Hz, Tempo 0.5', sekunde(144, 30, 0.5), 15);
// 3. zuruecksetzen
const takt = new Bildtakt();
takt.bilder(0.02, 30, 1);
if (takt.rest <= 0) throw new Error('Rest erwartet');
takt.zuruecksetzen();
gleich('zurueckgesetzt', takt.rest, 0);
console.log(JSON.stringify({ ok: true }));
"""


class BildtaktTest(SimpleTestCase):
    def test_das_tempo_haengt_nicht_am_monitor(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_die_studioschleife_nutzt_den_takt(self):
        text = SCHLEIFE.read_text(encoding='utf-8')
        self.assertIn('this.takt.bilder(dt, state.project.fps, state.playbackSpeed)', text)
        self.assertNotIn('Math.round(dt', text)
