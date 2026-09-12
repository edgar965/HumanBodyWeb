# -*- coding: utf-8 -*-
u"""Die Deutung eines Bibliotheksstuecks in GarmentCode-Regler.

DER ANLASS (09.09.2026, Edgar: „Kannst du die in das GarmentCode Modell
ueberfuehren, so dass es funktioniert?")
========================================================================
`Schnittdeutung` rechnet aus den Massen eines Kleidungsnetzes die Regler eines
GarmentCode-Schnitts. Jede Formel ist die Umkehrung einer aus dem Upstream:

    shirt.length        = design * body['waist_line']            (tee.py:34)
    pencil/flare.length = design * body['_leg_length']           (skirt_paneled.py:330)
    sleeve.length       = design * (arm_length - opening_length) (sleeves.py:137)

Rechnet eine davon falsch, entsteht kein Fehler — es entsteht ein Kleid mit
falscher Laenge, und das sieht man erst nach 46 s Simulation. Deshalb pruefen
diese Tests die Umrechnung an Zahlen, die von Hand nachzurechnen sind.

DREI FEHLER, DIE HIER FESTGEHALTEN WERDEN, weil sie schon passiert sind:

1. **Eine Kapuze wurde stumm zum T-Shirt.** `donitz_monk_robe_hood` sitzt
   146-176 cm ueber dem Boden; die Rueckfallzeile am Ende der Kette lieferte
   „t-shirt". Jetzt sagt die Deutung, dass der Katalog nichts dafuer hat.
2. **Handschuhe wurden zum Jumpsuit.** Die Luecke zwischen zwei Handschuhen
   sieht aus wie die zwischen zwei Hosenbeinen. Unterschieden werden sie an
   der Lage: 100 % des Stoffs liegt weiter aussen als die halbe Schulter.
3. **Eine Strumpfhose galt als Armstueck.** Die Armpruefung zaehlte auch
   Punkte unterhalb der Huefte mit — in der A-Pose stehen die Beine breiter
   als die Schultern. Eine falsche Begruendung ist schlimmer als keine.
"""
import os
import sys
import unittest

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(HIER)))
if WURZEL not in sys.path:
    sys.path.insert(0, WURZEL)


class SchnittdeutungTest(unittest.TestCase):
    u"""Rechnet die Deutung die Regler richtig zurueck?"""

    #: Keine Datenbank - die Deutung rechnet nur (Regel `tests-und-produktivdaten`).
    databases = set()

    #: Die Masse der Vorgabefigur, gemessen am 09.09.2026. Aus ihnen folgen
    #: Schulter 142,2 cm, Taille 109,9 cm und Huefte 84,9 cm ueber dem Boden.
    MASSE = {
        'height': 167.989, 'head_l': 25.809, 'waist_line': 32.312,
        'hips_line': 25.0, 'shoulder_w': 31.798, 'armscye_depth': 10.356,
        'arm_length': 52.151, 'waist': 61.842, 'hips': 97.432,
    }

    def _stueck(self, **abweichung):
        u"""Ein gemessenes Stueck; die Vorgabe ist ein knielanges Kleid."""
        werte = {'unten_cm': 50.0, 'oben_cm': 136.0, 'saum_umfang_cm': 106.0,
                 'saum_breite_cm': 40.0, 'oben_umfang_cm': 90.0,
                 'oben_breite_cm': 34.0, 'armstoff_cm': 0.0,
                 'beine_getrennt': False, 'aussen_anteil': 0.05,
                 'punkte': 6892}
        werte.update(abweichung)
        return werte

    def _deuten(self, kategorie='dresses', **abweichung):
        from GarmentCode.schnittdeutung import Schnittdeutung
        return Schnittdeutung(self._stueck(**abweichung), self.MASSE,
                              kategorie).deuten()

    # ------------------------------------------------------------ Koerperhoehen

    def test_koerperhoehen_folgen_garmentcodes_eigener_ableitung(self):
        u"""`_waist_level` und `_leg_length` wie in `body_params`."""
        from GarmentCode.schnittdeutung import Schnittdeutung
        deutung = Schnittdeutung(self._stueck(), self.MASSE)
        self.assertAlmostEqual(deutung.schulter_cm, 142.180, places=2)
        self.assertAlmostEqual(deutung.taille_cm, 109.868, places=2)
        self.assertAlmostEqual(deutung.huefte_cm, 84.868, places=2)

    # -------------------------------------------------------------- Laengen

    def test_rocklaenge_ist_der_anteil_der_beinlaenge(self):
        u"""Saum bei 50 cm, Huefte bei 84,868 cm -> (84,868-50)/84,868."""
        _, regler, _ = self._deuten()
        self.assertAlmostEqual(regler['pencil-skirt.length'], 0.411, places=3)
        self.assertAlmostEqual(regler['flare-skirt.length'], 0.411, places=3)

    def test_saum_am_boden_ergibt_volle_beinlaenge(self):
        u"""Ein bodenlanges Stueck darf `length` nicht ueber 1,0 treiben."""
        _, regler, _ = self._deuten(unten_cm=0.0)
        self.assertEqual(regler['pencil-skirt.length'], 1.0)

    def test_aermellaenge_gegen_arm_ohne_armloch(self):
        u"""20 cm Stoff am Arm / (52,151 - 10,356) nutzbarer Armlaenge."""
        _, regler, _ = self._deuten(armstoff_cm=20.0)
        self.assertFalse(regler['sleeve.sleeveless'])
        self.assertAlmostEqual(regler['sleeve.length'], 0.479, places=3)

    def test_ohne_armstoff_bleibt_das_stueck_aermellos(self):
        _, regler, _ = self._deuten(armstoff_cm=0.0)
        self.assertTrue(regler['sleeve.sleeveless'])
        self.assertNotIn('sleeve.length', regler)

    # ---------------------------------------------------------------- Weite

    def test_suns_kommt_aus_dem_gemessenen_saumumfang(self):
        u"""Saumumfang = Taille + 2*pi*Laenge*suns, nach `suns` aufgeloest.

        Saum 176 cm, Taille 61,842 cm, Rocklaenge (84,868-33) = 51,868 cm:
        (176 - 61,842) / (2*pi*51,868) = 0,350.
        """
        _, regler, _ = self._deuten(unten_cm=33.0, saum_umfang_cm=176.0)
        self.assertAlmostEqual(regler['flare-skirt.suns'], 0.350, places=2)

    def test_weiter_saum_wird_ein_sommerkleid_enger_ein_kleid(self):
        u"""Der Unterschied ist der Saum gegen die Huefte (97,4 cm)."""
        weit, _, _ = self._deuten(saum_umfang_cm=176.0)
        eng, _, _ = self._deuten(saum_umfang_cm=106.0)
        self.assertEqual(weit, 'sommerkleid')
        self.assertEqual(eng, 'kleid')

    # ------------------------------------------------------------- Bauarten

    def test_die_kategorie_der_bibliothek_entscheidet_ueber_beine(self):
        u"""Shorts und Minirock sind am Netz nicht zu trennen - der Ordner schon.

        Gemessen (09.09.2026): Auf Saumhoehe liegen 12 bis 24 Netzpunkte, die
        groesste Luecke betraegt bei `cortu_jeans_shorts` (Hose) 30 % und bei
        `frankyaye_mini_skirt_01` (Rock) 19 % der Breite. Dazwischen liegt
        keine Schwelle, die beide richtig trennt.
        """
        hose, _, _ = self._deuten(kategorie='pants', unten_cm=73.0,
                                  oben_cm=95.0, beine_getrennt=False)
        rock, _, _ = self._deuten(kategorie='skirts', unten_cm=74.0,
                                  oben_cm=95.0, beine_getrennt=True)
        self.assertEqual(hose, 'hose')
        self.assertEqual(rock, 'bleistiftrock')

    def test_ein_kurzes_oberteil_bekommt_kein_unterteil(self):
        oben, _, bericht = self._deuten(unten_cm=95.0, oben_cm=137.0)
        self.assertEqual(oben, 't-shirt')
        self.assertFalse(bericht['unterteil'])

    def test_unter_der_achsel_beginnendes_stueck_ist_traegerlos(self):
        u"""Achsel bei 142,18 - 10,356 = 131,8 cm ueber dem Boden."""
        _, regler, _ = self._deuten(oben_cm=124.0)
        self.assertTrue(regler['shirt.strapless'])

    # ------------------------------------------------- was der Katalog nicht kann

    def test_kopfbedeckung_wird_abgelehnt_statt_geraten(self):
        from GarmentCode.schnittdeutung import Unuebersetzbar
        with self.assertRaises(Unuebersetzbar) as gefangen:
            self._deuten(unten_cm=146.0, oben_cm=176.0)
        self.assertIn('oberhalb der Achsel', str(gefangen.exception))

    def test_schuh_wird_abgelehnt_statt_geraten(self):
        from GarmentCode.schnittdeutung import Unuebersetzbar
        with self.assertRaises(Unuebersetzbar) as gefangen:
            self._deuten(unten_cm=2.0, oben_cm=51.0)
        self.assertIn('unterhalb der Hüfte', str(gefangen.exception))

    def test_handschuh_wird_abgelehnt_und_nicht_zum_jumpsuit(self):
        u"""Der Fehler vom 09.09.2026: `toigo_gloves_long` -> „jumpsuit"."""
        from GarmentCode.schnittdeutung import Unuebersetzbar
        with self.assertRaises(Unuebersetzbar) as gefangen:
            self._deuten(unten_cm=88.0, oben_cm=126.0, aussen_anteil=1.0,
                         beine_getrennt=True)
        self.assertIn('an den Armen', str(gefangen.exception))

    def test_ein_normales_kleid_wird_nicht_abgelehnt(self):
        u"""Gegenprobe: Die drei Ablehnungen duerfen nicht zu breit greifen."""
        name, regler, _ = self._deuten()
        self.assertEqual(name, 'kleid')
        self.assertTrue(regler)


class StueckmasseTest(unittest.TestCase):
    u"""Misst `Stueckmasse` die Geometrie, die die Deutung erwartet?"""

    databases = set()

    @staticmethod
    def _koerper():
        u"""Ein Koerper, dessen Fuesse auf z=0 stehen - mehr braucht es nicht."""
        import numpy as np
        return np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.68]])

    def test_makehuman_netze_werden_auf_den_boden_gestellt(self):
        u"""MakeHuman-Fuesse liegen bei -0,84 m; der Koerper steht auf 0."""
        import numpy as np
        from GarmentCode.stueckmasse import Stueckmasse

        punkte = np.array([[0.0, 0.0, -0.84], [0.0, 0.0, 0.0]])
        masse = Stueckmasse(punkte, self._koerper())
        self.assertAlmostEqual(masse.unten_cm, 0.0, places=3)
        self.assertAlmostEqual(masse.oben_cm, 84.0, places=3)

    def test_beine_werden_an_der_luecke_erkannt_nicht_an_der_mitte(self):
        u"""Zwei Roehren mit Loch dazwischen gegen einen geschlossenen Ring."""
        import numpy as np
        from GarmentCode.stueckmasse import Stueckmasse

        hoehen = np.linspace(-0.84, -0.60, 20)
        beine, ring = [], []
        for z in hoehen:
            for winkel in np.linspace(0, 2 * np.pi, 24, endpoint=False):
                x, y = 0.06 * np.cos(winkel), 0.06 * np.sin(winkel)
                beine.append([x - 0.10, y, z])
                beine.append([x + 0.10, y, z])
                ring.append([0.18 * np.cos(winkel), 0.12 * np.sin(winkel), z])
        koerper = self._koerper()
        self.assertTrue(Stueckmasse(np.array(beine), koerper).beine_getrennt())
        self.assertFalse(Stueckmasse(np.array(ring), koerper).beine_getrennt())

    def test_armstoff_zaehlt_nur_oberhalb_der_huefte(self):
        u"""Der Strumpfhosen-Fehler: Beine stehen in A-Pose auch weit aussen."""
        import numpy as np
        from GarmentCode.stueckmasse import Stueckmasse

        # Stoff nur an den Beinen, weit aussen, aber tief.
        beine = np.array([[-0.30, 0.0, -0.80], [0.30, 0.0, -0.80],
                          [-0.28, 0.0, -0.60], [0.28, 0.0, -0.60]])
        masse = Stueckmasse(beine, self._koerper())
        self.assertEqual(masse.aussen_anteil(31.8, ab_hoehe_cm=84.9), 0.0)
        self.assertEqual(masse.aussen_anteil(31.8, ab_hoehe_cm=0.0), 1.0)


if __name__ == '__main__':
    unittest.main()
