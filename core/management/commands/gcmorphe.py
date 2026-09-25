# -*- coding: utf-8 -*-
"""`manage.py gcmorphe` — die Passform-Regler der GC-Stücke als Daz-Morphe (`Genesis9/gcmorphe.py`).

    manage.py gcmorphe --liste           je Stück die Regler, die gebacken würden
    manage.py gcmorphe                   alle Stücke ohne aktuelle Morphe
    manage.py gcmorphe --nur t_shirt     nur Stücke mit „t_shirt" im Namen
    manage.py gcmorphe --neu             auch Stücke mit aktuellen Morphen

Je Regler zwei Drapierungen (Minimum, Maximum, ~30 s je Fassung auf der GPU). Ein
zweiter Lauf backt nur, was fehlt (Ablage `gc_stuecke/<Kennung>/morphe/`).
"""
import time

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Passform-Regler der GarmentCode-Stuecke als Morphe backen'

    def add_arguments(self, parser):
        parser.add_argument('--liste', action='store_true', help='nur auflisten')
        parser.add_argument('--nur', default=None, help='Teilwort des Stuecknamens')
        parser.add_argument('--neu', action='store_true', help='auch Stuecke mit aktuellen Morphen')
        parser.add_argument('--teil', default='0/1', help='i/n: jedes n-te Stueck ab i (parallele Laeufe)')

    def handle(self, *args, **opt):
        import json

        from Genesis9.gcmorphe import G9gcmorphe
        from Genesis9.gcstuecke import G9gcstuecke

        if opt['liste']:
            wurzel = G9gcstuecke.arbeitsordner('x').parent
            summe = 0
            for pfad in sorted(wurzel.glob('*/bilanz.json')):
                b = json.loads(pfad.read_text(encoding='utf-8'))
                if opt['nur'] and opt['nur'] not in b['stueck']:
                    continue
                regler = G9gcmorphe.regler(b['vorlage'], b.get('werte') or {})
                summe += len(regler)
                self.stdout.write('%-40s %2d  %s' % (b['stueck'], len(regler),
                                                     ', '.join(r['pfad'] for r in regler)))
            self.stdout.write('\n%d Regler, bis %d Fassungen' % (summe, 2 * summe))
            return
        start = time.time()
        i, n = (int(x) for x in opt['teil'].split('/'))
        ergebnis = G9gcmorphe.alle(nur=opt['nur'], neu=opt['neu'], teil=(i, n),
                                   melden=lambda text: (self.stdout.write(text), self.stdout.flush()))
        fehler = {k: v for k, v in ergebnis.items() if 'fehler' in v}
        self.stdout.write('\n%d Stücke, %d Kanäle, %d Fehler in %.0f min' % (
            len(ergebnis), sum(len(v.get('kanaele') or []) for v in ergebnis.values()),
            len(fehler), (time.time() - start) / 60.0))
        for k, v in fehler.items():
            self.stdout.write('  %s: %s' % (k, v['fehler']))
