# -*- coding: utf-8 -*-
u"""`manage.py uma_beispiele` — drei UMA-Figuren in Python bauen und ablegen.

WARUM (Edgar, 08.09.2026: „Speichere ggf. auf der Platte 3 Beispiel Modelle
fuer UMA Python fuer diese 3 Optionen")
=====================================================================
Der Bau einer Rasse kostet gemessen 6 bis 14 Sekunden, weil acht
Slot-Assets zu zerlegen sind (fuenf davon ueber 2 MB). Das ist fuer den
ersten Blick zuviel — und es ist zugleich der beste Beleg dafuer, dass der
Port wirklich rechnet: Die Dateien liegen danach da, mit Punktzahl,
Knochenzahl und Hoehe.

WAS ABGELEGT WIRD, UND WARUM ZWEI FORMATE
=========================================
    <rasse>.obj     Netz in Szenenlage (m, Y oben) — mit jedem Werkzeug
                    zu oeffnen, ohne Kenntnis dieses Projekts
    <rasse>.json    Beipackzettel: Rasse, Punkt- und Knochenzahl, Hoehe,
                    Reglerstellung, und die Ruhe-Probe

Die Ruhe-Probe steht im Zettel, weil sie die Aussage IST: Sie muss null
sein, und ein Beispiel, das ohne sie abgelegt wird, belegt nichts.

Die Dateien liegen unter `Figuren/uma_python/` — neben `Figuren/uma/`, wo
die von Unity gebauten stehen. Der Vertrag daneben (`Figuren/VERTRAG.md`)
bleibt unberuehrt: Roomguest liest `humanbody/`, `uma/` und `unified/`.
"""
import json
import time

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = u'Baut Beispiel-UMA-Figuren in Python und legt sie ab.'

    #: Die drei, die Edgar nennt — Male, Female, Elf.
    VORGABE = ('Human Male 3.0', 'Human Female 3.0', 'Elf Male')

    def add_arguments(self, parser):
        parser.add_argument(
            '--rasse', action='append', dest='rassen',
            help=u'Rassenname aus dem Katalog; mehrfach angebbar. '
                 u'Ohne Angabe: %s' % ', '.join(self.VORGABE))
        parser.add_argument(
            '--ordner', default=None,
            help=u'Zielordner (Vorgabe: Figuren/uma_python)')

    def handle(self, *args, **optionen):
        from UMA_Python import Figur
        from UMA_Python.szene import Szenenfigur

        ziel = self._ordner(optionen.get('ordner'))
        rassen = optionen.get('rassen') or list(self.VORGABE)
        figur = Figur(settings.UMA_PROJEKT)
        bekannt = set(figur.rassen())

        for rasse in rassen:
            if rasse not in bekannt:
                self.stderr.write(u'Unbekannte Rasse: %s' % rasse)
                continue
            beginn = time.time()
            gebaut = figur.bauen(rasse)
            dauer = time.time() - beginn
            zettel = self._ablegen(ziel, gebaut, Szenenfigur, dauer)
            self.stdout.write(
                u'%-20s %6d Punkte  %3d Knochen  %.2f m  %.1f s  '
                u'Ruhe %.4f mm'
                % (rasse, zettel['punkte'], zettel['knochen'],
                   zettel['hoehe_m'], dauer, zettel['ruhe_mm']))

    # ------------------------------------------------------------------ Ort

    @staticmethod
    def _ordner(angabe):
        from pathlib import Path
        if angabe:
            ziel = Path(angabe)
        else:
            ziel = Path(str(settings.TOOLS_ROOT)) / 'Figuren' / 'uma_python'
        ziel.mkdir(parents=True, exist_ok=True)
        return ziel

    @staticmethod
    def _dateiname(rasse):
        u"""Rassenname -> Dateiname. Nur was ein Dateisystem vertraegt.

        Positivliste, keine Verbotsliste: „Human Female 3.0" traegt Punkte
        und Leerzeichen, und eine Verbotsliste hat in diesem Projekt schon
        zweimal einen Fall uebersehen (`Stoffexportziel`, 01.09.2026).
        """
        erlaubt = [z if (z.isalnum() or z in '-_') else '_' for z in rasse]
        return ''.join(erlaubt).strip('_')

    # ---------------------------------------------------------------- Ablage

    @classmethod
    def _ablegen(cls, ziel, gebaut, Szenenfigur, dauer):
        name = cls._dateiname(gebaut.rasse)
        punkte = Szenenfigur.nach_yoben(gebaut.punkte())
        dreiecke = gebaut.netz.dreiecke
        cls._obj(ziel / ('%s.obj' % name), punkte, dreiecke, gebaut.rasse)

        zettel = {
            'rasse': gebaut.rasse,
            'quelle': 'UMA_Python',
            'punkte': int(len(punkte)),
            'dreiecke': int(len(dreiecke)),
            'knochen': len(gebaut.netz.knochen),
            'slots': len(gebaut.netz.bereiche),
            'hoehe_m': round(float(punkte[:, 1].max() - punkte[:, 1].min()), 4),
            'lage': 'Meter, Y oben (Szenenlage)',
            'bauzeit_s': round(dauer, 2),
            'ruhe_mm': cls._ruhe_mm(gebaut),
            'dna': {n: float(w) for n, w in gebaut.dna.items()},
            'regler': len(gebaut.regler),
            'fehlende_slots': gebaut.fehlend,
        }
        (ziel / ('%s.json' % name)).write_text(
            json.dumps(zettel, indent=2, ensure_ascii=False), encoding='utf-8')
        return zettel

    @staticmethod
    def _ruhe_mm(gebaut):
        u"""Die Ruhe-Probe in Millimetern: Skelett unveraendert, Haut
        gerechnet — das Ergebnis MUSS das Eingangsnetz sein.

        Sie steht im Zettel, weil sie die Aussage ist. Ein Beispiel ohne
        sie belegt nur, dass eine Datei geschrieben wurde.
        """
        from UMA_Python.haut import Haut
        from UMA_Python.skelett import Skelett
        netz = gebaut.netz
        skelett = Skelett(netz.knochen)
        matrizen = Haut.matrizen(skelett.weltmatrizen(), netz.bindeposen)
        ruhe = Haut.verformen(netz.punkte, netz.gewichte,
                              netz.knochenindex, matrizen)
        return round(float(np.abs(ruhe - netz.punkte).max()) * 1000.0, 4)

    @staticmethod
    def _obj(pfad, punkte, dreiecke, rasse):
        u"""Netz als OBJ. Nur Punkte und Flaechen — Texturen rechnet der
        Port nicht mit, und ein leeres `vt` waere eine Behauptung."""
        zeilen = ['# %s — UMA_Python, Meter, Y oben' % rasse]
        zeilen += ['v %.6f %.6f %.6f' % tuple(p) for p in punkte]
        zeilen += ['f %d %d %d' % (a + 1, b + 1, c + 1)
                   for a, b, c in dreiecke]
        pfad.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
