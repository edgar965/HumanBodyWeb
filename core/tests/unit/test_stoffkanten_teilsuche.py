# -*- coding: utf-8 -*-
u"""Garderobe schneller (25.11.2026): Kanten als Felder, Nachbarsuche in Teilen, Codespur — dieselben Ergebnisse wie die Fassungen davor.

1. `G9stoffkanten.bereiche`: zwei Dreiecke mit gegenläufig geteilter Kante sind ein Bereich, mit gleichläufig geteilter zwei.
2. `G9stoffwicklung.geschlossene`: ein Würfel mit zwei verdrehten Seiten wird nach außen gedreht (genau die zwei), ein ganz nach innen gewickelter ganz; ein offener Würfel gilt nicht; ein
   Möbiusband gilt nicht.
3. `G9punktbaum.in_teilen` = volle Abstandsmatrix über die erlaubten Punkte (Gleichstand nach Nummer); keine erlaubten Punkte → unendlich / N.
4. `G9teilbindung.nachbarn` (ein Zug) = Gruppe für Gruppe (`_nachbarn_je_gruppe`).
5. `G9codespur`: ein anderer Faden zählt nicht mit; verschachtelte Abschnitte sammeln beide; danach ist die Werkzeugnummer frei; eine belegte Nummer → None.

Sabotage (nicht gelaufen): in `G9stoffkanten.bereiche` `gegen >= …beginn` weglassen → Fall 1 rot; in `koerper` `gleich` durch `1 - gleich` ersetzen → Fall 2 rot; in `punktbaum.cu`
`(bit[nr] & mk) == 0u` weglassen → Fälle 3 und 4 rot; in `G9codespur._beginn` die Faden-Abfrage weglassen → Fall 5 rot. Geschrieben, nicht gelaufen.
"""
import sys
import threading
import unittest

import torch
from django.conf import settings

for _p in (str(settings.TOOLS_ROOT), str(settings.TOOLS_ROOT / 'meshgenesis')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

KARTE = 'cuda'
WUERFEL = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]


def ecken():
    return torch.tensor([[x, y, z] for x in (0.0, 1.0) for y in (0.0, 1.0) for z in (0.0, 1.0)], dtype=torch.float64, device=KARTE)


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class StoffkantenTest(unittest.TestCase):

    def test_1_bereiche(self):
        from Genesis9.stoffkanten import G9stoffkanten
        self.assertEqual(G9stoffkanten([[0, 1, 2], [2, 1, 3]]).bereiche().tolist(), [0, 0])
        self.assertEqual(G9stoffkanten([[0, 1, 2], [1, 2, 3]]).bereiche().tolist(), [0, 1])
        self.assertEqual(G9stoffkanten([[0, 1, 2], [3, 4, 5]]).bereiche().tolist(), [0, 1])

    def test_2_geschlossene(self):
        from Genesis9.stoffwicklung import G9stoffwicklung
        aussen = WUERFEL if self._volumen(WUERFEL) > 0 else [list(reversed(f)) for f in WUERFEL]
        gilt, umdrehen, anzahl = G9stoffwicklung.geschlossene(ecken(), [list(reversed(f)) if i in (1, 4) else f for i, f in enumerate(aussen)])
        self.assertEqual((anzahl, gilt.tolist(), umdrehen.tolist()), (1, [True] * 6, [False, True, False, False, True, False]))
        gilt, umdrehen, anzahl = G9stoffwicklung.geschlossene(ecken(), [list(reversed(f)) for f in aussen])
        self.assertEqual((anzahl, umdrehen.tolist()), (1, [True] * 6))
        self.assertEqual(G9stoffwicklung.geschlossene(ecken(), aussen[:-1])[2], 0)
        band = [[0, 1, 3, 2], [2, 3, 5, 4], [4, 5, 0, 1]]                  # drei Vierecke, das letzte verdreht angeschlossen
        self.assertFalse(bool(G9stoffwicklung.geschlossene(ecken(), band)[0].any()))

    @staticmethod
    def _volumen(flaechen):
        p = ecken()
        return sum(float(torch.dot(p[f[0]], torch.linalg.cross(p[f[k]], p[f[k + 1]]))) for f in flaechen for k in (1, 2)) / 6.0


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class TeilsucheTest(unittest.TestCase):

    def setUp(self):
        g = torch.Generator(device=KARTE).manual_seed(7)
        self.z = (torch.randn(900, 3, dtype=torch.float64, device=KARTE, generator=g) * 20).round() / 20        # viele Gleichstände
        self.q = torch.randn(300, 3, dtype=torch.float64, device=KARTE, generator=g) * 1.2
        self.teil = torch.randint(0, 12, (900,), device=KARTE, generator=g)
        self.maske = torch.randint(0, 1 << 12, (300,), device=KARTE, generator=g) & torch.randint(0, 1 << 12, (300,), device=KARTE, generator=g)
        self.stoffteil = torch.randint(-1, 12, (300,), device=KARTE, generator=g).int()

    def test_3_in_teilen(self):
        from Genesis9.punktbaum import G9punktbaum
        d = self.q[:, None, :] - self.z[None, :, :]
        w = (d[..., 0] * d[..., 0] + d[..., 1] * d[..., 1]) + d[..., 2] * d[..., 2]
        darf = (torch.bitwise_right_shift(self.maske[:, None], self.teil[None, :]) & 1).bool()
        s, i = torch.sort(torch.where(darf, w, torch.full_like(w, float('inf'))), dim=1, stable=True)
        wert, nummer = G9punktbaum(self.z).in_teilen(self.q, 4, torch.bitwise_left_shift(torch.ones_like(self.teil), self.teil), self.maske)
        self.assertTrue(torch.equal(wert, s[:, :4]))
        self.assertTrue(torch.equal(nummer, torch.where(torch.isinf(s[:, :4]), torch.full_like(i[:, :4], 900), i[:, :4])))

    def test_4_ein_zug_wie_je_gruppe(self):
        from Genesis9.teilbindung import G9teilbindung
        bindung = G9teilbindung(self.stoffteil)
        for k, eigen in ((1, False), (4, True), (8, False)):
            with self.subTest(k=k, eigen=eigen):
                geprueft = bindung.geprueft(self.z, self.teil, self.q)
                alt = geprueft._nachbarn_je_gruppe(self.z, self.teil, self.q, k, eigen)
                neu = bindung.nachbarn(self.z, self.teil, self.q, k, eigen)
                self.assertTrue(torch.equal(alt[0], neu[0]))
                self.assertTrue(torch.equal(alt[1], neu[1]))


class CodespurTest(unittest.TestCase):

    @staticmethod
    def _arbeit():
        from Genesis9.kanalnamen import G9kanalnamen
        G9kanalnamen({'a': {'name': 'A', 'sichtbar': True}})

    @staticmethod
    def _klein():
        from Genesis9.pfade import G9pfade
        G9pfade.people_eigen()

    def test_5_faeden_und_verschachtelung(self):
        from Genesis9.codespur import G9codespur as Spur
        weiter, fertig = threading.Event(), threading.Event()

        def anderer():
            weiter.wait(10)
            self._arbeit()
            fertig.set()
        faden = threading.Thread(target=anderer)
        faden.start()
        with Spur.aufnahme() as dateien:
            weiter.set()
            fertig.wait(10)
            self._klein()
        faden.join()
        self.assertIn('pfade', Spur.namen(dateien))
        self.assertNotIn('kanalnamen', Spur.namen(dateien))
        with Spur.aufnahme() as aussen:
            with Spur.aufnahme() as innen:
                self._arbeit()
        self.assertIn('kanalnamen', Spur.namen(innen))
        self.assertTrue(innen <= aussen)
        self.assertIsNone(sys.monitoring.get_tool(Spur.KENNUNG))
        sys.monitoring.use_tool_id(Spur.KENNUNG, 'fremd')
        try:
            with Spur.aufnahme() as dateien:
                self._arbeit()
            self.assertIsNone(dateien)
        finally:
            sys.monitoring.free_tool_id(Spur.KENNUNG)


if __name__ == '__main__':
    unittest.main()
