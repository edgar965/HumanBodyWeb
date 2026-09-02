# -*- coding: utf-8 -*-
u"""Niemand greift auf ein Attribut einer Methode zu.

DER ANLASS (01.09.2026)
=======================
In `convert/convertDazPoseBvhToBlender.py` stand::

    Dazretarget.retarget_bvh.register()

`Dazretarget.retarget_bvh` ist eine statische Methode. Eine Funktion hat
kein `register` — der Aufruf waere beim ersten Daz-BVH mit
`AttributeError` gefallen, in Blender, nicht beim Uebersetzen.

Gemeint war das gleichnamige FREMDMODUL `retarget_bvh`. Beim Buendeln
der frueheren Modulfunktionen in eine Klasse hat das Werkzeug jeden
Namen `retarget_bvh` mit der Klasse qualifiziert — auch den Modulnamen,
denn im Syntaxbaum sehen beide gleich aus. Danach galt der `import`
als unbenutzt und fiel dem Aufraeumen zum Opfer.

Weder `test_blender_addon` (laedt jedes Modul) noch `test_addon_namen`
(pyflakes) sehen das: `Dazretarget.retarget_bvh` GIBT es ja, und der
Zugriff steht im Rumpf einer Methode.

WARUM DIE REGEL SCHARF IST
==========================
`Klasse.methode.irgendwas` ist praktisch immer falsch. Was eine Funktion
wirklich traegt (`__name__`, `__doc__`, `__wrapped__`, `fget` …), steht
in `Methodenzugriffe.ECHT` und ist ausgenommen. Beim Einbau gab es
genau einen Treffer, und der war der Fehler.

Das Werkzeug ist mit repariert (`Docu/umbau/funktionsbuendel.py`): Ein
Name, den die Datei importiert, wird nicht mehr qualifiziert, sondern
gemeldet.

BDD - GEGEBEN / DANN
====================
    KeinZugriffAufEineMethode ... kein `Klasse.methode.attribut`
    EineSabotageAmZugriff              ... der erfundene Zugriff wird erkannt
"""
import ast
import unittest

from ._methodenzugriffe import Methodenzugriffe
from ._projektquellen import Projektquellen

#: Die Wurzel, unter der die vier Repos liegen.
#: Wurzel, Baeume und Ausschluesse stehen in `Projektquellen`.
TOOLS = Projektquellen.TOOLS

#: Was eine Funktion wirklich traegt.


class KeinZugriffAufEineMethode(unittest.TestCase):
    u"""Kein Modul liest ein Attribut, das eine Funktion nicht hat."""

    databases = []

    def test_keiner_greift_auf_eine_methode_zu(self):
        gelesen = list(Projektquellen.baeume())
        methoden = Methodenzugriffe.methodennamen(gelesen)
        schlecht = []
        for pfad, baum in gelesen:
            for zeile, ausdruck in Methodenzugriffe.auf_methoden(baum, methoden):
                schlecht.append('%s:%d %s'
                                % (pfad.relative_to(TOOLS).as_posix(),
                                   zeile, ausdruck))
        self.assertEqual(schlecht, [],
                         'Zugriff auf ein Methodenattribut: %s' % schlecht)

    def test_es_werden_ueberhaupt_klassen_gefunden(self):
        u"""Sabotageschutz: Eine leere Menge bestuende jeden Test."""
        namen = Methodenzugriffe.methodennamen(
            list(Projektquellen.baeume()))
        self.assertGreater(len(namen), 150)


class EineSabotageAmZugriff(unittest.TestCase):
    u"""Die Gegenprobe: Der Test muss rot werden koennen."""

    databases = []

    def test_der_echte_fall_wird_erkannt(self):
        u"""Genau die Zeile aus `convertDazPoseBvhToBlender.py`."""
        baum = ast.parse('Dazretarget.retarget_bvh.register()')
        self.assertEqual(
            Methodenzugriffe.auf_methoden(baum, {'Dazretarget': {'retarget_bvh'}}),
            [(1, 'Dazretarget.retarget_bvh.register')])

    def test_ein_gewoehnlicher_aufruf_wird_nicht_gemeldet(self):
        baum = ast.parse('Dazretarget.retarget_bvh(a, b, c)')
        self.assertEqual(
            Methodenzugriffe.auf_methoden(baum, {'Dazretarget': {'retarget_bvh'}}), [])

    def test_ein_echtes_funktionsattribut_ist_erlaubt(self):
        baum = ast.parse('print(Dazretarget.retarget_bvh.__name__)')
        self.assertEqual(
            Methodenzugriffe.auf_methoden(baum, {'Dazretarget': {'retarget_bvh'}}), [])

    def test_ein_modul_gleichen_namens_wird_nicht_verwechselt(self):
        u"""`retarget_bvh.register()` ohne Klasse davor ist in Ordnung."""
        baum = ast.parse('retarget_bvh.register()')
        self.assertEqual(
            Methodenzugriffe.auf_methoden(baum, {'Dazretarget': {'retarget_bvh'}}), [])
