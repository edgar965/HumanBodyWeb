# -*- coding: utf-8 -*-
"""Reglerwirksamkeitstabelle — die Regler der Regler-KI als djangoBase-Tabelle auf Einstellungen → Genesis.

Edgar (27.10.2026): „mach bei http://127.0.0.1:8081/settings/genesis/ die liste der Regler in einer djangoBase Tabelle. Spalten: Wirksamkeit, 3dmesh-ai , 2d-3d-ai . Die letzten
2 Spalten : Empfehlung ob man die in den Pipelines nutzen sollte“.

Liest nur die Ablage `3DObjects/mesh3dai/regler_wirksamkeit_v<Fassung>_<Fingerabdruck des Reglerraums>.json`; gemessen wird sie auf der Karte von
`mesh3dai/mesh3dai_reglerwirksamkeit.py` (nie aus der Seite). Liegen mehrere (anderer Reglerraum), nimmt die Seite die jüngste und sagt es; fehlt jede, bleibt die Tabelle
leer und der Hinweis nennt den Befehl.
"""

import json
from pathlib import Path

from django.conf import settings
from django.utils.html import format_html


class Reglerwirksamkeitstabelle:
    """Baut die Struktur für `djangobase/_tabelle.html` aus der jüngsten Ablage."""

    SCHLUESSEL = 'genesis-regler'
    MUSTER = 'regler_wirksamkeit_v*_*.json'
    BEFEHL = 'python14 mesh3dai/mesh3dai_reglerwirksamkeit.py'
    SPALTEN = (
        {'label': 'Regler', 'key': 'regler', 'titel': 'Anzeigename, darunter der Name im Reglerraum der Regler-KI'},
        {'label': 'Wirksamkeit', 'key': 'wirkung', 'num': True,
         'titel': 'größte Verschiebung eines Punkts der Haut (Körper, Kopf) oder eines Gelenks, wenn der Regler allein am Ende seines Bereichs steht (mm)'},
        {'label': 'Mesh3D-AI', 'key': 'mesh3dai', 'titel': 'Empfehlung: Regler in der Pipeline Mesh3D-AI nutzen (Eingang: Netz, Messlinien entlang der Hautnormale)'},
        {'label': '2d-3d-AI', 'key': 'ai2d3d', 'titel': 'Empfehlung: Regler in der Pipeline 2d-3d-AI nutzen (Eingang: Fotos, Umriss und Gesicht)'},
    )

    def __init__(self, ordner=None):
        self.ordner = Path(ordner) if ordner else Path(settings.OBJECTS_ROOT) / 'mesh3dai'
        self.dateien = sorted(self.ordner.glob(self.MUSTER), key=lambda p: p.stat().st_mtime, reverse=True)
        self.daten = self._lesen(self.dateien[0]) if self.dateien else None

    @staticmethod
    def _lesen(datei):
        with open(datei, encoding='utf-8') as d:
            return json.load(d)

    def tabelle(self):
        zeilen = [self.zeile(z) for z in self.daten['regler']] if self.daten else []
        return {'key': self.SCHLUESSEL, 'spalten': [dict(s) for s in self.SPALTEN], 'zeilen': zeilen, 'klasse': 'genesis-regler',
                'leer': 'Noch nicht gemessen — %s' % self.BEFEHL}

    def kopf(self):
        """Kennzahlen über der Tabelle: Herkunft, Zählungen, Schwellen."""
        if not self.daten:
            return None
        r = self.daten['regler']
        return {'datei': self.dateien[0].name, 'andere': [p.name for p in self.dateien[1:]], 'erzeugt': self.daten['erzeugt'], 'lauf': self.daten['lauf'],
                'pruefformen': self.daten['pruefformen'], 'anzahl': len(r), 'schwellen': self.daten['schwellen'],
                'ohne_wirkung': sum(1 for z in r if z['wirkung_mm'] < self.daten['schwellen']['stumm_mm']), 'doppelt': sum(1 for z in r if 'doppelt' in z),
                'mesh3dai': sum(1 for z in r if z['mesh3dai']['nutzen']), 'ai2d3d': sum(1 for z in r if z['ai2d3d']['nutzen'])}

    def zeile(self, z):
        return {'id': z['name'], 'html': self._regler(z) + self._wirkung(z) + self._empfehlung(z['mesh3dai']) + self._empfehlung(z['ai2d3d'])}

    @staticmethod
    def _regler(z):
        art = z['familie'] + (' · ' + z['bereich'] if z['bereich'] else '')
        return format_html('<td data-sort="{}" title="{} · Bereich {} … {}">{}<br><small class="regler-klein">{}</small></td>',
                           z['anzeige'].lower(), art, Reglerwirksamkeitstabelle._de(z['lo'], 2), Reglerwirksamkeitstabelle._de(z['hi'], 2), z['anzeige'], z['name'])

    @staticmethod
    def _wirkung(z):
        de = Reglerwirksamkeitstabelle._de
        teile = [('Körper', z['koerper_mm']), ('Kopf', z['kopf_mm']), ('Gelenke', z['gelenke_mm']), ('Messlinien Netz', z['netz_mm']), ('Umriss', z['umriss_mm']),
                 ('Gesicht von vorn', z['gesicht_mm'])]
        titel = ' · '.join('%s %s mm' % (n, de(v)) for n, v in teile)
        titel += ' · gesetzt in %d Prüfformen, vorhergesagt in %d' % (z['in_pruefformen'], z['vorhergesagt'])
        if z.get('gedreht'):
            titel += ' · stellt Drehkanäle, die die Formrechnung nicht rechnet'
        zusatz = ''
        if 'doppelt' in z:
            zusatz = format_html('<br><small class="regler-klein">doppelt zu {}</small>', z['doppelt']['anzeige'])
        # Sortierschlüssel in hundertstel mm als ganze Zahl — die djangoBase-Sortierung liest „81.7“ deutsch als 817 (`tests.md`)
        return format_html('<td class="num" data-sort="{}" title="{}">{} mm{}</td>', int(round(z['wirkung_mm'] * 100)), titel, de(z['wirkung_mm']), zusatz)

    @staticmethod
    def _empfehlung(e):
        klasse, text = ('hb-gut', 'nutzen') if e['nutzen'] else ('hb-schlecht', 'weglassen')
        return format_html('<td data-sort="{}"><span class="{}">{}</span><br><small class="regler-klein">{}</small></td>', text, klasse, text, e['grund'])

    @staticmethod
    def _de(x, stellen=1):
        return ('%.*f' % (stellen, x)).replace('.', ',')
