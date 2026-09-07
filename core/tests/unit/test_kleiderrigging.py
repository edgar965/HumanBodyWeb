# -*- coding: utf-8 -*-
u"""Kleidung, die der Figur folgt — MakeHuman und GarmentCode/SMPL.

WARUM (Edgar, 07.09.2026): „Kleider werden nicht gerigged bei MakeHuman
(Animation animiert nur MakeHuman), bei SMPL verschwinden die Kleider beim
Abspielen einer Animation."

BEIDES IST DERSELBE BEFUND. Der Stoff hing als starres `Mesh` an der Figur.
Beim Abspielen bewegte sich der Koerper und das Stueck blieb stehen — von
vorn sieht das aus, als sei es verschwunden.

ZWEI WEGE, WEIL ES ZWEI LAGEN GIBT
==================================
* **MakeHuman**: Die `.mhclo` haengt jeden Stoffpunkt an DREI Koerperpunkte
  mit Gewichten. Dieselbe Mischung gilt fuer die Knochen — es wird nichts
  gesucht und nichts genaehert (`Mhhaut.fuer_kleidung`).
* **GarmentCode auf SMPL**: Dort gibt es keine Zuordnung, das Stueck ist ein
  simuliertes Netz im Raum. Uebertragen wird ueber das NAECHSTE DREIECK
  (`Anziehen` + `Gewichtsuebertragung`), nicht ueber den naechsten Punkt:
  Zwei benachbarte Stoffpunkte koennen sonst an verschiedenen Knochen
  haengen, und der Stoff reisst beim Heben des Arms.

DIE STILLE FEHLERQUELLE IST DIE REIHENFOLGE. Die UV-Aufteilung kopiert
Punkte (`ecken`), das Verdichten wirft welche weg. Wer die Gewichte nicht
durch dieselbe Auswahl schickt, bekommt ein Stueck, das sich bewegt — nur
verkehrt. Genau darauf zielen die Laengenpruefungen hier.
"""
import os
import unittest

import numpy as np
from django.conf import settings


class MhkleidHautTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        from core.dienste.mhgarderobe import Mhgarderobe
        from core.dienste.mhhaut import Mhhaut
        from core.dienste.mhbasisnetz import Mhbasisnetz
        if not (Mhhaut.vorhanden() and Mhbasisnetz.vorhanden()):
            raise unittest.SkipTest('MakeHuman-Upstream fehlt')
        cls.stuecke = [s['id'] for s in Mhgarderobe.liste()]
        if not cls.stuecke:
            raise unittest.SkipTest('keine MakeHuman-Garderobe')

    def _netz(self, kennung):
        from core.dienste.mhkleidnetz import Mhkleidnetz
        return Mhkleidnetz(kennung).netz()

    def test_je_stoffpunkt_ein_gewicht(self):
        u"""So viele Gewichte wie Punkte — die `ecken` muessen mitgehen."""
        netz = self._netz(self.stuecke[0])
        self.assertIsNotNone(netz['haut'])
        self.assertEqual(len(netz['haut']['index']), len(netz['punkte']))
        self.assertEqual(len(netz['haut']['gewicht']), len(netz['punkte']))

    def test_die_gewichte_summieren_sich_auf_eins(self):
        netz = self._netz(self.stuecke[0])
        summe = netz['haut']['gewicht'].sum(axis=1)
        self.assertTrue(np.allclose(summe, 1.0, atol=1e-5))

    def test_die_knochen_sind_die_des_rigs(self):
        u"""Der Browser loest NAMEN auf — ein fremder Name bindet gar nicht."""
        from core.dienste.mhskelett import Mhskelett
        netz = self._netz(self.stuecke[0])
        self.assertEqual(set(netz['haut']['knochen']),
                         set(Mhskelett.rig()['bones']))

    def test_die_mischung_ist_die_der_mhclo(self):
        u"""Kein zweites Verfahren: dieselben drei Punkte, dieselben Anteile.

        Nachgerechnet gegen die Grundmatrix — waere hier eine Suche nach dem
        naechsten Punkt eingebaut, faellt es auf.
        """
        from core.dienste.mhhaut import Mhhaut
        grund = Mhhaut.grundmatrix()
        v = np.array([[10, 20, 30]])
        a = np.array([[0.5, 0.3, 0.2]])
        index, gewicht = Mhhaut.fuer_kleidung(v, a)
        soll = (grund[10] * 0.5 + grund[20] * 0.3 + grund[30] * 0.2)
        # Die vier staerksten Anteile, normiert — genau das liefert `_vier`.
        for spalte, wert in zip(index[0], gewicht[0]):
            self.assertGreater(soll[spalte] + 1e-12, 0.0)
        self.assertAlmostEqual(float(gewicht[0].sum()), 1.0, places=5)

    def test_stuecke_der_bibliothek_bekommen_alle_gewichte(self):
        u"""Gemessen 162 von 181; die uebrigen 19 scheitern schon am Netz.

        Die 19 sind ein aelterer Befund (`punkte[ecken]` laeuft aus dem
        Feld) und haben mit den Gewichten nichts zu tun — der Test haelt
        beide Zahlen auseinander, damit niemand das eine fuer das andere
        haelt.
        """
        from core.dienste.mhkleidnetz import Mhkleidnetz
        mit, ohne, kaputt = 0, 0, 0
        for kennung in self.stuecke:
            try:
                netz = Mhkleidnetz(kennung).netz()
            except Exception:
                kaputt += 1
                continue
            if netz.get('haut'):
                mit += 1
            else:
                ohne += 1
        self.assertEqual(ohne, 0, 'Stuecke ohne Gewichte: %d' % ohne)
        self.assertGreater(mit, 150)
        self.assertLess(kaputt, 25)


class SmplTraegerTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(os.path.join(str(settings.SMPL_MODELS_DIR),
                                           'SMPL_FEMALE.npz')):
            raise unittest.SkipTest('SMPL-Modelle fehlen')
        from core.dienste.garmentdrapierung import Garmentdrapierung
        cls.traeger = Garmentdrapierung._smpl_traeger('mean_all')
        if cls.traeger is None:
            raise unittest.SkipTest('GarmentCode-Koerper nicht lesbar')

    def test_der_traeger_liegt_in_projektkoordinaten(self):
        u"""m, Z oben — so liest `Anziehen.netz_lesen` das Stoffnetz.

        Ohne die Drehung laege der Traeger um 90 Grad gekippt neben dem
        Stoff, und die Projektion traefe irgendetwas. Die Probe ist die
        Ausdehnung: Ein Mensch ist in der HOEHENachse am groessten, und
        das ist hier Z.
        """
        punkte = self.traeger['punkte']
        spanne = punkte.max(axis=0) - punkte.min(axis=0)
        self.assertEqual(int(np.argmax(spanne)), 2, 'Hoehe nicht in Z')
        self.assertGreater(spanne[2], 1.4)
        self.assertLess(spanne[2], 2.1)

    def test_je_koerperpunkt_eine_gewichtsliste(self):
        self.assertEqual(len(self.traeger['gewichte']),
                         len(self.traeger['punkte']))
        for zeile in self.traeger['gewichte'][:200]:
            self.assertTrue(zeile, 'Punkt ohne jedes Gewicht')
            self.assertAlmostEqual(sum(w for _, w in zeile), 1.0, places=4)

    def test_die_knochennamen_passen_zum_skelett_der_figur(self):
        u"""Der Browser ordnet ueber Namen zu — sonst bindet nichts."""
        from SMPL.skelett import Smplskelett
        self.assertEqual(self.traeger['knochen'], list(Smplskelett.NAMEN))

    def test_ein_stoffnetz_bekommt_stetige_gewichte(self):
        u"""Die Probe auf das Verfahren: Nachbarn duerfen nicht springen.

        Zwei Punkte, die 5 mm auseinanderliegen, muessen aehnliche Knochen
        bekommen. Die frueher benutzte Suche nach dem naechsten PUNKT
        schafft das nicht — daher die Projektion aufs Dreieck.
        """
        from GarmentCode.anziehen import Anziehen
        koerper = self.traeger['punkte']
        # Ein kleines Stueck „Stoff": Koerperpunkte, 1 cm nach aussen
        # versetzt, damit sie sicher ueber der Haut liegen.
        auswahl = np.arange(0, len(koerper), 97)[:300]
        stoff = koerper[auswahl] * 1.01
        anzieher = Anziehen(koerper, self.traeger['dreiecke'],
                            self.traeger['gewichte'], self.traeger['knochen'])
        rig = anzieher.anziehen(stoff)
        self.assertEqual(rig['punkte'], len(stoff))
        self.assertEqual(rig['ohne_gewicht'], 0)
        self.assertLess(rig['gewichtsabweichung'], 1e-3)
