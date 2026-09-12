# -*- coding: utf-8 -*-
u"""`manage.py auftrag_fahren <id>` — einen Video-to-BVH-Auftrag rechnen.

Das ist der Arbeitsprozess, den `Auftragsarbeiter` für jeden Auftrag startet
(12.09.2026): derselbe `Auftragslauf`, der bis dahin als Faden im Server
lief — nur dass ihn ein Neustart des Entwicklungsservers nicht mehr mitreißt.
Lässt sich auch von Hand rufen, etwa um einen Auftrag nach einem Absturz
weiterzurechnen; die PID-Datei trägt der Prozess dann selbst ein.

Der Server ruft NICHT `Startaufraeumen` in diesem Prozess (`CoreConfig.ready`
tut das nur für `runserver`) — sonst vermerkte der Arbeiter den Auftrag, den
er gerade rechnen soll, als verwaist.
"""
import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = u'Rechnet einen Video-to-BVH-Auftrag in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help=u'Die Kennung des BVHJob')

    def handle(self, *args, **options):
        from core.dienste.auftragsarbeiter import Auftragsarbeiter
        from core.dienste.auftragssteuerung import Auftragssteuerung
        from core.models import BVHJob
        from core.pipelines.auftragslauf import Auftragslauf

        jid = options['job_id']
        if not BVHJob.objects.filter(id=jid).exists():
            raise CommandError(u'Kein Auftrag %s' % jid)
        Auftragsarbeiter.eintragen(jid)
        logger.info('Auftrag %s: Arbeitsprozess rechnet', jid)
        try:
            Auftragslauf(jid).ausfuehren()
        except Exception:                                          # noqa: BLE001
            logger.exception('Auftrag %s: Arbeitsprozess abgestürzt', jid)
            Auftragssteuerung._absturz_vermerken(jid)
        finally:
            Auftragsarbeiter.austragen(jid)
