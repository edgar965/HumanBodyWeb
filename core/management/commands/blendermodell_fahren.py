# -*- coding: utf-8 -*-
"""`manage.py blendermodell_fahren <id> [--ab <schritt>] [--bis <schritt>]` — ein Auftrag „BlenderModel".

Der Arbeitsprozess, den `Blendermodellarbeiter` startet (29.09.2026): `Blendermodelllauf` in einem
eigenen Prozess, damit der Autoreload des Servers den Lauf nicht mitreißt. Von Hand aufrufbar, etwa
`--ab kostuem --bis kostuem`: nur weitere Runden des Kostüm-Kreislaufs („Weiter iterieren").
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Auftrag „BlenderModel" (Grundfigur → Kostüm → Blender) in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')
        parser.add_argument('--ab', default=None, help='Erster Schritt (Vorgabe: von vorn)')
        parser.add_argument('--bis', default=None, help='Letzter Schritt (Vorgabe: bis zum Ende)')

    def handle(self, *args, **options):
        from core.daten.blendermodellablage import Blendermodellablage
        from core.dienste.blendermodelllauf import Blendermodelllauf
        from core.models import Blendermodellauftrag

        jid = options['job_id']
        job = Blendermodellauftrag.objects.filter(id=jid).first()
        if job is None:
            raise CommandError('Kein Auftrag „BlenderModel" %s' % jid)
        ablage = Blendermodellablage(job.kennung)
        ablage.anlegen()
        ablage.pid().write_text(str(os.getpid()))
        job.pid = os.getpid()
        job.save(update_fields=['pid', 'updated_at'])
        logger.info('BlenderModel %s: Arbeitsprozess rechnet', job.kennung)
        try:
            Blendermodelllauf(jid).ausfuehren(ab=options.get('ab'), bis=options.get('bis'))
        except Exception:  # noqa: BLE001
            logger.exception('BlenderModel %s: Arbeitsprozess abgestürzt', job.kennung)
            job.refresh_from_db()
            if job.status != 'angehalten':
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess abgestürzt (siehe auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
