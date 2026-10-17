# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: die Kleidungsmaske ohne Löcher und mit glattem Rand (`Kleidung.kleidungsbereinigung.Kleidungsbereinigung`).

Anlass (Edgar, Unterhose von der Seite): „die Hose hat keinen Saum, die Hose hat Texturprobleme (Haut geht durch)". Die Sapiens-Maske ließ Flächen mitten in der Hose als Haut stehen (49 Löcher bis 9 cm²) und hatte einen
Zackenrand. Kunstnetz: ein Gitter aus Dreiecken (je Zelle zwei), Etikett 1 = Oberteil, 0 = kein Stück, 4 = Zubehör; Flächeninhalt je Fläche frei wählbar.
Sabotage-Gegenproben: `LOCH_CM2 = 0` → `test_ein_kleines_loch_wird_gefuellt` rot; `GLAETTEN = 0` → `test_eine_spitze_am_rand_faellt_weg` rot; `~self.kopf` aus `kandidat` streichen → `test_der_kopf_bleibt_kopf` rot.
"""

import unittest

import numpy as np
from Kleidung.kleidungsbereinigung import Kleidungsbereinigung

from ._kleidungsgitter import _bau


class LoecherTest(unittest.TestCase):
    def test_ein_kleines_loch_wird_gefuellt(self):
        f, nachbarn, zelle, inhalt, hoehe = _bau()
        stueck = np.ones(len(f), dtype=np.int8)
        loch = np.isin(zelle, [9 * 20 + 9, 9 * 20 + 10, 10 * 20 + 9, 10 * 20 + 10])     # 2 × 2 Zellen in der Mitte
        stueck[loch] = 0
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertTrue((neu == 1).all())
        self.assertEqual(bericht['loecher_gefuellt'], 1)
        self.assertEqual(bericht['loch_flaechen'], int(loch.sum()))

    def test_ein_grosses_loch_bleibt(self):
        """Ab `LOCH_CM2` ist es kein Loch mehr (Hand im Ärmel, Halsausschnitt, Bart)."""
        f, nachbarn, zelle, inhalt, hoehe = _bau()
        stueck = np.ones(len(f), dtype=np.int8)
        loch = np.isin(zelle, [9 * 20 + 9, 9 * 20 + 10, 10 * 20 + 9, 10 * 20 + 10])
        stueck[loch] = 0
        inhalt[loch] = 10.0 * 1e-4                                # 8 Flächen zu je 10 cm²: 80 cm² > 25
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertEqual(bericht['loecher_gefuellt'], 0)
        self.assertTrue((neu[loch] == 0).all())

    def test_der_kopf_bleibt_kopf(self):
        """Eine Insel oberhalb der Kopfhöhe ist nie Kleidung — auch nicht als kleines Loch."""
        f, nachbarn, zelle, inhalt, hoehe = _bau()
        stueck = np.ones(len(f), dtype=np.int8)
        loch = np.isin(zelle, [9 * 20 + 9, 9 * 20 + 10, 10 * 20 + 9, 10 * 20 + 10])
        stueck[loch] = 0
        hoehe[loch] = 2.0                                         # über kopf_ab
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertEqual(bericht['loecher_gefuellt'], 0)
        self.assertTrue((neu[loch] == 0).all())

    def test_zubehoer_in_der_hose_bleibt(self):
        """Ein Gürtel (Zubehör, Etikett 4) mitten im Stoff ändert sich weder durch die Löcher noch durch die Glättung."""
        f, nachbarn, zelle, inhalt, hoehe = _bau()
        stueck = np.ones(len(f), dtype=np.int8)
        gurt = np.isin(zelle, [10 * 20 + x for x in range(5, 15)])
        stueck[gurt] = 4
        neu, _ = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertTrue((neu[gurt] == 4).all())

    def test_ein_loch_zwischen_zwei_stuecken_gehoert_zum_staerkeren(self):
        """Ein Loch an der Grenze von Oberteil (1) und Hose (2) nimmt das Stück, das mehr als 90 % seines Rands stellt — sonst bleibt es."""
        f, nachbarn, zelle, inhalt, hoehe = _bau()
        stueck = np.where(zelle % 20 < 10, 1, 2).astype(np.int8)                # linke Hälfte 1, rechte 2
        loch = np.isin(zelle, [9 * 20 + 9, 9 * 20 + 10, 10 * 20 + 9, 10 * 20 + 10])      # genau auf der Grenze
        stueck[loch] = 0
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertEqual(bericht['loecher_gefuellt'], 0, 'der Rand ist halb 1, halb 2: kein Stück umschließt es zu 90 %')


class RandTest(unittest.TestCase):
    """Die Haut-Seite ist hier selbst groß (1 cm² je Fläche, 400 cm²): sie darf nicht als „Loch“ im Stoff gelten."""

    def test_eine_spitze_am_rand_faellt_weg(self):
        f, nachbarn, zelle, inhalt, hoehe = _bau(cm2_je_flaeche=1.0)
        stueck = np.where(zelle % 20 < 10, 1, 0).astype(np.int8)                # linke Hälfte Stoff, rechte Haut
        spitze = int(np.flatnonzero(zelle == 5 * 20 + 14)[0])                    # ein einzelnes Dreieck Stoff mitten in der Haut
        stueck[spitze] = 1
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertEqual(neu[spitze], 0)
        self.assertGreaterEqual(bericht['rand_geaendert_flaechen'], 1)

    def test_die_masse_des_stoffs_bleibt(self):
        """Die Glättung nimmt dem Stoff nichts Nennenswertes weg: der gerade Rand bleibt (höchstens ein Streifen von 2 % verschoben)."""
        f, nachbarn, zelle, inhalt, hoehe = _bau(cm2_je_flaeche=1.0)
        stueck = np.where(zelle % 20 < 10, 1, 0).astype(np.int8)
        neu, _ = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertLess(abs(int((neu == 1).sum()) - int((stueck == 1).sum())) / int((stueck == 1).sum()), 0.02)

    def test_ein_einiges_stueck_aendert_sich_nicht(self):
        f, nachbarn, zelle, inhalt, hoehe = _bau()
        stueck = np.full(len(f), 2, dtype=np.int8)
        neu, bericht = Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertTrue((neu == 2).all())
        self.assertEqual(bericht['rand_geaendert_flaechen'], 0)
        self.assertEqual(bericht['loecher_gefuellt'], 0)

    def test_die_eingabe_wird_nicht_veraendert(self):
        f, nachbarn, zelle, inhalt, hoehe = _bau(cm2_je_flaeche=1.0)
        stueck = np.where(zelle % 20 < 10, 1, 0).astype(np.int8)
        stueck[int(np.flatnonzero(zelle == 5 * 20 + 14)[0])] = 1
        vorher = stueck.copy()
        Kleidungsbereinigung(nachbarn, inhalt, hoehe, kopf_ab=1.0).bereinigen(stueck)
        self.assertTrue((stueck == vorher).all())


class RandbandTest(unittest.TestCase):
    """`Kleidung.kleidungsrand.Kleidungsrand`: der hautfarbene Textursaum an der Kante des Objekts (Edgar: „die Hose hat keinen Saum“). Kunstobjekt: 20 × 20 Zellen, die unteren Zeilen hautfarben (der Saum).
    Sabotage-Gegenproben: `RINGE = 1` → `test_das_band_ist_acht_ringe_breit` rot; die Bedingung `& hautfarbe[nxt]` streichen → `test_ein_hautfarbenes_stueck_verliert_nur_den_streifen` rot."""

    def test_der_hautfarbene_saum_an_der_kante_faellt_weg(self):
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, _, _ = _bau()
        nachbarn = Kleidungsrand.nachbarn_aus(f)
        haut = (zelle // 20) < 3                                              # die untersten 3 Zellzeilen: Saum
        weg = Kleidungsrand.hautband(nachbarn, haut)
        self.assertTrue(weg[haut].all(), 'drei Zeilen Saum liegen binnen acht Ringen und hängen am Rand')
        self.assertFalse(weg[~haut].any(), 'Stoff bleibt')

    def test_hautfarbe_mitten_im_stoff_bleibt(self):
        """Ein hautfarbener Fleck, der nicht am Rand hängt (Naht, Gesichtstextur), wird nicht angefasst."""
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, _, _ = _bau()
        haut = np.isin(zelle, [10 * 20 + 10, 10 * 20 + 11, 11 * 20 + 10, 11 * 20 + 11])
        self.assertFalse(Kleidungsrand.hautband(Kleidungsrand.nachbarn_aus(f), haut).any())

    def test_das_band_ist_acht_ringe_breit(self):
        """Eine ganz hautfarbene Fläche verliert nur ein Band von `RINGE` Flächen — die Mitte bleibt."""
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, _, _ = _bau(n=40)
        weg = Kleidungsrand.hautband(Kleidungsrand.nachbarn_aus(f), np.ones(len(f), dtype=bool))
        self.assertTrue(weg.any() and not weg.all())
        mitte = (zelle // 40 > 12) & (zelle // 40 < 27) & (zelle % 40 > 12) & (zelle % 40 < 27)
        self.assertFalse(weg[mitte].any(), 'weiter als acht Ringe vom Rand bleibt alles')

    def test_ein_hautfarbenes_stueck_verliert_nur_den_streifen(self):
        from Kleidung.kleidungsrand import Kleidungsrand

        f, _, zelle, _, _ = _bau(n=40)
        weg = Kleidungsrand.hautband(Kleidungsrand.nachbarn_aus(f), np.ones(len(f), dtype=bool))
        self.assertLess(weg.mean(), 0.7)


class InselTest(unittest.TestCase):
    """Eine Insel aus lauter Hautfarbe ohne Nachbarn im Stoff (bei Edgar 203 von 6.694 Bandflächen, als beige Flecken am Saum) nimmt die UV der räumlich nächsten Stofffläche — aber nur in Reichweite."""

    def _bau(self, abstand_insel):
        from scipy.sparse import csr_matrix

        # Flächen 0 und 1: Stoff, benachbart; 2 und 3: Insel (nur untereinander benachbart); 4 und 5: eine zweite Insel weit weg
        paare = [(0, 1), (2, 3), (4, 5)]
        zeilen = [a for a, b in paare] + [b for a, b in paare]
        spalten = [b for a, b in paare] + [a for a, b in paare]
        nachbarn = csr_matrix((np.ones(6), (zeilen, spalten)), shape=(6, 6))
        band = np.array([False, False, True, True, True, True])
        uv = np.zeros((6, 3, 2))
        uv[:, :, 0] = np.arange(6)[:, None]
        mitten = np.array([[0, 0, 0], [0.1, 0, 0], [0.1 + abstand_insel, 0, 0], [0.1 + abstand_insel, 0.01, 0], [2.0, 0, 0], [2.0, 0.01, 0]])
        return nachbarn, band, uv, mitten

    def test_die_insel_nimmt_die_uv_der_naechsten_stofflaeche(self):
        from Kleidung.kleidungsrand import Kleidungsrand

        nachbarn, band, uv, mitten = self._bau(0.02)
        neu, umgefaerbt = Kleidungsrand.umfaerben(nachbarn, band, uv, mitten)
        self.assertEqual(umgefaerbt.tolist(), [False, False, True, True, False, False])
        self.assertTrue((neu[2:4, :, 0] == 1).all(), 'Fläche 1 ist die nächste Stofffläche')
        self.assertTrue((neu[4:, :, 0] == uv[4:, :, 0]).all(), 'die ferne Insel (1,9 m weg) bleibt, wie sie ist')

    def test_ohne_mitten_bleibt_die_insel_wie_vorher(self):
        from Kleidung.kleidungsrand import Kleidungsrand

        nachbarn, band, uv, _ = self._bau(0.02)
        neu, umgefaerbt = Kleidungsrand.umfaerben(nachbarn, band, uv)
        self.assertFalse(umgefaerbt.any())
        self.assertTrue((neu == uv).all())

    def test_eine_insel_ausserhalb_der_reichweite_bleibt(self):
        from Kleidung.kleidungsrand import Kleidungsrand

        nachbarn, band, uv, mitten = self._bau(0.2)
        _, umgefaerbt = Kleidungsrand.umfaerben(nachbarn, band, uv, mitten)
        self.assertFalse(umgefaerbt[2:4].any(), '20 cm sind kein Saum mehr')


class HaarabzugTest(unittest.TestCase):
    """Eine Fläche, die der Schritt „haar“ als Haar führt, steht nicht auch in der Kleidung (Zauberer: 6.614 Flächen in beiden Objekten)."""

    def _ablage(self, haar):
        import shutil
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace

        from ._pruefablage import Pruefablage

        tmp = Path(tempfile.mkdtemp(prefix='haarabzug_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        if haar is not None:
            np.savez(tmp / 'haar_maske.npz', haar=haar)
        return SimpleNamespace(arbeit=lambda name: tmp / name)

    @staticmethod
    def _regel():
        from types import SimpleNamespace

        return SimpleNamespace(abschliessen=lambda stueck: {'stueck': np.asarray(stueck), 'kleidung': np.asarray(stueck) > 0})

    def test_haar_wird_aus_der_kleidung_genommen_der_hut_bleibt(self):
        from core.dienste.meshfigurhaarabzug import Meshfigurhaarabzug

        stueck = np.array([1, 1, 2, 4, 3, 0], dtype=np.int8)
        haar = np.array([True, False, True, True, False, True])
        neu = Meshfigurhaarabzug.abziehen(self._ablage(haar), {'stueck': stueck}, self._regel())
        self.assertEqual(neu['stueck'].tolist(), [0, 1, 0, 4, 3, 0], 'Flächen 0 und 2 waren Haar; der Hut (4) bleibt Zubehör')

    def test_ohne_haar_oder_ablage_bleibt_die_maske(self):
        from core.dienste.meshfigurhaarabzug import Meshfigurhaarabzug

        maske = {'stueck': np.array([1, 2, 0], dtype=np.int8)}
        self.assertIs(Meshfigurhaarabzug.abziehen(self._ablage(None), maske, self._regel()), maske)
        self.assertIs(Meshfigurhaarabzug.abziehen(self._ablage(np.zeros(3, dtype=bool)), maske, self._regel()), maske)
        self.assertIs(Meshfigurhaarabzug.abziehen(self._ablage(np.ones(5, dtype=bool)), maske, self._regel()), maske, 'andere Flächenzahl: nichts anfassen')


class VerdrahtungTest(unittest.TestCase):
    """Wächter: der Schritt „kleidung“ ruft die Bereinigung, zieht den langen Bart ab und schält das Randband ab (Quelltext, ohne Django-Lauf)."""

    def test_der_kleidungsschritt_bereinigt_vor_dem_ablegen_der_maske(self):
        from pathlib import Path

        quelle = (Path(__file__).resolve().parents[2] / 'dienste' / 'meshfigurkleidung.py').read_text(encoding='utf-8')
        self.assertIn('maske, bereinigung = self._bereinigen(maske, regel, ', quelle)
        self.assertIn('maske = self._bart_abziehen(maske, regel)', quelle)
        self.assertLess(quelle.index('self._bereinigen(maske, regel, '), quelle.index("np.savez_compressed(self.ablage.arbeit('kleidung_maske.npz')"))
        self.assertIn("hautfarbe=np.asarray(modell.ist_haut(entscheidung['farben'])", quelle)
        self.assertIn('self._hautrand_behandeln(scan, wahl, hautfarbe', quelle)        # seit 13.10.2026: umfärben statt abschälen (`hautband`-Option); vorher `_ohne_hautrand`
        self.assertIn('Kleidungsrand.umfaerben(nachbarn, band, scan.uv_ecken[ids], np.asarray(scan.punkte)', quelle)
        self.assertIn('Kleidungsrand.hautband(nachbarn, hautfarbe[ids], scan.flaecheninhalte()[ids])', quelle, 'die kleinen hautfarbenen Inseln im Innern (14.10.2026) brauchen den Flächeninhalt')
        self.assertLess(quelle.index('self._bereinigen(maske, regel, '), quelle.index('Meshfigurhaarabzug.abziehen(self.ablage, maske, regel)'), 'Haar nach dem Bereinigen abziehen')


if __name__ == '__main__':
    unittest.main()
