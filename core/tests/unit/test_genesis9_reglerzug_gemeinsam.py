# -*- coding: utf-8 -*-
u"""Ein Reglerzug rechnet jede Zwischengroesse nur einmal und die Bindung in Bloecken (16.10.2026), an Kunstdaten.

WARUM (Edgar, 16.10.2026: „Der Regler soll viel schneller die Figur ändern können. Warum dauert das so lange?"): Ein Reglerzug an Mann1 fragt den Koerper und vier Stuecke
GLEICHZEITIG. Gemessen (`ProjektTemp/_wegwerf/mann_regler/zeit_je_stueck.py`, Anfragen wie der Browser): nacheinander 7,4 s, gleichzeitig ~8,5 s — die vier Anfragen rechneten
dieselbe Koerperflaeche, dieselben Kaefige der anderen Stuecke und dieselbe Stellung (`G9formung`) je noch einmal. Dazu die Bindung an die Koerperdreiecke: 2,5 von 4,2 s des T-Shirts,
weil jedes Zwischenfeld ueber alle 83.347 Punkte auf einmal gerechnet wurde. Danach: nacheinander 5,9 s, gleichzeitig 4,1 s; die Bindung des T-Shirts 1,0 s und bitgleich zur alten
(`bindung_vergleich.py`: `np.array_equal` auf Dreieck, Baryzentrik, Abstand, Mischung — T-Shirt, Boxershorts, Stiefel).

1. `G9oberflaechenbindung.fuer` in vielen kleinen Bloecken (und Threads) = in einem Block, bitgleich.
2. `G9lagenanfrage._kaefig`: vier gleichzeitige Anfragen desselben Kaefigs rechnen ihn einmal; scheitert der Rechner, scheitern alle Wartenden mit demselben Fehler (keiner bleibt haengen).
3. `G9koerpernetz.koerperflaeche`: vier gleichzeitige Anfragen rechnen die Flaeche einmal.
4. `G9formung.formeln`: vier gleichzeitige Zugriffe auf dieselbe Stellung bauen die Formeln einmal.
5. `G9kollision.hinaus`: der zweite Durchgang rechnet nur ueber die bewegten Punkte und ihre Nachbarn — bitgleich zur Rechnung ueber alle Punkte (Mann1: Haar 319.503 Kaefigpunkte,
   0,49 s -> 0,42 s, mit fuenf Durchgaengen 0,97 -> 0,56 s; `kollision_vergleich.py`: T-Shirt, Boxershorts, Haar, Stiefel auf Stufe 0 und 1, Durchgaenge 1/3/5/Vorgabe, skalarer und
   punktweiser Abstand, alles `np.array_equal`).
6. `G9hebevorrat`: gleiche Punkte aus gleicher Haut werden einmal gehoben (Haar 0,42 s) — sonst hob jede der vier Anfragen ihren eigenen Kaefig UND die der anderen. Im selben Prozess abwechselnd
   gemessen (`fluss_ab.py`, 5 Runden, Median): ohne beides 2,89 s, nur Vorrat 2,63 s, nur Kollision 2,64 s, beides 2,42 s.

Sabotage-Gegenprobe (nicht gefahren): in `fuer` `BLOCK` auf einen Wert, der die Zeilen vertauscht (`grenzen` ohne `min`) → Fall 1 rot; das Warten (`rechnet.wait()`) in `_kaefig` streichen → Fall 2 zaehlt vier;
das Schloss in `koerperflaeche`/`formeln` streichen → Fall 3/4 zaehlen mehr als eins; in `_betroffene` die Nachbarn weglassen (`bewegt` allein) → Fall 5c rot (Fall 5 bleibt gruen: auf Kugel, Schale und Dach aendert die Nachbarschaft nichts, gemessen an 24 Einstellungen mit je 6 Seeds
mit `ProjektTemp/_wegwerf/mann_regler/sabotage_suche.py`; erst im steilen V-Tal (2–5 Punkte weichen ab) landet ein nach aussen geschobener Punkt auf der anderen Wand wieder im Koerper); im Vorrat den Inhalt aus dem Schluessel nehmen
(nur `id(grob[0])`) → Fall 6b rechnet fuer verschiedene Punkte denselben Wert. Tests geschrieben, nicht gelaufen (nur auf Ansage).
"""
import threading
import time
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from scipy.spatial import cKDTree

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from core.dienste.g9lagenanfrage import G9lagenanfrage  # noqa: E402
from Genesis9.formung import G9formung  # noqa: E402
from Genesis9.hebevorrat import G9hebevorrat  # noqa: E402
from Genesis9.kollision import G9kollision  # noqa: E402
from Genesis9.koerpernetz import G9koerpernetz  # noqa: E402
from Genesis9.lagen import G9lagen  # noqa: E402
from Genesis9.oberflaechenbindung import G9oberflaechenbindung  # noqa: E402


def gleichzeitig(anzahl, aufruf):
    u"""`aufruf()` auf `anzahl` Threads, alle gleichzeitig losgelassen; `[(Ergebnis | Ausnahme)]`."""
    start = threading.Barrier(anzahl)
    aus = [None] * anzahl

    def lauf(nr):
        start.wait()
        try:
            aus[nr] = aufruf()
        except Exception as fehler:  # noqa: BLE001 — die Ausnahme ist das Ergebnis, das der Test prueft
            aus[nr] = fehler
    faeden = [threading.Thread(target=lauf, args=(i,)) for i in range(anzahl)]
    [f.start() for f in faeden]
    [f.join(30) for f in faeden]
    return aus


def gitter_koerper(n=12):
    xs, ys = np.meshgrid(np.arange(n), np.arange(n))
    P = np.stack([xs.ravel(), ys.ravel(), np.sin(xs.ravel() * 0.4) * 0.3], axis=1).astype(float)
    D = []
    for j in range(n - 1):
        for i in range(n - 1):
            a = j * n + i
            D += [[a, a + 1, a + n + 1], [a, a + n + 1, a + n]]
    N = np.tile([0.0, 0.0, 1.0], (len(P), 1))
    return G9oberflaechenbindung(P, N, np.array(D), cKDTree(P.astype(np.float32)), stufen=1), P


class BindungInBloeckenTest(SimpleTestCase):
    databases = set()

    def test_1_viele_bloecke_geben_dasselbe_wie_ein_block(self):
        ein, _P = gitter_koerper()
        viele, _P = gitter_koerper()
        ein.BLOCK = 10 ** 6
        viele.BLOCK = 7
        rng = np.random.default_rng(11)
        x = rng.uniform(0.2, 10.8, 400)
        stoff = np.column_stack([x, rng.uniform(0.2, 10.8, 400), np.sin(x * 0.4) * 0.3 + rng.uniform(-0.03, 0.06, 400)])   # nahe der Flaeche (z = 0,3 sin 0,4 x)
        a, b = ein.fuer(stoff), viele.fuer(stoff)
        for feld in ('dreieck', 'bary', 'abstand', 'mischung'):
            self.assertTrue(np.array_equal(a[feld], b[feld]), feld)
        self.assertGreater(int((a['mischung'] > 0).sum()), 100, 'die Probe bindet wirklich Punkte')
        self.assertEqual(a['stufen'], b['stufen'])


class EinmalRechnenTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        G9lagenanfrage._kaefige.clear()
        G9lagenanfrage._rechnend.clear()
        G9koerpernetz._flaechen.clear()

    def test_2_ein_kaefig_wird_von_einem_thread_gerechnet(self):
        anfrage = G9lagenanfrage({}, formung=mock.Mock(fingerabdruck=lambda: 'f'), koerper=(None, None, None), grob=(None, None, None))
        zaehler = []

        def kaefig(kennung, formung, stile, regler):
            zaehler.append(kennung)
            time.sleep(0.2)
            return np.ones((3, 3))
        with mock.patch.object(G9lagen, 'kaefig', side_effect=kaefig):
            aus = gleichzeitig(4, lambda: anfrage._kaefig('jeans', ['a'], {}))
        self.assertEqual(zaehler, ['jeans'], 'einmal gerechnet, nicht viermal')
        self.assertTrue(all(isinstance(a, np.ndarray) and a.shape == (3, 3) for a in aus), aus)
        self.assertEqual(G9lagenanfrage._rechnend, {}, 'nichts bleibt als „rechnet gerade“ stehen')

    def test_2b_scheitert_der_rechner_scheitern_alle_und_keiner_haengt(self):
        anfrage = G9lagenanfrage({}, formung=mock.Mock(fingerabdruck=lambda: 'f'), koerper=(None, None, None), grob=(None, None, None))
        with mock.patch.object(G9lagen, 'kaefig', side_effect=ValueError('unbekannt')):
            aus = gleichzeitig(4, lambda: anfrage._kaefig('hut', [], {}))
        self.assertTrue(all(isinstance(a, ValueError) for a in aus), aus)
        self.assertEqual(G9lagenanfrage._rechnend, {})

    def test_3_die_koerperflaeche_wird_einmal_gerechnet(self):
        formung = mock.Mock(fingerabdruck=lambda: 'fa', punkte=lambda: np.zeros((4, 3)), boden=lambda: 0.0)
        zaehler = []

        def fein(self_, basis, stufe, punkte):
            zaehler.append(1)
            time.sleep(0.2)
            return np.zeros((4, 3))
        stufe = mock.Mock(normalen=lambda p, f: np.zeros((4, 3)))
        basis = mock.Mock(netzstufe=lambda s: stufe)
        with mock.patch.object(G9koerpernetz, '_fein', fein), mock.patch('Genesis9.koerpernetz.G9basisnetz.holen', return_value=basis):
            netz = G9koerpernetz(formung, eintrag={'name': 'kunst'}, stufen=1)
            aus = gleichzeitig(4, netz.koerperflaeche)
        self.assertEqual(len(zaehler), 1)
        self.assertTrue(all(a is aus[0] for a in aus), 'alle bekommen dasselbe Ergebnis')

    def test_4_die_formeln_einer_stellung_werden_einmal_gebaut(self):
        zaehler = []

        class Formeln:
            def __init__(self, regler, fremd=None):
                zaehler.append(1)
                time.sleep(0.2)
        with mock.patch('Genesis9.formung.G9formelnfremd', Formeln):
            formung = G9formung({'a': 1.0})
            aus = gleichzeitig(4, lambda: formung.formeln)
        self.assertEqual(len(zaehler), 1)
        self.assertTrue(all(a is aus[0] for a in aus))


def kugel_haut(zahl=4000, seed=3):
    u"""Eine Kugel vom Radius 1 als Haut: (Punkte, Normalen nach aussen, Baum)."""
    v = np.random.default_rng(seed).normal(size=(zahl, 3))
    p = v / np.linalg.norm(v, axis=1, keepdims=True)
    return p, p.copy(), G9kollision.baum(p)


def hinaus_ueber_alle(kleid, koerper, normalen, abstand, baum, durchgaenge):
    u"""Die Rechnung vor dem 16.10.2026: jeder Durchgang fragt ALLE Punkte (Vergleichsfassung von `G9kollision.hinaus`)."""
    abstand = np.asarray(G9kollision.ABSTAND if abstand is None else abstand, dtype=np.float64)
    punkte = np.array(kleid, dtype=np.float64, copy=True)
    nachbarn = None
    for _ in range(G9kollision.DURCHGAENGE if durchgaenge is None else durchgaenge):
        _weit, naechster = G9kollision.naechste(baum, punkte)
        n = normalen[naechster]
        hub = np.maximum(abstand - np.einsum('ij,ij->i', punkte - koerper[naechster], n), 0.0)
        if not (hub > 0).any():
            break
        if nachbarn is None and len(punkte) > G9kollision.NACHBARN:
            _w, nachbarn = G9kollision.naechste(G9kollision.baum(punkte), punkte, G9kollision.NACHBARN)
        if nachbarn is not None:
            hub = 0.5 * hub + 0.5 * hub[nachbarn].max(axis=1)
        punkte += hub[:, None] * n
    return punkte


class KollisionBewegtePunkteTest(SimpleTestCase):
    databases = set()

    def test_5_der_zweite_durchgang_nur_ueber_bewegte_punkte_gibt_dasselbe(self):
        haut, normalen, baum = kugel_haut()
        rng = np.random.default_rng(8)
        richtung = rng.normal(size=(1500, 3))
        kleid = richtung / np.linalg.norm(richtung, axis=1, keepdims=True) * rng.uniform(0.985, 1.02, (1500, 1))
        je_punkt = rng.uniform(-0.004, 0.006, 1500)
        bewegt = 0
        for teil in (kleid, kleid[:5]):           # zweiter Fall: weniger Punkte als Nachbarn — kein Nachbarschaftsmittel
            for durchgaenge in (None, 1, 3, 5):
                for abstand in (None, je_punkt[:len(teil)]):
                    soll = hinaus_ueber_alle(teil, haut, normalen, abstand, baum, durchgaenge)
                    ist = G9kollision.hinaus(teil, haut, normalen, abstand=abstand, baum=baum, durchgaenge=durchgaenge)
                    self.assertTrue(np.array_equal(soll, ist), (len(teil), durchgaenge, abstand is None))
                    bewegt = max(bewegt, int((soll != teil).any(axis=1).sum()))
        self.assertGreater(bewegt, 100, 'die Probe bewegt wirklich Punkte')

    @staticmethod
    def tal(seed, zahl=300, dichte=3000, spanne=0.03):
        u"""Ein steiles V-Tal (y = 1,5 |x|, Normalen ins Tal) und ein Kleid, das bis `spanne` darueber und darunter liegt — (Haut, Normalen, Baum, Kleid)."""
        rng = np.random.default_rng(seed)
        x, z = rng.uniform(-0.3, 0.3, zahl), rng.uniform(-0.3, 0.3, zahl)
        haut = np.column_stack([x, 1.5 * np.abs(x), z])
        n = np.column_stack([-1.5 * np.sign(x), np.ones(zahl), np.zeros(zahl)])
        normalen = n / np.linalg.norm(n, axis=1, keepdims=True)
        baum = G9kollision.baum(haut)
        rng = np.random.default_rng(seed + 1000)
        basis = haut[rng.integers(0, zahl, dichte)]
        nach = normalen[G9kollision.naechste(baum, basis)[1]]
        kleid = basis + nach * rng.uniform(-spanne, spanne, (dichte, 1)) + rng.normal(scale=0.004, size=(dichte, 3))
        return haut, normalen, baum, kleid

    def test_5c_auch_die_nachbarn_der_bewegten_punkte_zaehlen(self):
        for seed in (0, 2):
            haut, normalen, baum, kleid = self.tal(seed)
            soll = hinaus_ueber_alle(kleid, haut, normalen, None, baum, None)
            with mock.patch.object(G9kollision, '_betroffene', staticmethod(lambda bewegt, nachbarn: np.flatnonzero(bewegt))):
                ohne = G9kollision.hinaus(kleid, haut, normalen, baum=baum)
            self.assertFalse(np.array_equal(ohne, soll), 'die Probe trifft den Fall, in dem die Nachbarschaft zaehlt (Seed %d)' % seed)
            self.assertTrue(np.array_equal(G9kollision.hinaus(kleid, haut, normalen, baum=baum), soll), 'Seed %d' % seed)

    def test_5b_nichts_zu_heben_gibt_eine_unveraenderte_kopie(self):
        haut, normalen, baum = kugel_haut()
        draussen = haut[:200] * 1.05
        ist = G9kollision.hinaus(draussen, haut, normalen, baum=baum)
        self.assertTrue(np.array_equal(ist, draussen))
        self.assertIsNot(ist, draussen)


class HebevorratTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        G9hebevorrat._vorrat.clear()
        G9hebevorrat._rechnend.clear()
        self.haut = kugel_haut()

    def test_6_gleiche_punkte_werden_einmal_gehoben(self):
        punkte = np.random.default_rng(1).normal(size=(50, 3))
        zaehler = []

        def rechnen():
            zaehler.append(1)
            time.sleep(0.2)
            return punkte + 1.0
        aus = gleichzeitig(4, lambda: G9hebevorrat.holen(punkte.copy(), self.haut, rechnen))
        self.assertEqual(len(zaehler), 1)
        self.assertTrue(all(a is aus[0] for a in aus))
        self.assertFalse(aus[0].flags.writeable, 'wer das Ergebnis veraendern will, bekommt einen Fehler')

    def test_6b_andere_punkte_oder_andere_haut_rechnen_fuer_sich(self):
        a, b = np.zeros((5, 3)), np.ones((5, 3))
        gerechnet = []

        def rechnen_fuer(x):
            def rechnen():
                gerechnet.append(float(x.sum()))
                return x + 0.5
            return rechnen
        G9hebevorrat.holen(a, self.haut, rechnen_fuer(a))
        G9hebevorrat.holen(b, self.haut, rechnen_fuer(b))
        G9hebevorrat.holen(a, kugel_haut(seed=4), rechnen_fuer(a))
        self.assertEqual(gerechnet, [0.0, 15.0, 0.0], 'jede Eingabe fuer sich, auch dieselben Punkte auf anderer Haut')

    def test_6c_scheitert_der_rechner_scheitern_alle_und_keiner_haengt(self):
        punkte = np.ones((4, 3))

        def kaputt():
            raise ValueError('unbekannt')
        aus = gleichzeitig(3, lambda: G9hebevorrat.holen(punkte, self.haut, kaputt))
        self.assertTrue(all(isinstance(a, ValueError) for a in aus), aus)
        self.assertEqual(G9hebevorrat._rechnend, {})
        self.assertEqual(float(G9hebevorrat.holen(punkte, self.haut, lambda: punkte * 2).sum()), 24.0, 'danach rechnet es wieder')

    def test_6d_gehoben_nimmt_den_vorrat_und_laesst_requisiten_aus(self):
        haut, normalen, baum = self.haut
        lagen = G9lagen(self.haut)
        kleid = haut[:300] * 0.999
        koerperhaut = mock.Mock(koerperhaut=True)
        with mock.patch.object(G9kollision, 'hinaus', wraps=G9kollision.hinaus) as hinaus:
            a = lagen.gehoben(koerperhaut, kleid)
            b = lagen.gehoben(koerperhaut, kleid.copy())
            aufrufe = hinaus.call_count
            requisit = lagen.gehoben(mock.Mock(koerperhaut=False), kleid)
        self.assertEqual(aufrufe, 1, 'zweimal dieselben Punkte = einmal gehoben')
        self.assertTrue(np.array_equal(a, b))
        self.assertTrue(np.array_equal(a, G9kollision.hinaus(kleid, haut, normalen, baum=baum)), 'der Vorrat liefert die echte Rechnung')
        self.assertTrue(np.array_equal(requisit, kleid), 'ein Requisit wird nicht gehoben')
        self.assertEqual(hinaus.call_count, 1, 'auch das Requisit hat nichts mehr gerechnet')
