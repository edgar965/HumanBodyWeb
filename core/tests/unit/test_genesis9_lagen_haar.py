# -*- coding: utf-8 -*-
u"""Haar liegt über Kleidung; `_aeussere_stuecke` rechnet nur, wo es etwas zu verdecken gibt (17.10.2026).

WARUM (Edgar mit Bild: „posen dauern irrsinnig lange … arg fehlerhaft, das ist Pose 02 Stretching
G9B"): Mit erhobenen Armen ordnete die Tiefenregel beide Haare (319.503 und 433.212 Punkte) UNTER das
T-Shirt. Das Shirt wurde über die Haare gehoben (Löcher im Bild), und `_aeussere_stuecke` suchte für
jeden Haarpunkt 64 Nachbarn: 20,8 s statt 0,24 s (`ProjektTemp/_wegwerf/posen_lagen_diag.py`).

1. `G9lagenanfrage._haar_aussen`: Fragt ein Kleidungsstück, wandert ein Haar aus `innen` nach
   `aussen`; fragt ein Haar, wandert Kleidung aus `aussen` nach `innen`. Haar gegen Haar und
   Requisiten bleiben, wie die Tiefenregel sie legte.
2. `G9lagenflaeche._aeussere_stuecke` (nur Kandidaten binnen `ZWISCHEN_R`) liefert dasselbe wie die
   alte Rechnung über alle Punkte — hier an Kunstdaten gegen eine Abschrift der alten Schleife. An den
   echten Eingaben der Pose von Hand geprüft: bitgleich (`ProjektTemp/_wegwerf/lagen_gleichheit.py`).
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.kollision import G9kollision  # noqa: E402
from Genesis9.lagen import G9lagen  # noqa: E402

from core.dienste.g9lagenanfrage import G9lagenanfrage  # noqa: E402

from .test_genesis9_lagen import Kunsthaut, gitter  # noqa: E402

ARTEN = {'shirt': 'kleidung', 'hose': 'kleidung', 'haar': 'haar', 'bart': 'haar', 'schwert': 'requisit'}


class HaarAussen(SimpleTestCase):
    databases = set()

    def setUp(self):
        self._patch = mock.patch.object(G9lagenanfrage, '_art', classmethod(lambda cls, k: ARTEN.get(k)))
        self._patch.start()

    def tearDown(self):
        self._patch.stop()

    def test_kleidung_hebt_sich_nicht_ueber_haar(self):
        self.assertEqual(G9lagenanfrage._haar_aussen('shirt', ['hose', 'haar', 'bart'], ['schwert']),
                         (['hose'], ['schwert', 'haar', 'bart']))

    def test_haar_liegt_ueber_kleidung(self):
        self.assertEqual(G9lagenanfrage._haar_aussen('haar', ['bart'], ['shirt', 'schwert']),
                         (['bart', 'shirt'], ['schwert']))

    def test_requisit_bleibt_bei_der_tiefenregel(self):
        self.assertEqual(G9lagenanfrage._haar_aussen('schwert', ['haar', 'shirt'], ['hose']),
                         (['haar', 'shirt'], ['hose']))


class NurKandidaten(SimpleTestCase):
    databases = set()

    @staticmethod
    def alt(lagen, stuecke):
        u"""Die Schleife bis 17.10.2026 (`git show 411b8d0:Genesis9/lagenflaeche.py`), alle Punkte."""
        haut, normalen, baum = lagen.grob
        baeume = [G9kollision.baum(s) for s in stuecke]
        bleiben = []
        for i, eigene in enumerate(stuecke):
            _w, unter = G9kollision.naechste(baum, eigene)
            n = np.asarray(normalen[unter], dtype=np.float64)
            frei = np.ones(len(eigene), dtype=bool)
            for j, andere in enumerate(stuecke):
                if i == j:
                    continue
                k = min(lagen.ZWISCHEN_K, len(andere))
                weite, nachbar = G9kollision.naechste(baeume[j], eigene, k)
                weite, nachbar = weite.reshape(len(eigene), k), nachbar.reshape(len(eigene), k)
                weg = andere[nachbar] - eigene[:, None, :]
                hoeher = np.einsum('nkj,nj->nk', weg, n)
                seitlich = np.linalg.norm(weg - hoeher[..., None] * n[:, None, :], axis=2)
                verdeckt = ((hoeher > lagen.ZWISCHEN_D) & (seitlich <= lagen.LAGE_R)
                            & (weite <= lagen.ZWISCHEN_R))
                frei &= ~verdeckt.any(axis=1)
            bleiben.append(eigene[frei])
        return np.vstack(bleiben)

    def test_gleich_der_alten_rechnung(self):
        lagen = G9lagen(Kunsthaut.koerper())
        zufall = np.random.default_rng(17)
        stuecke = [gitter(0.003, -0.5, 0.5, -0.5, 0.5, 0.02),                 # tief, gross (der BH)
                   gitter(0.008, -0.2, 0.3, -0.2, 0.1, 0.015),                # hoeher, teilweise darueber
                   gitter(0.005, 0.6, 0.9, 0.6, 0.9, 0.02)]                   # weit weg: kein Kandidat
        stuecke = [s + zufall.normal(0, 0.0005, s.shape) for s in stuecke]
        neu = lagen._aeussere_stuecke(stuecke)
        self.assertTrue(np.array_equal(neu, self.alt(lagen, stuecke)))
        # Gegenprobe, dass überhaupt etwas verdeckt wurde: sonst prüfte der Vergleich nur „alles bleibt".
        self.assertLess(len(neu), sum(len(s) for s in stuecke))
