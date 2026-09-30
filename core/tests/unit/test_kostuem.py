# -*- coding: utf-8 -*-
"""Kostüm-Kreislauf von BlenderModel (29.09.2026) — Schema, Optimierer, Note, Referenzwinkel, Auswahl,
Optionen. Rein rechnend: keine Datenbank, kein Blender, kein Ollama. Die Blender-Seite
(`effekte/blender/kostuem/`) und die Prüf-KI prüft nur ein echter Lauf.
"""

from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.kostuembild import Kostuembild
from core.dienste.kostuemkreislauf import Kostuemkreislauf
from core.dienste.kostuemnote import Kostuemnote
from core.dienste.kostuemoptimierer import Kostuemoptimierer
from core.dienste.kostuemoptionen import Kostuemoptionen
from core.dienste.kostuemparameter import Kostuemparameter
from core.dienste.kostuemreferenz import Kostuemreferenz


class KostuemparameterTest(SimpleTestCase):
    def test_startwerte_liegen_in_ihren_grenzen(self):
        for k, e in Kostuemparameter.schema().items():
            self.assertLessEqual(e['min'], e['start'], k)
            self.assertLessEqual(e['start'], e['max'], k)

    def test_pruefen_zieht_auf_die_grenzen_und_schaltet_binaer(self):
        werte = Kostuemparameter.pruefen({'mantel.luft': 99, 'stab.an': 0.7, 'bart.laenge': 'kaputt', 'x': 1})
        self.assertEqual(werte['mantel.luft'], Kostuemparameter.schema()['mantel.luft']['max'])
        self.assertEqual(werte['stab.an'], 1)
        self.assertEqual(werte['bart.laenge'], Kostuemparameter.start()['bart.laenge'])
        self.assertNotIn('x', werte)
        self.assertEqual(set(werte), set(Kostuemparameter.schema()))

    def test_der_saum_des_mantels_liegt_immer_unter_der_kniehoehe(self):
        # Kostuemrumpf._rockringe setzt den Kniering auf 0,29 × Höhe — die Ringe müssen in z fallen.
        for k in ('mantel.saum_hoehe', 'unterkleid.saum_hoehe'):
            self.assertLess(Kostuemparameter.schema()[k]['max'], 0.29, k)

    def test_unterschiede_nennen_nur_merkliche_aenderungen(self):
        alt = Kostuemparameter.start()
        # Der Stab startet seit 30.09.2026 eingeschaltet — umgeschaltet wird gegen den Startwert.
        neu = dict(alt, **{'hut.hoehe': alt['hut.hoehe'] + 0.05, 'stab.an': 1 - alt['stab.an']})
        self.assertEqual(set(Kostuemparameter.unterschiede(alt, neu)), {'hut.hoehe', 'stab.an'})


class KostuemoptimiererTest(SimpleTestCase):
    def test_dieselbe_runde_schlaegt_dieselben_kandidaten_vor(self):
        start = Kostuemparameter.start()
        a = Kostuemoptimierer('2026.09.29.21.10.16').kandidaten(start, 4, 7)
        b = Kostuemoptimierer('2026.09.29.21.10.16').kandidaten(start, 4, 7)
        self.assertEqual(a, b)
        self.assertNotEqual(a, Kostuemoptimierer('2026.09.29.21.10.16').kandidaten(start, 4, 8))

    def test_kandidaten_sind_gueltig_und_weichen_ab(self):
        start = Kostuemparameter.start()
        for k in Kostuemoptimierer('x').kandidaten(start, 8, 1):
            self.assertEqual(k, Kostuemparameter.pruefen(k))
            self.assertTrue(Kostuemparameter.unterschiede(start, k), 'mindestens ein Wert geändert')

    def test_der_optimierer_schaltet_keine_teile_und_laesst_ausgeschaltete_in_ruhe(self):
        # Erster echter Lauf: er schaltete den Hut ab (−14 %) — Teile an/aus ist Sache der Prüf-KI.
        start = dict(Kostuemparameter.start(), **{'stab.an': 0})
        schalter = [k for k, e in Kostuemparameter.schema().items() if e['art'] == 'schalter']
        for runde in range(1, 40):
            for k in Kostuemoptimierer('x').kandidaten(start, 4, runde):
                self.assertEqual({s: k[s] for s in schalter}, {s: start[s] for s in schalter})
                self.assertEqual(k['stab.hoehe'], start['stab.hoehe'], 'Stab ist aus')
        self.assertNotIn('stab.hoehe', Kostuemoptimierer.veraenderlich(start))
        self.assertIn('stab.hoehe', Kostuemoptimierer.veraenderlich(dict(start, **{'stab.an': 1})))

    def test_farben_wuerfelt_der_optimierer_nicht(self):
        # Lauf vom 29./30.09.2026: Gürtel reines Grün, Unterkleid grelles Gelb, Bart reines Weiß — schwach sichtbare
        # Farben hatten keinen Gegendruck. Seit Modell Version 2 sind sie gemessen und fest.
        start = Kostuemparameter.start()
        self.assertFalse([k for k in Kostuemoptimierer.veraenderlich(start) if k.startswith('farbe.')])
        for runde in range(1, 20):
            for k in Kostuemoptimierer('x').kandidaten(start, 4, runde):
                self.assertEqual({f: v for f, v in k.items() if f.startswith('farbe.')},
                                 {f: v for f, v in start.items() if f.startswith('farbe.')})

    def test_schritt_waechst_bei_erfolg_und_schrumpft_sonst_in_grenzen(self):
        o = Kostuemoptimierer('x')
        self.assertGreater(o.anpassen(True), Kostuemoptimierer.SCHRITT_START)
        for _ in range(200):
            o.anpassen(False)
        self.assertEqual(o.schritt, Kostuemoptimierer.SCHRITT_MIN)


class KostuemnoteTest(SimpleTestCase):
    @staticmethod
    def bild(maske, farbe=(0.2, 0.3, 0.6)):
        f = np.zeros(maske.shape + (3,), np.float32)
        f[:] = farbe
        return Kostuembild(f, maske)

    def test_gleiche_bilder_haben_keine_abweichung(self):
        m = np.zeros((Kostuembild.HOEHE, Kostuembild.BREITE), bool)
        m[20:180, 40:90] = True
        note = Kostuemnote.vergleichen(self.bild(m), self.bild(m))
        self.assertEqual((note['iou'], note['farbe'], note['abweichung']), (1.0, 0.0, 0.0))

    def test_andere_farbe_und_anderer_umriss_kosten(self):
        a = np.zeros((Kostuembild.HOEHE, Kostuembild.BREITE), bool)
        a[20:180, 40:90] = True
        b = np.zeros_like(a)
        b[20:180, 40:120] = True
        gleich = Kostuemnote.vergleichen(self.bild(a), self.bild(a))
        breiter = Kostuemnote.vergleichen(self.bild(a), self.bild(b))
        bunter = Kostuemnote.vergleichen(self.bild(a), self.bild(a, (0.8, 0.7, 0.4)))
        self.assertGreater(breiter['abweichung'], gleich['abweichung'])
        self.assertAlmostEqual(breiter['iou'], 50 / 80, places=3)
        self.assertGreater(bunter['farbe'], 0.2)

    def test_gesamt_gewichtet_nach_den_fotos(self):
        n1, n2 = {'abweichung': 0.2, 'iou': 0.9, 'farbe': 0.1}, {'abweichung': 0.6, 'iou': 0.5, 'farbe': 0.1}
        self.assertEqual(Kostuemnote.gesamt([(3.0, n1), (1.0, n2)])['abweichung'], 0.3)


class KostuemreferenzTest(SimpleTestCase):
    def test_winkel_von_hand_dann_bogenname_dann_rolle(self):
        self.assertEqual(Kostuemreferenz.winkel_von({'original': 'ansicht_1_2.jpg', 'winkel': 42}), 42.0)
        self.assertEqual(Kostuemreferenz.winkel_von({'original': 'ansicht_1_2.jpg'}), -90.0)
        self.assertEqual(Kostuemreferenz.winkel_von({'datei': 'x.png', 'rolle': 'hinten'}), 180.0)
        self.assertIsNone(Kostuemreferenz.winkel_von({'datei': 'x.png', 'rolle': 'auto'}))


class KostuemauswahlTest(SimpleTestCase):
    def kreislauf(self, toleranz=2):
        k = Kostuemkreislauf.__new__(Kostuemkreislauf)
        # `pruefki_stillstand` ist seit 30.09.2026 eine Option (vorher fest 3 Runden).
        k.o = {'toleranz': toleranz, 'pruefki': 'qwen3.8:27b', 'pruefki_alle': 5, 'pruefki_stillstand': 3}
        return k

    @staticmethod
    def erg(name, abweichung):
        return {'name': name, 'note': {'abweichung': abweichung}}

    def test_besserer_optimierer_wird_uebernommen(self):
        wahl, art = self.kreislauf()._auswaehlen([self.erg('k0', 0.5), self.erg('k1', 0.4)], 0.45)
        self.assertEqual((wahl['name'], art), ('k1', 'optimierer'))

    def test_nichts_besseres_heisst_nichts_uebernehmen(self):
        self.assertEqual(self.kreislauf()._auswaehlen([self.erg('k0', 0.5)], 0.45), (None, None))

    def test_pruefki_darf_innerhalb_der_toleranz_schlechter_sein(self):
        k = self.kreislauf(toleranz=2)
        wahl, art = k._auswaehlen([self.erg('k0', 0.5), self.erg('ki', 0.458)], 0.45)
        self.assertEqual((wahl['name'], art), ('ki', 'ki'))
        self.assertEqual(k._auswaehlen([self.erg('k0', 0.5), self.erg('ki', 0.47)], 0.45), (None, None))

    def test_pruefki_faellig_alle_n_runden_und_nach_stillstand(self):
        k = self.kreislauf()
        self.assertEqual([k._kritik_faellig(i, 0, 9) for i in range(6)], [False] * 4 + [True, False])
        self.assertTrue(k._kritik_faellig(1, 3, 3))
        k.o['pruefki'] = Kostuemoptionen.AUS
        self.assertFalse(k._kritik_faellig(4, 9, 9))


class KostuemoptionenTest(SimpleTestCase):
    def test_pruefki_bleibt_ein_gespeichertes_modell_auch_ohne_ollama(self):
        self.assertEqual(
            Kostuemoptionen.pruefen({'pruefki': 'gemma4:26b-a4b-it-qat'})['pruefki'], 'gemma4:26b-a4b-it-qat'
        )
        self.assertEqual(
            Kostuemoptionen.pruefen({'pruefki': 'rm -rf /'})['pruefki'], Kostuemoptionen.VORGABE_KI
        )
        self.assertEqual(
            Kostuemoptionen.pruefen({'runden': 0})['runden'], 20, 'außerhalb der Grenzen → Vorgabe'
        )

    def test_ohne_ollama_bleibt_die_vorgabe_waehlbar(self):
        with mock.patch('core.dienste.kostuemoptionen.Ollamamodelle.mit_bildern', return_value=[]):
            feld = next(f for f in Kostuemoptionen.katalog()['optionen'] if f['schluessel'] == 'pruefki')
        self.assertEqual([w['wert'] for w in feld['werte']], ['aus', Kostuemoptionen.VORGABE_KI])
