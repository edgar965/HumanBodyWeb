# -*- coding: utf-8 -*-
"""`manage.py genesis9_dazpaket <zip …> [--machen] [--innen NAME] [--entfernen]` — Daz-Studio-Zips in die Daz-Bibliothek (`G9dazpaket`).

Ohne `--machen` nur der Plan: je Zip neue, schon vorhandene (gleiche Größe) und Konflikt-Dateien. Mit `--machen` werden die neuen
geschrieben — aus einem Zip mit Konflikt nichts. `--entfernen` löscht, was ein früherer Lauf aus diesem Zip geschrieben hat.
Danach baut die Garderobe ihre Liste über den Bestandsschlüssel selbst neu.
"""
import collections
import time
from pathlib import Path

from django.core.management.base import BaseCommand
from Genesis9.dazpaket import G9dazpaket


class Command(BaseCommand):
    help = 'Daz-Studio-Zips in die Daz-Bibliothek entpacken (ohne --machen nur der Plan)'

    def add_arguments(self, parser):
        parser.add_argument('zips', nargs='+')
        parser.add_argument('--machen', action='store_true', help='wirklich schreiben')
        parser.add_argument('--innen', action='append', default=[], help='nur dieses innere Zip (mehrfach möglich)')
        parser.add_argument('--entfernen', action='store_true', help='die Dateien eines früheren Laufs löschen')

    def handle(self, *args, **o):
        beginn = time.perf_counter()
        for z in o['zips']:
            pfad = Path(z)
            if o['entfernen']:
                weg, geaendert = G9dazpaket.entfernen(pfad.name)
                self.stdout.write('%-70s gelöscht %d, verändert (bleibt) %d' % (pfad.name[:70], len(weg), len(geaendert)))
                continue
            paket = G9dazpaket(pfad, innen=o['innen'])
            plan = paket.installieren() if o['machen'] else paket.plan()
            wurzeln = collections.Counter('/'.join(r.split('/')[:3]) for r, _g in plan['neu'])
            zustand = 'KONFLIKT' if plan['konflikt'] else ('geschrieben' if o['machen'] and plan['neu'] else 'Plan')
            self.stdout.write('%-70s neu %4d  gleich %4d  Konflikt %d  %s  %s' % (
                pfad.name[:70], len(plan['neu']), len(plan['gleich']), len(plan['konflikt']), zustand,
                ', '.join('%s (%d)' % w for w in wurzeln.most_common(3))))
            for rel, alt, neu in plan['konflikt'][:5]:
                self.stdout.write(self.style.WARNING('    Konflikt %s: Bibliothek %d B, Zip %d B' % (rel, alt, neu)))
        self.stdout.write(self.style.SUCCESS('fertig in %.1f s' % (time.perf_counter() - beginn)))
