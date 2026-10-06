# -*- coding: utf-8 -*-
"""Hautproben — die Fotofarbe der Haut je Texel und Ansicht, vom Licht befreit und ohne Hände (05.10.2026).

Aus `Koerperfotoprojektion._kachel` herausgelöst (Edgar, Auftrag 2026.10.04.21.41.43: „das Licht aus der Vorlage herausrechnen", „Texturprobleme auch bei der Hand"). Die Projektion kannte nur die Mischung aller Ansichten
(`Fotoprojektion.farben`) — das Licht jeder Ansicht lässt sich aber nur je Ansicht herausrechnen. Darum hier der Weg:

1. `sammeln(karten)`: für die Texel einer Kachel (`G9uvraster`-Karten: Lage, Normale, Maske, Dreieck) je Ansicht die Fotofarbe, den Kosinus Normale · Blick und ob der Punkt im Foto auf der Figur liegt;
   dazu, ob der Texel zur Hand gehört (Hautgewicht auf den Hand- und Fingerknochen des Dreiecks, `HAND_AB`, ein paar Texel erweitert).
2. `licht_schaetzen(alle)`: je Ansicht das Licht (`Fotolicht`, allgemein in `Fotoprojektion`) über ALLE Kacheln zusammen angepasst.
3. `farbe(proben)`: je Texel das nach Kosinus⁴ gewichtete Mittel der Ansichten, jede durch ihren Lichtfaktor geteilt; die Deckung = bester Kosinus (wie `Koerperfotoprojektion.DECKUNG`), 0 an der Hand.

Warum nicht die Fotos selbst entlichten? Im Foto fehlt die Normale je Pixel; im Texelraum liegen Lage und Normale vor — das Licht ist eine Funktion beider.
"""

import re

import numpy as np

from iterationen2d3d.fotolicht import Fotolicht

__all__ = ['Hautproben']


class Hautproben:
    #: Knochen der Hand: Hand, Finger, Mittelhand (Genesis 9: `l_hand`, `l_thumb1`, `l_index2`, `l_mid`, `l_ring`, `l_pinky`, `l_carpal1`, `l_metacarpal`…).
    HAND = re.compile(r'^[lr]_(hand|thumb|index|mid|ring|pinky|carpal|metacarpal)')
    #: Ab diesem Hautgewicht auf den Handknochen (Mittel der drei Eckpunkte eines Dreiecks) gehört ein Texel zur Hand, und so viele Texel wird der Bereich erweitert (Handgelenk).
    HAND_AB = 0.3
    HAND_RAND_PX = 6
    #: Deckung: ab `DECKUNG[0]` (Kosinus Normale · Blick) beginnt das Foto, ab `DECKUNG[1]` gilt es ganz.
    DECKUNG = (0.25, 0.6)
    AUSRICHTUNG = 4.0

    def __init__(self, projektion, haut, dreiecke):
        """`projektion`: `Fotoprojektion` mit den Ansichten; `haut`: `{knochen, index, gewicht}` je Punkt des Körpers; `dreiecke` (T, 3) des Körpers."""
        self.projektion = projektion
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        self.hand_je_dreieck = self._hand(haut)

    def _hand(self, haut):
        """Hautgewicht auf den Handknochen je Dreieck (T,) — Null ohne solche Knochen."""
        namen = [str(n) for n in (haut or {}).get('knochen') or []]
        ziele = [i for i, n in enumerate(namen) if self.HAND.match(n)]
        if not ziele:
            return np.zeros(len(self.dreiecke))
        index = np.asarray(haut['index']).reshape(-1, 4)
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64).reshape(-1, 4)
        je_punkt = (gewicht * np.isin(index, ziele)).sum(axis=1)
        return je_punkt[self.dreiecke].mean(axis=1)

    # ------------------------------------------------------------ sammeln

    def sammeln(self, karten):
        """Proben einer Kachel aus ihren Gruppenkarten: `{lage, normale, maske, hand, farbe (V, N, 3), kosinus (V, N), drin (V, N)}` — `N` die Texel aller Gruppen, `maske` (S, S) Bool, `index` (N, 2) die Texel (Zeile, Spalte)."""
        from scipy import ndimage

        s = karten[0]['maske'].shape[0]
        maske = np.zeros((s, s), dtype=bool)
        for k in karten:
            maske |= k['maske']
        zeilen, spalten = np.nonzero(maske)
        lage = np.zeros((len(zeilen), 3), dtype=np.float64)
        normale = np.zeros_like(lage)
        hand = np.zeros((s, s), dtype=bool)
        # je Gruppe die Texel an die richtigen Stellen der gemeinsamen Liste
        nummer = -np.ones((s, s), dtype=np.int64)
        nummer[zeilen, spalten] = np.arange(len(zeilen))
        for k in karten:
            m = k['maske']
            ziel = nummer[m]
            lage[ziel] = k['lage'][m]
            normale[ziel] = k['normale'][m]
            d = k['dreieck'][m]
            hand[m] = (d >= 0) & (self.hand_je_dreieck[np.clip(d, 0, len(self.hand_je_dreieck) - 1)] > self.HAND_AB)
        if hand.any():
            hand = ndimage.binary_dilation(hand, iterations=self.HAND_RAND_PX) & maske
        farben, kosinus, drin = [], [], []
        for a in self.projektion.ansichten:
            farbe, ist_drin = self.projektion._farbe_in(lage, a)                    # noqa: SLF001 — dieselbe Abbildung wie die Projektion selbst
            farben.append(farbe.astype(np.float32))
            kosinus.append(np.clip(normale @ self.projektion.blick(a['winkel']), 0.0, None).astype(np.float32))
            drin.append(ist_drin)
        return {'lage': lage, 'normale': normale, 'maske': maske, 'index': np.column_stack([zeilen, spalten]), 'hand': hand[zeilen, spalten],
                'farbe': np.asarray(farben), 'kosinus': np.asarray(kosinus), 'drin': np.asarray(drin)}

    # ------------------------------------------------------------ Licht

    def licht_schaetzen(self, proben):
        """Das Licht jeder Ansicht aus den Hautpunkten ALLER Kacheln (eine Liste von `sammeln`-Ergebnissen) zusammen schätzen (`Fotoprojektion.licht_schaetzen`, `Fotolicht`) — nur hautfarbene Punkte außerhalb der Hand
        zählen als Bezug. Ohne `projektion.licht` > 0 ohne Wirkung."""
        lage = np.vstack([p['lage'] for p in proben])
        normale = np.vstack([p['normale'] for p in proben])
        nicht_hand = ~np.concatenate([p['hand'] for p in proben])
        self.projektion.licht_schaetzen(lage, normale, lambda lin: Fotolicht.warm(lin) & nicht_hand)

    @staticmethod
    def _linear(c):
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def _srgb(c):
        c = np.clip(c, 0.0, 1.0)
        return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

    # ------------------------------------------------------------ Farbe

    def farbe(self, p):
        """`(farbe (N, 3) sRGB, deckung (N,), getroffen (N,) bool)` einer Kachel: das Mittel der Ansichten, vom Licht befreit (wo es geschätzt ist); Deckung 0 an der Hand."""
        n = len(p['lage'])
        summe = np.zeros((n, 3), dtype=np.float64)
        gewicht = np.zeros(n, dtype=np.float64)
        beste = np.zeros(n, dtype=np.float64)
        for i, a in enumerate(self.projektion.ansichten):
            farbe = self._linear(p['farbe'][i].astype(np.float64)) / self.projektion.licht_faktor(a, p['lage'], p['normale'])[:, None]
            gew = (p['kosinus'][i].astype(np.float64) ** self.AUSRICHTUNG) * p['drin'][i]
            summe += farbe * gew[:, None]
            gewicht += gew
            beste = np.maximum(beste, p['kosinus'][i] * p['drin'][i])
        getroffen = gewicht >= 1e-6
        farbe = self._srgb(np.where(getroffen[:, None], summe / np.maximum(gewicht, 1e-12)[:, None], 0.0))
        von, bis = self.DECKUNG
        deckung = np.clip((beste - von) / (bis - von), 0.0, 1.0) * getroffen * ~p['hand']
        return farbe.astype(np.float32), deckung.astype(np.float32), getroffen
