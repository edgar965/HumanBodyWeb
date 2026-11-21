# -*- coding: utf-8 -*-
"""Kleidregelnkatalog — Methoden und Kleidungsregeln für `/settings/kleider/` (21.11.2026, Edgar: „die Kleidungsregeln sollen auswählbar sein unter … Einstellungen – Kleider, für alle
Pipelines“ und „mach nochmal eine klare Tabelle und Erklärungen … zu den Methoden: Eigen, Drapieren, Kostüm, Bibliothek usw. mit allen offenen Punkten“).

Liest `meshgenesis/kleidregeln.json` (der Katalog, den auch die Kette liest: `meshgenesis/meshgenesis_kleidregeln.py`) und `meshgenesis/kleidmethoden.json` (die Übersicht). Die Wahl der
Regeln liegt in `AppSettings.ui_prefs` unter `kleider_regel_<Kennung>` = '1' / '0' (wie die übrigen Schalter der Seite); ohne Eintrag gilt die Voreinstellung `wie_bisher`.
STAND (21.11.2026): `Kleidregelnaufloesung` schreibt die Wahl bei jedem Start einer Rechnung in `einstellung.json` des Tests; der Schritt „kleidregeln“ der Kette
(`meshgenesis/meshgenesis_kleidstufe.py`) setzt `fetzen`, `rand_glatt` und `rock` in allen drei Wegen durch (Konzept Abschnitt 10, Stufen 2 bis 4). Die anderen Schalter ändern kein Ergebnis.
"""

import json
from pathlib import Path

from django.conf import settings

__all__ = ['Kleidregelnkatalog']


class Kleidregelnkatalog:
    PRAEFIX = 'kleider_regel_'
    VORGABE = 'wie_bisher'
    #: Text zum Stand je Weg (Schlüssel `wege` der Regeln); „herauszuloesen“: in einem anderen Weg gebaut, hier noch nicht
    STAND = {'gebaut': 'läuft', 'teilweise': 'teilweise', 'herauszuloesen': 'nur in anderem Weg', 'neu': 'nicht gebaut', 'nicht_gemessen': 'nicht gemessen'}
    WEGE = (('z', 'Bibliothek'), ('e', 'Eigen'), ('f', 'Drapieren'))

    @staticmethod
    def _laden(name):
        return json.loads((Path(settings.TOOLS_ROOT) / 'meshgenesis' / name).read_text(encoding='utf-8'))

    @classmethod
    def schluessel(cls, kennung):
        """Schlüssel in `ui_prefs` zur Regel `kennung`."""
        return cls.PRAEFIX + kennung

    @classmethod
    def regeln(cls, prefs):
        """Regeln des Katalogs für die Seite: Liste von Gruppen {'name', 'regeln': [{kennung, schluessel, nr, name, text, an, wege: [(Weg, Stand-Text, Stand)], messung}]}."""
        katalog = cls._laden('kleidregeln.json')
        vorgabe = next(v['regeln'] for v in katalog['voreinstellungen'] if v['kennung'] == cls.VORGABE)
        gruppen, nr = [], 0
        for g in katalog['gruppen']:
            zeilen = []
            for r in katalog['regeln']:
                if r['gruppe'] != g['kennung']:
                    continue
                nr += 1
                wert = prefs.get(cls.schluessel(r['kennung']))
                an = (r['kennung'] in vorgabe) if wert is None else str(wert) in ('1', 'True', 'true')
                zeilen.append(dict(r, nr=nr, schluessel=cls.schluessel(r['kennung']), an=an,
                                   wege=[(name, cls.STAND[r['wege'][weg]], r['wege'][weg]) for weg, name in cls.WEGE]))
            gruppen.append({'name': g['name'], 'regeln': zeilen})
        return gruppen

    @classmethod
    def voreinstellungen(cls):
        """Voreinstellungen {kennung, name, text, regeln als JSON-Liste} und alle Kennungen (für die Knöpfe)."""
        katalog = cls._laden('kleidregeln.json')
        return [dict(v, json=json.dumps(v['regeln'])) for v in katalog['voreinstellungen']], json.dumps([r['kennung'] for r in katalog['regeln']])

    @classmethod
    def methoden(cls):
        """Übersicht der Methoden: (Stand-Datum, Liste Gruppen {'name', 'text', 'methoden': [...]})."""
        daten = cls._laden('kleidmethoden.json')
        return daten['stand'], [dict(g, methoden=[m for m in daten['methoden'] if m['gruppe'] == g['kennung']]) for g in daten['gruppen']]
