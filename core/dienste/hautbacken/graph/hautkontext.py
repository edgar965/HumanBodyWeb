# -*- coding: utf-8 -*-
"""Hautkontext — der Schattierungszustand (`ShaderData` in Cycles) für einen Stapel von Treffern: Dreieck, Schwerpunkt, Normalen, Ableitungen, UV und Farbattribute.

Alles wird beim ersten Zugriff gerechnet und für den Stapel gemerkt. Konstanten (feste Buchsenwerte) teilen sich ein Feld je Wert.
"""

import warp as wp

from . import hautkontextkernel as kern
from .hautumwandlung import Hautumwandlung

__all__ = ['Hautkontext']


class Hautkontext:
    def __init__(self, schattung, face, hu, hv, dp, geraet='cuda:0'):
        """`face`, `hu`, `hv`: der Treffer je Stapeleintrag (Dreieck des Körpers und die Gewichte der Ecken 1 und 2); `dp`: die gepackte Pixel-Ableitung (`differenzial`)."""
        self.s, self.geraet = schattung, geraet
        self.face, self.hu, self.hv, self.dp = face, hu, hv, dp
        self.n = len(face)
        self._merk = {}

    def _neu(self, dtype):
        return wp.zeros(self.n, dtype=dtype, device=self.geraet)

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
            ng, n, dpdu, dpdv = (self._neu(wp.vec3) for _ in range(4))
            rueck = self._neu(wp.int32)
            wp.launch(kern.geometrie, dim=self.n, inputs=[self.face, self.hu, self.hv, s.tri, s.pos, s.ecke_n, s.glatt, ng, n, dpdu, dpdv, rueck], device=self.geraet)
            self._merk['geo'] = (ng, n, dpdu, dpdv, rueck)
        return self._merk['geo']

    def differenziale(self):
        """`(dP.dx, dP.dy, du.dx, dv.dx, du.dy, dv.dy)` — `differential_from_compact` und `differential_dudv`."""
        if 'diff' not in self._merk:
            ng, _n, dpdu, dpdv, _r = self.geometrie()
            dpx, dpy = self._neu(wp.vec3), self._neu(wp.vec3)
            dudx, dvdx, dudy, dvdy = (self._neu(wp.float32) for _ in range(4))
            wp.launch(kern.differenzial_uv, dim=self.n, inputs=[ng, dpdu, dpdv, self.dp, dpx, dpy, dudx, dvdx, dudy, dvdy], device=self.geraet)
            self._merk['diff'] = (dpx, dpy, dudx, dvdx, dudy, dvdy)
        return self._merk['diff']

    # ------------------------------------------------------------------ Attribute

    def uv(self, name):
        """`(Wert, dx, dy)` der UV-Karte als vec2-Felder; None, wenn das Netz die Karte nicht hat."""
        schluessel = ('uv', name)
        if schluessel not in self._merk:
            karte = self.s.uv(name)
            if karte is None:
                self._merk[schluessel] = None
            else:
                _dpx, _dpy, dudx, dvdx, dudy, dvdy = self.differenziale()
                val, dx, dy = (self._neu(wp.vec2) for _ in range(3))
                wp.launch(kern.attribut2, dim=self.n, inputs=[self.face, self.hu, self.hv, karte[0], dudx, dvdx, dudy, dvdy, val, dx, dy], device=self.geraet)
                self._merk[schluessel] = (val, dx, dy)
        return self._merk[schluessel]

    def farbattribut(self, name):
        """`(Wert, dx, dy)` des Farbattributs als vec4-Felder (linear); None, wenn das Netz es nicht hat."""
        schluessel = ('farbe', name)
        if schluessel not in self._merk:
            feld = self.s.farbe(name)
            if feld is None:
                self._merk[schluessel] = None
            else:
                _dpx, _dpy, dudx, dvdx, dudy, dvdy = self.differenziale()
                val, dx, dy = (self._neu(wp.vec4) for _ in range(3))
                wp.launch(kern.attribut4, dim=self.n, inputs=[self.face, self.hu, self.hv, feld, dudx, dvdx, dudy, dvdy, val, dx, dy], device=self.geraet)
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
                tang, vorz = self._neu(wp.vec3), self._neu(wp.float32)
                wp.launch(kern.tangente_interpoliert, dim=self.n, inputs=[self.face, self.hu, self.hv, t[0], t[1], tang, vorz], device=self.geraet)
                self._merk[schluessel] = (tang, vorz)
        return self._merk[schluessel]

    def normale_geglaettet(self):
        """Die Normale für den Normal-Map-Knoten, Basis „Displaced" (`triangle_smooth_normal_unnormalized_object_space`, normiert) — nur für glatte Dreiecke gültig."""
        if 'nglatt' not in self._merk:
            ng = self.geometrie()[0]
            aus = self._neu(wp.vec3)
            wp.launch(kern.normale_unnormiert, dim=self.n, inputs=[self.face, self.hu, self.hv, self.s.ecke_n, self.s.glatt, ng, aus], device=self.geraet)
            self._merk['nglatt'] = aus
        return self._merk['nglatt']

    def normale_roh(self):
        """Die Eckennormalen linear gemischt, nicht normiert (Normal-Map-Knoten, Basis „Original")."""
        if 'nroh' not in self._merk:
            aus = self._neu(wp.vec3)
            wp.launch(kern.normale_roh, dim=self.n, inputs=[self.face, self.hu, self.hv, self.s.ecke_n, aus], device=self.geraet)
            self._merk['nroh'] = aus
        return self._merk['nroh']

    def glatt(self):
        """1, wenn das getroffene Dreieck glatt schattiert ist (`SHADER_SMOOTH_NORMAL`), sonst 0."""
        if 'glatt' not in self._merk:
            aus = self._neu(wp.int32)
            wp.launch(kern.glatt_je_treffer, dim=self.n, inputs=[self.face, self.s.glatt, aus], device=self.geraet)
            self._merk['glatt'] = aus
        return self._merk['glatt']
