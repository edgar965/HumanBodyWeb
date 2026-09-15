# -*- coding: utf-8 -*-
u"""`manage.py mimik_vorbereiten` — die Mimik-Posenbibliothek aus MB-Lab bauen.

Liest die MB-Lab-Ausdrücke (`tools/MB-Lab/data`), rechnet jede Einheit über
die Hautgewichte in Drehungen der 49 DEF-Gesichtsknochen um
(`humanbody_core.mimik`) und schreibt

    static/mimik/basis.json     Einheit → Knochendrehungen (+1 / −1)
    static/mimik/posen.json     78 Posen mit Namen, Gruppe und Gewichten
    static/mimik/vorschau/      Kopfbilder je Pose (mit --vorschau)

Die Dateien sind versioniert; der Lauf ist nur nach einem Wechsel der
MB-Lab-Daten oder des Skeletts nötig. Schreibt nichts nach `HumanBody/data/`.
"""
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from humanbody_core.mimik.knochendeltas import Knochendeltas
from humanbody_core.mimik.mblab_ausdruecke import MblabAusdruecke
from humanbody_core.mimik.posenbibliothek import Posenbibliothek


class Command(BaseCommand):
    help = u'Mimik-Posen aus den MB-Lab-Ausdrücken für das DEF-Skelett bauen'

    def add_arguments(self, parser):
        parser.add_argument('--vorschau', action='store_true',
                            help=u'Kopfbilder je Pose rendern (pyrender)')

    def handle(self, *args, **optionen):
        mblab = settings.TOOLS_ROOT / 'tools' / 'MB-Lab' / 'data'
        daten = settings.HUMANBODY_ROOT / 'data' / 'humanBody'
        if not mblab.is_dir():
            raise CommandError(u'MB-Lab-Daten fehlen: %s' % mblab)
        ziel = settings.BASE_DIR / 'static' / 'mimik'
        ziel.mkdir(parents=True, exist_ok=True)

        start = time.perf_counter()
        ausdruecke = MblabAusdruecke(str(mblab))
        deltas = Knochendeltas(str(daten / 'def_skeleton.json'),
                               str(daten / 'skin_weights_base.json'),
                               str(daten / 'vertices_tpose.npy'))
        bibliothek = Posenbibliothek(ausdruecke, deltas)
        bibliothek.schreiben(str(ziel / 'basis.json'), str(ziel / 'posen.json'))
        posen = bibliothek.posen()
        basis = bibliothek.basis()
        knochen = {k for e in basis.values() for r in e.values() for k in r}
        self.stdout.write(u'%d Einheiten, %d Posen, %d Gesichtsknochen bewegt, %.1f s'
                          % (len(basis), len(posen), len(knochen),
                             time.perf_counter() - start))
        if optionen.get('vorschau'):
            from core.dienste.mimikvorschau import Mimikvorschau
            anzahl = Mimikvorschau(ausdruecke, daten, ziel / 'vorschau').alle(posen)
            self.stdout.write(u'%d Vorschaubilder' % anzahl)
