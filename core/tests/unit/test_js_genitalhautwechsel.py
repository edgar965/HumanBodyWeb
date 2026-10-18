"""Hautwechsel → das Genital bekommt ihn mit (18.10.2026), geprüft in Node.

Edgar, 18.10.2026: „schreibe tests, die genau das überprüfen - wechsel der Haut, dann überprüfen, ob das Genital auch den Wechsel mitkriegt" — nachdem der Fehler
„die Textur der Genitalien kommt nicht von der Textur des Körpers" zum dritten Mal zurück war (an diesem Tag zweimal: einmal durch eine Rücknahme in
`Anatomiehaut.anwenden`, einmal, weil die Hautebenen nur am Körper lagen — DamiraAlt mit Hautton und Sommersprossen).

`Anatomiehaut` (Karten der Haut, `anatomiehaut.js`):
1. Haut A: das Stück (mit eigener Karte, Variante Damira) rechnet seine Karten aus A (`anatomieBackt` = Schlüssel aus Geometrie und Karte von A), bis dahin flach im Ton von A.
2. Bake A fertig → das Stück zeigt genau die aus A gerechnete Karte.
3. WECHSEL auf Haut B (neues Körpernetz, andere Karte): neue Rechnung für B, die Karte aus A ist weg, bis dahin flach im Ton von B.
4. Bake B fertig → die Karte aus B.
5. Zurück auf die Katalog-Haut (`haut` leer): die eigene Karte der Variante (Damira) kommt zurück, keine neue Rechnung — Edgar 18.10.2026, 23:11: „Damira0 ist
   aktuell auch kaputt im Genital" (Katalog-Haut, gebacken). Bis dahin prüfte dieser Fall das Gegenteil.

`Genesis9hautebenenstueck` (Hautebenen auf dem Stück, `genesis9hautebenenstueck.js`):
6. Die Ziele der Hautebenen sind die Hautmaterialien des Körpers UND das Material des Stücks, das die Karten der Haut zeigt — mit dem Körpermaterial seines Bakes
   als Vorbild (`anatomieGebacken.vorbild`, nicht aufzählbar).
7. `uvHaut` je Punkt des Stücks = Kachel-UV am nächsten Punkt IM Hautdreieck der VORBILDgruppe (Gewichte der Ecken), durch die Kartenmatrix wie `vMapUv` (hier
   Versatz u − 1); ein näheres Dreieck eines anderen Materials zählt nicht. Der Shader des Stücks bekommt `HT_UV_HAUT`. (Bis 18.10.2026 abends die UV des nächsten
   HautPUNKTS: an DamiraAlt 218 verschiedene Werte auf 4.231 Stückpunkten, keine Sommersprossen auf dem Stück.)
8. WECHSEL der Haut (neues Körpernetz, andere UV): `uvHaut` wird neu gerechnet.
9. Zeigt das Stück seine eigene Karte (eigene Farbe gesetzt) oder ist noch nicht gebacken: kein Ziel.

Gelaufen 18.10.2026 auf Ansage: grün (Fall 5 damals mit dem Gegenteil; die neue Fassung ist nicht gelaufen). Sabotage-Gegenprobe gefahren: in
`Genesis9hautebenenstueck.ziele` die Stücke weggelassen → Fall 6 rot. Nicht gefahren: Karten-Kennung in `Anatomiekarten.schluessel` weg (Fall 3),
Körpernetz-Kennung im Schlüssel von `uvSetzen` weg (Fall 8).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from . import test_js_anatomiehaut as vorlage

HAUT = Jsmodul('gemeinsam', 'anatomiehaut.js')
EBENEN = Jsmodul('gemeinsam', 'genesis9hautebenenstueck.js')


class GenitalHautwechselTest(SimpleTestCase):
    databases = set()

    def test_hautwechsel_genital_bekommt_die_karten_der_neuen_haut(self):
        skript = vorlage.ATTRAPPEN + """
const { Anatomiehaut: A } = await import(MODUL);
console.warn = () => {};      // die Rechnung läuft asynchron gegen Attrappen und scheitert leise; hier zählen Anstoß und Anzeige
const DUNKEL = [115, 81, 62], HELL = [183, 125, 109], KATALOG = [202, 145, 119], WEISS = [255, 235, 225];
const koerper = (rgb, name) => ({ uuid: 'k' + name,
    geometry: { attributes: { position: attribut([0, 0, 0, 0.01, 0, 0, 0, 0.01, 0, 1, 1, 1], 3), uv: attribut([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], 2) },
                index: { getX: i => [0, 1, 2, 1, 2, 3][i] }, groups: [{ start: 0, count: 6, materialIndex: 0 }] },
    material: [{ userData: { gruppe: 'Legs' }, map: Object.assign(karte(rgb), { isTexture: true, uuid: 'karte' + name }), color: farbe(1, 1, 1) }] });
const eigeneKarte = karte(WEISS);
const netz = { uuid: 's1', userData: { hautTiefe: 0.03 }, material: { userData: {}, map: eigeneKarte, color: farbe(1, 1, 1), needsUpdate: false },
               geometry: { uuid: 'g1', attributes: { position: attribut([0, 0, 0, 0.02, 0.02, 0.02], 3), uv: attribut([0.5, 0.5, 0.5, 0.5], 2) } },
               traverse(f) { f(this); } };
const m = netz.material;
const ton = () => rund([m.color.r, m.color.g, m.color.b]);
const inst = { haut: 'Haut A', bodyMesh: koerper(DUNKEL, 'A'), clothMeshes: { 'daz_anatomie_frau/0': netz },
               kleidung: { daz_anatomie_frau: { variante: 'daz_anatomie_frau_damira', farbe: null, gruppenfarben: {} } } };
const fertig = (name) => {                     // der Bake für `name` ist fertig (wie `Anatomiebacken.anstossen` ablegt)
    const g = { map: { isTexture: true, uuid: 'gebacken' + name }, normalMap: null, roughnessMap: null, farbe: farbe(1, 1, 1), schluessel: 'g1|karte' + name + '/-/-' };
    netz.userData.anatomieBackt = null;
    netz.userData.anatomieGebacken = g;
    return g.map;
};

// 1. Haut A
A.anwenden(inst);
pruefe('A: Rechnung aus A', netz.userData.anatomieBackt, 'g1|karteA/-/-');
pruefe('A: eigene Karte weg', m.map, null);
pruefe('A: bis dahin flach im Ton von A', ton(), rund(DUNKEL.map(lin)));
// 2. Bake A fertig
const ausA = fertig('A');
A.anwenden(inst);
pruefe('A: zeigt die Karte aus A', m.map === ausA, true);
// 3. WECHSEL auf B
inst.haut = 'Haut B';
inst.bodyMesh = koerper(HELL, 'B');
A.anwenden(inst);
pruefe('B: neue Rechnung aus B', netz.userData.anatomieBackt, 'g1|karteB/-/-');
pruefe('B: Karte aus A ist weg', m.map === ausA, false);
pruefe('B: bis dahin flach im Ton von B', ton(), rund(HELL.map(lin)));
// 4. Bake B fertig
const ausB = fertig('B');
A.anwenden(inst);
pruefe('B: zeigt die Karte aus B', m.map === ausB, true);
// 5. zurück auf die Katalog-Haut
inst.haut = '';
inst.bodyMesh = koerper(KATALOG, 'Katalog');
A.anwenden(inst);
pruefe('Katalog: keine neue Rechnung', netz.userData.anatomieBackt, null);
pruefe('Katalog: die eigene Karte der Variante ist zurück', m.map === eigeneKarte, true);
pruefe('Katalog: Ablage weg', m.userData.anatomieHaut, undefined);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = HAUT.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_hautebenen_kommen_auf_das_genital_und_folgen_dem_hautwechsel(self):
        skript = """
const { Genesis9hautebenenstueck: H } = await import(MODUL);
const rund = (liste, n = 4) => liste.map(w => Math.round(w * 10 ** n) / 10 ** n);
class Attr { constructor(array, n) { this.array = array; this.itemSize = n; this.count = array.length / n; this.version = 0; } }
const matrix = (tx) => ({ elements: [1, 0, 0, 0, 1, 0, tx, 0, 1] });
const vorbild = { uuid: 'v', userData: { gruppe: 'Legs', kachel: 1003 }, map: { matrix: matrix(-1), updateMatrix() {} } };
const anderes = { uuid: 'a', userData: { gruppe: 'Body', kachel: 1002 }, map: { matrix: matrix(0), updateMatrix() {} } };
// Körper: Punkte 0–2 nahe am Stück (Dreieck 0, Vorbild), Punkt 3 fern; Dreieck 1 (Punkte 1, 2, 3) gehört dem anderen Material.
const koerpernetz = (uuid, uv) => ({ uuid, userData: {},
    attributes: { position: new Attr(Float32Array.from([0, 0, 0, 0.01, 0, 0, 0, 0.01, 0, 0.5, 0.5, 0.5]), 3), uv: new Attr(Float32Array.from(uv), 2) },
    index: { array: Uint32Array.from([0, 1, 2, 1, 2, 3]) }, groups: [{ start: 0, count: 3, materialIndex: 0 }, { start: 3, count: 3, materialIndex: 1 }] });
const st = { uuid: 'g1', userData: {}, attributes: { position: new Attr(Float32Array.from([0.001, 0, 0.002, 0.009, 0.001, 0, 0, 0.011, 0.001]), 3) },
             setAttribute(name, a) { this.attributes[name] = a; } };
const gebacken = { isTexture: true, uuid: 'gebackenA' };
const m = { map: gebacken, userData: { anatomieHaut: { hautKarte: gebacken } } };
const netz = { userData: { hautTiefe: 0.03, anatomieGebacken: Object.defineProperty({ schluessel: 'x' }, 'vorbild', { value: vorbild, enumerable: false }) },
               material: m, geometry: st, traverse(f) { f(this); } };
const inst = { bodyMesh: { geometry: koerpernetz('k1', [1.2, 0.3, 1.4, 0.3, 1.2, 0.6, 1.9, 0.9]), material: [vorbild, anderes] },
               clothMeshes: { 'daz_anatomie_frau/0': netz }, kleidung: {} };

// 6. Ziele: Körper (v = m) und das Stück mit dem Vorbild seines Bakes
const ziele = H.ziele(inst, [vorbild, anderes]);
pruefe('Ziele', ziele.map(z => [z.m === z.v, z.v.uuid]), [[true, 'v'], [true, 'a'], [false, 'v']]);
pruefe('Vorbild nicht in JSON', JSON.stringify(netz.userData.anatomieGebacken).includes('kachel'), false);
// 7. uvHaut: Kachel-UV am nächsten Punkt IM Hautdreieck der Vorbildgruppe (Versatz u − 1): Punkt 0 auf der Kante a–b (b 0,1),
//    Punkt 1 im Dreieck (b 0,9, c 0,1), Punkt 2 jenseits der Ecke c → c.
pruefe('uvHaut', rund([...st.attributes.uvHaut.array]), rund([0.22, 0.3, 0.38, 0.33, 0.2, 0.6]));
pruefe('Shader liest uvHaut', 'HT_UV_HAUT' in m.defines, true);
// 8. WECHSEL der Haut: neues Körpernetz, andere UV
inst.bodyMesh = { geometry: koerpernetz('k2', [1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.9, 0.9]), material: [vorbild, anderes] };
pruefe('Wechsel: Stück bleibt Ziel', H.ziele(inst, []).length, 1);
pruefe('Wechsel: uvHaut neu', rund([...st.attributes.uvHaut.array]), rund([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]));
// 9. eigene Karte (eigene Farbe gesetzt) bzw. noch nicht gebacken: kein Ziel
m.map = { uuid: 'eigen' };
pruefe('eigene Karte: kein Ziel', H.ziele(inst, []).length, 0);
m.map = gebacken;
netz.userData.anatomieGebacken = { schluessel: 'x' };
pruefe('ohne Bake: kein Ziel', H.ziele(inst, []).length, 0);
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = EBENEN.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
