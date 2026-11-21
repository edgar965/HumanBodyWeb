"""`Kleiderkette` und der Schritt „stoff“ mit Ketten (21.11.2026, Schritt 2 „Kette“: Halsketten und Anhänger der Kleiderbibliothek schwingen, abgelegt wie Stoff).

Geprüft: `ist_kette` am Namen; `ist_stueck` liest das Bibliotheksstück aus `eintrag.json` (`kennung`) — `rocker_necklace` ja, `chaingauntlet` (Handschuh) nein, ohne Datei zählt
die Zeile; `Kleiderstofflauf.stuecke` nimmt Ketten jeder Art (auch Requisit) mit und merkt sie in `ketten`, lässt abgewählte Stücke und Nicht-Stoff ohne Kette weg;
`Kleiderkette.rechnen` an einem geneigten Ring um einen Zylinder (Y oben, Mischung = 1): Versatz je Bild/jedes, Bericht mit `sekunden` als dict (`Kleiderstofflauf.schreiben`
trägt dort 'packen' ein — als Zahl brach das erste Kettenstück ab, gefunden beim Lesen 21.11.2026).
Echte Dateien nur in `ProjektTemp/pruefungen` (`Pruefablage`). Läuft nur auf Ansage; nicht gelaufen beim Schreiben (21.11.2026). Sabotage (von Hand): in `stuecke` die
Abfrage `Kleiderkette.ist_stueck` weglassen → „Kette als Requisit“ rot; in `Kleiderkette.rechnen` 'sekunden' als Zahl lassen → „sekunden ist dict“ rot.
"""
import json
import sys
import unittest
from pathlib import Path

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.insert(0, _pfad)

import torch  # noqa: E402

from ._pruefablage import Pruefablage  # noqa: E402

KARTE = 'cuda'


def _eintrag(ordner, stueck, kennung):
    d = Path(ordner) / 'z' / stueck
    d.mkdir(parents=True, exist_ok=True)
    (d / 'eintrag.json').write_text(json.dumps({'kennung': kennung, 'anzeige_name': kennung}), encoding='utf-8')
    return d


def _zeile(sid, art, wahl='z'):
    return {'id': sid, 'art': art, 'wahl': wahl, 'z': {'netz': '/api/meshgenesis/test/x/kleid/weiblich/z/%s' % sid}}


class Erkennen(unittest.TestCase):
    databases = []

    def test_ist_kette_am_namen(self):
        from meshgenesis_kleiderkette import Kleiderkette
        self.assertTrue(Kleiderkette.ist_kette('ki_requisit_1', 'Halskette'))
        self.assertTrue(Kleiderkette.ist_kette(None, 'barbossa_pendant'))
        self.assertFalse(Kleiderkette.ist_kette('ki_requisit_1', 'chaingauntlet', None))

    def test_ist_stueck_liest_eintrag(self):
        from meshgenesis_kleiderkette import Kleiderkette
        with Pruefablage.ordner() as ordner:
            ja = _eintrag(ordner, 'ki_requisit_1', 'rocker_necklace')
            nein = _eintrag(ordner, 'ki_requisit_2', 'chaingauntlet')
            self.assertTrue(Kleiderkette.ist_stueck({'id': 'ki_requisit_1'}, ja))
            self.assertFalse(Kleiderkette.ist_stueck({'id': 'ki_requisit_2'}, nein))
            self.assertTrue(Kleiderkette.ist_stueck({'id': 'eigen_kette_hals'}, Path(ordner) / 'z' / 'fehlt'))   # ohne eintrag.json: die Zeile


class Stoffstuecke(unittest.TestCase):
    databases = []

    def test_ketten_jeder_art_und_nur_gezeigte(self):
        from meshgenesis_kleiderstoff_lauf import Kleiderstofflauf
        with Pruefablage.ordner() as ordner:
            _eintrag(ordner, 'ki_requisit_1', 'rocker_necklace')
            _eintrag(ordner, 'ki_requisit_2', 'chaingauntlet')
            _eintrag(ordner, 'gk_kleid', 'g9_kleid')
            lauf = Kleiderstofflauf.__new__(Kleiderstofflauf)
            lauf.ordner = Path(ordner)
            lauf.liste = {'stuecke': [_zeile('ki_requisit_1', 'requisit'), _zeile('ki_requisit_2', 'freie_form'), _zeile('gk_kleid', 'kleid'),
                                      _zeile('ki_hose', 'hose', wahl='aus'), _zeile('ki_schuhe', 'schuhe')]}
            stuecke = lauf.stuecke()
            self.assertEqual([s[0] for s in stuecke], ['ki_requisit_1', 'gk_kleid'])
            self.assertEqual(lauf.ketten, {'ki_requisit_1'})
            self.assertEqual(stuecke[0][2], Path(ordner) / 'z' / 'ki_requisit_1')
            self.assertEqual([s[0] for s in lauf.stuecke(nur=['gk_kleid'])], ['gk_kleid'])


def _yoben(p):
    return torch.stack([p[:, 0], p[:, 2], -p[:, 1]], 1)


class Bewegung:
    u"""Schnittstelle von `Kleiderstoffbewegung`/`Sprungbewegung` für `Kleiderkette`: alles steht, Mischung = 1."""

    def __init__(self, koerper, dreiecke, bilder=10):
        self.k, self.k_dreiecke = koerper, dreiecke
        self.bilder, self.fps = list(range(bilder)), 60.0

    def stueck_im_bild(self, i, ruhe, knochen, gewicht):
        return ruhe

    def koerper(self, i):
        return self.k

    def dreh_mischung(self, i, knochen, gewicht):
        return torch.eye(3, dtype=torch.float64, device=KARTE).expand(len(knochen), 3, 3)


class Rechnen(unittest.TestCase):
    databases = []

    def test_versatz_und_bericht(self):
        from meshgenesis_kleiderkette import Kleiderkette
        from meshgenesis_kleiderstoff import Kleiderstoff
        from Stoffsolver.tests.test_kettenbahn import _zylinder
        from Stoffsolver.tests.test_kettenlinie import _ring
        mitten, kette = _ring(radius=0.08)
        k, j = len(mitten), 6
        a, r = torch.arange(k, device=KARTE), torch.arange(j, device=KARTE)
        b = (a + 1) % k
        q0, q1 = (a[:, None] * j + r).reshape(-1), (a[:, None] * j + (r + 1) % j).reshape(-1)
        p0, p1 = (b[:, None] * j + r).reshape(-1), (b[:, None] * j + (r + 1) % j).reshape(-1)
        dreiecke = torch.cat([torch.stack([q0, q1, p1], 1), torch.stack([q0, p1, p0], 1)])
        koerper, kd = _zylinder()
        netz = {'ruhe': _yoben(kette), 'dreiecke': dreiecke, 'knochen': torch.zeros((len(kette), 1), dtype=torch.int64, device=KARTE),
                'gewicht': torch.ones((len(kette), 1), dtype=torch.float64, device=KARTE)}
        kk = Kleiderkette(Bewegung(_yoben(koerper), kd))
        versatz, bericht = kk.rechnen(netz, jedes=2)
        self.assertEqual(tuple(versatz.shape), (5, len(kette), 3))
        self.assertEqual(versatz.dtype, torch.float32)
        self.assertTrue(bool(torch.isfinite(versatz).all()))
        self.assertIsInstance(bericht['sekunden'], dict)
        self.assertIn('simulation', bericht['sekunden'])
        self.assertAlmostEqual(bericht['zeitskala'], round(Kleiderstoff.EICH_FPS / 60.0, 4))
        self.assertLess(float((versatz[2] - kk.bahn.versatz(4)).abs().max()), 1e-6)           # Mischung = 1: Versatz in der Ruhe = Versatz im Bild


if __name__ == '__main__':
    unittest.main()
