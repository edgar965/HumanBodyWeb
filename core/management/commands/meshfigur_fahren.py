# -*- coding: utf-8 -*-
"""`manage.py meshfigur_fahren <id> [--ab <schritt>]` — ein Auftrag „Mesh to 3D".

Der Arbeitsprozess, den `Meshfigurarbeiter` startet (27.09.2026): `Meshfigurlauf` in einem
eigenen Prozess, damit der Autoreload des Servers den Lauf nicht mitreißt. Von Hand aufrufbar,
etwa um ab „gesicht" mit anderen Optionen neu zu rechnen.
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Auftrag „Mesh to 3D" (Netz → Genesis-9-Figur) in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')
        parser.add_argument('--ab', default=None, help='Erster Schritt (Vorgabe: von vorn)')

    def handle(self, *args, **options):
        from core.daten.meshfigurablage import Meshfigurablage
        from core.dienste.meshfigurlauf import Meshfigurlauf
        from core.models import Meshfigurauftrag

        jid = options['job_id']
        job = Meshfigurauftrag.objects.filter(id=jid).first()
        if job is None:
            raise CommandError('Kein Auftrag „Mesh to 3D" %s' % jid)
        ablage = Meshfigurablage(job.kennung)
        ablage.anlegen()
        ablage.pid().write_text(str(os.getpid()))
        job.pid = os.getpid()
        job.save(update_fields=['pid', 'updated_at'])
        logger.info('Mesh to 3D %s: Arbeitsprozess rechnet', job.kennung)
        try:
            Meshfigurlauf(jid).ausfuehren(ab=options.get('ab'))
        except Exception:  # noqa: BLE001
            logger.exception('Mesh to 3D %s: Arbeitsprozess abgestürzt', job.kennung)
            job.refresh_from_db()
            if job.status != 'angehalten':
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess abgestürzt (siehe auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
