# -*- coding: utf-8 -*-
"""`manage.py dazgeograft_anpassen --modell "cute girl" --scham "cute girl Scham" [--name …] [--aufloesung 1024] [--steifigkeit 3]` — Daz-Geograft an die Scham eines Imports anpassen (10.10.2026).

Baut das Stück „<Modell> Daz Scham" (`Dazgeograftangepasst`): das Geograft „Anatomical Elements" (Frau) auf der Figur des gespeicherten Modells, angepasst an die vorgegebene Scham des
Blender-Imports, mit Farbe, Rauheit und Normalen daraus. Wiederholbar; die Bake-Bilder liegen unter `3DObjects/models/Genesis9/eigene_stuecke/<Kennung>/gebacken`.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Passt das Daz-Geograft an die Scham eines Blender-Imports an und backt dessen Textur darauf.'

    def add_arguments(self, parser):
        parser.add_argument('--modell', required=True, help='Name des gespeicherten Modells, z. B. „cute girl"')
        parser.add_argument('--scham', required=True, help='Anzeigename des Scham-Stücks des Imports, z. B. „cute girl Scham"')
        parser.add_argument('--name', default=None, help='Name des neuen Stücks (Vorgabe: „<Modell> Daz Scham")')
        parser.add_argument('--aufloesung', type=int, default=1024, help='Kantenlänge der gebackenen Bilder in Pixeln (Vorgabe 1024)')
        parser.add_argument('--steifigkeit', type=float, default=None, help='Steifigkeit der Anpassung (Vorgabe siehe `Dazgeograftanpassung.STEIFIGKEIT`)')

    def handle(self, *args, **options):
        from core.dienste.dazgeograftangepasst import Dazgeograftangepasst

        try:
            bau = Dazgeograftangepasst(options['modell'], options['scham'], options['name'], options['aufloesung'], options['steifigkeit'])
            bilanz = bau.bauen()
        except (ValueError, FileNotFoundError, OSError) as fehler:
            raise CommandError(str(fehler)) from fehler
        self.stdout.write('Stück %s: %d Punkte, %d Flächen — %s' % (bilanz['stueck'], bilanz['punkte'], bilanz['flaechen'], bilanz['duf']))
        self.stdout.write('Bericht: %s' % {k: v for k, v in bilanz['bericht'].items() if k != 'loch'})
