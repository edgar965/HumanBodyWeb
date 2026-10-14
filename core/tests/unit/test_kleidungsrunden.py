# -*- coding: utf-8 -*-
"""Mesh to 3D, 14.10.2026: die Randlinie der Kleidungsmaske rund (`Kleidungsbereinigung._runden`) und die hautfarbenen Inseln im Hautband (`Kleidungsrand.hautband(…, inhalt)`).

Anlass (Edgar1, Unterhose und Uhr: „Saum, Uhr schlecht“): Kamm aus 5 mm breiten Zähnen am Saum, eine 12 mm breite Bucht am Bund, 61 (Hose) und 18 (Uhr) hautfarbene Inseln mitten im Stoff — gemessen am Objekt und im Chrome gesehen (`.claude/rules/mesh-3d-animation.md`).
Kunstnetz: 60 × 60 bzw. 40 × 40 Zellen (`_kleidungsgitter`), Etikett 1 = Oberteil, 2 = Hose, 4 = Zubehör, 0 = kein Stück.
"""

import unittest

import numpy as np

from Kleidung.kleidungsbereinigung import Kleidungsbereinigung

from ._kleidungsgitter import _bau


class RundenTest(unittest.TestCase):
    """14.10.2026 (Edgar, Unterhose: „Saum schlecht“): die Gauß-Mehrheit der Randlinie (`Kleidungsbereinigung._runden`, `RADIUS_M`). Kunstnetz: 60 × 60 Zellen zu je 0,02 cm² (Kante ~1,4 mm), der Radius 12 mm sind rund 8 Zellen.
    Sabotage-Gegenproben: `RADIUS_M = 1e-6` → `test_ein_kamm_am_rand_wird_zur_linie` und `test_eine_schmale_bucht_wird_geschlossen` rot; `SCHUTZ = 1.0` → `test_ein_schmaler_traeger_bleibt` rot."""

    N = 60

    def _netz(self):
        f, nachbarn, zelle, inhalt, hoehe = _bau(n=self.N, cm2_je_flaeche=0.01)
        return nachbarn, zelle, inhalt, hoehe

    def _zellen(self, zelle, ys, xs):
        return np.isin(zelle, [y * self.N + x for y in ys for x in xs])

    def test_ein_kamm_am_rand_wird_zur_linie(self):
        """Zähne von 3 × 2 Zellen im Abstand von 8 Zeilen an einer geraden Kante: die Mehrheit über die Kantennachbarn lässt sie stehen, das Runden nimmt sie weg."""
        nachbarn, zelle, inhalt, hoehe = self._netz()
        stueck = np.where(zelle % self.N < 30, 1, 0).astype(np.int8)
        zaehne = self._zellen(zelle, [y + d for y in range(4, 56, 8) for d in (0, 1)], (30, 31, 32))
        stueck[zaehne] = 1
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        spitzen = self._zellen(zelle, [y + d for y in range(4, 56, 8) for d in (0, 1)], (31, 32))
        self.assertTrue((neu[spitzen] == 0).all(), 'die äußeren zwei Spalten jedes Zahns sind weg')
        self.assertLess(float((neu[zaehne] == 1).mean()), 0.4, 'die Linie liegt dort, wo der mittlere Rand lag: nur ein Rest der Zahnwurzeln bleibt')
        self.assertGreaterEqual(bericht['rund_geaendert_flaechen'], 1)
        self.assertGreater(bericht['rund_schritte'], 100)

    def test_eine_schmale_bucht_wird_geschlossen(self):
        """Haut, die als 3 Zellen breiter Streifen in den Stoff hineinreicht (Sapiens-Fehler an einer Taschennaht), gehört zum Stoff."""
        nachbarn, zelle, inhalt, hoehe = self._netz()
        stueck = np.where(zelle // self.N < 40, 1, 0).astype(np.int8)               # unten Stoff, ab Zeile 40 Haut
        bucht = self._zellen(zelle, range(28, 40), (28, 29, 30))
        stueck[bucht] = 0
        neu, _ = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        tief = self._zellen(zelle, range(28, 34), (28, 29, 30))
        self.assertTrue((neu[tief] == 1).all(), 'der innere Teil der Bucht ist wieder Stoff')

    def test_ein_schmaler_traeger_bleibt(self):
        """Eine freistehende Gruppe, die beim Runden mehr als die Hälfte ihrer Fläche verlöre (Träger, Gürtelschlaufe), bekommt sie zurück."""
        nachbarn, zelle, inhalt, hoehe = self._netz()
        stueck = np.zeros(len(zelle), dtype=np.int8)
        traeger = self._zellen(zelle, range(10, 50), range(28, 34))            # 6 Zellen breit: schmaler als zwei Standardabweichungen
        stueck[traeger] = 2
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertGreater(float((neu[traeger] == 2).mean()), 0.95, 'ohne den Schutz bliebe nichts davon (die Mehrheit über die Kantennachbarn knabbert nur an den Enden)')
        self.assertEqual(bericht['rund_geschuetzt_gruppen'], 1)

    def test_eine_gerade_kante_bleibt_wo_sie_ist(self):
        nachbarn, zelle, inhalt, hoehe = self._netz()
        stueck = np.where(zelle % self.N < 30, 1, 0).astype(np.int8)
        neu, _ = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertLess(abs(int((neu == 1).sum()) - int((stueck == 1).sum())) / int((stueck == 1).sum()), 0.01)

    def test_der_kopf_ruehrt_sich_nicht(self):
        nachbarn, zelle, inhalt, hoehe = self._netz()
        stueck = np.where(zelle % self.N < 30, 1, 0).astype(np.int8)
        zaehne = self._zellen(zelle, range(4, 8), (30, 31, 32))
        stueck[zaehne] = 1
        hoehe[zaehne] = 2.0                                       # über kopf_ab
        neu, _ = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertTrue((neu[zaehne] == 1).all(), 'Flächen oberhalb der Kopfhöhe ändern sich nie')

    def test_ohne_grenze_gibt_es_nichts_zu_runden(self):
        nachbarn, zelle, inhalt, hoehe = self._netz()
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(np.full(len(zelle), 2, dtype=np.int8))
        self.assertTrue((neu == 2).all())
        self.assertEqual(bericht['rund_geaendert_flaechen'], 0)


class HautinselnTest(unittest.TestCase):
    """`Kleidung.kleidungsrand.Kleidungsrand.hautband` mit `inhalt`: kleine hautfarbene Inseln im Innern gehören zum Band.
    Sabotage-Gegenprobe: `INSEL_CM2 = 0` → `test_eine_kleine_hautfarbene_insel_mitten_im_stoff_gehoert_zum_band` rot."""

    def test_eine_kleine_hautfarbene_insel_mitten_im_stoff_gehoert_zum_band(self):
        """14.10.2026 (Edgar, Unterhose und Uhr: 61 und 18 Inseln, die größte 2,4 cm², alle weiter als acht Ringe vom Rand): mit `inhalt` kommen kleine Inseln im Innern ins Band."""
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, inhalt, _ = _bau(n=40, cm2_je_flaeche=0.1)
        insel = np.isin(zelle, [20 * 40 + 20, 20 * 40 + 21, 21 * 40 + 20, 21 * 40 + 21])       # 8 Flächen zu 0,1 cm² = 0,8 cm²
        weg = Kleidungsrand.hautband(Kleidungsrand.nachbarn_aus(f), insel, inhalt)
        self.assertTrue(weg[insel].all())
        self.assertFalse(weg[~insel].any())

    def test_eine_grosse_hautfarbene_flaeche_bleibt_auch_mit_inhalt(self):
        """Ein beiges Hemd (Hautfarbe über `INSEL_CM2`) verliert nichts im Innern."""
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, inhalt, _ = _bau(n=40, cm2_je_flaeche=1.0)
        insel = np.isin(zelle, [20 * 40 + x for x in range(15, 25)] + [21 * 40 + x for x in range(15, 25)])     # 40 Flächen zu 1 cm² = 40 cm²
        weg = Kleidungsrand.hautband(Kleidungsrand.nachbarn_aus(f), insel, inhalt)
        self.assertFalse(weg.any(), 'weder am Rand noch als kleine Insel')

    def test_ohne_inhalt_bleibt_es_beim_band_am_rand(self):
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, _, _ = _bau(n=40)
        insel = np.isin(zelle, [20 * 40 + 20, 20 * 40 + 21])
        self.assertFalse(Kleidungsrand.hautband(Kleidungsrand.nachbarn_aus(f), insel).any())


class ZubehoerTest(unittest.TestCase):
    """`Kleidungsbereinigung._zubehoer_vervollstaendigen` (14.10.2026, Edgar1: „Uhr noch fehlerhaft“): Sapiens las 20 % der Uhr (Armband) als Hintergrund oder Unterarm — sie wachsen über unbenannte, nicht hautfarbene Nachbarflächen dazu.
    Kunstnetz 60 × 60 Zellen zu je 0,02 cm²; Zubehör (4) ein Block, rechts daneben ein Streifen aus nicht hautfarbenen Flächen ohne Stück.
    Sabotage-Gegenproben: `WACHS_RINGE = 0` → `test_der_streifen_waechst_zum_zubehoer` rot; `WACHS_ANTEIL = 1e9` → `test_ein_ausreisser_waechst_nicht_ueber_alles` rot."""

    N = 60

    def _netz(self):
        f, nachbarn, zelle, inhalt, hoehe = _bau(n=self.N, cm2_je_flaeche=0.01)
        stueck = np.zeros(len(zelle), dtype=np.int8)
        block = np.isin(zelle, [y * self.N + x for y in range(10, 50) for x in range(5, 30)])             # 25 × 40 Zellen, größer als zwei Standardabweichungen des Rundens
        stueck[block] = 4
        streifen = np.isin(zelle, [y * self.N + x for y in range(10, 50) for x in range(30, 33)])
        return nachbarn, zelle, inhalt, hoehe, stueck, streifen

    def test_der_streifen_waechst_zum_zubehoer(self):
        nachbarn, zelle, inhalt, hoehe, stueck, streifen = self._netz()
        hautfarbe = np.ones(len(zelle), dtype=bool)
        hautfarbe[streifen] = False                                         # Armband: nicht hautfarben
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck, hautfarbe)
        self.assertEqual(bericht['zubehoer_dazu_flaechen'], int(streifen.sum()), 'alle Flächen des Streifens kommen dazu')
        self.assertGreater(float((neu[streifen] == 4).mean()), 0.8, 'nach dem Runden bleibt der Streifen bis auf die Ecken Zubehör')

    def test_hautfarbene_flaechen_wachsen_nicht_mit(self):
        nachbarn, zelle, inhalt, hoehe, stueck, streifen = self._netz()
        hautfarbe = np.ones(len(zelle), dtype=bool)                          # alles hautfarben: der Streifen auch
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck, hautfarbe)
        self.assertEqual(bericht['zubehoer_dazu_flaechen'], 0)
        self.assertTrue((neu[streifen] == 0).all())

    def test_ein_ausreisser_waechst_nicht_ueber_alles(self):
        """Ist ALLES ringsum nicht hautfarben (ein Hut in einem Raum voll Schatten), wüchse die Gruppe über mehr als die Hälfte ihrer Fläche: dann wächst sie gar nicht."""
        nachbarn, zelle, inhalt, hoehe, stueck, _ = self._netz()
        hautfarbe = np.zeros(len(zelle), dtype=bool)
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck, hautfarbe)
        self.assertEqual(bericht['zubehoer_dazu_flaechen'], 0)
        self.assertEqual(int((neu == 4).sum()), int((stueck == 4).sum()))

    def test_ohne_hautfarbe_bleibt_es_wie_vorher(self):
        nachbarn, zelle, inhalt, hoehe, stueck, streifen = self._netz()
        _, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertEqual(bericht['zubehoer_dazu_flaechen'], 0)

    def test_der_kopf_waechst_nie_mit(self):
        nachbarn, zelle, inhalt, hoehe, stueck, streifen = self._netz()
        hautfarbe = np.ones(len(zelle), dtype=bool)
        hautfarbe[streifen] = False
        hoehe[streifen] = 2.0                                                # über kopf_ab
        neu, _ = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck, hautfarbe)
        self.assertTrue((neu[streifen] == 0).all())


if __name__ == '__main__':
    unittest.main()
