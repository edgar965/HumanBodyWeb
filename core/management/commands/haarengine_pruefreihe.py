# -*- coding: utf-8 -*-
"""`manage.py haarengine_pruefreihe [--kennung K] [--starten]` — die Prüfreihe „2D3D Kleider" (01.10.2026, Punkt 6).

Ohne `--starten` werden nur die gespeicherten Ergebnisse gegen die Sollbereiche geprüft (`Haarenginepruefreihe`,
`core/daten/haarenginepruefreihe.json`) — Sekunden, keine Grafikkarte. Mit `--starten` rechnet jeder Auftrag erst neu:
über die Server-API (`Haarengineserverstart`) ab seinem Schritt `ab` bis zu den Iterationen, dann `runden` Runden
automatisch — je Auftrag rund eine halbe Stunde Grafikkarte, nur auf Ansage.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Prüft die Aufträge der Prüfreihe „2D3D Kleider" gegen ihre Sollbereiche (mit --starten: rechnet sie neu).'

    def add_arguments(self, parser):
        parser.add_argument('--kennung', default=None, help='Nur diesen Auftrag der Reihe')
        parser.add_argument('--starten', action='store_true', help='Erst neu rechnen (Server-API, Grafikkarte)')

    def handle(self, *args, **options):
        from core.dienste.haarenginepruefreihe import Haarenginepruefreihe
        from core.dienste.haarengineserverstart import Haarengineserverstart
        from core.models import Haarengineauftrag

        nur = options['kennung']
        reihe = [a for a in Haarenginepruefreihe.laden() if not nur or a['kennung'] == nur]
        start = Haarengineserverstart(melden=self.stdout.write)
        gesamt_ok = True
        for auftrag in reihe:
            job = Haarengineauftrag.objects.filter(kennung=auftrag['kennung']).first()
            if job is None:
                self.stdout.write('%s fehlt in der Datenbank' % auftrag['kennung'])
                gesamt_ok = False
                continue
            if options['starten']:
                start.starten(job, auftrag.get('ab') or 'netz', 'iterationen')
                if start.warten(job) == 'wartet':
                    start.automatisch(job, auftrag.get('runden') or 20)
                    start.warten(job)
            self.stdout.write('\n%s  %s' % (job.kennung, job.name))
            for name, ist, soll, ok in Haarenginepruefreihe.bewerten(job, auftrag.get('soll') or {}):
                gesamt_ok &= ok
                zeile = '  %-4s %-30s ist %-40s soll %s' % ('ok' if ok else 'FEHL', name, str(ist)[:40], soll)
                self.stdout.write(zeile)
        self.stdout.write('\nPrüfreihe: %s' % ('alles im Soll' if gesamt_ok else 'NICHT im Soll'))
