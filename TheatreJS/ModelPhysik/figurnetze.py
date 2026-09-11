# -*- coding: utf-8 -*-
u"""Laedt Koerper und Kleidungsstuecke in EINE gemeinsame Form.

Beide werden am Ende gleich behandelt: Punkte, Dreiecke, eine
Gewichtsmatrix und die Namen ihrer Spalten. Was danach kommt, sieht keinen
Unterschied mehr zwischen Haut und Stoff — und genau deshalb koennen sie
nicht auseinanderlaufen.

DIE GEWICHTE LAUFEN UEBER ALLE 176 KNOCHEN des `def_skeleton`, nicht ueber
eine Auswahl. Das Stoff-Rig verweist auf alle 176; wer auf 31 oder 69
umleitet, verliert bei der Haelfte der Stoffpunkte einen Teil des Gewichts
(gemessen: 3.670 von 7.290), und LBS verteilt den Rest stumm um.
"""
import json
import os

import numpy as np


class Figurnetze:
    u"""Haut und Kleidung derselben Figur, mit denselben Knochenspalten."""

    def __init__(self, figur):
        self.figur = figur
        self.namen = list(figur.knochen.keys())
        self.spalte = {n: i for i, n in enumerate(self.namen)}

    # -------------------------------------------------------------- Koerper

    def koerper(self):
        u"""Aussenhaut der Figur mit Gewichten auf alle Knochen."""
        tabelle = json.load(
            open(os.path.join(self.figur.wurzel, 'skin_weights_base.json')))
        knochennamen, roh = tabelle['bone_names'], tabelle['weights']
        aus = np.zeros((len(self.figur.punkte), len(self.namen)))
        for zeile, alt in enumerate(self.figur.gewaehlt):
            for name, wert in self.figur._paare(roh[int(alt)], knochennamen):
                ziel = self.spalte.get(name)
                if ziel is not None:
                    aus[zeile, ziel] += float(wert)
        summe = aus.sum(axis=1, keepdims=True)
        return (np.asarray(self.figur.punkte, dtype=np.float64),
                np.asarray(self.figur.dreiecke, dtype=np.int64),
                aus / np.maximum(summe, 1e-9))

    def koerper_basis(self, punkte, vierecke):
        u"""ALLE Basispunkte der Figur (18.210) mit ihren Gewichten — das
        Steuernetz, aus dem `Feinkoerper` je Bild das sichtbare Netz
        unterteilt.

        WARUM (11.09.2026): Der Film renderte die 18K-Aussenhaut, an der
        die Leggings (an das 70K-Netz auf 2 mm angelegt) schon in Ruhe zu
        7,4 % innen lag — im Video kam die Haut durch, obwohl die Szene
        sauber war. Physik und LBS auf 70.851 Punkten kosteten 1,7 s je
        Bild; die Unterteilung ist LINEAR, also laeuft beides auf der Basis
        und das feine Netz folgt als `W @ basis` in Millisekunden.
        `vierecke` sind die Basisflaechen (17.288 x 4).
        """
        tabelle = json.load(
            open(os.path.join(self.figur.wurzel, 'skin_weights_base.json')))
        knochennamen, roh = tabelle['bone_names'], tabelle['weights']
        aus = np.zeros((len(punkte), len(self.namen)))
        for zeile in range(min(len(punkte), len(roh))):
            for name, wert in self.figur._paare(roh[zeile], knochennamen):
                ziel = self.spalte.get(name)
                if ziel is not None:
                    aus[zeile, ziel] += float(wert)
        summe = aus.sum(axis=1, keepdims=True)
        q = np.asarray(vierecke, dtype=np.int64)
        dreiecke = np.vstack([q[:, [0, 1, 2]], q[:, [0, 2, 3]]])
        return (np.asarray(punkte, dtype=np.float64), dreiecke,
                aus / np.maximum(summe, 1e-9))

    # ------------------------------------------------------------ Kleidung

    def stueck(self, pfad):
        u"""Ein Stueck aus seiner `*_sim_rig.json` — oder `.npz` aus der Szene.

        Die Gewichte liegen in der Rig-Datei DUENNBESETZT je Punkt als
        [[knochennummer, wert], ...]; die Nummer zeigt in die Liste
        `knochen` DER DATEI, nicht in unsere. Ueber den NAMEN umsetzen,
        nie ueber die Nummer — welche Spalte ein Knochen hat, entscheidet
        jede Datei fuer sich. Dasselbe gilt fuer die `.npz`, die der
        Server aus einem Szenennetz schreibt (`figurvideostuecke.py`):
        dort stehen `skin_index`/`skin_weight` als n x 4 plus `knochen`.
        """
        if pfad.endswith('.npz'):
            return self._szenenstueck(pfad)
        with open(pfad) as datei:
            daten = json.load(datei)
        punkte = np.asarray(daten['punkte'], dtype=np.float64).reshape(-1, 3)
        dreiecke = np.asarray(daten['dreiecke'],
                              dtype=np.int64).reshape(-1, 3)
        eigene = list(daten['knochen'])
        aus = np.zeros((len(punkte), len(self.namen)))
        unbekannt = set()
        for zeile, eintraege in enumerate(daten['gewichte']):
            for nummer, wert in eintraege:
                name = eigene[int(nummer)]
                ziel = self.spalte.get(name)
                if ziel is None:
                    unbekannt.add(name)
                    continue
                aus[zeile, ziel] += float(wert)
        if unbekannt:
            raise ValueError(u'%d Knochen des Stuecks fehlen im Skelett: %s'
                             % (len(unbekannt),
                                u', '.join(sorted(unbekannt)[:4])))
        summe = aus.sum(axis=1, keepdims=True)
        return punkte, dreiecke, aus / np.maximum(summe, 1e-9)

    def _szenenstueck(self, pfad):
        daten = np.load(pfad)
        punkte = np.asarray(daten['punkte'], dtype=np.float64)
        dreiecke = np.asarray(daten['dreiecke'], dtype=np.int64)
        namen = [str(n) for n in daten['knochen']]
        umsetzung = np.array([self.spalte.get(n, -1) for n in namen])
        nummern, gewichte = daten['skin_index'], daten['skin_weight']
        aus = np.zeros((len(punkte), len(self.namen)))
        unbekannt = set()
        for spalte in range(nummern.shape[1]):
            gilt = gewichte[:, spalte] > 0
            ziel = umsetzung[nummern[:, spalte]]
            fremd = gilt & (ziel < 0)
            if fremd.any():
                unbekannt.update(namen[k] for k in nummern[fremd, spalte])
            treffer = gilt & (ziel >= 0)
            np.add.at(aus, (np.nonzero(treffer)[0], ziel[treffer]),
                      gewichte[treffer, spalte])
        if unbekannt:
            raise ValueError(u'%d Knochen des Stuecks fehlen im Skelett: %s'
                             % (len(unbekannt),
                                u', '.join(sorted(unbekannt)[:4])))
        summe = aus.sum(axis=1, keepdims=True)
        return punkte, dreiecke, aus / np.maximum(summe, 1e-9)

    @staticmethod
    def sitzprobe(stoff, koerper):
        u"""Abstand des Stoffs zur Haut, in Millimetern.

        Die Probe darauf, dass Stueck und Koerper ueberhaupt zusammen-
        gehoeren. Ein Stueck, das auf einem ANDEREN Koerper drapiert wurde,
        faellt hier auf — im Video sieht man es erst, wenn es zu spaet ist.
        Ueber 40 mm heisst „sitzt nicht" (CLAUDE.md, 06.09.2026).
        """
        from scipy.spatial import cKDTree
        baum = cKDTree(koerper)
        abstand, _ = baum.query(stoff)
        return float(np.median(abstand)) * 1000.0
