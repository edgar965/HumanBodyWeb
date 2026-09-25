# -*- coding: utf-8 -*-
"""`manage.py gcstuecke` — jede GarmentCode-Vorlage einmal als Genesis-9-Stück.

    manage.py gcstuecke --liste          nur zeigen, was gebaut würde
    manage.py gcstuecke                  alles, was fehlt oder veraltet ist
    manage.py gcstuecke --nur rock       nur Aufträge mit „rock" in Kennung/Vorlage
    manage.py gcstuecke --neu            auch aktuelle Stücke neu bauen

Je Stück eine Drapierung auf der GPU (~20–45 s) — der ganze Stapel dauert
Stunden und gehört nicht neben Edgars Arbeit (`Genesis9/gcstuecke.py`).
Danach den Server neu starten: die Garderoben-Liste steht in seinem Speicher.
"""
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'GarmentCode-Formen und -Vorbilder als Genesis-9-Stuecke bauen'

    def add_arguments(self, parser):
        parser.add_argument('--liste', action='store_true', help='nur auflisten')
        parser.add_argument('--nur', default=None, help='Teilwort der Kennung oder Vorlage')
        parser.add_argument('--neu', action='store_true', help='auch aktuelle Stuecke bauen')

    def handle(self, *args, **opt):
        from Genesis9.gcstuecke import G9gcstuecke

        if opt['liste']:
            for a in G9gcstuecke.auftraege():
                nur = opt['nur']
                if nur and nur.lower() not in a['kennung'].lower() and nur != a['vorlage']:
                    continue
                self.stdout.write('%-13s %-40s %s%s' % (a['vorlage'], a['kennung'], a['quelle'],
                                                        '  (aktuell)' if G9gcstuecke.aktuell(a) else ''))
            return
        start = time.time()
        ergebnis = G9gcstuecke.alle(nur=opt['nur'], neu=opt['neu'],
                                    melden=lambda text: (self.stdout.write(text), self.stdout.flush()))
        self.stdout.write('\nGebaut %d, übersprungen %d, Fehler %d in %.0f min'
                          % (len(ergebnis['gebaut']), len(ergebnis['uebersprungen']),
                             len(ergebnis['fehler']), (time.time() - start) / 60.0))
        for kennung, text in ergebnis['fehler']:
            self.stdout.write('  %s: %s' % (kennung, text))
