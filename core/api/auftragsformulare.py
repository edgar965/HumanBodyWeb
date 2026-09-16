# -*- coding: utf-8 -*-
u"""Auftragsformulare — Starten, Anhalten, Löschen aus den Auftragsseiten.

Die Formularfassungen der drei Vorgänge, herausgelöst aus `Auftragsendpunkte`
(16.09.2026, die Datei stand auf 300 Zeilen). Sie sind das Gegenstück zu den
AJAX-Fassungen dort: Sie leiten auf eine Seite weiter und setzen eine Meldung.
Adressiert werden sie — wie die Seiten selbst — über die `Auftragskennung`
(`/process/<kennung>/start/` …), nicht über die UUID.

DIE EINSTIEGE SIND `@staticmethod`, NICHT `@classmethod`: `@classmethod`
übergibt der umschlossenen Funktion die Klasse als erstes Argument.
`@require_POST` prüft aber `args[0].method` — es bekäme die Klasse statt der
Anfrage und liefe in einen `AttributeError`.

`require_POST` an allen dreien seit 13./17.08.2026: Starten setzt eine
Pipeline auf die Grafikkarte, Löschen nimmt Auftrag UND Dateien — beides war
per GET auslösbar; ein `<img src="…/start/">` auf einer fremden Seite hätte
gereicht. Die Vorlagen schicken POST-Formulare.
"""
import logging

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.auftragssteuerung import Auftragssteuerung
from ..logging_utils import Auftragskontext
from ..models import BVHJob

logger = logging.getLogger('core')
pipeline_logger = logging.getLogger('core.pipeline')


class Auftragsformulare:

    @staticmethod
    def auftrag(kennung):
        return get_object_or_404(BVHJob, kennung=kennung)

    @staticmethod
    @require_POST
    def starten(request, kennung):
        """Auftrag starten oder neu starten."""
        job = Auftragsformulare.auftrag(kennung)
        if job.status in ('pending', 'complete', 'failed'):
            with Auftragskontext.mit_auftrag(str(job.id)):
                pipeline_logger.info('start_processing pipeline=%s name=%s',
                                     job.pipeline, job.name)
                Auftragssteuerung.starten(job)
            messages.info(request, 'Processing started.')
        return redirect('job_status', kennung=job.kennung)

    @staticmethod
    @require_POST
    def anhalten(request, kennung):
        """Laufenden Auftrag abbrechen."""
        job = Auftragsformulare.auftrag(kennung)
        Auftragssteuerung.anhalten(job, herkunft='form')
        messages.info(request, 'Processing stopped.')
        return redirect('job_status', kennung=job.kennung)

    @staticmethod
    @require_POST
    def loeschen(request, kennung):
        """Auftrag samt Dateien löschen; die Rückfrage hängt am `submit`."""
        job = Auftragsformulare.auftrag(kennung)
        name = job.name
        logger.info('delete_job id=%s name=%s pipeline=%s',
                    job.id, name, job.pipeline)
        Auftragssteuerung.dateien_entfernen(job)
        job.delete()
        messages.success(request, 'Deleted %s.' % name)
        return redirect('processed')
