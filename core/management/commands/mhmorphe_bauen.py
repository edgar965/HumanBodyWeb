# -*- coding: utf-8 -*-
"""`manage.py mhmorphe_bauen` — die MakeHuman-Regler als Genesis-9-Morphs ablegen.

Rechnet jeden MakeHuman-Regler des Plans (`Mhmorphplan`: 13 Makros, 258 Detailregler, 22 Koerperformen) in beiden Richtungen auf dem MakeHuman-Netz, legt die
Differenz ueber den Klon (`Mhkopfklon`, ein `G9mhklon` mit ausgerichtetem Kopf) auf den Genesis-9-Kaefig und schreibt sie nach `Genesis9/ablage/mhmorphe/`
(`Mhmorpheaufgenesis`, `G9mhmorphe`). Danach zeigt die Szene-Seite sie unter „MH-Morphs …“.

Noetig nach einer Aenderung der MakeHuman-Ziele (`mh_ziele_bauen`), des Klons oder der Genesis-Grundfigur.
"""

import time

from django.core.management.base import BaseCommand
from Genesis9.mhmorphe import G9mhmorphe

from core.dienste.mhmorpheaufgenesis import Mhmorpheaufgenesis


class Command(BaseCommand):
    help = 'MakeHuman-Regler als Genesis-9-Morphs (MH-Morphs) bauen'

    def add_arguments(self, parser):
        parser.add_argument('--leise', action='store_true', help='Kein Fortschritt, nur das Ergebnis')
        parser.add_argument('--nur', default='', help='Nur diese Kennungen (Komma getrennt, z. B. macro_Alter_Baby,macro_Alter_Kind): Teilbau, der übrige Bestand bleibt')

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        melden = None if optionen.get('leise') else self._fortschritt
        nur = [k.strip() for k in str(optionen.get('nur') or '').split(',') if k.strip()] or None
        ergebnis = Mhmorpheaufgenesis(melden=melden).bauen(nur=nur)
        self.stdout.write(self.style.SUCCESS(
            '%d MH-Morphs in %.1f s nach %s geschrieben' % (len(ergebnis), time.perf_counter() - beginn, G9mhmorphe.ordner())))

    def _fortschritt(self, nummer, gesamt, name, brief):
        if brief is None:
            self.stdout.write('  %3d/%d  %-52s uebergangen (kein Kaefigpunkt)' % (nummer, gesamt, name))
            return
        self.stdout.write('  %3d/%d  %-52s %6d Punkte  +%.1f / -%.1f mm' % (nummer, gesamt, name, brief['punkte'], brief['plus_mm'], brief['minus_mm']))
