# -*- coding: utf-8 -*-
"""Mesh3daibild — aus EINER Pose (Knochenpunkte des Genesis-Rigs, `Mesh3dairig`) ein Bild in der Form einer Probe der Seite „Mesh3D-AI" (14.10.2026).

Dieselbe Rechnung für die 50 Proben und für die Bilder der Bewegung (`Mesh3daianimation`): Soll und „Ausgabe des Netzes" (= Soll plus Rauschen, `Mesh3dairausch`) für den ganzen Körper und für jede Zeile
darunter (nur Körper, Gesicht, Hände/Füße, Kleider), je mit Kennzahlen und den Rig-Punkten der Zeile. Die Flächen sind Dummies (Kapseln um 22 Gelenke, die aus dem Rig folgen; `Mesh3daikoerper`,
`Mesh3daigesicht`, `Mesh3daihaende`, `Mesh3daikleider`), das Rig selbst ist echt. Nichts ist trainiert.

    Mesh3daibild.bauen(pose, aufteilung, rausch) -> {soll, ausgabe, kennzahlen, eingabe, rig, teile: {schluessel: {soll, ausgabe, kennzahlen, eingabe, rig, …}}}
"""

import random

import numpy as np

from .mesh3daigeruest import Mesh3daigeruest
from .mesh3dairig import Mesh3dairig

__all__ = ['Mesh3daibild']


class Mesh3daibild:
    EINGABE_PUNKTE = 4096

    @staticmethod
    def _kennzahlen(soll, ausgabe, namen, gruppen, schwelle_mm=10.0):
        """Fehler je Punkt in mm, Mittel, größter, Anteil unter `schwelle_mm` und Mittel je Gruppe (`gruppen`: Gruppe je Punkt)."""
        fehler_mm = 1000.0 * np.linalg.norm(np.asarray(soll, dtype=float) - np.asarray(ausgabe, dtype=float), axis=1)
        schlimmster = int(np.argmax(fehler_mm))
        je_gruppe = {}
        for gruppe, f in zip(gruppen, fehler_mm):
            je_gruppe.setdefault(gruppe, []).append(f)
        return {'mittel_mm': round(float(fehler_mm.mean()), 1), 'groesster_mm': round(float(fehler_mm[schlimmster]), 1), 'groesster_gelenk': namen[schlimmster],
                'schwelle_mm': schwelle_mm, 'unter_schwelle_prozent': round(100.0 * float((fehler_mm < schwelle_mm).mean()), 0),
                'je_gelenk_mm': [round(float(f), 1) for f in fehler_mm], 'je_gruppe_mm': {g: round(float(np.mean(v)), 1) for g, v in je_gruppe.items()}}

    @classmethod
    def _rig(cls, soll, schluessel, indizes, beschr, basis, rausch):
        """Die Rig-Punkte einer Zeile: Soll, Ausgabe (Soll plus Rauschen mit dem Pegel der Zeile mal Gruppenfaktor), Fehler je Knochen und die Kennzahlen."""
        gruppen = [beschr['knochen'][i]['gruppe'] for i in indizes]
        namen = [beschr['knochen'][i]['name'] for i in indizes]
        sigma = basis * np.array([Mesh3dairig.RAUSCHFAKTOR.get(g, 1.0) for g in gruppen])
        ausgabe = np.asarray(soll) + rausch.werte('rig_' + schluessel, sigma)
        k = cls._kennzahlen(soll, ausgabe, namen, gruppen, 10.0)
        return {'soll': np.round(soll, 4).tolist(), 'ausgabe': np.round(ausgabe, 4).tolist(), 'je_mm': k['je_gelenk_mm'],
                'kennzahlen': {'mittel_mm': k['mittel_mm'], 'groesster_mm': k['groesster_mm'], 'groesster_knochen': k['groesster_gelenk'], 'knochen': len(indizes)}}

    @classmethod
    def bauen(cls, pose, aufteilung, rausch):
        """`pose` aus `Mesh3dairig.ausrichten`; `aufteilung` 'training' | 'pruefung' (Pegel des Rauschens); `rausch` ein `Mesh3dairausch`."""
        from .mesh3daiattrappe import Mesh3daiattrappe as A

        beschr = Mesh3dairig.beschreibung()
        lagen = Mesh3dairig.lagen(pose)
        drehungen = Mesh3dairig.drehungen(lagen, pose['kopf'])
        rig = Mesh3dairig.zeilen(pose)
        gelenke = Mesh3daigeruest.beschreibung()
        namen, gruppen = Mesh3daigeruest.namen(), [g['gruppe'] for g in gelenke]
        sigma = A.RAUSCHEN[aufteilung] * np.array([A.GRUPPENFAKTOR[g] for g in gruppen])
        soll = lagen.round(4)
        ausgabe = (soll + rausch.werte('koerper', sigma)).round(4)
        bild = {'soll': soll.tolist(), 'ausgabe': ausgabe.tolist(), 'kennzahlen': cls._kennzahlen(soll, ausgabe, namen, gruppen), 'eingabe': {'punkte': cls.EINGABE_PUNKTE},
                'rig': cls._rig(rig['koerper'], 'koerper', beschr['zeilen']['koerper'], beschr, A.RAUSCHEN[aufteilung], rausch), 'teile': {}}
        for k, klasse in enumerate(A.TEILE):
            teil = klasse.soll({}, [tuple(x) for x in lagen], drehungen, random.Random(8000 + k))
            teil['ausgabe'] = (np.asarray(teil['soll']) + rausch.werte(klasse.SCHLUESSEL, klasse.RAUSCHEN[aufteilung])).round(5).tolist()
            punkte = A.beschreibungen()[klasse.SCHLUESSEL]['punkte']
            teil['kennzahlen'] = cls._kennzahlen(teil['soll'], teil['ausgabe'], [p['name'] for p in punkte], [p['gruppe'] for p in punkte], klasse.SCHWELLE_MM)
            teil['eingabe'] = {'punkte': klasse.EINGABE_PUNKTE}
            teil['rig'] = cls._rig(rig[klasse.SCHLUESSEL], klasse.SCHLUESSEL, beschr['zeilen'][klasse.SCHLUESSEL], beschr, klasse.RAUSCHEN[aufteilung], rausch)
            bild['teile'][klasse.SCHLUESSEL] = teil
        return bild
