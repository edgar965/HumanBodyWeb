"""Haarrezept, Kurvengang und Messung des Haarnachbaus (17.11.2026): kleine Kunstfälle auf der Karte, keine echten Netze. Nur auf Ansage laufen lassen
(`testsuite-nur-auf-ansage`). Fortsetzung von `test_eigenhaar.py` (test_1–17).

  test_18 `Haarkurvengang.umlegen`: Punkte gleicher Bogenlänge, Anfang und Ende bleiben
  test_19 Bänder breiter Karten (`Haarvorlagelinien._karten`, `BAND_M`): Karte 4,5 cm × 20 cm → 3 Linien quer verteilt, Gewicht zusammen = Fläche; ohne Bänder 1 Linie
  test_20 Büschellinien nach Schritt (`Haarnachbau.eigen_linien`): verschieden lang gezeigte Haare eines Büschels → eine gerade, vorwärts laufende Linie
  test_21 `Haarrezept.uebertragen`: auf der Grundfigur unverändert; Käfig um 1 cm gehoben → Punkte um 1 cm gehoben
  test_22 `Haarkurvengang.waehlen`: längste gleichgerichtete Kurve in halber Strähnendicke, ohne Dicke die nächste
  test_23 `Haarwurzeldichte.je_punkt`: dicht bewurzelt 1, dünn unter 0,4, nicht über Füße behaart 1
  test_24 `Haarkurvengang.wuerfel`: fest nach der Lage, gleichverteilt in [0, 1)
  test_25 `Haarrezept.aus_linien`: „hängt“ ohne Fuß in der Nähe (Fehler Rezept F7)
  test_26 `Haarrezept.aus_linien`: am Fußpunkt die dort wurzelnde Strähne, nicht die darüber laufende (Rezept F9)
  test_27 `Haarrezeptleit.ordnen`: Leitwurzeln je Stützstelle, der übrige Anteil wie bisher, Wurzeln an Stützstellen außerhalb des Ansatzes
  test_28 `Haarwurzeldichte.haengend`: hängende Punkte unter nur einer Strähne dünn, übrige unverändert, Schalter aus → unverändert
  test_29 `Haarrezeptlagen.zweite`: zweite Lage nur unter Kandidaten mit anderer Spitze und genug Gewicht
  test_30 `Haarrezeptlagen.zusatz`: Zusatzkurve für eine offene Spitze; `Haarrezeptleit` setzt Wurzeln an feste Stützstellen
Sabotage: test_18 `- 1` hinter `searchsorted` weg → Abstände ungleich; test_19 `baender` immer 1 → eine Linie; test_20 `leit % spalten` durch die alte Stelle aus UV v
ersetzen → Linie läuft zurück; test_21 `schub` mit Vorzeichen − → Punkte sinken.
"""
import sys
import unittest

import torch

for _pfad in (r'A:\3DTools', r'A:\3DTools\meshgenesis'):
    if _pfad not in sys.path:
        sys.path.append(_pfad)

KARTE = torch.cuda.is_available()
f64 = torch.float64


@unittest.skipUnless(KARTE, 'braucht CUDA')
class HaarrezeptKurvenTest(unittest.TestCase):
    databases = []

    def test_18_umlegen(self):
        from haar_Bart.haarkurvengang import Haarkurvengang
        k = torch.tensor([[[0.0, 0.0, 0.0], [0.01, 0.0, 0.0], [0.04, 0.0, 0.0], [0.04, -0.06, 0.0]]], dtype=f64, device='cuda')   # Bogen 1 + 3 + 6 cm
        u = Haarkurvengang.umlegen(k, 10)
        schritt = (u[0, 1:] - u[0, :-1]).norm(dim=1)
        self.assertEqual(tuple(u.shape), (1, 11, 3))
        self.assertLess(float((schritt - 0.01).abs().max()), 1e-9)
        self.assertEqual(u[0, 0].tolist(), [0.0, 0.0, 0.0])
        self.assertLess(float((u[0, -1] - k[0, -1]).norm()), 1e-12)

    def test_19_baender(self):
        from haar_Bart.haarvorlagelinien import Haarvorlagelinien
        nx, ny = 10, 41                                                                                    # 4,5 cm quer (x), 20 cm längs (y)
        x = torch.linspace(-0.0225, 0.0225, nx, dtype=f64, device='cuda')
        y = torch.linspace(1.6, 1.4, ny, dtype=f64, device='cuda')
        gy, gx = torch.meshgrid(y, x, indexing='ij')
        p = torch.stack([gx, gy, torch.zeros_like(gx)], -1).reshape(-1, 3)
        uv = torch.stack([(gx - gx.min()) / 0.045, (gy - 1.4) / 0.2], -1).reshape(-1, 2)
        i = torch.arange(ny - 1, device='cuda')[:, None] * nx + torch.arange(nx - 1, device='cuda')[None]
        i = i.reshape(-1)
        d = torch.cat([torch.stack([i, i + 1, i + nx], 1), torch.stack([i + 1, i + nx + 1, i + nx], 1)])
        alt = Haarvorlagelinien.BAND_M
        try:
            Haarvorlagelinien.BAND_M = 0.015
            li, gw, br = Haarvorlagelinien._karten(p, d, uv)
            self.assertEqual(len(li), 3)
            self.assertAlmostEqual(float(br[0]), 0.045, places=6)                                           # Kartenbreite quer
            self.assertAlmostEqual(float(gw.sum()), 0.045 * 0.2, places=9)
            mitte_x = sorted(li[:, :, 0].mean(1).tolist())
            self.assertLess(mitte_x[0], -0.01)
            self.assertGreater(mitte_x[2], 0.01)
            self.assertAlmostEqual(mitte_x[1], 0.0, places=6)
            self.assertGreater(float(li[0, 0, 1]), float(li[0, -1, 1]))                                     # Wurzel oben
            Haarvorlagelinien.BAND_M = None
            self.assertEqual(len(Haarvorlagelinien._karten(p, d, uv)[0]), 1)
        finally:
            Haarvorlagelinien.BAND_M = alt

    def test_20_eigen_linien_nach_schritt(self):
        from haar_Bart.haarnachbau import Haarnachbau
        spalten = 9
        punkte, leit, uv = [], [], []
        for zeige in (8, 3, 5):                                                                           # drei Haare eines Büschels, verschieden lang gezeigt
            for kk in range(zeige + 1):
                for seite in (-0.001, 0.001):                                                              # zwei Punkte je Schritt (Band links, rechts)
                    punkte.append([seite, 1.6 - 0.01 * kk, 0.0])
                    leit.append(kk)
                    uv.append([0.0, 1.0 - 0.999 * kk / zeige])
        netz = {'ruhe': torch.tensor(punkte, dtype=torch.float32, device='cuda'), 'leit': torch.tensor(leit, device='cuda'),
                'uv': torch.tensor(uv, dtype=torch.float32, device='cuda'), 'leitpunkte': torch.zeros((1, spalten, 3), device='cuda')}
        e = Haarnachbau.eigen_linien(netz)
        self.assertEqual(len(e), 1)
        seg = e[0, 1:] - e[0, :-1]
        self.assertTrue(bool((seg[:, 1] < 0).all()))                                                      # läuft nur abwärts, nie zurück
        self.assertAlmostEqual(float(e[0, 0, 1]), 1.6, places=5)
        self.assertAlmostEqual(float(e[0, -1, 1]), 1.6 - 0.08, places=5)

    def test_22_kurve_waehlen(self):
        """`Haarkurvengang.waehlen`: in halber Strähnendicke die längste gleichgerichtete Kurve, die gegenläufige nicht, die ferne nicht; ohne Dicke die nächste. Sabotage:
        `argmax` → `argmin` → die kurze."""
        from haar_Bart.haarkaemmfeld import Haarkaemmfeld
        from haar_Bart.haarkurvengang import Haarkurvengang
        from haar_Bart.haarvorlagelinien import Haarvorlagelinien
        p = torch.tensor([[0.0, 1.6, 0.0], [0.004, 1.6, 0.0], [0.003, 1.6, 0.0], [0.05, 1.6, 0.0]], dtype=f64, device='cuda')
        ab = torch.linspace(0.0, 1.0, 5, dtype=f64, device='cuda')[:, None] * torch.tensor([0.0, -1.0, 0.0], dtype=f64, device='cuda')
        kurven = torch.stack([0.05 * ab, 0.20 * ab, -0.30 * ab, 0.40 * ab])        # kurz, lang, lang aber aufwärts, am längsten aber 5 cm weg
        null = torch.zeros(4, dtype=f64, device='cuda')
        feld = Haarkaemmfeld(p, kurven[:, 1], null, Haarvorlagelinien.laengen(kurven), kurven=kurven, dicke_m=0.012)
        g = Haarkurvengang.__new__(Haarkurvengang)
        wurzel = torch.tensor([[0.0005, 1.6, 0.0]], dtype=f64, device='cuda')
        self.assertEqual(int(g.waehlen(wurzel, feld)[0]), 1)
        feld.dicke_m = None
        self.assertEqual(int(g.waehlen(wurzel, feld)[0]), 0)

    def test_21_uebertragen(self):
        try:
            from Genesis9.basisnetz import G9basisnetz
            grund = torch.as_tensor(G9basisnetz.holen().punkte, device='cuda').double()
        except Exception as fehler:  # noqa: BLE001 — ohne Daz-Bibliothek kein Grundnetz
            self.skipTest('kein Genesis-9-Grundnetz: %s' % fehler)
        from haar_Bart.haarrezept import Haarrezept
        q = grund[:50] + torch.tensor([0.0, 0.0, 0.02], dtype=f64, device='cuda')                        # 2 cm vor dem Körper
        self.assertLess(float((Haarrezept.uebertragen(q, grund) - q).abs().max()), 1e-12)
        hoch = torch.tensor([0.0, 0.01, 0.0], dtype=f64, device='cuda')
        self.assertLess(float((Haarrezept.uebertragen(q, grund + hoch) - (q + hoch)).abs().max()), 1e-9)

    def test_23_wurzeldichte(self):
        """`Haarwurzeldichte.je_punkt`: 20 Punkte im Abstand 3 mm, die erste Hälfte dicht bewurzelt (Gewicht 1 je Punkt), die zweite dünn (0,05) → vorn 1, hinten unter 0,4;
        ein nicht über Füße behaarter Punkt 1. Sabotage: `/ (ANTEIL * bezug)` weg → hinten über 0,4 nicht mehr sicher, vorn nicht 1."""
        from haar_Bart.haarwurzeldichte import Haarwurzeldichte
        kopf = torch.zeros((20, 3), dtype=f64, device='cuda')
        kopf[:, 0] = 0.003 * torch.arange(20, dtype=f64, device='cuda')
        fuss = torch.arange(20, device='cuda')
        gewicht = torch.where(fuss < 10, 1.0, 0.05).double()
        behaart = torch.ones(20, dtype=torch.bool, device='cuda')
        behaart[19] = False
        d = Haarwurzeldichte.je_punkt(fuss, gewicht, kopf, behaart)
        self.assertEqual(d[:5].tolist(), [1.0] * 5)
        self.assertLess(float(d[14:19].max()), 0.4)
        self.assertEqual(float(d[19]), 1.0)

    def test_24_wuerfel(self):
        """`Haarkurvengang.wuerfel`: gleiche Lage, gleiche Zahl; Werte in [0, 1), gleichverteilt (Mittel 0,45–0,55, Anteil unter 0,3 zwischen 0,25 und 0,35)."""
        from haar_Bart.haarkurvengang import Haarkurvengang
        g = torch.Generator(device='cuda').manual_seed(3)
        p = 0.1 * torch.rand((20000, 3), generator=g, dtype=f64, device='cuda') + torch.tensor([0.0, 1.5, 0.0], dtype=f64, device='cuda')
        w = Haarkurvengang.wuerfel(p)
        self.assertTrue(torch.equal(w, Haarkurvengang.wuerfel(p.clone())))
        self.assertGreaterEqual(float(w.min()), 0.0)
        self.assertLess(float(w.max()), 1.0)
        self.assertTrue(0.45 < float(w.mean()) < 0.55)
        self.assertTrue(0.25 < float((w < 0.3).double().mean()) < 0.35)

    def test_25_haengt_ohne_fuss(self):
        """`Haarrezept.aus_linien`: eine Strähne 15 cm lang, 5 mm über einer ebenen Kopfhaut (10 cm hoch) — der Punkt 10 cm unter der Wurzel liegt über 15 mm vom nächsten Fuß
        (erstes Drittel bis ~5 cm), aber unter der Strähne, die tiefer endet: behaart („hängt“), Dichte 1. Rezept F7 prüfte für „hängt“ den Abstand zum nächsten Fuß (Name `d`
        überschrieben) — dort nicht behaart. Sabotage: `torch.isfinite(d[:, 0])` durch den Fußabstand ersetzen → rot."""
        from haar_Bart.haarrezept import Haarrezept
        x, y = torch.meshgrid(torch.linspace(-0.01, 0.01, 5, dtype=f64, device='cuda'), -0.005 * torch.arange(25, dtype=f64, device='cuda'), indexing='ij')
        kopf = torch.stack([x.reshape(-1), y.reshape(-1), torch.zeros(125, dtype=f64, device='cuda')], 1)
        t = torch.linspace(0.0, 1.0, 17, dtype=f64, device='cuda')
        linie = torch.stack([torch.zeros_like(t), -0.15 * t, torch.full_like(t, 0.005)], 1)[None]
        r = Haarrezept.aus_linien(linie, torch.ones(1, dtype=f64, device='cuda'), kopf, 0.01, 0.0)
        i = int(((kopf - torch.tensor([0.0, -0.10, 0.0], dtype=f64, device='cuda')).norm(dim=1)).argmin())
        self.assertTrue(bool(r.maske[i]))
        self.assertEqual(float(r.dichte[i]), 1.0)

    def test_26_wurzelwahl(self):
        """`Haarrezept.aus_linien` (Fassung 9): am Punkt 6 cm unter dem Scheitel wurzelt Strähne A (30 cm, 4 mm über der Haut); B wurzelt oben und läuft 2 mm über ihn hinweg
        bis 8 cm. Die nächste Stelle ist die von B — die Kurve des Punkts ist trotzdem A (Ende ~30 cm tiefer), weil er ein Fußpunkt von A ist. Sabotage: die Zeile mit
        `bis=p // 3 + 1` weg → Ende 2 cm tiefer (B)."""
        from haar_Bart.haarrezept import Haarrezept
        x, y = torch.meshgrid(torch.linspace(-0.01, 0.01, 5, dtype=f64, device='cuda'), -0.005 * torch.arange(25, dtype=f64, device='cuda'), indexing='ij')
        kopf = torch.stack([x.reshape(-1), y.reshape(-1), torch.zeros(125, dtype=f64, device='cuda')], 1)
        t = torch.linspace(0.0, 1.0, 17, dtype=f64, device='cuda')
        a = torch.stack([torch.zeros_like(t), -0.06 - 0.30 * t, torch.full_like(t, 0.004)], 1)
        b = torch.stack([torch.zeros_like(t), -0.08 * t, torch.full_like(t, 0.002)], 1)
        r = Haarrezept.aus_linien(torch.stack([a, b]), torch.ones(2, dtype=f64, device='cuda'), kopf, 0.01, 0.0)
        i = int(((kopf - torch.tensor([0.0, -0.06, 0.0], dtype=f64, device='cuda')).norm(dim=1)).argmin())
        self.assertTrue(bool(r.maske[i]))
        self.assertLess(float(r.kurve[i, -1, 1]), -0.2)

    def test_27_rezeptleit(self):
        """`Haarrezeptleit.ordnen`: 1000 gewürfelte Wurzeln auf 10 × 10 cm, 50 Stützstellen in der linken Hälfte und 3 weit draußen (keine Wurzel bis `behaart_m`), 100
        Leitwurzeln nach der Dicke → je Stützstelle mindestens eine Leitwurzel nahe dran, der übrige Anteil weiter weg wie bisher (75), die 3 äußeren bekommen je
        `MIN_HAARE` Wurzeln genau an ihrer Stelle, die erste davon unter den Leitwurzeln. Sabotage: `max(len(kaemm.p), …)` → nur der Anteil (25) → rot."""
        from types import SimpleNamespace

        from haar_Bart.haarbueschel import Haarbueschel
        from haar_Bart.haarrezeptleit import Haarrezeptleit
        g = torch.Generator(device='cuda').manual_seed(5)
        w = torch.cat([0.1 * torch.rand((1000, 2), generator=g, dtype=f64, device='cuda') - 0.05, torch.zeros((1000, 1), dtype=f64, device='cuda')], 1)
        gx, gy = torch.meshgrid(torch.linspace(-0.045, -0.005, 5, dtype=f64, device='cuda'), torch.linspace(-0.045, 0.045, 10, dtype=f64, device='cuda'), indexing='ij')
        innen = torch.stack([gx.reshape(-1), gy.reshape(-1), torch.zeros(50, dtype=f64, device='cuda')], 1)
        aussen = torch.tensor([[0.5, 0.0, 0.0], [0.5, 0.1, 0.0], [0.5, 0.2, 0.0]], dtype=f64, device='cuda')
        feld = SimpleNamespace(p=torch.cat([innen, aussen]), behaart_m=0.004)
        neu, gl = Haarrezeptleit.ordnen(w, 100, feld)
        self.assertEqual(len(neu), 1000 + 3 * Haarbueschel.MIN_HAARE)
        self.assertTrue(torch.equal(neu[gl - 3:gl], aussen))
        d = torch.cdist(neu[:gl - 3], innen).min(1).values
        self.assertGreaterEqual(int((d <= 0.004).sum()), 50)
        self.assertEqual(int((d > 0.004).sum()), 75)

    def test_28_haengend(self):
        """`Haarwurzeldichte.haengend` (Rezept Fassung 10): zehn Strähnen bis 6 cm unter dem Scheitel und eine bis 12 cm, 3 mm über einer ebenen Kopfhaut; Fußpunkte oben
        (bis 4 cm), hängend die Punkte unter 8 cm — dort läuft nur eine Strähne → Dichte unter 0,5; die übrigen Punkte behalten ihre Dichte; mit `HAENGT` aus unverändert.
        Sabotage: `torch.where(haengt, …)` durch die Rohmenge ohne Bezug ersetzen → rot."""
        from haar_Bart.haarwurzeldichte import Haarwurzeldichte
        x, y = torch.meshgrid(torch.linspace(-0.01, 0.01, 5, dtype=f64, device='cuda'), -0.005 * torch.arange(25, dtype=f64, device='cuda'), indexing='ij')
        kopf = torch.stack([x.reshape(-1), y.reshape(-1), torch.zeros(125, dtype=f64, device='cuda')], 1)
        t = torch.linspace(0.0, 1.0, 17, dtype=f64, device='cuda')
        kurz = torch.stack([torch.zeros_like(t), -0.06 * t, torch.full_like(t, 0.003)], 1)
        lang = torch.stack([torch.zeros_like(t), -0.12 * t, torch.full_like(t, 0.003)], 1)
        li = torch.stack([kurz] * 10 + [lang])
        fuss, haengt = kopf[:, 1] > -0.04, kopf[:, 1] < -0.08
        ein = torch.full((125,), 0.7, dtype=f64, device='cuda')
        d = Haarwurzeldichte.haengend(ein, li, torch.ones(11, dtype=f64, device='cuda'), kopf, fuss, haengt, 0.015)
        self.assertLess(float(d[haengt].max()), 0.5)
        self.assertTrue(torch.equal(d[~haengt], ein[~haengt]))
        alt = Haarwurzeldichte.HAENGT
        try:
            Haarwurzeldichte.HAENGT = False
            self.assertTrue(torch.equal(Haarwurzeldichte.haengend(ein, li, torch.ones(11, dtype=f64, device='cuda'), kopf, fuss, haengt, 0.015), ein))
        finally:
            Haarwurzeldichte.HAENGT = alt

    def test_29_zweite_lage(self):
        """`Haarrezeptlagen.zweite` (Rezept Fassung 11): Punkt 0 hat drei Kandidaten, zwei mit derselben Spitze, einer 10 cm daneben (Gewicht 0,4 von 1,9) → Kandidat der
        zweiten Lage ist dieser; Punkt 1 nur gleiche Spitzen → nie eine. Feste Schwelle (`ANTEILIG` aus): ab `LAGE_ANTEIL` 0,1 ja, 0,3 nein; anteilig: von 2000 Punkten
        wie Punkt 0 bekommen 21 % ± 3 % eine. Sabotage: `> cls.LAGE_M` → `>= 0` → Punkt 1 bekommt eine."""
        from haar_Bart.haarrezeptlagen import Haarrezeptlagen as L
        w = torch.tensor([[1.0, 0.5, 0.4], [1.0, 0.5, 0.4]], dtype=f64, device='cuda')
        s = torch.tensor([[[0.0, -0.3, 0.0], [0.0, -0.3, 0.01], [0.1, -0.3, 0.0]], [[0.0, -0.3, 0.0], [0.0, -0.3, 0.01], [0.01, -0.3, 0.0]]], dtype=f64, device='cuda')
        kopf = torch.tensor([[0.0, 0.0, 0.0], [0.01, 0.0, 0.0]], dtype=f64, device='cuda')
        viele = 0.2 * torch.rand((2000, 3), generator=torch.Generator(device='cuda').manual_seed(3), dtype=f64, device='cuda')
        alt = (L.ANTEILIG, L.LAGE_ANTEIL)
        try:
            L.ANTEILIG = False
            i2, hat = L.zweite(w, s, w.argmax(1), kopf)
            self.assertEqual(hat.tolist(), [True, False])
            self.assertEqual(int(i2[0]), 2)
            L.LAGE_ANTEIL = 0.3
            self.assertEqual(L.zweite(w, s, w.argmax(1), kopf)[1].tolist(), [False, False])
            L.ANTEILIG = True
            for k, soll in ((0, 0.4 / 1.9), (1, 0.0)):
                wk, sk = w[k:k + 1].expand(2000, 3), s[k:k + 1].expand(2000, 3, 3)
                self.assertAlmostEqual(float(L.zweite(wk, sk, wk.argmax(1), viele)[1].double().mean()), soll, delta=0.03)
        finally:
            L.ANTEILIG, L.LAGE_ANTEIL = alt

    def test_30_offene_spitze(self):
        """`Haarrezeptlagen.zusatz`: Strähne A und B wurzeln am Scheitel einer ebenen Kopfhaut, A endet 30 cm darunter, B 10 cm daneben; das Rezept hat nur A → eine
        Zusatzkurve mit der Spitze von B (Dichte 1), Wurzel `VERSATZ_M` neben einem Kopfhautpunkt; mit `AN` aus keine. `Haarrezeptleit.ordnen` setzt an eine feste Stützstelle
        `MIN_HAARE` Wurzeln, obwohl gewürfelte Wurzeln daneben liegen. Sabotage: `>= cls.SPITZE_M` → `< cls.SPITZE_M` → keine Zusatzkurve."""
        from types import SimpleNamespace

        from haar_Bart.haarbueschel import Haarbueschel
        from haar_Bart.haarrezeptlagen import Haarrezeptlagen
        from haar_Bart.haarrezeptleit import Haarrezeptleit
        x, y = torch.meshgrid(torch.linspace(-0.01, 0.01, 5, dtype=f64, device='cuda'), -0.005 * torch.arange(25, dtype=f64, device='cuda'), indexing='ij')
        kopf = torch.stack([x.reshape(-1), y.reshape(-1), torch.zeros(125, dtype=f64, device='cuda')], 1)
        t = torch.linspace(0.0, 1.0, 17, dtype=f64, device='cuda')
        a = torch.stack([torch.zeros_like(t), -0.30 * t, torch.full_like(t, 0.004)], 1)
        b = torch.stack([0.10 * t, -0.30 * t, torch.full_like(t, 0.004)], 1)
        maske = torch.zeros(125, dtype=torch.bool, device='cuda')
        i = int(kopf.norm(dim=1).argmin())
        maske[i] = True
        kurve = torch.zeros((125, 17, 3), dtype=f64, device='cuda')
        kurve[i] = a - kopf[i]
        wz, kz, dz = Haarrezeptlagen.zusatz(torch.stack([a, b]), torch.ones(2, dtype=f64, device='cuda'), kopf, maske, kurve, 0.3)
        self.assertEqual(len(wz), 1)
        self.assertLess(float((wz[0] + kz[0, -1] - b[-1]).norm()), 1e-9)
        self.assertAlmostEqual(float(torch.cdist(wz, kopf).min()), Haarrezeptlagen.VERSATZ_M, places=9)
        self.assertEqual(dz.tolist(), [1.0])
        alt = Haarrezeptlagen.AN
        try:
            Haarrezeptlagen.AN = False
            self.assertEqual(len(Haarrezeptlagen.zusatz(torch.stack([a, b]), torch.ones(2, dtype=f64, device='cuda'), kopf, maske, kurve, 0.3)[0]), 0)
        finally:
            Haarrezeptlagen.AN = alt
        feld = SimpleNamespace(p=kopf[:2], behaart_m=0.004, fest=torch.tensor([False, True], device='cuda'))
        neu, gl = Haarrezeptleit.ordnen(kopf[:2] + 0.001, 2, feld)
        self.assertEqual(int((neu == kopf[1]).all(1).sum()), Haarbueschel.MIN_HAARE)


if __name__ == '__main__':
    unittest.main()
