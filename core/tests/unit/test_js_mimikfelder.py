# -*- coding: utf-8 -*-
"""Mimik auf SMPL-X: `Mimikfelder` (Node) und die Verdrahtung im Studio.

WARUM (Edgar, 16.09.2026: „Mimik auch auf SMPL-X"): Eine SMPL-X-Figur hat
keine DEF-Gesichtsknochen; dieselben Gewichte auf den MB-Lab-Einheiten gehen
dort als Verschiebung der Kopfpunkte (`smplx_basis.json`). Hier ohne Netz und
ohne Browser:

1. `Mimikfelder.summe`: positive Gewichte nehmen `plus`, negative `minus`,
   der Betrag skaliert, Felder addieren sich je Punkt.
2. `Mimikfelder.anwenden`: schreibt `ruhe + summe` und stellt Punkte, die
   beim letzten Mal bewegt waren, zurück in die Ruhe — nichts bleibt hängen.
3. `kennung`: gleiche Gewichte, gleiche Kennung; Nullgewichte zählen nicht.
4. Verdrahtung: `Mimikanwendung.anwenden` wählt Netz (SMPL-X) oder Knochen,
   der Dialog geht über `anwenden`, der Hilfetext nennt SMPL-X, der Befehl
   schreibt `smplx_basis.json`, die Datei liegt versioniert unter `static/mimik/`.

Sabotage-Gegenprobe: in `anwenden` die Rückstellung der alten Punkte
entfernen → Fall 2 rot (Punkt 5 bleibt verschoben).
"""

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'mimikfelder.js')
STUDIO = Jsmodul.VIEWER / 'bvh_studio'

SKRIPT = """
const { Mimikfelder: M } = await import(MODUL);
const gleich = (was, a, b) => { if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b); };
const nah = (was, a, b) => { if (Math.abs(a - b) > 1e-6) throw new Error(was + ': ' + a + ' statt ' + b); };
const basis = {
    mouthSmile: { plus: { i: [1, 2], d: [0.01, 0.02, 0, 0, 0.01, 0] },
                  minus: { i: [1], d: [-0.01, 0, 0] } },
    eyeClosedL: { plus: { i: [5], d: [0, -0.008, 0] }, minus: { i: [], d: [] } },
};
// 1. Summe
let s = M.summe(basis, { mouthSmile: 0.5, eyeClosedL: 1 });
gleich('Punkte', s.size, 3);
nah('Punkt 1 dx', s.get(1)[0], 0.005); nah('Punkt 1 dy', s.get(1)[1], 0.01);
nah('Punkt 2 dy', s.get(2)[1], 0.005); nah('Punkt 5 dy', s.get(5)[1], -0.008);
s = M.summe(basis, { mouthSmile: -1 });
gleich('minus', s.size, 1); nah('minus dx', s.get(1)[0], -0.01);
gleich('null', M.summe(basis, { mouthSmile: 0, quatsch: 1 }).size, 0);
// 2. Anwenden und Zurückstellen
const ruhe = new Float32Array(18).fill(1);
const lage = Float32Array.from(ruhe);
let bewegt = M.anwenden(lage, ruhe, M.summe(basis, { eyeClosedL: 1 }), new Set());
nah('Punkt 5 verschoben', lage[16], 1 - 0.008);
gleich('bewegt', bewegt.size, 1);
bewegt = M.anwenden(lage, ruhe, M.summe(basis, { mouthSmile: 1 }), bewegt);
nah('Punkt 5 zurück', lage[16], 1);
nah('Punkt 1 dx', lage[3], 1.01);
bewegt = M.anwenden(lage, ruhe, new Map(), bewegt);
if (lage.some((w, i) => Math.abs(w - ruhe[i]) > 1e-9)) throw new Error('nicht alles in Ruhe');
gleich('nichts bewegt', bewegt.size, 0);
// 3. Kennung
gleich('kennung gleich', M.kennung({ a: 0.5, b: 1 }), M.kennung({ b: 1, a: 0.5, c: 0 }));
if (M.kennung({ a: 0.5 }) === M.kennung({ a: 0.6 })) throw new Error('Kennung unterscheidet nicht');
gleich('leer', M.kennung({}), '');
console.log(JSON.stringify({ ok: true }));
"""


class MimikfelderTest(SimpleTestCase):
    def test_summe_anwenden_kennung(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_verdrahtung_im_studio(self):
        anwendung = MimikfelderTest._text(STUDIO / 'mimikanwendung.js')
        self.assertIn('static anwenden(modellIdx, gewichte, ganz = true, visemes = null)', anwendung)
        self.assertIn(
            'if (Mimiksmplx.passt(figur)) { Mimiksmplx.setzen(figur.mesh, gewichte); return; }', anwendung
        )
        self.assertIn('Mimikanwendung.anwenden(i, stand.gewichte, stand.mimik, stand.visemes);', anwendung)
        self.assertIn(
            'Mimikanwendung.anwenden(spur._modellIdx, spur._vorschau || {});',
            MimikfelderTest._text(STUDIO / 'mimikdialog.js'),
        )
        smplx = MimikfelderTest._text(STUDIO / 'mimiksmplx.js')
        self.assertIn("figur?.quelle === 'smpl'", smplx)
        self.assertIn('Mimiksmplx._normalen(netz.geometry, stand);', smplx)
        self.assertIn('SMPL-X', MimikfelderTest._text(STUDIO / 'hilfetexte_spuren.js'))
        befehl = MimikfelderTest._text(
            settings.BASE_DIR / 'core' / 'management' / 'commands' / 'mimik_vorbereiten.py'
        )
        self.assertIn('Mimiksmplx.schreiben(ausdruecke.einheiten(), daten, ziel)', befehl)
        datei = settings.BASE_DIR / 'static' / 'mimik' / 'smplx_basis.json'
        self.assertTrue(datei.is_file())

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding='utf-8')
