# -*- coding: utf-8 -*-
"""`manage.py mesh3d_varianten <kennung>` — die Varianten eines Mesh-3D-Auftrags nacheinander rechnen.

Der Arbeitsprozess, den `Mesh3dvariantenlauf.starten` startet (13.10.2026): jede wartende Variante (`Meshfigurauftrag.status == 'angelegt'`) in diesem Prozess, ohne Anbindung an den Server.
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet die wartenden Varianten eines Mesh-3D-Auftrags nacheinander in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('kennung', help='Die Kennung des Mesh-3D-Auftrags (Import)')
        parser.add_argument('--warten', action='store_true', help='Erst rechnen, wenn kein anderer Import mehr rechnet (automatische Vergleichsvariante)')

    def handle(self, *args, **options):
        from core.daten.blendimportablage import Blendimportablage
        from core.dienste.mesh3dvariantenlauf import Mesh3dvariantenlauf

        kennung = options['kennung']
        try:
            ablage = Blendimportablage(kennung)
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        if not ablage.stand():
            raise CommandError('Kein Mesh-3D-Auftrag %s' % kennung)
        (ablage.ordner() / Mesh3dvariantenlauf.PID).write_text(str(os.getpid()))
        logger.info('Mesh-3D %s: Varianten-Prozess rechnet', kennung)
        try:
            Mesh3dvariantenlauf.ausfuehren(kennung, warten=options['warten'])
        except Exception:  # noqa: BLE001
            logger.exception('Mesh-3D %s: Varianten-Prozess abgestürzt', kennung)
        finally:
            try:
                (ablage.ordner() / Mesh3dvariantenlauf.PID).unlink()
            except OSError:
                logger.debug('Mesh-3D %s: %s war schon weg', kennung, Mesh3dvariantenlauf.PID)
