# -*- coding: utf-8 -*-
u"""Garmentcodemessung — die Testlaeufe fuer die Hilfeseite lesen.

Die Messreihen liegen als YAML neben den Bildern, die sie belegen:

    GarmentCode/test/HumanBody_local/   5 HumanBody-Figuren x 15 Stuecke
    GarmentCode/test/SMPL_local/        6 SMPL-Koerper x 15 Stuecke
    GarmentCode/test/SMPL_Online/       was garmentcode.ethz.ch liefert

Gelesen wird bei jedem Seitenaufruf frisch. Ein Zwischenspeicher waere hier
falsch: Die Dateien entstehen aus Messlaeufen, und eine Hilfeseite, die
gestrige Zahlen zeigt, ist schlimmer als eine leere — dieselbe Lehre wie
bei der Fehlerseite, die alte Fehler zeigte (`log_sources`, 30.08.2026).

Fehlt eine Datei, steht das in der Antwort. Nicht `{}` zurueckgeben: Eine
leere Tabelle sieht aus wie „nichts gefunden", nicht wie „nie gemessen".
"""

import logging
import os

import yaml
from django.conf import settings

logger = logging.getLogger('core')


class Garmentcodemessung:
    u"""Zugang zu den abgelegten Messreihen."""

    #: Wo die Messreihen liegen — unter `Assets/GarmentCode/test/`
    #: (bis zum 07.09.2026 `HumanBody/GarmentCode/test/`).
    UNTERORDNER = ('GarmentCode', 'test')

    #: Die Reihen, die die Hilfeseite zeigt.
    REIHEN = {
        'humanbody': ('HumanBody_local', 'messung_alle_stuecke.yaml'),
        'smpl': ('SMPL_local', 'messung_durchstich_stoff.yaml'),
        'koerper': ('HumanBody_local', 'koerper.yaml'),
    }

    @classmethod
    def wurzel(cls):
        return os.path.join(str(settings.ASSETS_ROOT), *cls.UNTERORDNER)

    @classmethod
    def pfad(cls, reihe):
        ordner, datei = cls.REIHEN[reihe]
        return os.path.join(cls.wurzel(), ordner, datei)

    @classmethod
    def lesen(cls, reihe):
        u"""dict der Reihe — oder `None`, wenn die Datei fehlt."""
        pfad = cls.pfad(reihe)
        if not os.path.isfile(pfad):
            logger.info('GarmentCode-Messung fehlt: %s', pfad)
            return None
        try:
            with open(pfad, 'r', encoding='utf-8') as quelle:
                return yaml.safe_load(quelle) or {}
        except Exception:
            logger.exception('GarmentCode-Messung unlesbar: %s', pfad)
            return None

    # --------------------------------------------------------------- Aufbereiten

    @classmethod
    def matrix(cls, reihe='humanbody'):
        u"""Die Messreihe als Tabelle: Zeilen = Stuecke, Spalten = Koerper.

        Rueckgabe:
            {'koerper': [...], 'zeilen': [{'stueck', 'zellen': [...]}],
             'anzahl', 'gelungen', 'fehlgeschlagen', 'quelle'}
        oder None, wenn die Datei fehlt.
        """
        daten = cls.lesen(reihe)
        if daten is None:
            return None
        koerper, stuecke = [], []
        for schluessel in daten:
            wer, was = schluessel.split('/', 1)
            if wer not in koerper:
                koerper.append(wer)
            if was not in stuecke:
                stuecke.append(was)
        koerper.sort()
        stuecke.sort()

        zeilen = []
        for stueck in stuecke:
            zellen = []
            for wer in koerper:
                werte = daten.get('%s/%s' % (wer, stueck))
                zellen.append(cls._zelle(werte))
            zeilen.append({'stueck': stueck, 'zellen': zellen})

        gelungen = [v for v in daten.values() if 'fehler' not in v]
        return {
            'koerper': koerper,
            'zeilen': zeilen,
            'anzahl': len(daten),
            'gelungen': len(gelungen),
            'fehlgeschlagen': len(daten) - len(gelungen),
            'quelle': cls.pfad(reihe),
            'kennzahlen': cls._kennzahlen(gelungen),
        }

    @classmethod
    def _zelle(cls, werte):
        u"""Eine Tabellenzelle: Wert, Zustand, Titel fuer den Mauszeiger."""
        if not werte:
            return {'text': '–', 'zustand': 'leer', 'titel': 'nicht gemessen'}
        if 'fehler' in werte:
            return {'text': 'Fehler', 'zustand': 'fehler',
                    'titel': werte['fehler']}
        wert = werte.get('durchstich_prozent', 0.0)
        zustand = 'gut' if wert < 0.5 else ('warnung' if wert < 2 else 'fehler')
        titel = ('Durchstich %s %% (roh %s %%), Hautabstand %s mm, '
                 'Knick %s %%, %.0f s'
                 % (cls._zahl(wert),
                    cls._zahl(werte.get('durchstich_roh_prozent', 0.0)),
                    cls._zahl(werte.get('haut_median_mm', 0.0), 1),
                    cls._zahl(werte.get('knick_prozent', 0.0)),
                    werte.get('sekunden', 0.0)))
        return {'text': cls._zahl(wert), 'zustand': zustand, 'titel': titel}

    @staticmethod
    def _zahl(wert, stellen=2):
        u"""Deutsche Schreibweise — Komma, kein Punkt.

        Djangos Lokalisierung greift hier nicht: Die Werte werden als
        Zeichenkette in die Vorlage gegeben, damit die Zellenfarbe am
        Zahlenwert haengt und nicht am Format.
        """
        return ('%.*f' % (stellen, float(wert))).replace('.', ',')

    @staticmethod
    def _kennzahlen(gelungen):
        u"""Median und Maximum der drei Groessen — oder leer."""
        if not gelungen:
            return {}
        import statistics as st

        def werte(name):
            return [float(v[name]) for v in gelungen if name in v]

        aus = {}
        for name, marke, stellen in (('durchstich_prozent', 'durchstich', 2),
                                     ('durchstich_roh_prozent', 'durchstich_roh', 2),
                                     ('haut_median_mm', 'haut', 1),
                                     ('knick_prozent', 'knick', 2),
                                     # Sekunden auf ganze Zahlen: Eine
                                     # Simulation, die 22,05 s meldet,
                                     # taeuscht eine Genauigkeit vor, die
                                     # sie bei Tageslast nicht hat.
                                     ('sekunden', 'zeit', 0)):
            liste = werte(name)
            if liste:
                aus[marke] = {
                    'median': Garmentcodemessung._zahl(st.median(liste), stellen),
                    'max': Garmentcodemessung._zahl(max(liste), stellen),
                }
        return aus

    @classmethod
    def koerper(cls):
        u"""Die Steckbriefe der fuenf HumanBody-Testfiguren."""
        daten = cls.lesen('koerper')
        if not daten:
            return []
        aus = []
        for schluessel in sorted(daten):
            eintrag = dict(daten[schluessel])
            eintrag['schluessel'] = schluessel
            eintrag['meta_text'] = ', '.join(
                '%s %+.2f' % (name, wert)
                for name, wert in sorted((eintrag.get('meta') or {}).items())
            ) or 'keine Regler'
            aus.append(eintrag)
        return aus
