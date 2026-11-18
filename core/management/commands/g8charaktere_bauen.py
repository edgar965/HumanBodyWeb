# -*- coding: utf-8 -*-
"""`manage.py g8charaktere_bauen [--nur "KT Margie G8" …]` — Genesis-8-Charaktere als Genesis-9-Morphs ablegen (`G8charakteraufgenesis`, `G9g8morphe`).

Je Charakterpreset von Genesis 8 Female/Male ein Regler `g8:<Kennung>` (Klon-Gestalt plus übertragene Charakterform) nach `Genesis9/ablage/g8morphe/`;
danach steht er im Bereich „Genesis-8-Charaktere“ und als „<Name>  (Genesis 8)“ im Katalog. Rechnet auf der Grafikkarte, unter der Gpusperre.
"""
import sys
import time

from django.core.management.base import BaseCommand
from Genesis9.g8morphe import G9g8morphe

from core.dienste.g8charakteraufgenesis import G8charakteraufgenesis


class Command(BaseCommand):
    help = 'Genesis-8-Charaktere als Genesis-9-Morphs bauen'
    GPUSPERRE = r'A:\3DTools\meshgenesis'

    def add_arguments(self, parser):
        parser.add_argument('--nur', action='append', default=[], help='Dateiname des Presets ohne .duf (mehrfach möglich)')

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        sys.path.insert(0, self.GPUSPERRE)
        from meshgenesis_gpusperre import Gpusperre
        Gpusperre.niedrig()
        with Gpusperre('g8charaktere_bauen', bedarf=4):
            ergebnis = G8charakteraufgenesis(melden=self._fortschritt).bauen(optionen['nur'] or None)
        self.stdout.write(self.style.SUCCESS('%d G8-Charaktere in %.1f s nach %s' % (len(ergebnis), time.perf_counter() - beginn, G9g8morphe.ordner())))

    def _fortschritt(self, nummer, gesamt, name, brief):
        self.stdout.write('  %d/%d  %-22s %6s Punkte  +%s mm  Höhe %s m' % (nummer, gesamt, name, brief.get('punkte'), brief.get('plus_mm'), brief.get('hoehe_m')))
