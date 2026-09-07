# -*- coding: utf-8 -*-
u"""`manage.py mh_ziele_bauen` — die MakeHuman-Ziele kompilieren.

Liest die 1.280 `.target`-Dateien des Upstreams und legt sie als
`MakeHuman/ziele/mh_ziele.npz` ab. Warum das noetig ist und was drin steht:
`MakeHuman/zielablage.py`.

Der Lauf dauert gemessene 13,7 s und ist nur
nach einem Wechsel des Upstreams noetig. Er schreibt NICHT nach
`HumanBody/data/` — die Ablage liegt beim Upstream, der sie erzeugt hat.
"""

import time

from django.core.management.base import BaseCommand, CommandError

from MakeHuman.zielablage import Mhzielablage
from MakeHuman.zielbaum import Mhzielbaum


class Command(BaseCommand):
    help = u'MakeHuman-Modellierziele in eine npz-Ablage kompilieren'

    def add_arguments(self, parser):
        parser.add_argument(
            '--leise', action='store_true',
            help=u'Kein Fortschritt, nur das Ergebnis')

    def handle(self, *args, **optionen):
        if not Mhzielbaum.vorhanden():
            raise CommandError(
                u'Kein Zielordner unter %s — liegt der MakeHuman-Upstream da? '
                u'Siehe MakeHuman/HERKUNFT.md.' % Mhzielbaum.wurzel())
        beginn = time.perf_counter()
        melden = None if optionen.get('leise') else self._fortschritt
        anzahl = Mhzielablage.bauen(melden=melden)
        self.stdout.write(self.style.SUCCESS(
            u'%d Ziele in %.1f s nach %s geschrieben'
            % (anzahl, time.perf_counter() - beginn, Mhzielablage.pfad())))

    def _fortschritt(self, nummer, gesamt):
        self.stdout.write(u'  %d/%d gelesen' % (nummer, gesamt))
