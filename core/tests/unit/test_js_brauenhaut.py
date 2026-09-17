# -*- coding: utf-8 -*-
u"""Brauenhaut und Brauenvorlagen (Node) und die Verdrahtung der Braue in der Haut.

WARUM (Edgar, 16.09.2026, Konzept A): Die Braue ist eine Zeichnung im
Hautshader, kein Objekt mehr. Hier ohne Browser:

1. `Brauenhaut.abfrage`: Detailfelder → Abfrage (mm-Felder aus Metern,
   gerundet, Farbe kodiert); gleiche Regler, gleiche Adresse; das Geschlecht
   aus der Körperart.
2. `Brauenhaut.patchen`: der Shader bekommt die Uniforms, das UV-Varying und
   die Mischung im Fenster; `anwenden` ohne Materialliste tut nichts.
3. `Brauenvorlagen`: eine Vorlage setzt ihre Felder, alles andere auf die
   Vorgabe; `erkennen` findet sie wieder und meldet eigene Werte als null.
4. Verdrahtung: das Modell ruft `Brauenhaut.anwenden`, nichts baut mehr
   `Augenbrauenbau`; die Albedo kommt ohne gemalte Brauen (`?brauen=ohne`);
   jedes `brauen_*`-Feld der Vorgabe hat einen Regler im Bereich Augenbrauen;
   der Bereich nennt die Vorlage.

Sabotage-Gegenprobe: in `Brauenhaut.abfrage` den Faktor 1000 der mm-Felder
weglassen → Fall 1 rot (`lage=0.01` statt `lage=10`).
"""
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'brauenhaut.js')
VORLAGEN = Jsmodul('gemeinsam', 'brauenvorlagen.js')
VIEWER = Jsmodul.VIEWER

SKRIPT = """
const { Brauenhaut: B } = await import(MODUL);
const gleich = (was, a, b) => {
    if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b); };
const details = { brauen: '#3a2a1e', brauen_staerke: 0.64, brauen_dicke: 1, brauen_dichte: 1.5,
                  brauen_bogen_laenge: 1, brauen_deckkraft: 0.8, brauen_lage: 0.01,
                  brauen_hoehe_innen: -0.0025, brauen_hoehe_aussen: 0, brauen_woelbung: 0.004,
                  haut: '', wimpern_laenge: 1 };
const a = B.abfrage(details, 'female', 3);
gleich('geschlecht', a.startsWith('geschlecht=female&f=3&'), true);
gleich('farbe', a.includes('farbe=%233a2a1e'), true);
gleich('haerchen', a.includes('haar_laenge=0.64'), true);
gleich('lage mm', a.includes('lage=10'), true);
gleich('hoehe innen mm', a.includes('hoehe_innen=-2.5'), true);
gleich('woelbung', a.includes('woelbung=4'), true);
gleich('deckkraft', a.includes('deckkraft=0.8'), true);
gleich('fremdes feld', a.includes('wimpern'), false);
gleich('gleiche adresse', B.adresse(details, 'female'), B.adresse({ ...details }, 'female'));
gleich('male', B.geschlecht('Male_Asian'), 'male');
gleich('female', B.geschlecht('Female_Caucasian'), 'female');
// 2. Shader
const shader = { uniforms: {}, vertexShader: 'void main(){\\n#include <begin_vertex>\\n}',
                 fragmentShader: 'void main(){\\n#include <color_fragment>\\n}' };
B.patchen(shader, { brauenKarte: { value: 'K' }, brauenFenster: { value: [0.38, 0.14, 0.62, 0.28] } });
gleich('uniform karte', shader.uniforms.brauenKarte.value, 'K');
gleich('varying', shader.vertexShader.includes('vBrauenUv = uv;'), true);
gleich('mischung', shader.fragmentShader.includes('mix(diffuseColor.rgb, braue.rgb, braue.a)'), true);
gleich('fenster', shader.fragmentShader.includes('brauenFenster.zw - brauenFenster.xy'), true);
gleich('ohne material', await B.anwenden({ material: null }, details, 'Female'), false);
console.log(JSON.stringify({ ok: true }));
"""

VORLAGEN_SKRIPT = """
const { Brauenvorlagen: V } = await import(MODUL);
const gleich = (was, a, b) => {
    if (a !== b) throw new Error(was + ': ' + a + ' statt ' + b); };
const vorgabe = { brauen_staerke: 1, brauen_dicke: 1, brauen_dichte: 1, brauen_bogen_laenge: 1,
                  brauen_deckkraft: 1, brauen_lage: 0, brauen_hoehe_innen: 0, brauen_hoehe_aussen: 0,
                  brauen_woelbung: 0 };
const buschig = V.anwenden({ brauen: '#000000', brauen_lage: 0.01 }, 'buschig', vorgabe);
gleich('vorlage dichte', buschig.brauen_dichte, 1.6);
gleich('vorlage setzt rest zurueck', buschig.brauen_lage, 0);
gleich('fremdes feld bleibt', buschig.brauen, '#000000');
gleich('erkennen', V.erkennen(buschig, vorgabe), 'buschig');
gleich('vorgabe', V.erkennen({ ...vorgabe }, vorgabe), '');
gleich('eigene', V.erkennen({ ...vorgabe, brauen_dichte: 1.23 }, vorgabe), null);
console.log(JSON.stringify({ ok: true }));
"""


class BrauenhautTest(SimpleTestCase):

    def test_abfrage_und_shader(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_vorlage_setzt_ihre_felder_und_wird_erkannt(self):
        self.assertTrue(VORLAGEN.laufen(VORLAGEN_SKRIPT).get('ok'))

    def test_modell_regler_und_albedo_sind_verdrahtet(self):
        modell = BrauenhautTest._text('gemeinsam', 'humanbodymodell.js')
        self.assertIn('Brauenhaut.anwenden(this.bodyMesh, this.details, this.bodyType)',
                      modell)
        for datei in ('gemeinsam/humanbodymodell.js', 'scene/detailbedienung.js',
                      'scene/charakter_koerper.js'):
            self.assertNotIn('Augenbrauenbau.', BrauenhautTest._text(*datei.split('/')), datei)
        self.assertIn("(farbig ? '?brauen=ohne' : '')",
                      BrauenhautTest._text('gemeinsam', 'hauttextur.js'))
        vorgabe = BrauenhautTest._text('gemeinsam', 'koerperdetails.js')
        felder = sorted(set(re.findall(r'(brauen_[a-z_]+):', vorgabe)))
        bereiche = BrauenhautTest._text('scene', 'detailbereiche.js')
        vorlage = (settings.BASE_DIR / 'templates' / '_szene_details.html'
                   ).read_text(encoding='utf-8')
        for feld in felder:
            self.assertIn("'%s'" % feld, bereiche, feld)
            kennung = 'prop-detail-' + feld.replace('_', '-')
            self.assertIn('"%s"' % kennung, vorlage, kennung)
        self.assertEqual(len(felder), 9, felder)
        self.assertIn('id="prop-detail-brauen-vorlage"', vorlage)
        self.assertIn("Brauenvorlagen.anwenden(inst.details, wahl.value, "
                      "Koerperdetails.VORGABE)", BrauenhautTest._text('scene', 'detailbedienung.js'))
        hauttexturen = (settings.BASE_DIR / 'core' / 'api' / 'hauttexturen.py'
                        ).read_text(encoding='utf-8')
        self.assertIn("request.GET.get('brauen') == 'ohne'", hauttexturen)

    @staticmethod
    def _text(*teile):
        return VIEWER.joinpath(*teile).read_text(encoding='utf-8')
