# -*- coding: utf-8 -*-
"""`manage.py mesh_fahren <id> [--ab <schritt>]` — ein Mesh-Auftrag (Reiter „Mesh").

Der Arbeitsprozess, den `Mesharbeiter` startet (26.09.2026): `Meshlauf` in einem
eigenen Prozess, damit der Autoreload des Servers den Lauf nicht mitreißt. Von Hand
aufrufbar, etwa um ab „textur" mit anderen Optionen neu zu rechnen.
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Mesh-Auftrag (Fotos → Netz) in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Meshauftrags')
        parser.add_argument('--ab', default=None, help='Erster Schritt (Vorgabe: von vorn)')

    def handle(self, *args, **options):
        from core.daten.meshablage import Meshablage
        from core.dienste.meshlauf import Meshlauf
        from core.models import Meshauftrag

        jid = options['job_id']
        job = Meshauftrag.objects.filter(id=jid).first()
        if job is None:
            raise CommandError('Kein Mesh-Auftrag %s' % jid)
        ablage = Meshablage(job.kennung)
        ablage.anlegen()
        ablage.pid().write_text(str(os.getpid()))
        job.pid = os.getpid()
        job.save(update_fields=['pid', 'updated_at'])
        logger.info('Mesh %s: Arbeitsprozess rechnet', job.kennung)
        try:
            Meshlauf(jid).ausfuehren(ab=options.get('ab'))
        except Exception:  # noqa: BLE001
            logger.exception('Mesh %s: Arbeitsprozess abgestürzt', job.kennung)
            job.refresh_from_db()
            job.status = 'gescheitert'
            job.error_message = job.error_message or 'Arbeitsprozess abgestürzt (siehe auftrag.log)'
            job.save(update_fields=['status', 'error_message', 'updated_at'])
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
