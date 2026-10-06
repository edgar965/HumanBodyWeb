# -*- coding: utf-8 -*-
"""`Hautporen`: feine Hautzeichnung (Normal + AO aus HumanShaders) im Shader der Haut, einstellbar im Bereich „Haut“.

WARUM (Edgar, 06.10.2026: „übernimm die Poren und die Augen, wie kann man die im UI einstellen“). Geprüft in Node mit Attrappen statt Three.js (das Laden der
Karte ist ersetzt):

1. `anwenden` hängt den Eingriff an Haut UND Censor (Gruppen 0 und 1), nicht an die Wimpern; beide tragen DIESELBE Eingriffsfunktion mit den Uniforms
   Stärke, Fliesen (Dichte / `KACHEL_M`), AO-Mittel der Karte und der Karte selbst.
2. Ein zweiter Aufruf stellt nur die Uniforms nach — dieselbe Funktion, kein neuer Eingriff (kein neuer Shader).
3. Leere Auswahl nimmt den Eingriff von beiden Materialien (und den Programmschlüssel) wieder ab.
4. Ein überholter Lauf setzt nichts mehr: Lädt die Karte noch, wenn die Auswahl auf „Keine“ springt, bleibt die Haut ohne Eingriff (Befund am Bild: nach „Keine“
   standen die Poren weiter, weil die Fortsetzung des ersten Laufs sie wieder anhängte).
5. `patchen` gibt Lage und Normale der Ruhepose und die Achsen des Skinnings durch, deklariert die Uniforms und stört Normale und AO an den Stellen der Standard-Shader
   (`color_fragment`, `normal_fragment_maps`); die Einbindungen selbst bleiben stehen.
6. Die Liste `WAHL` und die Dateien: jede Kennung steht im Auswahlfeld der Seite und als Datei in `static/img/humanshaders/`. `Koerperdetails.aus` nimmt nur Kennungen aus der
   Liste, klemmt Stärke (0..1) und Dichte (0,25..3).

Sabotage-Gegenprobe: `if (Hautporen._lauf.get(netz) !== lauf) return false;` weg → Fall 4 rot.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautporen.js')

SKRIPT = """
const { Hautporen: H } = await import(MODUL);
const { Shaderpatch } = await import(new URL('./shaderpatch.js', MODUL).href);
const material = () => ({ clone() { return material(); } });
const netz = () => ({ material: [material(), material(), material()] });
const rund = (x) => Math.round(x * 1000) / 1000;
H.laden = async (name) => ({ karte: name });

const n = netz();
pruefe('gesetzt', await H.anwenden(n, { haut_poren: 'poren_2', haut_poren_deckkraft: 0.8, haut_poren_dichte: 2 }), true);
pruefe('an haut und censor', [0, 1, 2].map(g => Shaderpatch.hat(n.material[g], 'hautporen')), [true, true, false]);
const e0 = Shaderpatch.eingriff(n.material[0], 'hautporen');
pruefe('dieselbe funktion', Shaderpatch.eingriff(n.material[1], 'hautporen') === e0, true);
const u = e0.uniforms;
pruefe('uniforms', [u.porenKarte.value.karte, u.porenStaerke.value, rund(u.porenFliesen.value), u.porenAoMittel.value], ['poren_2', 0.8, 250, 0.515]);
pruefe('schluessel', n.material[0].customProgramCacheKey(), 'hautporen');

await H.anwenden(n, { haut_poren: 'poren_3', haut_poren_deckkraft: 0.2, haut_poren_dichte: 0.5 });
pruefe('nur nachgestellt', Shaderpatch.eingriff(n.material[0], 'hautporen') === e0, true);
pruefe('neue werte', [u.porenKarte.value.karte, u.porenStaerke.value, rund(u.porenFliesen.value), u.porenAoMittel.value], ['poren_3', 0.2, 62.5, 0.478]);

pruefe('weg', await H.anwenden(n, { haut_poren: '' }), false);
pruefe('abgenommen', [0, 1].map(g => Shaderpatch.hat(n.material[g], 'hautporen')), [false, false]);
pruefe('schluessel leer', n.material[0].customProgramCacheKey(), '');
pruefe('unbekannt', await H.anwenden(n, { haut_poren: '../x' }), false);
pruefe('ohne materialliste', await H.anwenden({ material: material() }, { haut_poren: 'poren_1' }), false);

// Überholter Lauf: die Karte lädt noch, inzwischen steht die Auswahl auf „Keine“.
const m = netz();
let frei;
H.laden = () => new Promise(r => { frei = r; });
const alt = H.anwenden(m, { haut_poren: 'poren_1', haut_poren_deckkraft: 0.5, haut_poren_dichte: 1 });
H.laden = async (name) => ({ karte: name });
await H.anwenden(m, { haut_poren: '' });
frei({ karte: 'poren_1' });
pruefe('lauf ueberholt', await alt, false);
pruefe('bleibt ohne', [0, 1].map(g => Shaderpatch.hat(m.material[g], 'hautporen')), [false, false]);

// Der Shader
const shader = {
    uniforms: {},
    vertexShader: 'void main() {\\n#include <beginnormal_vertex>\\n#include <begin_vertex>\\n#include <skinnormal_vertex>\\n}',
    fragmentShader: 'void main() {\\n#include <color_fragment>\\n#include <normal_fragment_maps>\\n}',
};
const p = netz();
await H.anwenden(p, { haut_poren: 'poren_1', haut_poren_deckkraft: 0.5, haut_poren_dichte: 1 });
p.material[0].onBeforeCompile(shader);
pruefe('uniforms am shader', Object.keys(shader.uniforms).sort(), ['porenAoMittel', 'porenFliesen', 'porenKarte', 'porenStaerke']);
const v = shader.vertexShader, f = shader.fragmentShader;
pruefe('vertex', [v.includes('vPorenN = objectNormal;'), v.includes('vPorenP = transformed;'), v.includes('mat3( normalMatrix ) * mat3( skinMatrix )'), v.includes('vPorenZ = porenM[2];')], [true, true, true, true]);
pruefe('fragment deklariert', [f.includes('uniform sampler2D porenKarte;'), f.includes('varying vec3 vPorenX;')], [true, true]);
pruefe('fragment stoert', [f.includes('diffuseColor.rgb *= mix('), f.includes('normal = normalize( normal + porenV')], [true, true]);
pruefe('includes bleiben', [f.includes('#include <color_fragment>'), f.includes('#include <normal_fragment_maps>'), v.includes('#include <skinnormal_vertex>')], [true, true, true]);

// Liste und Koerperdetails
const { Koerperdetails: K } = await import(new URL('./koerperdetails.js', MODUL).href);
const d = K.aus({ details: { haut_poren: 'poren_2', haut_poren_deckkraft: 7, haut_poren_dichte: 9 } });
pruefe('aus: gueltig, geklemmt', [d.haut_poren, d.haut_poren_deckkraft, d.haut_poren_dichte], ['poren_2', 1, 3]);
const x = K.aus({ details: { haut_poren: 'poren_9', haut_poren_dichte: 0.01 } });
pruefe('aus: unbekannt und zu klein', [x.haut_poren, x.haut_poren_dichte], ['', 0.25]);
pruefe('vorgabe', [K.VORGABE.haut_poren, K.VORGABE.haut_poren_deckkraft, K.VORGABE.haut_poren_dichte], ['', 0.5, 1]);
console.log(JSON.stringify({ ok: true, wahl: H.WAHL.map(([w]) => w).filter(Boolean) }));
"""


class HautporenTest(SimpleTestCase):
    def test_anwenden_nachstellen_abnehmen_und_der_shader(self):
        ergebnis = MODUL.laufen(SKRIPT)
        self.assertTrue(ergebnis.get('ok'))
        self.assertEqual(ergebnis['wahl'], ['poren_1', 'poren_2', 'poren_3'])

    def test_jede_kennung_steht_auf_der_seite_und_als_datei_da(self):
        wurzel = Path(settings.BASE_DIR)
        vorlage = (wurzel / 'templates' / '_szene_details.html').read_text(encoding='utf-8')
        bereiche = (wurzel / 'static' / 'viewer' / 'charakter' / 'detailbereiche.js').read_text(encoding='utf-8')
        for kennung in MODUL.laufen(SKRIPT)['wahl']:
            self.assertIn(f'<option value="{kennung}">', vorlage, kennung)
            self.assertTrue((wurzel / 'static' / 'img' / 'humanshaders' / f'{kennung}.png').is_file(), kennung)
        for feld in ('haut_poren', 'haut_poren_deckkraft', 'haut_poren_dichte'):
            self.assertIn(f"'{feld}'", bereiche, feld)
        self.assertTrue((wurzel / 'static' / 'img' / 'humanshaders' / 'LIZENZ.txt').is_file())
