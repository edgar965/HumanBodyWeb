# -*- coding: utf-8 -*-
u"""`Netzkurz` und `Netzpaket.packen(kurz=True)` — float32-Felder als 16 Bit (19.10.2026, Edgar: „stelle auf 16 bit um").

1. Rundlauf: große float32-Felder kommen auf eine halbe Stufe genau zurück (Spanne/65534/2); ohne Vorzeichenwechsel das Minimum exakt.
2. Die Null bleibt exakt Null, auch wenn das Feld beide Vorzeichen hat (`mischung <= 0` im Shader fragt danach).
3. Nicht gekürzt: kleine Felder (unter `AB_ANZAHL`), andere Typen, NaN/∞, Spanne 0 — dort bleiben die Bytes, wie sie waren.
4. Das Paket: ohne `kurz` unverändert float32 (alte Tabs), mit `kurz` kleiner und die Marke trägt `kurz`; `auspacken` liefert float32 zurück.
5. `Netzausgabe.will_binaer`: nur mit `kodierung=u16` in `Accept` der Wert `'u16'`, sonst wie bisher `True`/`False`.
6. Nummern bleiben genau (12.11.2026, Olesia1: Stacheln an Kragen und Schuh): ein Feld mit `genau` (Körperpunkte der Oberflächenbindung, 0 … 104.479 und
   −1) kommt Byte für Byte zurück und trägt keine Marke `kurz`; `Netzantwort.feld` setzt `genau` für `skin_indices`, `G9netzantwort` für `bindung.dreieck`
   und nur dafür. Gegenprobe im Fall selbst: dasselbe Feld ohne die Marke wird gekürzt, und mehr als ein Zehntel der Nummern rundet auf einen anderen Punkt.
7. `Netzpaket.nummern_gekuerzt`: ein Paket alter Bauart (gekürztes `bindung.dreieck`) wird am Kopf erkannt, ein neues, eines ohne Bindung, JSON und None
   nicht — `G9vorratanfrage.holen` liefert so eines aus dem dauerhaften Vorrat nicht mehr aus.

Gemessen an den sechs Antworten im Vorrat (`ProjektTemp/_wegwerf/anzeigevorrat/kurz_probe.py`, 19.10.2026): 9,32 → 6,94 MB, Punkte höchstens 0,014 mm,
Normalen 1,5·10⁻⁵, UV 7,6·10⁻⁶ daneben, alle Nullen exakt.

Sabotage (nicht gelaufen — Tests nur auf Ansage): in `Netzkurz.packen` die Rasterung der Null weglassen (`ab = lo`) → Fall 2 rot;
`AB_ANZAHL` auf 0 → Fall 3 rot; in `Netzausgabe.will_binaer` immer `KURZ` → Fall 5 rot; in `Netzpaket._ersetzen` das `and not wert.genau` weglassen oder in
`G9netzantwort.aus` das `genau=` → Fall 6 rot. Geschrieben, nicht gelaufen.
"""
import unittest
from array import array
from types import SimpleNamespace

import numpy as np

from core.api.g9netzantwort import G9netzantwort
from core.daten.netzantwort import Netzantwort
from core.daten.netzausgabe import Netzausgabe
from core.daten.netzfeld import Netzfeld
from core.daten.netzkurz import Netzkurz
from core.daten.netzpaket import Netzpaket


class NetzkurzTest(unittest.TestCase):

    @staticmethod
    def rundlauf(werte):
        w = np.asarray(werte, dtype=np.float32)
        gekuerzt = Netzkurz.packen(w.tobytes(), w.size)
        if gekuerzt is None:
            return None
        return np.frombuffer(Netzkurz.entpacken(gekuerzt[0], w.size, gekuerzt[1]), dtype=np.float32)

    def test_1_rundlauf(self):
        w = np.random.default_rng(1).uniform(-0.4, 1.8, 30000).astype(np.float32)
        z = self.rundlauf(w)
        self.assertLessEqual(float(np.abs(z - w).max()), (1.8 + 0.4) / 65534 * 0.51)
        nur_plus = np.linspace(0.2, 1.7, 9000, dtype=np.float32)        # ohne Vorzeichenwechsel liegt `ab` auf dem Minimum: exakt
        self.assertEqual(float(self.rundlauf(nur_plus).min()), float(nur_plus.min()))

    def test_2_null_bleibt_null(self):
        w = np.random.default_rng(2).uniform(-0.37, 0.93, 20000).astype(np.float32)
        w[::7] = 0.0
        z = self.rundlauf(w)
        self.assertTrue((z[w == 0] == 0).all())

    def test_3_nicht_gekuerzt(self):
        self.assertIsNone(Netzkurz.packen(np.zeros(100, np.float32).tobytes(), 100))                     # klein
        self.assertIsNone(Netzkurz.packen(np.full(5000, 0.5, np.float32).tobytes(), 5000))               # Spanne 0
        nan = np.linspace(0, 1, 5000, dtype=np.float32)
        nan[3] = np.nan
        self.assertIsNone(Netzkurz.packen(nan.tobytes(), 5000))                                           # NaN
        daten = {'index': Netzfeld.aus(np.arange(9000), 'uint32'), 'klein': Netzfeld.aus(np.linspace(0, 1, 10), 'float32')}
        aus = Netzpaket.auspacken(Netzpaket.packen(daten, kurz=True))
        self.assertEqual(aus['index'].rohdaten, daten['index'].rohdaten)
        self.assertEqual(aus['klein'].rohdaten, daten['klein'].rohdaten)

    def test_4_paket(self):
        punkte = Netzfeld.aus(np.random.default_rng(3).uniform(-1, 2, 60000), 'float32')
        lang, kurz = Netzpaket.packen({'vertices': punkte}), Netzpaket.packen({'vertices': punkte}, kurz=True)
        self.assertEqual(Netzpaket.auspacken(lang)['vertices'].rohdaten, punkte.rohdaten)
        self.assertLess(len(kurz), len(lang) * 0.55)
        self.assertIn(b'"kurz"', kurz[:400])
        zurueck = Netzpaket.auspacken(kurz)['vertices']
        self.assertEqual((zurueck.typ, zurueck.anzahl), ('float32', 60000))
        a, b = np.frombuffer(punkte.rohdaten, np.float32), np.frombuffer(zurueck.rohdaten, np.float32)
        self.assertLess(float(np.abs(a - b).max()), 3 / 65534)

    def test_5_aushandlung(self):
        anfrage = lambda accept: SimpleNamespace(headers={'Accept': accept})  # noqa: E731
        self.assertEqual(Netzausgabe.will_binaer(anfrage('application/x-humanbody-netz;kodierung=u16, application/json')), 'u16')
        self.assertIs(Netzausgabe.will_binaer(anfrage('application/x-humanbody-netz, application/json')), True)
        self.assertIs(Netzausgabe.will_binaer(anfrage('application/json')), False)
        self.assertIs(Netzausgabe.will_binaer(None), False)

    def test_6_nummern_bleiben_genau(self):
        nummern = array('f', [-1.0] + [float(i) for i in range(0, 104480, 7)])          # wie `bindung.dreieck` auf der feinen Stufe
        genau = Netzfeld(nummern.tobytes(), 'float32', len(nummern), genau=True)
        paket = Netzpaket.packen({'bindung': {'dreieck': genau}}, kurz=True)
        self.assertNotIn(b'"kurz"', paket[:400])
        self.assertEqual(Netzpaket.auspacken(paket)['bindung']['dreieck'].rohdaten, genau.rohdaten)
        # Gegenprobe: ohne die Marke wird dasselbe Feld gekürzt, und die Nummern treffen andere Punkte
        ohne = Netzfeld(nummern.tobytes(), 'float32', len(nummern))
        zurueck = array('f')
        zurueck.frombytes(Netzpaket.auspacken(Netzpaket.packen({'d': ohne}, kurz=True))['d'].rohdaten)
        daneben = sum(1 for a, b in zip(nummern, zurueck, strict=True) if round(a) != round(b))
        self.assertGreater(daneben, len(nummern) // 10)
        # Wer die Marke setzt: die Tabelle für Knochennummern, `G9netzantwort` für die Körperpunkte der Bindung — und nur für die
        self.assertTrue(Netzantwort.feld([0, 1, 2], 'skin_indices').genau)
        self.assertFalse(Netzantwort.feld([0.5, 1.5], 'vertices').genau)
        bindung = {'dreieck': [[0, 1, 2]], 'bary': [[0.2, 0.3, 0.5]], 'abstand': [0.004], 'mischung': [1.0], 'stufen': 1}
        antwort = G9netzantwort.aus({'punkte': [[0.0, 0.0, 0.0]], 'dreiecke': [[0, 0, 0]], 'normalen': [[0.0, 1.0, 0.0]], 'uv': [[0.0, 0.0]],
                                     'gruppen': [], 'bindung': bindung})
        self.assertEqual({art: antwort['bindung'][art].genau for art in ('dreieck', 'bary', 'abstand', 'mischung')},
                         {'dreieck': True, 'bary': False, 'abstand': False, 'mischung': False})

    def test_7_altes_paket_wird_erkannt(self):
        nummern = array('f', [float(i) for i in range(0, 104480, 7)])
        punkte = Netzfeld(array('f', [0.001 * i for i in range(6000)]).tobytes(), 'float32', 6000)
        alt = Netzpaket.packen({'teile': [{'vertices': punkte, 'bindung': {'dreieck': Netzfeld(nummern.tobytes(), 'float32', len(nummern))}}]}, kurz=True)
        neu = Netzpaket.packen({'teile': [{'vertices': punkte, 'bindung': {'dreieck': Netzfeld(nummern.tobytes(), 'float32', len(nummern), genau=True)}}]},
                               kurz=True)
        self.assertTrue(Netzpaket.nummern_gekuerzt(alt))                 # so lagen die Antworten bis zum 12.11.2026 im dauerhaften Vorrat
        self.assertFalse(Netzpaket.nummern_gekuerzt(neu))                # `vertices` ist darin weiter gekürzt, das zählt nicht
        self.assertIn(b'"kurz"', neu[:600])
        self.assertFalse(Netzpaket.nummern_gekuerzt(Netzpaket.packen({'vertices': punkte}, kurz=True)))
        self.assertFalse(Netzpaket.nummern_gekuerzt(b'{"teile": [{"bindung": {"dreieck": "AAAA"}}]}'))     # JSON-Antwort
        self.assertFalse(Netzpaket.nummern_gekuerzt(None))


if __name__ == '__main__':
    unittest.main()
