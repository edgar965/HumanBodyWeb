# -*- coding: utf-8 -*-
"""`Pymafxbild.umbenennen`: Netzdateien tragen den Bildstamm (19.09.2026).

`netz_speichern`/`kopf_speichern` schreiben feste Namen neben das Bild.
Im Mehrbild-Runner (alle Bilder in einem Ordner, ein Prozess) bekam das
erste Bild so den Kopf des letzten, die anderen keinen.
"""

import os
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from pymafxbild import Pymafxbild  # noqa: E402


class DasUmbenennen(unittest.TestCase):
    def test_die_datei_bekommt_den_bildstamm(self):
        with Pruefablage.ordner() as ordner:
            fest = os.path.join(ordner, 'flame_vertices.npy')
            with open(fest, 'wb') as f:
                f.write(b'x')
            ziel = Pymafxbild.umbenennen(fest, os.path.join(ordner, 'kopf_04.jpg'), Pymafxbild.KOPF)
            self.assertEqual(os.path.basename(ziel), 'kopf_04_flame.npy')
            self.assertTrue(os.path.isfile(ziel))
            self.assertFalse(os.path.exists(fest))

    def test_zwei_bilder_ueberschreiben_sich_nicht(self):
        with Pruefablage.ordner() as ordner:
            ziele = []
            for name, inhalt in (('a.jpg', b'a'), ('b.jpg', b'b')):
                fest = os.path.join(ordner, 'posed_vertices.npy')
                with open(fest, 'wb') as f:
                    f.write(inhalt)
                ziele.append(Pymafxbild.umbenennen(fest, os.path.join(ordner, name), Pymafxbild.NETZ))
            self.assertEqual([os.path.basename(z) for z in ziele], ['a_posed.npy', 'b_posed.npy'])
            self.assertEqual(open(ziele[0], 'rb').read(), b'a')

    def test_nichts_geschrieben_nichts_umbenannt(self):
        self.assertIsNone(Pymafxbild.umbenennen(None, '/egal/x.jpg', Pymafxbild.NETZ))
