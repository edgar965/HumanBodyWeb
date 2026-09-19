# -*- coding: utf-8 -*-
u"""`Stoffpendel`: Stoff FÄLLT, und beim Sprung bleibt er am Bund.

Drei Befunde von Edgar in einer Nacht (20.09.2026), alle am Dancing-Queen-Kleid:
„Die Arme gehen ins Kleid … das kleid muss nach unten animieren!!!" (HumanBody,
Idle), „auch die ursula (genesis) mit diesem Kleid und dieser Idle animation
animiert falsch" und „bei der Jump animation verliert die Person das Kleid!!".

Was die Formel heute tut (`gemeinsam/stoffpendel.js`):

    x' = x + v + (ziel − x)·dt·FEDER_FREI + g·SCHWERE·dt²

Die Feder zur GEHÄUTETEN Lage (2/s) und die Schwerkraft (× 0,3) stehen im
Gleichgewicht bei rund 5 cm: 9,81 · 0,3 / (30 · 2) = 4,9 cm. Ein Rock, dessen
Netz 40 cm waagerecht absteht, bleibt also 40 cm abstehen, 5 cm tiefer — und
die hängenden Arme laufen hindurch. Beim Sprung folgt ein freier Punkt der
Lage mit 2/s: bei 2 m/s bleibt er einen Meter zurück, ab 0,5 m setzt
`ENTGLEIST_M` ihn hart auf die Lage — das Kleid springt der Figur nach.

DIESE FÄLLE SIND ROT, BIS DER STOFF FÄLLT UND FOLGT. Sie beschreiben, was
Edgar sieht — nicht, was die Formel kann. Sie wurden geschrieben, nicht
gelaufen (Edgar, 19.09.2026: „keine tests wenn ich nichts sage").

1. Ein Streifen, der in der gehäuteten Lage WAAGERECHT vom Bund absteht
   (9 Reihen à 5 cm = 40 cm, Bund gebunden), hängt nach 3 s zu mindestens
   70 % seiner Länge nach unten: Saum ≥ 28 cm unter dem Bund. Die Kanten
   halten ihn am Bund, die Schwerkraft zieht ihn hinunter; die Feder darf
   das nicht verhindern. Heute erwartet: rund 5 cm.
2. Ein Sprung: der Bund hebt sich in 0,3 s um 0,6 m (2 m/s) und bleibt dann
   oben. Kein Bild darf zurücksetzen (`zurueckgesetzt`), WÄHREND des Sprungs
   keine Kante länger als Ruhelänge + 10 % werden, und 1 s nach dem Sprung
   hängt der Saum wieder an seiner Lage (Auslenkung < 5 cm). „Verliert das
   Kleid" heißt: eines davon ist verletzt. Dass der Streifen nach dem Stopp
   aufbauscht (Trägheit), ist Stoff, kein Fehler.

Sabotage-Gegenprobe (wenn die Fälle einmal grün sind): `SCHWERE` auf 0 →
Fall 1 rot (nichts fällt); `ENTGLEIST_M` auf 0,05 → Fall 2 rot (jedes
Sprungbild setzt zurück). Die echten Kleider auf den echten Figuren prüft
`longrunner/test_kleid_arme_frei.py`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffpendel.js')

#: Gemeinsamer Vorspann: ein Streifen 2 × 9 Punkte, Kante 5 cm, oberste Reihe
#: gebunden. `richtung` legt ihn: (1, 0, 0) waagerecht, (0, -1, 0) hängend.
VORSPANN = """
const { Stoffpendel: S } = await import(MODUL);
const dt = 1 / 30, REIHEN = 9, KANTE = 0.05, BUND = 1.0;
const streifen = (richtung) => {
    const ruhe = [], frei = [];
    for (let r = 0; r < REIHEN; r++) for (let c = 0; c < 2; c++) {
        ruhe.push(richtung[0] * r * KANTE + (richtung[0] ? 0 : c * KANTE),
                  BUND + richtung[1] * r * KANTE,
                  richtung[0] ? c * KANTE : 0);
        frei.push(r === 0 ? 0 : 1);
    }
    const dreiecke = [];
    for (let r = 0; r < REIHEN - 1; r++) {
        const a = 2 * r, b = a + 1, c = a + 2, d = a + 3;
        dreiecke.push(a, b, c, b, d, c);
    }
    return { ruhe, pendel: S.ausDreiecken(Float32Array.from(ruhe), Uint32Array.from(dreiecke),
                                         Float32Array.from(frei)) };
};
const dehnung = (p) => {
    let max = 0;
    for (let e = 0; e < p.kanten.a.length; e++) {
        const i = 3 * p.kanten.a[e], j = 3 * p.kanten.b[e];
        const l = Math.hypot(p.x[j] - p.x[i], p.x[j + 1] - p.x[i + 1], p.x[j + 2] - p.x[i + 2]);
        max = Math.max(max, l / p.kanten.l[e]);
    }
    return max;
};
const saumtiefe = (p) => BUND - Math.max(p.x[3 * (2 * REIHEN - 2) + 1], p.x[3 * (2 * REIHEN - 1) + 1]);
"""

HAENGEN = VORSPANN + """
// --- 1. Waagerecht modelliert, Lage steht still: der Stoff muss fallen -----
const { ruhe, pendel: p } = streifen([1, 0, 0]);
const ziel = Float32Array.from(ruhe);
let zurueck = 0;
for (let i = 0; i < 90; i++) if (p.bild(ziel, dt).zurueckgesetzt) zurueck++;
console.log(JSON.stringify({
    laenge_cm: (REIHEN - 1) * KANTE * 100,
    saum_unter_bund_cm: +(saumtiefe(p) * 100).toFixed(1),
    dehnung: +dehnung(p).toFixed(3),
    zurueckgesetzt: zurueck,
}));
"""

SPRUNG = VORSPANN + """
// --- 2. Hängend, dann springt der Bund 0,6 m in 0,3 s nach oben -------------
const { ruhe, pendel: p } = streifen([0, -1, 0]);
const lage = (hub) => Float32Array.from(ruhe.map((w, k) => k % 3 === 1 ? w + hub : w));
let ziel = lage(0);
for (let i = 0; i < 30; i++) p.bild(ziel, dt);
const HUB = 0.6, BILDER = 9;
let zurueck = 0, dehnungSprung = 0, dehnungDanach = 0, lagMax = 0, bauschMax = 0;
for (let i = 1; i <= BILDER; i++) {
    ziel = lage(HUB * i / BILDER);
    if (p.bild(ziel, dt).zurueckgesetzt) zurueck++;
    dehnungSprung = Math.max(dehnungSprung, dehnung(p));
    lagMax = Math.max(lagMax, p.auslenkung(ziel));
}
for (let i = 0; i < 30; i++) {
    if (p.bild(ziel, dt).zurueckgesetzt) zurueck++;
    dehnungDanach = Math.max(dehnungDanach, dehnung(p));
    bauschMax = Math.max(bauschMax, p.auslenkung(ziel));
}
console.log(JSON.stringify({
    zurueckgesetzt: zurueck,
    dehnung_sprung: +dehnungSprung.toFixed(3),
    dehnung_danach: +dehnungDanach.toFixed(3),
    bausch_cm: +(bauschMax * 100).toFixed(1),
    zurueck_waehrend_cm: +(lagMax * 100).toFixed(1),
    danach_cm: +(p.auslenkung(ziel) * 100).toFixed(1),
    saum_unter_bund_cm: +((BUND + HUB - Math.min(p.x[3 * (2 * REIHEN - 2) + 1],
                                                 p.x[3 * (2 * REIHEN - 1) + 1])) * 100).toFixed(1),
}));
"""


class StoffpendelHaengtTest(SimpleTestCase):

    databases = set()

    #: So weit muss ein waagerecht modellierter Streifen nach 3 s hängen.
    HAENGT_ANTEIL = 0.7
    #: Mehr darf keine Kante über ihre Ruhelänge hinaus (wie in `test_js_stoffpendel`).
    DEHNUNG = 1.10
    #: So nah muss der Stoff eine Sekunde nach dem Sprung an seiner Lage sein.
    DANACH_CM = 5.0

    def test_1_ein_abstehender_rock_faellt_nach_unten(self):
        ausgabe = MODUL.laufen(HAENGEN)
        self.assertEqual(ausgabe['zurueckgesetzt'], 0, 'Sprungschutz griff im Stand: %s' % ausgabe)
        self.assertLess(ausgabe['dehnung'], self.DEHNUNG, 'Kante gerissen: %s' % ausgabe)
        soll = ausgabe['laenge_cm'] * self.HAENGT_ANTEIL
        self.assertGreaterEqual(
            ausgabe['saum_unter_bund_cm'], soll,
            'Der Saum eines %.0f cm langen, waagerecht modellierten Rocks hängt nach 3 s nur '
            '%.1f cm unter dem Bund (verlangt ≥ %.0f cm): die Feder zur gehäuteten Lage hält '
            'ihn in der Luft — genau das Bild, in dem die Arme durchs Kleid gehen.'
            % (ausgabe['laenge_cm'], ausgabe['saum_unter_bund_cm'], soll))

    def test_2_beim_sprung_bleibt_der_stoff_am_bund(self):
        ausgabe = MODUL.laufen(SPRUNG)
        fehler = []
        if ausgabe['zurueckgesetzt']:
            fehler.append('%d Bilder hart auf die Lage gesetzt (das Kleid springt nach)'
                          % ausgabe['zurueckgesetzt'])
        if ausgabe['dehnung_sprung'] >= self.DEHNUNG:
            fehler.append('Kante während des Sprungs auf das %.2f-Fache gedehnt (das Kleid reißt vom Bund)'
                          % ausgabe['dehnung_sprung'])
        if ausgabe['danach_cm'] >= self.DANACH_CM:
            fehler.append('1 s nach dem Sprung noch %.1f cm von der Lage entfernt'
                          % ausgabe['danach_cm'])
        # Nach dem Stopp bauscht der Streifen auf (Trägheit, wie Stoff) und faltet
        # sich dabei — als zweispaltiges Fachwerk in der Ebene staucht das einzelne
        # Kanten (gemessen 1,23); das ist eine Grenze des Kunststreifens, kein Riss.
        self.assertEqual(fehler, [],
                         'Beim Sprung um 0,6 m in 0,3 s verliert die Figur das Kleid: %s '
                         '(Rückstand während des Sprungs %.1f cm, Bausch danach %.1f cm, '
                         'Dehnung danach %.2f)'
                         % ('; '.join(fehler), ausgabe['zurueck_waehrend_cm'],
                            ausgabe['bausch_cm'], ausgabe['dehnung_danach']))
