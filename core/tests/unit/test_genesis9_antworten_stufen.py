# -*- coding: utf-8 -*-
u"""Strg+Alt+H in 1–2 s (18.09.2026 nachts): fertige Antworten je Stellung,
Kollision in zwei Stufen, Merker je Prozess — alles mit Kunstdaten, ohne
Bibliothek.

1. `G9antworten.liefern`: gleicher Rumpf → zweite Antwort aus dem Vorrat
   (`bauen` läuft einmal), anderer Rumpf / andere Stufe / anderer Eintrag →
   neuer Schlüssel; die Fassung steckt im Schlüssel; eine Fehlerantwort
   geht durch und wird nicht gemerkt; ausserhalb des Servers wird nichts
   vorausgerechnet.
2. `G9antwortvorrat`: Platte überlebt den Speicher (Speicher leeren → aus
   der Datei), `PLATTE_MB` dünnt die ältesten aus, `vergessen` räumt.
3. `G9antworten.rechnen`: zwei Fäden, ein Schlüssel — `bauen` läuft einmal,
   der zweite wartet und bekommt dieselben Bytes.
4. `G9kollision.stufenweise`: Käfig weit draussen → Browserpunkte sind die
   reine Unterteilung, kein `hinaus`; ein Käfigpunkt in der Haut → Käfig
   gehoben, feiner Durchgang nur auf den betroffenen Browserpunkten, danach
   liegt kein Punkt innen.
5. `G9formeln`: `knochen()`/`posen()`/`morphwerte()` rechnen je Instanz
   einmal; `morphwerte()` liefert eine Kopie.
6. `G9formung.gemerkt`: gleiche Regler → dieselbe Instanz, andere → neue;
   die Punkte sind schreibgeschützt.

Sabotage-Gegenproben: `cls.holen(schluessel)` in `liefern` weg → Fall 1 rot;
`nahe.any()` in `stufenweise` immer True → Fall 4 („kein hinaus") rot.
"""
import json
import tempfile
import threading
from pathlib import Path
from unittest import mock

import numpy as np
from django.http import HttpResponse, JsonResponse
from django.test import SimpleTestCase

from core.dienste import g9antworten, netzstufenwahl
from core.dienste.g9antworten import G9antworten
from core.dienste.g9antwortvorrat import G9antwortvorrat
from Genesis9 import formeln, pfade
from Genesis9.formeln import G9formeln
from Genesis9.formung import G9formung
from Genesis9.kollision import G9kollision


class _Stufe:
    u"""Eine Unterteilung als Attrappe: jeder Käfigpunkt bekommt zwei
    Browserpunkte (sich selbst und die Mitte zum nächsten)."""

    stufen = 1

    def punkte(self, roh):
        roh = np.asarray(roh, dtype=np.float64)
        mitte = 0.5 * (roh + np.roll(roh, -1, axis=0))
        return np.vstack([roh, mitte])

    def skalar(self, werte):
        werte = np.asarray(werte, dtype=np.float64)
        return np.concatenate([werte, np.maximum(werte, np.roll(werte, -1))])


class AntwortenStufenTest(SimpleTestCase):

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.ablage = Path(self.ordner.name)
        self._patches = [
            mock.patch.object(pfade.G9pfade, 'ablage', return_value=self.ablage),
            mock.patch.object(G9antworten, '_speicher',
                              G9antwortvorrat._speicher.__class__()),
            mock.patch.object(G9antworten, '_laufend', {}),
            mock.patch.object(G9antworten, '_auftraege', {}),
            mock.patch.object(G9antworten, 'voraus_an', False),
            # Platte im Test sofort, nicht im Faden — sonst schreibt der noch,
            # wenn `tearDown` den Ordner wegraeumt.
            mock.patch.object(G9antworten, 'merken', classmethod(
                lambda cls, schluessel, daten, platte=True: (
                    cls._im_speicher(schluessel, daten),
                    platte and cls._schreiben(schluessel, daten)))),
        ]
        for p in self._patches:
            p.start()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.ordner.cleanup()

    @staticmethod
    def _mit_stufe(gewaehlt, fn):
        marke = netzstufenwahl.Netzstufenwahl._gewaehlt.set(gewaehlt)
        try:
            return fn()
        finally:
            netzstufenwahl.Netzstufenwahl._gewaehlt.reset(marke)

    # ---------------------------------------------------------------- 1

    def test_1_liefern_aus_dem_vorrat(self):
        zaehler = {'n': 0}

        def bauen():
            zaehler['n'] += 1
            return {'punkte': [1, 2, 3], 'n': zaehler['n']}

        rumpf = {'regler': {'a': 0.5}}

        def liefern(stufe, r=rumpf, b=bauen, **mehr):
            return self._mit_stufe(
                stufe, lambda: G9antworten.liefern('koerper', 'x', r, b, **mehr))

        a = liefern(None)
        b = liefern(None, dict(rumpf))
        self.assertEqual(zaehler['n'], 1)
        self.assertEqual(a.content, b.content)
        self.assertEqual(json.loads(a.content)['n'], 1)
        self.assertEqual(a['Content-Type'], 'application/json')
        # andere Stufe, anderer Rumpf, anderer Eintrag: je ein neuer Bau
        liefern(3)
        liefern(None, {'regler': {'a': 0.6}})
        liefern(None, eintrag={'regler': {}})
        self.assertEqual(zaehler['n'], 4)
        # die Fassung steckt im Schluessel
        s1 = G9antworten.schluessel('koerper', 'x', rumpf, None)
        with mock.patch.object(G9antworten, '_fassung', G9antworten.fassung() + 1):
            s2 = G9antworten.schluessel('koerper', 'x', rumpf, None)
        self.assertNotEqual(s1, s2)
        self.assertTrue(s1.startswith('koerper_x_'))
        # Fehlerantwort: durchgereicht, nicht gemerkt
        fehler = JsonResponse({'fehler': 'kaputt'}, status=500)
        r = self._mit_stufe(None, lambda: G9antworten.liefern(
            'kleid', 'y', rumpf, lambda: fehler))
        self.assertIs(r, fehler)
        self.assertIsNone(G9antworten.holen(
            G9antworten.schluessel('kleid', 'y', rumpf, None)))
        self.assertEqual(G9antworten._auftraege, {})     # voraus_an False: kein Auftrag

    # ---------------------------------------------------------------- 2

    def test_2_platte_und_ausduennen(self):
        daten = b'{"a":1}'
        G9antworten.merken('probe_a', daten, platte=False)
        G9antworten._schreiben('probe_a', daten)
        with G9antworten._schloss:
            G9antworten._speicher.clear()
        self.assertEqual(G9antworten.holen('probe_a'), daten)
        self.assertTrue((self.ablage / 'antworten' / 'probe_a.json').is_file())
        with mock.patch.object(G9antworten, 'PLATTE_MB', 0):
            G9antworten._schreiben('probe_b', b'x' * 10)
        # Deckel 0 MB: alles ueber dem Deckel fliegt, die aelteste zuerst
        self.assertFalse((self.ablage / 'antworten' / 'probe_a.json').is_file())
        G9antworten.vergessen()
        self.assertEqual(list((self.ablage / 'antworten').glob('*.json')), [])

    # ---------------------------------------------------------------- 3

    def test_3_gleicher_schluessel_rechnet_einmal(self):
        frei = threading.Event()
        zaehler = {'n': 0}

        def bauen():
            zaehler['n'] += 1
            frei.wait(5)
            return {'wert': 42}

        ergebnisse = []

        def lauf():
            ergebnisse.append(G9antworten.rechnen('probe_3', bauen, platte=False))

        f1 = threading.Thread(target=lauf)
        f2 = threading.Thread(target=lauf)
        f1.start()
        f2.start()
        frei.set()
        f1.join(5)
        f2.join(5)
        self.assertEqual(zaehler['n'], 1)
        self.assertEqual(ergebnisse[0], ergebnisse[1])
        self.assertEqual(json.loads(ergebnisse[0]), {'wert': 42})
        self.assertEqual(G9antworten._laufend, {})

    # ---------------------------------------------------------------- 4

    def test_4_kollision_in_zwei_stufen(self):
        # Koerper: eine Ebene y = 0 mit Normale +y
        xs, zs = np.meshgrid(np.linspace(-1, 1, 21), np.linspace(-1, 1, 21))
        koerper = np.column_stack([xs.ravel(), np.zeros(xs.size), zs.ravel()])
        normalen = np.tile([0.0, 1.0, 0.0], (len(koerper), 1))
        stufe = _Stufe()
        weit = np.array([[0.0, 0.05, 0.0], [0.1, 0.06, 0.0],
                         [0.2, 0.05, 0.1], [0.3, 0.07, 0.1]])
        with mock.patch.object(G9kollision, 'hinaus', wraps=G9kollision.hinaus) as h:
            fein, kaefig = G9kollision.stufenweise(weit, stufe, koerper, normalen)
            self.assertEqual(h.call_count, 0)
        np.testing.assert_allclose(fein, stufe.punkte(weit))
        np.testing.assert_allclose(kaefig, weit)
        # ein Kaefigpunkt IN der Haut (y < 0)
        nah = weit.copy()
        nah[1, 1] = -0.002
        with mock.patch.object(G9kollision, 'hinaus', wraps=G9kollision.hinaus) as h:
            fein, kaefig = G9kollision.stufenweise(nah, stufe, koerper, normalen)
            self.assertEqual(h.call_count, 2)       # Kaefig + feiner Durchgang
            betroffen = h.call_args_list[1].args[0]
        self.assertGreaterEqual(float(kaefig[1, 1]), G9kollision.ABSTAND - 1e-9)
        self.assertEqual(G9kollision.innen(fein, koerper, normalen), 0)
        self.assertLess(len(betroffen), len(fein))      # nur die nahen Browserpunkte
        self.assertGreater(len(betroffen), 0)
        # HD-Beitrag geht auf die Browserpunkte
        hd = np.full((2 * len(weit), 3), 0.01)
        fein_hd, _ = G9kollision.stufenweise(weit, stufe, koerper, normalen, hd=hd)
        np.testing.assert_allclose(fein_hd, stufe.punkte(weit) + 0.01)

    # ---------------------------------------------------------------- 5

    def test_5_formeln_rechnen_einmal(self):
        ablage = mock.Mock()
        ablage.kanaele = {'m': {'vorgabe': 0.0, 'min': -1.0, 'max': 1.0,
                                'formeln': []}}
        ablage.hat_deltas = lambda name: True
        knochen = [('l_hand', 'center_point', 'x',
                    {'ops': [{'op': 'push', 'val': 2.0}]})]
        posen = [('hip', 'scale/general', {'ops': [{'op': 'push', 'val': 1.5}]})]
        with mock.patch.object(formeln.G9formeln, '_index', None), \
                mock.patch.object(formeln.G9formeln, 'index',
                                  return_value=({}, knochen, posen)):
            f = G9formeln({'m': 0.25}, ablage=ablage)
            with mock.patch.object(f, '_knochen', wraps=f._knochen) as k, \
                    mock.patch.object(f, '_posen', wraps=f._posen) as p:
                self.assertEqual(f.knochen()['l_hand']['center_point'], [2.0, 0.0, 0.0])
                self.assertEqual(f.knochen(), f.knochen())
                # Summenformel auf die Vorgabe 1 der Skalierung: 1 + 1.5
                self.assertEqual(f.posen()['hip']['scale/general'], 2.5)
                f.posen()
                self.assertEqual((k.call_count, p.call_count), (1, 1))
            a = f.morphwerte()
            a['m'] = 99.0
            self.assertEqual(f.morphwerte()['m'], 0.25)  # Kopie, kein Durchgriff

    # ---------------------------------------------------------------- 6

    def test_6_stellung_je_fingerabdruck(self):
        with mock.patch.object(G9formung, '_gemerkt', {}):
            a = G9formung.gemerkt({'m': 0.5})
            b = G9formung.gemerkt({'m': 0.5})
            c = G9formung.gemerkt({'m': 0.6})
            self.assertIs(a, b)
            self.assertIsNot(a, c)
            with mock.patch.object(G9formung, 'GEMERKT_MAX', 2):
                G9formung.gemerkt({'m': 0.7})
                self.assertEqual(len(G9formung._gemerkt), 2)
        with mock.patch.object(G9formung, 'morphpunkte',
                               return_value=np.ones((3, 3))), \
                mock.patch.object(G9formung, 'matrizen',
                                  return_value=mock.Mock(leer=True)):
            f = G9formung({'m': 0.5})
            p = f.punkte()
            self.assertFalse(p.flags.writeable)
            with self.assertRaises(ValueError):
                p[0, 0] = 5.0
