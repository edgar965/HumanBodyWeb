# -*- coding: utf-8 -*-
"""Bildmodelltabelle — die Aufträge „Modell aus Bildern" als djangoBase-Tabelle.

Edgar (18.09.2026): „Pro Job dann eine Zeile wo als Icon das 3D-Modell ist.
Mit Klick auf die Zeile komme ich dann in die Jobview." Die Struktur, die
`djangobase/_tabelle.html` erwartet (wie `Auftragstabelle`): Kästchen,
Icon (die gerenderte Figur, `ergebnis/icon.png`), Name, Typ, Bilder, Status
mit Fortschrittsbalken, Ergebnis (RMS mm), Erstellt. Die Zeile trägt
`data-id`; `bildmodell/liste.js` öffnet auf Klick die Auftragsseite.
"""

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import template_localtime

__all__ = ['Bildmodelltabelle']


class Bildmodelltabelle:
    KLASSE = 'auftragstabelle bildmodelltabelle'
    SPALTEN = (
        {
            'label': '<input type="checkbox" id="select-all" title="alle auswählen / Auswahl aufheben">',
            'key': 'wahl',
            'sortAus': True,
        },
        {'label': 'Modell', 'key': 'icon', 'sortAus': True},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Typ', 'key': 'typ'},
        {'label': 'Bilder', 'key': 'bilder', 'num': True},
        {'label': 'Status', 'key': 'status'},
        {
            'label': 'Abweichung',
            'key': 'rms',
            'num': True,
            'titel': 'RMS der Käfigpunkte zum Zielnetz in mm — mit Restmorph, wenn einer da ist',
        },
        {'label': 'Erstellt', 'key': 'erstellt'},
    )
    ZUSTAENDE = {
        'fertig': ('hb-gut', 'fa-check-circle', 'Fertig'),
        'gescheitert': ('hb-schlecht', 'fa-times-circle', 'Fehlgeschlagen'),
        'angelegt': ('hb-laeuft', 'fa-clock', 'Angelegt'),
        'angehalten': ('hb-laeuft', 'fa-pause-circle', 'Angehalten'),
    }
    TYPEN = {'genesis9': 'Genesis 9'}

    def __init__(self, auftraege, schluessel='bildmodell'):
        self.auftraege = list(auftraege)
        self.schluessel = schluessel

    def tabelle(self):
        return {
            'key': self.schluessel,
            'spalten': list(self.SPALTEN),
            'zeilen': [self.zeile(a) for a in self.auftraege],
            'leer': 'Noch kein Auftrag — oben Bilder hochladen.',
            'klasse': self.KLASSE,
        }

    # --------------------------------------------------------------- Zeile

    def zeile(self, a):
        seite = reverse('bildmodell_auftrag', args=[a.kennung])
        return {
            'id': str(a.id),
            'klasse': 'bildmodell-zeile',
            'html': mark_safe(
                ''.join(
                    (
                        self._kaestchen(a),
                        self._icon(a, seite),
                        self._name(a, seite),
                        format_html('<td data-sort="{}">{}</td>', a.typ, self.TYPEN.get(a.typ, a.typ)),
                        format_html(
                            '<td class="num" data-sort="{}">{}</td>', len(a.bilder or []), len(a.bilder or [])
                        ),
                        self._status(a),
                        self._rms(a),
                        self._erstellt(a),
                    )
                )
            ),
        }

    @staticmethod
    def _kaestchen(a):
        return format_html(
            '<td class="hb-kaestchen"><input type="checkbox" class="job-check" value="{}"></td>', a.id
        )

    @staticmethod
    def _icon(a, seite):
        v = (a.ergebnis or {}).get('vorschau') or {}
        if v.get('icon'):
            return format_html(
                '<td class="hb-kaestchen"><a href="{}">'
                '<img class="bildmodell-icon" src="{}" alt="Modell"></a></td>',
                seite,
                reverse('bildmodell_datei', args=[a.id, 'ergebnis', v['icon']]),
            )
        return format_html(
            '<td class="hb-kaestchen"><a href="{}" class="bildmodell-icon bildmodell-icon-leer" '
            'title="noch keine Vorschau">–</a></td>',
            seite,
        )

    @staticmethod
    def _name(a, seite):
        return format_html('<td data-sort="{}"><a href="{}">{}</a></td>', a.name.lower(), seite, a.name)

    def _status(self, a):
        if a.status == 'laeuft':
            return format_html(
                '<td id="status-{}" data-sort="1" class="hb-laeuft"><i class="fas fa-spinner fa-spin"></i> '
                '<span class="inline-progress">'
                '<span class="progress-fill-mini" style="width:{}%"></span></span> '
                '<span class="hb-fortschritt">{} % {}</span></td>',
                a.id,
                a.progress,
                a.progress,
                a.progress_detail or '',
            )
        klasse, symbol, text = self.ZUSTAENDE.get(a.status, ('', 'fa-question', a.status))
        titel = a.error_message or ''
        return format_html(
            '<td id="status-{}" data-sort="{}" class="{}" title="{}"><i class="fas {}"></i> {}</td>',
            a.id,
            a.status,
            klasse,
            titel,
            symbol,
            text,
        )

    @staticmethod
    def _rms(a):
        e = a.ergebnis or {}
        wert = (e.get('rest') or {}).get('rms_mit_morph_mm')
        if wert is None:
            wert = (e.get('anpassung') or {}).get('punkte_rms_mm')
        if wert is None:
            return '<td class="num" data-sort="999999"></td>'
        return format_html('<td class="num" data-sort="{}">{} mm</td>', wert, wert)

    @staticmethod
    def _erstellt(a):
        zeit = template_localtime(a.created_at)
        return format_html(
            '<td data-sort="{}">{}</td>', zeit.strftime('%Y%m%d%H%M%S'), zeit.strftime('%d.%m.%Y %H:%M')
        )
