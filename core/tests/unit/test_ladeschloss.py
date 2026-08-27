# -*- coding: utf-8 -*-
"""`Ladeschloss` — ein Schloss je Name, und der zweite Blick darunter.

Ein Schloss JE NAME: Mit einem einzigen Schloss wartete jede Anfrage auf
die 1,21 s der Catmull-Clark-Unterteilung — auch die, die nur Morphdaten
wollte. Geprueft werden die drei Punkte, an denen so etwas kippt: RLock
statt Lock, der zweite Blick unter dem Schloss, und dass Vorhandenes
nicht neu gebaut wird.
"""

import threading
import time

from django.test import SimpleTestCase

from core.daten.ladeschloss import Ladeschloss


class LadeschlossTest(SimpleTestCase):
    """Das Schloss je Name — und der zweite Blick darunter."""

    def test_gleicher_name_gleiches_schloss(self):
        schloss = Ladeschloss()
        self.assertIs(schloss.fuer('netz'), schloss.fuer('netz'))

    def test_verschiedene_namen_verschiedene_schloesser(self):
        """DER GRUND, WARUM ES DIESE KLASSE GIBT.

        Mit EINEM Schloss für alles wartete jede Anfrage auf die 1,21 s der
        Catmull-Clark-Unterteilung — auch die, die nur Morphdaten wollte.
        """
        schloss = Ladeschloss()
        self.assertIsNot(schloss.fuer('netz'), schloss.fuer('unterteiler'))

    def test_derselbe_faden_darf_zweimal_hinein(self):
        """`unterteiler()` braucht beim Füllen `netzdaten()` — RLock, nicht Lock."""
        schloss = Ladeschloss().fuer('netz')
        with schloss:
            self.assertTrue(schloss.acquire(blocking=False),
                            'ein einfacher Lock würde sich hier selbst sperren')
            schloss.release()

    def test_gebaut_wird_genau_einmal(self):
        """Der zweite Blick INNERHALB des Schlosses ist der Punkt.

        Zwei Fäden treffen gleichzeitig ein; der erste baut. Der zweite darf
        NICHT noch einmal bauen, auch wenn er beim ersten Blick nichts sah.
        """
        schloss = Ladeschloss()
        wert = {}
        gebaut = []
        losgehts = threading.Event()

        def bauen():
            gebaut.append(1)
            time.sleep(0.05)          # der zweite Faden laeuft hier auf
            wert['x'] = 'fertig'
            return wert['x']

        def holen():
            losgehts.wait()
            schloss.einmal('x', lambda: wert.get('x'), bauen)

        faeden = [threading.Thread(target=holen) for _ in range(4)]
        for faden in faeden:
            faden.start()
        losgehts.set()
        for faden in faeden:
            faden.join()
        self.assertEqual(len(gebaut), 1,
                         'gebaut wurde %dx statt einmal' % len(gebaut))

    def test_vorhandenes_wird_nicht_neu_gebaut(self):
        schloss = Ladeschloss()
        gebaut = []
        ergebnis = schloss.einmal('x', lambda: 'schon da',
                                  lambda: gebaut.append(1))
        self.assertEqual(ergebnis, 'schon da')
        self.assertEqual(gebaut, [])
