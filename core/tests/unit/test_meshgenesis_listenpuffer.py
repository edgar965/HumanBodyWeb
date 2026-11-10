# -*- coding: utf-8 -*-
"""Die Puffer hinter /mesh-genesis/ und dem Garderoben-Katalog (30.10.2026, Edgar: „wenn ich /studio/ öffne, und schnell eine andere Seite klicke,
dauert es ewig“ — die Liste las je Aufruf 571 Ergebnisdateien und 838 Einträge, ging alle 30 s über 16.876 Verzeichnisse, der Katalog filterte
2.380-mal die ganze Ordnerliste).

1. `Meshgenesistrainingsdatum._lesen` behält nur `FELDER` und liest erst wieder, wenn sich Zeit oder Größe der Datei ändern.
2. `Meshgenesislaufzeit._sekunden` ebenso.
3. `Meshgenesisrechendatum._gemerkt_oder`: frisch → gemerkt; älter als `MERKEN_S`, jünger als `HINTERGRUND_S` → alter Wert, Neurechnung im
   Hintergrund (später); älter → im Aufruf gerechnet.
4. `G9ordnerliste.passend` mit Tupel gibt dasselbe wie der alte Filter (Groß/Klein, leerer Mittelteil, Reihenfolge von `namen`) und baut den
   Index je Tupel nur einmal.

Sabotage: `_lesen` ohne Stand-Vergleich -> Fall 1 rot (zweites Lesen); `_gemerkt_oder` rechnet immer im Aufruf -> Fall 3 rot; `passend` gibt
sortierte statt Ordner-Reihenfolge -> Fall 4 rot.

Geschrieben am 30.10.2026, nicht gelaufen.
"""
import json
import random
import tempfile
import time
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.ordnerliste import G9ordnerliste

from core.dienste.meshgenesislaufzeit import Meshgenesislaufzeit
from core.dienste.meshgenesisrechendatum import Meshgenesisrechendatum
from core.dienste.meshgenesistrainingsdatum import Meshgenesistrainingsdatum

WEGWERF = Path(__file__).resolve().parent / '_wegwerf'


class Listenpuffer(SimpleTestCase):

    def _ordner(self):
        WEGWERF.mkdir(exist_ok=True)
        t = tempfile.TemporaryDirectory(dir=WEGWERF)
        self.addCleanup(t.cleanup)
        return Path(t.name)

    def test_1_trainingsdatum_liest_nur_bei_aenderung(self):
        datei = self._ordner() / 'lauf_ergebnis.json'
        datei.write_text(json.dumps({'training_daten': ['A'], 'paare': [], 'verlauf': list(range(100))}), encoding='utf-8')
        with mock.patch.object(Path, 'read_text', autospec=True, side_effect=Path.read_text) as lesen:
            erst = Meshgenesistrainingsdatum._lesen(datei)
            zweit = Meshgenesistrainingsdatum._lesen(datei)
        self.assertEqual(erst, {'training_daten': ['A'], 'paare': []}, 'nur FELDER, nicht der Verlauf')
        self.assertEqual(zweit, erst)
        self.assertEqual(lesen.call_count, 1, 'unveränderte Datei nicht neu gelesen')
        datei.write_text(json.dumps({'training_daten': ['A', 'B'], 'paare': ['P']}), encoding='utf-8')
        self.assertEqual(Meshgenesistrainingsdatum._lesen(datei), {'training_daten': ['A', 'B'], 'paare': ['P']})

    def test_2_laufzeit_sekunden_nur_bei_aenderung(self):
        datei = self._ordner() / 'eintrag.json'
        datei.write_text(json.dumps({'sekunden': 12.5}), encoding='utf-8')
        self.assertEqual(Meshgenesislaufzeit._sekunden(datei), 12.5)
        with mock.patch.object(Meshgenesislaufzeit, '_json', side_effect=AssertionError('neu gelesen')):
            self.assertEqual(Meshgenesislaufzeit._sekunden(datei), 12.5)
        datei.write_text(json.dumps({'sekunden': 7.25, 'mehr': 1}), encoding='utf-8')
        self.assertEqual(Meshgenesislaufzeit._sekunden(datei), 7.25)

    def test_3_rechendatum_alter_wert_und_hintergrund(self):
        schluessel = ('test', '_test_listenpuffer')
        self.addCleanup(Meshgenesisrechendatum._gemerkt.pop, schluessel, None)
        self.addCleanup(Meshgenesisrechendatum._offen.pop, schluessel, None)
        gerufen = []

        def rechnen():
            gerufen.append(1)
            return {'zeit': len(gerufen)}

        geplant = []
        timer = mock.Mock(side_effect=lambda frist, ziel: geplant.append(frist) or mock.Mock())
        with mock.patch('core.dienste.meshgenesisrechendatum.threading.Timer', timer), mock.patch.object(Meshgenesisrechendatum, '_faden', None):
            self.assertEqual(Meshgenesisrechendatum._gemerkt_oder(schluessel, rechnen), {'zeit': 1}, 'leer: im Aufruf gerechnet')
            self.assertEqual(Meshgenesisrechendatum._gemerkt_oder(schluessel, rechnen), {'zeit': 1}, 'frisch: gemerkt')
            self.assertEqual(len(gerufen), 1)
            jetzt = time.monotonic()
            Meshgenesisrechendatum._gemerkt[schluessel] = (jetzt - Meshgenesisrechendatum.MERKEN_S - 1, {'zeit': 1})
            self.assertEqual(Meshgenesisrechendatum._gemerkt_oder(schluessel, rechnen), {'zeit': 1}, 'abgelaufen: alter Wert')
            self.assertEqual(len(gerufen), 1, 'nicht im Aufruf gerechnet')
            self.assertEqual(geplant, [Meshgenesisrechendatum.WARTEN_S], 'Hintergrund geplant')
            self.assertIn(schluessel, Meshgenesisrechendatum._offen)
            Meshgenesisrechendatum._gemerkt[schluessel] = (jetzt - Meshgenesisrechendatum.HINTERGRUND_S - 1, {'zeit': 1})
            self.assertEqual(Meshgenesisrechendatum._gemerkt_oder(schluessel, rechnen), {'zeit': 2}, 'zu alt: im Aufruf gerechnet')

    def test_4_passend_wie_der_alte_filter(self):
        def alt(namen, vorn, hinten):
            v, h = vorn.lower(), hinten.lower()
            return [n for n in namen if len(n) >= len(v) + len(h) and n.lower().startswith(v) and n.lower().endswith(h)]

        zufall = random.Random(30)
        stuecke = ['hemd', 'HEMD', 'hemd_lang', 'rock', 'Rock', 'h']
        namen = tuple('%s__%s_f%d.json' % (zufall.choice(stuecke), zufall.choice(['a', 'B', '', 'c_d']), zufall.choice([1, 2])) for _ in range(300))
        namen += ('hemd_f1.json', 'hemd__', 'HEMD___F1.JSON')
        for vorn in ('hemd__', 'HEMD__', 'rock__', 'h__', 'fehlt__'):
            for hinten in ('_f1.json', '_F2.JSON'):
                self.assertEqual(G9ordnerliste.passend(namen, vorn, hinten), alt(namen, vorn, hinten), (vorn, hinten))
        index = G9ordnerliste._indizes[id(namen)]
        self.assertIs(index[0], namen)
        G9ordnerliste.passend(namen, 'rock__', '_f1.json')
        self.assertIs(G9ordnerliste._indizes[id(namen)], index, 'Index je Tupel nur einmal gebaut')
