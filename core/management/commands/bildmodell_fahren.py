# -*- coding: utf-8 -*-
"""`manage.py bildmodell_fahren <id> [--ab <schritt>] [--bis <schritt>]` — einen Bildmodell-Auftrag rechnen.

Der Arbeitsprozess, den `Bildmodellarbeiter` startet (19.09.2026) — wie
`auftrag_fahren` für Video → BVH: `Bildmodelllauf` in einem eigenen
Prozess, damit der Autoreload des Servers den Lauf nicht mitreißt. Von Hand
aufrufbar, etwa um ab „anpassung" mit anderen Optionen neu zu rechnen.
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Auftrag „Modell aus Bildern" in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Bildmodellauftrags')
        parser.add_argument('--ab', default='sichtung', help='Erster Schritt (Vorgabe: sichtung)')
        parser.add_argument('--bis', default=None, help='Letzter Schritt (Vorgabe: bis zum Ende)')

    def handle(self, *args, **options):
        from core.daten.bildmodellablage import Bildmodellablage
        from core.dienste.bildmodelllauf import Bildmodelllauf
        from core.models import Bildmodellauftrag

        jid = options['job_id']
        job = Bildmodellauftrag.objects.filter(id=jid).first()
        if job is None:
            raise CommandError('Kein Bildmodell-Auftrag %s' % jid)
        ablage = Bildmodellablage(job.kennung)
        ablage.anlegen()
        ablage.pid().write_text(str(os.getpid()))
        job.pid = os.getpid()
        job.save(update_fields=['pid', 'updated_at'])
        logger.info('Bildmodell %s: Arbeitsprozess rechnet ab %s', job.kennung, options['ab'])
        try:
            Bildmodelllauf(jid).ausfuehren(ab=options['ab'], bis=options.get('bis'))
        except Exception:  # noqa: BLE001
            logger.exception('Bildmodell %s: Arbeitsprozess abgestürzt', job.kennung)
            job.refresh_from_db()
            job.status = 'gescheitert'
            job.error_message = job.error_message or 'Arbeitsprozess abgestürzt (siehe auftrag.log)'
            job.save(update_fields=['status', 'error_message', 'updated_at'])
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
