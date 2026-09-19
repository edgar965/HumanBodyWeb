# -*- coding: utf-8 -*-
"""Die Laenge eines taillierten Oberteils — `FittedShirt` endet an der Taille.

Edgar, 19.09.2026, mit Bild (Laenge 2,75, Form „T-Shirt (anliegend)"): „die
Laenge ist nicht OK beim T-Shirt, auf dem Regler ist es schon ein langes
T-Shirt, ist es aber nicht in Realitaet." Gemessen: `bodice.py` 105 rechnet
`length = body['waist_line']` ohne Regler; der Stoff reichte bei 2,75 von
107,6 bis 142,6 cm — Taille bis Schulter. `Rumpfverlaengerung` setzt den
Teil darunter als geraden Rockteil an (`PencilSkirt`, wie das Kleid).

Die Zahlen sind Ursulas (Genesis 9): waist_line 34,7, hips_line 25,0,
height 169,4, head_l 26,0 -> Beinlaenge 83,7 cm.
"""

import sys

from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from GarmentCode.rumpfverlaengerung import Rumpfverlaengerung  # noqa: E402

URSULA = {'height': 169.36, 'head_l': 26.02, 'waist_line': 34.7, 'hips_line': 25.0}
TAILLIERT = {'meta.upper': 'FittedShirt', 'meta.bottom': None, 'meta.wb': None,
             'sleeve.length': 0.3}


class RumpfverlaengerungTest(SimpleTestCase):
    databases = set()

    def test_lang_bekommt_einen_rockteil(self):
        regler, hinweise = Rumpfverlaengerung.anwenden(
            dict(TAILLIERT, **{'shirt.length': 2.75}), URSULA, 'oberteil')
        self.assertEqual(regler['meta.bottom'], 'PencilSkirt')
        # (2,75 - 1) * 34,7 = 60,7 cm unter der Taille; davon 25,0 Hueftpartie,
        # der Rest 35,7 cm als Anteil der Beinlaenge 83,64.
        self.assertAlmostEqual(regler['pencil-skirt.length'], 35.725 / 83.64, places=3)
        self.assertEqual(len(hinweise), 1)
        self.assertIn(u'61 cm unter der Taille', hinweise[0])
        self.assertIsNone(regler['meta.wb'])

    def test_bis_zur_taille_bleibt_alles(self):
        for laenge in (1.0, 0.5, None):
            werte = dict(TAILLIERT)
            if laenge is not None:
                werte['shirt.length'] = laenge
            regler, hinweise = Rumpfverlaengerung.anwenden(werte, URSULA, 'oberteil')
            self.assertIsNone(regler.get('meta.bottom'), laenge)
            self.assertNotIn('pencil-skirt.length', regler)
            self.assertEqual(hinweise, [])

    def test_der_gerade_shirt_hat_seine_eigene_laenge(self):
        """`tee.py` liest `shirt.length` selbst — kein Rockteil."""
        regler, hinweise = Rumpfverlaengerung.anwenden(
            {'meta.upper': 'Shirt', 'shirt.length': 2.75}, URSULA, 'oberteil')
        self.assertIsNone(regler.get('meta.bottom'))
        self.assertEqual(hinweise, [])

    def test_das_kleid_bringt_seinen_rock_mit(self):
        """Katalogvorgabe: `kleid` hat schon einen PencilSkirt — nichts anfassen."""
        regler, hinweise = Rumpfverlaengerung.anwenden({'shirt.length': 2.0}, URSULA, 'kleid')
        self.assertNotIn('pencil-skirt.length', regler)
        self.assertEqual(hinweise, [])

    def test_ein_alias_kennt_seine_form(self):
        """`hemd` ist ein Alias des Oberteils mit FittedShirt — auch ohne
        `meta.upper` im Regler gilt die Regel."""
        regler, hinweise = Rumpfverlaengerung.anwenden({'shirt.length': 1.65}, URSULA, 'hemd')
        self.assertEqual(regler['meta.bottom'], 'PencilSkirt')
        # 22,6 cm unter der Taille, knapp ueber der Hueftlinie: leicht negativ.
        self.assertLess(regler['pencil-skirt.length'], 0)
        self.assertGreater(regler['pencil-skirt.length'], -0.05)

    def test_ueber_dem_bereich_wird_geklemmt_und_gesagt(self):
        regler, hinweise = Rumpfverlaengerung.anwenden(
            dict(TAILLIERT, **{'shirt.length': 3.5}), {'height': 150.0, 'head_l': 22.0,
                                                        'waist_line': 40.0, 'hips_line': 20.0})
        # (3,5 - 1) * 40 - 20 = 80 cm auf 68 cm Bein = 1,18 -> 0,95
        self.assertEqual(regler['pencil-skirt.length'], 0.95)
        self.assertIn(u'höchstens', hinweise[0])

    def test_ohne_masse_wird_nicht_geraten(self):
        regler, hinweise = Rumpfverlaengerung.anwenden(
            dict(TAILLIERT, **{'shirt.length': 2.0}), {'waist_line': 34.7}, 'oberteil')
        self.assertIsNone(regler.get('meta.bottom'))
        self.assertEqual(hinweise, [])

    def test_entwurf_ruft_die_regel(self):
        from GarmentCode import entwurf
        quelle = open(entwurf.__file__, encoding='utf-8').read()
        self.assertIn('Rumpfverlaengerung.anwenden(regler, self.masse, self.vorlage)', quelle)
