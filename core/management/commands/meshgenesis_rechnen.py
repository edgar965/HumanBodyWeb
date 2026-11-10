# -*- coding: utf-8 -*-
"""`manage.py meshgenesis_rechnen [kennung]` — der Arbeitsprozess der Rechenläufe von Mesh-Genesis (23.10.2026, `Meshgenesisrechenschlange`, `Meshgenesisrechenlauf`).

Ohne Kennung: die Warteschlange abarbeiten (so startet ihn der Knopf „Rechnen“). Mit Kennung: erst einreihen, dann abarbeiten — für einen Lauf ohne Oberfläche.
"""
from django.core.management.base import BaseCommand

from core.dienste.meshgenesisrechenlauf import Meshgenesisrechenlauf
from core.dienste.meshgenesisrechenschlange import Meshgenesisrechenschlange


class Command(BaseCommand):
    help = 'Mesh-Genesis: Rechenläufe der Warteschlange abarbeiten (optional eine Kennung einreihen)'

    def add_arguments(self, parser):
        parser.add_argument('kennung', nargs='?', default=None)
        parser.add_argument('--ab', default=None, help='erst ab diesem Schritt rechnen (Schlüssel, z. B. meshanpassung nach dem Umstellen des Geschlechts); die Schritte davor bleiben, wie sie sind')

    def handle(self, *args, **optionen):
        k = optionen.get('kennung')
        if k:
            Meshgenesisrechenlauf(k).vorbereiten('wartet', ab=optionen.get('ab'))
            schlange = Meshgenesisrechenschlange.schlange()
            if k not in schlange:
                from core.atomic_write import AtomarSchreiber
                AtomarSchreiber.json_schreiben(Meshgenesisrechenschlange.ordner() / 'schlange.json', schlange + [k])
        zahl = Meshgenesisrechenschlange.abarbeiten()
        self.stdout.write('Mesh-Genesis Rechenläufe: %d abgearbeitet' % zahl)
