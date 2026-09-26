# -*- coding: utf-8 -*-
"""`manage.py gcstuecke_fortschritt` — der GC-Stapellauf mit einer Fortschrittsdatei.

Wird vom Knopf auf `/settings/kleider/` als Unterprozess gestartet
(`core/dienste/gcstueckelauf.py`) — Edgars Handaufruf auf der Konsole bleibt
weiter `manage.py gcstuecke` (`core/management/commands/gcstuecke.py`),
unveraendert. Hier kommt nur die Fortschrittsdatei dazu, damit die Statusseite
den Balken fuellen kann: `G9gcstuecke.alle()` liefert den Fortschritt schon
als Textzeile je Stueck („[n/N] ..."), daraus wird n/N gelesen.

    manage.py gcstuecke_fortschritt --fortschritt <pfad>
    manage.py gcstuecke_fortschritt --fortschritt <pfad> --nur rock
    manage.py gcstuecke_fortschritt --fortschritt <pfad> --neu   auch aktuelle Stuecke neu bauen
"""
import json
import logging
import os
import re
import time

from django.core.management.base import BaseCommand

logger = logging.getLogger('core')

#: „[3/171] ..." — Zaehler des Stapellaufs am Zeilenanfang.
ZEILENMUSTER = re.compile(r'^\[(\d+)/(\d+)\]')


class Command(BaseCommand):
    help = 'GC-Stapellauf mit Fortschrittsdatei fuer den Knopf in /settings/kleider/'

    def add_arguments(self, parser):
        parser.add_argument('--fortschritt', required=True, help='Pfad der Fortschritts-JSON')
        parser.add_argument('--nur', default=None, help='Teilwort der Kennung oder Vorlage')
        parser.add_argument('--neu', action='store_true', help='auch aktuelle Stuecke neu bauen')

    def handle(self, *args, **opt):
        from Genesis9.gcstuecke import G9gcstuecke

        pfad = opt['fortschritt']
        stand = {'geschafft': 0, 'gesamt': 0, 'zeile': 'Startet …', 'fertig': False, 'fehler': None}
        self._schreiben(pfad, stand)

        def melden(text):
            self.stdout.write(text)
            self.stdout.flush()
            treffer = ZEILENMUSTER.match(text)
            if treffer:
                stand['geschafft'], stand['gesamt'] = int(treffer.group(1)), int(treffer.group(2))
            stand['zeile'] = text
            self._schreiben(pfad, stand)

        start = time.time()
        try:
            ergebnis = G9gcstuecke.alle(nur=opt['nur'], neu=opt['neu'], melden=melden)
        except Exception as fehler:                       # noqa: BLE001 -- muss auf der Seite ankommen
            logger.exception('gcstuecke_fortschritt: Stapellauf abgebrochen')
            stand.update({'fertig': True, 'fehler': '%s: %s' % (type(fehler).__name__, fehler)})
            self._schreiben(pfad, stand)
            raise
        stand.update({'fertig': True, 'gebaut': len(ergebnis['gebaut']),
                      'uebersprungen': len(ergebnis['uebersprungen']),
                      'fehlerliste': ergebnis['fehler'],
                      'minuten': round((time.time() - start) / 60.0, 1)})
        self._schreiben(pfad, stand)
        self.stdout.write('\nGebaut %d, übersprungen %d, Fehler %d in %.0f min'
                          % (len(ergebnis['gebaut']), len(ergebnis['uebersprungen']),
                             len(ergebnis['fehler']), stand['minuten']))

    @staticmethod
    def _schreiben(pfad, stand):
        """Atomar (`os.replace`) — die Statusseite liest sonst eine halb geschriebene Datei."""
        neben = pfad + '.neu'
        with open(neben, 'w', encoding='utf-8') as datei:
            json.dump(stand, datei, ensure_ascii=False, indent=1)
        os.replace(neben, pfad)
