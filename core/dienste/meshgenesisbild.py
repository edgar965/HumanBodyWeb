# -*- coding: utf-8 -*-
"""Meshgenesisbild — aus EINER Pose (Knochenpunkte des Genesis-Rigs, `Meshgenesisrig`) ein Bild in der Form einer Probe der Seite „Mesh-Genesis" (14.10.2026).

Dieselbe Rechnung für die 50 Proben und für die Bilder der Bewegung (`Meshgenesisanimation`): Soll und „Ausgabe des Netzes" (= Soll plus Rauschen, `Meshgenesisrausch`) für den ganzen Körper und für jede Zeile
darunter (nur Körper, Gesicht, Hände/Füße, Kleider), je mit Kennzahlen und den Rig-Punkten der Zeile. Die Flächen sind Dummies (Kapseln um 22 Gelenke, die aus dem Rig folgen; `Meshgenesiskoerper`,
`Meshgenesisgesicht`, `Meshgenesishaende`, `Meshgenesiskleider`), das Rig selbst ist echt. Nichts ist trainiert.

    Meshgenesisbild.bauen(pose, aufteilung, rausch) -> {soll, ausgabe, kennzahlen, eingabe, rig, teile: {schluessel: {soll, ausgabe, kennzahlen, eingabe, rig, …}}}
"""

import random

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .meshgenesisgeruest import Meshgenesisgeruest
from .meshgenesisrig import Meshgenesisrig

__all__ = ['Meshgenesisbild']


class Meshgenesisbild:
    EINGABE_PUNKTE = 4096

    @staticmethod
    def _kennzahlen(soll, ausgabe, namen, gruppen, schwelle_mm=10.0):
        """Fehler je Punkt in mm, Mittel, größter, Anteil unter `schwelle_mm` und Mittel je Gruppe (`gruppen`: Gruppe je Punkt)."""
        fehler_mm = 1000.0 * Torchfeld.linalg_norm(Torchfeld.feld(soll, dtype=torch.float64) - Torchfeld.feld(ausgabe, dtype=torch.float64), dim=1)
        schlimmster = int(Torchfeld.argmax(fehler_mm))
        je_gruppe = {}
        for gruppe, f in zip(gruppen, fehler_mm):
            je_gruppe.setdefault(gruppe, []).append(f)
        return {'mittel_mm': round(float(fehler_mm.mean()), 1), 'groesster_mm': round(float(fehler_mm[schlimmster]), 1), 'groesster_gelenk': namen[schlimmster],
                'schwelle_mm': schwelle_mm, 'unter_schwelle_prozent': round(100.0 * float((fehler_mm < schwelle_mm).mean()), 0),
                'je_gelenk_mm': [round(float(f), 1) for f in fehler_mm], 'je_gruppe_mm': {g: round(float(Torchfeld.mean(v)), 1) for g, v in je_gruppe.items()}}

    @classmethod
    def _rig(cls, soll, schluessel, indizes, beschr, basis, rausch):
        """Die Rig-Punkte einer Zeile: Soll, Ausgabe (Soll plus Rauschen mit dem Pegel der Zeile mal Gruppenfaktor), Fehler je Knochen und die Kennzahlen."""
        gruppen = [beschr['knochen'][i]['gruppe'] for i in indizes]
        namen = [beschr['knochen'][i]['name'] for i in indizes]
        sigma = basis * Torchfeld.feld([Meshgenesisrig.RAUSCHFAKTOR.get(g, 1.0) for g in gruppen], copy=True)
        ausgabe = Torchfeld.feld(soll) + rausch.werte('rig_' + schluessel, sigma)
        k = cls._kennzahlen(soll, ausgabe, namen, gruppen, 10.0)
        return {'soll': Torchfeld.round(soll, 4).tolist(), 'ausgabe': Torchfeld.round(ausgabe, 4).tolist(), 'je_mm': k['je_gelenk_mm'],
                'kennzahlen': {'mittel_mm': k['mittel_mm'], 'groesster_mm': k['groesster_mm'], 'groesster_knochen': k['groesster_gelenk'], 'knochen': len(indizes)}}

    @classmethod
    def bauen(cls, pose, aufteilung, rausch):
        """`pose` aus `Meshgenesisrig.ausrichten`; `aufteilung` 'training' | 'pruefung' (Pegel des Rauschens); `rausch` ein `Meshgenesisrausch`."""
        from .meshgenesisattrappe import Meshgenesisattrappe as A

        beschr = Meshgenesisrig.beschreibung()
        lagen = Meshgenesisrig.lagen(pose)
        drehungen = Meshgenesisrig.drehungen(lagen, pose['kopf'])
        rig = Meshgenesisrig.zeilen(pose)
        gelenke = Meshgenesisgeruest.beschreibung()
        namen, gruppen = Meshgenesisgeruest.namen(), [g['gruppe'] for g in gelenke]
        sigma = A.RAUSCHEN[aufteilung] * Torchfeld.feld([A.GRUPPENFAKTOR[g] for g in gruppen], copy=True)
        soll = lagen.round(decimals=4)
        ausgabe = (soll + rausch.werte('koerper', sigma)).round(decimals=4)
        bild = {'soll': soll.tolist(), 'ausgabe': ausgabe.tolist(), 'kennzahlen': cls._kennzahlen(soll, ausgabe, namen, gruppen), 'eingabe': {'punkte': cls.EINGABE_PUNKTE},
                'rig': cls._rig(rig['koerper'], 'koerper', beschr['zeilen']['koerper'], beschr, A.RAUSCHEN[aufteilung], rausch), 'teile': {}}
        for k, klasse in enumerate(A.TEILE):
            teil = klasse.soll({}, [tuple(x) for x in lagen], drehungen, random.Random(8000 + k))
            teil['ausgabe'] = (Torchfeld.feld(teil['soll']) + rausch.werte(klasse.SCHLUESSEL, klasse.RAUSCHEN[aufteilung])).round(decimals=5).tolist()
            punkte = A.beschreibungen()[klasse.SCHLUESSEL]['punkte']
            teil['kennzahlen'] = cls._kennzahlen(teil['soll'], teil['ausgabe'], [p['name'] for p in punkte], [p['gruppe'] for p in punkte], klasse.SCHWELLE_MM)
            teil['eingabe'] = {'punkte': klasse.EINGABE_PUNKTE}
            teil['rig'] = cls._rig(rig[klasse.SCHLUESSEL], klasse.SCHLUESSEL, beschr['zeilen'][klasse.SCHLUESSEL], beschr, klasse.RAUSCHEN[aufteilung], rausch)
            bild['teile'][klasse.SCHLUESSEL] = teil
        return bild
