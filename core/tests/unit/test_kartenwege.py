# -*- coding: utf-8 -*-
"""Die Bausteine für „ohne Wartepunkt“ (18.11.2026, Edgar: „fixe alle“): `Kartenrunden` (Pythons `round` auf der Karte), `Kartenpost` (Zahlen zur Karte über
angehefteten Speicher), `Kartenwerte` (Antwortzahlen, in einer Kopie abgeholt), `G9knochenformelkarte` (Knochenformeln auf der Karte gegen die Python-Fassung).

Gegenproben, aus denen die Tests stammen: `_wegwerf/kartenrunden_probe.py` (508.831 Werte gleich), `_wegwerf/knochenformel_probe.py` (36 Fälle gleich),
`_wegwerf/knochenformel_fremd_probe.py`; `Kartenvermutung` (Entscheidungen vermutet, auf der Karte geprüft): `_wegwerf/zug_referenz.py falsch`, `lagenentscheid_probe.py`.
Braucht die Grafikkarte (sonst übersprungen), `test_4` auch die Genesis-9-Bibliothek. Nicht gelaufen — läuft nur auf Ansage.
Sabotage: in `Kartenrunden.runden` durch die Python-Zahl `f` teilen statt durch den 0-d-Tensor → `test_1` rot; in `formelkernwarp.summen` die Summenformeln mit
`mal` statt `plus` → `test_4` rot.
"""
import random
import struct
import unittest

import torch


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class KartenwegeTest(unittest.TestCase):

    def test_1_runden_wie_python(self):
        from KoerperKI_alle.kartenpost import Kartenpost
        from KoerperKI_alle.kartenrunden import Kartenrunden
        from KoerperKI_alle.kartenwerte import Kartenwerte
        rnd = random.Random(3)
        werte = [rnd.uniform(-2.0, 2.0) for _ in range(20000)] + [k / 128.0 for k in range(-300, 301)] + [0.0, -0.0, -4e-7, 4e-7, 5e-7, -2.5e-6]
        for stellen in (4, 6):
            aus = Kartenwerte([Kartenrunden.runden(Kartenpost.hin(werte), stellen)], lambda x: x).wert()
            falsch = [w for w, a in zip(werte, aus) if struct.pack('<d', a) != struct.pack('<d', round(w, stellen))]
            self.assertEqual(falsch, [], 'Stellen %d' % stellen)

    def test_2_kartenpost_wie_torch_tensor(self):
        from KoerperKI_alle.kartenpost import Kartenpost
        werte = [[1.5, -0.0, 3.0], [1e-300, -2.0, 7.0]]
        self.assertTrue(torch.equal(Kartenpost.hin(werte), torch.tensor(werte, dtype=torch.float64, device='cuda')))
        self.assertTrue(torch.equal(Kartenpost.hin([3, -4, 5], torch.int64), torch.tensor([3, -4, 5], device='cuda')))

    def test_3_kartenwerte_in_einer_antwort(self):
        from KoerperKI_alle.kartenwerte import Kartenwerte
        t = torch.tensor([[1.0, 2.0], [3.0, 4.0]], dtype=torch.float64, device='cuda')
        daten = {'a': Kartenwerte.liste(t), 'b': [Kartenwerte([t.sum().reshape(1)], lambda s: round(s[0], 1))], 'c': 7}
        Kartenwerte.aufloesen(daten)
        self.assertEqual(daten, {'a': t.tolist(), 'b': [10.0], 'c': 7})

    def test_4_knochenformeln_wie_python(self):
        try:
            from core.api.g9figur import G9figur
            eintrag = G9figur._eintrag('luna_g9')
        except Exception:  # noqa: BLE001 — ohne Bibliothek gibt es nichts zu prüfen
            eintrag = None
        if not eintrag:
            self.skipTest('Genesis-9-Bibliothek fehlt')
        for wert in (0.0, 0.37):
            regler = dict(eintrag.get('regler') or {}, body_bs_ProportionLegsLength=wert)
            formeln = G9figur.formung({'regler': regler}, eintrag).formeln
            py, karte = formeln._knochen(), formeln._knochen_karte().als_dict()
            flach = lambda d: [(k, f, struct.pack('<3d', *map(float, w))) for k, v in d.items() for f, w in v.items()]  # noqa: E731
            self.assertEqual(flach(py), flach(karte))


    def test_5_vermutung_geprueft_und_verworfen(self):
        u"""`Kartenvermutung`: ohne Lauf abgeholt und gemerkt; im Lauf vermutet, Prüfbit 1 bei gleicher, 0 bei anderer Entscheidung; `verwerfen` vergisst sie."""
        from KoerperKI_alle.kartenvermutung import Kartenvermutung
        schluessel = ('test_kartenwege', 5)
        Kartenvermutung.verwerfen([schluessel])
        ja = torch.ones((), dtype=torch.bool, device='cuda')
        self.assertTrue(Kartenvermutung.wert(schluessel, ja, lambda t: bool(t)))
        for feld, bit in ((ja, 1), (~ja, 0)):
            with Kartenvermutung.lauf() as saetze:
                self.assertTrue(Kartenvermutung.wert(schluessel, feld, lambda _t: self.fail('im Lauf mit Vermutung darf nichts abgeholt werden')))
            self.assertEqual(Kartenvermutung.bits(saetze).tolist(), [bit])
        Kartenvermutung.verwerfen([schluessel])
        with Kartenvermutung.lauf() as saetze:
            self.assertFalse(Kartenvermutung.wert(schluessel, ~ja, lambda t: bool(t)))
        self.assertEqual(saetze, [])

    def test_6_listenpruefung_bei_anderer_laenge(self):
        from KoerperKI_alle.kartenvermutung import Kartenvermutung
        f = torch.tensor([1, 2, 3], device='cuda')
        self.assertTrue(bool(Kartenvermutung.gleich_liste(f, [1, 2, 3])))
        self.assertFalse(bool(Kartenvermutung.gleich_liste(f, [1, 2])))
        self.assertFalse(bool(Kartenvermutung.gleich_liste(f, [1, 2, 4])))


if __name__ == '__main__':
    unittest.main()
