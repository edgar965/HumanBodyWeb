"""Eigen Haar und Kämmfeld (16.11.2026): kleine Kunstfälle auf der Karte, keine echten Netze. Nur auf Ansage laufen lassen (`testsuite-nur-auf-ansage`).

  test_1  Kämmfeld aus Reglern: „nach hinten“ legt die Richtung auf −z, tangential zur Kopfhaut (Kugel); ohne Regler zeigt sie abwärts
  test_2  Kämmfeld aus Linien: Kämmlänge endet, wo die Linie steiler als 45° fällt; Länge = Bogenlänge
  test_3  Wurzel an der Kopfhaut: umgedrehte Linien werden zurückgedreht (klar), flache wie ihre Nachbarn
  test_4  Haarzylinder: größter Halbmesser je Zelle, Lücke aus den Nachbarn
  test_5  Eigenhaar.werte: Vorgabe für Fehlendes, Begrenzung, Unlesbares auf Vorgabe
  test_6  G9eigenhaarbau.sorten/eintrag: Haar und Bart, Kennung, Art, Regler mit Gruppe; der Bart endet auf `_beard` (Zusatz in der Mischung)
  test_7  „Haar – Generisch“ mit dem Generator als Sorte (16.11.2026 spät): Anteil-Regler mit Vorgabe 0, Präfix `eigen_haar.`; Mischung nur, wenn der Aufrufer ihn nennt
  test_8  Glatze (`Eigenhaar.kahl`): 0 kahl nichts, 1 nimmt den Scheitel und lässt den Kranz; die Stirn vor dem Hinterkopf
  test_9  Wellen (`Haarstraehnen._locke` mit `welle_m`): Höhe = Regler, Wellenlänge = Regler, eben ohne `locke`, nach außen mit
  test_10 Bartbereiche (`Eigenbart.bereiche`): Schnurrbart über, Kinn unter dem Mund, Wangen seitlich, Kotelette hinten oben, Hals; Maß am Kinn unten = 1
  test_11 dichte Strähnen (`Haarbueschel`): Zahl nach Kopfhaut ÷ (FLAECHE_JE_D2 · d²), mindestens MIN_HAARE je Strähne; Plätze im Querschnitt (Breite d, über der Leitsträhne);
          Verlauf von der Wurzel in den Platz, zur Spitze schmaler; Regler „Strähnendicke“ bis 5 cm → `straehne_m`
  test_12 Rezept (`Haarrezept`): Mischen je Punkt nur über behaarende Rezepte, Maske ab MISCH_MASKE, Dicke nach Anteil; Aufsetzen mit Kopfmaß, Länge und Fallfeld
  test_13–17 (16./17.11.2026) Restlänge und „ende“, Restkurven, Anschmiegen an die Leitsträhne, Einscheren des Rezepts, Netzstück ohne Farbbild — Sabotage je im Docstring
Sabotage (je Test): Vorzeichen von `ez` in `aus_einstellungen` umdrehen → test_1 rot; `STEIL_COS` auf 0,99 → test_2 rot; `KLAR_M` auf 1 m → test_3 rot (alle unklar);
max_pool weg → test_4 rot; Begrenzung in `werte` weg → test_5 rot; `erzeugt` in `G9haargenerisch.anteile` nicht in die Reihenfolge → test_7 rot; Vorzeichen von
`GLATZE_VORN` umdrehen → test_8 rot; `2 * math.pi * bogen / wellenlaenge_m` → `… * bogen` → test_9 rot; `0.5 * self.d +` in `Haarbueschel.plaetze` weg → test_11 rot (Haare in
der Leitsträhne).
"""
import math
import sys
import unittest

import torch

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.append(_pfad)

KARTE = torch.cuda.is_available()


@unittest.skipUnless(KARTE, 'braucht CUDA')
class EigenhaarTest(unittest.TestCase):
    databases = []

    @staticmethod
    def kugel(n=400, r=0.1):
        """Punkte auf der oberen Halbkugel um (0, 1.6, 0) und ihre Normalen (Fibonacci) — Kunstkopf."""
        i = torch.arange(n, dtype=torch.float64, device='cuda') + 0.5
        z = i / n                                                       # 0 … 1: nur obere Hälfte (y ≥ 0)
        th = math.pi * (1 + 5 ** 0.5) * i
        rr = torch.sqrt(1 - z * z)
        nrm = torch.stack([rr * torch.cos(th), z, rr * torch.sin(th)], 1)
        return torch.tensor([0.0, 1.6, 0.0], dtype=torch.float64, device='cuda') + r * nrm, nrm

    def test_1_kaemmfeld_regler(self):
        from haar_Bart.haarkaemmfeld import Haarkaemmfeld
        p, n = self.kugel()
        f = Haarkaemmfeld.aus_einstellungen(p, n, {'nach_hinten': 1.0, 'scheitel': 0.0, 'kaemmlaenge_cm': 5.0})
        seite = (p[:, 1] < 1.66) & (p[:, 2].abs() < 0.03)               # seitlich, nicht oben
        self.assertLess(float((f.r[seite] * n[seite]).sum(1).abs().max()), 1e-6)       # tangential
        self.assertLess(float(f.r[seite, 2].mean()), -0.5)                              # nach hinten
        self.assertAlmostEqual(float(f.k[0]), 0.05, places=9)
        g = Haarkaemmfeld.aus_einstellungen(p, n, {'scheitel': 0.0})
        unten = p[:, 1] < 1.63
        self.assertLess(float(g.r[unten, 1].mean()), -0.5)                              # ungekämmt: abwärts

    def test_2_kaemmfeld_linien(self):
        from haar_Bart.haarkaemmfeld import Haarkaemmfeld
        t = torch.linspace(0, 1, 17, dtype=torch.float64, device='cuda')
        x = torch.where(t <= 0.5, t * 0.10, torch.full_like(t, 0.05))                 # erst 5 cm waagerecht nach +x …
        y = 1.70 - torch.where(t <= 0.5, torch.zeros_like(t), (t - 0.5) * 0.20)       # … dann 10 cm senkrecht abwärts
        linie = torch.stack([x, y, torch.zeros_like(t)], 1)[None]
        f = Haarkaemmfeld.aus_linien(linie, linie[0, :1])
        self.assertAlmostEqual(float(f.k[0]), 0.05, places=6)
        self.assertAlmostEqual(float(f.l[0]), 0.15, places=6)
        self.assertGreater(float(f.r[0, 0]), 0.99)

    def test_3_wurzel_an_kopfhaut(self):
        from haar_Bart.haarvorlagelinien import Haarvorlagelinien as H
        kopf = torch.tensor([[0.0, 1.7, 0.0]], dtype=torch.float64, device='cuda')
        s = torch.linspace(0, 1, H.PUNKTE, dtype=torch.float64, device='cuda')
        lang = torch.stack([torch.zeros_like(s), 1.7 - 0.3 * s, torch.zeros_like(s)], 1)               # klar: Wurzel oben am Kopf
        flach = torch.stack([0.003 + 0.004 * s, 1.7 + torch.zeros_like(s), torch.zeros_like(s)], 1)    # flach, beide Enden nah
        li = torch.stack([lang.flip(0), flach.flip(0), lang + torch.tensor([0.005, 0, 0], dtype=torch.float64, device='cuda')])
        aus, gedreht = H.wurzel_an_kopfhaut(li, kopf)
        self.assertTrue(torch.allclose(aus[0], lang))
        self.assertGreaterEqual(gedreht, 1)

    def test_4_haarzylinder(self):
        from haar_Bart.haarzylinder import Haarzylinder
        mitte = torch.zeros(3, dtype=torch.float64, device='cuda')
        z = Haarzylinder(mitte, 0.0, 0.01, 10, 36)
        p = torch.tensor([[0.0, 0.05, 0.2], [0.01, 0.05, 0.2], [0.0, 0.06, 0.2]], dtype=torch.float64, device='cuda')
        k = z.karte(p, torch.tensor([[0, 1, 2]], device='cuda'))
        zl = int(z.zeile(torch.tensor(0.05, dtype=torch.float64, device='cuda')))
        f = int(z.fach(torch.tensor(0.0, dtype=torch.float64, device='cuda')))
        self.assertAlmostEqual(float(k[zl, f]), 0.2, places=3)
        self.assertGreater(float(k[zl + 2, f]), 0.0)                    # Lücke aus den Nachbarn
        self.assertLess(float(k[0, (f + 18) % 36]), 0.0)                # gegenüber nichts

    def test_5_werte(self):
        from haar_Bart.eigenhaar import Eigenhaar
        w = Eigenhaar.werte({'laenge_cm': 500, 'scheitel': 'x', 'unbekannt': 3})
        self.assertEqual(w['laenge_cm'], 100.0)
        self.assertEqual(w['scheitel'], 1.0)
        self.assertEqual(w['volumen_cm'], 1.5)
        self.assertNotIn('unbekannt', w)

    def test_6_eintrag(self):
        from core.dienste.g9eigenhaarbau import G9eigenhaarbau
        e = G9eigenhaarbau.eintrag('eigen_haar')
        self.assertEqual((e['id'], e['art']), ('eigen_haar', 'haar'))
        self.assertEqual([s['id'] for s in G9eigenhaarbau.sorten()], ['eigen_haar', 'eigen_beard'])
        self.assertTrue(all(r.get('gruppe') for r in e['regler']))
        self.assertTrue({'laenge_cm', 'glatze', 'welle_cm', 'wellenlaenge_cm', 'locken'} <= {r['name'] for r in e['regler']})
        bart = {r['name'] for r in G9eigenhaarbau.eintrag('eigen_beard')['regler']}
        self.assertTrue({'schnurrbart', 'kinn', 'wangen', 'koteletten', 'hals', 'spitz', 'bartansatz', 'welle_cm'} <= bart)
        from Genesis9.haargenerisch import G9haargenerisch
        self.assertTrue('eigen_beard'.endswith(G9haargenerisch.ZUSATZ))                  # zusätzlich zur Frisur getragen

    def test_7_generisch_mit_generator(self):
        from unittest import mock

        from Genesis9.haargenerisch import G9haargenerisch
        frisuren = [{'id': 'kin_hair', 'name': 'Kin', 'art': 'haar', 'zeigbar': True, 'regler': []},
                    {'id': 'toulouse_hair', 'name': 'Toulouse', 'art': 'haar', 'zeigbar': True, 'regler': []}]
        sorten = [{'id': 'eigen_haar', 'name': 'Eigen Haar', 'regler': [{'name': 'glatze', 'anzeige': 'Glatze', 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'gruppe': 'Haaransatz'}]}]
        with mock.patch.object(G9haargenerisch, 'frisuren', return_value=frisuren), \
                mock.patch('Genesis9.haarachsen.G9haarachsen.vorhanden', return_value=False), \
                mock.patch('Genesis9.kleidmorphe.G9kleidmorphe.regler', return_value=[]):
            regler = {r['name']: r for r in G9haargenerisch.regler(frisuren, sorten)}
            self.assertEqual(regler['sorte.eigen_haar']['vorgabe'], 0.0)
            self.assertEqual(regler['sorte.kin_hair']['vorgabe'], 1.0)
            self.assertEqual(regler['eigen_haar.glatze']['gruppe'], 'Eigen Haar')
            werte = {'sorte.eigen_haar': 1.0, 'sorte.kin_hair': 0.0, 'eigen_haar.glatze': 0.5}
            self.assertEqual(G9haargenerisch.mischung(werte, sorten), [('eigen_haar', 1.0, {'glatze': 0.5})])
            self.assertEqual(G9haargenerisch.aufloesen(werte), ('kin_hair', {}))              # ohne `erzeugt`: wie vorher
            anteile = G9haargenerisch.anteile({'sorte.eigen_haar': 0.3, 'sorte.kin_hair': 0.7}, sorten)
            self.assertAlmostEqual(anteile['eigen_haar'], 0.3, places=9)

    def test_8_glatze(self):
        from haar_Bart.eigenhaar import Eigenhaar
        p, _n = self.kugel()
        alle = torch.ones(len(p), dtype=torch.bool, device='cuda')
        self.assertFalse(bool(Eigenhaar.kahl(p, alle, 0.0).any()))
        kahl = Eigenhaar.kahl(p, alle, 1.0)
        self.assertTrue(bool(kahl[p[:, 1].argmax()]))                                         # der Scheitel
        self.assertFalse(bool(kahl[p[:, 1].argmin()]))                                        # der Kranz
        halb = Eigenhaar.kahl(p, alle, 0.6)
        band = (p[:, 1] > 1.66) & (p[:, 1] < 1.68)
        self.assertGreater(float(halb[band & (p[:, 2] > 0)].double().mean()), float(halb[band & (p[:, 2] < 0)].double().mean()))   # vorn zuerst

    def test_9_wellen(self):
        from haar_Bart.haarstraehnen import Haarstraehnen
        k = Haarstraehnen.__new__(Haarstraehnen)
        bogen = torch.linspace(0, 0.4, 401, dtype=torch.float64, device='cuda')[None]
        s = torch.ones_like(bogen)
        phase = torch.zeros(1, dtype=torch.float64, device='cuda')
        k.vorlage = {'welle_m': 0.01, 'wellenlaenge_m': 0.1, 'locke': 0.0, 'wellig': 0.0}
        quer, aussen = k._locke(bogen, bogen[:, -1], phase, s)
        self.assertAlmostEqual(float(quer.max()), 0.01, places=4)
        self.assertLess(float(aussen.abs().max()), 1e-12)
        self.assertLess(float(quer[0, 100].abs()), 1e-9)                                      # eine volle Welle auf 10 cm
        k.vorlage = dict(k.vorlage, locke=1.0)
        self.assertAlmostEqual(float(k._locke(bogen, bogen[:, -1], phase, s)[1].max()), 0.01, places=4)

    def test_10_bartbereiche(self):
        from haar_Bart.eigenbart import Eigenbart
        p = torch.tensor([[-0.02, 1.55, 0.10], [0.02, 1.55, 0.10],                         # Mund (Breite 4 cm)
                          [0.00, 1.57, 0.10], [0.00, 1.51, 0.09], [0.06, 1.53, 0.06],       # über dem Mund, unter dem Mund, seitlich
                          [0.07, 1.60, 0.00], [0.00, 1.45, 0.04], [0.00, 1.50, 0.08]],      # hinten oben (Kotelette), Hals, Kinn unten
                         dtype=torch.float64, device='cuda')
        mund = torch.tensor([True, True] + [False] * 6, device='cuda')
        hals = torch.tensor([False] * 6 + [True, False], device='cuda')
        bereich, mass, _mitte = Eigenbart.bereiche(p, ~mund, mund, hals)
        self.assertEqual(bereich[2:].tolist(), [0, 1, 2, 3, 4, 1])
        self.assertAlmostEqual(float(mass[7]), 1.0, places=9)                              # Kinn ganz unten = Rand des Bereichs
        self.assertLess(float(mass[3]), 1.0)

    def test_11_dichte_straehnen(self):
        from haar_Bart.eigenhaar import Eigenhaar
        from haar_Bart.haarbueschel import Haarbueschel
        b = Haarbueschel(0.04, zusammenhalt=0.0)
        self.assertEqual(b.zahl(10 ** 6, 4 * Haarbueschel.FLAECHE_JE_D2 * 16.0), 4)              # 4 Flächen à FLAECHE_JE_D2 · d² (d = 4 cm → 16 cm²)
        self.assertEqual(b.zahl(16, 1e4), 2)                                                      # je Strähne mindestens MIN_HAARE Haare
        z = torch.Generator(device='cuda').manual_seed(1)
        q, h = b.plaetze(20000, lambda n: torch.rand(n, generator=z, device='cuda', dtype=torch.float64))
        self.assertLessEqual(float(q.abs().max()), 0.02 + 1e-12)                                  # Breite = Durchmesser
        self.assertGreaterEqual(float(h.min()), -1e-12)                                           # über der Leitsträhne, nie darin
        self.assertLessEqual(float(h.max()), Haarbueschel.FLACH * 0.04 + 1e-12)
        self.assertGreater(float(q.abs().max()), 0.019)                                           # füllt den Querschnitt aus
        s = torch.tensor([[0.0, Haarbueschel.SAMMELN, 1.0]], dtype=torch.float64, device='cuda')
        quer, hoch = b.verlauf(torch.tensor([0.03], dtype=torch.float64, device='cuda'), q[:1], h[:1], s)
        self.assertAlmostEqual(float(quer[0, 0]), 0.03, places=12)                               # an der Wurzel der eigene Versatz
        self.assertAlmostEqual(float(quer[0, 1]), float(q[0]) * (1 - (1 - Haarbueschel.SPITZE) * Haarbueschel.SAMMELN ** 2), places=12)
        self.assertAlmostEqual(float(hoch[0, 2]), float(h[0]) * Haarbueschel.SPITZE, places=12)  # Spitze schmaler
        w = Eigenhaar.werte({'straehne_cm': 9.0})                                               # Regler „Strähnendicke“ bis 5 cm
        self.assertEqual(w['straehne_cm'], 5.0)
        self.assertAlmostEqual(Eigenhaar.vorlage(w)['straehne_m'], 0.05)

    def test_12_rezept_mischen_aufsetzen(self):
        from unittest import mock

        from haar_Bart.haarrezept import Haarrezept
        f64 = torch.float64
        stufen = torch.tensor([0.0, -0.1, -0.2], dtype=f64, device='cuda')
        kurve_a = torch.zeros((3, 3, 3), dtype=f64, device='cuda')
        kurve_a[:, :, 1] = stufen                                                               # A: senkrecht 20 cm
        kurve_b = torch.zeros((3, 3, 3), dtype=f64, device='cuda')
        kurve_b[:, :, 2] = stufen                                                               # B: nach hinten 20 cm
        a = Haarrezept(torch.tensor([True, True, False], device='cuda'), kurve_a, 0.01, 0.0, 'a')
        b = Haarrezept(torch.tensor([True, False, True], device='cuda'), kurve_b, 0.03, 0.1, 'b')
        m = Haarrezept.mischen([(a, 1.0), (b, 1.0)])
        self.assertEqual(m.maske.tolist(), [True, True, True])                                  # je Punkt einer von beiden = Anteil 0,5 ≥ MISCH_MASKE
        self.assertAlmostEqual(float(m.kurve[0, 2, 1]), -0.1, places=12)                         # Punkt 0: Mittel beider
        self.assertAlmostEqual(float(m.kurve[0, 2, 2]), -0.1, places=12)
        self.assertAlmostEqual(float(m.kurve[1, 2, 1]), -0.2, places=12)                         # Punkt 1: nur A behaart → A
        self.assertAlmostEqual(m.dicke_m, 0.02, places=12)
        nur_a = Haarrezept.mischen([(a, 0.8), (b, 0.2)])
        self.assertEqual(nur_a.maske.tolist(), [True, True, False])                             # Punkt 2: nur B mit 0,2 < 0,5
        basis = torch.tensor([[0.0, 1.70, 0.0], [0.05, 1.65, 0.0], [-0.05, 1.65, 0.0]], dtype=f64, device='cuda')   # Kopfhöhe 5 cm
        kaefig = torch.zeros((5, 3), dtype=f64, device='cuda')
        kaefig[[1, 2, 4]] = torch.tensor([[0.0, 1.80, 0.0], [0.05, 1.70, 0.0], [-0.05, 1.70, 0.0]], dtype=f64, device='cuda')   # Kopfhöhe 10 cm → × 2
        with mock.patch.object(Haarrezept, '_kopf', (torch.tensor([1, 2, 4], device='cuda'), basis)):
            feld = a.feld(kaefig)
        self.assertEqual(len(feld.p), 2)                                                        # zwei behaarte Punkte
        self.assertAlmostEqual(float(feld.l[0]), 0.4, places=12)                                 # 20 cm × Kopfmaß 2
        self.assertAlmostEqual(float(feld.fall[1][0, 1]), -1.0, places=12)                       # Fallfeld abwärts

    def test_13_restlaenge_und_ende(self):
        """Länge = Rest der Vorlagesträhne über der Wurzel + Abstand (`Haarkaemmfeld.abfragen` mit Fallfeld); „ende“ (`Haarvergleich`) 0 für gleiche Linien, Verkürzung in cm.
        Sabotage: in `abfragen` `self.rest[…]` durch `self.l[j]` ersetzen → Länge 0,2 statt 0,105; in `_ende` `ENDE_RANG` auf 0,5 → Verkürzung nicht mehr 5 cm."""
        from haar_Bart.haarkaemmfeld import Haarkaemmfeld
        from haar_Bart.haarvergleich import Haarvergleich
        f64 = torch.float64
        t = torch.linspace(0, 1, 21, dtype=f64, device='cuda')
        linie = torch.stack([torch.zeros_like(t), 1.70 - 0.20 * t, torch.zeros_like(t)], 1)[None]          # 20 cm senkrecht abwärts
        f = Haarkaemmfeld.aus_linien(linie, linie[0, :1], fall=True)
        wurzel = torch.tensor([[0.005, 1.60, 0.0]], dtype=f64, device='cuda')                              # neben der Mitte der Strähne
        _r, _k, laenge = f.abfragen(wurzel, torch.tensor([[1.0, 0.0, 0.0]], dtype=f64, device='cuda'))
        self.assertAlmostEqual(float(laenge[0]), 0.105, places=9)                                          # 10 cm Rest + 5 mm Abstand
        winkel = torch.linspace(0, 2 * math.pi, 64, dtype=f64, device='cuda')[:-1]
        ring = torch.stack([0.1 * torch.sin(winkel), torch.full_like(winkel, 1.70), 0.1 * torch.cos(winkel)], 1)
        vorlage = ring[:, None] + torch.stack([torch.zeros_like(t), -0.20 * t, torch.zeros_like(t)], 1)[None]   # 63 Strähnen rundum, 20 cm
        gleich = Haarvergleich.vergleichen(vorlage, torch.ones(len(vorlage), dtype=f64, device='cuda'), vorlage)
        self.assertEqual(gleich['ende_cm'], 0.0)
        kurz = Haarvergleich.vergleichen(vorlage, torch.ones(len(vorlage), dtype=f64, device='cuda'), vorlage[:, :16])   # nur bis 15 cm
        self.assertAlmostEqual(kurz['ende_hoeher_cm'], 5.0, delta=0.6)
        self.assertIn('ende', kurz['rot'])

    def test_14_restkurven(self):
        """`Haarrezept.restkurven`: je Stelle der Rest bis zur Spitze auf gleich lange Stücke, Versatz zur Stelle. Sabotage: `ziel` ohne `b[:, :, None] +` → Rest ab der Wurzel."""
        from haar_Bart.haarrezept import Haarrezept
        t = torch.linspace(0, 1, 5, dtype=torch.float64, device='cuda')
        r = Haarrezept.restkurven(torch.stack([torch.zeros_like(t), -0.2 * t, torch.zeros_like(t)], 1)[None])
        self.assertEqual(tuple(r.shape), (5, 5, 3))
        for i, rest in ((0, 0.2), (2, 0.1), (4, 0.0)):
            self.assertAlmostEqual(float(r[i, -1, 1]), -rest, places=12)
            self.assertAlmostEqual(float(r[i, 2, 1]), -rest / 2, places=12)

    def test_15_anschmiegen(self):
        """`Haarbueschel.anschmiegen` (17.11.2026): Versatz wächst je Schritt höchstens um STEIGUNG × Schrittlänge, ein Schritt der Länge 0 hält ihn, kleine Änderungen bleiben.
        Sabotage: `self.STEIGUNG * schritt[:, k - 1]` durch `1e9 * schritt[:, k - 1]` ersetzen → rot."""
        from haar_Bart.haarbueschel import Haarbueschel
        f64 = torch.float64
        b = Haarbueschel(0.012)
        quer = torch.tensor([[0.0, 0.01, 0.01, 0.01], [0.0, 0.0, 0.0001, 0.0002]], dtype=f64, device='cuda')    # Haar 0: 1 cm Sprung, Haar 1: 0,1 mm je Schritt
        hoch = torch.zeros_like(quer)
        schritt = torch.tensor([[0.0, 0.01, 0.01], [0.01, 0.01, 0.01]], dtype=f64, device='cuda')               # Haar 0: erster Schritt Wurzel → Schale (Länge 0)
        q, h = b.anschmiegen(quer, hoch, schritt)
        self.assertEqual(float(q[0, 1]), 0.0)                                                     # Länge 0 hält den Versatz
        self.assertAlmostEqual(float(q[0, 2]), Haarbueschel.STEIGUNG * 0.01, places=12)           # höchstens STEIGUNG × 1 cm
        self.assertAlmostEqual(float(q[0, 3]), 0.01 if 2 * Haarbueschel.STEIGUNG >= 1 else 2 * Haarbueschel.STEIGUNG * 0.01, places=12)
        self.assertTrue(torch.equal(q[1], quer[1]))                                               # flache Änderung bleibt unverändert
        self.assertEqual(float(h.abs().max()), 0.0)

    def test_16_rezept_einscheren(self):
        """`Haarrezept.aus_linien` Fassung 3/4: die Kurve beginnt am Kopfhautpunkt und endet an der Spitze der Strähne (nicht um den Abstand Punkt → Strähnenstelle versetzt);
        ein Punkt unter der Spitze (nur in 4 cm Nähe) ist nicht behaart; `Haarkaemmfeld` mit `behaart_m` gibt fern der Stützstellen die Länge 0.
        Sabotage: `+ (stellen[jj] - kopf_p[:, None])[:, :, None] * r[..., None]` weg → Ende 1 cm daneben → rot; Zeile `hat = hat & (behaart | …)` weg → Punkt 2 behaart → rot;
        in `Haarkaemmfeld.abfragen` die `behaart_m`-Zeile weg → Länge 0,2 statt 0 → rot."""
        from haar_Bart.haarrezept import Haarrezept
        from haar_Bart.haarvorlagelinien import Haarvorlagelinien
        f64 = torch.float64
        t = torch.linspace(0, 1, 21, dtype=f64, device='cuda')
        linie = torch.stack([torch.zeros_like(t), 1.70 - 0.20 * t, torch.zeros_like(t)], 1)[None]       # 20 cm senkrecht, Spitze bei y = 1,50
        punkt = torch.tensor([[0.01, 1.60, 0.0], [0.01, 1.48, 0.0]], dtype=f64, device='cuda')            # 1 cm neben der Mitte; 2 cm unter der Spitze
        r = Haarrezept.aus_linien(linie, torch.ones(1, dtype=f64, device='cuda'), punkt, 0.012, 0.0)
        self.assertTrue(bool(r.maske[0]))
        self.assertFalse(bool(r.maske[1]))                                                                 # Fassung 4: kein Haar, wo es nicht über den Punkt hängt
        self.assertEqual(float(r.kurve[0, 0].abs().max()), 0.0)                                            # beginnt am Punkt
        ende = (punkt[0] + r.kurve[0, -1]).tolist()
        for ist, soll in zip(ende, (0.0, 1.50, 0.0), strict=True):
            self.assertAlmostEqual(ist, soll, places=9)                                                    # endet an der Spitze der Strähne
        self.assertGreaterEqual(float(Haarvorlagelinien.laengen(r.kurve[:1])[0]), (0.01 ** 2 + 0.1 ** 2) ** 0.5 - 1e-9)
        from haar_Bart.haarkaemmfeld import Haarkaemmfeld
        unten = torch.tensor([[0.0, -1.0, 0.0]], dtype=f64, device='cuda')
        feld = Haarkaemmfeld(punkt[:1], unten, torch.zeros(1, dtype=f64, device='cuda'), torch.tensor([0.2], dtype=f64, device='cuda'), behaart_m=0.015)
        wurzeln = torch.tensor([[0.015, 1.60, 0.0], [0.10, 1.60, 0.0]], dtype=f64, device='cuda')        # 5 mm bzw. 9 cm von der Stützstelle
        laenge = feld.abfragen(wurzeln, torch.tensor([[1.0, 0.0, 0.0]] * 2, dtype=f64, device='cuda'))[2]
        self.assertEqual(laenge.tolist(), [0.2, 0.0])

    def test_17_stueck_ohne_farbbild(self):
        """`Eigenfarben.stueck` (17.11.2026): erstes Material MIT Bild; ohne Farbbild ein einfarbiges 4×4-Bild aus der linearen Materialfarbe in sRGB. Schreibt nur in einen
        eigenen Ordner unter `ProjektTemp/` und löscht ihn. Sabotage: `next(…)` durch `mats[0]` ersetzen → Fall 2 wirft (`Path / None`)."""
        import json
        import os
        import shutil
        from pathlib import Path

        from meshgenesis_eigenfarben import Eigenfarben
        from PIL import Image
        ordner = Path(r'A:\3DTools\ProjektTemp') / ('_test_eigenfarben_%d' % os.getpid()) / 'anzeige'
        try:
            (ordner / 'bilder').mkdir(parents=True)
            torch.save({'ruhe': torch.zeros((3, 3), device='cuda'), 'dreiecke': torch.tensor([[0, 1, 2]], device='cuda'),
                        'uv': torch.zeros((3, 2), device='cuda')}, ordner / 'netz.pt')
            (ordner / 'materialien.json').write_text(json.dumps([{'name': 'a', 'bild': None, 'farbe': [0.25, 0.25, 0.25]}]), encoding='utf-8')
            bild = Eigenfarben.stueck(ordner)[3]                                                           # Fall 1: kein Bild → Materialfarbe
            self.assertEqual(tuple(bild.shape), (3, 4, 4))
            self.assertEqual(int(bild[0, 0, 0]), 137)                                                      # linear 0,25 → sRGB 136,96 → 137
            Image.new('RGB', (2, 2), (10, 20, 30)).save(ordner / 'bilder' / 'm1.png')
            (ordner / 'materialien.json').write_text(json.dumps([{'name': 'a', 'bild': None, 'farbe': [0.0, 0.0, 0.0]},
                                                                  {'name': 'b', 'bild': 'm1.png', 'farbe': [1.0, 1.0, 1.0]}]), encoding='utf-8')
            bild = Eigenfarben.stueck(ordner)[3]                                                           # Fall 2: erstes Material ohne, zweites mit Bild
            self.assertEqual(tuple(bild.shape), (3, 2, 2))
            self.assertEqual(bild[:, 0, 0].tolist(), [10, 20, 30])
        finally:
            shutil.rmtree(ordner.parent, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
