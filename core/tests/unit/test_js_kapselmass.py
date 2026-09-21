# -*- coding: utf-8 -*-
u"""`Kapselmass` (`gemeinsam/kapselmass.js`), `Stoffkoerper` und die konische,
elliptische Kapsel im `Stoffpendel` (19.09.2026, Edgar: „Hose (genesis) animiert nicht").

Gemessen an Ursula in Daz' Idle: Ohne Kapseln folgte die Angie-Jeans der
gehaeuteten Lage auf 5,6 mm (max 33), mit den alten Kapseln (EIN Radius je
Knochen, 85. Perzentil, Achse zum ersten Kind) 36 mm (max 120) — sie
bluehte 12–19 cm auf. Hier die Regel:
1. Radius je Ende: ein Schenkel, der am Kopf 12 cm und am Kind 6 cm dick
   ist, bekommt 12 und 6 — je Haelfte ein Perzentil, nicht ein Wert fuer beide;
   `ellipse` findet dazu die Hauptachsen (30 Grad gedreht) und je Achse den Radius.
2. Eine Haelfte ohne Punkte nimmt den Radius der anderen (Zylinder, kein
   Kegel auf null).
3. Der Stoffpendel drueckt an einer konischen Kapsel je nach Anteil auf der
   Achse hinaus: am dicken Ende weiter als am duennen. `r` allein gilt
   weiter fuer beide Enden (die alte Form).

Sabotage-Gegenprobe: in `_kapseln` `r = ra` statt `ra + (rb - ra) * t` ->
Fall 3 rot (am duennen Ende steht der Punkt zu weit draussen).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MASS = Jsmodul('gemeinsam', 'kapselmass.js')
PENDEL = Jsmodul('gemeinsam', 'stoffpendel.js')

SKRIPT_MASS = """
const { Kapselmass: K } = await import(MODUL);
// 1. Kopfhaelfte um 0,12 (0,10..0,14), Kindhaelfte um 0,06 (0,04..0,08)
const d = [], t = [];
for (let i = 0; i < 50; i++) { d.push(0.10 + 0.04 * i / 49); t.push(0.1 + 0.3 * i / 49); }
for (let i = 0; i < 50; i++) { d.push(0.04 + 0.04 * i / 49); t.push(0.6 + 0.3 * i / 49); }
const [ra, rb] = K.endradien(d, t, 0.5);
if (Math.abs(ra - 0.12) > 0.006 || Math.abs(rb - 0.06) > 0.006) throw new Error('Enden: ' + ra + ' ' + rb);
// 2. nur Kopfpunkte: beide Enden gleich
const [ca, cb] = K.endradien(d.slice(0, 50), t.slice(0, 50), 0.5);
if (ca !== cb || Math.abs(ca - 0.12) > 0.006) throw new Error('Zylinder: ' + ca + ' ' + cb);
// leer: 0
const [la, lb] = K.endradien([], []);
if (la !== 0 || lb !== 0) throw new Error('leer');
// 3. Ellipse: Punkte auf einer um 30 Grad gedrehten Ellipse, Halbachsen 0,12 / 0,06
//    am Kopf, 0,08 / 0,04 am Kind — Hauptachse und Radien je Ende wiederfinden.
const x1 = [], x2 = [], at = [];
const w = Math.PI / 6;
for (let h = 0; h < 2; h++) for (let i = 0; i < 360; i += 3) {
    const phi = i * Math.PI / 180, A = h ? 0.08 : 0.12, B = h ? 0.04 : 0.06;
    const px = A * Math.cos(phi), py = B * Math.sin(phi);
    x1.push(px * Math.cos(w) - py * Math.sin(w)); x2.push(px * Math.sin(w) + py * Math.cos(w)); at.push(h ? 0.8 : 0.2);
}
const m = K.ellipse(x1, x2, at);
const winkel = Math.abs(((m.theta - w) % Math.PI + Math.PI) % Math.PI);
if (Math.min(winkel, Math.PI - winkel) > 0.02) throw new Error('Hauptachse: ' + m.theta);
if (Math.abs(m.rua - 0.12) > 0.004 || Math.abs(m.rwa - 0.06) > 0.004) throw new Error('Kopf: ' + m.rua + ' ' + m.rwa);
if (Math.abs(m.rub - 0.08) > 0.004 || Math.abs(m.rwb - 0.04) > 0.004) throw new Error('Kind: ' + m.rub + ' ' + m.rwb);
console.log(JSON.stringify({ ok: true, ra: +ra.toFixed(3), rb: +rb.toFixed(3), rua: +m.rua.toFixed(3), rwa: +m.rwa.toFixed(3) }));
"""

SKRIPT_PENDEL = """
const { Stoffpendel: S } = await import(MODUL);
// Eine Reihe freier Punkte entlang y = 0,7 auf der Achse einer Kapsel, die
// von x = 0 (Radius 0,10) nach x = 1 (Radius 0,02) laeuft; die Punkte liegen
// 1 mm ueber der Achse (z = 0,001), also in der Kapsel.
const n = 11, ruhe = [], frei = [];
for (let i = 0; i < n; i++) { ruhe.push(i / 10, 0.7, 0.001); frei.push(1); }
const paare = [];
for (let i = 0; i + 1 < n; i++) paare.push(i, i + 1);
const ohne = Object.assign(Object.create(S), { SCHWERE: 0, FEDER_FREI: 0, FEDER_HAFT: 0, DURCHGAENGE: 0 });
const p = S.ausKanten(Float32Array.from(ruhe), paare, Float32Array.from(frei));
const ziel = Float32Array.from(ruhe);
const kegel = [{ a: [0, 0.7, 0], b: [1, 0.7, 0], ra: 0.10, rb: 0.02 }];
p.schritt(ziel, 1 / 30, kegel, ohne);
const abstand = (i) => Math.hypot(p.x[3 * i + 1] - 0.7, p.x[3 * i + 2]);
const dick = abstand(0), mitte = abstand(5), duenn = abstand(10);
if (Math.abs(dick - (0.10 + S.ABSTAND)) > 1e-4) throw new Error('dickes Ende: ' + dick);
if (Math.abs(mitte - (0.06 + S.ABSTAND)) > 1e-4) throw new Error('Mitte: ' + mitte);
if (Math.abs(duenn - (0.02 + S.ABSTAND)) > 1e-4) throw new Error('duennes Ende: ' + duenn);
// alte Form: `r` fuer beide Enden
const q = S.ausKanten(Float32Array.from(ruhe), paare, Float32Array.from(frei));
q.schritt(ziel, 1 / 30, [{ a: [0, 0.7, 0], b: [1, 0.7, 0], r: 0.05 }], ohne);
const alt = Math.hypot(q.x[3 * 10 + 1] - 0.7, q.x[3 * 10 + 2]);
if (Math.abs(alt - (0.05 + S.ABSTAND)) > 1e-4) throw new Error('alte Form: ' + alt);
// elliptisch: u = z (Radius 0,10), w = d x u = x x z = -y (Radius 0,04) — ein Punkt
// 1 mm ueber der Achse in y landet auf 0,04 + ABSTAND, einer in z auf 0,10 + ABSTAND.
const r2 = [], f2 = [];
r2.push(0.5, 0.701, 0, 0.5, 0.7, 0.001); f2.push(1, 1);
const e = S.ausKanten(Float32Array.from(r2), [0, 1], Float32Array.from(f2));
e.schritt(Float32Array.from(r2), 1 / 30, [{ a: [0, 0.7, 0], b: [1, 0.7, 0], u: [0, 0, 1], rua: 0.10, rwa: 0.04, rub: 0.10, rwb: 0.04 }],
          Object.assign(Object.create(ohne), { DURCHGAENGE: 0 }));
const inY = Math.abs(e.x[1] - 0.7), inZ = Math.abs(e.x[5]);
if (Math.abs(inY - (0.04 + S.ABSTAND)) > 1e-4) throw new Error('Ellipse w: ' + inY);
if (Math.abs(inZ - (0.10 + S.ABSTAND)) > 1e-4) throw new Error('Ellipse u: ' + inZ);
console.log(JSON.stringify({ ok: true, dick_cm: +(dick * 100).toFixed(2), duenn_cm: +(duenn * 100).toFixed(2),
                             ellipse_w_cm: +(inY * 100).toFixed(2), ellipse_u_cm: +(inZ * 100).toFixed(2) }));
"""


class KapselmassTest(SimpleTestCase):

    databases = set()

    def test_radius_je_ende_median(self):
        ausgabe = MASS.laufen(SKRIPT_MASS)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe['ra'], ausgabe['rb'])

    def test_konische_kapsel_im_pendel(self):
        ausgabe = PENDEL.laufen(SKRIPT_PENDEL)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertGreater(ausgabe['dick_cm'], ausgabe['duenn_cm'])
        self.assertGreater(ausgabe['ellipse_u_cm'], ausgabe['ellipse_w_cm'])

    def test_die_kapseln_der_szene_sind_konisch(self):
        from django.conf import settings
        statik = settings.BASE_DIR / 'static' / 'viewer'
        kapseln = (statik / 'gemeinsam' / 'stoffkapseln.js').read_text(encoding='utf-8')
        self.assertIn('Kapselmass.ellipse(x1, x2, anteile)', kapseln)
        self.assertIn('Stoffkapseln.mittel(kinder, b, q)', kapseln)
        self.assertIn('new Float32Array(kapseln.length * je)', kapseln)
        self.assertIn('u.applyQuaternion(bone.getWorldQuaternion(new THREE.Quaternion()).invert())', kapseln)
        arbeiter = (statik / 'gemeinsam' / 'stoffarbeiter.js').read_text(encoding='utf-8')
        self.assertIn('Stoffkoerper.lesen(d.kapseln)', arbeiter)
