# -*- coding: utf-8 -*-
"""`manage.py mesh3d_pruefreihe [--kennung K] [--rechnen] [--aufnehmen]` — die Prüfreihe der Testaufträge von Mesh-3D (13.10.2026, `Mesh3dpruefreihe`).

Ohne Schalter werden die gespeicherten Ergebnisse jedes Testauftrags (Reiter „Testaufträge") gegen das Soll in `core/daten/mesh3dpruefreihe.json` geprüft — Sekunden, keine Grafikkarte, nichts wird geändert.
`--rechnen` rechnet jeden Auftrag erst als Kopie neu (Grafikkarte, nacheinander, nur auf Ansage) und prüft die Kopie; `--aufnehmen` schreibt das Soll aus dem jetzigen Stand (nur nach Ansicht und Billigung des Stands).
Ausgang 1, wenn ein Wert außerhalb der Toleranz liegt oder nicht gemessen wurde.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Prüft die Testaufträge von Mesh-3D gegen ihr Soll (mit --rechnen: rechnet sie als Kopie neu; mit --aufnehmen: schreibt das Soll).'

    def add_arguments(self, parser):
        parser.add_argument('--kennung', default=None, help='Nur diesen Testauftrag (Kennung des Imports)')
        parser.add_argument('--rechnen', action='store_true', help='Jeden Auftrag als Kopie neu rechnen (Grafikkarte, je Auftrag 6–20 Minuten)')
        parser.add_argument('--aufnehmen', action='store_true', help='Das Soll aus dem jetzigen Stand schreiben')
        parser.add_argument('--hinweis', default='', help='Mit --aufnehmen: ein Satz, warum dieser Stand das Soll ist')
        parser.add_argument('--auch', action='append', default=[], help='Mit --aufnehmen --kennung: Kennung eines weiteren Laufs desselben Auftrags (Kopie); bei max/min-Regeln gilt der schlechteste Wert (wiederholbar)')

    def handle(self, *args, **options):
        from core.dienste.mesh3dpruefreihe import Mesh3dpruefreihe as P

        alle = P.testauftraege()
        kennungen = [k for k in alle if not options['kennung'] or k == options['kennung']]
        if options['kennung'] and not kennungen:
            raise CommandError('Kein Testauftrag mit der Kennung %s (Reiter „Testaufträge“) — geprüft wurde nichts.' % options['kennung'])
        if options['auch'] and (not options['aufnehmen'] or len(kennungen) != 1):
            raise CommandError('--auch gilt nur mit --aufnehmen und genau einem Auftrag (--kennung)')
        if options['aufnehmen']:
            for k, n in P.aufnehmen(kennungen, options['hinweis'], options['auch']).items():
                self.stdout.write('%s: %d Sollwerte aufgenommen' % (k, n))
            return
        soll = P.laden()
        ganz_ok = True
        for k in kennungen:
            gemessen = P.neu_rechnen(k, self.stdout.write) if options['rechnen'] else None
            zeilen, ok = P.pruefen(k, gemessen)
            ganz_ok &= ok
            art = 'Soll + allgemeine Regeln' if k in soll else 'nur allgemeine Regeln, kein Soll (manage.py mesh3d_pruefreihe --kennung %s --aufnehmen, nachdem Sie den Stand gesehen haben)' % k
            self.stdout.write('\n%s  %s%s — %s [%s]' % (k, P.name(k), ' (Kopie %s)' % gemessen if gemessen else '', 'bestanden' if ok else 'NICHT bestanden', art))
            for name, ist, s, gut, text in zeilen:
                if gut is not True or options['verbosity'] > 1:
                    self.stdout.write('  %-4s %-24s ist %-28s soll %-28s %s' % ('offen' if gut is None else ('ok' if gut else 'FEHL'), name, str(ist)[:28], str(s)[:28], text))
        verwaist = [] if options['kennung'] else P.verwaist(alle)
        for k, name in verwaist:
            self.stdout.write('\nWARNUNG %s  %s: Soll ohne Testauftrag — der Auftrag ist gelöscht oder liegt nicht im Reiter „Testaufträge“; dieses Soll wurde NICHT geprüft (neu aufnehmen: --kennung <Auftrag> --aufnehmen)' % (k, name))
        self.stdout.write('\nPrüfreihe Mesh-3D: %s%s' % ('alles bestanden' if ganz_ok else 'NICHT alles bestanden', ' (%d Soll ohne Auftrag nicht geprüft)' % len(verwaist) if verwaist else ''))
        if not ganz_ok:
            raise SystemExit(1)
