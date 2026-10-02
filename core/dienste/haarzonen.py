# -*- coding: utf-8 -*-
"""Haarzonen — eine Haarfarbe je Kopfzone, aus den Fotos (02.10.2026, nachts).

Befund Edgar (01.10.2026): „das haar hat oben eine andere Farbe als unten". Die Fotos zeigen das Haar oben und vorn
weißgrau, am Hinterkopf dunkelgrau; eine Tönung je Frisur (`m.haar_farbe`) ist ein Kompromiss. Die Karten einer Frisur
teilen sich die UV-Fläche (die Haar-Fototextur mittelte sich deshalb zu Dunkelgrau, `IterationHaare.FOTOTEXTUR`) — die
Farbe muss also an die Karten, nicht in die Textur.

- `zonen(punkte, dreiecke)`: je Dreieck eine Zone (`ZONEN`) aus der Richtung seines Schwerpunkts von der Kopfmitte
  (Mitte des Haarkastens): oben, hinten, vorn, Seite — in der Ruhelage, damit Messung und Bau dieselben Dreiecke meinen
- `anwenden(teile, farben)`: je Haarteil die Dreiecke jeder Materialgruppe nach Zonen sortiert, die Gruppe in Zonen
  geteilt, der Farbfaktor mit `Zonenfarbe / Haarfarbe` multipliziert (Rezept: `m.haar_zonenfarbe(zone, '#rrggbb')`,
  steht in `modell.farben['haarzone:<zone>']`) — Runde (Mitsuba) und Bühne (`Standmodellglb`) lesen den Faktor je Gruppe
- `messen(teile, projektion, index)`: Fotofarbe je Zone (Median über die Punkte, die ein Foto zugewandt sieht) relativ
  zum Median des ganzen Haars → `{zone: Verhältnis (3,)}`; daraus macht `IterationHaare` die Zonenfarben
"""

import numpy as np

__all__ = ['Haarzonen']


class Haarzonen:
    ZONEN = ('oben', 'hinten', 'vorn', 'seite')
    PRAEFIX = 'haarzone:'
    #: Richtung vom Kopfmittelpunkt: oben ab y > `OBEN`, sonst hinten/vorn ab |z| > `TIEFE` (Genesis blickt nach +z).
    OBEN = 0.55
    TIEFE = 0.35
    #: Ein Bart (`…_beard`) ist keine Kopfzone.
    OHNE = ('_beard',)
    VERHAELTNIS = (0.4, 2.5)

    @classmethod
    def zonen(cls, punkte, dreiecke):
        punkte = np.asarray(punkte, dtype=np.float64)
        mitte_d = punkte[np.asarray(dreiecke, dtype=np.int64)].mean(axis=1)
        lo, hi = punkte.min(axis=0), punkte.max(axis=0)
        mitte = (lo + hi) / 2.0
        mitte[1] = hi[1] - 0.6 * (hi[1] - lo[1])                    # Kopfmitte unter dem Scheitel
        d = mitte_d - mitte
        d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)
        zone = np.full(len(d), cls.ZONEN.index('seite'))
        zone[d[:, 2] > cls.TIEFE] = cls.ZONEN.index('vorn')
        zone[d[:, 2] < -cls.TIEFE] = cls.ZONEN.index('hinten')
        zone[d[:, 1] > cls.OBEN] = cls.ZONEN.index('oben')
        return zone

    @staticmethod
    def _hex(text):
        roh = str(text or '').lstrip('#')
        return np.array([int(roh[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]) if len(roh) == 6 else None

    @classmethod
    def faktoren(cls, farben):
        """`{zone: (3,)}` = Zonenfarbe / Haarfarbe aus `modell.farben`; leer ohne Zonenfarben."""
        grund = cls._hex((farben or {}).get('haar'))
        if grund is None:
            return {}
        aus = {}
        for zone in cls.ZONEN:
            f = cls._hex((farben or {}).get(cls.PRAEFIX + zone))
            if f is not None:
                aus[zone] = np.clip(f / np.maximum(grund, 1e-3), *cls.VERHAELTNIS)
        return aus

    @classmethod
    def anwenden(cls, teile, farben):
        faktoren = cls.faktoren(farben)
        if not faktoren:
            return teile
        for t in teile:
            if t.get('art') != 'haar' or not t.get('textur') or any(o in str(t.get('sorte')) for o in cls.OHNE):
                continue
            zone = cls.zonen(t['punkte'], t['dreiecke'])
            dreiecke, textur = np.asarray(t['dreiecke']).copy(), []
            for eintrag in t['textur']:
                ab, anzahl = int(eintrag['ab']), int(eintrag['anzahl'])
                reihe = ab + np.argsort(zone[ab:ab + anzahl], kind='stable')
                dreiecke[ab:ab + anzahl] = np.asarray(t['dreiecke'])[reihe]
                zonen_hier = zone[reihe]
                for z in np.unique(zonen_hier):
                    stueck = np.flatnonzero(zonen_hier == z)
                    neu = dict(eintrag, ab=ab + int(stueck[0]), anzahl=len(stueck))
                    f = faktoren.get(cls.ZONEN[int(z)])
                    if f is not None and eintrag.get('faktor') is not None:
                        neu['faktor'] = np.clip(np.asarray(eintrag['faktor']) * f, 0.0, 1.0)
                    textur.append(neu)
            t['dreiecke'], t['textur'] = dreiecke, textur
        return teile

    @classmethod
    def messen(cls, teile, projektion):
        """`{sorte: {zone: [r, g, b] Verhältnis zum ganzen Haar}}` aus den Fotos — nur Kopfhaar mit Textur."""
        aus = {}
        for t in teile:
            if t.get('art') != 'haar' or not t.get('textur') or any(o in str(t.get('sorte')) for o in cls.OHNE):
                continue
            ruhe = t.get('ruhe', t)
            zone_d = cls.zonen(ruhe['punkte'], ruhe['dreiecke'])
            punkte = np.asarray(t['punkte'], dtype=np.float64)
            mitte = punkte[np.asarray(t['dreiecke'], dtype=np.int64)].mean(axis=1)
            # Karten sind zweiseitig, ihre Flächennormale zeigt beliebig: „zugewandt" heißt hier vom Kopf weg
            lo, hi = punkte.min(axis=0), punkte.max(axis=0)
            kopf = np.array([(lo[0] + hi[0]) / 2, hi[1] - 0.6 * (hi[1] - lo[1]), (lo[2] + hi[2]) / 2])
            normale = mitte - kopf
            normale /= np.maximum(np.linalg.norm(normale, axis=1, keepdims=True), 1e-12)
            farbe, getroffen = projektion.farben(mitte, normale)
            if getroffen.sum() < 50:
                continue
            gesamt = np.median(farbe[getroffen], axis=0)
            zonen = {}
            for i, name in enumerate(cls.ZONEN):
                wahl = getroffen & (zone_d == i)
                if wahl.sum() >= 30:
                    verhaeltnis = np.median(farbe[wahl], axis=0) / np.maximum(gesamt, 1e-3)
                    zonen[name] = [round(float(v), 4) for v in verhaeltnis]
            if zonen:
                aus[str(t.get('sorte'))] = zonen
        return aus
