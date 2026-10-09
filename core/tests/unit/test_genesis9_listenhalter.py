# -*- coding: utf-8 -*-
u"""`G9listenhalter` (09.10.2026): die alte Liste weiterreichen, solange die neue gebaut wird.

Edgar: „warum dauert laden des Characters ewig". Ein Import schreibt alle ~50 s ein Stück, jeder Neuaufbau der Garderobe-Liste
kostet 6–17 s, und jede Stückanfrage stand dahinter (`ProjektTemp/_wegwerf/`, `szene-ladezeit.md`).

1. Die Liste wird einmal gebaut und gemerkt.
2. Hat ein anderer Prozess geschrieben (`veraltet`), bekommt ein Nachschlagen (`veraltet_ok`) die ALTE sofort, während der
   Faden die neue baut; wer die frische braucht, wartet auf sie.
3. `vergessen` (Schreiber im selben Prozess) verwirft auch die alte: Nachschlagen wartet auf die frische.
4. Eine Entwertung WÄHREND eines Neuaufbaus geht nicht verloren: Danach wird noch einmal gebaut.
5. Ohne alte Liste (erster Aufruf) wartet auch ein Nachschlagen.

Sabotage: `holen` gibt bei `veraltet_ok` nie die alte zurück → Fall 2 rot; `vergessen` lässt `_alt` stehen → Fall 3 rot;
`_neu` setzt `_liste` ohne die Zahl zu prüfen → Fall 4 rot.

Gelaufen am 09.10.2026 (Gesamtlauf auf Ansage): grün.
"""
import threading
import time
import unittest

from Genesis9.listenhalter import G9listenhalter


class Listenhalter(unittest.TestCase):

    def _halter(self):
        self.gebaut = 0
        self.aenderung = False
        self.bremse = None            # ein Event: der Bau wartet darauf

        def bauen():
            self.gebaut += 1
            nummer = self.gebaut
            if self.bremse is not None:
                self.bremse.wait(5)
            return ['liste%d' % nummer]

        def veraltet():
            geaendert, self.aenderung = self.aenderung, False
            return geaendert

        return G9listenhalter(bauen, veraltet)

    def test_1_einmal_gebaut(self):
        halter = self._halter()
        self.assertEqual(halter.holen(), ['liste1'])
        self.assertEqual(halter.holen(), ['liste1'])
        self.assertEqual(self.gebaut, 1)

    def test_2_nachschlagen_bekommt_die_alte_waehrend_neu_gebaut_wird(self):
        halter = self._halter()
        halter.holen()
        self.bremse = threading.Event()
        self.aenderung = True
        t0 = time.monotonic()
        self.assertEqual(halter.holen(veraltet_ok=True), ['liste1'], 'die alte, sofort')
        self.assertLess(time.monotonic() - t0, 1.0)
        antwort = []
        wartender = threading.Thread(target=lambda: antwort.append(halter.holen()))
        wartender.start()
        time.sleep(0.2)
        self.assertEqual(antwort, [], 'wer die frische braucht, wartet')
        self.bremse.set()
        wartender.join(5)
        self.assertEqual(antwort, [['liste2']])
        self.assertEqual(self.gebaut, 2, 'ein Neuaufbau, nicht zwei')

    def test_3_vergessen_verwirft_auch_die_alte(self):
        halter = self._halter()
        halter.holen()
        halter.vergessen()
        self.assertEqual(halter.holen(veraltet_ok=True), ['liste2'])

    def test_4_entwertung_waehrend_des_baus_geht_nicht_verloren(self):
        halter = self._halter()
        halter.holen()
        self.bremse = threading.Event()
        self.aenderung = True
        halter.holen(veraltet_ok=True)          # startet den Faden, der am Bremsklotz wartet
        time.sleep(0.2)
        self.aenderung = True
        halter.holen(veraltet_ok=True)          # zweite Entwertung, während der Bau läuft
        self.bremse.set()
        halter._faden.join(5)
        self.bremse = None
        self.assertEqual(halter.holen(), ['liste3'], 'die zweite Entwertung verlangt einen weiteren Bau')

    def test_5_ohne_alte_liste_wartet_auch_nachschlagen(self):
        halter = self._halter()
        self.assertEqual(halter.holen(veraltet_ok=True), ['liste1'])


if __name__ == '__main__':
    unittest.main()
