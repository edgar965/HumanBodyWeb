# -*- coding: utf-8 -*-
u"""Auftragstabelle — die Liste der Video-Aufträge als djangoBase-Tabelle.

Edgar (12.09.2026): „mache die Tabelle mit den Jobs mit der djangoBase
Vorlage für Tabellen, mit sortierbaren Spalten, Checkbox auswählen, Multi-
Select mit Shift und Batch-Delete".

Bis dahin stand die Tabelle handgeschrieben in `_auftragstabelle.html`: Sie
trug zwar `db-tabelle sortable`, aber `tabellen.css` lud die Seite nicht (kein
Zellgitter), das Kästchen-Feld im Kopf sortierte mit, und die Spalten hießen
„Size", „Created", „Actions". Jetzt baut diese Klasse die Struktur, die
`djangobase/_tabelle.html` erwartet — Kopf, Zeilen, Sortier-Rohwerte —, und
die Vorlage rendert sie wie jede andere Tabelle des Hauses.

DAS DRAHTFORMAT ZU `auftragsliste.js` BLEIBT: `data-id` an der Zeile (so
sieht es `_tabelle.html` vor), `status-<id>` an der Statuszelle,
`pl-<id>` am Auswahlfeld, `job-check` an den Kästchen, `select-all` im Kopf,
`data-aktion`/`data-auftrag` an den Knöpfen.
"""
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import template_localtime


class Auftragstabelle:
    u"""Baut die Tabellen-Struktur für `djangobase/_tabelle.html`."""

    #: Kopf: Kästchen, Name, Pipeline, Status, Größe, Erstellt, Verarbeiten,
    #: Aktionen. Kästchen und Knöpfe sortieren nicht — ein Pfeil daneben
    #: verspräche eine Ordnung, die es nicht gibt.
    SPALTEN = (
        {'label': '<input type="checkbox" id="select-all" '
                  'title="alle auswählen / Auswahl aufheben">',
         'key': 'wahl', 'sortAus': True,
         'titel': 'Kästchen wählt eine Zeile; Shift-Klick wählt alle Zeilen '
                  'bis zur zuletzt angeklickten'},
        {'label': 'Name', 'key': 'name'},
        {'label': 'Pipeline', 'key': 'pipeline'},
        {'label': 'Status', 'key': 'status'},
        {'label': 'Größe', 'key': 'groesse', 'num': True},
        {'label': 'Erstellt', 'key': 'erstellt'},
        {'label': 'Verarbeiten', 'key': 'verarbeiten', 'sortAus': True,
         'titel': 'Pipeline wählen und starten — eine andere Pipeline legt '
                  'einen neuen Auftrag an, der alte bleibt'},
        {'label': 'Aktionen', 'key': 'aktionen', 'sortAus': True},
    )

    #: Statuszelle je Endzustand: (Klasse, Symbol, Text). Was läuft, bekommt
    #: den Fortschrittsbalken (`_laeuft`).
    ZUSTAENDE = {
        'complete': ('hb-gut', 'fa-check-circle', 'Fertig'),
        'failed': ('hb-schlecht', 'fa-times-circle', 'Fehlgeschlagen'),
        'pending': ('hb-laeuft', 'fa-clock', 'Wartet'),
    }

    #: Klasse der `<table>` — dort hängt das Eigene (Kästchenspalte, gewählte
    #: Zeile) in `auftragstabelle.css`.
    KLASSE = 'auftragstabelle'

    def __init__(self, auftraege, schluessel, pipelines):
        u"""@param auftraege BVHJob-Liste mit `video_size`/`video_size_display`
        (hängt `Dateigroessen.anhaengen` an)
        @param schluessel `data-sort-key` — djangoBase merkt Sortierung und
        Spaltenbreiten darunter
        @param pipelines [(wert, beschriftung)] für das Auswahlfeld je Zeile"""
        self.auftraege = auftraege
        self.schluessel = schluessel
        self.pipelines = list(pipelines)

    def tabelle(self):
        # Dictionary gewollt: geht unverändert in `djangobase/_tabelle.html`.
        return {'key': self.schluessel,
                'spalten': [dict(s) for s in self.SPALTEN],
                'zeilen': [self.zeile(a) for a in self.auftraege],
                'leer': 'keine Aufträge',
                'klasse': self.KLASSE}

    # ---------------------------------------------------------------- Zeile

    def zeile(self, job):
        u"""Eine Zeile — `id` wird zu `data-id`, `html` ist die Zellenkette."""
        # Dictionary gewollt: Zeilenform von `_tabelle.html`.
        return {'id': str(job.id),
                'html': ''.join((self._kaestchen(job), self._name(job),
                                 self._pipeline(job), self._status(job),
                                 self._groesse(job), self._erstellt(job),
                                 self._verarbeiten(job), self._aktionen(job)))}

    @staticmethod
    def _kaestchen(job):
        return format_html('<td class="kaestchen"><input type="checkbox" '
                           'class="job-check" value="{}"></td>', job.id)

    @staticmethod
    def _name(job):
        return format_html('<td>{}</td>', job.name)

    @staticmethod
    def _pipeline(job):
        return format_html('<td><span class="badge badge-{}">{}</span></td>',
                           job.pipeline, job.get_pipeline_display())

    def _status(self, job):
        u"""Sortiert wird nach dem Text — „Fehlgeschlagen" vor „Fertig" vor
        „Wartet", und die laufenden nach ihrem Fortschritt."""
        ende = self.ZUSTAENDE.get(job.status)
        if ende:
            klasse, symbol, text = ende
            inhalt = format_html('<span class="{}"><i class="fas {}"></i> {}'
                                 '</span>', klasse, symbol, text)
            return format_html('<td id="status-{}" data-sort="{}">{}</td>',
                               job.id, text, inhalt)
        return format_html('<td id="status-{}" data-sort="läuft {}">{}</td>',
                           job.id, '%03d' % int(job.progress or 0),
                           self._laeuft(job))

    @staticmethod
    def _laeuft(job):
        u"""Fortschritt in der Zeile — dieselbe Form schreibt
        `Auftragszeile._statuszelle` beim Nachfragen."""
        text = (job.progress_detail or job.get_status_display())[:30]
        prozent = int(job.progress or 0)
        return format_html(
            '<div class="inline-progress"><span class="status-text">'
            '<i class="fas fa-spinner fa-spin"></i> {}</span>'
            '<div class="progress-bar-mini"><div class="progress-fill-mini" '
            'style="width:{}%"></div></div>'
            '<span class="progress-pct">{}%</span></div>', text, prozent, prozent)

    @staticmethod
    def _groesse(job):
        return format_html('<td class="num" data-sort="{}">{}</td>',
                           getattr(job, 'video_size', 0),
                           getattr(job, 'video_size_display', ''))

    @staticmethod
    def _erstellt(job):
        wann = template_localtime(job.created_at)
        return format_html('<td data-sort="{}">{}</td>',
                           wann.strftime('%Y-%m-%d %H:%M:%S'),
                           wann.strftime('%d.%m.%Y %H:%M'))

    def _verarbeiten(self, job):
        optionen = ''.join(
            format_html('<option value="{}"{}>{}</option>', wert,
                        ' selected' if wert == job.pipeline else '', text)
            for wert, text in self.pipelines)
        return format_html(
            '<td><div class="hb-zeilenaktionen">'
            '<select class="pipeline-select" id="pl-{id}" data-current="{p}">'
            '{opt}</select>'
            '<button class="btn btn-sm btn-primary" data-aktion="start" '
            'data-auftrag="{id}" title="starten"><i class="fas fa-play"></i>'
            '</button></div></td>',
            id=job.id, p=job.pipeline, opt=mark_safe(optionen))

    @staticmethod
    def _aktionen(job):
        teile = []
        if job.status == 'complete':
            teile.append(format_html(
                '<a class="btn btn-sm btn-primary" href="{}">'
                '<i class="fas fa-eye"></i> Ergebnis</a>',
                reverse('job_result', args=[job.id])))
        elif job.status != 'pending':
            teile.append(format_html(
                '<a class="btn btn-sm btn-secondary" href="{}">'
                '<i class="fas fa-info-circle"></i> Status</a>',
                reverse('job_status', args=[job.id])))
        teile.append(format_html(
            '<button class="btn btn-sm btn-danger" data-aktion="delete" '
            'data-auftrag="{}" title="löschen"><i class="fas fa-trash"></i>'
            '</button>', job.id))
        return mark_safe('<td class="hb-zeilenaktionen">%s</td>' % ''.join(teile))
