# -*- coding: utf-8 -*-
"""Hautkontext — der Schattierungszustand (`ShaderData` in Cycles) für einen Stapel von Treffern: Dreieck, Schwerpunkt, Normalen, Ableitungen, UV und Farbattribute.

Alles wird beim ersten Zugriff gerechnet und für den Stapel gemerkt. Konstanten (feste Buchsenwerte) teilen sich ein Feld je Wert. Felder als torch-Tensoren auf der Karte,
die Kerne in `hautbackenkerne_cu/hautkontextkern.cuh` (`Hautbackenkernbau`; bis 21.11.2026 Warp in `hautkontextkernel.py`).
"""

import torch

from ..hautbackenkernbau import Hautbackenkernbau
from .hautumwandlung import Hautumwandlung

__all__ = ['Hautkontext']


class Hautkontext:
    def __init__(self, schattung, face, hu, hv, dp, geraet='cuda:0'):
        """`face`, `hu`, `hv`: der Treffer je Stapeleintrag (Dreieck des Körpers und die Gewichte der Ecken 1 und 2); `dp`: die gepackte Pixel-Ableitung (`differenzial`)."""
        self.s, self.geraet = schattung, torch.device(geraet)
        self.face, self.hu, self.hv, self.dp = face, hu, hv, dp
        self.n = len(face)
        self._merk = {}

    def _neu(self, breite=0, dtype=torch.float32):
        return torch.zeros((self.n, breite) if breite else (self.n,), dtype=dtype, device=self.geraet)

    def _rufen(self, name, *args):
        with torch.cuda.device(self.geraet):
            Hautbackenkernbau.rufen(name, *args)

    def konstante(self, art, wert):
        """Das Feld für einen festen Wert (`art` f/c/v), je Stapel einmal."""
        schluessel = ('k', art, wert if art == 'f' else tuple(wert))
        if schluessel not in self._merk:
            self._merk[schluessel] = Hautumwandlung.konstante(art, wert, self.n, self.geraet)
        return self._merk[schluessel]

    # ------------------------------------------------------------------ Geometrie

    def geometrie(self):
        """`(Ng, N, dPdu, dPdv, rueckseite)` am Treffer."""
        if 'geo' not in self._merk:
            s = self.s
            ng, n, dpdu, dpdv = (self._neu(3) for _ in range(4))
            rueck = self._neu(dtype=torch.int32)
            self._rufen('hb_geometrie', self.n, self.face, self.hu, self.hv, s.tri, s.pos, s.ecke_n, s.glatt, ng, n, dpdu, dpdv, rueck)
            self._merk['geo'] = (ng, n, dpdu, dpdv, rueck)
        return self._merk['geo']

    def differenziale(self):
        """`(dP.dx, dP.dy, du.dx, dv.dx, du.dy, dv.dy)` — `differential_from_compact` und `differential_dudv`."""
        if 'diff' not in self._merk:
            ng, _n, dpdu, dpdv, _r = self.geometrie()
            dpx, dpy = self._neu(3), self._neu(3)
            dudx, dvdx, dudy, dvdy = (self._neu() for _ in range(4))
            self._rufen('hb_differenzial_uv', self.n, ng, dpdu, dpdv, self.dp, dpx, dpy, dudx, dvdx, dudy, dvdy)
            self._merk['diff'] = (dpx, dpy, dudx, dvdx, dudy, dvdy)
        return self._merk['diff']

    # ------------------------------------------------------------------ Attribute

    def uv(self, name):
        """`(Wert, dx, dy)` der UV-Karte als (n, 2)-Felder; None, wenn das Netz die Karte nicht hat."""
        schluessel = ('uv', name)
        if schluessel not in self._merk:
            karte = self.s.uv(name)
            if karte is None:
                self._merk[schluessel] = None
            else:
                _dpx, _dpy, dudx, dvdx, dudy, dvdy = self.differenziale()
                val, dx, dy = (self._neu(2) for _ in range(3))
                self._rufen('hb_attribut2', self.n, self.face, self.hu, self.hv, karte[0], dudx, dvdx, dudy, dvdy, val, dx, dy)
                self._merk[schluessel] = (val, dx, dy)
        return self._merk[schluessel]

    def farbattribut(self, name):
        """`(Wert, dx, dy)` des Farbattributs als (n, 4)-Felder (linear); None, wenn das Netz es nicht hat."""
        schluessel = ('farbe', name)
        if schluessel not in self._merk:
            feld = self.s.farbe(name)
            if feld is None:
                self._merk[schluessel] = None
            else:
                _dpx, _dpy, dudx, dvdx, dudy, dvdy = self.differenziale()
                val, dx, dy = (self._neu(4) for _ in range(3))
                self._rufen('hb_attribut4', self.n, self.face, self.hu, self.hv, feld, dudx, dvdx, dudy, dvdy, val, dx, dy)
                self._merk[schluessel] = (val, dx, dy)
        return self._merk[schluessel]

    def tangente(self, uv_name):
        """`(Tangente, Vorzeichen)` am Treffer für die UV-Karte (Normal-Map-Knoten); None, wenn es keine Karte gibt."""
        schluessel = ('tang', uv_name)
        if schluessel not in self._merk:
            t = self.s.tangenten(uv_name)
            if t is None:
                self._merk[schluessel] = None
            else:
                tang, vorz = self._neu(3), self._neu()
                self._rufen('hb_tangente_interpoliert', self.n, self.face, self.hu, self.hv, t[0], t[1], tang, vorz)
                self._merk[schluessel] = (tang, vorz)
        return self._merk[schluessel]

    def normale_geglaettet(self):
        """Die Normale für den Normal-Map-Knoten, Basis „Displaced" (`triangle_smooth_normal_unnormalized_object_space`, normiert) — nur für glatte Dreiecke gültig."""
        if 'nglatt' not in self._merk:
            ng = self.geometrie()[0]
            aus = self._neu(3)
            self._rufen('hb_normale_unnormiert', self.n, self.face, self.hu, self.hv, self.s.ecke_n, self.s.glatt, ng, aus)
            self._merk['nglatt'] = aus
        return self._merk['nglatt']

    def glatt(self):
        """1, wenn das getroffene Dreieck glatt schattiert ist (`SHADER_SMOOTH_NORMAL`), sonst 0."""
        if 'glatt' not in self._merk:
            aus = self._neu(dtype=torch.int32)
            self._rufen('hb_glatt_je_treffer', self.n, self.face, self.s.glatt, aus)
            self._merk['glatt'] = aus
        return self._merk['glatt']
