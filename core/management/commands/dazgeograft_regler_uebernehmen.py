# -*- coding: utf-8 -*-
"""`manage.py dazgeograft_regler_uebernehmen [--angepasst cute_girl_daz_scham] [--basis daz_anatomie_frau]` (10.10.2026).

Legt die Regler `sch_*` des an eine Blender-Scham angepassten Daz-Stücks (`dazgeograft_anpassen`; deren Deltas stammen aus der alten Scham, `Dazgeograftmorphuebertrag`) auch auf das
Basis-Stück „Daz Anatomie Frau" — Punkt für Punkt über die Nummern der Stufe-1-Punkte, bei einem angepassten Stück auf Stufe 2 über die Rohnummern der Unterteilung (`Dazgeograftmorphbasis`,
`Dazgeograftstufenzuordnung`). Danach bewegen die Regler auf dem Basis-Stück dieselben Teile der Anatomie wie
auf der alten Scham. Ein späteres `dazgeograft_einbauen --geschlecht frau` rechnet die Regler wieder aus der Form (überschreibt) — dann diesen Befehl noch einmal.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Überträgt die übernommenen Scham-Regler vom angepassten Daz-Stück auf das Basis-Stück „Daz Anatomie Frau".'

    def add_arguments(self, parser):
        parser.add_argument('--angepasst', default='cute_girl_daz_scham', help='Kennung des angepassten Stücks (Vorgabe cute_girl_daz_scham)')
        parser.add_argument('--basis', default='daz_anatomie_frau', help='Kennung des Basis-Stücks (Vorgabe daz_anatomie_frau)')

    def handle(self, *args, **options):
        from Genesis9.anatomien import G9anatomien

        from core.dienste.dazgeograftmorphbasis import Dazgeograftmorphbasis

        namen = [e[0] for e in G9anatomien.fuer('vagina').eintraege()]
        try:
            bau = Dazgeograftmorphbasis(options['angepasst'], options['basis'])
        except (ValueError, OSError, KeyError) as fehler:
            raise CommandError(str(fehler)) from fehler
        uebernommen, gescheitert = bau.alle(namen)
        weg = ('Punkt i ↔ Punkt i; davon mit gleich vielen Dreiecken in beiden Stücken: %.1f %%' % (bau.gleich * 100) if bau.gleich is not None
               else 'über die Stufen (Rohnummer der Unterteilung), angepasstes Stück %d Punkte' % len(bau.p_a))
        self.stdout.write('%s → %s: %d Regler übertragen (%d Punkte des Basis-Stücks mit Gegenstück, %s; Lage nach Abzug der Mittellage Median %s / p99 %s mm), gescheitert: %s' % (
            options['angepasst'], options['basis'], len(uebernommen), bau.stufe, weg, bau.lage_mm[0], bau.lage_mm[1], gescheitert or 'keiner'))
        self.stdout.write('%-26s %-8s %-10s %s' % ('Regler', 'bewegt', 'max mm', 'Winkel Delta ↔ Normale (Basis / angepasst, Grad)'))
        for name, b in bau.pruefen(uebernommen).items():
            if 'fehler' in b:
                self.stdout.write('%-26s FEHLER %s' % (name, b['fehler']))
                continue
            self.stdout.write('%-26s %-8d %-10.2f %s' % (name, b['bewegt'], b['weg_max_mm'], '%s / %s' % (b['normal_grad_basis'], b['normal_grad_angepasst']) if 'normal_grad_basis' in b else ''))
