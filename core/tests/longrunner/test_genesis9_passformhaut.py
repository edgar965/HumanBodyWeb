# -*- coding: utf-8 -*-
u"""Genesis 9 gegen die installierte Daz-Bibliothek (20.09.2026, Edgar mit Bild:
„T-Shirt bei Animation kaputt" — Olesia1 traegt das Base Shirt mit Laenge
−14,5 cm und Weite −2,7 cm):

1. Ein Stueck MIT Passform bekommt eine eigene Haut (`G9passformhaut`), und
   die passt an seinem VERSCHOBENEN Saum besser zur Haut des Koerpers darunter
   als die Haut der Ruhelage: gemessen als mittlerer Gewichtsunterschied
   (Summe |w_stueck − w_koerper| ueber die Knochen) zum naechsten Koerperpunkt
   an den untersten 5 % der Kaefigpunkte. Vor dem Umbau trug der Saum an der
   Taille die Gewichte der Huefte.
2. Die Stueckfelder mit Passform liegen unter eigenem Namen (`_l-14.5_w-2.7`)
   und unterscheiden sich von denen ohne — die Projektion ist eine andere.
3. Der Endpunkt `garderobe/g9_base_shirt/felder/gelenke/?laenge=&weite=`
   antwortet mit `passform`, das Kleidnetz mit Passform traegt die
   Passformhaut (andere Gewichte als ohne).

LongRunner: Stueckfelder des Shirts (117 JCMs, Sekunden). Ohne Bibliothek
uebersprungen.

Sabotage-Gegenprobe: `folgernetz` gibt `stufe.haut` statt
`passform.browserhaut(stufe)` -> Fall 3 rot (Gewichte gleich); `G9passformhaut`
mit `folger.projektion()` statt `projizieren(self.punkte)` -> Fall 1 rot.
"""

import base64
import json
import unittest

import numpy as np
from django.test import Client, SimpleTestCase
from Genesis9.basisnetz import G9basisnetz
from Genesis9.garderobe import G9garderobe
from Genesis9.haut import G9haut
from Genesis9.pfade import G9pfade
from Genesis9.stueckfelder import G9stueckfelder
from scipy.spatial import cKDTree

from core.api.g9felder import G9felderapi

KENNUNG = 'g9_base_shirt'
PASSFORM = {'passform:laenge': -14.5, 'passform:weite': -2.7}


def _hautgewichte(antwort):
    u"""`{knochen, index (n, 4), gewicht (n, 4)}` aus der kompakten Antwort (`u16u8`)."""
    index = np.frombuffer(base64.b64decode(antwort['skin_indices']), dtype=np.uint16)
    gewicht = np.frombuffer(base64.b64decode(antwort['skin_weights']), dtype=np.uint8)
    return {'knochen': antwort['knochen'], 'index': index.reshape(-1, 4).astype(np.int64),
            'gewicht': gewicht.reshape(-1, 4).astype(np.float64) / 255.0}


def _gewichtskarte(haut, n):
    u"""(n, Knochen) dichte Gewichte aus `{knochen, index, gewicht}` oder `G9haut`."""
    index = np.asarray(haut['index'] if isinstance(haut, dict) else haut.index)
    gewicht = np.asarray(haut['gewicht'] if isinstance(haut, dict) else haut.gewicht,
                         dtype=np.float64)
    knochen = haut['knochen'] if isinstance(haut, dict) else haut.knochen
    aus = np.zeros((n, len(knochen)))
    for k in range(index.shape[1]):
        np.add.at(aus, (np.arange(n), index[:n, k]), gewicht[:n, k])
    return aus


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class PassformhautTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.folger = next(f for f, lage in G9garderobe.teile(KENNUNG) if lage is None)
        cls.stand = cls.folger.passformhaut(PASSFORM)

    def _unterschied(self, haut, punkte):
        u"""Mittlerer Gewichtsunterschied der untersten 5 % von `punkte` zum
        naechsten Koerperpunkt des Grundnetzes."""
        koerper = G9haut.holen()
        basis = G9basisnetz.holen().punkte
        y = punkte[:, 1]
        saum = np.flatnonzero(y <= np.quantile(y, 0.05))
        _d, naechster = cKDTree(basis).query(punkte[saum])
        stueck = _gewichtskarte(haut, len(punkte))[saum]
        unten = _gewichtskarte(koerper, len(basis))[naechster]
        self.assertEqual(list(haut.knochen if not isinstance(haut, dict) else haut['knochen']),
                         list(koerper.knochen))
        return float(np.abs(stueck - unten).sum(axis=1).mean())

    def test_1_saum_traegt_die_haut_unter_dem_verschobenen_kaefig(self):
        self.assertIsNotNone(self.stand)
        self.assertEqual(self.stand.schluessel, 'l-14.5_w-2.7')
        # Der Saum wanderte hoch: die untersten Punkte liegen hoeher als in Ruhe.
        self.assertGreater(self.stand.punkte[:, 1].min(), self.folger.punkte[:, 1].min() + 0.08)
        neu = self._unterschied(self.stand.haut, self.stand.punkte)
        alt = self._unterschied(self.folger.haut, self.stand.punkte)
        self.assertLess(neu, 0.25, 'Passformhaut am Saum: %.3f' % neu)
        self.assertLess(neu, alt, 'Passformhaut %.3f, Ruhehaut %.3f am verschobenen Saum' % (neu, alt))
        # Gemerkt: derselbe Stand beim zweiten Mal.
        self.assertIs(self.folger.passformhaut(dict(PASSFORM)), self.stand)
        self.assertIsNone(self.folger.passformhaut({}))

    def test_2_stueckfelder_je_passform(self):
        kanaele = G9felderapi.kanaele('gelenke')
        ohne = G9stueckfelder.holen('gelenke', kanaele, KENNUNG, 1)
        mit = G9stueckfelder.holen('gelenke', kanaele, KENNUNG, 1, PASSFORM)
        self.assertIsNone(ohne.passform)
        self.assertEqual(mit.passform, (-14.5, -2.7))
        self.assertTrue(G9stueckfelder.pfad('gelenke', KENNUNG, 1, 'npz', mit.passform).is_file())
        gemeinsam = sorted(set(ohne.teile[0]) & set(mit.teile[0]))
        self.assertGreater(len(gemeinsam), 20)
        verschieden = 0
        for kanal in gemeinsam:
            n1, d1 = ohne.teile[0][kanal]
            n2, d2 = mit.teile[0][kanal]
            if len(n1) != len(n2) or not np.array_equal(n1, n2) or not np.allclose(d1, d2):
                verschieden += 1
        self.assertGreater(verschieden, len(gemeinsam) // 2)

    def test_3_endpunkte_mit_passform(self):
        client = Client()
        antwort = client.get('/api/character/genesis9-figur/garderobe/%s/felder/gelenke/'
                             '?stufen=1&laenge=-14.5&weite=-2.7' % KENNUNG)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['passform'], [-14.5, -2.7])
        adresse = '/api/character/genesis9-figur/garderobe/%s/netz/?stufen=1' % KENNUNG
        rumpf = {'regler': {'BaseFeminine_figure_ctrl_Character': 1}}
        teile = []
        for stueckregler in ({}, PASSFORM):
            antwort = client.post(adresse, data=json.dumps(dict(rumpf, regler_stueck=stueckregler)),
                                  content_type='application/json')
            self.assertEqual(antwort.status_code, 200, antwort.content[:300])
            teile.append(antwort.json()['teile'][0])
        ohne, mit = teile
        h1 = _hautgewichte(ohne['hautgewichte'])
        h2 = _hautgewichte(mit['hautgewichte'])
        self.assertEqual(h1['knochen'], h2['knochen'])
        self.assertFalse(np.array_equal(h1['index'], h2['index'])
                         and np.allclose(h1['gewicht'], h2['gewicht']))
