# -*- coding: utf-8 -*-
"""Mesh3daiformtrainingtabelle — die Trainingsläufe der gemeinsamen Netze im Reiter „Formtraining“ auf /mesh-3D-AI/ als djangoBase-Tabelle (18.10.2026).

Edgar: „ich brauche ein UI für alle Training Jobs … die gerade laufenden Jobs sehen, letztes Datum usw.“ Eine Zeile je Ordner unter `3DObjects/mesh3dai/_vorstufe/laeufe/` (`Mesh3daiformtraining`),
der jüngste zuerst; laufende Zeilen tragen die Klasse `mesh3dai-laeuft`. Gleiche Bauart wie `Mesh3daitabelle`. Seit dem Abend öffnet eine Zeile die Seite des Laufs
(`/mesh-3D-AI/formtraining/<lauf>/`, `Mesh3daiformlaufendpunkte`): Klasse `mesh3daitabelle` (Klick über `Mesh3dailiste`), die Adresse trägt der Link in der Zelle „Lauf“.
"""

import time

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daiformzellen import Mesh3daiformzellen as Z
from .mesh3daitabelle import Mesh3daitabelle

__all__ = ['Mesh3daiformtrainingtabelle']


class Mesh3daiformtrainingtabelle:
    SCHLUESSEL = 'mesh3dai-formtraining'
    SPALTEN = (
        {'label': 'Lauf', 'key': 'lauf', 'titel': 'Ordner unter 3DObjects/mesh3dai/_vorstufe/laeufe ohne die Startzeit; der volle Name steht im Tooltip'},
        {'label': 'Art', 'key': 'art', 'titel': 'Formkopf: sagt das Rig UND die Genesis-Formregler voraus (Formtraining). Vorstufe: nur das Rig der Figur in der A-Pose'},
        {'label': 'Zuletzt', 'key': 'zuletzt',
         'titel': 'Fertig: Ende des Trainings (Änderungszeit von lauf_ergebnis.json). Läuft oder steht: Zeit der letzten Zeile im lauf.log'},
        {'label': 'Status', 'key': 'status',
         'titel': 'Nur von der Platte: fertig = lauf_ergebnis.json liegt da; läuft = ohne Ergebnis und lauf.log vor weniger als 60 min geändert (bzw. dem Dreifachen eines Abschnitts von 20 Epochen); '
                  'steht = länger still (abgebrochen oder abgestürzt). Die Messwerte der letzten Zwischenmessung stehen im Tooltip der Zelle'},
        {'label': 'Gestartet', 'key': 'start', 'titel': 'Aus dem Ordnernamen — das Skript legt den Ordner nach dem Laden der Daten an'},
        {'label': 'Dauer', 'key': 'dauer', 'num': True,
         'titel': 'Trainingszeit in Minuten und Sekunden, ohne das Laden der Daten (dauer_s; während des Laufs die Sekunden der letzten Epochenzeile)'},
        {'label': 'Epochen', 'key': 'epochen', 'num': True},
        {'label': 'Figuren', 'key': 'figuren', 'num': True, 'titel': 'Jobs (training_daten) und Formvarianten im Training; die Namen der Jobs stehen im Tooltip'},
        {'label': 'Proben', 'key': 'proben', 'num': True, 'titel': 'Wolken im Training / in der Prüfung'},
        {'label': 'Gelenke Prüfung (mm)', 'key': 'rig', 'num': True,
         'titel': 'Gelenkfehler der Prüfwolken bei der letzten Zwischenmessung (verlauf: pruefung_mm bzw. pruefung_gelenke_mm). Läufe mit anderen Prüfmengen sind nicht direkt vergleichbar'},
        {'label': 'Form Prüfformen (mm)', 'key': 'form', 'num': True,
         'titel': 'form_mm aus formen_ergebnis.json → zusammen → „Prüfformen (nie trainiert)“: Formfehler der Auswertung im Trainingsskript auf Formvarianten, die nie trainiert wurden'},
        {'label': 'Kopf-Form Prüfformen (mm)', 'key': 'kopf', 'num': True, 'titel': 'kopf_form_mm derselben Zeile (gibt es erst seit Formtraining 2)'},
    )

    def tabelle(self, laeufe):
        return {'key': self.SCHLUESSEL, 'spalten': list(self.SPALTEN), 'zeilen': [self.zeile(lauf) for lauf in laeufe],
                'klasse': 'auftragstabelle mesh3daitabelle mesh3daiformtabelle', 'leer': 'Noch kein Trainingslauf unter 3DObjects/mesh3dai/_vorstufe/laeufe.'}

    def zeile(self, lf):
        epochen = '%d von %d' % (lf['epoche'], lf['epochen']) if lf['zustand'] != 'fertig' and lf['epochen'] else str(lf['epoche'] or lf['epochen'] or '—')
        jobs = lf['jobs']
        figuren = len(jobs) + (lf['formvarianten'] or 0)
        figurtext = ('%d Jobs + %s Formvarianten' % (len(jobs), Z.zahl(lf['formvarianten'])) if lf['formvarianten'] else '%d Jobs' % len(jobs)) if jobs or lf['formvarianten'] else '—'
        p = lf['proben']
        probentext = '%s / %s' % (Z.zahl(p['training']) if p['training'] is not None else '—', Z.zahl(p['pruefung']) if p['pruefung'] is not None else '—')
        zellen = (
            format_html('<td data-sort="{}" title="{}"><a href="/mesh-3D-AI/formtraining/{}/">{}</a></td>', lf['kurz'].lower(), lf['name'], lf['name'], lf['kurz']),
            Z.text(lf['art']),
            Z.zeit(lf['letzte'] if lf['zustand'] != 'fertig' else lf['ende'], titel='Fertig' if lf['zustand'] == 'fertig' else 'Letzte Zeile im lauf.log'),
            Z.text(self.status(lf), sort=lf['zustand'], titel=self.messung(lf['messung'])),
            Z.zeit(lf['start']),
            Mesh3daitabelle.laufzeit_zelle({'sekunden': lf['dauer_s'], 'teile': [('Training ohne das Laden der Daten', lf['dauer_s'])], 'ohne': []} if lf['dauer_s'] else None),
            Z.text(epochen, sort=lf['epoche'] or 0),
            Z.text(figurtext, sort=figuren, titel=', '.join(jobs)),
            Z.text(probentext, sort=p['training'] or 0),
            Z.mmzelle(lf['rig_mm']),
            Z.mmzelle(lf['form_mm']),
            Z.mmzelle(lf['kopf_mm']),
        )
        klasse = 'mesh3dai-zeile-lauf' + (' mesh3dai-laeuft' if lf['zustand'] == 'läuft' else '') + (' mesh3dai-probelauf' if lf['probe'] else '')
        return {'id': lf['name'], 'klasse': klasse, 'html': mark_safe(''.join(zellen))}

    @staticmethod
    def status(lf, jetzt=None):
        jetzt = time.time() if jetzt is None else jetzt
        if lf['zustand'] == 'fertig':
            text = 'fertig'
        elif lf['zustand'] == 'läuft':
            text = 'läuft · Epoche %d von %s' % (lf['epoche'], lf['epochen'] or '?') if lf['epoche'] else 'läuft · vor der ersten Epochenzeile'
        else:
            text = 'steht · keine Zeile seit %s' % Z.spanne(jetzt - (lf['letzte'] or jetzt))
        return text + (' · Probelauf' if lf['probe'] else '')

    @staticmethod
    def messung(m):
        """Die Messwerte der letzten Zwischenmessung als Tooltip, Zahlen in mm wie im Log."""
        return ' · '.join('%s %s' % (k, Z.mm(v) if isinstance(v, (int, float)) and k != 'epoche' else v) for k, v in (m or {}).items())
