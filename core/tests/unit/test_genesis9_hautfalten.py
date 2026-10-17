# -*- coding: utf-8 -*-
u"""Die Hautfalten des Alters (`G9hautfalten`, `G9hautfaltenablage`, 17.10.2026) — Kunstdaten, keine HumanBody-Figur, keine Paarung.

WARUM (Edgar, 17.10.2026: „altersregler funktioniert nicht, das Gesicht wenn der am Anschlag ist, ist noch immer das gleiche … schau dir das bei HumanBody an … baue die Runzeln und
Hautfalten"): HumanBodys Altersfalten (G-Kanal des MB-Lab-Verschiebungsbilds) werden je UDIM-Kachel zu einer Normalenkarte; der Browser legt sie mit dem Alterswert als Gewicht über die Haut.
Zusagen an der Rechnung (der Weg Texel → HumanBody-UV ist `Bildmodellhautverschiebung.texel`, in `test_bildmodell_hautverschiebung` geprüft):

1. Eine Fläche ohne Höhe ergibt die flache Normale (128, 128, 255) und die Steigung 0.
2. Steigt die Höhe nach rechts (+u), kippt die Normale nach links: R < 128; steigt sie nach UNTEN im Bild (−v), kippt die Normale nach +v (nach oben im Bild): G > 128 —
   Tangentenraum OpenGL, wie Three ihn liest.
3. Die Steigung ist physikalisch: Höhe je Meter Kante — dieselbe Höhe auf einer halb so großen Kante ergibt die doppelte Steigung.
4. Die Kantenlänge je Texel kommt aus den Lagen der Nachbartexel (`_kante`); außerhalb der Inseln gilt der Wert des nächsten gültigen Texels.
5. Die Dateinamen tragen die Fassung; eine Liste, die eine fehlende Kachel nennt, gilt als nicht gebaut (`G9hautfaltenablage.liste` → None, kein Ergebnis eines anderen Laufs).
6. Fassung 2 (zweiter Durchgang, 17.10.2026): Alpha = Furchentiefe — eine Rinne unter ihrer Umgebung > 0, Flaches 0.
7. Fassung 3: An einer Naht der Übertragung (Sprung der HumanBody-UV zwischen Nachbartexeln) bleibt die Normale flach.

Sabotage-Gegenprobe (nicht gefahren): in `normalen` das Vorzeichen von `sy` drehen → Fall 2 rot; die Division durch `kante_*` streichen → Fall 3 rot; in `liste` die Prüfung der Bilddateien
streichen → Fall 5 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from core.dienste.g9hautfalten import G9hautfalten  # noqa: E402
from core.dienste.g9hautfaltenablage import G9hautfaltenablage  # noqa: E402

S = 32


def rampe(achse, steigung):
    u"""Eine Höhe, die entlang `achse` (1 = nach rechts, 0 = nach unten) um `steigung` Meter je Pixel steigt."""
    z, x = np.mgrid[0:S, 0:S].astype(float)
    return (x if achse == 1 else z) * steigung


class NormalenTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.falten = G9hautfalten('male')
        self.eins = np.full((S, S), 0.001)            # 1 mm je Pixel

    def mitte(self, bild):
        return bild[S // 2, S // 2].astype(int)

    def test_1_flach_bleibt_flach(self):
        bild, steigung = self.falten.normalen(np.zeros((S, S)), self.eins, self.eins)
        self.assertEqual(self.mitte(bild).tolist(), [128, 128, 255])
        self.assertAlmostEqual(float(steigung.max()), 0.0)

    def test_2_richtung_der_normale(self):
        rechts, _s = self.falten.normalen(rampe(1, 0.0002), self.eins, self.eins)      # 0,2 mm Höhe je mm Kante
        unten, _s = self.falten.normalen(rampe(0, 0.0002), self.eins, self.eins)
        self.assertLess(self.mitte(rechts)[0], 128, 'steigt nach rechts → Normale nach links')
        self.assertAlmostEqual(int(self.mitte(rechts)[1]), 128, delta=1)
        self.assertGreater(self.mitte(unten)[1], 128, 'steigt nach unten → Normale nach +v (im Bild nach oben)')
        self.assertAlmostEqual(int(self.mitte(unten)[0]), 128, delta=1)

    def test_3_die_steigung_ist_hoehe_je_meter(self):
        _b, grob = self.falten.normalen(rampe(1, 0.0002), self.eins, self.eins)
        _b, fein = self.falten.normalen(rampe(1, 0.0002), self.eins / 2.0, self.eins)
        self.assertAlmostEqual(float(grob[S // 2, S // 2]), 0.2, places=2)
        self.assertAlmostEqual(float(fein[S // 2, S // 2]), 0.4, places=2, msg='dieselbe Höhe auf halber Kante: doppelte Steigung')

    def test_3b_die_steigung_ist_begrenzt(self):
        _b, steigung = self.falten.normalen(rampe(1, 0.01), self.eins, self.eins)      # 10 m/m
        self.assertLessEqual(float(steigung.max()), np.sqrt(2.0) * self.falten.STEIGUNG_MAX + 1e-9)

    def test_6_furche_im_alpha(self):
        u"""Fassung 2: eine Rinne 1 mm unter der Fläche ergibt Alpha > 0 in der Rinne, die flache Umgebung 0."""
        hoehe = np.zeros((S, S))
        hoehe[:, S // 2 - 1:S // 2 + 1] = -0.001
        drin = np.ones((S, S), dtype=bool)
        tiefe = self.falten.hoehle(hoehe, self.eins / 4.0, drin)         # 0,25 mm je Pixel: die Umgebung reicht über die Rinne hinaus
        self.assertGreater(int(tiefe[S // 2, S // 2]), 100)
        self.assertEqual(int(tiefe[S // 2, 2]), 0)
        self.assertEqual(tiefe.dtype, np.uint8)

    def test_7_naht_der_uebertragung_bleibt_flach(self):
        u"""Fassung 3: springt die HumanBody-UV zwischen zwei Nachbarn (Inselgrenze), ist die Steigung dort keine Falte — die Normale bleibt flach."""
        uv = np.zeros((S, S, 2))
        uv[..., 0] = np.arange(S)[None, :] * 0.001
        uv[:, S // 2:, 0] += 0.5                                         # Sprung in der Mitte
        drin = np.ones((S, S), dtype=bool)
        hoehe = np.zeros((S, S))
        hoehe[:, S // 2:] = 0.0002                                       # die Stufe, die der Sprung erzeugt
        naht = self.falten._naht(uv, drin, hoehe, self.eins, self.eins)
        self.assertTrue(naht[S // 2, S // 2])
        self.assertFalse(naht[S // 2, 2])
        self.falten.naht = naht
        bild, _s = self.falten.normalen(hoehe, self.eins, self.eins)
        self.assertEqual(self.mitte(bild).tolist(), [128, 128, 255], 'an der Naht flach')


class KanteTest(SimpleTestCase):
    databases = set()

    def test_4_kante_aus_den_nachbartexeln(self):
        lage = np.zeros((S, S, 3))
        lage[..., 0] = np.arange(S)[None, :] * 0.002        # 2 mm je Pixel nach rechts
        lage[..., 1] = np.arange(S)[:, None] * 0.003        # 3 mm je Pixel nach unten
        drin = np.zeros((S, S), dtype=bool)
        drin[4:28, 4:28] = True
        kx = G9hautfalten._kante(lage, drin, 1)
        ky = G9hautfalten._kante(lage, drin, 0)
        self.assertAlmostEqual(float(kx[16, 16]), 0.002, places=6)
        self.assertAlmostEqual(float(ky[16, 16]), 0.003, places=6)
        self.assertAlmostEqual(float(kx[0, 0]), 0.002, places=6, msg='außerhalb der Insel: der Wert des nächsten gültigen Texels')

    def test_4b_ohne_gueltige_texel_ein_notwert(self):
        kx = G9hautfalten._kante(np.zeros((S, S, 3)), np.zeros((S, S), dtype=bool), 1)
        self.assertTrue(np.all(kx > 0))


class AblageTest(SimpleTestCase):
    databases = set()

    def test_5_fassung_im_namen_und_liste_nennt_nur_vorhandene_bilder(self):
        with ProjektTemp.wegwerfordner(prefix='g9hautfalten_') as ordner:          # Projektordner, nicht System-Temp (`systemtemp.md`)
            stamm = Path(ordner) / ('hautfalten_male_v%d' % G9hautfalten.FASSUNG)
            with mock.patch.object(G9hautfalten, 'stamm', classmethod(lambda cls, g: stamm)):
                self.assertIn('v%d' % G9hautfalten.FASSUNG, G9hautfalten.bildpfad('male', 1001).name)
                self.assertIsNone(G9hautfaltenablage.liste('male'), 'ohne Liste kein Ergebnis')
                G9hautfalten.listenpfad('male').write_text(json.dumps({'fassung': 1, 'kacheln': {'1001': {}}}), encoding='utf-8')
                self.assertIsNone(G9hautfaltenablage.liste('male'), 'die Liste nennt eine Kachel, deren Bild fehlt: nicht fertig')
                G9hautfalten.bildpfad('male', 1001).write_bytes(b'png')
                self.assertEqual(G9hautfaltenablage.liste('male')['kacheln'], {'1001': {}})
                self.assertEqual(G9hautfaltenablage.bild('male', 1001), G9hautfalten.bildpfad('male', 1001))
                self.assertIsNone(G9hautfaltenablage.bild('male', 1002), 'eine Kachel, die die Liste nicht nennt, gibt es nicht')
