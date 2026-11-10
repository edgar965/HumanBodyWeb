# -*- coding: utf-8 -*-
"""Meshgenesistesttabelle — die Tests des Reiters „Test“ auf `/mesh-genesis/` als djangoBase-Tabelle (16.10.2026).

Edgar: „darin auch eine Jobliste, aber nur Mesh und Ausgabe“. Eine Zeile je Netz ohne Trainingsdaten (`Meshgenesistest`); ein Klick öffnet `/mesh-genesis/test/<kennung>/` mit den Feldern Mesh und Ausgabe.
Gleiche Bauart wie `Meshgenesistabelle`.
"""

from datetime import datetime
from pathlib import Path

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .meshgenesisjobtest import Meshgenesisjobtest
from .meshgenesislaufzeit import Meshgenesislaufzeit
from .meshgenesisrechendatum import Meshgenesisrechendatum
from .meshgenesistabelle import Meshgenesistabelle
from .meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesistesttabelle']


class Meshgenesistesttabelle:
    SCHLUESSEL = 'meshgenesis-test'
    SPALTEN = (
        Meshgenesistabelle.WAHL_SPALTE,
        {'label': 'Test', 'key': 'name'},
        {'label': 'Mesh', 'key': 'mesh', 'titel': 'Das Netz (Datei) — dasselbe wie im gleichnamigen Auftrag auf /mesh-3D/'},
        # dritte Spalte (Edgar, 18.10.2026: „an dritter Stelle, nach dem Mesh-Namen“); Tag und Uhrzeit getrennt, Tag als TT.MM.JJJJ (23.10.2026)
        {'label': 'Gerechnet am', 'key': 'gerechnet',
         'titel': 'Tag der jüngsten Datei, die ein Rechenschritt für diesen Test geschrieben hat — Testlauf, Vorstufe, Form, Zerlegung, Kleider, Kostüm (Meshgenesisrechendatum.test); '
                  'im Tooltip Schritt, Datei und der Testlauf aus test.json. Sortiert nach Tag und Uhrzeit'},
        {'label': 'Uhrzeit', 'key': 'gerechnet_uhrzeit', 'titel': 'Uhrzeit dazu, in Klammern der Schritt; sortiert nach der Tageszeit'},
        {'label': 'Laufzeit', 'key': 'laufzeit', 'num': True,
         'titel': 'Wie lange die Rechnung des gezeigten Ergebnisses gedauert hat — nur gemessene Zeiten (Meshgenesislaufzeit): Vorstufe, Figur bauen, Zerlegung, Kleider des eingestellten Geschlechts; '
                  'die Vorhersage des Formnetzes legt keine Zeit ab. Aufteilung im Tooltip der Zelle'},
        {'label': 'Punkte', 'key': 'punkte', 'num': True, 'titel': 'Punkte des Netzes (die Vorschau der Seite ist auf rund 100.000 Dreiecke verkleinert)'},
        {'label': 'Lauf', 'key': 'lauf', 'titel': 'Das Netz von Mesh-Genesis, das die Ausgabe gerechnet hat'},
        {'label': 'Figur', 'key': 'figur', 'titel': 'Die trainierte Figur der Ausgabe: die mit dem kleinsten Rest der Anpassung (Tests vor dem 16.10.2026 abends: immer Ursula1)'},
        {'label': 'Status', 'key': 'status'},
    )

    def tabelle(self):
        # Tests der Foto-Genesis-Jobs gehören zur Jobseite, nicht in diese Liste (06.11.2026, `Meshgenesisjobtest`).
        job = Meshgenesisjobtest.kennungen()
        return {'key': self.SCHLUESSEL, 'spalten': list(self.SPALTEN), 'zeilen': [self.zeile(t) for t in Meshgenesistest.alle(mit_tripo=True) if t['kennung'] not in job],
                'klasse': 'auftragstabelle meshgenesistabelle', 'leer': 'Noch kein Test gerechnet.'}

    @staticmethod
    def adresse(kennung):
        return '/mesh-genesis/test/%s/' % kennung

    def zeile(self, t):
        name = str(t.get('name') or t['kennung'])
        quelle = Path(str(t.get('quelle') or ''))
        status = 'Fehler: %s' % t['fehler'] if t.get('fehler') else ('fertig' if t.get('fertig') else 'nicht fertig')
        # Tripo-Jobs (mit Genesis-Wahrheit, zugleich Trainingsdaten) öffnen die Seite des Trainingsjobs (`/mesh-genesis/<kennung>/`, gleiche Kennung) — Edgar, 23.10.2026: „Ich will erstmal in den
        # Testjobs die Ergebnisse des Trainingsjobs sehen“; die Testseite bleibt über den kleinen Link dahinter erreichbar.
        ziel = '/mesh-genesis/%s/' % t['kennung'] if t.get('tripo') else self.adresse(t['kennung'])
        # Die KI hat diese Netze im Training gesehen (Formnetz, Zerlegung, Kleider-KI) — ihr Ergebnis misst nicht, was sie an einem fremden Netz kann; das steht in der Zeile (Edgar: „du hast gefaked!!“)
        marke = format_html(' <span class="hb-hinweis" title="{}">· im Training gesehen</span> <a class="hb-hinweis" href="{}">· Testseite</a>',
                            'Tripo-Job: die KI hat dieses Netz im Training gesehen — kein Test für fremde Netze', self.adresse(t['kennung'])) if t.get('tripo') else ''
        zellen = (
            Meshgenesistabelle.wahl_zelle(t['kennung']),
            format_html('<td data-sort="{}"><a href="{}">{}</a>{}</td>', name.lower(), ziel, name, marke),
            format_html('<td data-sort="{}" title="{}">{}</td>', quelle.name.lower(), str(quelle), quelle.name),
            self._gerechnet(t),
            Meshgenesistabelle.laufzeit_zelle(self._laufzeit(t)),
            format_html('<td class="num" data-sort="{}">{}</td>', int(t.get('netz_punkte') or 0), '{:,}'.format(int(t.get('netz_punkte') or 0)).replace(',', '.')),
            format_html('<td data-sort="{}">{}</td>', str(t.get('lauf') or ''), str(t.get('lauf') or '—')),
            format_html('<td data-sort="{}">{}</td>', str(t.get('figur') or 'Ursula1'), str(t.get('figur') or 'Ursula1')),
            format_html('<td data-sort="{}">{}</td>', status, status),
        )
        return {'id': t['kennung'], 'klasse': 'meshgenesis-zeile-test', 'html': mark_safe(''.join(zellen))}

    @classmethod
    def _gerechnet(cls, t):
        """Jüngste Rechnung im Testordner (`Meshgenesisrechendatum.test`), sonst der Testlauf aus `test.json`."""
        lauf = 'Testlauf (test.json): %s' % (str(t.get('gerechnet') or '—').replace('T', ' '))
        letztes = Meshgenesisrechendatum.test(t['kennung'])
        if letztes:
            return Meshgenesistabelle.datum_zellen(letztes['zeit'], 'Zuletzt gerechnet: %s — %s · %s' % (letztes['was'], letztes['datei'], lauf), letztes['was'])
        return Meshgenesistabelle.datum_zellen(cls._zeit(t.get('gerechnet')), lauf, 'Testlauf' if t.get('gerechnet') else '')

    @staticmethod
    def _zeit(text):
        """`test.json` → `gerechnet` („2026-10-23T15:19:48“) als Unix-Zeit; unlesbar oder leer → None."""
        try:
            return datetime.fromisoformat(str(text)).timestamp() if text else None
        except ValueError:
            return None

    @staticmethod
    def _laufzeit(t):
        if t.get('fehler'):
            return None
        ordner = Meshgenesistest.ordner() / t['kennung']
        return Meshgenesislaufzeit.test(ordner, t.get('geschlecht') or 'weiblich')
