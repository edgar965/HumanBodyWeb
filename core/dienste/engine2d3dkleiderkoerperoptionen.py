# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkoerperoptionen — die Gruppe `koerper` der Optionen von „2D3D Kleider": woher die Figur kommt.

Dieselbe Katalogform wie `Iterationsoptionen`. `quelle` entscheidet den Schritt „koerper" (`Engine2d3dKleiderkoerper`):
`uebernehmen` nimmt den fertigen Fit eines Auftrags „Mesh to 3D" (`auftrag` = seine Kennung), `rechnen` rechnet
die Kette auf dem Netz dieses Auftrags. Die Feinheiten der Kette (Runden, Dämpfung, Eigenmorph …) sind die
Vorgaben von `Meshfiguroptionen`.
"""

import re

__all__ = ['Engine2d3dKleiderkoerperoptionen']


class Engine2d3dKleiderkoerperoptionen:
    KENNUNG = re.compile(r'^\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2}$')
    KATALOG = [
        {
            'schluessel': 'quelle',
            'titel': 'Figur',
            'art': 'wahl',
            'vorgabe': 'uebernehmen',
            'werte': [
                ('uebernehmen', 'Aus einem fertigen Auftrag „Mesh to 3D" übernehmen (Sekunden)'),
                ('rechnen', 'Auf dem Netz dieses Auftrags rechnen — die Kette von „Mesh to 3D" (~15 min Grafikkarte)'),
            ],
            'hinweis': 'Übernehmen: Reglerstellung, Eigenmorph, Kacheln und das Netz des Fits als 3D-Bezug der '
                       'Iterationen.',
        },
        {
            'schluessel': 'auftrag',
            'titel': 'Auftrag „Mesh to 3D" (Kennung)',
            'art': 'text',
            'vorgabe': '',
            'hinweis': 'Die Kennung der Seite, etwa 2026.09.29.15.42.36 — nur bei „übernehmen".',
        },
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def katalog(cls):
        aus = []
        for e in cls.KATALOG:
            werte = [{'wert': w, 'text': t} for w, t in e.get('werte', [])]
            aus.append(dict(e, werte=werte, fein=False))
        return {'optionen': aus}

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        wert = roh.get('quelle')
        if wert in ('uebernehmen', 'rechnen'):
            aus['quelle'] = wert
        auftrag = str(roh.get('auftrag') or '').strip()
        if cls.KENNUNG.match(auftrag):
            aus['auftrag'] = auftrag
        if aus['quelle'] == 'uebernehmen' and not aus['auftrag']:
            aus['quelle'] = 'rechnen'       # ohne Kennung scheitert „übernehmen" immer (01.10.2026: neuer Auftrag)
        return aus
