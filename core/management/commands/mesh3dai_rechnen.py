# -*- coding: utf-8 -*-
"""`manage.py mesh3dai_rechnen [kennung]` — der Arbeitsprozess der Rechenläufe von Mesh3D-AI (23.10.2026, `Mesh3dairechenschlange`, `Mesh3dairechenlauf`).

Ohne Kennung: die Warteschlange abarbeiten (so startet ihn der Knopf „Rechnen“). Mit Kennung: erst einreihen, dann abarbeiten — für einen Lauf ohne Oberfläche.
"""
from django.core.management.base import BaseCommand

from core.dienste.mesh3dairechenlauf import Mesh3dairechenlauf
from core.dienste.mesh3dairechenschlange import Mesh3dairechenschlange


class Command(BaseCommand):
    help = 'Mesh3D-AI: Rechenläufe der Warteschlange abarbeiten (optional eine Kennung einreihen)'

    def add_arguments(self, parser):
        parser.add_argument('kennung', nargs='?', default=None)
        parser.add_argument('--ab', default=None, help='erst ab diesem Schritt rechnen (Schlüssel, z. B. zerlegung); die Schritte davor bleiben, wie sie sind')

    def handle(self, *args, **optionen):
        k = optionen.get('kennung')
        if k:
            Mesh3dairechenlauf(k).vorbereiten('wartet', ab=optionen.get('ab'))
            schlange = Mesh3dairechenschlange.schlange()
            if k not in schlange:
                from core.atomic_write import AtomarSchreiber
                AtomarSchreiber.json_schreiben(Mesh3dairechenschlange.ordner() / 'schlange.json', schlange + [k])
        zahl = Mesh3dairechenschlange.abarbeiten()
        self.stdout.write('Mesh3D-AI Rechenläufe: %d abgearbeitet' % zahl)
