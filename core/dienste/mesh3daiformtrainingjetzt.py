# -*- coding: utf-8 -*-
"""Mesh3daiformtrainingjetzt — die Zeilen „Jetzt“ über den Tabellen des Reiters „Formtraining“ auf /mesh-3D-AI/ (18.10.2026): was gerade läuft.

Edgar: „die gerade laufenden Jobs sehen“. Drei Quellen, alle von der Platte: die GPU-Sperre (`Mesh3daiformtraining.gpu`), die Trainingsläufe (Zustand läuft/steht) und die Summe des
Datenstands der Formvarianten (`Mesh3daiformvarianten.summe`). Ein Lauf, der auf die GPU oder auf die Daten WARTET, hinterlässt noch keine Datei — den sieht die Seite erst, wenn er beginnt.

    Mesh3daiformtrainingjetzt.zeilen(laeufe, summe, gpu) -> [Text, …]
"""

import time

from .mesh3daiformzellen import Mesh3daiformzellen as Z

__all__ = ['Mesh3daiformtrainingjetzt']


class Mesh3daiformtrainingjetzt:
    @classmethod
    def zeilen(cls, laeufe, summe, gpu, jetzt=None):
        jetzt = time.time() if jetzt is None else jetzt
        aus = [cls._gpu(gpu, jetzt)]
        laufend = [lf for lf in laeufe if lf['zustand'] == 'läuft']
        for lf in laufend:
            messung = (' · Gelenke Prüfung %s mm' % Z.mm(lf['rig_mm'])) if lf['rig_mm'] is not None else ''
            aus.append('Training läuft: %s (%s) — %s%s, letzte Zeile vor %s.' % (
                lf['kurz'], lf['art'], 'Epoche %d von %s' % (lf['epoche'], lf['epochen'] or '?') if lf['epoche'] else 'vor der ersten Epochenzeile', messung,
                Z.spanne(jetzt - (lf['letzte'] or jetzt))))
        if not laufend:
            aus.append('Kein Trainingslauf läuft.')
        for lf in laeufe:
            if lf['zustand'] == 'steht' and not lf['probe']:
                aus.append('Ohne Ergebnis stehen geblieben: %s — keine Zeile seit %s (abgebrochen oder abgestürzt).' % (lf['kurz'], Z.spanne(jetzt - (lf['letzte'] or jetzt))))
        if summe['figuren']:
            aus.append('Formvarianten: %s von %s mit Daten Fassung 9 fertig; Proben mit MIA %s von %s, mit Wolke v9 %s von %s%s.' % (
                Z.zahl(summe['fertig']), Z.zahl(summe['figuren']), Z.zahl(summe['mia']), Z.zahl(summe['geplant']), Z.zahl(summe['wolken']), Z.zahl(summe['geplant']),
                '; gerade gerechnet: %s Formvarianten' % Z.zahl(summe['aktiv']) if summe['aktiv'] else ''))
        return aus

    @staticmethod
    def _gpu(gpu, jetzt):
        if gpu is None:
            return 'GPU-Sperre: frei.'
        seit = (' seit %s Uhr (%s)' % (Z.uhr(gpu['seit']), Z.spanne(jetzt - gpu['seit']))) if gpu.get('seit') else ''
        return 'GPU-Sperre: gehalten von „%s“%s.' % (gpu['name'], seit)
