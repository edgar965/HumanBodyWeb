# -*- coding: utf-8 -*-
"""`manage.py ai2d3d_modell <job> <geschlecht> <name> [--ziel <ordner>]` — die Figur aus den Fotos eines 2d-3d-AI-Jobs mit ihren Stücken als Genesis-Modell speichern
(31.10.2026, `Ai2d3dmodell`). Der Arbeitsprozess hinter „Als Modell speichern“ der Exportleiste auf der Jobseite; `--ziel` schreibt das Modell in einen anderen Ordner (Probelauf).
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Speichert die Figur aus den Fotos eines 2d-3d-AI-Jobs mit ihren Stücken als Genesis-Modell.'

    def add_arguments(self, parser):
        parser.add_argument('job', help='Kennung des Jobs (Ordner unter 3DObjects/ai2d3d)')
        parser.add_argument('geschlecht', choices=('weiblich', 'maennlich'))
        parser.add_argument('name', help='Name des Modells')
        parser.add_argument('--ziel', default=None, help='Ordner für das Modell (Vorgabe: die Modelle der Szene)')

    def handle(self, *args, **options):
        from core.dienste.ai2d3dmodell import Ai2d3dmodell

        if Ai2d3dmodell.ordner(options['job'], options['geschlecht']) is None:
            raise CommandError('Keine Figur für Job %s (%s)' % (options['job'], options['geschlecht']))
        name = Ai2d3dmodell.ausfuehren(options['job'], options['geschlecht'], options['name'], options.get('ziel'))
        self.stdout.write('Modell gespeichert: %s' % name)
