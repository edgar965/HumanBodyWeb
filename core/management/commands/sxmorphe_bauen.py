# -*- coding: utf-8 -*-
"""`manage.py sxmorphe_bauen` — die SMPL-X-Regler als Genesis-9-Morphs ablegen.

Legt die 23 Massregler (cm) und die ersten zehn Formkomponenten von SMPL-X ueber die Netzpaarung (`G9netzpaarung`) auf den Genesis-9-Kaefig und schreibt sie nach
`Genesis9/ablage/sxmorphe/` (`Sxmorpheaufgenesis`, `G9sxmorphe`). Danach zeigt die Szene-Seite sie unter „SMPL-X-Morphs …“.

Voraussetzung: die SMPL-X-Modelle (`3DObjects/Archiv/SMPL-X`) und `massregler_f1_female.npz` (`Smplxmassregler.berechnen`).
"""

import time

from django.core.management.base import BaseCommand
from Genesis9.sxmorphe import G9sxmorphe

from core.dienste.sxmorpheaufgenesis import Sxmorpheaufgenesis


class Command(BaseCommand):
    help = 'SMPL-X-Regler als Genesis-9-Morphs (SX-Morphs) bauen'

    def add_arguments(self, parser):
        parser.add_argument('--leise', action='store_true', help='Kein Fortschritt, nur das Ergebnis')

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        melden = None if optionen.get('leise') else self._fortschritt
        ergebnis = Sxmorpheaufgenesis(melden=melden).bauen()
        self.stdout.write(self.style.SUCCESS(
            '%d SX-Morphs in %.1f s nach %s geschrieben' % (len(ergebnis), time.perf_counter() - beginn, G9sxmorphe.ordner())))

    def _fortschritt(self, nummer, gesamt, name, brief):
        if brief is None:
            self.stdout.write('  %3d/%d  %-34s uebergangen (kein Kaefigpunkt)' % (nummer, gesamt, name))
            return
        self.stdout.write('  %3d/%d  %-34s %6d Punkte  +%.1f / -%.1f mm' % (nummer, gesamt, name, brief['punkte'], brief['plus_mm'], brief['minus_mm']))
