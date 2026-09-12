# -*- coding: utf-8 -*-
u"""Der UMA-Klon als Quelle: wo er liegt, was er nach aussen zeigt.

Geteilt von `test_umaabdeckung` (Tabelle gegen die .cs-Dateien) und
`test_umaabdeckung_tabelle` (Gegenstuecke und Proben) — beide brauchen
dieselben Klassen des Ports und denselben Leser fuer den C#-Quelltext.
"""
import re
import sys
from pathlib import Path

from django.conf import settings

# `UMA_Python` liegt seit dem 08.09.2026 unter `Assets/` (Edgar: „alles was
# mit Garments zu tun hat soll direkt A:\3DTools\Assets hier kommen").
sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

from UMA_Python import (Bindung, Einstellungen,               # noqa: E402
                        Glaettung, Kleidungskonformer, Nahtgruppen,
                        Netzgeometrie)
from UMA_Python.abdeckung import Abdeckung                    # noqa: E402


class Umaquelle:
    u"""Der C#-Quelltext des Konformers und die Klassen des Ports."""

    #: Die Klassen, in denen ein Gegenstueck stehen kann.
    KLASSEN = {'Netzgeometrie': Netzgeometrie, 'Glaettung': Glaettung,
               'Nahtgruppen': Nahtgruppen, 'Bindung': Bindung,
               'Einstellungen': Einstellungen,
               'Kleidungskonformer': Kleidungskonformer}

    #: Nur `public`. Das ist die SCHNITTSTELLE — und nur die muss der Port
    #: abdecken. Mit `private static` kamen 18 Hilfsnamen dazu (`Add`,
    #: `Find`, `Union`, `EdgeKey`, `LaplacianPass` …), die im Original
    #: Bausteine EINER Methode sind: UMAs `BuildWeldedVertexGroups` traegt
    #: seine eigene Union-Find-Struktur im Rumpf. Sie einzeln zu fordern
    #: hiesse, die INNERE Bauart nachzubauen statt das Verhalten.
    MUSTER = (
        re.compile(r'\bpublic\s+static\s+[\w\[\]<>,\.]+\s+(\w+)\s*\('),
        re.compile(r'\bpublic\s+(?!class|enum|struct|static)'
                   r'[\w\[\]<>,\.]+\s+(\w+)\s*\('),
        re.compile(r'\bpublic\s+[\w\[\]<>,\.]+\s+(\w+)\s*[=;]'),
    )

    #: Zusaetzlich, wenn auch die privaten Schritte und die Klassennamen
    #: zaehlen sollen. Die Klasse steht drin, weil die Tabelle
    #: `ClothingConformerSpatialIndex` als GANZES fuehrt: Sie ist im Port
    #: kein eigener Baustein, sondern in `cKDTree` aufgegangen — ein
    #: Eintrag ohne Methodennamen, aber mit Vorbild.
    PRIVAT = (
        re.compile(r'\bprivate\s+static\s+[\w\[\]<>,\.]+\s+(\w+)\s*\('),
        re.compile(r'\bclass\s+(\w+)'),
    )

    @staticmethod
    def quellordner():
        u"""Der UMA-Klon, oder `None`."""
        ordner = Path(str(settings.TOOLS_ROOT)).joinpath(*Abdeckung.QUELLORDNER)
        return ordner if ordner.is_dir() else None

    @classmethod
    def mitglieder(cls, text, klasse=None, privat=False):
        u"""Die Namen, die das Original nach aussen zeigt.

        Gelesen wird mit regulaeren Ausdruecken statt mit einem C#-Zerleger:
        Es geht um `public`-Zeilen einer bekannten Form, und ein Zerleger
        fuer C# waere ein zweites Fremdprojekt in dieser Pruefung.
        """
        if klasse:
            teile = text.split('class %s' % klasse)
            if len(teile) < 2:
                return set()
            text = teile[1]
            # bis zur naechsten Klasse auf derselben Ebene
            naechste = re.search(
                r'\n    (?:public |internal )?(?:sealed |static )?'
                r'class \w', text)
            if naechste:
                text = text[:naechste.start()]
        namen = set()
        muster = cls.MUSTER + (cls.PRIVAT if privat else ())
        for eines in muster:
            for treffer in eines.finditer(text):
                namen.add(treffer.group(1))
        return namen
