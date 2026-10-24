# -*- coding: utf-8 -*-
"""Mesh3daitabelle — die Jobs der Seite „Mesh3D-AI“ als djangoBase-Tabelle (14.10.2026).

Edgar: „wir werden bei /mesh-3D-AI/ mehrere Jobs außer Ursula haben … eine Hauptansicht mit einer Tabelle so wie bei /mesh-3D/, und dann die Unterjobs wie Ursula1 als Unterseiten“.
Ein Job ist ein Modell, an dem eine KI „Netz → Genesis-Modell“ trainiert wird. Die Zeilen kommen aus `Mesh3daiattrappe.jobs()` (heute ein Job, die Zahlen der Attrappe), die Spalte „Datensatz“ aus der Platte (`Mesh3daidatensatz`, 14.10.2026);
`mesh3dai/mesh3dailiste.js` öffnet auf Klick die Jobseite `/mesh-3D-AI/<job>/`. Gleiche Bauart wie `Mesh3dtabelle`: Spalten, Zeilen mit `data-id`, fertiges HTML je Zeile.
"""

import json
from datetime import datetime

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daidaten import Mesh3daidaten
from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3dailaufzeit import Mesh3dailaufzeit
from .mesh3daipaare import Mesh3daipaare
from .mesh3dairechendatum import Mesh3dairechendatum
from .mesh3daitrainingsdatum import Mesh3daitrainingsdatum

__all__ = ['Mesh3daitabelle']


class Mesh3daitabelle:
    SCHLUESSEL = 'mesh3dai'
    #: Auswahl zum Löschen (23.10.2026, `Mesh3daipapierkorb`, `mesh3dailoeschen.js`) — auch in `Mesh3daitesttabelle`
    WAHL_SPALTE = {'label': '<input type="checkbox" class="mesh3dai-alle" title="alle auswählen / Auswahl aufheben">', 'key': 'wahl', 'sortAus': True}
    SPALTEN = (
        WAHL_SPALTE,
        {'label': 'Job', 'key': 'name'},
        {'label': 'Modell', 'key': 'modell', 'titel': 'Das Genesis-Modell, an dem trainiert wird'},
        {'label': 'Zuletzt trainiert', 'key': 'trainiert',
         'titel': 'Ende des jüngsten fertigen Trainings an den Daten dieses Jobs (Zeit von lauf_ergebnis.json): Läufe des Jobs (_laeufe) und gemeinsame Netze der Vorstufe/Form (_vorstufe/laeufe), '
                  'die den Job in ihren Trainingsdaten nennen; Probeläufe zählen nicht. Der Name des Laufs steht im Tooltip der Zelle'},
        {'label': 'Gerechnet am', 'key': 'gerechnet',
         'titel': 'Tag der jüngsten Datei, die ein Rechenschritt für diesen Job geschrieben hat — Training, Datensatz, Vorstufe, Form, Ergebnisfigur, Zerlegung, Kleider, künstliche Tripo-Netze '
                  '(Mesh3dairechendatum). Im Tooltip Schritt und Datei. Einstellungen und Namen zählen nicht; sortiert nach Tag und Uhrzeit'},
        {'label': 'Uhrzeit', 'key': 'gerechnet_uhrzeit', 'titel': 'Uhrzeit dazu, in Klammern der Schritt; sortiert nach der Tageszeit'},
        {'label': 'Laufzeit', 'key': 'laufzeit', 'num': True,
         'titel': 'Wie lange die Rechnung gedauert hat, deren Ergebnis die Jobseite zeigt — nur gemessene Zeiten (Mesh3dailaufzeit): beim Grundjob das Training aus „Zuletzt trainiert“ (dauer_s), '
                  'beim Tripo-Job die Kette seines Tests (Vorstufe, Figur bauen, Zerlegung, Kleider). Aufteilung im Tooltip der Zelle'},
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

    @staticmethod
    def wahl_zelle(kennung):
        return format_html('<td class="mesh3dai-wahlzelle"><input type="checkbox" class="mesh3dai-wahl" data-id="{}" aria-label="wählen"></td>', kennung)

    def zeile(self, job):
        zellen = (
            self.wahl_zelle(job['id']),
            format_html('<td data-sort="{}"><a href="{}">{}</a></td>', job['name'].lower(), self.adresse(job), job['name']),
            format_html('<td data-sort="{}">{}</td>', job['modell'].lower(), job['modell']),
            self._paartraining(job) if job.get('paar') else self._trainiert(job['ordner']),          # dritte Spalte (Edgar, 18.10.2026)
            self._gerechnet(job),                                                                      # vierte und fünfte Spalte (Edgar, 20.10.2026; Tag und Uhrzeit getrennt 23.10.2026)
            self.laufzeit_zelle(Mesh3dailaufzeit.job(job)),                                            # Laufzeit (Edgar, 20.10.2026 abends)
            self._zahl(job['proben']),
            self._zahl(job['training']),
            self._zahl(job['pruefung']),
            self._datensatz(job['ordner']),
            self._paarstatus(job) if job.get('paar') else format_html('<td data-sort="{}">{}</td>', job['status'].lower(), job['status']),
        )
        return {'id': job['id'], 'klasse': 'mesh3dai-zeile-job', 'html': mark_safe(''.join(zellen))}

    #: Trainingspaare: bis 19.10.2026 vormittags nur Prüffälle (Edgar: „Hast du jetzt diese Jobs trainiert oder nicht?“ — das Datum war die Zeit der Kette, nicht eines Trainings);
    #: seitdem Trainingsdaten des Formnetzes (Edgar: „die sollst du als nächstes trainieren“), sofern MIA das Tripo-Netz in die A-Pose bringt (`mesh3dai_paar_wolke.py` nimmt nur den Weg MIA).
    #: Die Spalte zählt deshalb nur die gemeinsamen Formläufe (`paare` in `lauf_ergebnis.json`); die Läufe unter `_laeufe/` eines Paars sind Ergebnisse der Kette.
    #: 19.10.2026 spätabends: „Tripo-Job“ statt „Trainingspaar/Prüfpaar“ (Edgar: „hör auch mit Tripo Paar, das sind ganz einfache Tripo jobs“).
    PAAR_TITEL = ('Tripo-Job: ein Tripo-Netz mit bekannter Lösung (dein Genesis-Export). Im Formtraining lernt das Formnetz daraus, wenn MIA das Netz in die A-Pose bringt; das Posennetz hat Tripo-Jobs '
                  'bisher nie gesehen.')
    #: Kette der Vorstufe je Paar (`mesh3dai_vorstufe.py test <kennung>`): `weg` = mia, sonst Rückfall mit `weg_grund`.
    KETTE = ('_test', 'vorstufe')

    @classmethod
    def _paartraining(cls, job):
        """Datum des jüngsten Formtrainings, das dieses Paar in `paare` nennt; sonst „nie“ mit dem Grund aus der Kette (MIA im Rückfall → keine Trainingswolke)."""
        if Mesh3daitrainingsdatum.letztes(job['ordner'], wo=('vorstufe',)):
            return cls._trainiert(job['ordner'], wo=('vorstufe',))
        grund = cls._ohne_wolke(job)
        if grund:
            return format_html('<td data-sort="0" title="{} Kette: {}">nie (MIA-Prüfung nicht bestanden)</td>', cls.PAAR_TITEL, grund)
        return format_html('<td data-sort="0" title="{} Kein Formtraining nennt dieses Paar.">nie</td>', cls.PAAR_TITEL)

    @classmethod
    def _ohne_wolke(cls, job):
        """Grund aus der jüngsten Kette, wenn sie nicht über MIA lief (dann gibt es keine Trainingswolke) — sonst None."""
        ordner = Mesh3daipaare.ordner().joinpath(cls.KETTE[0], job['id'], cls.KETTE[1])
        ketten = sorted(ordner.glob('*/kette.json')) if ordner.is_dir() else []
        if not ketten:
            return None
        try:
            kette = json.loads(ketten[-1].read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return None if kette.get('weg') == 'mia' else (kette.get('weg_grund') or 'Weg %s' % kette.get('weg'))

    @classmethod
    def _paarstatus(cls, job):
        """„Tripo-Job (im Formtraining)" oder „Tripo-Job (nicht im Training)"; die jüngste Kette auf dem Tripo-Netz im Tooltip."""
        im_training = Mesh3daitrainingsdatum.letztes(job['ordner'], wo=('vorstufe',))
        text = 'Tripo-Job (im Formtraining)' if im_training else 'Tripo-Job (nicht im Training)'
        kette = Mesh3daitrainingsdatum.letztes(job['ordner'], wo=('job',))
        titel = cls.PAAR_TITEL + (' Kette zuletzt: Lauf %s, %s' % (kette['lauf'], datetime.fromtimestamp(kette['zeit']).strftime('%d.%m.%Y %H:%M')) if kette else ' Die Kette lief noch nicht.')
        return format_html('<td data-sort="{}" title="{}">{}</td>', text.lower(), titel, text)

    @staticmethod
    def _trainiert(ordner, wo=('job', 'vorstufe')):
        """„17.10.2026 16:20" (Ende des jüngsten fertigen Trainings, `Mesh3daitrainingsdatum`), Tooltip: Lauf und mit welchen Jobs; ohne Training „—". Sortiert nach der Zeit."""
        letztes = Mesh3daitrainingsdatum.letztes(ordner, wo=wo)
        if not letztes:
            return mark_safe('<td data-sort="0" title="Noch kein fertiges Training">—</td>')
        art = 'gemeinsames Netz der Vorstufe/Form' if letztes['art'] == 'vorstufe' else 'Lauf des Jobs'
        titel = '%s %s, trainiert mit %s' % (art, letztes['lauf'], ', '.join(letztes['mit']))
        return format_html('<td data-sort="{}" title="{}">{}</td>', int(letztes['zeit']), titel,
                           datetime.fromtimestamp(letztes['zeit']).strftime('%d.%m.%Y %H:%M'))

    @classmethod
    def _gerechnet(cls, job):
        """„20.10.2026“ · „11:02 (Kleider)“ (`Mesh3dairechendatum`), Tooltip: Schritt und Datei; ohne Rechnung zweimal „—“."""
        letztes = Mesh3dairechendatum.letztes(job)
        if not letztes:
            return cls.datum_zellen(None)
        return cls.datum_zellen(letztes['zeit'], 'Zuletzt gerechnet: %s — %s' % (letztes['was'], letztes['datei']), letztes['was'])

    @staticmethod
    def datum_zellen(zeit, titel='', zusatz=''):
        """Zwei Zellen „23.10.2026“ · „15:19“ aus einer Unix-Zeit (Edgar, 23.10.2026: „das Datumsformat tag-monat-jahr und mache Spalte mit Tag und eine mit Uhrzeit, damit ich die schneller
        finden kann“). Der Tag sortiert nach der vollen Zeit, die Uhrzeit nach der Tageszeit; `zusatz` (der Schritt) steht hinter der Uhrzeit. Auch für die Tabelle der Tests."""
        if not zeit:
            leer = format_html('<td data-sort="0" title="{}">—</td>', titel or 'Noch nichts gerechnet')
            return leer + leer
        d = datetime.fromtimestamp(zeit)
        uhr = d.strftime('%H:%M') + (' (%s)' % zusatz if zusatz else '')
        return (format_html('<td data-sort="{}" title="{}">{}</td>', int(zeit), titel, d.strftime('%d.%m.%Y'))
                + format_html('<td data-sort="{}" title="{}">{}</td>', d.hour * 3600 + d.minute * 60 + d.second, titel, uhr))

    @staticmethod
    def laufzeit_zelle(laufzeit):
        """„3 min 12 s“, Tooltip die gemessenen Teile; ohne gemessene Zeit „—“. Sortiert nach Sekunden. Auch für die Tabelle der Tests."""
        if not laufzeit:
            return mark_safe('<td class="num" data-sort="0" title="Keine gemessene Laufzeit abgelegt">—</td>')
        return format_html('<td class="num" data-sort="{}" title="{}">{}</td>', int(round(laufzeit['sekunden'])), Mesh3dailaufzeit.titel(laufzeit),
                           Mesh3dailaufzeit.text(laufzeit['sekunden']))

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
