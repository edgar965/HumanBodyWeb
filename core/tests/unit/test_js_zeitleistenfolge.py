# -*- coding: utf-8 -*-
"""`Zeitleistenfolge`: die Zeitleiste blättert beim Abspielen mit dem Kopf.

WARUM (Edgar, 13.09.2026: „bei Play soll die Zeitleiste die Timeline
mitziehen, im Moment ist der Playhead außerhalb des sichtbaren Bereichs"):
`timelineScrollX` änderte sich nur über Rad und Ziehen; nach 13 s (100 px/s,
1.300 px Sichtbreite) lief der Kopf rechts hinaus, und die Leiste blieb am
Anfang.

1. Sichtbarer Kopf: keine Verschiebung (die Leiste steht, Klips bleiben
   anfassbar). Am rechten Rand (x == sichtbar) wird geblättert, der Kopf
   steht danach `RAND` Pixel vom linken Rand.
2. Kopf links außerhalb (Sprung auf 0 bei „Endlos", Rückwärts): ebenfalls
   geblättert, nie unter 0.
3. `nachziehen` rechnet den Kopf aus Bild, fps und Zoom und schreibt
   `timelineScrollX`; Sichtbreite 0 (Leinwand noch nicht da) tut nichts.
4. Die Studioschleife ruft `nachziehen` im Abspielschritt VOR
   `renderTimeline()` — sonst zeichnet sie noch den alten Ausschnitt.

Sabotage-Gegenprobe: in `verschiebung` `x < sichtbar` → `x <= sichtbar`
→ Fall 1 rot; Aufruf in `studioschleife.js` hinter `renderTimeline()` →
Fall 4 rot.
"""

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('studio', 'zeitleiste_folgen.js')
SCHLEIFE = settings.BASE_DIR / 'static' / 'viewer' / 'studio' / 'studioschleife.js'

SKRIPT = """
const { Zeitleistenfolge: Z } = await import(MODUL);
const gleich = (was, a, b) => {
    if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b);
};
// 1. sichtbar → null; am rechten Rand → Kopf RAND Pixel vom linken Rand
gleich('mitten drin', Z.verschiebung(500, 0, 1300), null);
gleich('kurz vor dem Rand', Z.verschiebung(1299, 0, 1300), null);
gleich('am Rand', Z.verschiebung(1300, 0, 1300), 1300 - Z.RAND);
gleich('weit dahinter', Z.verschiebung(5000, 1276, 1300), 5000 - Z.RAND);
gleich('nach dem Blaettern', Z.verschiebung(1300, 1300 - Z.RAND, 1300), null);
// 2. links ausserhalb, nie unter 0
gleich('links raus', Z.verschiebung(100, 2000, 1300), 100 - Z.RAND);
gleich('Sprung auf 0', Z.verschiebung(0, 2000, 1300), 0);
gleich('nahe 0 nicht negativ', Z.verschiebung(5, 2000, 1300), 0);
// 3. nachziehen aus Bild/fps/Zoom; Sichtbreite 0 tut nichts
const z = { playheadFrame: 900, project: { fps: 30 }, timelineZoom: 100,
            timelineScrollX: 0 };
gleich('geblaettert', Z.nachziehen(z, 1300), true);
gleich('scrollX', z.timelineScrollX, 3000 - Z.RAND);
gleich('danach ruhig', Z.nachziehen(z, 1300), false);
gleich('scrollX bleibt', z.timelineScrollX, 3000 - Z.RAND);
const leer = { playheadFrame: 900, project: { fps: 30 }, timelineZoom: 100,
               timelineScrollX: 7 };
gleich('ohne Leinwand', Z.nachziehen(leer, 0), false);
gleich('ohne Leinwand unveraendert', leer.timelineScrollX, 7);
console.log(JSON.stringify({ ok: true }));
"""


class ZeitleistenfolgeTest(SimpleTestCase):
    def test_die_leiste_blaettert_mit_dem_kopf(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_die_studioschleife_zieht_vor_dem_zeichnen_nach(self):
        text = SCHLEIFE.read_text(encoding='utf-8')
        rumpf = text[text.index('abspielen(dt) {') : text.index('kameraspurAktiv() {')]
        aufruf = rumpf.index('Zeitleistenfolge.nachziehen(state, Zeitleistenflaeche.breite - HEADER_WIDTH);')
        self.assertLess(aufruf, rumpf.index('renderTimeline();'))
