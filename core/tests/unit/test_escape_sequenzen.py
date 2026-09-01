# -*- coding: utf-8 -*-
u"""Kein Backslash, den Python spaeter anders liest.

DER ANLASS (01.09.2026)
=======================
In einem Docstring stand ein Windows-Pfad::

    A:\\3DTools\\python14\\Scripts\\python.exe Docu/pruefe_zuordnungstabellen.py

`\\p` ist keine Escape-Sequenz. Python laesst sie heute durch und warnt;
kuenftige Fassungen werden daraus einen SyntaxError machen. Bis dahin
ist der Text still falsch — `\\3` etwa wird schon jetzt als
Oktalzeichen gelesen, nicht als Backslash-Drei.

Gefunden werden solche Stellen nur beim Uebersetzen mit eingeschalteten
Warnungen. Weder `pyflakes` noch `pycodestyle` melden sie, und im
Normalbetrieb sieht sie niemand: Ein Docstring wird nie ausgefuehrt.

DER FUND: 21 Stellen im eigenen Code, alle in Docstrings mit
Windows-Pfaden. Behoben durch Vorwaertsschraegstriche — die funktionieren
unter Windows genauso und brauchen kein Rohtext-Praefix.

BDD - GEGEBEN / DANN
====================
    JedeEigeneDatei   ... uebersetzt ohne SyntaxWarning
    EineSabotage      ... eine erfundene Sequenz wird erkannt
"""
import unittest
import warnings
from pathlib import Path

#: Die Wurzel ueber allen Repos.
TOOLS = Path(__file__).resolve().parents[4]

#: Die Baeume mit eigenem Code. `tools/` und `VideoToBVH/` bleiben
#: aussen vor: Dort liegen eingelagerte Fremdprojekte (MB-Lab, GVHMR,
#: WHAM, MocapNET) — deren Warnungen gehen dieses Projekt nichts an.
BAEUME = ('HumanBody/humanbody_core', 'HumanBody/assetCreator',
          'HumanBody/collision', 'HumanBody/PhotoToTexture',
          'HumanBodyWeb/core', 'HumanBodyWeb/ui', 'Docu')

#: Ordner ohne eigenen Quelltext oder mit fremdem.
AUS = ('__pycache__', 'convert', 'kbs_retarget', 'node_modules',
       'TestCharakter', 'alt', 'migrations')


def dateien():
    u"""Alle eigenen Python-Dateien der geprueften Baeume."""
    for baum in BAEUME:
        wurzel = TOOLS / baum
        if not wurzel.is_dir():
            continue
        for pfad in sorted(wurzel.rglob('*.py')):
            if not set(pfad.parts) & set(AUS):
                yield pfad


def warnungen(quelle, name):
    u"""[(Zeile, Meldung)] — die SyntaxWarnings beim Uebersetzen."""
    with warnings.catch_warnings(record=True) as gefangen:
        warnings.simplefilter('always')
        compile(quelle, name, 'exec')
        return [(w.lineno, str(w.message)) for w in gefangen
                if issubclass(w.category, SyntaxWarning)]


class JedeEigeneDatei(unittest.TestCase):
    u"""Keine Datei traegt eine ungueltige Escape-Sequenz."""

    databases = []

    def test_kein_syntaxwarning(self):
        schlecht = []
        for pfad in dateien():
            quelle = pfad.read_text(encoding='utf-8', errors='replace')
            for zeile, meldung in warnungen(quelle, str(pfad)):
                schlecht.append('%s:%s %s' % (pfad.name, zeile, meldung))
        self.assertEqual(schlecht, [], 'Ungueltige Sequenzen: %s' % schlecht)

    def test_es_werden_ueberhaupt_dateien_geprueft(self):
        u"""Sabotageschutz: Eine leere Menge bestuende jeden Test."""
        self.assertGreater(len(list(dateien())), 200)


class EineSabotage(unittest.TestCase):
    u"""Die Gegenprobe: Der Test muss rot werden koennen."""

    databases = []

    def test_eine_erfundene_sequenz_wird_erkannt(self):
        quelle = 'u"""Pfad: A:%s3DTools%spython14"""%s' % (
            chr(92), chr(92), chr(10))
        self.assertTrue(warnungen(quelle, 'probe.py'))

    def test_ein_rohtext_ist_in_ordnung(self):
        u"""Ein Rohtext (r-Praefix) ist der andere richtige Weg."""
        quelle = 'r%s%s%sPfad: A:%s3DTools%s%s%s%s' % (
            chr(34), chr(34), chr(34), chr(92),
            chr(34), chr(34), chr(34), chr(10))
        self.assertEqual(warnungen(quelle, 'probe.py'), [])
