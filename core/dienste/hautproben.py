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

import torch
from KoerperKI_alle.torchfeld import Torchfeld

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
        self.dreiecke = Torchfeld.feld(dreiecke, dtype=torch.int64).reshape(-1, 3)
        self.hand_je_dreieck = self._hand(haut)

    def _hand(self, haut):
        """Hautgewicht auf den Handknochen je Dreieck (T,) — Null ohne solche Knochen."""
        namen = [str(n) for n in (haut or {}).get('knochen') or []]
        ziele = [i for i, n in enumerate(namen) if self.HAND.match(n)]
        if not ziele:
            return torch.zeros(len(self.dreiecke), dtype=torch.float64, device='cuda')
        index = Torchfeld.feld(haut['index']).reshape(-1, 4)
        gewicht = Torchfeld.feld(haut['gewicht'], dtype=torch.float64).reshape(-1, 4)
        je_punkt = (gewicht * torch.isin(index, Torchfeld.feld(ziele))).sum(axis=1)
        return je_punkt[self.dreiecke].mean(axis=1)

    # ------------------------------------------------------------ sammeln

    def sammeln(self, karten):
        """Proben einer Kachel aus ihren Gruppenkarten: `{lage, normale, maske, hand, farbe (V, N, 3), kosinus (V, N), drin (V, N)}` — `N` die Texel aller Gruppen, `maske` (S, S) Bool, `index` (N, 2) die Texel (Zeile, Spalte)."""
        from KoerperKI_alle.kartenbild import Kartenbild as ndimage

        s = karten[0]['maske'].shape[0]
        maske = torch.zeros((s, s), dtype=torch.bool, device='cuda')
        for k in karten:
            maske |= k['maske']
        zeilen, spalten = torch.nonzero(maske, as_tuple=True)
        lage = torch.zeros((len(zeilen), 3), dtype=torch.float64, device='cuda')
        normale = torch.zeros_like(lage)
        hand = torch.zeros((s, s), dtype=torch.bool, device='cuda')
        # je Gruppe die Texel an die richtigen Stellen der gemeinsamen Liste
        nummer = -torch.ones((s, s), dtype=torch.int64, device='cuda')
        nummer[zeilen, spalten] = Torchfeld.arange(len(zeilen))
        for k in karten:
            m = k['maske']
            ziel = nummer[m]
            lage[ziel] = k['lage'][m]
            normale[ziel] = k['normale'][m]
            d = k['dreieck'][m]
            hand[m] = (d >= 0) & (self.hand_je_dreieck[Torchfeld.clip(d, 0, len(self.hand_je_dreieck) - 1)] > self.HAND_AB)
        if hand.any():
            hand = ndimage.binary_dilation(hand, iterations=self.HAND_RAND_PX) & maske
        farben, kosinus, drin = [], [], []
        for a in self.projektion.ansichten:
            farbe, ist_drin = self.projektion._farbe_in(lage, a)                    # noqa: SLF001 — dieselbe Abbildung wie die Projektion selbst
            farben.append(Torchfeld.astype(farbe, torch.float32))
            kosinus.append(Torchfeld.astype(Torchfeld.clip(normale @ self.projektion.blick(a['winkel']), 0.0, None), torch.float32))
            drin.append(ist_drin)
        return {'lage': lage, 'normale': normale, 'maske': maske, 'index': Torchfeld.column_stack([zeilen, spalten]), 'hand': hand[zeilen, spalten],
                'farbe': Torchfeld.feld(farben), 'kosinus': Torchfeld.feld(kosinus), 'drin': Torchfeld.feld(drin)}

    # ------------------------------------------------------------ Licht

    def licht_schaetzen(self, proben):
        """Das Licht jeder Ansicht aus den Hautpunkten ALLER Kacheln (eine Liste von `sammeln`-Ergebnissen) zusammen schätzen (`Fotoprojektion.licht_schaetzen`, `Fotolicht`) — nur hautfarbene Punkte außerhalb der Hand
        zählen als Bezug. Ohne `projektion.licht` > 0 ohne Wirkung."""
        lage = Torchfeld.vstack([p['lage'] for p in proben])
        normale = Torchfeld.vstack([p['normale'] for p in proben])
        nicht_hand = ~Torchfeld.cat([p['hand'] for p in proben])
        self.projektion.licht_schaetzen(lage, normale, lambda lin: Fotolicht.warm(lin) & nicht_hand)

    @staticmethod
    def _linear(c):
        return torch.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def _srgb(c):
        c = Torchfeld.clip(c, 0.0, 1.0)
        return torch.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

    # ------------------------------------------------------------ Farbe

    def summen(self, p):
        """`(summe (N, 3) linear, gewicht (N,), beste (N,))` der Ansichten dieser Proben — Zwischenstand von `farbe`; `Hautprobenmehrpose` legt die Summen mehrerer Proben (je Ansicht eine Haltung) zusammen."""
        n = len(p['lage'])
        summe = torch.zeros((n, 3), dtype=torch.float64, device='cuda')
        gewicht = torch.zeros(n, dtype=torch.float64, device='cuda')
        beste = torch.zeros(n, dtype=torch.float64, device='cuda')
        for i, a in enumerate(self.projektion.ansichten):
            farbe = self._linear(Torchfeld.astype(p['farbe'][i], torch.float64)) / self.projektion.licht_faktor(a, p['lage'], p['normale'])[:, None]
            gew = (Torchfeld.astype(p['kosinus'][i], torch.float64) ** self.AUSRICHTUNG) * p['drin'][i]
            summe += farbe * gew[:, None]
            gewicht += gew
            beste = Torchfeld.maximum(beste, p['kosinus'][i] * p['drin'][i])
        return summe, gewicht, beste

    @classmethod
    def abschluss(cls, summe, gewicht, beste, hand):
        """`(farbe (N, 3) sRGB, deckung (N,), getroffen (N,) bool)` aus den Summen; Deckung 0 an der Hand (`hand` (N,) bool)."""
        getroffen = gewicht >= 1e-6
        farbe = cls._srgb(torch.where(getroffen[:, None], summe / Torchfeld.maximum(gewicht, 1e-12)[:, None], 0.0))
        von, bis = cls.DECKUNG
        deckung = Torchfeld.clip((beste - von) / (bis - von), 0.0, 1.0) * getroffen * ~hand
        return Torchfeld.astype(farbe, torch.float32), Torchfeld.astype(deckung, torch.float32), getroffen

    def farbe(self, p):
        """`(farbe (N, 3) sRGB, deckung (N,), getroffen (N,) bool)` einer Kachel: das Mittel der Ansichten, vom Licht befreit (wo es geschätzt ist); Deckung 0 an der Hand."""
        return self.abschluss(*self.summen(p), p['hand'])
