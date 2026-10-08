# -*- coding: utf-8 -*-
"""`manage.py blendimport_fahren <kennung> [--ab <schritt>]` — ein Blender-Import (08.10.2026).

Der Arbeitsprozess, den `Blendimportarbeiter` startet: `Blendimportlauf` in einem eigenen Prozess, damit der Autoreload
des Servers den Lauf nicht mitreißt. Von Hand aufrufbar, etwa um ab „haut" mit anderer Kachelgröße neu zu backen.
"""

import logging
import os

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rechnet einen Blender-Import (.blend → Genesis-9-Modell mit eigenen Stücken) in diesem Prozess.'

    def add_arguments(self, parser):
        parser.add_argument('kennung', help='Die Kennung des Imports (Ordner unter 3DObjects/blendimport)')
        parser.add_argument('--ab', default=None, help='Erster Schritt (Vorgabe: von vorn)')

    def handle(self, *args, **options):
        from core.daten.blendimportablage import Blendimportablage
        from core.dienste.blendimportlauf import Blendimportlauf

        try:
            ablage = Blendimportablage(options['kennung'])
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        if not ablage.stand():
            raise CommandError('Kein Blender-Import %s' % options['kennung'])
        ablage.pid().write_text(str(os.getpid()))
        try:
            Blendimportlauf(ablage.kennung).ausfuehren(ab=options.get('ab'))
        except Exception:  # noqa: BLE001
            logger.exception('Blender-Import %s: Arbeitsprozess abgestürzt', ablage.kennung)
            stand = ablage.stand()
            if stand.get('status') != 'angehalten':
                stand.update(status='gescheitert', fehler=stand.get('fehler') or 'Arbeitsprozess abgestürzt (auftrag.log)')
                ablage.stand_schreiben(stand)
        finally:
            if ablage.pid().is_file():
                ablage.pid().unlink()
