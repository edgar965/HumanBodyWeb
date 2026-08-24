# -*- coding: utf-8 -*-
"""Attrappen für die Tests — hier, damit es sie nur EINMAL gibt.

`AuftragsAttrappe` stand am 17.08.2026 in VIER Testdateien
(`test_erkennungsfortschritt`, `test_gelenkquelle`, `test_hybridlauf`,
`test_v4lauf`), jedes Mal mit einer anderen Teilmenge der Felder — gemeldet vom
Werkzeug `namens-dubletten`. Wer dem Auftragsmodell ein Feld hinzufügt, das die
Pipelines lesen, soll nicht vier Attrappen suchen müssen.

WARUM ÜBERHAUPT EINE ATTRAPPE
=============================
Ein echter `BVHJob` bräuchte die Datenbank, und die Pipelines schreiben ihren
Fortschritt sehr oft (`save()` je Meldung). Die Attrappe zählt die
Speicherungen stattdessen — daran hängen mehrere Prüfungen, etwa die Drosselung
auf eine Meldung je Sekunde.
"""


class AuftragsAttrappe:
    """Ein `BVHJob`-Doppel: nur die Felder, die die Pipelines anfassen."""

    def __init__(self, pipeline='v4', params=None, kennung=7, name='tanz.mp4'):
        self.id = kennung
        self.name = name
        self.pipeline = pipeline
        self.pipeline_params = params or {}
        self.video_file = 'video.mp4'
        self.status = ''
        self.progress = 0
        self.progress_detail = ''
        self.bvh_file = ''
        self.bvh_file_face = ''
        #: Wie oft `save()` gerufen wurde. Mehrere Prüfungen hängen daran.
        self.speicherungen = 0

    def save(self, *args, **kwargs):
        self.speicherungen += 1

    def get_pipeline_display(self):
        return str(self.pipeline).upper()
