# -*- coding: utf-8 -*-
"""Meshtabelle — die Mesh-Aufträge (Reiter „Mesh") als djangoBase-Tabelle.

Wie `Bildmodelltabelle`: Kästchen, Icon (die gerenderte Vorderansicht des Netzes,
`ergebnis/icon.png`), Name, Formmodell, Bilder, Status mit Fortschritt, Flächen, Dauer,
Erstellt. Die Zeile trägt `data-id`; `mesh/meshliste.js` öffnet auf Klick die
Auftragsseite `/modell-aus-dateien/mesh/<kennung>/`.
"""

from django.urls import reverse
from django.utils.html import format_html, format_html_join
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
        {'label': 'Vorlage', 'key': 'vorlage', 'sortAus': True, 'titel': 'Das erste hochgeladene Foto'},
        {'label': 'Mesh', 'key': 'icon', 'sortAus': True, 'titel': 'Ansicht des erzeugten Netzes (von vorn)'},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Formmodell', 'key': 'formmodell'},
        {'label': 'Kopf/Körper', 'key': 'verwendung', 'sortAus': True,
         'titel': 'Wozu dieses Netz dienen soll — direkt hier umstellbar, ohne neuen Lauf'},
        {'label': 'Auflösung', 'key': 'aufloesung', 'titel': 'Voxelauflösung des Formmodells'},
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
                self._vorlage(a, seite),
                self._meshicon(a, seite),
                self._name(a, seite),
                format_html('<td data-sort="{}" title="{}">{}</td>', modell, modelle.get(modell, ''),
                            modelle.get(modell, modell).split(' — ')[0]),
                self._verwendung(a),
                self._aufloesung(a),
                format_html('<td class="num" data-sort="{}">{}</td>', len(a.bilder or []), len(a.bilder or [])),
                self._status(a),
                self._zahl(e.get('flaechen')),
                self._dauer(e.get('dauer_s')),
                self._erstellt(a),
            ))),
        }

    @staticmethod
    def _verwendung(a):
        """Kopf/Körper als Auswahlfeld direkt in der Zeile (Edgar, 27.09.2026: „beim Anlegen
        des Jobs, oder beim Job selber nachträglich setzen"). `mesh/meshliste.js` schickt die
        Änderung an `/api/mesh/<id>/verwendung/` — ohne Neuberechnung, es ist nur eine
        Kennzeichnung. Der Kurztext ist der Teil vor dem Gedankenstrich, sonst sprengt die
        Auswahl die Spalte."""
        eintrag = Meshoptionen.eintrag('verwendung')
        jetzt = (a.optionen or {}).get('verwendung') or eintrag['vorgabe']
        optionen = format_html_join('', '<option value="{}"{}>{}</option>',
                                    ((w, mark_safe(' selected') if w == jetzt else '', t.split(' — ')[0])
                                     for w, t in eintrag['werte']))
        return format_html('<td data-sort="{}"><select class="viewer-select mesh-verwendung" '
                           'data-id="{}" data-vorher="{}" title="{}">{}</select></td>',
                           jetzt, str(a.id), jetzt, dict(eintrag['werte'])[jetzt], optionen)

    @staticmethod
    def _aufloesung(a):
        """Die Auflösungsstufe als Wort, sortiert nach ihrer Höhe — nicht alphabetisch
        („hoch" stünde sonst vor „mittel" vor „schnell", also genau falsch herum)."""
        stufen = [w for w, _ in Meshoptionen.eintrag('aufloesung')['werte']]
        texte = dict(Meshoptionen.eintrag('aufloesung')['werte'])
        stufe = (a.optionen or {}).get('aufloesung', '')
        if stufe not in texte:
            return '<td data-sort="0"></td>'
        return format_html('<td data-sort="{}" title="{}">{}</td>', stufen.index(stufe) + 1, texte[stufe],
                           texte[stufe].split(' — ')[0])

    @staticmethod
    def _vorlage(a, seite):
        """Das erste hochgeladene Foto (Edgar, 27.09.2026) — unverändert aus `eingang/`, nicht
        das freigestellte: Es soll zeigen, WAS der Lauf bekommen hat. `bilder` ist die Reihenfolge
        des Hochladens, also ist der erste Eintrag „das erste Vorlagebild"."""
        bilder = a.bilder or []
        if not bilder or not bilder[0].get('datei'):
            return format_html('<td class="hb-kaestchen"><a href="{}" class="bildmodell-icon '
                               'bildmodell-icon-leer" title="kein Foto">–</a></td>', seite)
        erstes = bilder[0]
        # Bevorzugt das verkleinerte `ergebnis/vorlage.png` (`Meshicon.vorlage_schreiben`);
        # solange es fehlt (Auftrag noch nie gelaufen), das Original — lieber ein großes Bild
        # als eine leere Zelle.
        klein = ((a.ergebnis or {}).get('dateien') or {}).get('vorlage')
        quelle = Meshtabelle._mit_stand(a, (('ergebnis', klein) if klein else ('eingang', erstes['datei'])))
        return format_html('<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
                           'alt="Vorlage" title="{}" loading="lazy"></a></td>', seite, quelle,
                           erstes.get('original') or erstes['datei'])

    @staticmethod
    def _mit_stand(a, ort):
        """Bildadresse mit dem Stand des Auftrags als Kennung.

        Ohne sie liefert `Auftragsdatei` nur `no-cache` (jeder Aufruf fragt nach, spart
        aber wenigstens den Inhalt); MIT ihr gilt die Antwort ein Jahr, und ein neu
        gerendertes Icon ist trotzdem sofort da — es steht dann unter einer anderen
        Adresse. Gemessen am 27.09.2026: 50 Vorschaubilder, 2,86 MB, 0,99 s bei JEDEM
        Seitenaufruf, weil `/api/` pauschal `no-store` trug.
        """
        ordner, datei = ort
        return '%s?v=%d' % (reverse('mesh_datei', args=[a.id, ordner, datei]),
                            int(a.updated_at.timestamp()))

    @staticmethod
    def _meshicon(a, seite):
        icon = ((a.ergebnis or {}).get('dateien') or {}).get('icon')
        if icon:
            return format_html('<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
                               'alt="Mesh" title="Erzeugtes Netz, von vorn" loading="lazy"></a></td>',
                               seite, Meshtabelle._mit_stand(a, ('ergebnis', icon)))
        return format_html('<td class="hb-kaestchen"><a href="{}" class="bildmodell-icon '
                           'bildmodell-icon-leer" title="noch kein Netz">–</a></td>', seite)

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
        # `format_html` escapt jedes Argument zu `SafeString` — ein Zahlenformat wie `{:02d}`
        # scheitert daran ("Unknown format code 'd'"). Erst rechnen, dann einsetzen.
        return format_html('<td class="num" data-sort="{}">{} min</td>', s, '%d:%02d' % (s // 60, s % 60))

    @staticmethod
    def _erstellt(a):
        zeit = template_localtime(a.created_at)
        return format_html('<td data-sort="{}">{}</td>', zeit.strftime('%Y%m%d%H%M%S'), zeit.strftime('%d.%m.%Y %H:%M'))
