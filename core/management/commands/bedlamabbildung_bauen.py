# -*- coding: utf-8 -*-
"""`manage.py bedlamabbildung_bauen` — die Abbildung Genesis-9-Texel → SMPL-X-UV für die BEDLAM-Häute rechnen (`G9bedlamabbildung`).

Einmal für alle 100 Häute (ein paar Minuten, danach liegt `Genesis9/ablage/bedlamuv_2048_v1.npz`). Ohne sie erscheinen die BEDLAM-Häute nicht in der Hautauswahl.
Nötig nach einer Änderung der Paarung (`G9netzpaarung`), der SMPL-X-UV oder der Kachelabtastung.
"""
import time

from django.core.management.base import BaseCommand

from core.dienste.g9bedlamabbildung import G9bedlamabbildung


class Command(BaseCommand):
    help = 'Abbildung Genesis-9-Texel → SMPL-X-UV für die BEDLAM-Häute bauen'

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        zahlen = G9bedlamabbildung.bauen()
        self.stdout.write(self.style.SUCCESS('BEDLAM-Abbildung: %s Texel in %.0f s nach %s' % (zahlen, time.perf_counter() - beginn, G9bedlamabbildung.pfad())))
