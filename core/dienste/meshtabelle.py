# -*- coding: utf-8 -*-
"""Meshtabelle — die Mesh-Aufträge (Reiter „Mesh") als djangoBase-Tabelle.

Wie `Bildmodelltabelle`: Kästchen, Icon (die gerenderte Vorderansicht des Netzes,
`ergebnis/icon.png`), Name, Formmodell, Bilder, Status mit Fortschritt, Flächen, Dauer,
Erstellt. Die Zeile trägt `data-id`; `mesh/meshliste.js` öffnet auf Klick die
Auftragsseite `/modell-aus-dateien/mesh/<kennung>/`.
"""

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import template_localtime

from .bildmodelltabelle import Bildmodelltabelle
from .meshoptionen import Meshoptionen

__all__ = ['Meshtabelle']


class Meshtabelle(Bildmodelltabelle):
    KLASSE = 'auftragstabelle meshtabelle'
    SPALTEN = (
        {
            'label': '<input type="checkbox" id="mesh-select-all" title="alle auswählen / Auswahl aufheben">',
            'key': 'wahl',
            'sortAus': True,
        },
        {'label': 'Mesh', 'key': 'icon', 'sortAus': True},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Formmodell', 'key': 'formmodell'},
        {'label': 'Bilder', 'key': 'bilder', 'num': True},
        {'label': 'Status', 'key': 'status'},
        {'label': 'Flächen', 'key': 'flaechen', 'num': True},
        {'label': 'Dauer', 'key': 'dauer', 'num': True, 'titel': 'Rechenzeit des letzten Laufs'},
        {'label': 'Erstellt', 'key': 'erstellt'},
    )

    def __init__(self, auftraege):
        super().__init__(auftraege, schluessel='mesh')

    def tabelle(self):
        aus = super().tabelle()
        aus['leer'] = 'Noch kein Mesh — oben Fotos hochladen.'
        return aus

    def zeile(self, a):
        seite = reverse('mesh_auftrag', args=[a.kennung])
        modelle = dict(Meshoptionen.eintrag('formmodell')['werte'])
        modell = (a.optionen or {}).get('formmodell', '')
        e = a.ergebnis or {}
        return {
            'id': str(a.id),
            'klasse': 'mesh-zeile',
            'html': mark_safe(''.join((
                self._kaestchen(a),
                self._meshicon(a, seite),
                self._name(a, seite),
                format_html('<td data-sort="{}" title="{}">{}</td>', modell, modelle.get(modell, ''),
                            modelle.get(modell, modell).split(' — ')[0]),
                format_html('<td class="num" data-sort="{}">{}</td>', len(a.bilder or []), len(a.bilder or [])),
                self._status(a),
                self._zahl(e.get('flaechen')),
                self._dauer(e.get('dauer_s')),
                self._erstellt(a),
            ))),
        }

    @staticmethod
    def _meshicon(a, seite):
        icon = ((a.ergebnis or {}).get('dateien') or {}).get('icon')
        if icon:
            return format_html('<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
                               'alt="Mesh"></a></td>', seite, reverse('mesh_datei', args=[a.id, 'ergebnis', icon]))
        return format_html('<td class="hb-kaestchen"><a href="{}" class="bildmodell-icon bildmodell-icon-leer" '
                           'title="noch keine Vorschau">–</a></td>', seite)

    @staticmethod
    def _zahl(wert):
        if not wert:
            return '<td class="num" data-sort="0"></td>'
        return format_html('<td class="num" data-sort="{}">{}</td>', int(wert), '{:,}'.format(int(wert)).replace(',', '.'))

    @staticmethod
    def _dauer(sekunden):
        if not sekunden:
            return '<td class="num" data-sort="0"></td>'
        s = int(round(float(sekunden)))
        return format_html('<td class="num" data-sort="{}">{}:{:02d} min</td>', s, s // 60, s % 60)

    @staticmethod
    def _erstellt(a):
        zeit = template_localtime(a.created_at)
        return format_html('<td data-sort="{}">{}</td>', zeit.strftime('%Y%m%d%H%M%S'), zeit.strftime('%d.%m.%Y %H:%M'))
