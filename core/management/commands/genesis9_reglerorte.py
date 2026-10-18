# -*- coding: utf-8 -*-
"""`manage.py genesis9_reglerorte` — jeden Regler des Genesis-9-Bedienfelds messen und die Zuordnungstabelle schreiben (`G9reglerorte`).

Danach stehen die Regler im Bedienfeld dort, wo sie wirken (`G9reglergliederung`): HB-, MH-, SMPL-X- und UMA-Regler beim Körperteil statt in ihrem
Herkunftsbereich, die verborgenen Daz-Kanäle bei ihrem Körperteil, Doppelte als ein Regler. Nötig nach neuen Morphs (Familien neu gebaut, Daz-Paket
installiert) — fehlt ein Regler in der Tabelle, steht er in seinem Herkunftsbereich, und das Log sagt es einmal.

Rechenlastig (Inventur 18.10.2026: 2.406 Regler in 265 s) — mit niedriger Priorität starten.
"""

import time

from django.core.management.base import BaseCommand

from core.dienste.reglerortebau import Reglerortebau


class Command(BaseCommand):
    help = 'Genesis-9-Regler messen: Wirkungsort, bedingte Wirkung, Doppelte (Zuordnungstabelle des Bedienfelds)'

    def add_arguments(self, parser):
        parser.add_argument('--leise', action='store_true', help='Kein Fortschritt, nur das Ergebnis')

    def handle(self, *args, **optionen):
        beginn = time.perf_counter()
        melden = None if optionen.get('leise') else (lambda text: self.stdout.write('  ' + text))
        regler = Reglerortebau(melden=melden).bauen()
        self.stdout.write(self.style.SUCCESS('%d Regler gemessen in %.0f s' % (len(regler), time.perf_counter() - beginn)))
