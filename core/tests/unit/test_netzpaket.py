# -*- coding: utf-8 -*-
u"""Das Binaerformat der Netzantworten (`core/daten/netzpaket.py`, 30.09.2026).

Geprueft wird, was der Browser braucht — nicht, wie das Paket innen aussieht:
Byteweise Gleichheit nach dem Auspacken, die Ausrichtung jedes Feldes (sonst wirft
`new Float32Array(puffer, versatz, n)` drueben einen `RangeError`), und dass ein
falsches Format LAUT scheitert statt ein Netz aus Rauschen zu ergeben.
"""
import base64
import json
import struct

import numpy as np
from django.test import SimpleTestCase

from core.daten.netzantwort import Netzantwort
from core.daten.netzausgabe import Netzausgabe
from core.daten.netzfeld import Netzfeld
from core.daten.netzjson import Netzjson
from core.daten.netzpaket import Netzpaket


class NetzfeldTest(SimpleTestCase):

    def test_1_der_typ_reist_mit_den_bytes(self):
        feld = Netzfeld.aus(np.arange(6, dtype=np.float64), np.float32)
        self.assertEqual(feld.typ, 'float32')
        self.assertEqual(feld.anzahl, 6)
        self.assertEqual(len(feld.rohdaten), 24)

    def test_2_ein_feld_wird_flach_und_zusammenhaengend(self):
        u"""Nach `[:, [0, 2, 1]]` ist ein Feld nicht mehr C-zusammenhaengend —
        `tobytes()` gaebe dann eine andere Reihenfolge, als der Browser liest."""
        werte = np.arange(12, dtype=np.float32).reshape(4, 3)[:, [0, 2, 1]]
        feld = Netzfeld.aus(werte, np.float32)
        erwartet = np.ascontiguousarray(werte.ravel(), dtype=np.float32).tobytes()
        self.assertEqual(feld.rohdaten, erwartet)

    def test_3_ein_typ_den_der_browser_nicht_liest_wird_abgelehnt(self):
        u"""float64 haette drueben kein passendes TypedArray — lieber hier ein
        Fehler als drueben ein zerrissenes Netz."""
        with self.assertRaises(ValueError):
            Netzfeld.aus(np.zeros(3), np.float64)


class NetzpaketTest(SimpleTestCase):

    def antwort(self):
        u"""Verschachtelt wie die echten Antworten (`G9netzantwort`)."""
        rand = np.random.default_rng(3)
        daten = Netzantwort.aus(rand.random((50, 3)),
                                faces=rand.integers(0, 50, (80, 3)),
                                normals=rand.random((50, 3)),
                                uvs=rand.random((50, 2)))
        daten['bindung'] = {'dreieck': Netzantwort.feld(rand.random((50, 3)), 'dreieck'),
                            'stufen': 1}
        daten['teile'] = [{'n': Netzantwort.feld(np.arange(9), 'n', typ='uint32')}]
        daten['name'] = u'Stück mit Umlaut'
        return daten

    def test_1_ausgepackt_ist_byteweise_dasselbe(self):
        daten = self.antwort()
        zurueck = Netzpaket.auspacken(Netzpaket.packen(daten))
        self.assertEqual(zurueck['name'], daten['name'])
        self.assertEqual(zurueck['vertex_count'], daten['vertex_count'])
        self.assertEqual(zurueck['bindung']['stufen'], 1)
        for pfad in ('vertices', 'faces', 'normals', 'uvs'):
            self.assertEqual(zurueck[pfad].rohdaten, daten[pfad].rohdaten, pfad)
            self.assertEqual(zurueck[pfad].typ, daten[pfad].typ, pfad)
        self.assertEqual(zurueck['bindung']['dreieck'].rohdaten,
                         daten['bindung']['dreieck'].rohdaten)
        self.assertEqual(zurueck['teile'][0]['n'].rohdaten,
                         daten['teile'][0]['n'].rohdaten)

    def test_2_jedes_feld_liegt_auf_seiner_elementbreite(self):
        u"""`new Float32Array(puffer, versatz, n)` verlangt Versatz % 4 == 0."""
        roh = Netzpaket.packen(self.antwort())
        (kopflaenge,) = struct.unpack('<I', roh[4:8])
        kopf = json.loads(roh[8:8 + kopflaenge].decode('utf-8'))
        beginn = 8 + kopflaenge
        beginn += (8 - beginn % 8) % 8
        breiten = {'float32': 4, 'uint32': 4, 'int32': 4, 'uint16': 2, 'uint8': 1}
        gefunden = []

        def lauf(wert):
            if isinstance(wert, dict):
                marke = wert.get(Netzpaket.MARKE)
                if isinstance(marke, dict) and len(wert) == 1:
                    gefunden.append(marke)
                    return
                for v in wert.values():
                    lauf(v)
            elif isinstance(wert, list):
                for v in wert:
                    lauf(v)

        lauf(kopf)
        self.assertGreaterEqual(len(gefunden), 6)
        for marke in gefunden:
            versatz = beginn + marke['pos']
            self.assertEqual(versatz % breiten[marke['typ']], 0,
                             'Feld %s liegt auf %d' % (marke['typ'], versatz))

    def test_3_ein_fremdes_format_scheitert_laut(self):
        u"""Ohne die Magie laese der Browser eine Fehlerseite als Float32 —
        und suchte den Fehler dann in der Geometrie."""
        roh = Netzpaket.packen(self.antwort())
        with self.assertRaises(ValueError):
            Netzpaket.auspacken(b'XXXX' + roh[4:])

    def test_4_das_paket_ist_kleiner_als_der_json_weg(self):
        u"""base64 macht aus 3 Bytes 4 Zeichen — das Paket muss deutlich
        kleiner sein, sonst hat der Umbau seinen Zweck verfehlt.

        Mit der Größe eines kleinen Kleidungsstücks (5.000 Punkte): Bei den 50 Punkten von
        `antwort()` fressen die Feldköpfe den Vorteil auf (erster Lauf, 30.09.2026: 3.776
        gegen 4.432 Bytes, 15 %) — behauptet ist er für echte Netze."""
        rand = np.random.default_rng(4)
        daten = Netzantwort.aus(rand.random((5000, 3)), faces=rand.integers(0, 5000, (9000, 3)),
                                normals=rand.random((5000, 3)), uvs=rand.random((5000, 2)))
        self.assertLess(len(Netzpaket.packen(daten)),
                        len(Netzjson.bytes(daten)) * 0.85)

    def test_5_ein_leeres_feld_bleibt_ein_leeres_feld(self):
        u"""Auf der Kaefigstufe haben viele JCM-Kanaele null Punkte."""
        daten = {'leer': Netzantwort.feld(np.zeros(0), 'leer')}
        zurueck = Netzpaket.auspacken(Netzpaket.packen(daten))
        self.assertEqual(zurueck['leer'].anzahl, 0)
        self.assertEqual(zurueck['leer'].rohdaten, b'')


class NetzausgabeTest(SimpleTestCase):

    class Anfrage:
        def __init__(self, accept):
            self.headers = {'Accept': accept}

    def test_1_ohne_accept_kopf_bleibt_es_bei_json(self):
        u"""Eine Lesestelle, die noch nicht umgestellt ist, muss weiter JSON
        bekommen — sonst laeuft ihr `JSON.parse` in Binaerdaten."""
        self.assertFalse(Netzausgabe.will_binaer(None))
        self.assertFalse(Netzausgabe.will_binaer(self.Anfrage('application/json')))

    def test_2_mit_accept_kopf_kommt_das_paket(self):
        anfrage = self.Anfrage('%s, application/json' % Netzpaket.INHALTSTYP)
        self.assertTrue(Netzausgabe.will_binaer(anfrage))
        antwort = Netzausgabe.antwort({'v': Netzantwort.feld(np.zeros(3), 'v')}, anfrage)
        self.assertEqual(antwort['Content-Type'], Netzpaket.INHALTSTYP)
        self.assertTrue(antwort.content.startswith(Netzpaket.MAGIE))

    def test_3_der_json_weg_macht_wieder_base64(self):
        antwort = Netzausgabe.antwort({'v': Netzantwort.feld(np.arange(3), 'v')})
        daten = json.loads(antwort.content.decode('utf-8'))
        self.assertIsInstance(daten['v'], str)
        self.assertEqual(
            np.frombuffer(base64.b64decode(daten['v']), dtype=np.float32).tolist(),
            [0.0, 1.0, 2.0])
