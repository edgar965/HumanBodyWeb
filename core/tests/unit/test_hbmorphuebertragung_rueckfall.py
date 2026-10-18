# -*- coding: utf-8 -*-
"""Verschluckte HumanBody-Regler werden mit Kopfausrichtung und Vorwärtsübertragung gerettet (`Hbmorphuebertragung.uebertragen_wirksam`, 17.10.2026).

WARUM (Edgar, 17.10.2026: „Teste alle Morphs", dann „fixe alle die keine Wirkung haben"): Genesis' Gesicht sitzt 9–25 mm anders als das von HumanBody, die Brustwarze 40 mm. Ein Regler mit 3 mm Hub auf
1–2 cm Fläche fiel zwischen die Punkte — `hb:Eyes_innerSinus` kam mit 0,000 mm an (Quelle 2,62 mm), `hb:Torso_BreastNipple` mit 0,000 (Quelle 5,9). Reihenfolge der Rückfälle, Zusagen (mit einer Attrappe
der Übertragung, ohne Netze):

1. Kommt weniger als `RUECKFALL` der Quell-Stärke an und ist die ausgerichtete Fassung mindestens `FAKTOR`-mal stärker, gilt sie (`weg` = 'ausgerichtet') — für beide Richtungen.
2. Kommt genug an, wird kein Rückfall gerechnet: der Regler bleibt bitgleich (kein Risiko für die guten); `weg` = 'rahmen'.
3. Ist keine Rückfallfassung deutlich stärker (Mund: `Mouth_UpperlipVolume` 0,94 → 0,03 mm ausgerichtet), bleibt die normale.
4. Hilft die Ausrichtung nicht, kommt die Vorwärtsübertragung dran ('vorwaerts', dann 'vorwaerts_ausgerichtet'); genommen wird die stärkste, die mindestens `FAKTOR`-mal stärker ist als die bisher beste.
5. Genügt schon die Ausrichtung (≥ `RUECKFALL`), wird die Vorwärtsübertragung nicht gerechnet.
6. Eine Quelle ohne Verschiebung ist kein Fall für den Rückfall.

FEHLERBILD OHNE DIESE TESTS: Ein Gesichtsregler steht im Menü und tut nichts (Test 6 in `longrunner/test_genesis9_alter_semantik`), oder ein guter Regler wird still durch eine schlechtere Fassung ersetzt.
Gefahren am 17.10.2026. Sabotage-Gegenprobe gefahren (erste Fassung): `RUECKFALL` auf 0 → Fall 1 rot. Nicht gefahren: den Faktorvergleich streichen → Fall 3 und 4 müssten rot werden.
"""
import numpy as np
from core.dienste.hbmorphuebertragung import Hbmorphuebertragung
from django.test import SimpleTestCase


class _Attrappe(Hbmorphuebertragung):
    """Die Übertragung liefert vorbereitete Felder (m) je Weg und Richtung; `aufrufe` merkt, welche Wege gerechnet wurden."""

    def __init__(self, **felder):
        super().__init__()
        self.felder = felder
        self.aufrufe = []

    def _liefern(self, weg, hb_delta):
        self.aufrufe.append(weg)
        return self.felder.get(weg, self.felder['rahmen'])['plus' if hb_delta[0, 0] > 0 else 'minus']

    def uebertragen(self, hb_delta, welt=False, ausgerichtet=False):
        return self._liefern('ausgerichtet' if ausgerichtet else 'rahmen', hb_delta)

    def uebertragen_vorwaerts(self, hb_delta, ausgerichtet=False):
        return self._liefern('vorwaerts_ausgerichtet' if ausgerichtet else 'vorwaerts', hb_delta)


def feld(mm):
    return np.array([[mm / 1000.0, 0.0, 0.0], [0.0, 0.0, 0.0]])


def paar(mm):
    return {'plus': feld(mm), 'minus': -feld(mm)}


QUELLE_PLUS, QUELLE_MINUS = feld(3.0), -feld(3.0)


class RueckfallTest(SimpleTestCase):
    databases = set()

    def test_1_verschluckt_und_ausgerichtet_deutlich_staerker_gilt_die_ausgerichtete(self):
        u = _Attrappe(rahmen=paar(0.1), ausgerichtet=paar(1.5))
        plus, minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'ausgerichtet')
        self.assertAlmostEqual(u.staerke(plus), 0.0015)
        self.assertAlmostEqual(u.staerke(minus), 0.0015, msg='beide Richtungen aus derselben Zuordnung')

    def test_2_kommt_genug_an_wird_kein_rueckfall_gerechnet(self):
        u = _Attrappe(rahmen=paar(1.5), ausgerichtet=paar(9.0), vorwaerts=paar(9.0))
        plus, _minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'rahmen')
        self.assertEqual(u.aufrufe, ['rahmen', 'rahmen'], 'nur die normale Zuordnung')
        self.assertAlmostEqual(u.staerke(plus), 0.0015)

    def test_3_nicht_deutlich_staerker_bleibt_die_normale(self):
        u = _Attrappe(rahmen=paar(0.5), ausgerichtet=paar(0.7), vorwaerts=paar(0.8), vorwaerts_ausgerichtet=paar(0.9))
        plus, _minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'rahmen')
        self.assertAlmostEqual(u.staerke(plus), 0.0005)

    def test_3b_ist_der_rueckfall_schwaecher_bleibt_die_normale(self):
        u = _Attrappe(rahmen=paar(0.36), ausgerichtet=paar(0.0), vorwaerts=paar(0.0), vorwaerts_ausgerichtet=paar(0.0))
        _plus, _minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'rahmen', 'Eyes_Crosscalibration: 0,36 mm gegen 0,000 mm')

    def test_4_hilft_die_ausrichtung_nicht_kommt_die_vorwaertsuebertragung(self):
        u = _Attrappe(rahmen=paar(0.0), ausgerichtet=paar(0.0), vorwaerts=paar(1.2), vorwaerts_ausgerichtet=paar(0.4))
        plus, _minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'vorwaerts', 'Torso_BreastNipple: 0,000 mm normal, 1,2 mm vorwärts')
        self.assertAlmostEqual(u.staerke(plus), 0.0012)

    def test_4b_die_ausgerichtete_vorwaertsuebertragung_kann_die_beste_sein(self):
        u = _Attrappe(rahmen=paar(0.04), ausgerichtet=paar(0.0), vorwaerts=paar(0.1), vorwaerts_ausgerichtet=paar(1.0))
        _plus, _minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'vorwaerts_ausgerichtet', 'Mouth_Protusion')

    def test_5_genuegt_die_ausrichtung_wird_vorwaerts_nicht_gerechnet(self):
        u = _Attrappe(rahmen=paar(0.05), ausgerichtet=paar(0.9), vorwaerts=paar(2.0))
        _plus, _minus, weg = u.uebertragen_wirksam(QUELLE_PLUS, QUELLE_MINUS)
        self.assertEqual(weg, 'ausgerichtet')
        self.assertNotIn('vorwaerts', u.aufrufe)
        self.assertNotIn('vorwaerts_ausgerichtet', u.aufrufe)

    def test_6_eine_quelle_ohne_verschiebung_ist_kein_fall(self):
        null = np.zeros((2, 3))
        u = _Attrappe(rahmen={'plus': null, 'minus': null}, ausgerichtet=paar(5.0), vorwaerts=paar(5.0))
        _plus, _minus, weg = u.uebertragen_wirksam(null, null)
        self.assertEqual(weg, 'rahmen')
        self.assertEqual(u.aufrufe, ['rahmen', 'rahmen'])
