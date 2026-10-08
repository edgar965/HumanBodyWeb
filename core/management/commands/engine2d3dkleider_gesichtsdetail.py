# -*- coding: utf-8 -*-
"""`manage.py engine2d3dkleider_gesichtsdetail <id> <fassung>` — die Bilderreihen Augen/Mund/Nase des Reiters „Gesicht" eines Auftrags „2D3D Kleider" rendern.

Ein eigener kurzer Prozess (pyrender braucht einen GL-Kontext, den kein Anfrage-Faden des Servers halten soll), bestellt von `Engine2d3dKleiderGesichtsdetail`.
Schreibt `ergebnis/gesicht_<bereich>_<fassung>.png`.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Rendert die Bilderreihen Augen, Mund und Nase (Mesh gegen Modell) für den Reiter „Gesicht" eines Auftrags „2D3D Kleider".'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')
        parser.add_argument('fassung', help='Der Fassungsname der Dateien (Teil des Dateinamens)')

    def handle(self, *args, **options):
        from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from core.dienste.engine2d3dkleidergesichtsdetailrender import Engine2d3dKleiderGesichtsdetailrender
        from core.models import Engine2d3dKleiderauftrag

        job = Engine2d3dKleiderauftrag.objects.filter(id=options['job_id']).first()
        if job is None:
            raise CommandError('Kein Auftrag „2D3D Kleider" %s' % options['job_id'])
        try:
            namen = Engine2d3dKleiderGesichtsdetailrender.erzeugen(job, Engine2d3dKleiderablage(job.kennung), options['fassung'])
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        self.stdout.write('gerendert: %s' % ', '.join(namen))
