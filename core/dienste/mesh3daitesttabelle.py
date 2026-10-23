# -*- coding: utf-8 -*-
"""Mesh3daitesttabelle — die Tests des Reiters „Test“ auf `/mesh-3D-AI/` als djangoBase-Tabelle (16.10.2026).

Edgar: „darin auch eine Jobliste, aber nur Mesh und Ausgabe“. Eine Zeile je Netz ohne Trainingsdaten (`Mesh3daitest`); ein Klick öffnet `/mesh-3D-AI/test/<kennung>/` mit den Feldern Mesh und Ausgabe.
Gleiche Bauart wie `Mesh3daitabelle`.
"""

from pathlib import Path

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3dailaufzeit import Mesh3dailaufzeit
from .mesh3daitabelle import Mesh3daitabelle
from .mesh3daitest import Mesh3daitest

__all__ = ['Mesh3daitesttabelle']


class Mesh3daitesttabelle:
    SCHLUESSEL = 'mesh3dai-test'
    SPALTEN = (
        {'label': 'Test', 'key': 'name'},
        {'label': 'Mesh', 'key': 'mesh', 'titel': 'Das Netz (Datei) — dasselbe wie im gleichnamigen Auftrag auf /mesh-3D/'},
        {'label': 'Gerechnet', 'key': 'gerechnet'},          # dritte Spalte (Edgar, 18.10.2026: „an dritter Stelle, nach dem Mesh-Namen“)
        {'label': 'Laufzeit', 'key': 'laufzeit', 'num': True,
         'titel': 'Wie lange die Rechnung des gezeigten Ergebnisses gedauert hat — nur gemessene Zeiten (Mesh3dailaufzeit): Vorstufe, Figur bauen, Zerlegung, Kleider des eingestellten Geschlechts; '
                  'die Vorhersage des Formnetzes legt keine Zeit ab. Aufteilung im Tooltip der Zelle'},
        {'label': 'Punkte', 'key': 'punkte', 'num': True, 'titel': 'Punkte des Netzes (die Vorschau der Seite ist auf rund 100.000 Dreiecke verkleinert)'},
        {'label': 'Lauf', 'key': 'lauf', 'titel': 'Das Netz von Mesh3D-AI, das die Ausgabe gerechnet hat'},
        {'label': 'Figur', 'key': 'figur', 'titel': 'Die trainierte Figur der Ausgabe: die mit dem kleinsten Rest der Anpassung (Tests vor dem 16.10.2026 abends: immer Ursula1)'},
        {'label': 'Status', 'key': 'status'},
    )

    def tabelle(self):
        return {'key': self.SCHLUESSEL, 'spalten': list(self.SPALTEN), 'zeilen': [self.zeile(t) for t in Mesh3daitest.alle()],
                'klasse': 'auftragstabelle mesh3daitabelle', 'leer': 'Noch kein Test gerechnet.'}

    @staticmethod
    def adresse(kennung):
        return '/mesh-3D-AI/test/%s/' % kennung

    def zeile(self, t):
        name = str(t.get('name') or t['kennung'])
        quelle = Path(str(t.get('quelle') or ''))
        status = 'Fehler: %s' % t['fehler'] if t.get('fehler') else ('fertig' if t.get('fertig') else 'nicht fertig')
        zellen = (
            format_html('<td data-sort="{}"><a href="{}">{}</a></td>', name.lower(), self.adresse(t['kennung']), name),
            format_html('<td data-sort="{}" title="{}">{}</td>', quelle.name.lower(), str(quelle), quelle.name),
            format_html('<td data-sort="{}">{}</td>', str(t.get('gerechnet') or ''), str(t.get('gerechnet') or '—').replace('T', ' ')),
            Mesh3daitabelle.laufzeit_zelle(self._laufzeit(t)),
            format_html('<td class="num" data-sort="{}">{}</td>', int(t.get('netz_punkte') or 0), '{:,}'.format(int(t.get('netz_punkte') or 0)).replace(',', '.')),
            format_html('<td data-sort="{}">{}</td>', str(t.get('lauf') or ''), str(t.get('lauf') or '—')),
            format_html('<td data-sort="{}">{}</td>', str(t.get('figur') or 'Ursula1'), str(t.get('figur') or 'Ursula1')),
            format_html('<td data-sort="{}">{}</td>', status, status),
        )
        return {'id': t['kennung'], 'klasse': 'mesh3dai-zeile-test', 'html': mark_safe(''.join(zellen))}

    @staticmethod
    def _laufzeit(t):
        if t.get('fehler'):
            return None
        ordner = Mesh3daitest.ordner() / t['kennung']
        return Mesh3dailaufzeit.test(ordner, t.get('geschlecht') or 'weiblich')
