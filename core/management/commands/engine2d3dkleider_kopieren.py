# -*- coding: utf-8 -*-
"""`manage.py engine2d3dkleider_kopieren <quelle> <ziel>` — den gerechneten Stand eines Auftrags „2D3D Kleider" in einen leeren Auftrag kopieren.

Beide Angaben sind die Kennungen der Seiten (z. B. `2026.10.04.11.11.44`). Was mitgeht und was nicht: `Engine2d3dKleiderauftragskopie`.
`--pruefen` zeigt nur, ob und was kopiert würde.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Kopiert den gerechneten Stand eines Auftrags „2D3D Kleider“ in einen leeren Auftrag (Dateien und Zeile).'

    def add_arguments(self, parser):
        parser.add_argument('quelle', help='Kennung des gerechneten Auftrags')
        parser.add_argument('ziel', help='Kennung des leeren Auftrags (Status „angelegt“)')
        parser.add_argument('--pruefen', action='store_true', help='Nur prüfen und zählen, nichts schreiben')
        parser.add_argument('--alles', action='store_true', help='Auch Renderläufe, tmp und Protokoll mitnehmen (Vorgabe: ohne)')

    def handle(self, *args, **options):
        from core.dienste.engine2d3dkleiderauftragskopie import Engine2d3dKleiderauftragskopie

        try:
            kopie = Engine2d3dKleiderauftragskopie.von_kennungen(options['quelle'], options['ziel'])
            kopie.mit_allem = options['alles']
            kopie.pruefen()
        except ValueError as fehler:
            raise CommandError(str(fehler)) from None
        dateien = kopie.dateien()
        self.stdout.write('%s (%s) → %s (%s): %d Dateien, %.1f MB' % (
            kopie.quelle.name, kopie.quelle.kennung, kopie.ziel.name, kopie.ziel.kennung, len(dateien), sum(d[0].stat().st_size for d in dateien) / 1e6))
        if options['pruefen']:
            self.stdout.write('Nur geprüft, nichts geschrieben.')
            return
        try:
            ergebnis = kopie.kopieren()
        except (ValueError, OSError) as fehler:
            raise CommandError('Kopie gescheitert: %s' % fehler) from None
        self.stdout.write(self.style.SUCCESS('Kopiert: %(dateien)d neue Dateien, %(mb)s MB, %(umgeschrieben)d Textdateien umgeschrieben' % ergebnis))
