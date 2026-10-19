# -*- coding: utf-8 -*-
"""`Anatomiehaut` / `Anatomieton`: das starre Anatomie-Stück folgt der gewählten Haut (11.10.2026), geprüft in Node.

Edgar: „wenn ich die Haut eines Daz-Modells ändere, wird die Textur der Scham nicht angepasst" — Ursulas helle Geograft-Karte stand als
Fleck auf einer dunklen Haut (im Chrome nachgestellt: `Ursula1` + `G9 Feminine Skin 04 MAT`). Die Module sind Rechnung ohne Three.js;
Körper, Stück und Karten sind hier Attrappen mit den Feldern, die der Code liest (`geometry.attributes`, `groups`, `userData`, `map`).

`Anatomieton` (Messung):
1. `abstand`: gleiche Farbe 0, die gemessenen Paare aus dem Chrome (183/125/109 gegen 206/153/128: 11,0; gegen 115/81/62: 22,1).
2. `proben`: die Texel an den UV der Punkte, Zeile 0 = v 0, die UV wickeln (u − floor(u)); Deckkraft ≤ 0,5 zählt nicht; ohne Karte der Ton der Farbe.
3. `median` je Kanal; `kasten` + `nahe`: nur Punkte des Indexbereichs im erweiterten Kasten.

`Anatomiehaut` (Entscheidung):
4. dunkle Haut, helles Stück → Karte weg, Farbe = Hautton rings um das Stück; die Ablage hält Karte und Farbe.
5. passende Haut OHNE Farbkarte (Rechnung nicht möglich) → das Stück bleibt, wie es war.
6. Haut zurück auf leer → das Stück MIT eigener Karte (Genitalvariante) zeigt sie wieder, Farbe und Ablage zurück (Rundreise); eine eigene Farbe ändert daran nichts.
7. Eigene Farbe am Stück gilt vor der Haut; fehlt die Karte des Stücks (Bild noch nicht da), bleibt alles und `anwenden` meldet „nicht fertig".
8. Kommt die eigene Karte NACH dem Umstellen an (Texturen laden asynchron), wird sie wieder abgenommen und gemerkt.
9. `stand` ändert sich mit Haut und Körpernetz; ohne Anatomie-Stück ist `nachziehen` leer.
10. Mit Farbkarte der Haut folgt das Stück JEDER Haut, auch einer mit passendem Ton (Edgar, 12.10.2026: „fixe alle skins" — auf `G9 Feminine Skin 01`, sehr hell,
    stand das Stück als Fleck auf seiner eigenen Karte): die eigene Karte weg (gerechnet wird), die Ablage hält sie, die Rechnung ist angestoßen (`anatomieBackt` = Schlüssel);
    der Schlüssel der Rechnung ändert sich mit der Haut (andere Karten → andere Rechnung).
11. Katalog-Haut (`haut` leer, Edgar 18.10.2026: „Figur Matt0 - textur vom Genital wird nicht von der textur des Körpers übernommen", dann „fixe das bei allen
    Modellen"): ein Stück OHNE eigene Farbkarte („Daz Anatomie Mann" hat nur eine Farbe) bekommt die gerechneten Karten der Haut; MIT eigener (Variante der Frau)
    behält es sie — die Karte ist das Genital, aus der glatten Haut darunter gebacken war es weg (Regression, Edgar 18.10.2026 abends: „Damira0 … haben schon wieder
    nicht mehr die weiblichen Genitalien"). Sabotage: in `anwenden` `bleibt` auf false → Fälle 6 und 11 rot; den Hautton an `inst.haut` binden → Fall 11 rot.
    Geschrieben 18.10.2026, nicht gelaufen.

Sabotage-Gegenprobe: `TOLERANZ` auf 100 → Fall 4 rot; `_zurueck` leeren → Fall 6 rot; die Prüfung `eigene` weglassen → Fall 7 rot; die Zeile
`ablage.karte = m.map` streichen → Fall 8 rot; in `proben` die Zeile von `v` nicht wickeln → Fall 2 rot; in `anwenden` `schluessel ||` streichen → Fall 10 rot.
Gelaufen 12.10.2026 (2 Tests, grün); die Sabotage-Gegenprobe ist nicht gefahren.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

TON = Jsmodul('gemeinsam', 'anatomieton.js')
HAUT = Jsmodul('gemeinsam', 'anatomiehaut.js')

# Gemeinsame Attrappen: Farbe (r, g, b linear), Attribut, Karte aus einem einfarbigen Raster (sRGB-Bytes).
ATTRAPPEN = """
const rund = (liste, n = 4) => liste.map(w => Math.round(w * 10 ** n) / 10 ** n);
const farbe = (r, g, b) => ({ r, g, b,
    clone() { return farbe(this.r, this.g, this.b); },
    copy(o) { this.r = o.r; this.g = o.g; this.b = o.b; return this; },
    setRGB(r2, g2, b2) { this.r = r2; this.g = g2; this.b = b2; return this; } });
const attribut = (flach, n) => ({ count: flach.length / n, array: Float32Array.from(flach),      // `array`: `Anatomielage.lage` liest die Punkte als Feld (seit 18.10.2026)
    getX: i => flach[n * i], getY: i => flach[n * i + 1], getZ: i => flach[n * i + 2] });
const lin = (byte) => { const c = byte / 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const karte = (rgb, alpha = 255) => {
    const s = 256, pixel = new Uint8ClampedArray(s * s * 4), bild = {};
    for (let i = 0; i < s * s; i++) { pixel[4 * i] = rgb[0]; pixel[4 * i + 1] = rgb[1]; pixel[4 * i + 2] = rgb[2]; pixel[4 * i + 3] = alpha; }
    return { image: bild, userData: { tonraster: { bild, pixel } } };
};
"""


class AnatomietonTest(SimpleTestCase):
    databases = set()

    def test_messung_der_farbe_rings_um_ein_stueck(self):
        skript = ATTRAPPEN + """
const { Anatomieton: N } = await import(MODUL);

// 1. Farbabstand
pruefe('gleich', N.abstand([0.5, 0.3, 0.2], [0.5, 0.3, 0.2]), 0);
const l = (r, g, b) => [lin(r), lin(g), lin(b)];
pruefe('Ursula auf Ursula', Math.round(N.abstand(l(183, 125, 109), l(206, 153, 128)) * 10) / 10, 11.0);
pruefe('auf dunkler Haut', Math.round(N.abstand(l(183, 125, 109), l(115, 81, 62)) * 10) / 10, 22.1);

// 2. Proben: Zeile 0 = v 0 (links unten hell, oben dunkel), UV wickeln, Deckkraft
const unten = new Uint8ClampedArray(256 * 256 * 4);
for (let y = 0; y < 256; y++) for (let x = 0; x < 256; x++) {
    const k = 4 * (y * 256 + x), hell = y < 128;
    unten[k] = hell ? 200 : 20; unten[k + 1] = hell ? 150 : 20; unten[k + 2] = hell ? 100 : 20; unten[k + 3] = (x < 128) ? 255 : 0;
}
const bild = {};
const geteilt = { image: bild, userData: { tonraster: { bild, pixel: unten } } };
const mat = { map: geteilt, color: farbe(1, 1, 1) };
const uv = attribut([0.25, 0.25, 0.25, 0.75, 1.25, 0.25, 0.75, 0.25], 2);   // unten-links, oben-links, (1.25 → 0.25) unten-links, unten-RECHTS
const proben = N.proben(mat, uv, [0, 1, 2, 3]);
pruefe('Zeilen und Deckkraft', proben.length, 3);                   // Punkt 3 liegt rechts: durchsichtig
pruefe('v 0 ist unten, hell', rund(proben[0]), rund(l(200, 150, 100)));
pruefe('v 0,75 ist oben, dunkel', rund(proben[1]), rund(l(20, 20, 20)));
pruefe('u wickelt', rund(proben[2]), rund(l(200, 150, 100)));
pruefe('Farbe wirkt', rund(N.proben({ map: geteilt, color: farbe(0.5, 1, 1) }, uv, [0])[0]), rund([lin(200) * 0.5, lin(150), lin(100)]));
pruefe('ohne Karte der Ton der Farbe', N.proben({ map: null, color: farbe(0.2, 0.3, 0.4) }, uv, [0, 1, 2]), [[0.2, 0.3, 0.4]]);
pruefe('Karte ohne Bild', N.proben({ map: { userData: {} }, color: farbe(1, 1, 1) }, uv, [0]), null);

// 3. Median je Kanal, Kasten, nahe Punkte
pruefe('Median', N.median([[1, 9, 5], [2, 8, 6], [3, 7, 4]]), [2, 8, 5]);
pruefe('Median leer', N.median([]), null);
const geo = { attributes: { position: attribut([0, 0, 0, 1, 1, 1, 0.5, 0.5, 0.5, 5, 5, 5], 3) },
              index: { getX: i => [0, 1, 2, 3, 2, 1][i] } };
const kasten = N.kasten({ attributes: { position: attribut([0, 0, 0, 1, 1, 1], 3) } }, 0.1);
pruefe('Kasten', [rund(kasten.lo, 2), rund(kasten.hi, 2)], [[-0.1, -0.1, -0.1], [1.1, 1.1, 1.1]]);
pruefe('nahe: nur im Kasten, jeder Punkt einmal', [...N.nahe(geo, { start: 0, count: 6 }, kasten)].sort(), [0, 1, 2]);
pruefe('nahe: nur der Bereich', [...N.nahe(geo, { start: 3, count: 3 }, kasten)].sort(), [1, 2]);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = TON.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class AnatomiehautTest(SimpleTestCase):
    databases = set()

    def test_das_stueck_folgt_der_haut_und_laesst_sich_zurueckholen(self):
        skript = ATTRAPPEN + """
const { Anatomiehaut: A } = await import(MODUL);

// Körper: ein Netz, drei Punkte nahe dem Stück und einer weit weg, Gruppe `Legs` mit einfarbiger Karte (Hautton rgb).
const koerper = (rgb) => ({ uuid: 'k' + rgb.join(','),
    geometry: { attributes: { position: attribut([0, 0, 0, 0.01, 0, 0, 0, 0.01, 0, 1, 1, 1], 3), uv: attribut([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], 2) },
                index: { getX: i => [0, 1, 2, 1, 2, 3][i] }, groups: [{ start: 0, count: 6, materialIndex: 0 }] },
    material: [{ userData: { gruppe: 'Legs' }, map: karte(rgb), color: farbe(1, 1, 1) }] });
// Stück mit Hauttiefe: ein Material mit eigener Karte `rgb` (oder ohne Bild), alle Punkte in der Nähe des Körperpunkts.
const stueck = (rgb) => {
    const m = { userData: {}, map: rgb ? karte(rgb) : { userData: {} }, color: farbe(1, 1, 1), needsUpdate: false };
    return { uuid: 's1', userData: { hautTiefe: 0.03 }, material: m,
             geometry: { attributes: { position: attribut([0, 0, 0, 0.02, 0.02, 0.02], 3), uv: attribut([0.5, 0.5, 0.5, 0.5], 2) } },
             traverse(f) { f(this); } };
};
const figur = (haut, eigenRgb, hautRgb) => ({ haut, bodyMesh: koerper(hautRgb), clothMeshes: { 'daz_anatomie_frau/0': stueck(eigenRgb) },
                                               kleidung: { daz_anatomie_frau: { variante: 'daz_anatomie_frau_ursula', farbe: null, gruppenfarben: {} } } });
const m = (inst) => inst.clothMeshes['daz_anatomie_frau/0'].material;
const HELL = [183, 125, 109], DUNKEL = [115, 81, 62], DAMIRA = [202, 145, 119], WEISS = [255, 235, 225];

// 4. dunkle Haut, helles Stück
let inst = figur('G9 Feminine Skin 04 MAT', WEISS, DUNKEL);
const alteKarte = m(inst).map;
pruefe('fertig', A.anwenden(inst), true);
pruefe('Karte weg', m(inst).map, null);
pruefe('Farbe = Hautton', rund([m(inst).color.r, m(inst).color.g, m(inst).color.b]), rund(DUNKEL.map(lin)));
pruefe('Ablage hält die Karte', m(inst).userData.anatomieHaut.karte === alteKarte, true);
pruefe('idempotent', A.anwenden(inst) && m(inst).map === null && m(inst).userData.anatomieHaut.karte === alteKarte, true);

// 5. passende Haut: das Stück bleibt
inst = figur('mbolesia:x', HELL, DAMIRA);
const bleibt = m(inst).map;
A.anwenden(inst);
pruefe('passt: Karte bleibt', m(inst).map === bleibt, true);
pruefe('passt: Farbe bleibt', [m(inst).color.r, m(inst).color.g, m(inst).color.b], [1, 1, 1]);
pruefe('passt: keine Ablage', m(inst).userData.anatomieHaut, undefined);

// 6. Rundreise: Haut zurück auf leer → die eigene Karte (Genitalvariante) ist wieder da; eine eigene Farbe ändert daran nichts
inst = figur('G9 Feminine Skin 04 MAT', WEISS, DUNKEL);
const vorher = m(inst).map;
A.anwenden(inst);
inst.haut = '';
A.anwenden(inst);
pruefe('zurück: Karte', m(inst).map === vorher, true);
pruefe('zurück: Farbe', [m(inst).color.r, m(inst).color.g, m(inst).color.b], [1, 1, 1]);
pruefe('zurück: Ablage weg', m(inst).userData.anatomieHaut, undefined);
inst.kleidung.daz_anatomie_frau.farbe = '#ffffff';
A.anwenden(inst);
pruefe('eigene Farbe: Karte bleibt', m(inst).map === vorher && m(inst).userData.anatomieHaut === undefined, true);

// 7. eigene Farbe gilt vor der Haut; Bild noch nicht da → nicht fertig, nichts geändert
inst = figur('G9 Feminine Skin 04 MAT', WEISS, DUNKEL);
inst.kleidung.daz_anatomie_frau.farbe = '#ff0000';
const eigene = m(inst).map;
A.anwenden(inst);
pruefe('eigene Farbe: Karte bleibt', m(inst).map === eigene, true);
inst = figur('G9 Feminine Skin 04 MAT', null, DUNKEL);
const ohneBild = m(inst).map;
pruefe('ohne Bild nicht fertig', A.anwenden(inst), false);
pruefe('ohne Bild unverändert', m(inst).map === ohneBild && m(inst).userData.anatomieHaut === undefined, true);

// 8. die eigene Karte kommt nach dem Umstellen an
inst = figur('G9 Feminine Skin 04 MAT', WEISS, DUNKEL);
A.anwenden(inst);
const spaet = karte(WEISS);
m(inst).map = spaet;                                   // `Genesis9netz.texturen` hängt das Bild nachträglich ein
pruefe('spät: wieder fertig', A.anwenden(inst), true);
pruefe('spät: Karte wieder weg', m(inst).map, null);
pruefe('spät: Ablage hat die neue', m(inst).userData.anatomieHaut.karte === spaet, true);

// 9. Stand und nachziehen
inst = figur('', WEISS, DUNKEL);
const s1 = A.stand(inst);
inst.haut = 'G9 Feminine Skin 04 MAT';
pruefe('Stand wechselt mit der Haut', A.stand(inst) !== s1, true);
const s2 = A.stand(inst);
inst.bodyMesh = koerper(HELL);       // ein anderes Netz: andere Kennung (mit `DUNKEL` wäre es dieselbe wie vorher)
pruefe('Stand wechselt mit dem Körper', A.stand(inst) !== s2, true);
pruefe('ohne Anatomie-Stück nichts', A.nachziehen({ clothMeshes: { 'shirt/0': { userData: {} } }, kleidung: {} }), null);
pruefe('ohne inst nichts', A.nachziehen(undefined), null);

// 10. mit Farbkarte der Haut folgt das Stück jeder Haut — auch einer passenden (HELL auf DAMIRA bliebe ohne Karten, Fall 5)
console.warn = () => {};      // die Rechnung läuft asynchron gegen Attrappen ohne Index und meldet sich beim Scheitern; hier zählt nur der Anstoß
const mitKarten = (hautRgb) => {
    const i = figur('G9 Feminine Skin 01 MAT', HELL, hautRgb);
    for (const mat of i.bodyMesh.material) { mat.map.isTexture = true; mat.map.uuid = 'karte' + hautRgb.join(','); }
    i.clothMeshes['daz_anatomie_frau/0'].geometry.uuid = 'g1';
    return i;
};
inst = mitKarten(DAMIRA);
const eigeneKarte = m(inst).map;
A.anwenden(inst);
pruefe('Karten: eigene Karte weg', m(inst).map, null);
pruefe('Karten: Ablage hält sie', m(inst).userData.anatomieHaut.karte === eigeneKarte, true);
const netz = inst.clothMeshes['daz_anatomie_frau/0'];
pruefe('Karten: Rechnung angestoßen', netz.userData.anatomieBackt, 'g1|karte202,145,119/-/-');
const anderes = mitKarten(DUNKEL);
A.anwenden(anderes);
pruefe('andere Haut, anderer Schlüssel', anderes.clothMeshes['daz_anatomie_frau/0'].userData.anatomieBackt, 'g1|karte115,81,62/-/-');

// 11. Katalog-Haut (`haut` leer): ohne eigene Farbkarte folgt das Stück dem Körper (Matt0, „Daz Anatomie Mann"), mit eigener bleibt sie (Damira, Ursula1)
inst = mitKarten(DUNKEL);
inst.haut = '';
m(inst).map = null;
m(inst).color.setRGB(0.35, 0.18, 0.13);
pruefe('ohne Karte: fertig', A.anwenden(inst), true);
pruefe('ohne Karte: Ablage angelegt', m(inst).userData.anatomieHaut.karte, null);
pruefe('ohne Karte: Rechnung angestoßen', inst.clothMeshes['daz_anatomie_frau/0'].userData.anatomieBackt, 'g1|karte115,81,62/-/-');
inst = mitKarten(DUNKEL);
inst.haut = '';
const mitEigener = m(inst).map;
A.anwenden(inst);
pruefe('eigene Karte: bleibt, keine Ablage', m(inst).map === mitEigener && m(inst).userData.anatomieHaut === undefined, true);
pruefe('eigene Karte: Farbe bleibt', [m(inst).color.r, m(inst).color.g, m(inst).color.b], [1, 1, 1]);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = HAUT.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
