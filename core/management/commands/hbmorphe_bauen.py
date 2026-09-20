# -*- coding: utf-8 -*-
"""`manage.py hbmorphe_bauen` — die HumanBody-Regler als Genesis-9-Morphs ablegen.

Uebertraegt alle HumanBody-Regler (MB-Lab, 204) ueber die Paarung der
Grundfiguren auf den Genesis-9-Kaefig und schreibt sie nach
`Genesis9/ablage/hbmorphe/` (`Hbmorpheaufgenesis`, `G9hbmorphe`). Danach
zeigt die Szene-Seite sie unter „HB-Morphs Koerper/Gesicht/Fantasie".

Noetig nach einer Aenderung der HumanBody-Morphpakete oder der Paarung
(`G9aufhumanbody`); `--nur-veraltet` baut nur, wenn der Bestand aelter ist
als die Pakete.
"""

import time

from django.core.management.base import BaseCommand
from Genesis9.hbmorphe import G9hbmorphe

from core.dienste.hbmorpheaufgenesis import Hbmorpheaufgenesis


class Command(BaseCommand):
    help = 'HumanBody-Regler als Genesis-9-Morphs (HB-Morphs) bauen'

    def add_arguments(self, parser):
        parser.add_argument('--leise', action='store_true', help='Kein Fortschritt, nur das Ergebnis')
        parser.add_argument('--nur-veraltet', action='store_true',
                            help='Nur bauen, wenn die Ablage fehlt oder aelter ist als die HumanBody-Morphs')

    def handle(self, *args, **optionen):
        if optionen.get('nur_veraltet') and not Hbmorpheaufgenesis.veraltet():
            self.stdout.write('HB-Morphs sind auf dem Stand (%s)' % G9hbmorphe.ordner())
            return
        beginn = time.perf_counter()
        melden = None if optionen.get('leise') else self._fortschritt
        ergebnis = Hbmorpheaufgenesis(melden=melden).bauen()
        self.stdout.write(self.style.SUCCESS(
            '%d HB-Morphs in %.1f s nach %s geschrieben'
            % (len(ergebnis), time.perf_counter() - beginn, G9hbmorphe.ordner())))

    def _fortschritt(self, nummer, gesamt, name, brief):
        if brief is None:
            self.stdout.write('  %3d/%d  %-40s uebergangen (kein Kaefigpunkt)' % (nummer, gesamt, name))
            return
        self.stdout.write('  %3d/%d  %-40s %6d Punkte  +%.1f / -%.1f mm'
                          % (nummer, gesamt, name, brief['punkte'],
                             brief['plus_mm'], brief['minus_mm']))
