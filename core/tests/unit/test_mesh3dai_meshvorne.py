# -*- coding: utf-8 -*-
"""„Nicht vor dem Eingang“ in der ersten Zeile (`Mesh3daimeshvorne`, 30.10.2026) an einer Kunstfläche, auf der CPU, ohne Figur, Ziel und Karte.

Figur: Punkte auf z = d (Blick +Z); Hülle des Ziels: die Ebene z = 0, außen bei z > 0. Attrappe für `G9meshinnen` (Suche, Abstand, außen/innen mit nächstem Punkt und Normale, Klasse
des nächsten Dreiecks) — mit Signatur-Wächter gegen die echten Klassen.
    1  `paare`: aktiv ist Haut mehr als `VOR_HAUT_MM` davor und Haar weniger als `INNEN_SONST_MM` innen; Haut 1 mm davor oder dahinter nicht; nicht freie Punkte und `nur` nie
    2  `verlust`: für Haut 6 mm davor (4 mm zu weit) 16 mm², der Gradient zeigt nach innen (−z), erfüllte Punkte ohne Gradient
    3  Abstieg mit `verlust` allein bringt die Haut auf höchstens `VOR_HAUT_MM` davor (+0,05 mm), das Haar auf `INNEN_SONST_MM` innen
    4  `zahlen`: Punkte mit Rest > 0,5 mm und größter Rest
    5  Signaturen der Attrappen = echte Klassen
Sabotage (von Hand): in `_messen` das Soll der Haut auf +1 setzen → Fall 1 rot; in `verlust` das Vorzeichen von s umdrehen → Fall 2 und 3 rot; `nur` in `_frei` übergehen → Fall 1 rot.
"""
import inspect
import sys
import unittest

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))
sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


class Mesh3daimeshvorneTest(unittest.TestCase):
    databases = []
    HAUT, HAAR = 0, 1

    class Flaeche:
        """Attrappe `G9meshflaeche`: je Punkt ein eigenes „Dreieck“, Art 3 (Fläche), Abstand² zur Ebene z = 0."""
        def suchen(self, punkte, ecken):
            import torch
            return torch.arange(len(punkte)), torch.full((len(punkte),), 3)

        def abstaende(self, punkte, ecken, gefunden):
            return punkte[:, 2].pow(2)

    class Innen:
        """Attrappe `G9meshinnen`: Hülle z = 0, außen z > 0, nächster Punkt (x, y, 0), Normale +Z."""
        def __init__(self, klassen):
            import torch
            self.tri_klasse = torch.as_tensor(klassen)
            self.fl = Mesh3daimeshvorneTest.Flaeche()
            self.z = type('Ziel', (), {'p': torch.zeros((1, 3))})()

        def aussen(self, x, gefunden, d_mm):
            import torch
            q = x.clone()
            q[:, 2] = 0.0
            return x[:, 2] > 0, q, torch.tensor([0.0, 0.0, 1.0], dtype=x.dtype).expand_as(x)

    @classmethod
    def bau(cls, z_mm, klassen, frei):
        """→ (Mesh3daimeshvorne mit Attrappe, x (N, 3) m)."""
        import torch
        from Genesis9.meshziel import G9meshziel
        from mesh3dai_meshvorne import Mesh3daimeshvorne
        n = len(z_mm)
        x = torch.zeros((n, 3), dtype=torch.float64)
        x[:, 0] = torch.arange(n, dtype=torch.float64) * 0.01
        x[:, 2] = torch.as_tensor(z_mm, dtype=torch.float64) / 1000.0
        vo = object.__new__(Mesh3daimeshvorne)
        vo.i = cls.Innen([G9meshziel.HAUT if c == cls.HAUT else G9meshziel.HAAR for c in klassen])
        vo.frei = torch.as_tensor(frei)
        return vo, x

    def test_paare(self):
        import torch
        vo, x = self.bau([6.0, 1.0, -1.0, 3.0, -0.5, 6.0], [self.HAUT] * 3 + [self.HAAR] * 2 + [self.HAUT], [True] * 5 + [False])
        self.assertEqual(vo.paare(x)[3].tolist(), [True, False, False, True, True, False])
        nur = torch.tensor([False, True, True, True, True, True])
        self.assertEqual(vo.paare(x, nur)[3].tolist(), [False, False, False, True, True, False])

    def test_verlust(self):
        vo, x = self.bau([6.0, 0.0], [self.HAUT] * 2, [True, True])
        paare = vo.paare(x)
        x = x.clone().requires_grad_(True)
        v = vo.verlust(x, paare)
        self.assertAlmostEqual(float(v), 16.0, places=4)
        v.backward()
        self.assertGreater(float(x.grad[0, 2]), 0.0)          # Abstieg = −Gradient → nach −z, hinein
        self.assertEqual(float(x.grad[1].abs().sum()), 0.0)

    def test_abstieg(self):
        import torch
        vo, x = self.bau([6.0, 3.0], [self.HAUT, self.HAAR], [True, True])
        o = torch.zeros_like(x).requires_grad_(True)
        opt = torch.optim.Adam([o], 2e-4)
        for s in range(400):
            if s % 50 == 0:
                paare = vo.paare((x + o).detach())
            opt.zero_grad()
            vo.verlust(x + o, paare).backward()
            opt.step()
        z = (x + o).detach()[:, 2].numpy() * 1000.0
        self.assertLessEqual(float(z[0]), vo.VOR_HAUT_MM + 0.05)
        self.assertLessEqual(float(z[1]), -vo.INNEN_SONST_MM + 0.05)

    def test_zahlen(self):
        vo, x = self.bau([6.0, 2.2, 0.0], [self.HAUT] * 3, [True] * 3)
        n, rest = vo.zahlen(x).tolist()
        self.assertEqual(int(n), 1)
        self.assertAlmostEqual(rest, 4.0, places=4)

    def test_signaturen_der_attrappen(self):
        from Genesis9.meshflaeche import G9meshflaeche
        from Genesis9.meshinnen import G9meshinnen

        def namen(f):
            return set(inspect.signature(f).parameters) - {'self'}
        self.assertLessEqual(namen(G9meshinnen.aussen), namen(self.Innen.aussen))
        for m in ('suchen', 'abstaende'):
            self.assertLessEqual(namen(getattr(G9meshflaeche, m)), namen(getattr(self.Flaeche, m)), m)
