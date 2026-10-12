# -*- coding: utf-8 -*-
"""`manage.py mesh3d_netzansicht <kennung>` — die vereinfachte Netz-Kopie für die 3D-Ansicht eines Mesh-3D-Auftrags (11.10.2026).

Der Arbeitsprozess, den `Mesh3dnetzansicht.anstossen` startet: Die Vereinfachung eines Netzes mit zwei Millionen Dreiecken dauert über eine Minute
und läuft deshalb nicht im Server (Autoreload, Faden der Ansichten).
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Baut die vereinfachte Netz-Kopie für die 3D-Ansicht eines Mesh-3D-Auftrags.'

    def add_arguments(self, parser):
        parser.add_argument('kennung', help='Die Kennung des Auftrags (Ordner unter 3DObjects/blendimport)')

    def handle(self, *args, **options):
        from core.dienste.mesh3dnetzansicht import Mesh3dnetzansicht

        try:
            ansicht = Mesh3dnetzansicht(options['kennung'])
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        try:
            flaechen = ansicht.bauen()
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler wird gemerkt, die Bühne lädt dann das Original
            logger.exception('Mesh-3D %s: Netzansicht nicht gebaut', options['kennung'])
            ansicht.fehler_merken('%s: %s' % (type(fehler).__name__, fehler))
            raise CommandError('Netzansicht nicht gebaut: %s' % fehler) from fehler
        self.stdout.write('Netzansicht %s: %d Dreiecke' % (options['kennung'], flaechen))
