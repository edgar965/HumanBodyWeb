# -*- coding: utf-8 -*-
"""`Augentextur`: Iris und Augapfel aus Karten (HumanShaders), einstellbar im Bereich „Augen · Wimpern“.

WARUM (Edgar, 06.10.2026: „übernimm die Poren und die Augen, wie kann man die im UI einstellen, neue Skins / Augen?“). Geprüft in Node mit Attrappen statt
Three.js (das Laden der Karten ist ersetzt):

1. `uv` bildet je Auge (Seite von x) planar ab: Mitte = Schwerpunkt der Iris, 2 × größter Abstand der Sklera = 1. Iris und Sklera teilen Ecken (am Basisnetz 32) —
   eine geteilte Ecke bekommt EINE UV; Sklerarand liegt bei 0/1, die Iris innen. Ohne Auge (keine Iris oder keine Sklera) bleibt 0 Ecken.
2. `anwenden` setzt dieselbe Farbkarte und dieselbe Normalkarte auf Sklera (4) und Iris (6), die Normalstärke aus `augen_relief` (· `RELIEF_MAX`), macht die Farbe weiß,
   wenn sie die Vorgabe trägt, und lässt eine eigene Farbe stehen; die Hornhaut (5) wird klarer und merkt sich ihren alten Wert.
3. Leere Auswahl nimmt Karten und Normale wieder weg und stellt die Hornhaut zurück.
4. Ohne UV-Attribut, ohne Topologie oder ohne Augen: false, nichts gesetzt.
5. Ein überholter Lauf (Karte lädt noch, die Auswahl springt auf „Keine“) setzt nichts mehr — wie bei `Hautporen`.
6. Die Liste `WAHL` und die Dateien: jede Irisfarbe steht im Auswahlfeld und als `auge_<farbe>.jpg` da, dazu `auge_normal.png`; `Koerperdetails.aus` nimmt nur Kennungen aus der
   Liste und klemmt `augen_relief` auf 0..1.

Sabotage-Gegenprobe: `if (Augentextur._lauf.get(netz) !== lauf) return false;` weg → Fall 5 rot.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'augentextur.js')

SKRIPT = """
const { Augentextur: A } = await import(MODUL);
const rund = (x) => Math.round(x * 1000) / 1000;

// 1. UV: zwei Augen (x < 0 und x > 0), je 4 Irisecken (Radius 5 mm) und 4 Skleraecken (Radius 15 mm); die Iris-Aussenecken sind zugleich Skleraecken (geteilt).
const punkte = [];
const auge = (cx, cy, ersteEcke) => {
    for (const [dx, dy] of [[0.005, 0], [-0.005, 0], [0, 0.005], [0, -0.005]]) punkte.push(cx + dx, cy + dy, 0.1);              // 0..3: Iris (geteilt)
    for (const [dx, dy] of [[0.015, 0], [-0.015, 0], [0, 0.015], [0, -0.015]]) punkte.push(cx + dx, cy + dy, 0.0);            // 4..7: nur Sklera
    return ersteEcke;
};
auge(-0.03, 1.6, 0); auge(0.03, 1.6, 8);
const p = Float32Array.from(punkte);
const iris = [0, 1, 2, 3, 8, 9, 10, 11];
const sklera = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
const index = Uint32Array.from([...iris, ...sklera]);
const gruppen = [{ materialIndex: 6, start: 0, count: iris.length }, { materialIndex: 4, start: iris.length, count: sklera.length }];
const uv = new Float32Array(16 * 2).fill(-1);
pruefe('gesetzt', A.uv(uv, index, gruppen, p), 16);
pruefe('iris rechts', [rund(uv[2 * 8]), rund(uv[2 * 8 + 1])], [rund(0.5 + 0.005 / 0.03), 0.5]);
pruefe('sklerarand rechts', [rund(uv[2 * 12]), rund(uv[2 * 12 + 1])], [1, 0.5]);
pruefe('sklerarand oben links', [rund(uv[2 * 6]), rund(uv[2 * 6 + 1])], [0.5, 1]);
pruefe('geteilte ecke eine uv', [rund(uv[2 * 1]), rund(uv[2 * 1 + 1])], [rund(0.5 - 0.005 / 0.03), 0.5]);
pruefe('ohne sklera', A.uv(new Float32Array(32), index, [{ materialIndex: 6, start: 0, count: iris.length }], p), 0);

// 2. anwenden
const farbe = () => ({ h: null, setRGB(r, g, b) { this.h = [r, g, b]; } });
const mat = (opacity) => ({ map: null, normalMap: null, color: farbe(), normalScale: { w: null, set(a, b) { this.w = [a, b]; } }, needsUpdate: false, opacity, userData: {} });
const netz = () => {
    const material = [0, 1, 2, 3, 4, 5, 6].map(() => mat(1)); material[5].opacity = 0.3;
    return { material, geometry: { attributes: { uv: { array: new Float32Array(32), needsUpdate: false } } } };
};
A.laden = async (name, farbig) => ({ name, farbig });
const n = netz();
const roh = { augen_textur: 'blau', augen_relief: 0.8, iris: '#4a7a9b', sklera: '#aabbcc' };
pruefe('gesetzt', await A.anwenden(n, roh, index, gruppen, p), true);
pruefe('uv uebernommen', n.geometry.attributes.uv.needsUpdate, true);
pruefe('karten', [n.material[4].map.name, n.material[6].map.name, n.material[4].map === n.material[6].map, n.material[6].normalMap.name], ['auge_blau', 'auge_blau', true, 'auge_normal']);
pruefe('farbkarte farbig, normale linear', [n.material[4].map.farbig, n.material[6].normalMap.farbig], [true, false]);
pruefe('relief', n.material[6].normalScale.w.map(rund), [rund(0.8 * A.RELIEF_MAX), rund(0.8 * A.RELIEF_MAX)]);
pruefe('vorgabefarbe weiss, eigene bleibt', [n.material[6].color.h, n.material[4].color.h], [[1, 1, 1], null]);
pruefe('hornhaut klar', n.material[5].opacity, A.HORNHAUT_DECKUNG);
pruefe('andere ohne karte', [n.material[0].map, n.material[5].map, n.material[3].map], [null, null, null]);

// 3. weg
pruefe('weg', await A.anwenden(n, { augen_textur: '' }, index, gruppen, p), false);
pruefe('karten weg', [n.material[4].map, n.material[6].map, n.material[6].normalMap], [null, null, null]);
pruefe('hornhaut zurueck', n.material[5].opacity, 0.3);
pruefe('weg ohne karten ist leer', A.entfernen(n.material), 0);

// 4. nichts zu tun
const ohneUv = netz(); delete ohneUv.geometry.attributes.uv;
pruefe('ohne uv', await A.anwenden(ohneUv, roh, index, gruppen, p), false);
pruefe('ohne topologie', await A.anwenden(netz(), roh, null, null, p), false);
pruefe('ohne augen', await A.anwenden({ material: [mat(1)] }, roh, index, gruppen, p), false);
pruefe('unbekannt', await A.anwenden(netz(), { augen_textur: 'violett' }, index, gruppen, p), false);

// 5. ueberholter Lauf
const m = netz();
let frei;
const offen = new Promise(r => { frei = r; });                       // EIN offenes Versprechen für beide Karten (Farbe und Normale)
A.laden = () => offen;
const alt = A.anwenden(m, roh, index, gruppen, p);
A.laden = async (name, farbig) => ({ name, farbig });
await A.anwenden(m, { augen_textur: '' }, index, gruppen, p);
frei({ name: 'auge_blau', farbig: true });
pruefe('lauf ueberholt', await alt, false);
pruefe('bleibt ohne', [m.material[4].map, m.material[6].map], [null, null]);

// 6. Liste und Koerperdetails
const { Koerperdetails: K } = await import(new URL('./koerperdetails.js', MODUL).href);
const d = K.aus({ details: { augen_textur: 'gruen', augen_relief: 5 } });
pruefe('aus: gueltig, geklemmt', [d.augen_textur, d.augen_relief], ['gruen', 1]);
pruefe('aus: unbekannt', K.aus({ details: { augen_textur: 'violett' } }).augen_textur, '');
pruefe('vorgabe', [K.VORGABE.augen_textur, K.VORGABE.augen_relief], ['', 0.7]);
console.log(JSON.stringify({ ok: true, wahl: A.WAHL.map(([w]) => w).filter(Boolean), normal: A.NORMALKARTE }));
"""


class AugentexturTest(SimpleTestCase):
    def test_uv_anwenden_abnehmen_und_ueberholte_laeufe(self):
        ergebnis = MODUL.laufen(SKRIPT)
        self.assertTrue(ergebnis.get('ok'))
        self.assertEqual(ergebnis['wahl'], ['braun', 'haselnuss', 'gruen', 'blau', 'grau'])

    def test_jede_irisfarbe_steht_auf_der_seite_und_als_datei_da(self):
        wurzel = Path(settings.BASE_DIR)
        vorlage = (wurzel / 'templates' / '_szene_details.html').read_text(encoding='utf-8')
        bereiche = (wurzel / 'static' / 'viewer' / 'charakter' / 'detailbereiche.js').read_text(encoding='utf-8')
        ergebnis = MODUL.laufen(SKRIPT)
        ordner = wurzel / 'static' / 'img' / 'humanshaders'
        for farbe in ergebnis['wahl']:
            self.assertIn(f'<option value="{farbe}">', vorlage, farbe)
            self.assertTrue((ordner / f'auge_{farbe}.jpg').is_file(), farbe)
        self.assertTrue((ordner / f'{ergebnis["normal"]}.png').is_file())
        for feld in ('augen_textur', 'augen_relief'):
            self.assertIn(f"'{feld}'", bereiche, feld)
