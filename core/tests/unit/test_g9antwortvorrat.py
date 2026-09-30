# -*- coding: utf-8 -*-
u"""Der Antwortvorrat legt jeden Inhalt EINMAL ab (`g9antwortvorrat.py`, 30.09.2026).

Edgar: „warum löschst du keine Dubletten". Gemessen: 105 Dateien, 1.569 MB, nur 53
verschiedene Inhalte; nach dem ersten Umbau (Fassungsordner) in EINER Fassung noch 64
Dateien, davon 42 Dubletten — verschiedene Anfragen, dasselbe Netz. Dazu 21 `.tmp`-Leichen
(327 MB, bis 11,7 Tage alt).

Geprüft in einem eigenen Ordner unter `ProjektTemp` (nie im echten Vorrat): gleicher
Inhalt unter zwei Schlüsseln belegt die Platte einmal, beide Schlüssel lesen ihn; der Putz
räumt fremde Fassungen, alte Leichen, verwaiste Inhalte und nach Alter — aber nichts, was
jünger ist als die Schonfrist, und keinen Inhalt, auf den noch ein Verweis zeigt.
"""
import os
import shutil
import time
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.g9antwortvorrat import G9antwortvorrat
from core.dienste.g9vorratputz import G9vorratputz
from core.projekt_temp import ProjektTemp


class Vorrat(G9antwortvorrat):
    u"""Eigene Unterklasse: eigener Speicher, eigener Ordner."""
    _speicher = type(G9antwortvorrat._speicher)()


class AblageTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = Path(ProjektTemp.ordner(prefix='antwortvorrat_'))
        self.addCleanup(shutil.rmtree, self.ordner, True)
        patch = mock.patch.object(Vorrat, 'wurzel', classmethod(lambda cls: self.ordner))
        patch.start()
        self.addCleanup(patch.stop)
        Vorrat._speicher.clear()

    def fassung(self):
        return self.ordner / Vorrat.fassungsmarke()

    def test_1_gleicher_inhalt_liegt_einmal(self):
        Vorrat._schreiben('kleid_a', b'NETZ' * 1000)
        Vorrat._schreiben('kleid_b', b'NETZ' * 1000)
        Vorrat._schreiben('kleid_c', b'ANDERS' * 1000)
        inhalte = list((self.fassung() / Vorrat.INHALT).glob('*' + Vorrat.ENDUNG))
        verweise = list(self.fassung().glob('*' + Vorrat.VERWEIS))
        self.assertEqual(len(inhalte), 2)
        self.assertEqual(len(verweise), 3)

    def test_2_jeder_schluessel_liest_seinen_inhalt(self):
        Vorrat._schreiben('kleid_a', b'NETZ' * 1000)
        Vorrat._schreiben('kleid_b', b'NETZ' * 1000)
        Vorrat._speicher.clear()                       # von der Platte, nicht aus dem Speicher
        self.assertEqual(Vorrat.holen('kleid_a'), b'NETZ' * 1000)
        self.assertEqual(Vorrat.holen('kleid_b'), b'NETZ' * 1000)
        self.assertIsNone(Vorrat.holen('kleid_fehlt'))

    def test_3_das_schema_steht_in_der_fassungsmarke(self):
        u"""Ein neues Ablageformat macht den alten Ordner zur fremden Fassung."""
        alt = Vorrat.fassungsmarke()
        with mock.patch.object(Vorrat, 'SCHEMA', Vorrat.SCHEMA + 1):
            self.assertNotEqual(Vorrat.fassungsmarke(), alt)


class PutzTest(SimpleTestCase):
    databases = set()
    FRIST = 300.0

    def setUp(self):
        self.ordner = Path(ProjektTemp.ordner(prefix='vorratputz_'))
        self.addCleanup(shutil.rmtree, self.ordner, True)

    def datei(self, pfad, inhalt=b'x', alter_s=0.0):
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_bytes(inhalt)
        zeit = time.time() - alter_s
        os.utime(pfad, (zeit, zeit))
        return pfad

    def test_1_fremde_fassungen_und_alte_leichen_gehen(self):
        alt = self.datei(self.ordner / 'fALT' / 'inhalt' / 'a.hbm', alter_s=3600)
        jung = self.datei(self.ordner / 'fJUNG' / 'inhalt' / 'b.hbm', alter_s=10)
        eigen = self.datei(self.ordner / 'fEIGEN' / 'inhalt' / 'c.hbm', alter_s=3600)
        leiche = self.datei(self.ordner / 'x.json.123.tmp', b'L' * 50, alter_s=3600)
        frisch = self.datei(self.ordner / 'y.json.456.tmp', alter_s=5)
        G9vorratputz.fremde_fassungen(self.ordner, 'fEIGEN', self.FRIST)
        self.assertFalse(alt.exists(), 'alte fremde Fassung')
        self.assertTrue(jung.exists(), 'junge fremde Fassung (Autoreload) bleibt')
        self.assertTrue(eigen.exists(), 'die eigene Fassung fasst dieser Schritt nicht an')
        self.assertFalse(leiche.exists(), 'eine .tmp von vor einer Stunde ist eine Leiche')
        self.assertTrue(frisch.exists(), 'eine junge .tmp gehört einem laufenden Faden')

    def test_2_verwaiste_inhalte_und_leere_verweise_gehen(self):
        f = self.ordner / 'fEIGEN'
        waise = self.datei(f / 'inhalt' / 'waise.hbm', alter_s=3600)
        jungwaise = self.datei(f / 'inhalt' / 'jung.hbm', alter_s=5)
        gebraucht = self.datei(f / 'inhalt' / 'da.hbm', alter_s=3600)
        self.datei(f / 'k1.ref', b'da', alter_s=3600)
        leer = self.datei(f / 'k2.ref', b'fehlt', alter_s=3600)
        G9vorratputz.eigene(f, 10 ** 9, self.FRIST, 'inhalt', '.hbm', '.ref')
        self.assertFalse(waise.exists())
        self.assertTrue(jungwaise.exists(), 'Inhalt vor seinem Verweis (Schreibfaden) bleibt')
        self.assertTrue(gebraucht.exists())
        self.assertFalse(leer.exists(), 'Verweis ins Leere')

    def test_3_nach_alter_zaehlt_der_inhalt_einmal(self):
        u"""Zwei Verweise auf denselben Inhalt: der ältere geht, der Inhalt bleibt — er
        wird noch gebraucht. Erst wenn kein Verweis mehr zeigt, geht der Inhalt."""
        f = self.ordner / 'fEIGEN'
        a = self.datei(f / 'inhalt' / 'a.hbm', b'A' * 100, alter_s=900)
        b = self.datei(f / 'inhalt' / 'b.hbm', b'B' * 100, alter_s=900)
        alt_a = self.datei(f / 'alt_a.ref', b'a', alter_s=900)
        neu_a = self.datei(f / 'neu_a.ref', b'a', alter_s=60)
        alt_b = self.datei(f / 'alt_b.ref', b'b', alter_s=800)
        belegt = G9vorratputz.eigene(f, 150, self.FRIST, 'inhalt', '.hbm', '.ref')
        self.assertLessEqual(belegt, 150)
        self.assertFalse(alt_a.exists(), 'ältester Verweis geht zuerst')
        self.assertTrue(a.exists(), 'Inhalt a hat noch einen Verweis')
        self.assertFalse(alt_b.exists())
        self.assertFalse(b.exists(), 'Inhalt b hat keinen Verweis mehr')
        self.assertTrue(neu_a.exists())
