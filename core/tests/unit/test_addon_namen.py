# -*- coding: utf-8 -*-
u"""Kein Name im eigenen Code, den es beim Ausfuehren nicht gibt.

DER ANLASS (01.09.2026)
=======================
Beim Aufteilen der Dateien blieben dreimal Namen zurueck, die ihr neues
Modul nicht kennt::

    assetCreator/geometriedaten.py:23   _REGION_BOUNDS
    charakter/charakterdatei.py:61      Koerpermaterial
    ui_teile/zeichnen_garderobe.py:93   wardrobe

Und einmal andersherum: `pinselzeichnung.py` las fuenf Modulvariablen,
die in `brush.py` zurueckgeblieben waren. Alle vier Faelle stehen IM
RUMPF einer Methode. Die Datei parst, das Addon laedt, und der Fehler
kommt erst, wenn jemand die Funktion ruft — bei `_draw_brush_circle`
also erst beim Malen, im GPU-Rueckruf.

`test_blender_addon` (laedt jedes Modul) und `test_addon_importe` (jeder
relative Import zeigt auf eine Datei) sehen das beide nicht. Diese
Pruefung schliesst die Luecke: Sie fragt fuer JEDEN gelesenen Namen, ob
er zu diesem Zeitpunkt ueberhaupt gebunden ist.

Geprueft wird nicht nur das Addon, sondern auch der Kern in
`HumanBody/` — dieselben Umbauten laufen dort, und dort gibt es keinen
Ladetest, der ein fehlendes `bpy` ersetzen muesste.

WARUM PYFLAKES UND NICHT SELBST GEBAUT
======================================
Sichtbarkeitsregeln sind heikel — Verschachtelung, Komprehensionen,
`nonlocal`, `try/except NameError`. Pyflakes kann das seit Jahren.

DIE EINE AUSNAHME, DIE NOETIG IST
=================================
Pyflakes liest Zeichenketten IN Annotationen als Vorwaertsreferenz auf
einen Typ. Blender-Eigenschaften sind aber genau so geschrieben::

    region: bpy.props.EnumProperty(items=[("HEAD", "Head", "")])

Daraus wurden „unbekannte Namen" wie `Head` — 110 Stueck allein hier.
`djangobase.umbau.codequalitaet._annotationsketten` sammelt diese
Beschriftungen ein; die Trennlinie ist scharf: nur Zeichenketten
INNERHALB eines Aufrufs in einer Annotation.

BDD - GEGEBEN / DANN
====================
    JederGeleseneName ... ist an seiner Stelle gebunden
    EineSabotageAmNamen      ... ein erfundener Name wird erkannt
"""
import unittest

from ._namensbindung import Namensbindung
from ._projektquellen import Projektquellen


#: Die Wurzel, unter der die vier Repos liegen.
#: Wurzel, Baeume und Ausschluesse stehen in `Projektquellen` —
#: `test_addon_zugriffe` trug dieselbe Liste ein zweites Mal.
TOOLS = Projektquellen.TOOLS


class JederGeleseneName(unittest.TestCase):
    u"""Kein Modul liest einen Namen, den es nicht gibt."""

    databases = []

    def test_keiner_ist_unbekannt(self):
        schlecht = []
        for pfad in Projektquellen.dateien():
            quelle = pfad.read_text(encoding='utf-8', errors='replace')
            try:
                treffer = Namensbindung.unbekannte(quelle, str(pfad))
            # stumm gewollt: Eine Datei, die sich nicht zerlegen laesst,
            # meldet `test_escape_sequenzen` — hier waere es dieselbe
            # Meldung ein zweites Mal.
            except SyntaxError:
                continue
            for zeile, name in treffer:
                schlecht.append('%s:%d %s'
                                % (pfad.relative_to(TOOLS).as_posix(),
                                   zeile, name))
        self.assertEqual(schlecht, [], 'Unbekannte Namen: %s' % schlecht)

    def test_es_werden_ueberhaupt_dateien_geprueft(self):
        u"""Sabotageschutz: Eine leere Menge bestuende jeden Test."""
        self.assertGreater(len(list(Projektquellen.dateien())), 180)


class EineSabotageAmNamen(unittest.TestCase):
    u"""Die Gegenprobe: Der Test muss rot werden koennen."""

    databases = []

    def test_ein_erfundener_name_wird_erkannt(self):
        quelle = 'def f():\n    return _gibtesnicht\n'
        self.assertEqual(Namensbindung.unbekannte(quelle, 'probe.py'),
                         [(2, '_gibtesnicht')])

    def test_ein_gebundener_name_wird_nicht_gemeldet(self):
        quelle = '_da = 1\n\n\ndef f():\n    return _da\n'
        self.assertEqual(Namensbindung.unbekannte(quelle, 'probe.py'), [])

    def test_eine_blender_beschriftung_ist_kein_name(self):
        u"""Ohne diese Ausnahme meldete die Pruefung 110 Fehlalarme."""
        quelle = ('from bpy.props import EnumProperty\n\n\n'
                  'class P:\n'
                  '    region: EnumProperty(items=[("HEAD", "Head", "")])\n')
        self.assertEqual(Namensbindung.unbekannte(quelle, 'probe.py'), [])

    def test_der_aufruf_in_der_annotation_wird_sehr_wohl_geprueft(self):
        u"""Ausgenommen sind die BESCHRIFTUNGEN, nicht die ganze Zeile."""
        quelle = ('class P:\n'
                  '    region: EnumProperty(items=[("HEAD", "Head", "")])\n')
        self.assertEqual(Namensbindung.unbekannte(quelle, 'probe.py'),
                         [(2, 'EnumProperty')])
