# -*- coding: utf-8 -*-
"""Engine2d3dKleidertabelle — die Aufträge des Bereichs „Haar Engine" als djangoBase-Tabelle (30.09.2026).

Die Spalten von `Blendermodelltabelle`, soweit dieser Bereich sie füllt: das erste Foto der Bildauswahl
(„Vorlage"), Name, Zahl der Fotos, Status mit Fortschrittsbalken, Dauer, Erstellt — dazu zwei Spalten der
Iterationen: die Zahl der abgelegten Runden und die Abweichung des besten Modells. Es fehlen die Spalten,
die zur Kette „Netz aus Fotos → Figur" gehörten (Netz, Formmodell, Abstand, Regler): Dieser Bereich hat sie
nicht. Die Zeile trägt `data-id`; `engine2d3dkleider/engine2d3dkleiderliste.js` öffnet auf Klick die Auftragsseite.

Das Bild trägt den Stand des Auftrags in der Adresse (`?v=`): So darf der Browser es behalten, und ein neu
geschriebenes Bild ist trotzdem sofort da (`Meshtabelle._mit_stand`).
"""

from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .bildmodelltabelle import Bildmodelltabelle
from .meshtabelle import Meshtabelle

__all__ = ['Engine2d3dKleidertabelle']


class Engine2d3dKleidertabelle(Meshtabelle):
    KLASSE = 'auftragstabelle engine2d3dkleidertabelle'
    SPALTEN = (
        {
            'label': '<input type="checkbox" id="engine2d3dkleider-select-all" '
            'title="alle auswählen / Auswahl aufheben">',
            'key': 'wahl',
            'sortAus': True,
        },
        {'label': 'Vorlage', 'key': 'vorlage', 'sortAus': True, 'titel': 'Das erste Foto der Bildauswahl'},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Bilder', 'key': 'bilder', 'num': True, 'titel': 'Fotos der Bildauswahl'},
        {'label': 'Status', 'key': 'status'},
        {'label': 'Runden', 'key': 'runden', 'num': True, 'titel': 'Abgelegte Runden der Iterationen'},
        {
            'label': 'Abweichung',
            'key': 'abweichung',
            'num': True,
            'titel': 'Abweichung des besten Modells von der Vorlage: (1 − Umriss-IoU) + Farbabstand, kleiner ist besser',
        },
        {'label': 'Dauer', 'key': 'dauer', 'num': True, 'titel': 'Rechenzeit des letzten Laufs'},
        {'label': 'Erstellt', 'key': 'erstellt'},
    )

    def __init__(self, auftraege):
        Bildmodelltabelle.__init__(self, auftraege, schluessel='engine2d3dkleider')

    def tabelle(self):
        aus = Bildmodelltabelle.tabelle(self)
        aus['leer'] = 'Noch kein Auftrag — oben Fotos wählen.'
        return aus

    def zeile(self, a):
        seite = reverse('engine2d3dkleider_auftrag', args=[a.kennung])
        e = a.ergebnis or {}
        abweichung = ((e.get('kreislauf') or {}).get('note') or {}).get('abweichung')
        return {
            'id': str(a.id),
            'klasse': 'engine2d3dkleider-zeile',
            'html': mark_safe(
                ''.join(
                    (
                        self._kaestchen(a),
                        self._vorlage_foto(a, seite),
                        self._name(a, seite),
                        format_html(
                            '<td class="num" data-sort="{}">{}</td>', len(a.bilder or []), len(a.bilder or [])
                        ),
                        self._status(a),
                        self._zahl(len(e.get('iterationen') or [])),
                        self._abweichung(abweichung),
                        self._dauer(e.get('dauer_s')),
                        self._erstellt(a),
                    )
                )
            ),
        }

    # ---------------------------------------------------------------- Zellen

    @staticmethod
    def _adresse(a, ordner, datei):
        return '%s?v=%d' % (
            reverse('engine2d3dkleider_datei', args=[a.id, ordner, datei]),
            int(a.updated_at.timestamp()),
        )

    @classmethod
    def _vorlage_foto(cls, a, seite):
        """Das erste Foto der Bildauswahl: das verkleinerte `vorlage/vorlage.png`, solange es fehlt das
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
            cls._adresse(a, Engine2d3dKleiderablage.VORLAGE, klein)
            if klein
            else cls._adresse(a, Engine2d3dKleiderablage.EINGANG, erstes['datei'])
        )
        return format_html(
            '<td class="hb-kaestchen"><a href="{}"><img class="bildmodell-icon" src="{}" '
            'alt="Vorlage" title="{}" loading="lazy"></a></td>',
            seite,
            quelle,
            erstes.get('original') or erstes['datei'],
        )

    @staticmethod
    def _abweichung(wert):
        """Die Note des besten Modells, vier Stellen mit Komma (`data-sort` ebenso: djangoBase liest einen Punkt als
        Tausendertrenner). Ohne Note sortiert die Zelle ans Ende."""
        if wert is None:
            return '<td class="num" data-sort="999999"></td>'
        text = ('%.4f' % float(wert)).replace('.', ',')
        return format_html('<td class="num" data-sort="{}">{}</td>', text, text)
