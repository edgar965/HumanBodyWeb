# -*- coding: utf-8 -*-
u"""Fitting-Konzept (21.09.2026) an der Bibliothek: Bindung im Kleidnetz, Abnahme-Probe.

Edgar: „Mach ein besseres Konzept, da wir dieses Problem schon 20 Mal hatten."
Das Konzept steht in Hilfe → Kleidung → Fitting; hier die Abnahme, an echten
Stuecken (LongRunner, nur auf Ansage — Sekunden je Stueck und Pose, pyrender).

1. `folgernetz(…, bindung=…)` gibt jedem Browserpunkt des Base Shirts ein
   Koerperdreieck; ueber 90 % der Punkte sind voll gebunden (anliegendes Stueck),
   die Indizes zeigen in den Koerper der Browserstufe.
2. `Durchschimmerprobe` (ohne Bilder): an die Oberflaeche gebunden stehen in der
   Laufpose weniger Shirtpunkte im Koerper als gehaeutet — gemessen 21.09.2026:
   857 → 262 (2,59 → 0,79 %); Schwelle: hoechstens die Haelfte.
3. Mit Bildern: die Hautpixel vor dem Stoff sinken durch die Bindung in der
   Standpose in JEDER Ansicht (gemessen vorn 240 → 1, hinten 92 → 19, links
   372 → 0, rechts 546 → 0); Kontaktbogen liegt unter `ProjektTemp/durchschimmern/`.
"""
import unittest

from django.test import SimpleTestCase

from Genesis9.pfade import G9pfade
from ui.settings.wurzeln import TOOLS_ROOT

KENNUNG = 'g9_base_shirt'
POSEN = ('de_g9_base_05_standing', 'g9_base_pose_01_running_g9f')


def bibliothek_da():
    try:
        from Genesis9.garderobe import G9garderobe
        return G9pfade.vorhanden() and G9garderobe.eintrag(KENNUNG) is not None
    except Exception:  # noqa: BLE001
        return False


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek oder G9 Base Shirt fehlt')
class Genesis9FittingTest(SimpleTestCase):
    databases = set()

    def test_1_kleidnetz_traegt_die_bindung(self):
        from Genesis9.koerpernetz import G9koerpernetz
        from core.api.g9figur import G9figur
        from core.dienste.durchschimmerprobe import Durchschimmerprobe
        probe = Durchschimmerprobe(posen=POSEN[:1], rendern=False)
        formung = G9figur.formung({'regler': {}}, {})
        koerper = probe.koerper(formung)
        teile = [t for t in probe.ruhe(KENNUNG, formung, koerper) if t is not None]
        self.assertEqual(len(teile), 1)
        b = teile[0].bindung
        n = len(teile[0].punkte)
        self.assertEqual(b['dreieck'].shape, (n, 3))
        voll = (b['mischung'] >= 1).mean()
        self.assertGreater(voll, 0.9, 'das Base Shirt liegt an: ueber 90 %% voll gebunden (%.2f)' % voll)
        self.assertLess(int(b['dreieck'].max()), len(koerper.punkte))
        self.assertEqual(G9koerpernetz(formung, stufen=probe.stufen).bindungsflaeche().stufen, probe.stufen)

    def test_2_gebunden_weniger_im_koerper_als_gehaeutet(self):
        from core.dienste.durchschimmerprobe import Durchschimmerprobe
        zeilen = Durchschimmerprobe(posen=POSEN[1:], rendern=False).laufen([KENNUNG])
        nach = {z['weg']: z for z in zeilen}
        self.assertLessEqual(nach['gebunden']['innen'], nach['gehaeutet']['innen'] / 2,
                             'gebunden %d, gehaeutet %d' % (nach['gebunden']['innen'], nach['gehaeutet']['innen']))

    def test_3_bilder_hautpixel_sinken_in_jeder_ansicht(self):
        from core.dienste.durchschimmerprobe import Durchschimmerprobe
        ziel = TOOLS_ROOT / 'ProjektTemp' / 'durchschimmern'
        probe = Durchschimmerprobe(posen=POSEN[:1], ziel=ziel, rendern=True)
        zeilen = probe.laufen([KENNUNG])
        nach = {z['weg']: z for z in zeilen}
        self.assertLess(nach['gebunden']['pixel'], nach['gehaeutet']['pixel'] / 4,
                        'Pixel gebunden %s, gehaeutet %s' % (nach['gebunden']['pixel'], nach['gehaeutet']['pixel']))
        self.assertTrue((ziel / ('%s.jpg' % KENNUNG)).is_file())
