# -*- coding: utf-8 -*-
"""Fotogenesistabellen — die vier Tabellen der Liste `/foto-genesis/` als djangoBase-Tabellen (24.10.2026), Reiter für Reiter wie `/mesh-genesis/`.

Edgar: „mach eine Kopie von Dashboard - Mesh3d-AI …“, dann „Ich sagte eine Kopie der Mesh3d-Ai jobs … keine Gerechnet Spalten, keine Jobauswahl zum Löschen usw“. Darum stehen hier die Spalten
VON Mesh-Genesis (die Klassen dort sind die Quelle, nichts abgeschrieben): Jobs (`Fotogenesisjobtabelle`: Exporte mit Wahrheit), Test (`Fotogenesistesttabelle`: echte Fotos), Formtraining und Formvarianten
(`Meshgenesisformtrainingtabelle`, `Meshgenesisformvariantentabelle` — Foto-Genesis hat noch kein Training, also keine Zeilen).
"""

from .fotogenesisjobs import Fotogenesisjobs
from .fotogenesisjobtabelle import Fotogenesisjobtabelle
from .fotogenesistesttabelle import Fotogenesistesttabelle
from .meshgenesisformtrainingtabelle import Meshgenesisformtrainingtabelle
from .meshgenesisformvariantentabelle import Meshgenesisformvariantentabelle

__all__ = ['Fotogenesistabellen']


class Fotogenesistabellen:
    KLASSE = 'auftragstabelle meshgenesistabelle fotogenesistabelle'

    @classmethod
    def alle(cls):
        """Der Kontext der Liste: je Reiter die Tabelle (Schlüssel wie in `meshgenesis_liste.html`)."""
        jobs = Fotogenesisjobs.alle()
        # Ohne die Jobs von Mesh-Genesis (31.10.2026, Edgar: „In dieser Jobliste stehen Jobs drin, die nicht hierhin gehören. Alle Mesh-3D-Jobs NICHT in der Liste!“): ein Export mit
        # Mesh-Genesis-Paar (`paar`, Messlatte A) ist ein Job von Mesh-Genesis und steht dort; seine Seite unter /foto-genesis/<id>/ bleibt erreichbar
        exporte = [j for j in jobs if j['art'] == 'export' and not j.get('paar')]
        tests = [j for j in jobs if j['art'] == 'foto']
        return {
            'tabelle': cls._tabelle(Fotogenesisjobtabelle.SCHLUESSEL, Fotogenesisjobtabelle.spalten(), [Fotogenesisjobtabelle.zeile(j) for j in exporte],
                                    'Noch kein Job: ein Ordner unter 3DObjects/modelsExport mit <Name>.json und vier Fotos wird einer.'),
            'testtabelle': cls._tabelle(Fotogenesistesttabelle.SCHLUESSEL, Fotogenesistesttabelle.spalten(), Fotogenesistesttabelle.zeilen(tests), 'Noch kein Test.'),
            'formtraining': cls._tabelle('fotogenesis-formtraining', Meshgenesisformtrainingtabelle.SPALTEN, [], 'Noch kein Trainingslauf für Foto-Genesis.'),
            'formvarianten': cls._tabelle('fotogenesis-formvarianten', Meshgenesisformvariantentabelle.SPALTEN, [], 'Noch keine Formvariante für Foto-Genesis.'),
        }

    @classmethod
    def _tabelle(cls, schluessel, spalten, zeilen, leer):
        return {'key': schluessel, 'spalten': list(spalten), 'zeilen': zeilen, 'klasse': cls.KLASSE, 'leer': leer}
