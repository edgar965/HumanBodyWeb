# -*- coding: utf-8 -*-
"""Bild- und Textwege auf der Karte (25.11.2026, Edgar: „alles auf Karte, nichts auf CPU!“): Pilgroesse gegen Pillow, Bildleser, Kartentext gegen Pythons `%`, Gzipfaeden, Kartenabstand gegen die
volle Suche, der UV-Satz der eigenen Stücke gegen die Schleife."""
import gzip
import io
import json
import os
import shutil
import sys
import unittest
from pathlib import Path

import torch
from django.conf import settings
from django.test import SimpleTestCase

if r'A:\3DTools' not in sys.path:
    sys.path.append(r'A:\3DTools')


def zufall(*form, saat=1):
    return torch.rand(form, device='cuda', generator=torch.Generator(device='cuda').manual_seed(saat))


@unittest.skipUnless(torch.cuda.is_available(), 'braucht die Karte')
class KartenTests(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / ('_test_karte_%d' % os.getpid())
        self.ordner.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, self.ordner, True)

    # ------------------------------------------------------------------ Größe ändern

    def test_groesse_bitgleich_mit_pillow(self):
        from PIL import Image

        from KoerperKI_alle.pilbild import Pilbild
        from KoerperKI_alle.pilgroesse import Pilgroesse
        filter_ = {'box': Image.BOX, 'bilinear': Image.BILINEAR, 'bicubic': Image.BICUBIC, 'lanczos': Image.LANCZOS, 'nearest': Image.NEAREST}
        for form in ((64, 48, 3), (133, 217, 3), (100, 90)):
            x = (zufall(*form) * 256).to(torch.uint8)
            bild = Pilbild.aus(x)
            for ziel in ((form[1] // 2, form[0] // 3), (form[1] * 2, form[0] + 7), (31, 29)):
                for name, f in filter_.items():
                    with self.subTest(form=form, ziel=ziel, filter=name):
                        self.assertTrue(torch.equal(Pilbild.feld(bild.resize(ziel, f)), Pilgroesse.resize(x, ziel, name)))

    def test_thumbnail_wie_pillow_auch_mit_vorverkleinern(self):
        from PIL import Image

        from KoerperKI_alle.pilbild import Pilbild
        from KoerperKI_alle.pilgroesse import Pilgroesse
        x = (zufall(400, 611, 3) * 256).to(torch.uint8)
        for kante in (300, 64, 33, 1000):
            for name, f in (('bicubic', Image.BICUBIC), ('lanczos', Image.LANCZOS)):
                klein = Pilbild.aus(x)
                klein.thumbnail((kante, kante), f)
                mit = Pilgroesse.thumbnail(x, (kante, kante), name)
                with self.subTest(kante=kante, filter=name):
                    self.assertTrue(torch.equal(Pilbild.feld(klein), mit))

    # ------------------------------------------------------------------ Bilder lesen und schreiben

    def test_bildleser_liest_jpeg_wie_pillow_und_merkt_den_stand(self):
        from KoerperKI_alle.bildleser import Bildleser
        from KoerperKI_alle.pilbild import Pilbild
        pfad = self.ordner / 'a.jpg'
        x = torch.nn.functional.interpolate(zufall(1, 3, 8, 8), (128, 96), mode='bicubic').clamp(0, 1)[0].permute(1, 2, 0)
        x = (x * 255).to(torch.uint8)
        Pilbild.aus(x).save(pfad, quality=92, subsampling=0)          # 4:4:4: nvJPEG und libjpeg geben dieselben Pixel
        from PIL import Image
        with Image.open(pfad) as b:
            soll = Pilbild.feld(b.convert('RGB'))
        ist = Bildleser.lesen(pfad, 'RGB')
        self.assertTrue(torch.equal(soll, ist))
        self.assertIs(Bildleser.lesen(pfad, 'RGB'), ist)          # aus dem Speicher
        Pilbild.aus(255 - x).save(pfad, quality=92, subsampling=0)
        os.utime(pfad, ns=(1, 1))
        self.assertFalse(torch.equal(Bildleser.lesen(pfad, 'RGB'), ist))          # neuer Stand, neu gelesen

    def test_bildleser_png_palette_und_grau(self):
        from PIL import Image

        from KoerperKI_alle.bildleser import Bildleser
        from KoerperKI_alle.pilbild import Pilbild
        x = (zufall(40, 30, 4) * 256).to(torch.uint8)
        Pilbild.aus(x).save(self.ordner / 'rgba.png')
        Pilbild.aus(x[..., :3]).convert('P').save(self.ordner / 'palette.png')
        for name in ('rgba.png', 'palette.png'):
            for modus in ('RGB', 'RGBA', 'L'):
                with Image.open(self.ordner / name) as b:
                    soll = Pilbild.feld(b.convert('RGBA' if modus == 'RGBA' else 'RGB').convert(modus) if modus == 'L' else b.convert(modus))
                with self.subTest(datei=name, modus=modus):
                    self.assertTrue(torch.equal(soll, Bildleser.lesen(self.ordner / name, modus)))

    def test_jpeg_schreiben_ist_lesbar_und_nah(self):
        from KoerperKI_alle.bildleser import Bildleser
        x = torch.nn.functional.interpolate(zufall(1, 3, 6, 6), (64, 64), mode='bicubic').clamp(0, 1)[0].permute(1, 2, 0)
        x = (x * 255).to(torch.uint8)
        Bildleser.jpeg(x, self.ordner / 'b.jpg', 95)
        self.assertLess(float((Bildleser.lesen(self.ordner / 'b.jpg', 'RGB').int() - x.int()).abs().double().mean()), 2.0)
        grau = Bildleser.dekodieren(Bildleser.jpeg_bytes(x[..., 0], 95))
        self.assertLess(float((grau[..., 0].int() - x[..., 0].int()).abs().double().mean()), 2.0)

    # ------------------------------------------------------------------ Text

    def test_zahlentext_wie_python(self):
        from KoerperKI_alle.kartentext import Kartentext
        x = torch.cat([(zufall(500, 3).double() - 0.5) * 40, torch.tensor([[0.0, -0.0, 1.0], [5e-7, 1.5e-6, -5e-7], [0.5, 1.5, 2.5], [99.9999995, 2.675, -123456.789]], dtype=torch.float64, device='cuda')])
        for stellen in (6, 5, 2):
            soll = ''.join('v %.*f %.*f %.*f\n' % (stellen, a, stellen, b, stellen, c) for a, b, c in x.tolist()).encode()
            self.assertEqual(soll, Kartentext.zeilen(x, stellen, 'v ', ' ', '\n'))
        self.assertEqual([[round(v, 5) for v in z] for z in x.tolist()], json.loads(Kartentext.json(x, 5)))
        i = torch.arange(12, device='cuda').reshape(2, 6)
        self.assertEqual(b'f 0/1 2/3 4/5\nf 6/7 8/9 10/11\n', Kartentext.zeilen(i, 0, 'f ', ('/', ' ', '/', ' ', '/')))
        self.assertEqual(b'[]', Kartentext.json(x[:0], 5))

    def test_objtext_auf_der_karte_wie_die_zeilen(self):
        from KoerperKI_alle.objtext import Objtext
        p, d = zufall(9, 3).double(), torch.tensor([[0, 1, 2], [3, 4, 5], [6, 7, 8]], device='cuda')
        uv = zufall(9, 2).double()
        soll = '\n'.join([*Objtext.v(p), *Objtext.vt(uv), *Objtext.f_ecken(d)]) + '\n'
        self.assertEqual(soll.encode(), Objtext.karte(p, uv, d))

    def test_gzip_in_faeden_ist_ein_strom(self):
        from KoerperKI_alle.gzipfaeden import Gzipfaeden
        for inhalt in (b'', b'abc', os.urandom(1 << 20) + b'x' * (3 << 20)):
            self.assertEqual(inhalt, gzip.decompress(Gzipfaeden.packen(inhalt)))
            self.assertEqual(inhalt, gzip.GzipFile(fileobj=io.BytesIO(Gzipfaeden.packen(inhalt))).read())

    # ------------------------------------------------------------------ Abstand, UV-Satz, DSON

    def test_abstand_kern_gegen_die_volle_suche_mit_gleichstand(self):
        from KoerperKI_alle.kartenabstand import Kartenabstand
        for form, dichte in (((23, 31), 0.1), ((40, 17), 0.6), ((1, 30), 0.2), ((9, 8, 7), 0.1)):
            x = zufall(*form, saat=3) >= dichte
            d, idx = Kartenabstand.distance_transform_edt(x, return_distances=True, return_indices=True)
            frei = torch.nonzero(~x)
            alle = torch.stack(torch.meshgrid(*[torch.arange(k, device='cuda') for k in form], indexing='ij'), -1).reshape(-1, len(form))
            quadrat = ((alle[:, None] - frei[None]) ** 2).sum(-1).amin(1)
            self.assertTrue(torch.equal(quadrat.double().sqrt().reshape(form), d))
            self.assertTrue(torch.equal(((alle.T.reshape(len(form), *form) - idx.long()) ** 2).sum(0), quadrat.reshape(form)))

    def test_abstand_kern_wie_die_bandsuche(self):
        from KoerperKI_alle.kartenabstand import Kartenabstand
        x = zufall(60, 80, saat=5) >= 0.05
        a = Kartenabstand.distance_transform_edt(x, sampling=[1.0, 1.0], return_distances=True, return_indices=True)          # mit Sampling: die Bandsuche
        b = Kartenabstand.distance_transform_edt(x, return_distances=True, return_indices=True)
        self.assertTrue(all(torch.equal(p, q) for p, q in zip(a, b, strict=True)))

    def test_uvsatz_auf_der_karte_wie_die_schleife(self):
        from Genesis9.dsonuvsatz import G9dsonuvsatz
        flaechen = torch.tensor([[0, 1, 2], [2, 1, 3], [3, 1, 5]], device='cuda')          # Punkt 4 kommt nicht vor
        uv = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0], [0.5, 1.0], [0.25, 0.0], [0.75, 0.5], [0.75, 0.5], [1.0, 0.0], [0.1, 0.2]], dtype=torch.float64, device='cuda')
        je_ecke = torch.arange(9, device='cuda').reshape(3, 3)
        _n, werte, ueber = G9dsonuvsatz.felder(6, flaechen.tolist(), uv, je_ecke.tolist())
        w, u = G9dsonuvsatz.karte(6, flaechen, uv, je_ecke)
        self.assertEqual(werte, w.tolist())
        self.assertEqual(ueber, u.tolist())

    def test_dsontext_setzt_die_felder_ein(self):
        from Genesis9.dsontext import G9dsontext
        t = G9dsontext()
        daten = {'a': 'Tür „x“', 'v': {'count': 2, 'values': t.feld(torch.tensor([[1.0, 2.5], [0.123456, -3.0]], dtype=torch.float64, device='cuda'), 5)}, 'p': t.feld(torch.tensor([[0, 7]], device='cuda'), 0)}
        self.assertEqual({'a': 'Tür „x“', 'v': {'count': 2, 'values': [[1.0, 2.5], [0.12346, -3.0]]}, 'p': [[0, 7]]}, json.loads(t.bytes(daten)))
        self.assertEqual({'a': [1, 2]}, json.loads(G9dsontext().bytes({'a': [1, 2]})))
