# -*- coding: utf-8 -*-
u"""`Hauttextur`: MB-Lab-Albedo, Bump und Rauheit auf der Haut — und der Endpunkt dazu.

WARUM (Edgar, 13.09.2026: „es fehlt auch die Einstellung der Hautfarbe,
Textur, usw."). In Node mit Attrappen, das Laden ist ersetzt (kein
Three.js, kein Netz):

1. `karten` nennt zu `hum_f_cauc` die Albedo und die weiblichen Karten, zu
   `hum_m_afro` die männlichen; leer oder unbekannt → null.
2. `anwenden` setzt map, bumpMap, roughnessMap auf Haut UND Censor, nicht
   auf die Wimpern; ohne eigene Hautfarbe wird die Farbe weiß, mit eigener
   bleibt sie.
3. Wert leer → Karten weg (`entfernen`), Rückgabe false.
4. `Koerperdetails.aus` nimmt nur Werte aus `WAHL`; `anwenden` dort ruft die
   Textur (Drahtformat).

Der Endpunkt: erlaubte Datei → 200 `image/png` mit Cache-Kopf; unbekannter
Name und `..` → 404, nie ein Pfad aus der Anfrage.

Sabotage-Gegenprobe: `m.color.setRGB(1, 1, 1)` weg → Fall 2 rot.
"""
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase

from core.api.hauttexturen import Hauttexturen
from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hauttextur.js')

SKRIPT = """
const { Hauttextur: H } = await import(MODUL);
pruefe('karten frau', H.karten('hum_f_cauc'), { map: 'hum_f_cauc_albedo.png', bumpMap: 'human_female_bump.png', roughnessMap: 'human_female_roughness.png' });
pruefe('karten mann', H.karten('hum_m_afro').bumpMap, 'human_male_bump.png');
pruefe('leer', H.karten(''), null); pruefe('unbekannt', H.karten('../x'), null);
H.laden = async (datei) => ({ datei });
const material = () => ({ color: { r: 0.8, g: 0.6, b: 0.5, setRGB(r, g, b) { this.r = r; this.g = g; this.b = b; } }, map: null, needsUpdate: false });
const netz = { material: [material(), material(), material()] };
pruefe('gesetzt', await H.anwenden(netz, { haut_textur: 'hum_f_cauc', haut: '' }), true);
pruefe('karten an haut', [netz.material[0].map.datei, netz.material[0].bumpMap.datei, netz.material[1].roughnessMap.datei],
       ['hum_f_cauc_albedo.png', 'human_female_bump.png', 'human_female_roughness.png']);
pruefe('wimpern ohne', netz.material[2].map, null);
pruefe('farbe weiss', [netz.material[0].color.r, netz.material[1].color.b], [1, 1]);
pruefe('bump', netz.material[0].bumpScale, H.BUMP);
const eigen = { material: [material(), material()] };
await H.anwenden(eigen, { haut_textur: 'hum_m_cauc', haut: '#aabbcc' });
pruefe('eigene farbe bleibt', eigen.material[0].color.r, 0.8);
pruefe('weg', await H.anwenden(netz, { haut_textur: '' }), false);
pruefe('karten weg', [netz.material[0].map, netz.material[1].bumpMap], [null, null]);
pruefe('ohne materialliste', await H.anwenden({ material: material() }, { haut_textur: 'hum_f_cauc' }), false);
console.log(JSON.stringify({ ok: true }));
"""


class HauttexturTest(SimpleTestCase):

    def test_karten_anwenden_und_entfernen(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_koerperdetails_kennt_das_feld(self):
        text = Path(settings.BASE_DIR).joinpath('static', 'viewer', 'gemeinsam', 'koerperdetails.js') \
            .read_text(encoding='utf-8')
        self.assertIn("haut_textur: ''", text)
        self.assertIn("Hauttextur.WAHL.some(([w]) => w === wert)", text)
        self.assertIn('Hauttextur.anwenden(netz, details)', text)


class DerEndpunkt(SimpleTestCase):

    def setUp(self):
        self.client = Client()

    def test_erlaubte_textur_kommt_als_png_mit_cache(self):
        self.assertTrue((Hauttexturen.ordner() / 'human_female_bump.png').is_file(),
                        'MB-Lab-Texturen fehlen unter %s' % Hauttexturen.ordner())
        antwort = self.client.get('/api/character/textur/human_female_bump.png/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort['Content-Type'], 'image/png')
        self.assertEqual(antwort['Cache-Control'], Hauttexturen.CACHE)
        antwort.close()

    def test_unbekannt_und_pfad_bleiben_404(self):
        self.assertEqual(self.client.get('/api/character/textur/settings.py/').status_code, 404)
        self.assertEqual(self.client.get('/api/character/textur/..%2Fsettings.py/').status_code, 404)
        self.assertFalse(Hauttexturen.ERLAUBT.match('human_female_lipmap.png/../x.png'))
