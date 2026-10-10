# -*- coding: utf-8 -*-
"""`manage.py dazgeograft_einbauen [--geschlecht mann|frau]` — das Daz-Geograft „Anatomical Elements" als eigenes Stück der Garderobe (10.10.2026).

Wandelt `data/Daz 3D/Genesis 9/Anatomical Elements Male|Female` (Genesis 9 Starter Essentials Expansion; die Bibliothek wird nur gelesen) in ein Stück
„Daz Anatomie Mann|Frau" in der eigenen Bibliothek (`Dazgeograft`). Lässt sich beliebig oft wiederholen: das Stück wird neu geschrieben, seine Regler beim
nächsten Aufruf neu gebaut.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Baut das Daz-Geograft (Anatomical Elements) als Stück der eigenen Garderobe.'

    def add_arguments(self, parser):
        parser.add_argument('--geschlecht', default='mann', choices=['mann', 'frau'])
        parser.add_argument('--realism', type=float, default=1.0, help='Wert des Morphs „Realism HD" (Vorgabe des Produkts: 1)')
        parser.add_argument('--nur-varianten', action='store_true', help='Nur die Charakter-Varianten neu schreiben (das Stück bleibt, Sekunden statt Minuten)')

    def handle(self, *args, **options):
        from core.dienste.dazgeograft import Dazgeograft

        if options['nur_varianten']:
            self._varianten(options['geschlecht'], Dazgeograft)
            return
        try:
            bilanz = Dazgeograft(options['geschlecht']).bauen(options['realism'])
        except ValueError as fehler:
            raise CommandError(str(fehler)) from fehler
        self.stdout.write('Stück %s: %d Punkte, %d Flächen — %s' % (bilanz['stueck'], bilanz['punkte'], bilanz['flaechen'], bilanz['duf']))
        self.stdout.write('Bericht: %s' % bilanz['bericht'])

    def _varianten(self, geschlecht, dazgeograft):
        """Die Varianten des vorhandenen Stücks neu schreiben (`Dazgeograftvarianten.schreiben`)."""
        from core.dienste.dazgeograftvarianten import Dazgeograftvarianten
        from Genesis9.pfade import G9pfade

        stueck = G9pfade.eigene() / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / ('%s.duf' % dazgeograft.NAMEN[geschlecht][0])
        if not stueck.is_file():
            raise CommandError('Das Stück %s fehlt — erst ohne --nur-varianten bauen' % stueck.name)
        namen = Dazgeograftvarianten.schreiben(stueck, geschlecht, dazgeograft.GRUPPEN[geschlecht])
        self.stdout.write('Varianten (%d): %s' % (len(namen), ', '.join(namen)))
