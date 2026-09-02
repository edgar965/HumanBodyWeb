# -*- coding: utf-8 -*-
u"""Das Blender-Addon laedt — und meldet an, was es anmelden soll.

DER ANLASS (01.09.2026)
=======================
`HumanBodyBlender` hatte keinen einzigen Test. Der Grund klingt
zwingend: Der Code braucht `bpy`, und Blender zu starten ist in diesem
Projekt unerwuenscht. Also blieben 11.788 eigene Zeilen ungeprueft —
darunter `cloth_builder.py` (2.254 Zeilen), `ui.py` (2.194) und
`animation.py` (1.745).

Der Schluss war falsch. Ein Addon laesst sich sehr wohl laden, wenn man
Blenders Module nachbildet (`blenderattrappe.py`), und dabei faellt
genau die Fehlerklasse auf, die ein Umbau erzeugt: ein Import, der ins
Leere zeigt, ein Name, den es auf Modulebene nicht mehr gibt, eine
Klasse, die beim Aufteilen aus einem `classes`-Tupel gefallen ist.

WAS DIESER TEST NICHT IST
=========================
Er ersetzt keinen Blender-Lauf. Ob ein Operator in einer echten Szene
das Richtige tut, sagt er nicht — er sagt, dass das Addon vollstaendig
und in sich stimmig ist.

Was das Addon danach TUT — geteilter Anzeigezustand, Projektpfade,
erzeugte Panels — steht in `test_blender_zustand.py`; die Basis mit den
Suchpfaden in `_addonbasis.Addonbasis`.

BDD - GEGEBEN / DANN
====================
    JedesEigeneModul ... laesst sich einzeln laden
    DieAnmeldung     ... meldet 93 Klassen an und wieder ab
    DieAttrappe      ... faellt auf, wenn ein Name fehlt
"""
import importlib
import sys
import unittest

from ._addonbasis import Addonbasis
from .blenderattrappe import Blenderattrappe


class JedesEigeneModul(Addonbasis):
    u"""Jede Datei des Addons laesst sich laden."""

    def test_alle_module_laden(self):
        with Blenderattrappe():
            schlecht = []
            for name in self.eigene_module():
                try:
                    importlib.import_module(name)
                except Exception as fehler:      # noqa: BLE001
                    schlecht.append('%s — %s: %s'
                                    % (name, type(fehler).__name__, fehler))
        self.assertEqual(schlecht, [], 'Module laden nicht: %s' % schlecht)

    def test_es_sind_ueberhaupt_welche_da(self):
        u"""Sabotageschutz: Eine leere Liste bestuende jeden Test."""
        self.assertGreaterEqual(len(self.eigene_module()), 15)


class DieAnmeldung(Addonbasis):
    u"""``register()`` meldet jede Klasse an, ``unregister()`` alle ab."""

    def anmelden(self):
        with Blenderattrappe() as attrappe:
            addon = importlib.import_module('HumanBodyBlender')
            addon.register()
            angemeldet = list(attrappe.angemeldet)
            addon.unregister()
            return angemeldet, list(attrappe.angemeldet)

    def test_die_erwartete_zahl(self):
        angemeldet, _uebrig = self.anmelden()
        self.assertEqual(len(angemeldet), self.KLASSEN)

    def test_nach_dem_abmelden_bleibt_nichts(self):
        _angemeldet, uebrig = self.anmelden()
        self.assertEqual(uebrig, [])

    def test_keine_klasse_doppelt(self):
        u"""Ein Name in zwei ``classes``-Tupeln ist ein Fehler.

        Blender wirft beim zweiten ``register_class`` desselben Namens;
        beim Aufteilen einer Datei passiert das schnell.
        """
        angemeldet, _uebrig = self.anmelden()
        doppelt = {n for n in angemeldet if angemeldet.count(n) > 1}
        self.assertEqual(doppelt, set())


class DieAttrappe(Addonbasis):
    u"""Die Gegenprobe: Der Test muss rot werden koennen."""

    def test_ein_fehlender_name_faellt_auf(self):
        u"""Sabotage — ein Modul, das einen Namen einfuehrt, den es nicht gibt."""
        with Blenderattrappe():
            with self.assertRaises(ImportError):
                exec('from HumanBodyBlender.morphing import GibtEsNicht',
                     {})

    def test_sie_raeumt_sys_modules_wieder_auf(self):
        u"""Sonst sieht der naechste Test im Lauf ein halbes Blender."""
        vorher = 'bpy' in sys.modules
        with Blenderattrappe():
            self.assertIn('bpy', sys.modules)
        self.assertEqual('bpy' in sys.modules, vorher)
