# -*- coding: utf-8 -*-
"""`manage.py dazgeograft_anpassen --modell "cute girl" --scham "cute girl Scham" [--name …] [--aufloesung 1024] [--steifigkeit 3] [--nachformung 1] [--ziel-modell …]` (10.10.2026).

Baut das Stück „<Modell> Daz Scham" (`Dazgeograftangepasst`): das Geograft „Anatomical Elements" (Frau) auf der Figur des gespeicherten Modells, angepasst an die vorgegebene Scham des
Blender-Imports, mit Farbe, Rauheit und Normalen daraus. Wiederholbar; die Bake-Bilder liegen unter `3DObjects/models/Genesis9/eigene_stuecke/<Kennung>/gebacken`.
Danach läuft IMMER die Scham-Messung (`Schammessung`): ihre Zeilen stehen am Ende der Ausgabe, `messung.json` im Arbeitsordner des Stücks.
"""

import logging

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Passt das Daz-Geograft an die Scham eines Blender-Imports an, backt dessen Textur darauf und misst das Ergebnis.'

    def add_arguments(self, parser):
        parser.add_argument('--modell', required=True, help='Name des gespeicherten Modells, z. B. „cute girl"')
        parser.add_argument('--scham', required=True, help='Anzeigename des Scham-Stücks des Imports, z. B. „cute girl Scham"')
        parser.add_argument('--name', default=None, help='Name des neuen Stücks (Vorgabe: „<Modell> Daz Scham")')
        parser.add_argument('--aufloesung', type=int, default=1024, help='Kantenlänge der gebackenen Bilder in Pixeln (Vorgabe 1024)')
        parser.add_argument('--steifigkeit', type=float, default=None, help='Steifigkeit der Anpassung (Vorgabe siehe `Dazgeograftanpassung.STEIFIGKEIT`)')
        parser.add_argument('--nachformung', type=float, default=None, help='Nachformung der Figur am Becken (`eigen:…_scham`), 0 = aus (Vorgabe siehe `Dazgeograftangepasst.NACHFORMUNG`)')
        parser.add_argument('--ziel-modell', default=None, help='Modell, das das Stück trägt und die Nachformung mitbekommt (Vorgabe: „<Modell> Daz", wenn es existiert)')

    def handle(self, *args, **options):
        from core.dienste.dazgeograftangepasst import Dazgeograftangepasst
        from core.dienste.dazgeograftmorphuebertrag import Dazgeograftmorphuebertrag
        from core.dienste.schammessung import Schammessung

        try:
            bau = Dazgeograftangepasst(options['modell'], options['scham'], options['name'], options['aufloesung'], options['steifigkeit'], options['nachformung'])
            bilanz = bau.bauen()
        except (ValueError, FileNotFoundError, OSError) as fehler:
            raise CommandError(str(fehler)) from fehler
        ziel = options['ziel_modell'] or '%s Daz' % options['modell']
        geaendert = bau.modell_abgleichen(ziel)
        self.stdout.write('Stück %s: %d Punkte, %d Flächen — %s' % (bilanz['stueck'], bilanz['punkte'], bilanz['flaechen'], bilanz['duf']))
        self.stdout.write('Nachformung der Figur: %s; Modell „%s": %s' % (bau.nachformung or 'keine', ziel, geaendert or 'unverändert'))
        self.stdout.write('Bericht: %s' % {k: v for k, v in bilanz['bericht'].items() if k not in ('loch', 'messung')})
        for zeile in Schammessung.zeilen(bilanz['bericht']['messung']):
            self.stdout.write(zeile)
        uebertrag = bilanz['bericht'].get('regler_uebertrag') or {}
        if uebertrag.get('pruefung'):
            for zeile in Dazgeograftmorphuebertrag.zeilen(uebertrag['pruefung']):
                self.stdout.write(zeile)
        elif uebertrag.get('fehler'):
            self.stdout.write('REGLER-ÜBERNAHME GESCHEITERT: %s' % uebertrag['fehler'])
