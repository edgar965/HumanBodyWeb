# -*- coding: utf-8 -*-
"""`manage.py makehumangenital_bauen` — MakeHumans Genitalien als Stück „MakeHuman Penis" der eigenen Garderobe (18.10.2026).

Liest MakeHumans Genitalhelfer und seine drei Ziele (`MakeHuman/makehuman/data`, nur lesen) und schreibt das Stück mit sechs Reglern und den eigenen
Reglern des Penis (`Makehumangenital`). Wiederholbar: das Stück und seine Regler werden neu geschrieben.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Baut MakeHumans Genitalhelfer mit seinen Zielen als Stück „MakeHuman Penis".'

    def handle(self, *args, **options):
        from core.dienste.makehumangenital import Makehumangenital

        try:
            bilanz = Makehumangenital().bauen()
        except (ValueError, OSError) as fehler:
            raise CommandError(str(fehler)) from fehler
        self.stdout.write('Stück %s: %d Punkte, %d Flächen — %s' % (bilanz['stueck'], bilanz['punkte'], bilanz['flaechen'], bilanz['duf']))
        self.stdout.write('Bericht: %s' % bilanz['bericht'])
