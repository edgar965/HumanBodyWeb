# -*- coding: utf-8 -*-
u"""Jeder relative Import im Addon zeigt auf eine Datei, die es gibt.

DER ANLASS (01.09.2026)
=======================
`test_blender_addon` laedt jedes Modul und war gruen. Trotzdem standen
vier Importe im Addon, die ins Leere zeigten::

    anim/zwischenspeicher.py:15   from .convert.convertDazPoseBvhToBlender
    ui_teile/zeichnen_garderobe.py:202  from .assetCreator.geometric
    ui_teile/zeichnen_stoff.py:13       from .assetCreator.preview
    ui_teile/zeichnen_stoff.py:181      from .assetCreator.preview

Alle vier stehen IM RUMPF einer Funktion — dort, wo man einen Import
hinschreibt, um einen Ring aufzuloesen. Sie werden erst ausgefuehrt, wenn
jemand die Funktion ruft; das Laden des Moduls faellt darauf nicht
herein. `_get_retarget_func()` haette also erst in Blender gefehlt, beim
Laden einer Daz-Animation.

Entstanden sind sie beim Aufteilen der Monolithen: Eine Datei rutschte
von der Wurzel nach `anim/`, und ein Punkt reicht dann nicht mehr —
`.convert` heisst von dort aus `anim/convert/`, ein Verzeichnis, das es
nie gab. Dieselbe Fehlerklasse wie die `.parent`-Ketten in der
Projektpfade-Regel: falsch, ohne dass etwas rot wird.

DIE LUECKE, DIE DIESE PRUEFUNG SELBST HATTE (01.09.2026)
=========================================================
Geprueft wurde nur der MODULPFAD. Bei `from . import assetCreator` ist
`knoten.module` aber leer — der Pfad ist dann der eigene Ordner, den es
selbstverstaendlich gibt, und der Name dahinter wurde nie angesehen.
Genau so stand in `ui_teile/zeichnen_garderobe.py` ein Import auf
`ui_teile/assetCreator`, ein Paket, das eine Ebene hoeher liegt.

Deshalb gilt jetzt zusaetzlich: Zeigt ein Import auf ein PAKET, muss
jeder importierte Name dort auch zu finden sein — als Untermodul oder
als Name im `__init__.py`. Bei einem Import auf eine .py-Datei bleibt es
beim Pfad; die Namen darin prueft `test_addon_namen` ueber pyflakes.

Ein `__init__.py` mit `from .x import *` wird uebersprungen: Was ein
Sternimport hereinholt, steht nicht im Syntaxbaum.

WARUM STATISCH GEPRUEFT WIRD
============================
Den Rumpf jeder Funktion auszufuehren, um an ihre Importe zu kommen,
hiesse das halbe Addon in Blender zu fahren. Der Syntaxbaum kennt sie
ohne einen einzigen Aufruf — und er sieht sie ALLE, auch die in Zweigen,
die selten laufen.

BDD - GEGEBEN / DANN
====================
    JederRelativeImport ... zeigt auf eine vorhandene Datei
    JederNameAusEinemPaket ... ist dort auch zu finden
    EineSabotageAmImport        ... ein erfundener Pfad wird erkannt
"""
import ast
import unittest

from ._addonimporte import Addonimporte

ADDON = Addonimporte.WURZEL


class JederRelativeImport(unittest.TestCase):
    u"""Kein Import zeigt auf ein Modul, das es nicht gibt."""

    databases = []

    def test_keiner_zeigt_ins_leere(self):
        schlecht = Addonimporte.ins_leere()
        self.assertEqual(schlecht, [], 'Importe ins Leere: %s' % schlecht)

    def test_es_werden_ueberhaupt_importe_geprueft(self):
        u"""Sabotageschutz: Eine leere Menge bestuende jeden Test."""
        self.assertGreater(Addonimporte.anzahl(), 150)


class EineSabotageAmImport(unittest.TestCase):
    u"""Die Gegenprobe: Der Test muss rot werden koennen."""

    databases = []

    @staticmethod
    def _zeigt_auf_etwas(datei, knoten):
        u"""Findet `from …` aus dieser Datei heraus ein Ziel?"""
        pfad = ADDON.joinpath(*datei.split('/'))
        return Addonimporte.gibt_es(Addonimporte.ziel(pfad, knoten))

    @staticmethod
    def _fehlend(datei, knoten):
        pfad = ADDON.joinpath(*datei.split('/'))
        return Addonimporte.fehlende_namen(pfad, knoten)

    def test_ein_erfundener_pfad_wird_erkannt(self):
        knoten = ast.parse('from .gibtesnicht import x').body[0]
        self.assertFalse(self._zeigt_auf_etwas('ui.py', knoten))

    def test_ein_richtiger_pfad_wird_nicht_gemeldet(self):
        knoten = ast.parse('from .ui_teile.zonen import Zonen').body[0]
        self.assertTrue(self._zeigt_auf_etwas('ui.py', knoten))

    def test_eine_ebene_zu_wenig_faellt_auf(self):
        u"""Genau der Fall von `anim/zwischenspeicher.py`."""
        knoten = ast.parse('from .convert.x import y').body[0]
        katalog = 'anim/katalog.py'
        self.assertFalse(self._zeigt_auf_etwas(katalog, knoten))
        zwei = ast.parse('from ..convert.retarget_bvh import y').body[0]
        self.assertTrue(self._zeigt_auf_etwas(katalog, zwei))

    def test_ein_name_der_im_paket_fehlt_wird_erkannt(self):
        u"""Genau der Fall von `ui_teile/zeichnen_garderobe.py`."""
        knoten = ast.parse('from . import assetCreator').body[0]
        self.assertEqual(self._fehlend('ui_teile/ui.py', knoten),
                         ['assetCreator'])

    def test_ein_untermodul_wird_nicht_gemeldet(self):
        knoten = ast.parse('from . import zonen').body[0]
        self.assertEqual(self._fehlend('ui_teile/ui.py', knoten),
                         [])

    def test_namen_aus_einem_modul_werden_hier_nicht_geprueft(self):
        u"""`from .zonen import Zonen` zeigt auf eine Datei, kein Paket."""
        knoten = ast.parse('from .zonen import Zonen, Egal').body[0]
        self.assertEqual(self._fehlend('ui_teile/ui.py', knoten),
                         [])
