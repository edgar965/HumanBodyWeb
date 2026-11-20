"""`Kettenregler`: Regler der Exportleiste auf die Kettenschritte „stoff“ und „haar“ (20.11.2026, Edgar: Wind-, Stoff- und Haar-Regler „sollen wirken, wenn der Render eingestellt ist“).

Echte Regler-Dateien (`Filmregler.schreiben`, wie der Render) in `ProjektTemp/pruefungen` (`Pruefablage`), geladen über den Weg des Servers (`Exportleistekettenlauf.kettenregler`).
Geprüft: unberührte Regler → kein Zeichen (der Render spielt die Ablage der Seite); ein Wind-Regler → Zeichen für beide Schritte, gleich bei gleichen Werten; „Wind auf Bart“ nur für
„haar“; Anlauf in Bilder der Bewegung; Wind mit Y oben; `stoff.anker` und `stoff.zeitskala` als Faktor auf die Werte der Kette. Läuft nur auf Ansage; nicht gelaufen beim Schreiben
(20.11.2026). Sabotage (von Hand): in `zeichen` immer '' zurückgeben → „Wind ändert das Zeichen“ rot; in `wind` `(x, z, -y)` durch `(x, y, z)` ersetzen → „Neigung nach oben“ rot.
"""
import os
import unittest
from types import SimpleNamespace

from core.dienste.exportleistekettenlauf import Exportleistekettenlauf

from ._pruefablage import Pruefablage


class KettenreglerTest(unittest.TestCase):
    databases = []

    def _regler(self, ordner, name, werte):
        from Figurfilm.filmregler import Filmregler
        pfad = Filmregler.schreiben(os.path.join(ordner, name), {'renderphysik': werte} if werte else {})
        return Exportleistekettenlauf.kettenregler(pfad)

    def test_unberuehrt_kein_zeichen(self):
        with Pruefablage.ordner() as ordner:
            r = self._regler(ordner, 'leer.json', {})
            self.assertEqual((r.zeichen('stoff'), r.zeichen('haar')), ('', ''))
            self.assertEqual(r.abweichungen('haar'), {})

    def test_wind_aendert_das_zeichen(self):
        with Pruefablage.ordner() as ordner:
            a = self._regler(ordner, 'a.json', {'wind.staerke': 20.0})
            b = self._regler(ordner, 'b.json', {'wind.staerke': 20.0})
            self.assertRegex(a.zeichen('stoff'), r'^r[0-9a-f]{10}$')
            self.assertNotEqual(a.zeichen('stoff'), a.zeichen('haar'))
            self.assertEqual(a.zeichen('haar'), b.zeichen('haar'))

    def test_wind_auf_bart_nur_fuer_haar(self):
        with Pruefablage.ordner() as ordner:
            r = self._regler(ordner, 'bart.json', {'wind.bart': 1.0})
            self.assertEqual(r.zeichen('stoff'), '')
            self.assertNotEqual(r.zeichen('haar'), '')

    def test_anlauf_in_bildern_der_bewegung(self):
        with Pruefablage.ordner() as ordner:
            r = self._regler(ordner, 'vorlauf.json', {'straehnen.vorlauf': 30})
            self.assertEqual(r.vorlauf('straehnen.vorlauf', 15, 60.0), 60)        # 30 Bilder Film (1 s) = 60 Bilder bei 60 fps
            self.assertEqual(r.vorlauf('stoff.vorlauf', 15, 60.0), 15)            # unberührt: der Wert der Kette

    def test_neigung_nach_oben(self):
        with Pruefablage.ordner() as ordner:
            r = self._regler(ordner, 'wind.json', {'wind.staerke': 20.0, 'wind.richtung': 90.0, 'wind.neigung': 30.0})
            richtung = [float(x) for x in r.wind('haar', 60.0, 15).felder[0].richtung]
            self.assertAlmostEqual(richtung[0], -0.866, places=3)                  # von rechts (+x) her, weht nach −x
            self.assertAlmostEqual(richtung[1], 0.5, places=3)                     # von unten: Y ist oben
            self.assertAlmostEqual(richtung[2], 0.0, places=3)

    def test_anker_und_zeitskala_als_faktor(self):
        from Stoffsolver.stoffmaterial import StoffMaterial
        k = SimpleNamespace(art='mantel', BIEGUNG_FAKTOR=1.0, SCHRITTE=15, MATERIAL='baumwolle', STEIFIGKEIT=150.0, VORLAUF=15, b=SimpleNamespace(fps=60.0))
        z0 = 31.6 / 60.0
        argumente = {'material': StoffMaterial.baumwolle().mit(abstand=0.002, zeitskala=z0, schritte=15), 'abstand': 0.002, 'pin_steifigkeit': 150.0,
                     'schwerkraft': (0.0, -9.81, 0.0)}
        with Pruefablage.ordner() as ordner:
            r = self._regler(ordner, 'stoff.json', {'stoff.anker': 2.0, 'stoff.zeitskala': 2.0, 'stoff.schwerkraft': 0.5})
            a = r.stoff(k, argumente)
        self.assertEqual(a['pin_steifigkeit'], 300.0)
        self.assertAlmostEqual(a['material_felder']['zeitskala'], 2.0 * z0)
        self.assertEqual(a['schwerkraft'], (0.0, -9.81 * 0.5, 0.0))
        self.assertNotIn('wind', a)                                                # kein Wind-Regler geändert: windstill wie die Kette


if __name__ == '__main__':
    unittest.main()
