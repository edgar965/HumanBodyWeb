# -*- coding: utf-8 -*-
u"""`Kleiderknochen`: Haar und freie Stoffteile folgen einer neuen Pose über ihre Knochen (17.10.2026).

WARUM (Edgar: „posen dauern irrsinnig lange, das sollte doch in 1 s gehen" — „mach erst …
Sofortschau"): Die Kleidervorschau nahm nur Stoffpunkte mit Oberflächenbindung mit; das Haar schwebte bei
„03 Laying Back" 1,8 s nach dem Klick noch an der alten Kopfstelle. Jetzt folgt alles ohne Bindung (und
der ungebundene Anteil `1 − mischung`) seinen Knochen: je Knochen `neu · alt⁻¹`, gemischt mit den
Hautgewichten. Im Chrome gemessen (fünf Stücke, „18 Defending"): nach dem Körper-Neubau Haar 0,0 mm,
Shirt 9,2, Boxershorts 7,3, Stiefel 5,8 mm von der genauen Lage — vorher Haar 28–40 mm (Achsen aus den
Gelenken), ohne Vorschau 434 mm.

1. Matrizen (spaltenweise wie Three.js): `umkehren` · Matrix = Einheit, `mal` stimmt.
2. `lagen` liest die BINDELAGE (`boneInverses` umgekehrt), nicht die gerade gedrehten Knochen;
   `wege` = neu · alt⁻¹.
3. `haeuten`: gemischte Bewegung je Punkt, `anteil` teilt sie, ein Knochen ohne Weg bleibt stehen,
   ohne Gewicht nichts.
4. `ausServer`: ein Knochen ohne eigenen Weg nimmt den seines Vorfahren.
5. `Kleidervorschau.folgen` mit `exakt`: ein Haar ohne Bindung folgt; ein gebundener Punkt mit
   `mischung` 0,5 bekommt halb Oberfläche, halb Knochen. Ohne Knochen bleibt alles wie vor dem
   17.10.2026 (`test_js_kleidervorschau`).

Sabotage-Gegenprobe (nicht gefahren): in `haeuten` das `/ summe` streichen → Fall 3 rot; in `lagen` die
Umkehrung weglassen → Fall 2 rot. Tests geschrieben, nicht gelaufen (nur auf Ansage).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

# Einstieg ist die Kleidervorschau: `Webmodul` spiegelt nur, was der Einstieg importiert — sie zieht
# `kleiderknochen.js` und `protokoll.js` mit.
MODUL = Jsmodul('gemeinsam', 'kleidervorschau.js')

SKRIPT = """
const { Kleidervorschau } = await import(MODUL);
const { Kleiderknochen: K } = await import(new URL('./kleiderknochen.js', MODUL).href);
const { Protokoll } = await import(new URL('./protokoll.js', MODUL).href);
Protokoll.debug = () => {};
const nah = (was, ist, soll, d = 1e-9) => {
    if (Math.abs(ist - soll) > d) throw new Error(was + ': ' + ist + ' statt ' + soll);
};
// Spaltenweise 4×4: Drehung um z (Grad), Verschiebung t, gleichmäßige Skalierung s.
const matrix = (grad, t = [0, 0, 0], s = 1) => {
    const w = grad * Math.PI / 180, c = Math.cos(w) * s, n = Math.sin(w) * s;
    return [c, n, 0, 0, -n, c, 0, 0, 0, 0, s, 0, t[0], t[1], t[2], 1];
};
const anwenden = (m, p) => [m[0] * p[0] + m[4] * p[1] + m[8] * p[2] + m[12],
                            m[1] * p[0] + m[5] * p[1] + m[9] * p[2] + m[13],
                            m[2] * p[0] + m[6] * p[1] + m[10] * p[2] + m[14]];

// 1. Matrizen
{
    const a = matrix(37, [0.3, -1.2, 2], 1.5);
    const e = K.mal(a, K.umkehren(a));
    for (let i = 0; i < 16; i++) nah('Einheit ' + i, e[i], [0, 5, 10, 15].includes(i) ? 1 : 0);
    const b = matrix(90, [1, 0, 0]);
    const ab = K.mal(a, b), p = [0.2, 0.4, -0.1];
    const soll = anwenden(a, anwenden(b, p)), ist = anwenden(ab, p);
    for (let i = 0; i < 3; i++) nah('mal ' + i, ist[i], soll[i]);
}

// 2. lagen aus der Bindelage, wege = neu · alt⁻¹
const figur = (lagen) => ({ skelett: {
    // `matrixWorld`: gerade gedreht (Vorschau, Animation) — zählt nicht
    bones: lagen.map(([name]) => ({ name, isBone: true, matrixWorld: { elements: matrix(123) } })),
    skeleton: { boneInverses: lagen.map(([, m]) => ({ elements: K.umkehren(m) })) } } });
{
    const alt = figur([['kopf', matrix(0, [0, 1.6, 0])]]);
    const neu = figur([['kopf', matrix(90, [0.5, 1.2, 0])]]);
    const lagen = K.lagen(alt);
    nah('Bindelage', lagen.get('kopf')[13], 1.6);
    const wege = K.wege(lagen, neu);
    const p = anwenden(wege.get('kopf'), [0.1, 1.7, 0]);    // 10 cm rechts, 10 cm über dem alten Kopfgelenk
    nah('Weg x', p[0], 0.5 - 0.1); nah('Weg y', p[1], 1.2 + 0.1); nah('Weg z', p[2], 0);
    pruefe('ohne gemerkte Lagen', K.wege(null, neu), null);
    pruefe('ohne Skelett', K.lagen({}), null);
}

// 3. haeuten
const netz = (punkte, index, gewicht, namen) => ({
    skeleton: { bones: namen.map(name => ({ name })) },
    geometry: { boundingSphere: 'alt', boundingBox: 'alt', attributes: {
        position: { array: Float32Array.from(punkte), count: punkte.length / 3, needsUpdate: false },
        skinIndex: { array: Float32Array.from(index) },
        skinWeight: { array: Float32Array.from(gewicht) } } } });
{
    const wege = new Map([['a', matrix(0, [1, 0, 0])], ['b', matrix(0, [0, 2, 0])]]);
    const n = netz([0, 0, 0, 0, 0, 0, 5, 5, 5, 7, 7, 7],
                   [0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                   [0.5, 0.5, 0, 0, 0.5, 0.5, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], ['a', 'b', 'ohne']);
    const bewegt = K.haeuten(n, wege, (i) => (i === 1 ? 0.5 : 1));
    const p = Array.from(n.geometry.attributes.position.array);
    nah('gemischt x', p[0], 0.5); nah('gemischt y', p[1], 1);
    nah('Anteil halb x', p[3], 0.25); nah('Anteil halb y', p[4], 0.5);
    pruefe('Knochen ohne Weg bleibt', p.slice(6, 9), [5, 5, 5]);
    pruefe('ohne Gewicht bleibt', p.slice(9, 12), [7, 7, 7]);
    pruefe('Zahl (der Knochen ohne Weg zählt mit)', bewegt, 3);
    pruefe('Kugel neu', n.geometry.boundingSphere, null);
    pruefe('ohne Wege', K.haeuten(n, null), 0);
}

// 4. ausServer: Vorfahren
{
    const wurzel = { name: 'head', isBone: true, parent: { isBone: false } };
    const zopf = { name: 'zopf1', isBone: true, parent: wurzel };
    const ende = { name: 'zopf1_end', isBone: true, parent: zopf };
    const aus = K.ausServer({ head: matrix(10) }, { skelett: { bones: [wurzel, zopf, ende] } });
    pruefe('Zopf nimmt den Kopf', aus.get('zopf1'), aus.get('head'));
    pruefe('Ende nimmt den Kopf', aus.get('zopf1_end'), aus.get('head'));
    pruefe('ohne Wege', K.ausServer(null, { skelett: { bones: [wurzel] } }), null);
}

// 5. Kleidervorschau mit exakten Wegen
{
    const kopf = { name: 'head', isBone: true, parent: { isBone: false } };
    const weg = matrix(0, [0, -0.5, 0]);                         // die Figur legt sich: alles 50 cm tiefer
    const koerper = Float32Array.from([0, -0.5, 0, 1, -0.5, 0, 0, 0.5, 0]);
    const inst = { stufen: 1, _lauf: 5, clothMeshes: {},
                   skelett: { bones: [kopf], skeleton: { boneInverses: [{ elements: matrix(0) }] } },
                   bodyMesh: { geometry: { attributes: { position: { array: koerper } } } } };
    const haar = netz([0, 1.7, 0], [0, 0, 0, 0], [1, 0, 0, 0], ['head']);
    haar.userData = {}; haar.geometry.userData = {};
    const hemd = netz([5, 5, 5], [0, 0, 0, 0], [1, 0, 0, 0], ['head']);
    hemd.userData = {}; hemd.geometry.userData = { bindung: { stufen: 1 } };
    Object.assign(hemd.geometry.attributes, { bindung: { array: Float32Array.from([0, 1, 2]) },
        bary: { array: Float32Array.from([1, 0, 0]) }, mischung: { array: Float32Array.from([0.5]) } });
    inst.clothMeshes = { haar, hemd };
    const vorher = { punkte: Float32Array.from([0, 0, 0, 1, 0, 0, 0, 1, 0]), stufen: 1,
                     knochen: null, exakt: { head: weg } };
    const n = Kleidervorschau.folgen(inst, vorher);
    pruefe('zwei Stücke', n, 2);
    nah('Haar folgt', haar.geometry.attributes.position.array[1], 1.2, 1e-6);
    // Hemd: halb Oberfläche (v0: −0,5), halb Knochen (−0,5) → −0,5 insgesamt.
    nah('Hemd halb/halb', hemd.geometry.attributes.position.array[1], 4.5, 1e-6);
}
console.log(JSON.stringify({ ok: true }));
"""


class KleiderknochenTest(SimpleTestCase):
    databases = set()

    def test_stuecke_ohne_bindung_folgen_ihren_knochen(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))
