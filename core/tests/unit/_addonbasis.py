# -*- coding: utf-8 -*-
u"""Addonbasis — die Pfade, die Blender dem Addon gibt, und seine Module.

Blender legt beim Laden eines Addons dessen Elternordner in den
Suchpfad. Hier gibt es kein Blender, also muss der Testfall das selbst
tun — sonst findet `import HumanBodyBlender.ui` nichts, und der Fehler
sieht aus wie ein kaputtes Addon.

FREMDCODE BLEIBT AUSSEN VOR
===========================
`convert/retarget_bvh` (Thomas Larsson, GPL-2.0-or-later) und
`kbs_retarget` (KBS DEV, GPL-3) sind fremde Addons — 25.143 der 36.931
Zeilen. Sie werden aktualisiert; ihre Befunde gehen dieses Projekt
nichts an.

Herausgeloest am 02.09.2026: `test_blender_addon.py` war auf 331 Zeilen
gewachsen und traegt seither nur noch das Laden und die Anmeldung; der
geteilte Zustand, die Projektpfade und die Panels stehen in
`test_blender_zustand.py`. Beide brauchen diese Basis.
"""
import sys
import unittest

from ._projektquellen import Projektquellen

__all__ = ['Addonbasis']

#: Die Wurzel, unter der die vier Repos liegen, und der Addonordner.
TOOLS = Projektquellen.TOOLS
ADDON = Projektquellen.ADDON


class Addonbasis(unittest.TestCase):
    u"""Legt die Pfade so, wie Blender sie dem Addon gibt."""

    databases = []

    #: Fremde Addons — Urheber siehe Kopf.
    FREMD = ('convert', 'kbs_retarget')

    #: Kein Quelltext.
    KEIN_CODE = ('data', 'cache', '__pycache__')

    #: So viele Klassen meldet `register()` an. Die Zahl steht hier,
    #: damit eine verschwundene Klasse auffaellt statt stillschweigend zu
    #: fehlen — sie zu aendern ist eine bewusste Entscheidung, kein
    #: Nebeneffekt.
    KLASSEN = 93

    @classmethod
    def setUpClass(cls):
        for pfad in (TOOLS, TOOLS / 'HumanBody'):
            if str(pfad) not in sys.path:
                sys.path.insert(0, str(pfad))

    @classmethod
    def eigene_module(cls):
        u"""Die Modulnamen des eigenen Addon-Codes, ohne Fremdbestand."""
        namen = []
        for pfad in sorted(ADDON.rglob('*.py')):
            teile = pfad.relative_to(ADDON).parts
            if teile[0] in cls.FREMD or set(teile) & set(cls.KEIN_CODE):
                continue
            if pfad.name == '__init__.py':
                teile = teile[:-1]
            else:
                teile = teile[:-1] + (pfad.stem,)
            namen.append('.'.join(('HumanBodyBlender',) + teile))
        return namen
