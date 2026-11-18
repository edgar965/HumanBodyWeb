# -*- coding: utf-8 -*-
u"""Hautkarteeinzug — `Hauteinzugrechnung.rechnen` (mit `Saumschnitt`, `Saumband`, `Hautdicke`) auf der Karte (18.11.2026, `Hautkarterechnung`).

Wie JS: die offenen Kanten aller deckenden Stücke als Strecken (je Stück in der Reihenfolge, in der die `Map` sie zuerst sah), ihre Mitten als float32
im Gitter (25 mm); die Randecken (verdeckt, an einem gezeichneten Dreieck); der Weg auf der Haut zur nächsten gezeichneten (`Hautkartewege`, bis
`BAND_M`); die Dicke je verdecktem Punkt bis `nachgeben / ANTEIL` (float32 wie dort); dann der Kern `einzug`. Konstanten aus `saumband.js`,
`saumschnitt.js`, `hautdicke.js`.
"""
import torch
import warp as wp

from . import hautkartewarpeinzug as kern
from .hautkartegitter import Hautkartegitter
from .hautkartewege import Hautkartewege

__all__ = ['Hautkarteeinzug']


def _a(t, typ):
    return wp.from_torch(t.contiguous(), dtype=typ)


class Hautkarteeinzug:
    BAND_M = 0.15
    STEIGUNG = 1.0
    TIEFE_M = 0.010
    SCHNAPP_M = 0.015
    UNTERKANTE_M = 0.001
    KANTENZELLE_M = 0.025
    ANTEIL = 0.4
    REICHWEITE_M = 0.025
    QUER_M = 0.002
    QUER_MAX_M = 0.0125
    DICKENZELLE_M = 0.025

    @staticmethod
    def kanten(stoffe):
        u"""(k, 6) float64: die offenen Kanten aller Stücke wie `Saumschnitt.kanten` (Float32Array dort — die Punkte sind float32)."""
        teile = []
        for s in stoffe:
            S, ST = s['punkte'], s['dreiecke']
            if not len(S) or not len(ST):
                continue
            n = len(S)
            einzeln, zahl, stelle = Hautkartegitter.kanten(ST, n)
            rand = einzeln[zahl == 1]
            rand = rand.index_select(0, torch.argsort(stelle[zahl == 1]))
            a, b = rand // n, rand % n
            teile.append(torch.cat([S.index_select(0, a), S.index_select(0, b)], 1))
        if not teile:
            return None
        return torch.cat(teile)

    @classmethod
    def rechnen(cls, K, N, KT, maske, stoffe, nachgeben):
        u"""`{werte (n, 3) float32, gesetzt, geschnappt, band, weg (n,) uint8}` — Zahlen als Tensoren (eine Abholung mit der Antwort)."""
        n, g = len(K), K.device
        strom = wp.stream_from_torch(torch.cuda.current_stream(g))
        verdeckt = maske != 0
        kanten = cls.kanten(stoffe)
        mit_kanten = kanten is not None and len(kanten) > 0
        if mit_kanten:
            mitten = (0.5 * (kanten[:, :3] + kanten[:, 3:])).to(torch.float32).to(torch.float64)
            mg = Hautkartegitter(mitten, cls.KANTENZELLE_M)
        else:
            kanten = torch.zeros((1, 6), dtype=torch.float64, device=g)
            mg = Hautkartegitter(torch.zeros((1, 3), dtype=torch.float64, device=g), cls.KANTENZELLE_M)
        t = KT.reshape(-1, 3)
        m = maske.to(torch.int64)
        summe = m.index_select(0, t[:, 0]) + m.index_select(0, t[:, 1]) + m.index_select(0, t[:, 2])
        gemischt = (summe > 0) & (summe < 3)
        ecken = torch.zeros(n, dtype=torch.uint8, device=g)
        ecke = t[gemischt].reshape(-1)
        ecken[ecke[maske.index_select(0, ecke) != 0]] = 1
        abstaende = Hautkartewege.wege(K, KT, ~verdeckt, cls.BAND_M)
        reich32 = torch.where(verdeckt & (nachgeben > 0), (nachgeben.to(torch.float64) / cls.ANTEIL).to(torch.float32), torch.zeros_like(nachgeben))
        weite = torch.clamp(reich32.to(torch.float64), min=cls.REICHWEITE_M)
        dg = Hautkartegitter(K, cls.DICKENZELLE_M)
        dicken = torch.full((n,), float('inf'), dtype=torch.float32, device=g)
        wp.launch(kern.dicke, dim=n, inputs=[_a(K, wp.float64), _a(N, wp.float64), _a(dg.schl, wp.int64), _a(dg.folge, wp.int64), cls.DICKENZELLE_M,
                                             _a(maske, wp.uint8), _a(weite, wp.float64), cls.QUER_M, cls.QUER_MAX_M, _a(dicken, wp.float32)], stream=strom)
        werte = torch.zeros((n, 3), dtype=torch.float32, device=g)
        geschnappt = torch.zeros(n, dtype=torch.uint8, device=g)
        anteil = torch.full((1,), cls.ANTEIL, dtype=torch.float64, device=g)
        wp.launch(kern.einzug, dim=n, inputs=[_a(K, wp.float64), _a(N, wp.float64), _a(maske, wp.uint8), _a(ecken, wp.uint8), _a(kanten, wp.float64),
                                              _a(mg.schl, wp.int64), _a(mg.folge, wp.int64), cls.KANTENZELLE_M, int(mit_kanten),
                                              cls.SCHNAPP_M * cls.SCHNAPP_M, cls.UNTERKANTE_M, _a(abstaende, wp.float64), _a(nachgeben, wp.float32),
                                              cls.TIEFE_M, cls.STEIGUNG, _a(dicken, wp.float32), _a(anteil, wp.float64), _a(werte, wp.float32),
                                              _a(geschnappt, wp.uint8)], stream=strom)
        im_band = abstaende <= cls.BAND_M
        return {'werte': werte, 'gesetzt': verdeckt.sum(), 'geschnappt': (geschnappt != 0).sum(), 'band': (verdeckt & im_band).sum(),
                'weg': (verdeckt & ~im_band).to(torch.uint8)}
