# -*- coding: utf-8 -*-
"""Pfadvergabe (12.10.2026): ein Suchpfad-Eintrag, den zwei Fäden zugleich brauchen, bleibt, bis der LETZTE ihn loslässt.

Anlass: Der Lauf „Edgar S1 nah" scheiterte im Schritt „kleidung" an `No module named 'meshfigur_landmarkenflaeche'` — `haar` und `kleidung` rechnen in Fäden nebeneinander, jeder hinter `with Meshto3dpfad():`;
der Kontext räumte beim Verlassen weg, was ER eingehängt hatte, also nahm der erste fertige Faden den Ordner dem zweiten unter den Füßen weg. Kunstverzeichnisse (kein echter Ordner nötig), alles ohne Datenbank.
Sabotage-Gegenprobe: `Pfadvergabe.loslassen` ohne Zählung (`cls._halter.pop` ohne Prüfung `rest > 0`) → `test_der_erste_faden_raeumt_dem_zweiten_nichts_weg` wird rot.
"""

import sys
import threading
import unittest

from core.daten.pfadvergabe import Pfadvergabe


class PfadvergabeTest(unittest.TestCase):
    ORDNER = ['A:/_pfadvergabe_test/eins', 'A:/_pfadvergabe_test/zwei']

    def setUp(self):
        self.addCleanup(self._aufraeumen)

    def _aufraeumen(self):
        for o in self.ORDNER:
            while o in sys.path:
                sys.path.remove(o)
            Pfadvergabe._halter.pop(o, None)
            Pfadvergabe._eigen.discard(o)

    def test_ein_halter_haengt_ein_und_raeumt_weg(self):
        Pfadvergabe.halten(self.ORDNER)
        self.assertEqual(sys.path[:2], self.ORDNER, 'Reihenfolge wie in der Liste, ganz vorn')
        Pfadvergabe.loslassen(self.ORDNER)
        self.assertFalse(any(o in sys.path for o in self.ORDNER))

    def test_der_erste_faden_raeumt_dem_zweiten_nichts_weg(self):
        Pfadvergabe.halten(self.ORDNER)      # Faden A
        Pfadvergabe.halten(self.ORDNER)      # Faden B, der Ordner steht schon im Suchpfad
        Pfadvergabe.loslassen(self.ORDNER)   # A ist fertig
        self.assertTrue(all(o in sys.path for o in self.ORDNER), 'B braucht ihn noch')
        Pfadvergabe.loslassen(self.ORDNER)   # B ist fertig
        self.assertFalse(any(o in sys.path for o in self.ORDNER))

    def test_ein_fremder_eintrag_bleibt(self):
        """Stand der Ordner schon vorher im Suchpfad (nicht von uns), nimmt ihn keiner heraus."""
        sys.path.insert(0, self.ORDNER[0])
        Pfadvergabe.halten(self.ORDNER[:1])
        Pfadvergabe.loslassen(self.ORDNER[:1])
        self.assertIn(self.ORDNER[0], sys.path)

    def test_viele_faeden_zugleich(self):
        fehler = []
        start = threading.Barrier(8)

        def faden():
            try:
                start.wait()
                for _ in range(200):
                    Pfadvergabe.halten(self.ORDNER)
                    if not all(o in sys.path for o in self.ORDNER):
                        fehler.append('fehlt im Block')
                    Pfadvergabe.loslassen(self.ORDNER)
            except Exception as e:  # noqa: BLE001 — jeder Fehler im Faden ist ein Befund des Tests
                fehler.append(repr(e))

        faeden = [threading.Thread(target=faden) for _ in range(8)]
        for f in faeden:
            f.start()
        for f in faeden:
            f.join()
        self.assertEqual(fehler, [])
        self.assertFalse(any(o in sys.path for o in self.ORDNER))


if __name__ == '__main__':
    unittest.main()
