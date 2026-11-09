# -*- coding: utf-8 -*-
"""`manage.py umamorphe_bauen` — die UMA-Regler als Genesis-9-Morphs ablegen.

Liest die 62 DNA-Regler (Koerper, Gesicht) und die drei Kinder-Posen aus den Unity-Assets des UMA-Projekts (`Umaregler`), uebertraegt ihre Knochenoperationen auf die
Genesis-9-Knochen (`Umaabbildung`, `G9knochenfeld`) und schreibt sie nach `Genesis9/ablage/umamorphe/` (`Umamorpheaufgenesis`, `G9umamorphe`). Danach zeigt die Szene-Seite sie
unter „UMA-Morphs …“. Kein Unity-Start noetig — nur Text lesen.
"""

import time

from django.core.management.base import BaseCommand
from Genesis9.umamorphe import G9umamorphe

from core.dienste.umamorpheaufgenesis import Umamorpheaufgenesis
from .sxmorphe_bauen import Command as SxmorphebauenCommand


class Command(BaseCommand):
    help = 'UMA-Regler als Genesis-9-Morphs (UMA-Morphs) bauen'

    def add_arguments(self, parser):
        parser.add_argument('--leise', action='store_true', help='Kein Fortschritt, nur das Ergebnis')

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        melden = None if optionen.get('leise') else self._fortschritt
        ergebnis = Umamorpheaufgenesis(melden=melden).bauen()
        self.stdout.write(self.style.SUCCESS(
            '%d UMA-Morphs in %.1f s nach %s geschrieben' % (len(ergebnis), time.perf_counter() - beginn, G9umamorphe.ordner())))

    _fortschritt = SxmorphebauenCommand._fortschritt          # dieselbe Rechnung wie `Command._fortschritt` (bis 08.11.2026 eine Kopie hier)
