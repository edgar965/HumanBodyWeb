# -*- coding: utf-8 -*-
"""Mesh3dtabelle — die Aufträge der Seite „Mesh-3D“ als djangoBase-Tabelle (11.10.2026).

Ein Auftrag ist ein Modell-Import (`Blendimportablage`, `stand.json`); es gibt kein Datenbankmodell. Die Spalten folgen der Liste von
„2D3D Kleider“: Name, Format, Status mit Fortschrittsbalken, Schritt, Stücke, Modell, Dauer, Erstellt — dazu das Kästchen für „Gewählte löschen“.
Die Zeile trägt `data-id` = Kennung; `mesh3d/mesh3dliste.js` öffnet auf Klick die Auftragsseite.
"""

from datetime import datetime

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..daten.blendimportablage import Blendimportablage
from .mesh3dlink import Mesh3dlink
from .mesh3dreiter import Mesh3dreiter
from .mesh3dschritte import Mesh3dschritte
from .mesh3dzustand import Mesh3dzustand

__all__ = ['Mesh3dtabelle']


class Mesh3dtabelle:
    SCHLUESSEL = 'mesh3d'
    SPALTEN = (
        {'label': '<input type="checkbox" class="mesh3d-alle" title="alle auswählen / Auswahl aufheben">', 'key': 'wahl', 'sortAus': True},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Format', 'key': 'format', 'titel': 'Blender, OBJ, FBX oder GLB'},
        {'label': 'Status', 'key': 'status'},
        {'label': 'Schritt', 'key': 'schritt'},
        {'label': 'Stücke', 'key': 'stuecke', 'num': True, 'titel': 'Kleider, Haar und Augen als Genesis-Stücke'},
        {'label': 'Modell', 'key': 'modell', 'titel': 'Das gespeicherte Genesis-Modell'},
        {'label': 'Dauer', 'key': 'dauer', 'num': True, 'titel': 'Rechenzeit des letzten Laufs'},
        {'label': 'Erstellt', 'key': 'erstellt'},
    )
    ZUSTAENDE = {
        'fertig': ('hb-gut', 'fa-check-circle', 'Fertig'),
        'gescheitert': ('hb-schlecht', 'fa-times-circle', 'Fehlgeschlagen'),
        'neu': ('hb-laeuft', 'fa-clock', 'Angelegt'),
        'angehalten': ('hb-laeuft', 'fa-pause-circle', 'Angehalten'),
    }

    def __init__(self, kennungen=None):
        self.kennungen = list(kennungen) if kennungen is not None else Blendimportablage.alle()

    def tabelle(self, reiter=None):
        """`reiter`: Schlüssel des Reiters, in dem die Tabelle steht. Jede Tabelle hat ihren eigenen Speicher für Sortierung und Spaltenbreiten; die des ersten Reiters heißt weiter `mesh3d`."""
        zeilen = [z for z in (self.zeile(k) for k in self.kennungen) if z]
        erster = reiter is None or reiter == Mesh3dreiter.erster()
        return {'key': self.SCHLUESSEL if erster else '%s-%s' % (self.SCHLUESSEL, reiter), 'spalten': list(self.SPALTEN), 'zeilen': zeilen,
                'klasse': 'auftragstabelle mesh3dtabelle',
                'leer': 'Noch kein Auftrag — oben eine Datei angeben.' if erster else 'Kein Auftrag in diesem Reiter — in der Liste „Aufträge“ wählen und hierher verschieben.'}

    def zeile(self, kennung):
        stand = Mesh3dzustand.stand(kennung)
        if stand is None:
            return None
        quelle = stand.get('quelle') or {}
        e = stand.get('ergebnis') or {}
        seite = Mesh3dlink.pfad(kennung, quelle.get('name') or kennung)
        zellen = (
            format_html('<td><input type="checkbox" class="mesh3d-wahl" data-id="{}" aria-label="Auftrag wählen"></td>', kennung),
            format_html('<td data-sort="{}"><a href="{}">{}</a></td>', str(quelle.get('name') or kennung).lower(), seite, quelle.get('name') or kennung),
            format_html('<td data-sort="{}">{}</td>', quelle.get('format') or 'blend', {'blend': 'Blender'}.get(quelle.get('format') or 'blend', str(quelle.get('format')).upper())),
            self._status(stand),
            format_html('<td>{}</td>', Mesh3dschritte.TITEL.get(stand.get('schritt'), '') if stand.get('schritt') else ''),
            self._zahl(len(((e.get('stuecke') or {}).get('stuecke') or {}))),
            format_html('<td>{}</td>', ((e.get('modell') or {}).get('name')) or ''),
            self._dauer(stand.get('dauer_s')),
            self._erstellt(kennung),
        )
        return {'id': kennung, 'klasse': 'mesh3d-zeile', 'html': mark_safe(''.join(zellen))}

    # ---------------------------------------------------------------- Zellen

    def _status(self, stand):
        status = stand.get('status') or 'neu'
        if status == 'laeuft':
            prozent = int(stand.get('fortschritt') or 0)
            return format_html(
                '<td id="mesh3d-status-{}" data-sort="1" data-status="laeuft" class="hb-laeuft"><i class="fas fa-spinner fa-spin"></i> '
                '<span class="inline-progress"><span class="progress-bar-mini"><span class="progress-fill-mini" style="width:{}%"></span></span></span> '
                '<span class="hb-fortschritt">{} % {}</span></td>', stand.get('kennung'), prozent, prozent, stand.get('detail') or '')
        klasse, symbol, text = self.ZUSTAENDE.get(status, ('', 'fa-question-circle', status))
        return format_html('<td data-sort="0" class="{}"><i class="fas {}"></i> {}</td>', klasse, symbol, text)

    @staticmethod
    def _zahl(wert):
        return format_html('<td class="num" data-sort="{}">{}</td>', int(wert), int(wert) if wert else '')

    @staticmethod
    def _dauer(sekunden):
        if not sekunden:
            return mark_safe('<td class="num" data-sort="0"></td>')
        s = int(round(float(sekunden)))
        return format_html('<td class="num" data-sort="{}">{}</td>', s, '%d:%02d min' % (s // 60, s % 60))

    @staticmethod
    def _erstellt(kennung):
        try:
            zeit = datetime.strptime(kennung, '%Y.%m.%d.%H.%M.%S')
        except ValueError:
            return mark_safe('<td></td>')
        return format_html('<td data-sort="{}">{}</td>', zeit.strftime('%Y%m%d%H%M%S'), zeit.strftime('%d.%m.%Y %H:%M'))
