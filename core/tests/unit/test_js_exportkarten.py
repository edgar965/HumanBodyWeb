# -*- coding: utf-8 -*-
u"""Exportierte Bildkarten müssen richtigherum in der Datei liegen (26.09.2026).

Edgar, nach dem dritten Anlauf: „gleiche fehler, hoffentlich merkt dein
Testcase das!"

DER VORFALL
===========
Three lädt die Texturen als `ImageBitmap` und setzt dafür `texture.flipY =
false`: das Bild liegt dann schon so im Speicher, wie die Grafikkarte es
braucht — Zeile 0 gehört zu v = 0, also UNTEN. Eine Bilddatei neben einer
`.obj` wird andersherum gelesen: Zeile 0 ist oben, v = 1.

`Werkstoffbild.png` hat das Bild einfach abgemalt. Jede Karte lag damit in der
Exportdatei auf dem Kopf, und in MeshLab traf jede Fläche die falsche
Texturzeile. Auf der Haut sieht man das fast nicht — eine gespiegelte
Hautstelle sieht aus wie Haut. Sichtbar wurde es erst dort, wo die gespiegelte
Stelle NEBEN die UV-Insel fällt: helle Flecken an Hals, Knie und Fingern, drei
Tage lang für „fehlende Textur" gehalten.

Gemessen an `DamiraFein.obj` (261 MB, 1.514.592 Flächen): 133.552 Flächen
trafen den leeren Kartenrand. Mit gespiegelter Karte: null. Diese Gegenprobe
ist der Beweis, nicht die Vermutung — beide Richtungen wurden gerechnet.

WAS HIER GEPRÜFT WIRD
=====================
Nicht „wurde `scale(1, -1)` gerufen" — das prüft die Umsetzung, nicht die
Wirkung. Der Canvas ist hier eine kleine, echte Rasterattrappe: sie führt die
Transformationsmatrix mit und schreibt die Zeilen wirklich um. Der Fall liest
danach die Pixel und verlangt, dass die ERSTE Bildzeile in der Datei UNTEN
steht, wenn die Karte `flipY = false` trägt.

Sabotage (so wird der Fall rot): in `werkstoffbild.js` den Block
`if (flipY === false) { … }` streichen, oder in `objmtl.js` wieder
`Werkstoffbild.png(karte.image, maxSeite)` ohne das dritte Argument rufen.
"""
import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

WURZEL = Path(settings.BASE_DIR)
VIEWER = (WURZEL / 'static' / 'viewer').as_posix()

#: Rasterattrappe statt Canvas: `drawImage` schreibt die Zeilen des Quellbilds
#: wirklich um, unter der gesetzten Transformation. Nur die zwei Fälle, die
#: `Werkstoffbild` benutzt (Einheitsmatrix und y-Spiegelung) — mehr braucht es
#: nicht, und mehr wäre nicht geprüft.
SKRIPT = """
let letztes = null;

function attrappenCanvas() {
    const zustand = { flip: false, breite: 0, hoehe: 0, daten: null };
    const ctx = {
        globalCompositeOperation: 'source-over',
        fillStyle: '',
        translate: (x, y) => { if (y) zustand.flip = true; },
        scale: (x, y) => { if (y === -1) zustand.flip = !zustand.flip ? true : zustand.flip; },
        drawImage: (bild, x, y, b, h) => {
            // Quellbild: `bild.zeilen[i]` ist der Wert der i-ten Zeile,
            // Zeile 0 wie im Speicher. Ziel: Zeile 0 der DATEI.
            const aus = [];
            for (let i = 0; i < h; i++) {
                const quelle = Math.floor(i * bild.height / h);
                aus.push(bild.zeilen[zustand.flip ? bild.height - 1 - quelle : quelle]);
            }
            zustand.daten = aus;
        },
        // Der harte Schnitt greift über getImageData/putImageData. Die
        // Attrappe reicht jede Zeile als EINEN Bildpunkt durch (R=G=B=Wert),
        // damit `schneiden` unverändert darüberläuft.
        getImageData: () => {
            const roh = new Uint8ClampedArray((zustand.daten || []).length * 4);
            (zustand.daten || []).forEach((wert, i) => {
                roh[i*4] = wert; roh[i*4+1] = wert; roh[i*4+2] = wert; roh[i*4+3] = 255;
            });
            return { data: roh };
        },
        putImageData: (daten) => {
            const aus = [];
            for (let i = 0; i < daten.data.length; i += 4) aus.push(daten.data[i]);
            zustand.daten = aus;
        },
        // `multiply` wie im Browser: Zielwert mal Füllwert, beide 0…1.
        fillRect: () => {
            if (ctx.globalCompositeOperation !== 'multiply' || !zustand.daten) return;
            const treffer = /rgb\\((\\d+), (\\d+), (\\d+)\\)/.exec(ctx.fillStyle);
            if (!treffer) return;
            const faktor = Number(treffer[1]) / 255;
            zustand.daten = zustand.daten.map((wert) => Math.round(wert * faktor * 100) / 100);
        },
    };
    return {
        set width(w) { zustand.breite = w; },
        set height(h) { zustand.hoehe = h; },
        get width() { return zustand.breite; },
        get height() { return zustand.hoehe; },
        getContext: () => ctx,
        toBlob: (rueck) => { letztes = zustand.daten; rueck(new Blob(['x'])); },
    };
}

globalThis.document = { createElement: () => attrappenCanvas() };

const { Werkstoffbild } = await import('file:///%(viewer)s/gemeinsam/werkstoffbild.js');
const { ObjMtl } = await import('file:///%(viewer)s/gemeinsam/objmtl.js');

/** Bild mit unterscheidbaren Zeilen: oben 0, unten 3. Werte ungleich null,
 *  damit eine Multiplikation überhaupt sichtbar wird. */
const bild = () => ({ width: 4, height: 4, zeilen: [100, 120, 140, 160] });

const ergebnis = {};

// 1. `flipY = true` (gewöhnliches <img>): Zeilen bleiben, wie sie sind.
await Werkstoffbild.png(bild(), 0, true);
ergebnis.mitFlipY = letztes;

// 2. `flipY = false` (ImageBitmap, wie Three die Karten lädt): umgedreht.
await Werkstoffbild.png(bild(), 0, false);
ergebnis.ohneFlipY = letztes;

// 3. Voreinstellung — ein Aufrufer, der nichts sagt, meint die gewöhnliche.
await Werkstoffbild.png(bild(), 0);
ergebnis.vorgabe = letztes;

// 4. Der Weg, den der OBJ-Export wirklich nimmt: `ObjMtl` muss das `flipY`
// der Karte durchreichen. Genau das fehlte.
const karte = (flipY) => ({ image: bild(), flipY, name: 'k' });
const werkstoff = { name: 'haut', color: { r: 1, g: 1, b: 1 }, opacity: 1,
                    map: karte(false) };
const netz = { material: werkstoff, geometry: { groups: [] } };
const { mtl, bilder } = await ObjMtl.bauen([netz], true, '', 0);
ergebnis.ueberObjMtl = letztes;
ergebnis.mtlHatKarte = mtl.includes('map_Kd');
ergebnis.bildzahl = bilder.length;

// 5. Und die Deckkraftmaske genauso — sie geht denselben Weg.
const werkstoff2 = { name: 'wimper', color: { r: 1, g: 1, b: 1 }, opacity: 1,
                     alphaMap: karte(false) };
await ObjMtl.bauen([{ material: werkstoff2, geometry: { groups: [] } }], true, '', 0);
ergebnis.ueberAlphaMap = letztes;

// 6. Grundfarbe: eine dunkle Braue (Kd 0,2) muss in der KARTE landen, und
// die `.mtl` muss dazu `Kd 1 1 1` schreiben.
const braue = { name: 'braue', color: { r: 0.2, g: 0.2, b: 0.2 }, opacity: 1,
                map: karte(false) };
const aus3 = await ObjMtl.bauen([{ material: braue, geometry: { groups: [] } }], true, '', 0);
ergebnis.braueKarte = letztes;
ergebnis.braueMtl = aus3.mtl.split('\\n').filter((z) => z.startsWith('Kd '))[0];

// 7. Gegenprobe: die MASKE desselben Werkstoffs darf NICHT eingefärbt werden —
// sie ist eine Zahl je Bildpunkt, keine Farbe.
const braue2 = { name: 'braue2', color: { r: 0.2, g: 0.2, b: 0.2 }, opacity: 1,
                 alphaMap: karte(false) };
await ObjMtl.bauen([{ material: braue2, geometry: { groups: [] } }], true, '', 0);
ergebnis.braueMaske = letztes;

// 8. Ohne Karte bleibt die Grundfarbe in der `.mtl` stehen — sonst verlöre
// ein farbiges Stück ohne Bildkarte (Kleid, Schuh) seine Farbe.
const kleid = { name: 'kleid', color: { r: 0.1, g: 0.2, b: 0.8 }, opacity: 1 };
const aus4 = await ObjMtl.bauen([{ material: kleid, geometry: { groups: [] } }], true, '', 0);
ergebnis.kleidMtl = aus4.mtl.split('\\n').filter((z) => z.startsWith('Kd '))[0];

// 9. Haarmaske: `alphaTest` schneidet sie hart. Zeilen 100/120/140/160,
// Schwelle 0,5 (= 128) -> alles darunter weg, alles darüber voll.
const haar = { name: 'haar', color: { r: 1, g: 1, b: 1 }, opacity: 1,
               alphaTest: 0.5, alphaMap: karte(true) };
await ObjMtl.bauen([{ material: haar, geometry: { groups: [] } }], true, '', 0);
ergebnis.haarMaske = letztes;

// 10. Gegenprobe: ohne `alphaTest` bleibt die Maske weich — ein Schleier,
// der wirklich mischen soll, darf seine Abstufung behalten.
const schleier = { name: 'schleier', color: { r: 1, g: 1, b: 1 }, opacity: 0.5,
                   transparent: true, alphaTest: 0, alphaMap: karte(true) };
await ObjMtl.bauen([{ material: schleier, geometry: { groups: [] } }], true, '', 0);
ergebnis.schleierMaske = letztes;

console.log(JSON.stringify(ergebnis));
"""


class ExportkartenTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — die JS-Tests führen die Module wirklich aus.')
        ordner = Path(ProjektTemp.ordner('test_modellexport'))
        skript = ordner / 'karten_probe.mjs'
        skript.write_text(SKRIPT % {'viewer': VIEWER}, encoding='utf-8')
        lauf = subprocess.run(
            ['node', skript.as_posix()], cwd=WURZEL, capture_output=True, text=True, timeout=120,
        )
        if lauf.returncode != 0:
            raise RuntimeError(f'node-Lauf gescheitert:\n{lauf.stdout}\n{lauf.stderr}')
        cls.ergebnis = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_1_gewoehnliches_bild_bleibt_wie_es_ist(self):
        u"""Ein `<img>` trägt `flipY = true` — daran darf nichts gedreht werden."""
        self.assertEqual(self.ergebnis['mitFlipY'], [100, 120, 140, 160])
        self.assertEqual(self.ergebnis['vorgabe'], [100, 120, 140, 160],
                         'ohne Angabe gilt die gewöhnliche Richtung')

    def test_2_imagebitmap_karte_wird_gedreht(self):
        u"""`flipY = false` heißt: Zeile 0 liegt unten. In der Datei muss sie
        wieder nach unten — sonst trifft im fremden Programm jede Fläche die
        falsche Texturzeile."""
        self.assertEqual(self.ergebnis['ohneFlipY'], [160, 140, 120, 100],
                         'die Karte steht in der Exportdatei auf dem Kopf')

    def test_3_objmtl_reicht_die_richtung_durch(self):
        u"""Der eigentliche Fehler saß nicht in `Werkstoffbild`, sondern im
        Aufruf: `ObjMtl` gab nur das Bild weiter, nicht die Karte."""
        self.assertTrue(self.ergebnis['mtlHatKarte'], 'ohne map_Kd prüft der Fall nichts')
        self.assertEqual(self.ergebnis['bildzahl'], 1)
        self.assertEqual(self.ergebnis['ueberObjMtl'], [160, 140, 120, 100],
                         'ObjMtl reicht `karte.flipY` nicht an Werkstoffbild durch')

    def test_4_auch_die_deckkraftmaske(self):
        u"""Wimpern und Haarkarten tragen ihre Form in der `alphaMap` —
        steht die auf dem Kopf, sitzt die Maske spiegelverkehrt."""
        self.assertEqual(self.ergebnis['ueberAlphaMap'], [160, 140, 120, 100])

    def test_5_grundfarbe_landet_in_der_karte(self):
        u"""DER ZWEITE VORFALL: Three rechnet `color` MAL `map`; Blender und
        MeshLab ERSETZEN `Kd` durch `map_Kd`. Die Brauenkarte ist ein helles
        Graustufenbild — ohne die fast schwarze Grundfarbe wurden daraus
        schneeweiße Brauen, und das Haar (Kd 0,6444) war ein Drittel zu hell.
        Also: Farbe in die Karte, `Kd 1 1 1` in die `.mtl`."""
        self.assertEqual(self.ergebnis['braueKarte'], [32, 28, 24, 20],
                         'die Grundfarbe 0,2 steckt nicht in der Karte')
        self.assertEqual(self.ergebnis['braueMtl'], 'Kd 1.0000 1.0000 1.0000',
                         'mit Karte muss Kd die Eins sein, sonst wird doppelt gerechnet')

    def test_6_maske_bleibt_ungefaerbt(self):
        u"""Eine Deckkraftmaske ist eine Zahl je Bildpunkt, keine Farbe —
        wird sie mit 0,2 multipliziert, verschwindet das Haar fast ganz."""
        self.assertEqual(self.ergebnis['braueMaske'], [160, 140, 120, 100])

    def test_7_ohne_karte_bleibt_die_farbe_in_der_mtl(self):
        u"""Gegenprobe: Kleid und Schuh haben keine Bildkarte. Würde hier
        pauschal `Kd 1 1 1` geschrieben, wären sie weiß."""
        self.assertEqual(self.ergebnis['kleidMtl'], 'Kd 0.1000 0.2000 0.8000')

    def test_8_haarmaske_wird_am_alphatest_geschnitten(self):
        u"""DER DRITTE VORFALL (Edgar mit Bild: brauner Klecks statt Strähne):
        Three zeichnet Haarkarten mit `alphaTest` — ganz da oder ganz weg, der
        Tiefenpuffer entscheidet. Ein `.obj`-Leser MISCHT stattdessen, und die
        schwach maskierten, beige auslaufenden Strähnenenden schimmerten durch
        die vorderen hindurch."""
        self.assertEqual(self.ergebnis['haarMaske'], [0, 0, 255, 255],
                         'unter 128 muss weg, darüber voll')

    def test_9_ohne_alphatest_bleibt_die_maske_weich(self):
        u"""Gegenprobe: ein Schleier, der wirklich mischen soll, behält seine
        Abstufung — sonst wäre er plötzlich undurchsichtig."""
        self.assertEqual(self.ergebnis['schleierMaske'], [100, 120, 140, 160])
