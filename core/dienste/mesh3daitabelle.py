# -*- coding: utf-8 -*-
"""Mesh3daitabelle — die Jobs der Seite „Mesh3D-AI“ als djangoBase-Tabelle (14.10.2026).

Edgar: „wir werden bei /mesh-3D-AI/ mehrere Jobs außer Ursula haben … eine Hauptansicht mit einer Tabelle so wie bei /mesh-3D/, und dann die Unterjobs wie Ursula1 als Unterseiten“.
Ein Job ist ein Modell, an dem eine KI „Netz → Genesis-Modell“ trainiert wird. Die Zeilen kommen aus `Mesh3daiattrappe.jobs()` (heute ein Job, die Zahlen der Attrappe), die Spalte „Datensatz“ aus der Platte (`Mesh3daidatensatz`, 14.10.2026);
`mesh3dai/mesh3dailiste.js` öffnet auf Klick die Jobseite `/mesh-3D-AI/<job>/`. Gleiche Bauart wie `Mesh3dtabelle`: Spalten, Zeilen mit `data-id`, fertiges HTML je Zeile.
"""

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daidaten import Mesh3daidaten
from .mesh3daidatensatz import Mesh3daidatensatz

__all__ = ['Mesh3daitabelle']


class Mesh3daitabelle:
    SCHLUESSEL = 'mesh3dai'
    SPALTEN = (
        {'label': 'Job', 'key': 'name'},
        {'label': 'Modell', 'key': 'modell', 'titel': 'Das Genesis-Modell, an dem trainiert wird'},
        {'label': 'Proben', 'key': 'proben', 'num': True, 'titel': 'Posen, die die Seite des Jobs zeigt'},
        {'label': 'Training', 'key': 'training', 'num': True, 'titel': 'Davon zum Training'},
        {'label': 'Prüfposen', 'key': 'pruefung', 'num': True, 'titel': 'Davon nie trainiert — daran wird gemessen'},
        {'label': 'Datensatz', 'key': 'datensatz', 'num': True,
         'titel': 'Proben des echten Datensatzes auf der Platte (3DObjects/mesh3dai/<Modell>/proben): fertig gerechnet von geplant. Fertig heißt: eingabe.npz liegt da, das Datenskript schreibt sie zuletzt'},
        {'label': 'Status', 'key': 'status', 'titel': '„Echt (Lauf …)“: Datensatz und Vorhersagen des jüngsten fertigen Trainingslaufs; „Attrappe“: Flächen, Kleider und Ausgabe des Netzes sind erfunden, Posen und Rig echt'},
    )

    def tabelle(self):
        return {'key': self.SCHLUESSEL, 'spalten': list(self.SPALTEN), 'zeilen': [self.zeile(j) for j in Mesh3daidaten.jobs()],
                'klasse': 'auftragstabelle mesh3daitabelle', 'leer': 'Noch kein Job.'}

    @staticmethod
    def adresse(job):
        return '/mesh-3D-AI/%s/' % job['id']

    def zeile(self, job):
        zellen = (
            format_html('<td data-sort="{}"><a href="{}">{}</a></td>', job['name'].lower(), self.adresse(job), job['name']),
            format_html('<td data-sort="{}">{}</td>', job['modell'].lower(), job['modell']),
            self._zahl(job['proben']),
            self._zahl(job['training']),
            self._zahl(job['pruefung']),
            self._datensatz(job['ordner']),
            format_html('<td data-sort="{}">{}</td>', job['status'].lower(), job['status']),
        )
        return {'id': job['id'], 'klasse': 'mesh3dai-zeile-job', 'html': mark_safe(''.join(zellen))}

    @staticmethod
    def _zahl(wert):
        return format_html('<td class="num" data-sort="{}">{}</td>', int(wert), int(wert))

    @staticmethod
    def _datensatz(ordner):
        """„216 von 425" (fertig von geplant); ohne `proben.json` nur die Zahl, ohne Ordner „—". Sortiert wird nach der Zahl der fertigen Proben."""
        z = Mesh3daidatensatz.zaehlen(ordner)
        if z['geplant'] is None and not z['vorhanden']:
            return mark_safe('<td class="num" data-sort="0">—</td>')
        text = '%d von %d' % (z['vorhanden'], z['geplant']) if z['geplant'] else str(z['vorhanden'])
        return format_html('<td class="num" data-sort="{}">{}</td>', z['vorhanden'], text)
