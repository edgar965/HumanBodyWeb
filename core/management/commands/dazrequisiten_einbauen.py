# -*- coding: utf-8 -*-
"""`manage.py dazrequisiten_einbauen` — Daz-Props außerhalb von `People/` (Scifi Melee Weapons) als Requisiten in die Garderobe (10.10.2026).

Kopiert die `.duf` aus `Props/SciFiMelee` der Daz-Bibliothek (nur gelesen) nach `People/Genesis/Props/SciFiMelee` der eigenen Wurzel (`Dazrequisiten`).
Wiederholbar. Danach die Garderobenliste neu lesen (der Server tut es selbst, sobald die Quelle neuer ist als die Ablage).
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Kopiert Daz-Props (Scifi Melee Weapons) als Requisiten in die eigene Garderobe.'

    def handle(self, *args, **options):
        from core.dienste.dazrequisiten import Dazrequisiten

        try:
            ergebnis = Dazrequisiten.einbauen()
        except FileNotFoundError as fehler:
            raise CommandError(str(fehler)) from fehler
        for satz, namen in ergebnis.items():
            self.stdout.write('%s: %d Requisiten — %s' % (satz, len(namen), ', '.join(namen)))
