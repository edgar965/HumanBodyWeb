# -*- coding: utf-8 -*-
"""`manage.py g1morphe_bauen` — die Kinder von Genesis 1 (Basic Child, Kids 4) als Genesis-9-Morphs ablegen.

Legt `FBMBasicChild` und `CloneKids4` über Daz' Klon von Genesis 1 (`CloneGenesis`) als Ähnlichkeit plus Form auf den Genesis-9-Käfig und schreibt sie nach
`Genesis9/ablage/g1morphe/` (`G1morpheaufgenesis`, `G9g1morphe`). Danach zeigt die Szene-Seite sie im Bereich „Alter“.

Voraussetzung: Genesis 1 Starter Essentials in der Daz-Bibliothek (`data/DAZ 3D/Genesis/Base/Genesis.dsf` und die beiden Morphs).
"""

import time

from django.core.management.base import BaseCommand
from Genesis9.g1morphe import G9g1morphe

from core.dienste.g1morpheaufgenesis import G1morpheaufgenesis


class Command(BaseCommand):
    help = 'Genesis-1-Kinder (Basic Child, Kids 4) als Genesis-9-Morphs bauen'

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        ergebnis = G1morpheaufgenesis(melden=self._fortschritt).bauen()
        self.stdout.write(self.style.SUCCESS('%d G1-Morphs in %.1f s nach %s geschrieben' % (len(ergebnis), time.perf_counter() - beginn, G9g1morphe.ordner())))

    def _fortschritt(self, nummer, gesamt, name, brief):
        self.stdout.write('  %d/%d  %-12s %6d Punkte  +%.1f mm  s %.3f  Höhe %.3f m' % (nummer, gesamt, name, brief['punkte'], brief['plus_mm'], brief['aehnlichkeit'], brief['hoehe_m']))
