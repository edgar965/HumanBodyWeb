# -*- coding: utf-8 -*-
u"""Lesen und Schreiben im Schritt „rig“ ohne Umwege (25.11.2026, Edgar: „vor allem rig“) — dieselben Inhalte wie vorher.

1. `Nebenschreiber`: schreibt nebenher, `warten` sieht die fertige Datei, zweimal dieselbe Datei der Reihe nach, ein Fehler wirft beim Warten.
2. `Kurzspeicher`: `leeren` ruft jede gemeldete Ablage.
3. `Schnelllader.laden` = `torch.load` (verschachtelt, geteilte Ablagen, Parameter, andere Typen); `bereiche` liefert die Bytes der Datei.
4. `Glbfelder`: Punkte, Dreiecke, UV, Textur und Eckfarben wie trimesh; zwei Netze, Punktfarben oder Spiegelung → None.
5. `Netzvorrat.felder`/`eckfarben` mit und ohne `Glbfelder` gleich.
6. `Ansichtnetz` = `Ansichtraster.netze(trimesh)`; ein gedrehter Knoten oder eine Normalenkarte → None.
7. `Uvprojektion`/`Uvgeometrie.kaesten` = Insel für Insel.

Sabotage (nicht gelaufen): in `Nebenschreiber.legen` das `cls.warten(pfad)` weglassen → Fall 1 kann rot werden; in `Glbfelder` `1.0 - uv[:, 1]` weglassen → Fall 4 rot; in `Uvprojektion` `% v` durch
`// v` → Fall 7 rot. Geschrieben, nicht gelaufen.
"""
import sys
import threading
import unittest
from pathlib import Path

import torch
import trimesh
from django.conf import settings
from PIL import Image

from ._pruefablage import Pruefablage

for _p in (str(settings.TOOLS_ROOT), str(settings.TOOLS_ROOT / 'meshgenesis')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from KoerperKI_alle.glbfelder import Glbfelder  # noqa: E402
from KoerperKI_alle.kurzspeicher import Kurzspeicher  # noqa: E402
from KoerperKI_alle.nebenschreiber import Nebenschreiber  # noqa: E402
from KoerperKI_alle.schnelllader import Schnelllader  # noqa: E402

KARTE = 'cuda'


class NebenschreiberTest(unittest.TestCase):

    def test_1_warten_und_reihenfolge(self):
        with Pruefablage.ordner() as ordner:
            pfad, tor = Path(ordner) / 'a.txt', threading.Event()
            Nebenschreiber.legen(pfad, lambda: (tor.wait(5), pfad.write_text('eins')))
            self.assertFalse(pfad.exists())
            tor.set()
            Nebenschreiber.legen(pfad, lambda: pfad.write_text(pfad.read_text() + ' zwei'))
            Nebenschreiber.warten(pfad)
            self.assertEqual(pfad.read_text(), 'eins zwei')

            def kaputt():
                raise ValueError('voll')
            Nebenschreiber.legen(pfad, kaputt)
            with self.assertRaises(ValueError):
                Nebenschreiber.warten()
            Nebenschreiber.warten()          # der Fehler ist gemeldet, danach ist nichts mehr offen

    def test_2_kurzspeicher(self):
        gerufen = []
        alt = list(Kurzspeicher._ablagen)
        try:
            Kurzspeicher._ablagen[:] = []
            Kurzspeicher.melden(lambda: gerufen.append('a'))
            Kurzspeicher.melden(lambda: gerufen.append('b'))
            Kurzspeicher.leeren()
        finally:
            Kurzspeicher._ablagen[:] = alt
        self.assertEqual(gerufen, ['a', 'b'])


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class SchnellladerTest(unittest.TestCase):

    def test_3_wie_torch_load(self):
        z = torch.Generator(device=KARTE).manual_seed(2)
        gross = torch.randn(3000, 700, device=KARTE, generator=z)
        inhalt = {'a': gross, 'sicht': gross[10:20], 'zahl': 7, 'liste': [torch.arange(5, device=KARTE), ('x', torch.ones(2, 2, dtype=torch.float16, device=KARTE))],
                  'parameter': torch.nn.Parameter(torch.rand(4, 4, device=KARTE, generator=z)), 'leer': torch.empty(0, 3, device=KARTE)}
        with Pruefablage.ordner() as ordner:
            pfad = Path(ordner) / 'm.pt'
            torch.save(inhalt, pfad)
            soll, ist = torch.load(pfad, map_location=KARTE, weights_only=False), Schnelllader.laden(pfad, weights_only=False)
            roh = pfad.read_bytes()
            teile = Schnelllader.bereiche(pfad, [(100, 5000), (0, 17)])
        self.assertEqual(list(soll), list(ist))
        for a, b in ((soll['a'], ist['a']), (soll['sicht'], ist['sicht']), (soll['liste'][0], ist['liste'][0]), (soll['liste'][1][1], ist['liste'][1][1]), (soll['parameter'], ist['parameter']),
                     (soll['leer'], ist['leer'])):
            self.assertTrue(a.dtype == b.dtype and a.shape == b.shape and b.is_cuda and torch.equal(a, b))
        self.assertEqual(ist['zahl'], 7)
        self.assertIsInstance(ist['parameter'], torch.nn.Parameter)
        self.assertEqual(ist['sicht'].untyped_storage().data_ptr(), ist['a'].untyped_storage().data_ptr())
        for (ab, laenge), t in zip([(100, 5000), (0, 17)], teile, strict=True):
            self.assertEqual(bytes(t.tolist()), roh[ab:ab + laenge])


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class GlbTest(unittest.TestCase):

    def _glb(self, ordner, name='n.glb', lage=None, zwei=False, normalenkarte=False, farben=False):
        kugel = trimesh.creation.icosphere(subdivisions=2)
        z = torch.Generator(device=KARTE).manual_seed(4)
        uv = torch.rand(len(kugel.vertices), 2, device=KARTE, generator=z).cpu().numpy()          # cpu gewollt: Übergabe an trimesh
        bild = Image.frombytes('RGB', (16, 8), bytes(range(256)) + bytes(128))
        if farben:
            kugel.visual.vertex_colors = [10, 20, 30, 255]
        else:
            mat = trimesh.visual.material.PBRMaterial(baseColorTexture=bild, metallicFactor=0.0, roughnessFactor=0.8, normalTexture=bild if normalenkarte else None)
            kugel.visual = trimesh.visual.TextureVisuals(uv=uv, material=mat)
        szene = trimesh.Scene()
        szene.add_geometry(kugel, transform=lage)
        if zwei:
            szene.add_geometry(kugel.copy(), transform=trimesh.transformations.translation_matrix([3, 0, 0]))
        pfad = Path(ordner) / name
        szene.export(str(pfad))
        Glbfelder.leeren()
        return pfad

    def _trimesh(self, pfad):
        n = trimesh.load(str(pfad), process=False).to_geometry()
        return n, torch.as_tensor(n.vertices.copy(), dtype=torch.float64, device=KARTE), torch.as_tensor(n.faces.copy(), dtype=torch.int64, device=KARTE)

    def test_4_glbfelder(self):
        with Pruefablage.ordner() as ordner:
            for lage in (None, trimesh.transformations.scale_matrix(2.0)):
                pfad = self._glb(ordner, 'a%d.glb' % (lage is not None), lage)
                e = Glbfelder.lesen(pfad)
                n, p, f = self._trimesh(pfad)
                self.assertLess(float((e.punkte - p).abs().max()), 1e-12)
                self.assertTrue(torch.equal(e.dreiecke, f))
                self.assertTrue(torch.equal(e.uv.double(), torch.as_tensor(n.visual.uv.copy(), dtype=torch.float64, device=KARTE)))
                self.assertEqual(e.eckfarben().tolist(), n.visual.to_color().vertex_colors.tolist())
                self.assertIs(Glbfelder.lesen(pfad), e)
            self.assertIsNone(Glbfelder.lesen(self._glb(ordner, 'zwei.glb', zwei=True)))
            self.assertIsNone(Glbfelder.lesen(self._glb(ordner, 'farben.glb', farben=True)))
            self.assertIsNone(Glbfelder.lesen(self._glb(ordner, 'spiegel.glb', trimesh.transformations.reflection_matrix([0, 0, 0], [1, 0, 0]))))

    def test_5_netzvorrat(self):
        from meshgenesis_netzvorrat import Netzvorrat
        with Pruefablage.ordner() as ordner:
            for farben in (False, True):
                pfad = self._glb(ordner, 'v%d.glb' % farben, farben=farben)
                v, f = Netzvorrat.felder(pfad)
                n, p, d = self._trimesh(pfad)
                self.assertTrue(torch.equal(f, d) and float((v - p).abs().max()) < 1e-12)
                c = n.visual.vertex_colors if farben else n.visual.to_color().vertex_colors
                soll = torch.as_tensor(c.copy(), device=KARTE)[:, :3].float() / 255.0
                self.assertTrue(torch.equal(Netzvorrat.eckfarben(pfad, f), soll[f]))

    def test_6_ansichtnetz(self):
        from meshgenesis_ansichtnetz import Ansichtnetz
        from meshgenesis_ansichtraster import Ansichtraster
        g = torch.device(KARTE)
        with Pruefablage.ordner() as ordner:
            pfad = self._glb(ordner, 'b.glb', trimesh.transformations.scale_matrix(1.5))
            kasten, ((p, f, d),) = Ansichtnetz.lesen(pfad, g)
            szene = Ansichtraster._szene_lesen(pfad)
            ((p0, f0, d0),) = Ansichtraster.netze(szene, g)
            self.assertLess(float((p - p0).abs().max()), 1e-6)
            self.assertTrue(torch.equal(f, f0))
            self.assertLess(float((d['n'] - d0['n']).abs().max()), 1e-5)
            self.assertTrue(torch.equal(d['uv'], d0['uv']) and (d['metall'], d['rauheit']) == (d0['metall'], d0['rauheit']))
            self.assertTrue(all(torch.equal(a, b) for a, b in zip(d['farbe'], d0['farbe'], strict=True)))
            self.assertLess(float((kasten - torch.as_tensor(szene.bounds.copy(), device=KARTE)).abs().max()), 1e-6)
            self.assertIsNone(Ansichtnetz.lesen(self._glb(ordner, 'c.glb', trimesh.transformations.rotation_matrix(0.4, [0, 1, 0])), g))
            self.assertIsNone(Ansichtnetz.lesen(self._glb(ordner, 'd.glb', normalenkarte=True), g))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Grafikkarte')
class UvTest(unittest.TestCase):

    def test_7_insel_fuer_insel(self):
        from Stoffsolver.uvgeometrie import Uvgeometrie
        from Stoffsolver.uvprojektion import Uvprojektion
        kugel = trimesh.creation.icosphere(subdivisions=2)
        p, d = torch.as_tensor(kugel.vertices.copy(), dtype=torch.float64, device=KARTE), torch.as_tensor(kugel.faces.copy(), dtype=torch.int64, device=KARTE)
        insel = torch.arange(len(d), device=KARTE) % 7 - 1          # −1 = ohne UV
        achsen = torch.nn.functional.normalize(torch.randn(6, 3, device=KARTE, dtype=torch.float64, generator=torch.Generator(device=KARTE).manual_seed(3)), dim=1)
        uv, ecken, herkunft = Uvprojektion.rechnen(p, d, insel, 6, achsen)
        ab = 0
        for i in range(6):
            faces = torch.nonzero(insel == i, as_tuple=True)[0]
            benutzt, lokal = torch.unique(d[faces], return_inverse=True)
            soll = (p[benutzt] @ Uvgeometrie.projektionsbasis(achsen[i])[0].T)[lokal]
            self.assertTrue(torch.equal(uv[faces], soll) and torch.equal(ecken[faces], lokal + ab) and torch.equal(herkunft[ab:ab + len(benutzt)], benutzt))
            unten, oben = Uvgeometrie.kaesten(uv[insel >= 0], insel[insel >= 0], 6)
            self.assertTrue(torch.equal(unten[i], soll.reshape(-1, 2).amin(0)) and torch.equal(oben[i], soll.reshape(-1, 2).amax(0)))
            ab += len(benutzt)
        self.assertEqual(len(herkunft), ab)
        self.assertEqual(float(uv[insel < 0].abs().max()), 0.0)


if __name__ == '__main__':
    unittest.main()
