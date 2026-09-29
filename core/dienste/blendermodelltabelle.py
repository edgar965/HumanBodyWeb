# -*- coding: utf-8 -*-
"""Blendermodelltabelle — die Aufträge des Bereichs „BlenderModel" als djangoBase-Tabelle.

Die Spalten von `Meshfigurtabelle` (Vorlage, Figur, Name, Status, Abstand, Regler, Dauer, Erstellt),
dazu das, was hier am Anfang steht: das erste Foto der Bildauswahl („Vorlage"), das Netz, das der Lauf
daraus gebaut hat („Mesh"), das Formmodell und die Zahl der Fotos. Die Zeile trägt `data-id`;
`blendermodell/blendermodellliste.js` öffnet auf Klick die Auftragsseite.

Alle drei Bilder tragen den Stand des Auftrags in der Adresse (`?v=`): So darf der Browser sie
behalten, und ein neu gerendertes Bild ist trotzdem sofort da (`Meshtabelle._mit_stand`).
"""

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..daten.blendermodellablage import Blendermodellablage
from .bildmodelltabelle import Bildmodelltabelle
from .meshoptionen import Meshoptionen
from .meshtabelle import Meshtabelle

__all__ = ['Blendermodelltabelle']


class Blendermodelltabelle(Meshtabelle):
    KLASSE = 'auftragstabelle blendermodelltabelle'
    SPALTEN = (
        {
            'label': '<input type="checkbox" id="blendermodell-select-all" '
            'title="alle auswählen / Auswahl aufheben">',
            'key': 'wahl',
            'sortAus': True,
        },
        {'label': 'Vorlage', 'key': 'vorlage', 'sortAus': True, 'titel': 'Das erste Foto der Bildauswahl'},
        {'label': 'Mesh', 'key': 'netz', 'sortAus': True, 'titel': 'Das Netz aus den Fotos, von vorn'},
        {'label': 'Figur', 'key': 'icon', 'sortAus': True, 'titel': 'Die Figur mit Textur, von vorn'},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Formmodell', 'key': 'formmodell'},
        {'label': 'Bilder', 'key': 'bilder', 'num': True, 'titel': 'Fotos der Bildauswahl'},
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
        Bildmodelltabelle.__init__(self, auftraege, schluessel='blendermodell')

    def tabelle(self):
        aus = Bildmodelltabelle.tabelle(self)
        aus['leer'] = 'Noch kein Auftrag — oben Fotos wählen.'
        return aus

    def zeile(self, a):
        seite = reverse('blendermodell_auftrag', args=[a.kennung])
        e = a.ergebnis or {}
        netz = e.get('netz') or {}
        modelle = dict(Meshoptionen.eintrag('formmodell')['werte'])
        modell = ((a.optionen or {}).get('netz') or {}).get('formmodell', '')
        abstand = ((e.get('vorschau') or {}).get('abstand') or {}).get('figur_netz_rms_mm')
        regler = len((e.get('regler') or {}).get('geaendert') or [])
        return {
            'id': str(a.id),
            'klasse': 'blendermodell-zeile',
            'html': mark_safe(
                ''.join(
                    (
                        self._kaestchen(a),
                        self._vorlage_foto(a, seite),
                        self._bild(
                            a,
                            seite,
                            Blendermodellablage.NETZ,
                            (netz.get('dateien') or {}).get('icon'),
                            'Mesh',
                            'noch kein Netz',
                        ),
                        self._bild(
                            a,
                            seite,
                            Blendermodellablage.ERGEBNIS,
                            ((e.get('vorschau') or {}).get('dateien') or {}).get('icon'),
                            'Figur',
                            'noch keine Figur',
                        ),
                        self._name(a, seite),
                        format_html(
                            '<td data-sort="{}" title="{}">{}</td>',
                            modell,
                            modelle.get(modell, ''),
                            modelle.get(modell, modell).split(' — ')[0],
                        ),
                        format_html(
                            '<td class="num" data-sort="{}">{}</td>', len(a.bilder or []), len(a.bilder or [])
                        ),
                        self._status(a),
                        self._mm(abstand),
                        self._zahl(regler),
                        self._dauer(e.get('dauer_s')),
                        self._erstellt(a),
                    )
                )
            ),
        }

    # ---------------------------------------------------------------- Bilder

    @staticmethod
    def _adresse(a, ordner, datei):
        return '%s?v=%d' % (
            reverse('blendermodell_datei', args=[a.id, ordner, datei]),
            int(a.updated_at.timestamp()),
        )

    @classmethod
    def _vorlage_foto(cls, a, seite):
        """Das erste Foto der Bildauswahl: das verkleinerte `netz/vorlage.png`, solange es fehlt das
        Original — lieber ein großes Bild als eine leere Zelle (wie `Meshtabelle._vorlage`)."""
        bilder = a.bilder or []
        if not bilder or not bilder[0].get('datei'):
            return format_html(
                '<td class="hb-kaestchen"><a href="{}" class="bildmodell-icon '
                'bildmodell-icon-leer" title="kein Foto">–</a></td>',
                seite,
            )
        erstes = bilder[0]
        klein = (a.ergebnis or {}).get('vorlage_foto')
        quelle = (
            cls._adresse(a, Blendermodellablage.NETZ, klein)
            if klein
            else cls._adresse(a, Blendermodellablage.EINGANG, erstes['datei'])
        )
        return format_html(
            '<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
            'alt="Vorlage" title="{}" loading="lazy"></a></td>',
            seite,
            quelle,
            erstes.get('original') or erstes['datei'],
        )

    @classmethod
    def _bild(cls, a, seite, ordner, datei, text, fehlt):
        if datei:
            return format_html(
                '<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
                'alt="{}" loading="lazy"></a></td>',
                seite,
                cls._adresse(a, ordner, datei),
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
