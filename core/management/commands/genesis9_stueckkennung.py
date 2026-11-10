# -*- coding: utf-8 -*-
"""`manage.py genesis9_stueckkennung <kennung> "<neuer Name>" [--machen]` — Kennung eines eigenen Garderobenstücks ändern (`G9stueckkennung`, 10.11.2026).

Ohne `--machen` nur der Plan: welche Dateien umbenannt, welche Modelle umgehängt werden. Mit `--machen` in einem Zug; danach liest die Garderobe neu.
"""

from django.core.management.base import BaseCommand, CommandError

from core.dienste.g9stueckkennung import G9stueckkennung


class Command(BaseCommand):
    help = 'Kennung eines eigenen Genesis-9-Stücks ändern: Daz-Dateien, Verweise darin, Modelle, Anzeigename'

    def add_arguments(self, parser):
        parser.add_argument('kennung')
        parser.add_argument('name', help='neuer Dateiname des Stücks, z. B. "Edgar Foto-Genesis Uhr"')
        parser.add_argument('--machen', action='store_true', help='ausführen statt nur planen')

    def handle(self, *args, **o):
        try:
            if not o['machen']:
                plan = G9stueckkennung.plan(o['kennung'], o['name'])
                self.stdout.write('%s -> %s (%s)' % (plan['alt'], plan['neu'], plan['name']))
                for a, b in plan['dateien']:
                    self.stdout.write('  %s\n    -> %s' % (a, b))
                if plan['arbeitsordner']:
                    self.stdout.write('  Arbeitsordner %s -> %s' % plan['arbeitsordner'])
                self.stdout.write('  Modelle: %s' % ([p.name for p in plan['modelle']] or 'keine'))
                return
            bilanz = G9stueckkennung.umbenennen(o['kennung'], o['name'])
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        self.stdout.write(self.style.SUCCESS(str(bilanz)))
