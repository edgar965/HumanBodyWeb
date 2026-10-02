# -*- coding: utf-8 -*-
"""`manage.py engine2d3dkleider_standmodell <id>` — das 3D-Modell des letzten Stands eines Auftrags „2D3D Kleider" bauen.

Der kurze Arbeitsprozess, den die Bühne bestellt (`POST /api/engine2d3dkleider/<id>/standmodell/`), wenn die Datei fehlt
oder veraltet ist (`Engine2d3dKleiderstandmodell`). Ein eigener Prozess, weil der Bau Genesis-Netze rechnet (Sekunden) — im
Server hielte er jede andere Anfrage auf. Die PID liegt in `arbeit/stand.pid`, solange er läuft.
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Baut das 3D-Modell des letzten Stands eines Auftrags „2D3D Kleider" (ergebnis/stand_<fassung>.glb).'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')

    def handle(self, *args, **options):
        from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from core.dienste.engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
        from core.models import Engine2d3dKleiderauftrag

        job = Engine2d3dKleiderauftrag.objects.filter(id=options['job_id']).first()
        if job is None:
            raise CommandError('Kein Auftrag „2D3D Kleider" %s' % options['job_id'])
        ablage = Engine2d3dKleiderablage(job.kennung)
        pid = ablage.arbeit('stand.pid')
        pid.parent.mkdir(parents=True, exist_ok=True)
        pid.write_text(str(os.getpid()))
        stand = Engine2d3dKleiderstandmodell(job, ablage)
        try:
            stand.bauen()
        except Exception as fehler:  # noqa: BLE001 — der Fehler gehört ins Log des Auftrags, die Bühne baut dann im Browser
            logger.exception('2D3D Kleider %s: Modell des Stands nicht gebaut', job.kennung)
            stand.scheitern(fehler)
        finally:
            if pid.is_file():
                pid.unlink()
