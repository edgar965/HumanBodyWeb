# -*- coding: utf-8 -*-
u"""Objwerkstoffe — welches Objekt einer `.obj` welchen Werkstoff trägt, und
ob der eine Bildkarte hat.

WOZU (27.09.2026): `Exportfleckenpruefung` braucht die Objekte OHNE eigene
Bildkarte (nur `Kd`, z. B. Schuh, Kleid) — dort ist jede Farbabweichung im
Umriss ein Fund, keine Textur könnte sie erklären. Welche das sind, steht
nicht fest im Code, sondern in der jeweiligen Exportdatei (`o <name>` /
`usemtl <mat>` in der `.obj`, `map_Kd` in der `.mtl`) — siehe
`Gruppennetze.zerlegen`: ein Objekt trägt in dieser Datei genau EINEN
Werkstoff.
"""
from pathlib import Path


class Objwerkstoffe:

    def __init__(self, obj_pfad):
        self.obj_pfad = Path(obj_pfad)
        self.mtl_pfad = self._mtllib(self.obj_pfad)

    @staticmethod
    def _mtllib(obj_pfad):
        with obj_pfad.open('r', encoding='utf-8', errors='replace') as f:
            for zeile in f:
                if zeile.startswith('mtllib '):
                    name = zeile.split(None, 1)[1].strip()
                    return obj_pfad.parent / name
        return None

    def objekt_werkstoff(self):
        u"""`{objektname: werkstoffname}` — der zuletzt aktive `usemtl` je `o`-Block."""
        zuordnung = {}
        objekt = None
        with self.obj_pfad.open('r', encoding='utf-8', errors='replace') as f:
            for zeile in f:
                if zeile.startswith('o '):
                    objekt = zeile[2:].strip()
                elif zeile.startswith('usemtl ') and objekt:
                    zuordnung[objekt] = zeile.split(None, 1)[1].strip()
        return zuordnung

    def werkstoffe_ohne_karte(self):
        u"""Namen aller Werkstoffe, deren `newmtl`-Block kein `map_Kd` trägt
        (reine Farbe — `mat_15`/`mat_16` bei Damira: Kleid, Schuh)."""
        if not self.mtl_pfad or not self.mtl_pfad.is_file():
            return set()
        ohne = set()
        aktuell = None
        hat_karte = False
        with self.mtl_pfad.open('r', encoding='utf-8', errors='replace') as f:
            for zeile in f:
                if zeile.startswith('newmtl '):
                    if aktuell and not hat_karte:
                        ohne.add(aktuell)
                    aktuell = zeile.split(None, 1)[1].strip()
                    hat_karte = False
                elif zeile.startswith('map_Kd '):
                    hat_karte = True
        if aktuell and not hat_karte:
            ohne.add(aktuell)
        return ohne

    def objekte_ohne_karte(self):
        u"""Objektnamen, deren Werkstoff reine Farbe ist (kein `map_Kd`) —
        genau die Kandidaten für `Exportfleckenpruefung`."""
        ohne = self.werkstoffe_ohne_karte()
        return sorted(o for o, m in self.objekt_werkstoff().items() if m in ohne)

    def werkstoffwerte(self):
        u"""`{werkstoff: {'Kd': (r, g, b) | None, 'd': float, 'karte': bool}}`
        aus der `.mtl`. `Kd` ist None, wenn der Block gar keine Zeile `Kd`
        trägt (verlorene Farbe); `d` ist 1,0 ohne Zeile; `karte` gilt für
        `map_Kd` UND `map_d` (Haarkarten haben nur die Deckkraftmaske)."""
        if not self.mtl_pfad or not self.mtl_pfad.is_file():
            return {}
        werte = {}
        aktuell = None
        with self.mtl_pfad.open('r', encoding='utf-8', errors='replace') as f:
            for zeile in f:
                teile = zeile.split()
                if not teile:
                    continue
                if teile[0] == 'newmtl' and len(teile) > 1:
                    aktuell = zeile.split(None, 1)[1].strip()
                    werte[aktuell] = {'Kd': None, 'd': 1.0, 'karte': False}
                elif aktuell is None:
                    continue
                elif teile[0] == 'Kd' and len(teile) >= 4:
                    werte[aktuell]['Kd'] = tuple(float(t) for t in teile[1:4])
                elif teile[0] == 'd' and len(teile) >= 2:
                    werte[aktuell]['d'] = float(teile[1])
                elif teile[0] in ('map_Kd', 'map_d'):
                    werte[aktuell]['karte'] = True
        return werte
