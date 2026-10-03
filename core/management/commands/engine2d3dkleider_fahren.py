# -*- coding: utf-8 -*-
"""`manage.py engine2d3dkleider_fahren <id> [--ab <schritt>] [--bis <schritt>]` — ein Auftrag „2D3D Kleider".

Der Arbeitsprozess, den `Engine2d3dKleiderarbeiter` startet: `Engine2d3dKleiderlauf` in einem eigenen Prozess, damit der
Autoreload des Servers den Lauf nicht mitreißt. Von Hand aufrufbar, etwa `--ab iterationen --bis
iterationen`: nur weitere Runden der Iterationen („Weiter iterieren").
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Auftrag „2D3D Kleider" (Grundfigur → Iterationen → Film) in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')
        parser.add_argument('--ab', default=None, help='Erster Schritt (Vorgabe: von vorn)')
        parser.add_argument('--bis', default=None, help='Letzter Schritt (Vorgabe: bis zum Ende)')

    def handle(self, *args, **options):
        from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
        from core.models import Engine2d3dKleiderauftrag

        jid = options['job_id']
        job = Engine2d3dKleiderauftrag.objects.filter(id=jid).first()
        if job is None:
            raise CommandError('Kein Auftrag „2D3D Kleider" %s' % jid)
        ablage = Engine2d3dKleiderablage(job.kennung)
        ablage.anlegen()
        ablage.pid().write_text(str(os.getpid()))
        job.pid = os.getpid()
        job.save(update_fields=['pid', 'updated_at'])
        logger.info('2D3D Kleider %s: Arbeitsprozess rechnet', job.kennung)
        try:
            Engine2d3dKleiderlauf(jid).ausfuehren(ab=options.get('ab'), bis=options.get('bis'))
        except Exception:  # noqa: BLE001
            logger.exception('2D3D Kleider %s: Arbeitsprozess abgestürzt', job.kennung)
            job.refresh_from_db()
            if job.status != 'angehalten':
                job.status = 'gescheitert'
                job.error_message = job.error_message or 'Arbeitsprozess abgestürzt (siehe auftrag.log)'
                job.save(update_fields=['status', 'error_message', 'updated_at'])
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
