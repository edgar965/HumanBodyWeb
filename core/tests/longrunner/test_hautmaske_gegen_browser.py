# -*- coding: utf-8 -*-
u"""`ModelPhysik/hautmaske.py` gegen `gemeinsam/hautmaske.js` — die
Server-Fassung der Hautmaske, Punkt für Punkt gegen die Browser-Fassung
gehalten (LongRunner: zwei Node-Läufe, rund 1 s).

Beide rechnen am selben Kunstkörper (Zylinder, Rohr) — die Python-Maske
muss der JS-Maske Punkt für Punkt gleichen: anliegendes Rohr (bis zur
Kante), lockeres Rohr (zwei Ringe frei), Stoff 30 mm entfernt (nichts),
Stoff 3 mm in der Haut (noch verdeckt). Dazu die Lagenmaske (Shirt über
Leggings). Die Python-eigenen Fälle: `core/tests/unit/test_hautmaske_python.py`.

Sabotage-Gegenprobe: `t >= -tiefe` → `t >= 0` in `_ein_stueck` macht den
Vergleich rot (3 mm in der Haut); `groesse_frei < groesste` entfernt macht
die Insel rot.
"""
import numpy as np
from django.test import SimpleTestCase
from ..unit._modelphysik import Modelphysik

from ..jsmodul import Jsmodul
from ..unit._kunstkoerper import Kunstkoerper

MODUL = Jsmodul('gemeinsam', 'hautmaske.js')
LAGEN = Jsmodul('gemeinsam', 'lagenmaske.js')


JS_ZYLINDER = """
function zylinder(radius, y0, y1, ringe, n) {
    const P = [], T = [];
    for (let r = 0; r < ringe; r++) { const y = y0 + (y1 - y0) * r / (ringe - 1);
        for (let i = 0; i < n; i++) { const w = 2 * Math.PI * i / n; P.push(radius * Math.cos(w), y, radius * Math.sin(w)); } }
    for (let r = 0; r + 1 < ringe; r++) for (let i = 0; i < n; i++) {
        const a = r * n + i, b = r * n + (i + 1) % n, c = (r + 1) * n + i, d = (r + 1) * n + (i + 1) % n;
        T.push(a, c, b, b, c, d); }
    return { punkte: Float32Array.from(P), dreiecke: Uint32Array.from(T) };
}
const koerper = zylinder(0.10, 0.0, 1.0, 51, 36);
const eng = zylinder(0.102, 0.30, 0.70, 41, 36);
const locker = zylinder(0.110, 0.30, 0.70, 41, 36);
const weit = zylinder(0.13, 0.30, 0.70, 41, 36);
const knapp = zylinder(0.097, 0.30, 0.70, 41, 36);
const als = (m) => Array.from(m).join('');
"""

SKRIPT_HAUT = JS_ZYLINDER + """
const { Hautmaske } = await import(MODUL);
console.log(JSON.stringify({
    eng: als(Hautmaske.verdeckt(koerper.punkte, koerper.dreiecke, [eng])),
    locker: als(Hautmaske.verdeckt(koerper.punkte, koerper.dreiecke, [locker])),
    weit: als(Hautmaske.verdeckt(koerper.punkte, koerper.dreiecke, [weit])),
    knapp: als(Hautmaske.verdeckt(koerper.punkte, koerper.dreiecke, [knapp])),
}));
"""

SKRIPT_LAGEN = JS_ZYLINDER + """
const { Lagenmaske } = await import(MODUL);
const leggings = { schluessel: 'hose', ...zylinder(0.102, 0.10, 0.70, 61, 36) };
const shirt = { schluessel: 'shirt', ...zylinder(0.115, 0.50, 0.90, 41, 36) };
const e = Lagenmaske.verdeckt(koerper, [leggings, shirt]);
console.log(JSON.stringify({ hose: als(e.get('hose').maske), shirt: als(e.get('shirt').maske), ueber: e.get('hose').ueber }));
"""


class HautmaskeGegenBrowserTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.hm = HautmaskeGegenBrowserTest._hautmaske_modul()
        self.koerper = Kunstkoerper.zylinder(0.10, 0.0, 1.0, 51, 36)

    def _maske(self, stoff, **optionen):
        P, T = self.koerper
        return self.hm.Hautmaske.verdeckt(P, T, [stoff], **optionen)

    def test_python_gleicht_der_browserfassung(self):
        js = MODUL.laufen(SKRIPT_HAUT)
        faelle = {
            'eng': Kunstkoerper.zylinder(0.102, 0.30, 0.70, 41, 36),
            'locker': Kunstkoerper.zylinder(0.110, 0.30, 0.70, 41, 36),
            'weit': Kunstkoerper.zylinder(0.13, 0.30, 0.70, 41, 36),
            'knapp': Kunstkoerper.zylinder(0.097, 0.30, 0.70, 41, 36),
        }
        # Die Punkte GENAU auf der Rohrkante (y = 0,30 / 0,70) trifft der
        # Strahl auf der Dreieckskante — ein Gleitkomma-Gleichstand, den
        # beide Fassungen verschieden entscheiden duerfen.
        y = self.koerper[0][:, 1]
        kante = (np.abs(y - 0.30) < 1e-6) | (np.abs(y - 0.70) < 1e-6)
        for name, stoff in faelle.items():
            py = ''.join('1' if v else '0' for v in self._maske(stoff))
            unterschiede = sum(a != b for k, (a, b) in enumerate(zip(py, js[name]))
                               if not kante[k])
            self.assertEqual(unterschiede, 0,
                             '%s: %d von %d Punkten anders' % (name, unterschiede, len(py)))
        self.assertGreater(js['eng'].count('1'), 500)
        self.assertEqual(js['weit'].count('1'), 0)
        self.assertGreater(js['knapp'].count('1'), 300)

    def test_lagenmaske_gleicht_der_browserfassung(self):
        js = LAGEN.laufen(SKRIPT_LAGEN)
        P, T = self.koerper
        hose = Kunstkoerper.zylinder(0.102, 0.10, 0.70, 61, 36)
        shirt = Kunstkoerper.zylinder(0.115, 0.50, 0.90, 41, 36)
        # Seit dem 12.09.2026 eine eigene Datei (`lagenmaske.py`).
        Lagenmaske = Modelphysik.modul('lagenmaske').Lagenmaske
        aus = Lagenmaske.verdeckt(P, T, [('hose', hose[0], hose[1]),
                                         ('shirt', shirt[0], shirt[1])])
        self.assertEqual(aus['hose'][1], ['shirt'])
        self.assertEqual(js['ueber'], ['shirt'])
        py = ''.join('1' if v else '0' for v in aus['hose'][0])
        self.assertEqual(sum(a != b for a, b in zip(py, js['hose'])), 0)
        self.assertEqual(int(aus['shirt'][0].sum()), 0)
        self.assertGreater(int(aus['hose'][0].sum()), 300)

    @staticmethod
    def _hautmaske_modul():
        return Modelphysik.modul('hautmaske')
