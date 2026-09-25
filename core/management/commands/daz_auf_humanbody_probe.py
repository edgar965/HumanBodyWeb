# -*- coding: utf-8 -*-
"""`manage.py daz_auf_humanbody_probe` — jedes Genesis-Kleidungsstück auf HumanBody.

    manage.py daz_auf_humanbody_probe                   alle, weiblich und männlich
    manage.py daz_auf_humanbody_probe --nur gc_         nur Stücke mit „gc_" in Kennung/Name
    manage.py daz_auf_humanbody_probe --geschlecht female
    manage.py daz_auf_humanbody_probe --neu             auch schon geprüfte neu

Bilder und `ergebnis.json` nach `ProjektTemp/hbprobe/`; ein abgebrochener Lauf setzt
fort. Rechnet je Stück Sekunden auf CPU/GPU — nicht nebenbei starten
(`core/dienste/hbkleidprobe.py`).
"""
from django.core.management.base import BaseCommand

from ui.settings.wurzeln import TOOLS_ROOT


class Command(BaseCommand):
    help = 'Genesis-Kleidung auf den HumanBody-Grundfiguren rendern und Hautpixel zaehlen'

    def add_arguments(self, parser):
        parser.add_argument('--nur', default=None)
        parser.add_argument('--geschlecht', nargs='*', default=None)
        parser.add_argument('--neu', action='store_true')
        parser.add_argument('--ziel', default=str(TOOLS_ROOT / 'ProjektTemp' / 'hbprobe'))

    def handle(self, *args, **opt):
        from core.dienste.hbkleidprobe import Hbkleidprobe

        probe = Hbkleidprobe(opt['ziel'], nur=opt['nur'], geschlechter=opt['geschlecht'], neu=opt['neu'])
        zeilen = probe.laufen(melden=lambda text: (self.stdout.write(text), self.stdout.flush()))
        fehler = [z for z in zeilen if z['fehler']]
        gut = sorted((z for z in zeilen if not z['fehler']), key=lambda z: -z['pixel'])
        self.stdout.write('\n%d Proben, %d Fehler, %d ohne Hautpixel' % (
            len(zeilen), len(fehler), sum(1 for z in gut if z['pixel'] == 0)))
        self.stdout.write('Schlechteste 30:')
        for z in gut[:30]:
            self.stdout.write('  %6d  %-7s %-14s %s' % (z['pixel'], z['geschlecht'], z['kategorie'], z['id']))
        for z in fehler:
            self.stdout.write('  FEHLER %-7s %s: %s' % (z['geschlecht'], z['id'], z['fehler']))
