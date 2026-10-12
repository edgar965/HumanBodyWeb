# -*- coding: utf-8 -*-
"""Die zweite Runde der Beschleunigung von „Mesh to 3D", Teil 2 (12.10.2026, `meshfigur-tempo.md`): gleiche Ergebnisse wie vorher, nur nicht mehr bei jedem Lauf neu — Kunstdaten, kleine Dateien.

* `G9zeileneindeutig` gegen `np.unique(axis=0)` (Haar- und Kleidungsobjekt),
* `Meshfigurablegen.npy`, `Meshfigurgenesis._gleich`, `Blendimportnetz._kopieren/_ablegen`: eine Datei mit gleichem Inhalt bleibt unangetastet (Änderungszeit gleich) — sonst trifft kein Stempel mehr, der sie nennt, und die Frisurwahl
  läse eine halbe Datei, während die Vorschau sie ein weiteres Mal schreibt,
* `Mesh3dansicht.eingaben`: der Schlüssel des SAM-Ergebnisses hängt am Netz und den Einstellungen des Renderings, nicht am frisch gerenderten Bild,
* `Kleidungsentposen`: die Matrixprodukte geben dieselbe Rückrechnung wie die Dreifach-Summe.

NICHT gelaufen (Tests nur auf Ansage). Sabotagen: in `G9zeileneindeutig._zusammen` die Spalten in umgekehrter Reihenfolge gewichten macht `test_gleiche_ausgabe_wie_numpy` rot; `Meshfigurablegen.npy` ohne den Vergleich
(immer `np.save`) macht `test_gleicher_inhalt_bleibt_liegen` rot.
"""

import os
import time
import unittest

import numpy as np

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


class ZeileneindeutigTest(unittest.TestCase):
    def test_gleiche_ausgabe_wie_numpy(self):
        from Genesis9.zeileneindeutig import G9zeileneindeutig

        z = np.random.default_rng(5)
        faelle = [z.integers(0, 5, size=(500, 3)), z.integers(-40, 40, size=(800, 3)), z.integers(-3, 4, size=(600, 4)),
                  np.tile([[3, -2, 7]], (30, 1)), z.integers(0, 5, size=(1, 3)), z.integers(0, 9, size=(400, 3)).astype(np.int32)]
        breit = z.integers(-2 ** 40, 2 ** 40, size=(300, 3))                           # zu breit für einen int64-Schlüssel: der lexsort-Weg
        breit[150:] = breit[:150]
        faelle.append(breit)
        for zeilen in faelle:
            erwartet = np.unique(zeilen, axis=0, return_index=True, return_inverse=True)
            eindeutig, erste, umkehr = G9zeileneindeutig.eindeutig(zeilen)
            self.assertTrue(np.array_equal(eindeutig, erwartet[0]))
            self.assertTrue(np.array_equal(erste, erwartet[1]))
            self.assertTrue(np.array_equal(umkehr, np.asarray(erwartet[2]).reshape(-1)))
            self.assertEqual(eindeutig.dtype, erwartet[0].dtype)
            self.assertTrue(np.array_equal(eindeutig[umkehr], zeilen))                  # die Umkehrung stellt die Eingabe wieder her

    def test_leere_eingabe_geht_den_numpy_weg(self):
        from Genesis9.zeileneindeutig import G9zeileneindeutig

        eindeutig, erste, umkehr = G9zeileneindeutig.eindeutig(np.zeros((0, 3), dtype=np.int64))
        self.assertEqual((len(eindeutig), len(erste), len(umkehr)), (0, 0, 0))


class AblegenTest(unittest.TestCase):
    def setUp(self):
        self._ablage = Pruefablage.ordner()
        self.ordner = self._ablage.__enter__()
        self.addCleanup(self._ablage.__exit__, None, None, None)

    def _zeit(self, pfad):
        return os.stat(pfad).st_mtime_ns

    def test_gleicher_inhalt_bleibt_liegen(self):
        from meshfigur_ablegen import Meshfigurablegen

        pfad = os.path.join(self.ordner, 'posiert.npy')
        a = np.arange(30, dtype=np.float32).reshape(10, 3)
        self.assertTrue(Meshfigurablegen.npy(pfad, a))
        zeit = self._zeit(pfad)
        time.sleep(0.05)
        self.assertFalse(Meshfigurablegen.npy(pfad, a.copy()))
        self.assertEqual(self._zeit(pfad), zeit)
        self.assertTrue(Meshfigurablegen.npy(pfad, a + 1))                             # anderer Inhalt: geschrieben
        self.assertTrue(np.array_equal(np.load(pfad), a + 1))
        self.assertTrue(Meshfigurablegen.npy(pfad, (a + 1).astype(np.float64)))        # anderer Datentyp zählt als anderer Inhalt

    def test_unlesbare_datei_wird_ersetzt(self):
        from meshfigur_ablegen import Meshfigurablegen

        pfad = os.path.join(self.ordner, 'posiert.npy')
        with open(pfad, 'wb') as f:
            f.write(b'kaputt')
        a = np.ones((4, 3), dtype=np.float32)
        self.assertTrue(Meshfigurablegen.npy(pfad, a))
        self.assertTrue(np.array_equal(np.load(pfad), a))

    def test_genesisdatei_gleich_und_ungleich(self):
        from core.dienste.meshfigurgenesis import Meshfigurgenesis

        pfad = os.path.join(self.ordner, 'genesis_ende.npz')
        daten = {'punkte': np.arange(12, dtype=np.float64).reshape(4, 3), 'eltern': np.array([-1, 0, 1]), 'name': np.array(['a', 'b'])}
        self.assertFalse(Meshfigurgenesis._gleich(pfad, daten))                        # fehlt
        np.savez(pfad, **daten)
        self.assertTrue(Meshfigurgenesis._gleich(pfad, daten))
        geaendert = dict(daten, punkte=daten['punkte'] + 1e-9)
        self.assertFalse(Meshfigurgenesis._gleich(pfad, geaendert))
        self.assertFalse(Meshfigurgenesis._gleich(pfad, {k: v for k, v in daten.items() if k != 'name'}))

    def test_koerpernetz_kopie_und_ablage_lassen_gleiche_datei_in_ruhe(self):
        from core.dienste.blendimportnetz import Blendimportnetz

        quelle, ziel = os.path.join(self.ordner, 'q.glb'), os.path.join(self.ordner, 'z.glb')
        with open(quelle, 'wb') as f:
            f.write(b'glTF' + bytes(range(200)))
        self.assertTrue(Blendimportnetz._kopieren(quelle, ziel))
        zeit = self._zeit(ziel)
        time.sleep(0.05)
        self.assertFalse(Blendimportnetz._kopieren(quelle, ziel))
        self.assertEqual(self._zeit(ziel), zeit)
        with open(quelle, 'ab') as f:
            f.write(b'x')
        self.assertTrue(Blendimportnetz._kopieren(quelle, ziel))
        inhalt = b'abc' * 100
        pfad = os.path.join(self.ordner, 'a.glb')
        self.assertTrue(Blendimportnetz._ablegen(pfad, inhalt))
        zeit = self._zeit(pfad)
        time.sleep(0.05)
        self.assertFalse(Blendimportnetz._ablegen(pfad, inhalt))
        self.assertEqual(self._zeit(pfad), zeit)
        self.assertTrue(Blendimportnetz._ablegen(pfad, inhalt + b'!'))
        self.assertEqual([n for n in os.listdir(self.ordner) if n.endswith('.teil')], [])   # keine Nebendatei bleibt liegen


class AnsichtSchluesselTest(unittest.TestCase):
    def test_schluessel_haengt_am_netz_nicht_am_bild(self):
        from core.dienste.mesh3dansicht import Mesh3dansicht

        with Pruefablage.ordner() as ordner:
            glb = os.path.join(ordner, 'koerper.glb')
            with open(glb, 'wb') as f:
                f.write(b'glTF')
            a = Mesh3dansicht.eingaben(glb)
            self.assertEqual(a, Mesh3dansicht.eingaben(glb))                             # stabil über zwei Aufrufe
            self.assertEqual(set(a), {'netz', 'ansicht'})
            self.assertEqual(a['ansicht'][0], Mesh3dansicht.FASSUNG)
            os.utime(glb, ns=(1, 1))
            self.assertNotEqual(a, Mesh3dansicht.eingaben(glb))                          # andere Datei (Zeit): anderer Schlüssel
            self.assertNotEqual(Mesh3dansicht.eingaben(glb)['ansicht'], Mesh3dansicht.eingaben(glb, kante=512)['ansicht'])


class SchammessungNahtzeilenTest(unittest.TestCase):
    def test_naht_ohne_angaben_wirft_nicht(self):
        from core.dienste.schammessungzeilen import Schammessungzeilen

        self.assertEqual(Schammessungzeilen._naht({}), ['Naht: keine Angaben'])         # vorher KeyError 'randpunkte' (Fallout ranger, „Farbe am Ring")
        self.assertEqual(Schammessungzeilen._naht({'aus': 'zu weit'})[0], 'Naht: aus — zu weit')            # die Zeile nennt den Grund
        self.assertEqual(Schammessungzeilen._naht({'hinweis': 'x'}), ['Naht: x'])


class EntposenMatrixprodukteTest(unittest.TestCase):
    def test_rueckrechnung_gleich_der_dreifachsumme(self):
        from Kleidung.kleidungsentposen import Kleidungsentposen

        z = np.random.default_rng(2)
        ruhe = z.normal(size=(300, 3)) * 0.2
        winkel = 0.4
        r = np.array([[np.cos(winkel), -np.sin(winkel), 0], [np.sin(winkel), np.cos(winkel), 0], [0, 0, 1]])
        posiert = ruhe @ r.T + np.array([0.1, -0.2, 0.3])
        entposen = Kleidungsentposen(ruhe, posiert)
        stoff = posiert[:50] + z.normal(size=(50, 3)) * 0.001
        zurueck = entposen.ruhelage(stoff)
        erwartet = (stoff - np.array([0.1, -0.2, 0.3])) @ r                           # starre Bewegung: die Rückrechnung ist ihre Umkehrung
        self.assertLess(float(np.abs(zurueck - erwartet).max()), 1e-6)


if __name__ == '__main__':
    unittest.main()
