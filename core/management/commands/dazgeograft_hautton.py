# -*- coding: utf-8 -*-
"""`manage.py dazgeograft_hautton --name "Hautton cute girl" --farbe 214,168,155 [--geschlecht frau]` — eine Hautton-Variante des Daz-Geografts (10.10.2026).

Das Stück hat keine Textur und steht ohne Variante in der Mittelfarbe der Basishaut (160/121/104). Trägt ein Modell eine Fototextur-Haut (cute girl), schreibt dieser Befehl
neben das Stück ein Materialpreset nur mit der Diffusfarbe (`Dazgeograftvarianten.hautton`); im Modell wählt man es dann als Variante des Stücks.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Schreibt eine Hautton-Variante (nur Diffusfarbe) neben das Daz-Geograft-Stück.'

    def add_arguments(self, parser):
        parser.add_argument('--geschlecht', default='frau', choices=['mann', 'frau'])
        parser.add_argument('--name', required=True, help='Name der Variante, z. B. „Hautton cute girl"')
        parser.add_argument('--farbe', required=True, help='sRGB 0 … 255, z. B. 214,168,155')

    def handle(self, *args, **options):
        from core.dienste.dazgeograft import Dazgeograft
        from core.dienste.dazgeograftvarianten import Dazgeograftvarianten
        from Genesis9.pfade import G9pfade

        try:
            rgb = [int(w) for w in options['farbe'].split(',')]
        except ValueError as fehler:
            raise CommandError('--farbe: drei ganze Zahlen mit Komma, z. B. 214,168,155') from fehler
        if len(rgb) != 3 or not all(0 <= w <= 255 for w in rgb):
            raise CommandError('--farbe: genau drei Werte von 0 bis 255')
        geschlecht = options['geschlecht']
        stueck = G9pfade.eigene() / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / ('%s.duf' % Dazgeograft.NAMEN[geschlecht][0])
        if not stueck.is_file():
            raise CommandError('Das Stück %s fehlt — erst `dazgeograft_einbauen --geschlecht %s`' % (stueck.name, geschlecht))
        name = Dazgeograftvarianten.hautton(stueck, geschlecht, Dazgeograft.GRUPPEN[geschlecht], options['name'], rgb)
        self.stdout.write('Variante „%s" neben %s geschrieben (Farbe %s)' % (name, stueck.name, options['farbe']))
