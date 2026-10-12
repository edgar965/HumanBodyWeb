# -*- coding: utf-8 -*-
"""`Anatomiezuordnung`, `Strahldreieck`, `Anatomiefuellung`: die Karten des Anatomie-Stücks Texel für Texel aus der Haut rechnen (11./12.10.2026), in Node mit den echten Modulen.

Edgar (Bild, „cute girl DAZ"): „Skin änderung funktioniert nicht bei der Scham, die neue skin Textur erscheint da nicht, nur die farbe." Die Haut hat ihre Karten in ihrer UV, das Stück seinen
eigenen Atlas. Erste Fassung (UV der Haut je Punkt des Stücks): Streifen und Zickzack, und 3 % der Dreiecke zogen die Karte über eine Naht der Hautinseln. Seither wird je Texel des Stücks
die Stelle der Haut darunter gesucht — nach der LAGE im Raum, die UV der Haut spielt dabei keine Rolle, also kann eine Naht der UV nichts zerreißen.

Kunstwelt: Haut = Quadrat 50 × 50 mm in z = 0 aus zwei Dreiecken, Diagonale bei x = y; Stück = Quadrat 30 × 30 mm bei (10 … 40 mm), 2 mm über der Haut, Normalen +z, im Atlas 16 × 16 Texel
auf der Fläche (0,125 … 0,875) — 12 × 12 Texel.

1. `Strahldreieck.trifft`: ein Strahl von oben trifft die Mitte; Abstand und Gewichte stimmen; er trifft auch von unten (beide Richtungen); daneben trifft er nicht; ein zu flacher Strahl (|cos| < 0,5) gilt nicht.
2. `Anatomiezuordnung.rechnen`: jedes belegte Texel zeigt auf den Punkt der Haut, der in x und y genau unter ihm liegt (Fehler < 1 µm) — über die Diagonale der Haut hinweg, und beide Hautdreiecke kommen vor.
   Die belegte Fläche ist die des Stücks (144 Texel ± 6), ohne Normalen (nächster Punkt statt Strahl) dasselbe für die Lage.
3. Ein Stück, das weiter als `REICHWEITE` über der Haut liegt, belegt nichts.
4. `Anatomiefuellung.fuellen`: belegte Texel bleiben, die Nachbarn greifen die Farbe auf (Mittel der belegten Nachbarn), der Rest bekommt das Mittel (oder die Vorgabe der Karte); Alpha 255.

Sabotage-Gegenprobe: in `Strahldreieck.trifft` `MIN_COS` auf 0 → Fall 1 (flacher Strahl) rot; in `_rastern` die Texelmitte (`+ 0.5`) streichen → Fall 2 rot (Lage um ein halbes Texel verschoben); `REICHWEITE` auf 0,05
→ Fall 3 rot. Nicht gelaufen (12.10.2026) — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

ZUORDNUNG = Jsmodul('gemeinsam', 'anatomiezuordnung.js')
STRAHL = Jsmodul('gemeinsam', 'strahldreieck.js')
FUELLUNG = Jsmodul('gemeinsam', 'anatomiefuellung.js')

WELT = """
const haut = { pos: Float32Array.from([0, 0, 0,  0.05, 0, 0,  0.05, 0.05, 0,  0, 0.05, 0]), ecken: Uint32Array.from([0, 1, 2,  0, 2, 3]) };
const stueck = (z, mitNormalen = true) => ({
    pos: Float32Array.from([0.01, 0.01, z,  0.04, 0.01, z,  0.01, 0.04, z,  0.04, 0.04, z]),
    uv: Float32Array.from([0.125, 0.125,  0.875, 0.125,  0.125, 0.875,  0.875, 0.875]),
    index: Uint32Array.from([0, 1, 2,  1, 3, 2]),
    normal: mitNormalen ? Float32Array.from([0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1]) : null,
});
const B = 16;
// Lage (x, y) in der Mitte des Texels `nr` des Stücks
const lage = (nr) => { const i = nr % B, j = Math.floor(nr / B); return [0.01 + (((i + 0.5) / B) - 0.125) / 0.75 * 0.03, 0.01 + (((j + 0.5) / B) - 0.125) / 0.75 * 0.03]; };
// Lage (x, y) auf der Haut aus Dreieck und Gewichten
const hautlage = (z, k) => { const e = haut.ecken, t = z.btri[k], l2 = z.l2[k], l3 = z.l3[k], l1 = 1 - l2 - l3, p = haut.pos;
    const f = (c) => l1 * p[3 * e[3 * t] + c] + l2 * p[3 * e[3 * t + 1] + c] + l3 * p[3 * e[3 * t + 2] + c]; return [f(0), f(1)]; };
"""


class AnatomiezuordnungTest(SimpleTestCase):
    databases = set()

    def test_strahl_trifft_in_beide_richtungen_und_nicht_flach(self):
        skript = """
const { Strahldreieck: S } = await import(MODUL);
const aus = new Float64Array(3), runde = (w) => Math.round(w * 1e6) / 1e6;
const dreieck = [0, 0, 0,  1, 0, 0,  0, 1, 0];

pruefe('von oben', S.trifft(0.25, 0.25, 0.5, 0, 0, 1, ...dreieck, aus), true);
pruefe('Abstand und Gewichte', [runde(aus[0]), runde(aus[1]), runde(aus[2])], [0.5, 0.25, 0.25]);
pruefe('von unten (beide Richtungen)', S.trifft(0.25, 0.25, -0.5, 0, 0, 1, ...dreieck, aus), true);
pruefe('daneben', S.trifft(0.8, 0.8, 0.5, 0, 0, 1, ...dreieck, aus), false);
const flach = Math.hypot(0.9, 0.436), s = [0.9 / flach, 0, 0.436 / flach];
pruefe('zu flacher Strahl gilt nicht', S.trifft(0.25, 0.25, 0.5, ...s, ...dreieck, aus), false);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = STRAHL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_jedes_texel_zeigt_auf_die_stelle_darunter_ueber_die_diagonale_hinweg(self):
        skript = WELT + """
const { Anatomiezuordnung: Z } = await import(MODUL);
for (const mitNormalen of [true, false]) {
    const z = await Z.rechnen(stueck(0.002, mitNormalen), haut, B, B);
    const was = mitNormalen ? 'Strahl' : 'nächster Punkt';
    if (Math.abs(z.anzahl - 144) > 6) throw new Error(was + ': ' + z.anzahl + ' belegte Texel statt 144 ± 6');
    let fehler = 0;
    for (let k = 0; k < z.anzahl; k++) {
        const [ex, ey] = lage(z.texel[k]), [hx, hy] = hautlage(z, k);
        fehler = Math.max(fehler, Math.hypot(ex - hx, ey - hy));
    }
    if (fehler > 1e-6) throw new Error(was + ': größte Abweichung ' + fehler + ' m');
    pruefe(was + ': beide Hautdreiecke kommen vor', [...new Set(z.btri)].sort(), [0, 1]);
}
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = ZUORDNUNG.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_zu_weit_ueber_der_haut_belegt_nichts(self):
        skript = WELT + """
const { Anatomiezuordnung: Z } = await import(MODUL);
const z = await Z.rechnen(stueck(0.1), haut, B, B);
pruefe('nichts belegt', z.anzahl, 0);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = ZUORDNUNG.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_fuellen_greift_in_die_leere_und_laesst_belegtes_stehen(self):
        skript = """
const { Anatomiefuellung: F } = await import(MODUL);
const B = 8, belegt = new Uint8Array(B * B), rgba = new Uint8ClampedArray(B * B * 4), normal = new Uint8ClampedArray(B * B * 4);
const setze = (i, j, r) => { belegt[j * B + i] = 1; rgba.set([r, 0, 0, 255], 4 * (j * B + i)); normal.set([120, 130, 250, 255], 4 * (j * B + i)); };
setze(3, 3, 100); setze(4, 3, 200);
const n = F.fuellen(belegt, B, B, [{ rgba, vorgabe: null }, { rgba: normal, vorgabe: [128, 128, 255, 255] }], 2);
const rot = (i, j) => Array.from(rgba.slice(4 * (j * B + i), 4 * (j * B + i) + 4));

pruefe('belegte Texel gezählt', n, 2);
pruefe('belegt bleibt', [rot(3, 3), rot(4, 3)], [[100, 0, 0, 255], [200, 0, 0, 255]]);
pruefe('Nachbar links nimmt die Farbe auf', rot(2, 3), [100, 0, 0, 255]);
pruefe('Nachbar rechts', rot(5, 3), [200, 0, 0, 255]);
pruefe('weit weg: Mittel der belegten', rot(0, 0), [150, 0, 0, 255]);
pruefe('weit weg: Vorgabe der zweiten Karte', Array.from(normal.slice(0, 4)), [128, 128, 255, 255]);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = FUELLUNG.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
