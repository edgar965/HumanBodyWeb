# -*- coding: utf-8 -*-
u"""Stoffauftrag — die Kleidung des Films an Newton uebergeben und zurueckholen.

Sitzt zwischen `Hbfilm` (python14: Koerper und Stuecke je Bild aus dem LBS)
und `stoffnewton.py` (Newton-Umgebung, ohne Django). Der Austausch ist EINE
`.npz` im Laufordner: Koerper je Bild als Kollider, alle GarmentCode-Stuecke
als EIN Stoffnetz (damit Stoff auf Stoff kollidiert), die RUHELAGE der
Stuecke (die Drapierung auf der A-Haltung) fuer die Rest-Laengen, und je
Punkt, ob er FEST ist.

NICHT DIE UV DER RIG-DATEI als Panel-Ruhelage (gemessen 12.09.2026): Die
Dreiecke entlang der Naehte verbinden Punkte ZWEIER Panels — ihre UV-Kanten
sind bis zu 30-mal laenger als die Kante im Netz (p1 des Verhaeltnisses 3D/UV
0,03, p99 2,8). Als Rest-Laenge genommen sprengt das den Stoff im Einlauf
(10.821 von 22.781 Punkten mehr als 5 cm verschoben, ehe sich der Koerper
bewegt hat). Newton bekommt darum jedes Dreieck einzeln flach gelegt aus
seiner 3D-Ruhelage.

FEST ist das obere Band eines Stuecks (`bund` cm unter seinem hoechsten
Punkt): Bund der Hose, Bund des Rocks, Schulter und Halsloch des Shirts.
Diese Punkte folgen dem LBS wie bisher, alles darunter rechnet Newton.

DER STOFF STARTET IN DER RUHELAGE, NICHT IM SKINNING VON BILD 0 (gemessen
12.09.2026): Das LBS dehnt Kanten des Rocks in der ersten Tanzpose bis auf
das 39-fache (p99 2,7), das Shirt bis 6,4-fach — als Startzustand des
Loesers sprengt das den Stoff im ersten Teilschritt. Darum bekommt Newton
auch den Koerper in Ruhelage (`koerper_ruhe`) und eine RAMPE von
Zwischenposen (`Stofframpe`, im Gelenkraum) bis Bild 0; der Stoff folgt
ueber Kontakt und Bund.

Nach dem Lauf ersetzen die gerechneten Lagen die LBS-Lagen der Stuecke
(`teil['haut'].folge`), und die Hautmaske des Koerpers faellt weg: Sie war
in Ruhelage entschieden — hebt der Wind den Rock, laege darunter ein Loch
(dieselbe Falle wie MPFBs Delete-Maske in der Blender-Pipeline).
"""
import json
import os
import subprocess
import sys

import numpy as np

__all__ = ['Stoffauftrag']


class Stoffauftrag:

    FRISUR = 'Frisur '

    def __init__(self, film, ablage, parameter, melder, stuecke):
        u"""`film` ist der gerechnete `Hbfilm`; `stuecke` die Liste aus
        `Modellfigur.stuecke()` (Name -> Rig-Datei fuer die UV)."""
        self.film = film
        self.ablage = ablage
        self.p = parameter
        self.melder = melder
        self.rig_pfade = {s['name']: s['pfad'] for s in stuecke}
        self.teile = [t for t in film.teile[1:]
                      if not t['name'].startswith(self.FRISUR)
                      and self.rig_pfade.get(t['name'], '').endswith('.json')]

    # -------------------------------------------------------------- Ablauf

    def rechnen(self, python, skript, cache):
        if not self.teile:
            print(u'Stoff: kein GarmentCode-Stueck am Modell — nichts zu rechnen',
                  flush=True)
            return None
        self.melder(u'Stoff vorbereiten', 0.3)
        auftrag = os.path.join(self.ablage, 'stoffauftrag.npz')
        ergebnis = os.path.join(self.ablage, 'stoff.npz')
        grenzen = self._schreiben(auftrag)
        self._laufen(python, skript, auftrag, ergebnis, cache)
        with np.load(ergebnis) as d:
            folge = np.asarray(d['folge'], dtype=np.float64)
            ms = np.asarray(d['ms'], dtype=np.float64)
        for teil, (a, b) in zip(self.teile, grenzen):
            teil['haut'].folge = [folge[k, a:b] for k in range(len(folge))]
        # Ohne Hautmaske — der Stoff bewegt sich jetzt vom Koerper weg.
        self.film.teile[0].pop('maske', None)
        self.film.teile[0].pop('dreiecke_sichtbar', None)
        return {'stuecke': [t['name'] for t in self.teile],
                'punkte': int(folge.shape[1]),
                'ms_je_bild_median': round(float(np.median(ms)), 1) if len(ms) else None,
                'ms_je_bild_p90': round(float(np.percentile(ms, 90)), 1) if len(ms) else None}

    # ------------------------------------------------------------ Schreiben

    def _schreiben(self, pfad):
        koerper = self.film.teile[0]
        koerper_folge = np.stack(koerper['haut'].folge).astype(np.float32)
        punkte, ruhe, dreiecke, fest, grenzen = [], [], [], [], []
        versatz = 0
        for teil in self.teile:
            lagen = np.stack(teil['haut'].folge).astype(np.float32)
            n = lagen.shape[1]
            punkte.append(lagen)
            ruhe.append(np.asarray(teil['haut'].punkte, dtype=np.float32))
            dreiecke.append(np.asarray(teil['dreiecke'], dtype=np.int32) + versatz)
            fest.append(self._fest(lagen[0]))
            grenzen.append((versatz, versatz + n))
            versatz += n
        parameter = {
            'fps': self.p.fps, 'teilschritte': self.p.teilschritte,
            'iterationen': self.p.iterationen, 'wind': self.p.wind,
            'richtung': self._windrichtung().tolist(), 'turbulenz': self.p.turbulenz,
            'dichte': self.p.dichte, 'steifigkeit': self.p.steifigkeit,
            'biegung': self.p.biegung, 'einlauf': self.p.einlauf,
        }
        koerper_rampe, stoff_rampe = self._rampe(koerper)
        np.savez(pfad, parameter=json.dumps(parameter),
                 koerper_folge=koerper_folge,
                 koerper_ruhe=np.asarray(koerper['haut'].punkte, dtype=np.float32),
                 koerper_rampe=koerper_rampe, stoff_rampe=stoff_rampe,
                 koerper_dreiecke=np.asarray(koerper['dreiecke'], dtype=np.int32),
                 stoff_folge=np.concatenate(punkte, axis=1),
                 stoff_ruhe=np.concatenate(ruhe),
                 stoff_dreiecke=np.concatenate(dreiecke),
                 fest=np.concatenate(fest))
        return grenzen

    def _rampe(self, koerper):
        u"""Zwischenposen A-Haltung -> Bild 0 (`einlauf` Sekunden bei `fps`),
        im Gelenkraum interpoliert (`Stofframpe`): Koerper (S, Nb, 3) und
        alle Stuecke (S, Ns, 3)."""
        from .stofframpe import Stofframpe
        schritte = max(1, int(round(float(self.p.einlauf) * float(self.p.fps))))
        felder = Stofframpe(self.film.bahn).punkte(
            [koerper['haut']] + [t['haut'] for t in self.teile], schritte)
        return felder[0], np.concatenate(felder[1:], axis=1)

    def _fest(self, ruhe):
        u"""Das obere Band des Stuecks — `bund` cm unter dem hoechsten Punkt."""
        oben = float(ruhe[:, 2].max())
        return ruhe[:, 2] >= oben - float(self.p.bund) / 100.0

    def _windrichtung(self):
        u"""Aus der Blickrichtung des Rigs (Zehe gegen Fuss, Ruhelage, z oben)."""
        ruhe = self.film.bahn.ruhe
        vorn = np.array([0.0, -1.0, 0.0])
        if 'DEF-toe.L' in ruhe and 'DEF-foot.L' in ruhe:
            v = np.asarray(ruhe['DEF-toe.L'][0]) - np.asarray(ruhe['DEF-foot.L'][0])
            v[2] = 0.0
            if np.linalg.norm(v) > 1e-9:
                vorn = v / np.linalg.norm(v)
        seite = np.cross(np.array([0.0, 0.0, 1.0]), vorn)
        return {'seite': seite, 'vorn': -vorn, 'hinten': vorn}[self.p.windrichtung]

    # --------------------------------------------------------------- Laufen

    def _laufen(self, python, skript, auftrag, ergebnis, cache):
        if not os.path.isfile(python):
            raise ValueError(u'Newton-Umgebung fehlt: %s' % python)
        prozess = subprocess.Popen(
            [python, skript, auftrag, ergebnis, cache],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=os.path.dirname(skript))
        letzte = []
        for roh in prozess.stdout:
            zeile = roh.decode('utf-8', errors='replace').rstrip()
            letzte = (letzte + [zeile])[-30:]
            if zeile.startswith('Effekte: '):
                # Bruchform durchreichen: Stoff liegt zwischen 30 % und 45 %.
                teil = zeile[len('Effekte: '):]
                try:
                    n, m = [int(x) for x in teil.rsplit(u'—', 1)[1].split('/')]
                    self.melder(teil.rsplit(u'—', 1)[0].strip(), 0.3 + 0.15 * n / max(m, 1))
                except (ValueError, IndexError):
                    print(zeile, flush=True)
            else:
                print(zeile, flush=True)
        code = prozess.wait()
        if code != 0 or not os.path.isfile(ergebnis):
            raise RuntimeError(u'Newton endete mit Code %s:\n%s'
                               % (code, u'\n'.join(letzte)))
