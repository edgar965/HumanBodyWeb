# -*- coding: utf-8 -*-
"""Meshfigurtabelle — die Aufträge des Reiters „Mesh to 3D" als djangoBase-Tabelle.

Wie `Meshtabelle`: Kästchen, Vorlage (das Körpernetz von vorn, `ergebnis/vorlage.png`, seit
27.09.2026), Icon (die angepasste Figur mit Textur, `ergebnis/icon.png`), Name, Netz
(Originaldatei), Status mit Fortschritt, Abstand Figur ↔ Netz (RMS in mm, aus dem Schritt
„vorschau"), Regler (wie viele von der Grundfigur abweichen), Dauer, Erstellt. Die Zeile trägt
`data-id`; `meshfigur/meshfigurliste.js` öffnet auf Klick die Auftragsseite.
"""

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .meshtabelle import Meshtabelle

__all__ = ['Meshfigurtabelle']


class Meshfigurtabelle(Meshtabelle):
    KLASSE = 'auftragstabelle meshfigurtabelle'
    SPALTEN = (
        {
            'label': '<input type="checkbox" id="meshfigur-select-all" '
            'title="alle auswählen / Auswahl aufheben">',
            'key': 'wahl',
            'sortAus': True,
        },
        {'label': 'Vorlage', 'key': 'vorlage', 'sortAus': True, 'titel': 'Das Körpernetz, von vorn'},
        {'label': 'Figur', 'key': 'icon', 'sortAus': True, 'titel': 'Die Genesis-Figur mit Textur, von vorn'},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Netz', 'key': 'netz'},
        {'label': 'Status', 'key': 'status'},
        {'label': 'Abstand', 'key': 'abstand', 'num': True, 'titel': 'Figur → Netz, RMS in mm (nur Haut)'},
        {
            'label': 'Regler',
            'key': 'regler',
            'num': True,
            'titel': 'Regler, die von der Grundfigur abweichen',
        },
        {'label': 'Dauer', 'key': 'dauer', 'num': True, 'titel': 'Rechenzeit des letzten Laufs'},
        {'label': 'Erstellt', 'key': 'erstellt'},
    )

    def __init__(self, auftraege):
        super(Meshtabelle, self).__init__(auftraege, schluessel='meshfigur')

    def tabelle(self):
        aus = super(Meshtabelle, self).tabelle()
        aus['leer'] = 'Noch keine Figur — oben ein Netz hochladen.'
        return aus

    def zeile(self, a):
        seite = reverse('meshfigur_auftrag', args=[a.kennung])
        e = a.ergebnis or {}
        abstand = ((e.get('vorschau') or {}).get('abstand') or {}).get('figur_netz_rms_mm')
        regler = len((e.get('regler') or {}).get('geaendert') or [])
        netz = (a.eingang or {}).get('original', '')
        return {
            'id': str(a.id),
            'klasse': 'meshfigur-zeile',
            'html': mark_safe(
                ''.join(
                    (
                        self._kaestchen(a),
                        self._bild(a, seite, e.get('vorlage'), 'Vorlage', 'noch kein Bild des Netzes'),
                        self._bild(
                            a, seite, ((e.get('vorschau') or {}).get('dateien') or {}).get('icon'),
                            'Figur', 'noch keine Vorschau',
                        ),
                        self._name(a, seite),
                        format_html('<td data-sort="{}" title="{}">{}</td>', netz, netz, netz[:40]),
                        self._status(a),
                        self._mm(abstand),
                        self._zahl(regler),
                        self._dauer(e.get('dauer_s')),
                        self._erstellt(a),
                    )
                )
            ),
        }

    @staticmethod
    def _bild(a, seite, datei, text, fehlt):
        """Ein Tabellenbild aus `ergebnis/` — mit dem Stand des Auftrags in der Adresse, sonst
        zeigte der Browser nach einem neuen Lauf das alte Bild (gleicher Name)."""
        if datei:
            adresse = '%s?v=%d' % (
                reverse('meshfigur_datei', args=[a.id, 'ergebnis', datei]),
                int(a.updated_at.timestamp()),
            )
            return format_html(
                '<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
                'alt="{}" loading="lazy"></a></td>',
                seite,
                adresse,
                text,
            )
        return format_html(
            '<td class="hb-kaestchen"><a href="{}" class="bildmodell-icon bildmodell-icon-leer" '
            'title="{}">–</a></td>',
            seite,
            fehlt,
        )

    @staticmethod
    def _mm(wert):
        if wert is None:
            return '<td class="num" data-sort="0"></td>'
        return format_html(
            '<td class="num" data-sort="{}">{} mm</td>', wert, ('%.1f' % float(wert)).replace('.', ',')
        )
