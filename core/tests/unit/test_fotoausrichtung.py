# -*- coding: utf-8 -*-
"""Die Rechnung der automatischen Fotoausrichtung — jetzt prüfbar.

`Fotoausrichtung.automatisch` hatte 194 Zeilen, zwei Kameraformate, eine Prüfung
und einen Rückfall — und KEINEN Test. Prüfbar war sie auch nicht: Der erste
Schritt lädt über `sys.path`-Umbiegung den SMPL-X-Wrapper aus `VideoToBVH`, der
im Django-Interpreter gar nicht installiert ist.

Nach der Aufteilung (17.08.2026) rechnen `_aus_pymafx` und `_aus_smplestx` auf
einem übergebenen `Netzmasse` — ohne Wrapper, ohne Foto, ohne GPU. Die
Erwartungswerte hier sind von Hand nachgerechnet, nicht aus dem Lauf abgelesen:
Ein Test, der das Ergebnis des Codes als Sollwert nimmt, prüft nur, dass sich
nichts ÄNDERT, nicht dass es stimmt.
"""

import numpy as np
from django.test import SimpleTestCase

from core.daten.netzmasse import Netzmasse
from core.daten.persongrenzen import Persongrenzen
from core.dienste.fotoausrichtung import Fotoausrichtung

#: Ein Netz, das sich im Kopf rechnen lässt: 1 breit, 2 hoch, Mitte im Ursprung.
NETZ = np.array([[-0.5, -1.0, 0.0], [0.5, 1.0, 0.0]], dtype=np.float32)

#: Bildgröße wie in den Vorgaben.
BILD = {'image_width': 1920, 'image_height': 1080}

#: base_scale = min(1920*0,9/1 ; 1080*0,9/2) = min(1728 ; 486) = 486
BASIS = 486.0


class NetzmasseTest(SimpleTestCase):

    def test_masse_und_grundmassstab(self):
        m = Netzmasse.aus(NETZ, BILD)
        self.assertEqual((m.cx, m.cy), (0.0, 0.0))
        self.assertEqual((m.mesh_w, m.mesh_h), (1.0, 2.0))
        self.assertEqual((m.y_min, m.y_max), (-1.0, 1.0))
        self.assertAlmostEqual(m.base_scale, BASIS, places=3)

    def test_fehlende_bildgroesse_faellt_auf_die_vorgabe(self):
        """`'image_width': None` ist der ECHTE Fall — der Schlüssel ist da.

        Genau daran ist die alte Fassung gescheitert (Review 13.08.2026):
        `.get('image_width', 1920)` greift nicht, wenn der Wert None IST, und
        danach rechnete `img_w * 0.9` mit None.
        """
        m = Netzmasse.aus(NETZ, {'image_width': None, 'image_height': None})
        self.assertEqual((m.img_w, m.img_h), (1920, 1080))

    def test_bildhoehe_von(self):
        m = Netzmasse.aus(NETZ, BILD)
        # scale so wählen, dass s = 400 ist: 400/486
        verschiebung = {'center_y': 500.0, 'scale': 400.0 / BASIS}
        self.assertAlmostEqual(m.bildhoehe_von(m.y_max, verschiebung), 100.0,
                               places=3)
        self.assertAlmostEqual(m.bildhoehe_von(m.y_min, verschiebung), 900.0,
                               places=3)


class PersongrenzenTest(SimpleTestCase):

    def test_ohne_foto_gilt_das_ganze_bild(self):
        g = Persongrenzen.aus_foto(None, 1920, 1080)
        self.assertFalse(g.erkannt)
        self.assertEqual((g.oben, g.unten, g.mitte_x), (0.0, 1080.0, 960.0))

    def test_unlesbares_foto_gilt_als_nicht_erkannt(self):
        g = Persongrenzen.aus_foto('A:/gibt/es/nicht.jpg', 800, 600)
        self.assertFalse(g.erkannt)
        self.assertEqual(g.unten, 600.0)

    def test_hoehe_und_mitte(self):
        g = Persongrenzen(100.0, 900.0, 480.0, True)
        self.assertEqual(g.hoehe, 800.0)
        self.assertEqual(g.mitte_y, 500.0)


class PymafxTest(SimpleTestCase):
    """`pred_cam` [s, tx, ty] im Ausschnittsraum -> Mitte und Maßstab."""

    def cam(self, **zusatz):
        daten = dict(BILD, pred_cam=[1.0, 0.0, 0.0],
                     bbox_cxcywh=[960, 540, 400, 400], bbox_scale=1.0)
        daten.update(zusatz)
        return daten

    def test_mittige_person_landet_in_der_bildmitte(self):
        masse = Netzmasse.aus(NETZ, BILD)
        aus = Fotoausrichtung._aus_pymafx(self.cam(), masse)
        self.assertEqual(aus['method'], 'pymafx')
        bt = aus['body_transform']
        self.assertAlmostEqual(bt['center_x'], 960.0, places=3)
        self.assertAlmostEqual(bt['center_y'], 540.0, places=3)
        # s_pixels = 1,0 * 400 / 2 = 200 -> 200/486
        self.assertAlmostEqual(bt['scale'], 200.0 / BASIS, places=6)

    def test_ohne_bbox_kein_vorschlag(self):
        masse = Netzmasse.aus(NETZ, BILD)
        self.assertIsNone(
            Fotoausrichtung._aus_pymafx(self.cam(bbox_cxcywh=None), masse))


class SmplestxTest(SimpleTestCase):
    """`cam_trans` mit Brennweite und Hauptpunkt -> Mitte und Maßstab."""

    def cam(self, **zusatz):
        daten = dict(BILD, cam_trans=[0.0, 0.0, 2.0], cam_focal=[1000.0, 1000.0],
                     cam_princpt=[128.0, 128.0], processed_bbox=[100, 50, 256, 256],
                     input_body_shape=[256, 256])
        daten.update(zusatz)
        return daten

    def test_hauptpunkt_wird_auf_das_originalbild_zurueckgerechnet(self):
        masse = Netzmasse.aus(NETZ, BILD)
        bt = Fotoausrichtung._aus_smplestx(self.cam(), masse)['body_transform']
        # princpt_orig_x = 128/256*256 + 100 = 228, y = 128 + 50 = 178
        self.assertAlmostEqual(bt['center_x'], 228.0, places=3)
        self.assertAlmostEqual(bt['center_y'], 178.0, places=3)
        # wp_scale = focal_orig_x / tz = 1000 / 2 = 500
        self.assertAlmostEqual(bt['scale'], 500.0 / BASIS, places=6)

    def test_kamera_auf_der_bildebene_ergibt_keinen_vorschlag(self):
        """`tz = 0` wäre eine Division durch Null."""
        masse = Netzmasse.aus(NETZ, BILD)
        self.assertIsNone(
            Fotoausrichtung._aus_smplestx(self.cam(cam_trans=[0, 0, 0]), masse))


class PruefungTest(SimpleTestCase):

    def setUp(self):
        self.masse = Netzmasse.aus(NETZ, BILD)
        self.grenzen = Persongrenzen(100.0, 900.0, 480.0, True)

    def test_treffer_auf_die_person_gilt(self):
        bt = {'center_x': 480.0, 'center_y': 500.0, 'scale': 400.0 / BASIS}
        self.assertTrue(Fotoausrichtung._passt(bt, self.masse, self.grenzen))

    def test_um_300_pixel_daneben_gilt_nicht(self):
        bt = {'center_x': 480.0, 'center_y': 200.0, 'scale': 400.0 / BASIS}
        self.assertFalse(Fotoausrichtung._passt(bt, self.masse, self.grenzen))

    def test_ohne_personenerkennung_zaehlt_der_grobe_massstab(self):
        """Kopf muss über 216 (20 %), Füße unter 864 (80 %) liegen."""
        offen = Persongrenzen.ganzes_bild(1920, 1080)
        # s = 200 -> Kopf bei 300, und 300 liegt NICHT im oberen Fünftel.
        zu_klein = {'center_x': 960.0, 'center_y': 500.0, 'scale': 200.0 / BASIS}
        self.assertFalse(Fotoausrichtung._passt(zu_klein, self.masse, offen))
        # s = 400 -> Kopf 100, Füße 900, beide innerhalb, Überdeckung 100 %.
        passend = {'center_x': 960.0, 'center_y': 500.0, 'scale': 400.0 / BASIS}
        self.assertTrue(Fotoausrichtung._passt(passend, self.masse, offen))


class EinpassenTest(SimpleTestCase):

    def test_netz_fuellt_95_prozent_der_personenhoehe(self):
        masse = Netzmasse.aus(NETZ, BILD)
        grenzen = Persongrenzen(100.0, 900.0, 480.0, True)
        aus = Fotoausrichtung._einpassen(
            {'method': 'pymafx'}, masse, grenzen)
        self.assertEqual(aus['method'], 'pymafx_fallback')
        bt = aus['body_transform']
        self.assertAlmostEqual(bt['center_x'], 480.0, places=3)
        self.assertAlmostEqual(bt['center_y'], 500.0, places=3)
        # 800 * 0,95 / 2 = 380 -> 380/486
        self.assertAlmostEqual(bt['scale'], 380.0 / BASIS, places=6)
