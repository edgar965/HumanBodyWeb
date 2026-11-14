# -*- coding: utf-8 -*-
"""Glättung je Bild (`Stoffglaettung`, 12.11.2026) an einem Kunststreifen in Node.

Edgar, 12.11.2026: „mach“ zu „Daz glättet den Stoff an solchen Stellen in jedem Bild nach“ (Riss der Jeans im Schritt, Olesia1, Spagat).

Ein Streifen 21 × 5 Punkte (1 cm Raster) mit Einheitsmatrix als Unterteilung (Browserpunkte = Käfigpunkte) und Außennormale +z:

1. Reine Drehung um eine Achse: keine Zone, kein Versatz.
2. Die rechte Hälfte rückt um 6 cm nach rechts und 3 cm nach oben (die Kanten in der Mitte reißen auf): Zone > 0, die größte Kantendehnung des Geglätteten liegt
   unter der des Gehäuteten, kein Versatz über `VERSATZ_M`, kein Punkt unter seiner gehäuteten Lage entlang der Normale (Kollision).
3. Danach wieder ein Bild ohne Riss: jeder Versatz ist null (nichts bleibt vom vorigen Bild stehen).

Sabotage: in `bild` die Zeile `if (s < 0) { x[o] -= … }` entfernen → Fall 2 rot („nie unter die gehäutete Lage“); `this._leeren()` im Zweig
ohne Risse streichen → Fall 3 rot.

Geschrieben am 12.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STREIFEN = """
const { Stoffglaettung } = await import(MODUL);
const B = 21, H = 5, n = B * H, ruhe = new Float32Array(3 * n), normalen = new Float32Array(3 * n), kanten = [];
for (let j = 0; j < H; j++) for (let i = 0; i < B; i++) {
    const p = j * B + i; ruhe.set([0.01 * i, 0.01 * j, 0], 3 * p); normalen.set([0, 0, 1], 3 * p);
    if (i + 1 < B) kanten.push(p, p + 1);
    if (j + 1 < H) kanten.push(p, p + B);
}
const indptr = new Uint32Array(n + 1), indices = new Uint32Array(n), data = new Float32Array(n).fill(1);
for (let p = 0; p < n; p++) { indptr[p + 1] = p + 1; indices[p] = p; }
const g = new Stoffglaettung(ruhe, Uint32Array.from(kanten), { indptr, indices, data, zeilen: n }, normalen);
const groesste = (lage) => { let m = 0; for (let e = 0; e < g.a.length; e++) { const i = 3 * g.a[e], j = 3 * g.b[e];
    m = Math.max(m, Math.hypot(lage[i] - lage[j], lage[i + 1] - lage[j + 1], lage[i + 2] - lage[j + 2]) / g.l[e]); } return m; };
"""

DREHUNG = STREIFEN + """
const c = Math.cos(0.7), s = Math.sin(0.7);
const r = g.bild((i, x, y, z, aus) => { aus[0] = c * x - s * y; aus[1] = s * x + c * y; aus[2] = z; });
pruefe('Zone', r.zone, 0);
pruefe('Versatz null', r.versatz.every(v => v === 0), true);
console.log(JSON.stringify({ ok: true }));
"""

AUFRISS = STREIFEN + """
const rechts = (i) => (i % B) > 10;
// Rechts 6 cm zur Seite und 3 cm nach oben: Die Glättung zöge die rechten Punkte an der Kante nach unten, unter ihre gehäutete Lage.
const zieh = (i, x, y, z, aus) => { aus[0] = x + (rechts(i) ? 0.06 : 0); aus[1] = y; aus[2] = z + (rechts(i) ? 0.03 : 0); };
const r = g.bild(zieh);
pruefe('Zone', r.zone > 0, true);
const geglaettet = Float32Array.from(g.lage, (v, k) => v + r.versatz[k]);
pruefe('weniger gedehnt', groesste(geglaettet) < groesste(g.lage) - 0.5, true);
let weit = 0, drunter = 0;
for (let p = 0; p < n; p++) {
    const v = r.versatz.subarray(3 * p, 3 * p + 3);
    if (Math.hypot(v[0], v[1], v[2]) > Stoffglaettung.VERSATZ_M + 1e-6) weit++;
    if (v[2] < -1e-6) drunter++;
}
pruefe('Versatz begrenzt', weit, 0);
pruefe('nie unter die gehäutete Lage', drunter, 0);
const r2 = g.bild((i, x, y, z, aus) => { aus[0] = x; aus[1] = y; aus[2] = z; });
pruefe('ohne Riss kein Versatz', r2.versatz.every(v => v === 0) && r2.geaendert, true);
console.log(JSON.stringify({ ok: true }));
"""


class StoffglaettungTest(SimpleTestCase):

    def test_1_drehung_bleibt_wie_gehaeutet(self):
        self.assertTrue(Jsmodul('gemeinsam', 'stoffglaettung.js').laufen(DREHUNG).get('ok'))

    def test_2_aufriss_wird_geglaettet_und_bleibt_ueber_der_lage(self):
        self.assertTrue(Jsmodul('gemeinsam', 'stoffglaettung.js').laufen(AUFRISS).get('ok'))
