# -*- coding: utf-8 -*-
"""manage.py sam_kalibrieren — die Tabelle der SAM-Gelenkpunkte auf Genesis bauen (einmal je Rechner, GPU, rund 2,5 Minuten); Einzelheiten: `core/dienste/samkalibrierung.py`."""

import json

from django.core.management.base import BaseCommand

from core.dienste.samkalibrierung import Samkalibrierung


class Command(BaseCommand):
    help = 'Genesis durch SAM 3D Body schicken und den Gelenkversatz in Genesis9/ablage/ ablegen.'

    def handle(self, *args, **optionen):
        # Die Konsole kann cp1252 sein: Fortschrittstexte tragen „°" und „…".
        _, bericht = Samkalibrierung(lambda anteil, text: self.stdout.write('  [%3.0f %%] %s' % (100 * anteil, str(text).encode('ascii', 'replace').decode()))).ausfuehren()
        self.stdout.write(json.dumps(bericht, ensure_ascii=False, indent=1))
