# -*- coding: utf-8 -*-
"""`manage.py durchschimmern_probe` — die Abnahme des Fitting-Konzepts.

    manage.py durchschimmern_probe g9_base_shirt angie_jeans
    manage.py durchschimmern_probe --alle --posen de_g9_base_05_standing
    manage.py durchschimmern_probe g9_base_shirt --ohne-bilder

Je Stueck und Daz-Pose: Stoffpunkte im Koerper (gehaeutet wie die GPU, und
an die Oberflaeche gebunden) und Hautpixel vor dem Stoff aus vier Ansichten;
Kontaktbogen je Stueck nach `ProjektTemp/durchschimmern/<kennung>.jpg`.
Rechnet Sekunden je Stueck und Pose — NICHT nebenbei starten
(`core/dienste/durchschimmerprobe.py`).
"""

from django.core.management.base import BaseCommand, CommandError

from ui.settings.wurzeln import TOOLS_ROOT


class Command(BaseCommand):
    help = 'Durchschimmern je Kleidungsstueck und Daz-Pose messen und rendern'

    def add_arguments(self, parser):
        parser.add_argument('kennungen', nargs='*', help='Kennungen der Daz-Stuecke')
        parser.add_argument('--alle', action='store_true', help='alle Stuecke der Art kleidung')
        parser.add_argument('--posen', nargs='*', help='Daz-Posen-Kennungen')
        parser.add_argument('--stufen', type=int, default=None)
        parser.add_argument('--ohne-bilder', action='store_true', help='nur Zahlen, kein pyrender')
        parser.add_argument('--ziel', default=str(TOOLS_ROOT / 'ProjektTemp' / 'durchschimmern'))

    def handle(self, *args, **opt):
        from Genesis9.garderobe import G9garderobe
        from Genesis9.pfade import G9pfade

        from core.dienste.durchschimmerprobe import Durchschimmerprobe

        if not G9pfade.vorhanden():
            raise CommandError('Daz-Bibliothek nicht gefunden')
        kennungen = list(opt['kennungen'] or [])
        if opt['alle']:
            kennungen = [e['id'] for e in G9garderobe.liste() if e.get('art') == 'kleidung' and e.get('zeigbar')]
        if not kennungen:
            raise CommandError('Kennungen angeben oder --alle')
        probe = Durchschimmerprobe(posen=opt['posen'], stufen=opt['stufen'], ziel=opt['ziel'],
                                   rendern=not opt['ohne_bilder'])
        zeilen = probe.laufen(kennungen)
        self.stdout.write('%-22s %-14s %-24s %-9s %7s %6s %7s %6s' % (
            'Stueck', 'Teil', 'Pose', 'Weg', 'Punkte', 'innen', '%', 'Pixel'))
        schlecht = 0
        for z in zeilen:
            self.stdout.write('%-22s %-14s %-24s %-9s %7d %6d %6.2f %6s' % (
                z['kennung'][:22], z['teil'][:14], z['pose'][:24], z['weg'], z['punkte'], z['innen'],
                z['anteil'], '-' if z['pixel'] is None else z['pixel']))
            if z['weg'] == 'gebunden' and z['pixel']:
                schlecht += 1
        self.stdout.write('Kontaktboegen: %s' % opt['ziel'])
        if schlecht:
            self.stdout.write(self.style.WARNING('%d gebundene Bilder mit Hautpixeln' % schlecht))
