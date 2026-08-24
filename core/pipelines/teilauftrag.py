# -*- coding: utf-8 -*-
"""Teilauftrag — ein Auftrags-Doppel für eine Unter-Pipeline.

Der Hybridlauf fährt zwei Pipelines gleichzeitig (Körper und Gesicht) und ruft
dafür `_run_smpl_pipeline` bzw. `_run_v4_pipeline`. Beide erwarten ein
`BVHJob`-artiges Objekt: sie lesen `pipeline_params`, schreiben `progress` und
`progress_detail` und rufen `save()`.

WARUM KEIN ECHTER `BVHJob` (Stand 17.08.2026)
=============================================
Zwei Gründe, und der zweite ist der wichtige:

* Die Unteraufträge dürfen **nicht in die Datenbank schreiben** — sonst
  überschreiben sich Körper- und Gesichtsfortschritt gegenseitig im
  Auftragsdatensatz. `save()` tut hier absichtlich nichts; der Hybridlauf liest
  die beiden Fortschritte und schreibt EINE Zeile in den echten Auftrag.
* Jeder Unterauftrag braucht eine **eigene Kennung** (`<id>_body`, `<id>_face`),
  weil die Prozessverwaltung (`LaufendeProzesse`) je Kennung einen
  Unterprozess führt. Mit derselben Kennung würde „Abbrechen" beim Gesicht den
  Körperlauf treffen.

Herausgelöst aus `hybridlauf._run_hybrid_pipeline` (164 Zeilen, Grenze 60): Die
Klasse stand dort als lokale Klasse IN der Funktion und schloss über die Closure
`job.id` und `body_backend` ein — dadurch war sie nicht einzeln prüfbar.
"""


class Teilauftrag:
    """Auftrags-Doppel für eine Unter-Pipeline: schreibt nichts, merkt sich alles."""

    def __init__(self, pipeline, params, name, kennung, anzeige=''):
        self.pipeline = pipeline
        self.pipeline_params = params
        self.name = name
        self.id = kennung
        self.status = 'processing'
        self.progress = 0
        self.progress_detail = ''
        #: Was `get_pipeline_display()` liefert — die Unter-Pipelines zeigen den
        #: Namen im Fortschritt an.
        self.anzeige = anzeige or str(pipeline).upper()

    def save(self, **kw):
        """Absichtlich leer — siehe Modul-Docstring."""

    def get_pipeline_display(self):
        return self.anzeige
