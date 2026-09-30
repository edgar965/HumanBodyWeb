# -*- coding: utf-8 -*-
"""`manage.py haarengine_fahren <id> [--ab <schritt>] [--bis <schritt>]` — ein Auftrag „Haar Engine".

Der Arbeitsprozess, den `Haarenginearbeiter` startet: `Haarenginelauf` in einem eigenen Prozess, damit der
Autoreload des Servers den Lauf nicht mitreißt. Von Hand aufrufbar, etwa `--ab iterationen --bis
iterationen`: nur weitere Runden der Iterationen („Weiter iterieren").
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Auftrag „Haar Engine" (Grundfigur → Iterationen → Film) in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')
        parser.add_argument('--ab', default=None, help='Erster Schritt (Vorgabe: von vorn)')
        parser.add_argument('--bis', default=None, help='Letzter Schritt (Vorgabe: bis zum Ende)')

    def handle(self, *args, **options):
        from core.daten.haarengineablage import Haarengineablage
        from core.dienste.haarenginelauf import Haarenginelauf
        from core.models import Haarengineauftrag

        jid = options['job_id']
        job = Haarengineauftrag.objects.filter(id=jid).first()
        if job is None:
            raise CommandError('Kein Auftrag „Haar Engine" %s' % jid)
        ablage = Haarengineablage(job.kennung)
        ablage.anlegen()
        ablage.pid().write_text(str(os.getpid()))
        job.pid = os.getpid()
        job.save(update_fields=['pid', 'updated_at'])
        logger.info('Haar Engine %s: Arbeitsprozess rechnet', job.kennung)
        try:
            Haarenginelauf(jid).ausfuehren(ab=options.get('ab'), bis=options.get('bis'))
        except Exception:  # noqa: BLE001
            logger.exception('Haar Engine %s: Arbeitsprozess abgestürzt', job.kennung)
            job.refresh_from_db()
            if job.status != 'angehalten':
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess abgestürzt (siehe auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
