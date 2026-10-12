# -*- coding: utf-8 -*-
"""Nebenläufe von „Mesh to 3D" (12.10.2026): „haar" und „kleidung" rechnen in Fäden neben den Ketten (`Meshfigurlauf.NEBENLAEUFIG`) — Kunstdaten, ohne Datenbank, Runner und GPU.

Geprüft: Der Faden arbeitet auf einer KOPIE des Auftrags (der Hauptfaden sichert `job.ergebnis`, während der Faden schreibt), das Ergebnis kommt erst beim Abwarten in den Auftrag, ein Fehler im Faden
ist der Fehler des Schritts (mit dem Namen des Nebenlaufs als Schritt), die Vorgaben stehen für „Mesh to 3D", und „2D3D Kleider" rechnet weiter nacheinander.
NICHT gelaufen (Tests nur auf Ansage). Sabotage: `kopie.job.ergebnis = self.job.ergebnis` in `_nebenlauf` (gleiches Wörterbuch) macht `test_der_faden_schreibt_auf_einer_kopie` rot.
"""

import threading
from types import SimpleNamespace

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderkoerperlauf import Engine2d3dKleiderkoerperlauf
from core.dienste.meshfigurlauf import Meshfigurlauf
from core.dienste.meshfigurnebenlauf import Meshfigurnebenlauf


def lauf():
    z = Meshfigurlauf.__new__(Meshfigurlauf)
    z.job = SimpleNamespace(kennung='k', ergebnis={'erkennung': {'ok': True}}, schritt='')
    z.sicherungen = []
    z.sichern = lambda *felder: z.sicherungen.append(felder)
    return z


class NebenlaufTest(SimpleTestCase):
    def test_vorgaben(self):
        self.assertEqual(Meshfigurlauf.NEBENLAEUFIG, ('haar', 'kleidung', 'frisur'))
        self.assertEqual(set(Meshfigurlauf.WARTEN_VOR), {'vorschau', 'frisur', 'speichern'})
        for schritt in Meshfigurlauf.WARTEN_VOR.values():
            self.assertTrue(set(schritt) <= set(Meshfigurlauf.NEBENLAEUFIG))
        # Wer ein Nebenlauf-Ergebnis liest, wartet vorher: vorschau (Objekte), frisur (Haarmaske, Farbe), speichern (alle drei, auch die Frisur).
        self.assertEqual(Meshfigurlauf.WARTEN_VOR['speichern'], ('haar', 'kleidung', 'frisur'))
        self.assertNotIn('frisur', Meshfigurlauf.WARTEN_VOR['vorschau'])               # die Vorschau läuft neben der Frisurwahl
        self.assertEqual(Meshfigurlauf.NACH_SCHRITT, {'textur': ('frisur',)})          # ist die Textur „aus", startet die Frisur nach ihr; sonst früher, aus `Meshfigurende.textur`
        for folgen in Meshfigurlauf.NACH_SCHRITT.values():
            self.assertTrue(set(folgen) <= set(Meshfigurlauf.NEBENLAEUFIG))
        self.assertEqual(Engine2d3dKleiderkoerperlauf.NEBENLAEUFIG, ())

    def test_frueh_startet_einmal_und_nur_was_ein_nebenlauf_ist(self):
        z = lauf()
        halt = threading.Event()
        gestartet = []

        def fabrik(kopie):
            gestartet.append(kopie.job.ergebnis.get('haar'))
            halt.wait(5)

        self.assertFalse(Meshfigurnebenlauf.frueh(z, 'frisur'))                       # ohne laufendes `ausfuehren`: nichts
        nebenlaeufe = {}
        z._laufend = (nebenlaeufe, {'frisur': fabrik})
        self.assertFalse(Meshfigurnebenlauf.frueh(z, 'vorschau'))                    # kein Nebenlauf
        z.job.schritt = 'textur'
        self.assertTrue(Meshfigurnebenlauf.frueh(z, 'frisur'))
        self.assertEqual(z.job.schritt, 'textur')                                     # der Hauptfaden steht weiter in seinem Schritt
        self.assertIn('frisur', nebenlaeufe)
        self.assertFalse(Meshfigurnebenlauf.frueh(z, 'frisur'))                      # läuft schon: geschieht nichts
        halt.set()
        nebenlaeufe['frisur'][0].join()
        self.assertEqual(len(gestartet), 1)

    def test_frueh_wartet_vorher_auf_haar_und_kleidung_und_gibt_ihr_ergebnis_mit(self):
        z = lauf()
        z.job.ergebnis.pop('erkennung')
        haar_kopie = SimpleNamespace(job=SimpleNamespace(ergebnis={'haar': {'farbe': [1, 2, 3]}}))
        fertig = threading.Thread(target=lambda: None)
        fertig.start()
        fertig.join()
        nebenlaeufe = {'haar': (fertig, haar_kopie, {'sekunden': 1.0})}
        gesehen = {}

        def fabrik(kopie):
            gesehen['haar'] = kopie.job.ergebnis.get('haar')

        z._laufend = (nebenlaeufe, {'frisur': fabrik})
        self.assertTrue(Meshfigurnebenlauf.frueh(z, 'frisur'))
        nebenlaeufe['frisur'][0].join()
        self.assertEqual(gesehen['haar'], {'farbe': [1, 2, 3]})                       # die Frisur rechnet mit der Farbe des Haars, nicht mit der Vorgabe
        self.assertNotIn('haar', nebenlaeufe)

    def test_unterklasse_ohne_nebenlaeufe_startet_nichts(self):
        z = lauf()
        z.NEBENLAEUFIG = ()
        z._laufend = ({}, {'frisur': lambda kopie: self.fail('darf nicht laufen')})
        self.assertFalse(Meshfigurnebenlauf.frueh(z, 'frisur'))

    def test_der_faden_schreibt_auf_einer_kopie(self):
        z = lauf()
        halt = threading.Event()

        def fabrik(kopie):
            kopie.job.ergebnis['haar'] = {'bilder': 6}
            halt.wait(5)

        faden, kopie, aus = z._nebenlauf('haar', fabrik)
        self.assertNotIn('haar', z.job.ergebnis)                      # der Faden hat den Auftrag nicht angefasst
        self.assertIsNot(kopie.job.ergebnis, z.job.ergebnis)
        self.assertEqual(kopie.job.ergebnis['erkennung'], {'ok': True})
        halt.set()
        faden.join()
        z._nebenlaeufe_abwarten({'haar': (faden, kopie, aus)}, ('haar',))
        self.assertEqual(z.job.ergebnis['haar'], {'bilder': 6})
        self.assertIn('haar', z.job.ergebnis['dauer'])
        self.assertTrue(z.sicherungen)

    def test_fortschritt_und_sichern_des_fadens_tun_nichts(self):
        z = lauf()
        z.melden = lambda *a, **k: self.fail('der Faden meldet nicht')

        def fabrik(kopie):
            kopie.melden(0.5, 'x')
            kopie.sichern('ergebnis')

        faden, kopie, aus = z._nebenlauf('kleidung', fabrik)
        faden.join()
        self.assertNotIn('fehler', aus)
        self.assertEqual(z.sicherungen, [])

    def test_ein_fehler_im_faden_ist_der_fehler_des_schritts(self):
        z = lauf()

        def fabrik(kopie):
            raise ValueError('kaputt')

        nebenlaeufe = {'kleidung': z._nebenlauf('kleidung', fabrik)}
        with self.assertRaises(ValueError):
            z._nebenlaeufe_abwarten(nebenlaeufe, ('kleidung',))
        self.assertEqual(z.job.schritt, 'kleidung')                   # sonst stünde der Schritt, in dem gerade gewartet wurde
        self.assertEqual(nebenlaeufe, {})

    def test_unbekannte_namen_werden_uebersprungen(self):
        z = lauf()
        z._nebenlaeufe_abwarten({}, ('haar', 'kleidung'))
        self.assertEqual(z.job.ergebnis, {'erkennung': {'ok': True}})
