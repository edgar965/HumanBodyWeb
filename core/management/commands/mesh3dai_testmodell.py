# -*- coding: utf-8 -*-
"""`manage.py mesh3dai_testmodell <kennung> <geschlecht> <name> [--ziel <ordner>]` — die vorhergesagte Figur eines Tests von Mesh3D-AI mit den gewählten Kleidern als Genesis-Modell speichern
(17.10.2026 nachts, `Mesh3daitestmodell`). Der Arbeitsprozess hinter dem Knopf „Übernehmen und speichern“ der Testseite; `--ziel` schreibt das Modell in einen anderen Ordner (Probelauf).
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Speichert die vorhergesagte Figur eines Mesh3D-AI-Tests mit den gewählten Kleidern (Katalog oder aus dem Netz) als Genesis-Modell.'

    def add_arguments(self, parser):
        parser.add_argument('kennung', help='Kennung des Tests (Ordner unter 3DObjects/mesh3dai/_test)')
        parser.add_argument('geschlecht', choices=('weiblich', 'maennlich'))
        parser.add_argument('name', help='Name des Modells')
        parser.add_argument('--ziel', default=None, help='Ordner für das Modell (Vorgabe: die Modelle der Szene)')

    def handle(self, *args, **options):
        from core.dienste.mesh3daitestmodell import Mesh3daitestmodell
        from core.dienste.mesh3daitestkleider import Mesh3daitestkleider

        if Mesh3daitestkleider.ordner(options['kennung'], options['geschlecht']) is None:
            raise CommandError('Kein Test %s' % options['kennung'])
        name = Mesh3daitestmodell.ausfuehren(options['kennung'], options['geschlecht'], options['name'], options.get('ziel'))
        self.stdout.write('Modell gespeichert: %s' % name)
