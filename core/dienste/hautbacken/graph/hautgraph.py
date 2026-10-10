# -*- coding: utf-8 -*-
"""Hautgraph — der Knotengraph eines Materials (Export `blendmaterialgraph.py`) und seine Auswertung für einen Stapel Texel auf der GPU.

    graph = Hautgraph('Std_Skin_Body', spec, geraet='cuda:0', texturen={})
    werte = graph.auswerten(ctx)          # {'farbe': Hautwert c (linear) | None, 'rauheit': Hautwert f | None, 'normal': Hautwert v | None}

Beim Anlegen wird der ganze Graph geprüft: ein Knotentyp, eine Einstellung oder ein Bild, das der lokale Backer nicht kennt, ist ein `Hautgraphfehler` mit allen Befunden — nichts
fällt still auf eine Näherung zurück. Die Auswertung folgt den Verbindungen von den Zielen (Base Color, Roughness, Normal des Principled BSDF) rückwärts; jeder Knoten rechnet je Stapel
und Modus einmal (`ctx` merkt sich die Ergebnisse). Modus `(0, 0)` ist die Mitte, `(1|2, Breite)` der Bump-Versatz in dx/dy — nur Knoten, die (über ihre Eingänge) Koordinaten lesen,
rechnen ihn gesondert.
"""

import warp as wp

from .hautgraphfehler import Hautgraphfehler
from .hautumwandlung import Hautumwandlung
from .hautwert import Hautwert
from .hauttextur import Hauttextur
from .knoten.hautknotenfabrik import Hautknotenfabrik
from .knoten.hautknotenkoordinate import _uv_koordinate

__all__ = ['Hautgraph']

#: Buchsenart des Exports → Art des Auswerters (Ganzzahlen und Schalter rechnen als Zahl, Drehungen als Vektor).
ART = {'f': 'f', 'c': 'c', 'v': 'v', 'i': 'f', 'b': 'f', 'r': 'v'}
MITTE = (0, 0.0)


class Hautgraph:
    def __init__(self, name, spec, geraet='cuda:0', texturen=None):
        """`spec`: der Graph aus dem Export (JSON). `texturen`: gemeinsamer Speicher `{(datei, farbraum, alpha_modus): Hauttextur}` — Materialien teilen sich Bilder."""
        self.name, self.spec, self.geraet = name, spec, geraet
        self._texturen = texturen if texturen is not None else {}
        self.knoten = {}
        gruende = []
        for schluessel, eintrag in spec['knoten'].items():
            if not Hautknotenfabrik.bekannt(eintrag['typ']):
                gruende.append('Knoten „%s" (Typ %s) ist nicht übernommen' % (schluessel, eintrag['typ']))
            else:
                self.knoten[schluessel] = Hautknotenfabrik.bauen(schluessel, eintrag)
        self._genutzt = self._ausgaenge()
        for schluessel, knoten in self.knoten.items():
            gruende += ['Knoten „%s": %s' % (schluessel, g) for g in knoten.pruefen(self._genutzt.get(schluessel, set()))]
            if knoten.typ == 'TEX_IMAGE' and knoten.eig.get('bild') in spec['bilder']:
                grund = Hauttextur.pruefen(knoten.eig['bild'], spec['bilder'][knoten.eig['bild']])
                if grund:
                    gruende.append(grund)
        for ziel, q in spec['ziel'].items():
            if 'von' in q and q['von'][0] not in self.knoten and q['von'][0] in spec['knoten']:
                gruende.append('Ziel „%s" hängt an einem nicht übernommenen Knoten' % ziel)
        if gruende:
            raise Hautgraphfehler(['Material „%s": %s' % (name, g) for g in gruende])
        self._abhaengig = {}

    # ------------------------------------------------------------------ Analyse

    def _ausgaenge(self):
        """`{Knoten: {gelesene Ausgänge}}`."""
        aus = {}
        for q in self.spec['ziel'].values():
            if 'von' in q:
                aus.setdefault(q['von'][0], set()).add(q['von'][1])
        for eintrag in self.spec['knoten'].values():
            for q in eintrag['ein'].values():
                if 'von' in q:
                    aus.setdefault(q['von'][0], set()).add(q['von'][1])
        return aus

    def genutzt(self, schluessel):
        return self._genutzt.get(schluessel, set())

    def abhaengig(self, schluessel):
        """Liest der Knoten (über seine Eingänge) Koordinaten oder Attribute?"""
        if schluessel not in self._abhaengig:
            self._abhaengig[schluessel] = False                           # gegen Kreise
            knoten = self.knoten[schluessel]
            ergebnis = bool(knoten.KOORDINATE) or any('von' in q and self.abhaengig(q['von'][0]) for q in knoten.eintrag['ein'].values())
            self._abhaengig[schluessel] = ergebnis
        return self._abhaengig[schluessel]

    def textur(self, name):
        eintrag = self.spec['bilder'][name]
        schluessel = (eintrag['datei'], eintrag['farbraum'], eintrag['alpha_modus'])
        if schluessel not in self._texturen:
            self._texturen[schluessel] = Hauttextur(name, eintrag, self.geraet)
        return self._texturen[schluessel]

    # ------------------------------------------------------------------ Auswertung

    def standard_uv(self, ctx, modus):
        """Die Standard-UV als Punkt — was Cycles' eingefügter „Texture Coordinate"-Knoten an einem unverbundenen Vektor liefert."""
        schluessel = ('stduv', modus)
        if schluessel not in ctx._merk:
            uv = ctx.uv('')
            if uv is None:
                ctx._merk[schluessel] = ctx.konstante('v', (0.0, 0.0, 0.0))
            else:
                aus = Hautwert.leer('v', ctx.n, self.geraet)
                wp.launch(_uv_koordinate, dim=ctx.n, inputs=[uv[0], uv[1], uv[2], modus[0], float(modus[1]), aus.daten], device=self.geraet)
                ctx._merk[schluessel] = aus
        return ctx._merk[schluessel]

    def ausgang(self, schluessel, ausgang, ctx, modus):
        knoten = self.knoten[schluessel]
        m = modus if self.abhaengig(schluessel) else MITTE
        merk = ('n', self.name, schluessel, m)
        if merk not in ctx._merk:
            ctx._merk[merk] = None                                        # in Arbeit (Kreisschutz)
            ctx._merk[merk] = knoten.auswerten(self, ctx, m)
        ergebnis = ctx._merk[merk]
        if ergebnis is None:
            raise Hautgraphfehler('Material „%s": der Graph enthält einen Kreis bei Knoten „%s"' % (self.name, schluessel))
        if ausgang not in ergebnis:
            raise Hautgraphfehler('Material „%s": Knoten „%s" (%s) hat keinen Ausgang „%s"' % (self.name, schluessel, knoten.typ, ausgang))
        return ergebnis[ausgang]

    def quelle(self, q, ctx, modus, art):
        """Der Wert einer Quelle (Verbindung oder fester Wert) als Art `art`."""
        if 'von' in q:
            wert = self.ausgang(q['von'][0], q['von'][1], ctx, modus)
        else:
            if q['wert'] is None:
                raise Hautgraphfehler('Material „%s": eine Buchse ohne Wert (Art %s)' % (self.name, q['art']))
            kind = ART.get(q['art'], 'f')
            wert = ctx.konstante(kind, q['wert'] if kind == 'f' else tuple(q['wert']))
        return Hautumwandlung.nach(wert, art, self.geraet)

    def eingang(self, knoten, name, ctx, modus, art):
        if name not in knoten.eintrag['ein']:
            raise Hautgraphfehler('Material „%s": Knoten „%s" (%s) hat keine Buchse „%s"' % (self.name, knoten.schluessel, knoten.typ, name))
        return self.quelle(knoten.eintrag['ein'][name], ctx, modus, art)

    def auswerten(self, ctx, kanaele=('farbe', 'rauheit', 'normal')):
        """Die Kanäle des Principled BSDF für den Stapel: Farbe (linear, `c`), Rauheit (`f`), Normale (`v`; None, wenn der Normal-Eingang nicht verbunden ist)."""
        aus = {}
        ziel = self.spec['ziel']
        if 'farbe' in kanaele:
            aus['farbe'] = self.quelle(ziel['farbe'], ctx, MITTE, 'c')
        if 'rauheit' in kanaele:
            aus['rauheit'] = self.quelle(ziel['rauheit'], ctx, MITTE, 'f')
        if 'normal' in kanaele:
            aus['normal'] = self.quelle(ziel['normal'], ctx, MITTE, 'v') if 'von' in ziel['normal'] else None
        return aus
