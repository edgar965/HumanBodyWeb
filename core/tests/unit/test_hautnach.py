# -*- coding: utf-8 -*-
"""Die Nacharbeit einer Haut-Kachel auf der GPU (`core/dienste/hautnach`) gegen die CPU-Fassungen (`blendimportnormalen.py`, `blendimportfarbangleich.py`, `blendimportumfeld.py`).

Dieselbe Rechnung, anderes Gerät (Edgar, 10.10.2026: „die Nacharbeit im Speicher auf der GPU rechnen"): Rosemarys Kachel 1001 brauchte auf der CPU 120 s, auf der GPU 12 s. Die Tests prüfen,
dass die Zahlen dieselben sind — an synthetischen Feldern, ohne Blender und Datenbank:

1. `Hautnachfilter.gauss` gleicht `scipy.ndimage.gaussian_filter` (gemessen größte Abweichung 8e-7 bei σ = 48); `dilatation` gleicht `binary_dilation` Texel für Texel.
2. `Hautnachnormalen.saeubern`: Anteil und Bytes gleich; `feindetail`: höchstens eine Stufe Abweichung (`rint` gegen Rundung auf der GPU), und nur an wenigen Bytes (gemessen 11 von 786.432).
3. `Hautnachfarbe.hinten`: höchstens eine Stufe (gemessen 1 Byte von 786.432); Texel ohne Fehlstelle ändern sich nie.
4. `Hautnachumfeld`: dieselben Fälle wie der CPU-Test (`test_blendimport_umfeld.py`, Fall 1–5) und ein Vergleich mit der CPU-Fassung (die Berichtszahlen sind gleich, 99 % der Texel
   höchstens eine Stufe daneben; an Rosemarys Kachel 1001 gemessen: 1.129 von 548.790 Texeln verschieden, 66 um mehr als eine Stufe, größte Abweichung 17).

Sabotage-Gegenprobe (11.10.2026, danach rückgängig): in `Hautnachfilter.kern` die Halbbreite `4σ` → `2σ` → Fall 1 (Gauß), 4 (Feindetail) und 6 (Farbangleich) rot; in `hautnachumfeld._rastern` die Zugabe
`kleinste >= -rand` → `-rand · 0` → UmfeldGpu-Fall 4 (Saum) und 8 (gleich der CPU) rot.
"""

import numpy as np
import warp as wp
from django.test import SimpleTestCase
from PIL import Image
from scipy import ndimage

from core.dienste.blendimportfarbangleich import Blendimportfarbangleich
from core.dienste.blendimportnormalen import Blendimportnormalen
from core.dienste.blendimportumfeld import Blendimportumfeld
from core.dienste.hautnach import Hautnachfarbe, Hautnachfilter, Hautnachnormalen
from core.dienste.hautnach.hautnachumfeld import Hautnachumfeld
from core.tests.unit import test_blendimport_umfeld as cpu_umfeld

GERAET = 'cuda:0'


class FilterTest(SimpleTestCase):
    databases = set()

    def test_1_gauss_gleicht_scipy(self):
        f = Hautnachfilter(GERAET)
        a = np.random.default_rng(7).random((90, 130)).astype(np.float32)
        for sigma in (1.5, 3.0, 12.0, 48.0):
            gpu = f.gauss(wp.array(a, dtype=wp.float32, device=GERAET), sigma).numpy()
            self.assertLess(float(np.abs(gpu - ndimage.gaussian_filter(a, sigma)).max()), 5e-6, 'sigma %s' % sigma)

    def test_2_dilatation_gleicht_scipy_texel_fuer_texel(self):
        f = Hautnachfilter(GERAET)
        m = np.random.default_rng(3).random((70, 90)) > 0.99
        for schritte in (1, 2, 3):
            gpu = f.dilatation(wp.array(m.astype(np.uint8), dtype=wp.uint8, device=GERAET), schritte).numpy().astype(bool)
            self.assertTrue(np.array_equal(gpu, ndimage.binary_dilation(m, iterations=schritte)), 'Schritte %d' % schritte)


def _normalenkarte():
    rng = np.random.default_rng(5)
    h = w = 192
    yy, xx = np.mgrid[0:h, 0:w]
    nx = 0.3 * np.sin(xx / 25.0) + 0.05 * rng.standard_normal((h, w))
    ny = 0.3 * np.cos(yy / 33.0) + 0.05 * rng.standard_normal((h, w))
    nz = np.sqrt(np.maximum(1 - nx ** 2 - ny ** 2, 0.01))
    n = np.stack([nx, ny, nz], axis=-1)
    n[40:46, 70:90] = (0.9, 0.1, 0.1)                        # falsche Treffer
    n = np.clip(np.rint((n / np.linalg.norm(n, axis=2, keepdims=True) + 1) * 127.5), 0, 255).astype(np.uint8)
    leer = np.zeros((h, w), bool)
    leer[100:130, 20:80] = True
    leer[:, :8] = True
    n[leer] = (128, 128, 255)
    return n, leer


class NormalenTest(SimpleTestCase):
    databases = set()

    def test_3_saeubern_gleich(self):
        n, leer = _normalenkarte()
        g = Hautnachnormalen(GERAET)
        for grad in (None, 30.0):
            cpu, anteil_cpu = Blendimportnormalen.saeubern(n, leer, grad)
            gpu, anteil_gpu = g.saeubern(n, leer, grad)
            self.assertEqual(anteil_cpu, anteil_gpu)
            self.assertTrue(np.array_equal(cpu, gpu), 'grad %s: %d Bytes verschieden' % (grad, int((cpu != gpu).sum())))
        self.assertGreater(anteil_cpu, 1.0)                       # der Test schneidet wirklich etwas weg (sonst prüfte er nichts)

    def test_4_feindetail_hoechstens_eine_stufe(self):
        n, leer = _normalenkarte()
        g = Hautnachnormalen(GERAET)
        for sigma in (None, 12.0):
            cpu = Blendimportnormalen.feindetail(n, leer, sigma)
            gpu = g.feindetail(n, leer, sigma)
            d = np.abs(cpu.astype(int) - gpu.astype(int))
            self.assertLessEqual(int(d.max()), 1, 'sigma %s' % sigma)
            self.assertLess(int((d > 0).sum()), d.size * 0.001)
            self.assertTrue((gpu[leer] == (128, 128, 255)).all(), 'Fehlstellen bleiben flach')
        self.assertGreater(int((n != cpu).sum()), 1000)           # die Karte ändert sich wirklich

    def test_5_die_eingabe_bleibt_unveraendert(self):
        n, leer = _normalenkarte()
        kopie = n.copy()
        g = Hautnachnormalen(GERAET)
        g.saeubern(n, leer)
        g.feindetail(n, leer)
        self.assertTrue(np.array_equal(n, kopie))


class FarbeTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _szene():
        rng = np.random.default_rng(11)
        h = w = 256
        yy, xx = np.mgrid[0:h, 0:w]
        farbe = np.clip(np.stack([180 + 30 * np.sin(xx / 30.0), 130 + 20 * np.cos(yy / 25.0), 110 + 10 * np.sin((xx + yy) / 50.0)], axis=-1) + rng.standard_normal((h, w, 3)) * 2, 0, 255).astype(np.uint8)
        fehl = np.zeros((h, w), bool)
        fehl[100:170, 50:150] = True
        fehl[:, :20] = True
        farbe[fehl] = 0
        ersatz = np.clip(np.stack([210 + 10 * np.sin(xx / 20.0), 160 + 15 * np.cos(yy / 33.0), 140 + 0 * xx], axis=-1), 0, 255).astype(np.uint8)
        ersatz[30:33, 200:204] = 255                             # ein weißes Loch in der Ersatzkachel
        return farbe, fehl, Image.fromarray(ersatz).resize((128, 128), Image.BILINEAR)

    def test_6_hinten_hoechstens_eine_stufe_und_nur_auf_fehlstellen(self):
        farbe, fehl, ersatz = self._szene()
        cpu = Blendimportfarbangleich.hinten(ersatz, farbe, fehl)
        gpu = Hautnachfarbe(GERAET).hinten(ersatz, farbe, fehl)
        d = np.abs(cpu.astype(int) - gpu.astype(int))
        self.assertLessEqual(int(d.max()), 1)
        self.assertLess(int((d > 0).sum()), d.size * 0.001)
        # Der Angleich verändert die Ersatzfarbe der Fehlstellen (ohne ihn wäre der Test leer) …
        voll = np.asarray(ersatz.resize((256, 256), Image.LANCZOS))
        self.assertGreater(float(np.abs(gpu[fehl].astype(int) - voll[fehl].astype(int)).mean()), 5.0)
        # … und das Ergebnis ist die Ersatzkachel im Ton der Nachbarschaft: die Mitte der Fehlstelle liegt näher an den gebackenen Texeln daneben als die rohe Ersatzfarbe.
        gebacken = farbe[~fehl].mean(axis=0)
        self.assertLess(float(np.abs(gpu[fehl].mean(axis=0) - gebacken).mean()), float(np.abs(voll[fehl].mean(axis=0) - gebacken).mean()))


class UmfeldGpuTest(cpu_umfeld.UmfeldTest):
    """Die Fälle der CPU-Fassung (Fall 1–5), auf der GPU. Fall 6 und 7 prüfen CPU-Bausteine (`Hbdreiecksuche`, `trimesh`) und entfallen."""

    def _umfeld(self, original_z=-0.003, von=0.0, bis=1.0, kachel=None, stueck=(0.0, 0.0, 0.0)):
        cpu, figur = super()._umfeld(original_z, von, bis, kachel, stueck)
        gpu = Hautnachumfeld(cpu.stueck, cpu.figur, cpu.original, cpu.farbbild, GERAET)
        return gpu, figur

    test_6_weit_entfernte_texel_kosten_keinen_weg_zur_flaeche = None
    test_7_die_flaechensuche_liefert_dieselbe_uv_und_denselben_abstand_wie_trimesh = None

    def test_8_gleich_der_cpu_fassung(self):
        cpu, _ = cpu_umfeld.UmfeldTest._umfeld(self, original_z=-0.003)
        gpu = Hautnachumfeld(cpu.stueck, cpu.figur, cpu.original, cpu.farbbild, GERAET)
        farbe_a, leer = self._kachel()
        farbe_b = farbe_a.copy()
        cpu.fuellen(self.KACHEL, farbe_a, leer)
        gpu.fuellen(self.KACHEL, farbe_b, leer)
        self.assertEqual(cpu.bericht['texel'], gpu.bericht['texel'])
        self.assertEqual(cpu.bericht['gefuellt'], gpu.bericht['gefuellt'])
        self.assertGreater(gpu.bericht['gefuellt'], 100)
        d = np.abs(farbe_a.astype(int) - farbe_b.astype(int)).max(axis=2)
        self.assertGreaterEqual(float((d <= 1).mean()), 0.99)
        self.assertLess(int(d.max()), 20)
