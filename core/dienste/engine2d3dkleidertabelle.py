# -*- coding: utf-8 -*-
"""Engine2d3dKleidertabelle — die Aufträge des Bereichs „2D3D Kleider" als djangoBase-Tabelle (30.09.2026).

Die Spalten von `Blendermodelltabelle`, soweit dieser Bereich sie füllt: das erste Foto der Bildauswahl
(„Vorlage"), Name, Zahl der Fotos, Status mit Fortschrittsbalken, Dauer, Erstellt — dazu zwei Spalten der
Iterationen: die Zahl der abgelegten Runden und die Abweichung des besten Modells. Es fehlen die Spalten,
die zur Kette „Netz aus Fotos → Figur" gehörten (Netz, Formmodell, Abstand, Regler): Dieser Bereich hat sie
nicht. Die Zeile trägt `data-id`; `engine2d3dkleider/engine2d3dkleiderliste.js` öffnet auf Klick die Auftragsseite.

Das Bild trägt den Stand des Auftrags in der Adresse (`?v=`): So darf der Browser es behalten, und ein neu
geschriebenes Bild ist trotzdem sofort da (`Meshtabelle._mit_stand`).
"""

from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .bildmodelltabelle import Bildmodelltabelle
from .engine2d3dkleiderki import Engine2d3dKleiderki
from .engine2d3dkleiderqualitaet import Engine2d3dKleiderqualitaet
from .meshtabelle import Meshtabelle

__all__ = ['Engine2d3dKleidertabelle']


def _qualitaetsspalten():
    """Die acht Rangspalten der Handwertung im Kopf der Tabelle — aus `Engine2d3dKleiderqualitaet.FELDER`, in dessen Reihenfolge."""
    return tuple(
        {
            'label': label,
            'key': spalte,
            'num': True,
            'titel': Engine2d3dKleiderqualitaet.kopftitel(schluessel),
        }
        for schluessel, (spalte, label, _frage) in Engine2d3dKleiderqualitaet.FELDER.items()
    )


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
        {
            'label': 'KI',
            'key': 'ki',
            'titel': 'Welche KI das Netz aus den Fotos rechnet (Schritt „Netz"): TRELLIS.2, Pixal3D oder Pixal3D Mehrbild. '
            'Von Hand wählbar, gilt beim nächsten Lauf; während eines Laufs gesperrt.',
        },
        {'label': 'Status', 'key': 'status'},
        {'label': 'Runden', 'key': 'runden', 'num': True, 'titel': 'Abgelegte Runden der Iterationen'},
        {
            'label': 'Abweichung',
            'key': 'abweichung',
            'num': True,
            'titel': 'Abweichung des besten Modells von der Vorlage: (1 − Umriss-IoU) + Farbabstand, kleiner ist besser',
        },
        *_qualitaetsspalten(),
        {'label': 'Dauer', 'key': 'dauer', 'num': True, 'titel': 'Rechenzeit des letzten Laufs'},
        {'label': 'Erstellt', 'key': 'erstellt'},
    )

    def __init__(self, auftraege):
        Bildmodelltabelle.__init__(self, auftraege, schluessel='engine2d3dkleider')
        #: Wie viele Läufe je Rangspalte bewertet sind: Die Auswahl eines Felds reicht bis zum nächsten freien Rang (`_qualitaet`).
        self._bewertet = {
            spalte: sum(1 for a in self.auftraege if getattr(a, spalte, None))
            for spalte, _label, _frage in Engine2d3dKleiderqualitaet.FELDER.values()
        }

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
                        self._ki(a),
                        self._status(a),
                        self._zahl(len(e.get('iterationen') or [])),
                        self._abweichung(abweichung),
                        *(self._qualitaet(a, schluessel) for schluessel in Engine2d3dKleiderqualitaet.FELDER),
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
    def _ki(a):
        """Die KI des Schritts „Netz" als Auswahlfeld in der Zeile (`engine2d3dkleider/engine2d3dkleiderkiwahl.js` speichert die Änderung als
        `mesh.modell` über `/api/engine2d3dkleider/<id>/einstellungen/`). Gesperrt, solange der Auftrag läuft: Der Arbeitsprozess hat seine
        Optionen schon gelesen, der Server lehnt die Änderung dann mit 409 ab."""
        jetzt = Engine2d3dKleiderki.aktuell(a.optionen)
        werte = Engine2d3dKleiderki.werte()
        optionen = format_html_join(
            '',
            '<option value="{}" title="{}"{}>{}</option>',
            ((w, t, mark_safe(' selected') if w == jetzt else '', k) for w, k, t in werte),
        )
        return format_html(
            '<td data-sort="{}"><select class="viewer-select engine2d3dkleider-ki" data-id="{}" data-vorher="{}" title="{}"{}>{}</select></td>',
            jetzt,
            str(a.id),
            jetzt,
            next(t for w, _k, t in werte if w == jetzt),
            mark_safe(' disabled') if a.status == 'laeuft' else '',
            optionen,
        )

    def _qualitaet(self, a, schluessel):
        """Der Rang des Laufs in einer Qualitätsspalte als Auswahlfeld direkt in der Zeile (`engine2d3dkleider/engine2d3dkleiderqualitaet.js`
        speichert jede Änderung an `/api/engine2d3dkleider/<id>/qualitaet/` und stellt danach die Felder der anderen Zeilen nach). Zur Wahl
        stehen „–" und die Ränge 1 bis zum nächsten freien (bewertete Läufe + 1, solange dieser Lauf noch keinen hat) — weiter hinten
        gäbe es eine Lücke. `data-sort` ist der Rang, „nicht bewertet" sortiert ans Ende (`SORT_OHNE_RANG`)."""
        spalte = Engine2d3dKleiderqualitaet.spalte(schluessel)
        jetzt = getattr(a, spalte, None) or 0
        bis = max(self._bewertet.get(spalte, 0) + (0 if jetzt else 1), jetzt, 1)
        optionen = format_html_join(
            '',
            '<option value="{}"{}>{}</option>',
            (
                (rang, mark_safe(' selected') if rang == jetzt else '', rang or '–')
                for rang in range(0, bis + 1)
            ),
        )
        return format_html(
            '<td class="num" data-sort="{}"><select class="viewer-select engine2d3dkleider-qualitaet" data-id="{}" '
            'data-feld="{}" data-vorher="{}" title="{}">{}</select></td>',
            jetzt or Engine2d3dKleiderqualitaet.SORT_OHNE_RANG,
            str(a.id),
            schluessel,
            jetzt,
            Engine2d3dKleiderqualitaet.titel(schluessel, jetzt),
            optionen,
        )

    @staticmethod
    def _abweichung(wert):
        """Die Note des besten Modells, vier Stellen mit Komma (`data-sort` ebenso: djangoBase liest einen Punkt als
        Tausendertrenner). Ohne Note sortiert die Zelle ans Ende."""
        if wert is None:
            return '<td class="num" data-sort="999999"></td>'
        text = ('%.4f' % float(wert)).replace('.', ',')
        return format_html('<td class="num" data-sort="{}">{}</td>', text, text)
