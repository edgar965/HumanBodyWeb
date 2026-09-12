# -*- coding: utf-8 -*-
u"""Jeder Rechenweg der Vorlage hat seinen Klartext (11.09.2026).

Edgar: „da steht Server und Browser?? Mach das eindeutig". Die Auswahl
`figurvideo-weg` in `_figurvideo.html` und `Figurvideoanzeige.HINWEIS`
muessen dieselben Schluessel fuehren — ein Weg ohne Text stuende wieder
unerklaert da. Dazu die Bilanztexte, in Node.

Sabotage-Gegenprobe: `server` aus HINWEIS entfernt -> rot.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'figurvideo_anzeige.js')

SKRIPT = """
const { Figurvideoanzeige: A } = await import(MODUL);
const kurz = A.kurz({ bilder: 72, teile: [{ zuschlag_mm: 13.9 }, { name: 'T-Shirt' }, { name: 'Hose' }] });
const lang = A.lang({ wurzelweg_m: 1.234, quell_fps: 120, schritt: 5,
    teile: [{ name: 'Koerper', punkte: 70851, ruheprobe_mm: 0.0004, zuschlag_mm: 13.9 },
            { name: 'Hose', punkte: 3, ruheprobe_mm: 0, sitz_mm: 26.4, gleichlauf_mm: [26.2, 26.3], stoff_im_koerper_prozent: 5.49 }] });
console.log(JSON.stringify({ hinweise: Object.keys(A.HINWEIS).sort(), kurz, lang }));
"""


class FigurvideoAnzeigeTest(SimpleTestCase):

    databases = set()

    def test_jeder_weg_hat_einen_hinweis(self):
        vorlage = (settings.BASE_DIR / 'templates' / '_figurvideo.html')
        text = vorlage.read_text(encoding='utf-8')
        auswahl = re.search(r'<select id="figurvideo-weg".*?</select>', text, re.S)
        self.assertIsNotNone(auswahl)
        werte = sorted(re.findall(r'<option value="([^"]+)"', auswahl.group(0)))
        self.assertGreaterEqual(len(werte), 2)
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertEqual(ausgabe['hinweise'], werte)
        self.assertEqual(ausgabe['kurz'], '72 Bilder · Weichgewebe 13.9 mm · 2 Stücke')
        self.assertIn('Hose: 3 Punkte, Ruheprobe 0 mm, Sitz 26.4 mm, zur Haut 26.2 / 26.3 mm',
                      ausgabe['lang'])
        self.assertIn('im Körper 5.49 %', ausgabe['lang'])
