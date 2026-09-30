# -*- coding: utf-8 -*-
"""Kostuem — baut alle Teile aus einem Wertesatz und räumt sie vor dem nächsten Kandidaten wieder ab.

Der Körper bleibt in der Szene; abgeräumt wird nur, was `Rohr.MARKE` trägt — samt Netz und Material, sonst
wächst die Datei bei vielen Kandidaten in einem Blender-Lauf mit jedem Bau.
"""

import bpy  # pyright: ignore[reportMissingImports]

from effekte.blender.kostuem.kostuemkopf import Kostuemkopf
from effekte.blender.kostuem.kostuemrumpf import Kostuemrumpf
from effekte.blender.kostuem.kostuemschuhe import Kostuemschuhe
from effekte.blender.kostuem.kostuemstab import Kostuemstab
from effekte.blender.kostuem.kostuemutensilien import Kostuemutensilien
from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuem']


class Kostuem:
    def __init__(self, masse, vorn_grad, huelle=None):
        """`huelle`: `Kostuemhuelle` (Umriss der Vorlage) oder None — der Mantel folgt ihr dann."""
        self.m = masse
        self.vorn_grad = vorn_grad
        self.huelle = huelle

    def bauen(self, p):
        teile = Kostuemrumpf(self.m, p, self.vorn_grad, self.huelle).bauen()
        teile += Kostuemkopf(self.m, p, self.vorn_grad, self.huelle).bauen()
        teile += Kostuemstab(self.m, p, self.vorn_grad).bauen()
        teile += Kostuemschuhe(self.m, p, self.vorn_grad).bauen()
        teile += Kostuemutensilien(self.m, p, self.vorn_grad).bauen()
        return teile

    @staticmethod
    def entfernen():
        for obj in [o for o in bpy.data.objects if o.get(Rohr.MARKE)]:
            netz = obj.data
            materialien = list(netz.materials)
            bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.meshes.remove(netz, do_unlink=True)
            for mat in materialien:
                if mat is not None and mat.users == 0:
                    bpy.data.materials.remove(mat, do_unlink=True)
