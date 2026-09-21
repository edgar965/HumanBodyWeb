# -*- coding: utf-8 -*-
"""Freisteller-Bausteine im Browser (21.09.2026, Edgar: „schreibe dir tests, diese buttons auf den
Seiten funktionieren nicht, das Vorschaubild ist weg usw"). In Node mit Attrappen für Leinwand,
Foto und Feld — kein DOM, kein Server:

1. `Bildmodellauftrag.dateiAdresse`: Ausschnitt-Adresse trägt `freisteller.stand`, sonst
   `bildstand`, sonst nichts — ohne Stand zeigte Chrome nach Zurücksetzen das alte Bild.
2. `Freistellerpinsel`: Breite in Bildpixeln (Regler 1 → 1 px, 100 → 400 px), Strich/Punkt,
   Rückgängig/Wiederholen/Alle weg mit Knopfzuständen, Strg beim Pinsel = kein Strich.
3. `Freistellerzoom`: Rad zoomt um den Zeiger (1…16×), Bühne bleibt im Feld, Strg + linke oder
   mittlere Taste schiebt, `einpassen` setzt zurück; ohne Zoom keine Verschiebung.
Sabotage-Gegenprobe: `bildstand` in `dateiAdresse` weg → Fall 1 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

AUFTRAG = Jsmodul('bildmodell', 'auftrag.js')
PINSEL = Jsmodul('bildmodell', 'freistellerpinsel.js')
ZOOM = Jsmodul('bildmodell', 'freistellerzoom.js')

SKRIPT_AUFTRAG = """
const { Bildmodellauftrag } = await import(MODUL);
const a = new Bildmodellauftrag({ id: 'j1', bilder: [
    { datei: 'a.jpg', freisteller: { stand: '2026-09-21T10:00:00' }, bildstand: 111 },
    { datei: 'b.jpg', bildstand: 222 },
    { datei: 'c.jpg' }] });
pruefe('freisteller.stand zuerst', a.dateiAdresse('zuschnitt', 'a.jpg').endsWith('?t=2026-09-21T10%3A00%3A00'), true);
pruefe('bildstand', a.dateiAdresse('zuschnitt', 'b.jpg').endsWith('/zuschnitt/b.jpg?t=222'), true);
pruefe('ohne stand', a.dateiAdresse('zuschnitt', 'c.jpg').endsWith('/zuschnitt/c.jpg'), true);
pruefe('andere ordner ohne t', a.dateiAdresse('ergebnis', 'a.jpg').includes('?'), false);
console.log(JSON.stringify({ ok: true }));
"""

ATTRAPPEN = """
const ctx = new Proxy({}, { get: () => () => {} });
const leinwand = { width: 0, height: 0, style: {}, addEventListener() {}, getContext: () => ctx,
                   getBoundingClientRect: () => ({ left: 0, top: 0, width: 200, height: 300 }),
                   setPointerCapture() {}, releasePointerCapture() {} };
const foto = { naturalWidth: 1000, naturalHeight: 1500, clientWidth: 200, clientHeight: 300, offsetLeft: 0, offsetTop: 0,
               addEventListener() {} };
const zeiger = (typ, x, y, extra = {}) => ({ type: typ, button: 0, buttons: 1, pointerId: 1, clientX: x, clientY: y,
                                             preventDefault() {}, ...extra });
"""

SKRIPT_PINSEL = ATTRAPPEN + """
const { Freistellerpinsel: P } = await import(MODUL);
let aenderungen = 0;
const p = new P(leinwand, foto, () => { aenderungen += 1; });
p.passen();
pruefe('leinwand in bildauflösung', [leinwand.width, leinwand.height, leinwand.style.width], [1000, 1500, '200px']);
pruefe('breite px', [1, 20, 50, 100].map(w => { p.regler = w; return p.breitePx(); }), [1, 16, 99, 400]);
p.regler = 1;
pruefe('anteil = 1 px', Math.round(p.breite * foto.naturalWidth), 1);
pruefe('anfangs leer', [p.leer, p.rueckgaengigMoeglich, p.wiederholenMoeglich], [true, false, false]);
p.werkzeug = 'pinsel-draussen';
p._anfang(zeiger('pointerdown', 20, 30)); p._weiter(zeiger('pointermove', 40, 60)); p._ende(zeiger('pointerup', 40, 60));
pruefe('ein strich', [p.striche().length, p.striche()[0].art, p.striche()[0].punkte.length, aenderungen], [1, 'draussen', 2, 1]);
pruefe('strichpunkte normiert', p.striche()[0].punkte[0], [0.1, 0.1]);
p._anfang(zeiger('pointerdown', 50, 50, { ctrlKey: true })); p._ende(zeiger('pointerup', 50, 50));
pruefe('strg = kein strich', p.striche().length, 1);
p.werkzeug = 'punkt-drin';
p._anfang(zeiger('pointerdown', 100, 150));
pruefe('punkt', p.punkte(), [[0.5, 0.5, 1]]);
pruefe('knöpfe', [p.leer, p.rueckgaengigMoeglich, p.wiederholenMoeglich], [false, true, false]);
p.rueckgaengig();
pruefe('rückgängig nimmt den punkt', [p.punkte().length, p.striche().length, p.wiederholenMoeglich], [0, 1, true]);
p.wiederholen();
pruefe('wiederholen bringt ihn zurück', [p.punkte().length, p.wiederholenMoeglich], [1, false]);
p.leeren();
pruefe('alle weg', [p.leer, p.wiederholenMoeglich], [true, true]);
p.wiederholen();
pruefe('alle weg ist rückgängig', [p.striche().length, p.punkte().length], [1, 1]);
p.setzen([{ art: 'drin', breite: 0.02, punkte: [[0.1, 0.2]] }], [[0.3, 0.3, 0]]);
pruefe('setzen', [p.striche().length, p.punkte(), p.rueckgaengigMoeglich, p.wiederholenMoeglich], [1, [[0.3, 0.3, 0]], true, false]);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_ZOOM = """
const { Freistellerzoom: Z } = await import(MODUL);
const feld = { clientWidth: 400, clientHeight: 300, style: {}, addEventListener() {},
               getBoundingClientRect: () => ({ left: 0, top: 0 }), setPointerCapture() {}, releasePointerCapture() {} };
const b1 = { parentElement: feld, style: {} }, b2 = { parentElement: feld, style: {} };
const skalen = [];
const z = new Z([b1, b2], s => skalen.push(s));
z._anfang({ button: 1, pointerId: 1, clientX: 10, clientY: 10, preventDefault() {} }, feld);
pruefe('ohne zoom kein griff', z._griff, null);
z._rad({ deltaY: -100, clientX: 200, clientY: 150, preventDefault() {} }, feld);
pruefe('rad zoomt', z.skala, 1.25);
pruefe('um den zeiger', [z.tx, z.ty], [-50, -37.5]);
pruefe('beide bühnen gleich', b1.style.transform === b2.style.transform && b1.style.transform.includes('scale(1.25)'), true);
for (let i = 0; i < 30; i++) z._rad({ deltaY: -100, clientX: 200, clientY: 150, preventDefault() {} }, feld);
pruefe('höchstens 16×', z.skala, 16);
z.setzen(2, 500, -9999);
pruefe('bühne bleibt im feld', [z.tx, z.ty], [0, -300]);
z._anfang({ button: 0, ctrlKey: true, pointerId: 7, clientX: 100, clientY: 100, preventDefault() {} }, feld);
z._weiter({ pointerId: 7, clientX: 60, clientY: 90 });
pruefe('strg + links schiebt', [z.tx, z.ty], [-40, -300]);
z._ende({ pointerId: 7 }, feld);
z._anfang({ button: 0, pointerId: 8, clientX: 100, clientY: 100, preventDefault() {} }, feld);
pruefe('links ohne strg schiebt nicht', z._griff, null);
z.einpassen();
pruefe('einpassen', [z.skala, z.tx, z.ty, b1.style.transform], [1, 0, 0, '']);
pruefe('gemeldet', skalen[0] === 1.25 && skalen[skalen.length - 1] === 1, true);
console.log(JSON.stringify({ ok: true }));
"""


VORSCHAU = Jsmodul('bildmodell', 'freistellervorschau.js')

SKRIPT_VORSCHAU = """
const { Freistellervorschau: V } = await import(MODUL);
// 5×5, ein Pixel in der Mitte gesetzt: Dilatation r=1 füllt 3×3, Erosion danach lässt den Mittelpunkt.
const a = new Float32Array(25); a[12] = 1;
const dil = V.morph(a, 5, 5, 1, true);
pruefe('dilatation 3x3', Array.from(dil).reduce((s, v) => s + v, 0), 9);
pruefe('rand bleibt 0', [dil[0], dil[4], dil[20]], [0, 0, 0]);
const ero = V.morph(dil, 5, 5, 1, false);
pruefe('erosion zurück', [Array.from(ero).reduce((s, v) => s + v, 0), ero[12]], [1, 1]);
// Kastenfilter: konstantes Feld bleibt konstant, Summe bleibt erhalten (Randbehandlung: Mittel über vorhandene).
const k = new Float32Array(25).fill(0.5);
pruefe('kasten konstant', Array.from(V._kasten(k, 5, 5, 1, true)).every(v => Math.abs(v - 0.5) < 1e-6), true);
const w = V.weich(a, 5, 5, 0.8);
pruefe('weich verteilt', w[12] < 1 && w[7] > 0 && w[17] > 0, true);
pruefe('hintergrund', V.HINTERGRUND.gruen, [0, 177, 64]);
// Bereichswachstum (Positivliste NUR außerhalb der Figur): 6×1, Haut an 0..2 und 4..5, Figur bei 0 → 4..5 hängt nicht dran.
const haut = Float32Array.from([1, 1, 1, 0, 1, 1]), figur = Float32Array.from([1, 0, 0, 0, 0, 0]);
pruefe('verbunden', Array.from(V.verbunden(haut, 6, 1, figur)), [1, 1, 1, 0, 0, 0]);
pruefe('diagonal zählt', Array.from(V.verbunden(Float32Array.from([1, 0, 0, 1]), 2, 2, Float32Array.from([1, 0, 0, 0]))), [1, 0, 0, 1]);
pruefe('ohne figur nichts', Array.from(V.verbunden(haut, 6, 1, new Float32Array(6))), [0, 0, 0, 0, 0, 0]);
console.log(JSON.stringify({ ok: true }));
"""


class FreistellerJsTest(SimpleTestCase):
    def test_vorschau_filter(self):
        self.assertTrue(VORSCHAU.laufen(SKRIPT_VORSCHAU).get('ok'))

    def test_dateiadresse_mit_stand(self):
        self.assertTrue(AUFTRAG.laufen(SKRIPT_AUFTRAG).get('ok'))

    def test_pinsel(self):
        self.assertTrue(PINSEL.laufen(SKRIPT_PINSEL).get('ok'))

    def test_zoom(self):
        self.assertTrue(ZOOM.laufen(SKRIPT_ZOOM).get('ok'))
