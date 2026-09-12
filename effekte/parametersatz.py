# -*- coding: utf-8 -*-
u"""Parametersatz — Felder, Vorgaben, Grenzen und Kommandozeile EINER Pipeline.

Herausgeloest aus `Effektparameter` (12.09.2026), als die zweite Pipeline
kam (`Figurparameter`: HumanBody-Figur mit DEF-Skelett). Beide brauchen
dasselbe: eine Feldliste, die Karte, Django-Befehl und Unterprozess
gemeinsam lesen (Regel `JederParameterWirkt`), Grenzen beim Anlegen,
`argumente()` fuer den Aufruf und `aus_argv()` fuer die Gegenseite.

Eine Unterklasse nennt:
    FELDER   (name, typ, vorgabe, minimum, maximum, beschriftung, hinweis)
    PFLICHT  Namen der Pflichtargumente (Pfade), in Aufrufreihenfolge
    WAHLEN   {name: (vorgabe, zulaessige Werte)} — Auswahlfelder
    PROG     Name fuers Hilfe-Banner
"""
from __future__ import print_function

import argparse

__all__ = ['Parametersatz']


class Parametersatz:

    FELDER = ()
    PFLICHT = ()
    WAHLEN = {}
    PROG = 'pipeline'

    def __init__(self, **werte):
        for name in self.PFLICHT:
            if name not in werte:
                raise TypeError('%s fehlt' % name)
            setattr(self, name, werte.pop(name))
        for name, (vorgabe, zulaessig) in self.WAHLEN.items():
            wert = werte.pop(name, vorgabe)
            if wert not in zulaessig:
                raise ValueError('%s: %r' % (name, wert))
            setattr(self, name, wert)
        for name, typ, vorgabe, kleinst, groesst, _b, _h in self.FELDER:
            wert = werte.pop(name, vorgabe)
            if wert is None:
                wert = vorgabe
            if typ is bool:
                setattr(self, name, self.wahr(wert))
            else:
                setattr(self, name, min(max(typ(wert), kleinst), groesst))
        if werte:
            raise ValueError('Unbekannte Parameter: %s' % sorted(werte))

    @staticmethod
    def wahr(wert):
        u"""Schalter aus JSON (`true`), Formular (`on`) oder Argument (`1`)."""
        if isinstance(wert, str):
            return wert.strip().lower() in ('1', 'true', 'on', 'ja', 'yes')
        return bool(wert)

    @classmethod
    def vorgaben(cls):
        return {name: vorgabe for name, _t, vorgabe, _k, _g, _b, _h in cls.FELDER}

    @classmethod
    def namen(cls):
        return [name for name, _t, _v, _k, _g, _b, _h in cls.FELDER]

    @classmethod
    def karte(cls):
        u"""Die Felder fuer das Formular — je Feld ein Woerterbuch."""
        return [{'name': name, 'typ': typ.__name__,
                 'vorgabe': vorgabe, 'min': kleinst, 'max': groesst,
                 'schritt': cls.schritt(typ, vorgabe, kleinst, groesst),
                 'beschriftung': beschriftung, 'hinweis': hinweis}
                for name, typ, vorgabe, kleinst, groesst, beschriftung, hinweis
                in cls.FELDER]

    #: Schrittweiten, die ein Schieberegler anbieten darf — grob nach fein.
    SCHRITTE = (100, 50, 20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.001)

    @classmethod
    def schritt(cls, typ, vorgabe, kleinst, groesst):
        u"""Die Schrittweite eines Felds als Text fuers `step`-Attribut.

        Ein Schieberegler (Edgar, 12.09.2026: „mach für alle Einstellungen
        slider") rastet von `min` aus in Schritten ein: Mit pauschal 0,5 waere
        Boeen 0,3 oder Stoffgewicht 0,2 gar nicht einstellbar, und Dehnsteifig-
        keit (min 0,05) traefe die Vorgabe 1,0 nie. Darum die groebste Stufe,
        die mindestens ~200 Rasten ergibt UND Vorgabe wie Minimum trifft.
        """
        if typ is not float:
            return '1'
        spanne = float(groesst) - float(kleinst)
        for stufe in cls.SCHRITTE:
            if spanne / stufe < 200:
                continue
            passt = all(abs(w / stufe - round(w / stufe)) < 1e-6
                        for w in (float(vorgabe), float(kleinst)))
            if passt:
                return ('%g' % stufe)
        return '0.001'

    # ---------------------------------------------------------- Kommandozeile

    def argumente(self):
        u"""`--name wert` fuer Pflicht, Wahlen und Felder — in dieser Reihenfolge."""
        arg = []
        for name in list(self.PFLICHT) + list(self.WAHLEN):
            arg += ['--' + name, str(getattr(self, name))]
        for name in self.namen():
            wert = getattr(self, name)
            arg += ['--' + name, str(int(wert)) if isinstance(wert, bool) else str(wert)]
        return arg

    @classmethod
    def parser(cls):
        p = argparse.ArgumentParser(prog=cls.PROG)
        for name in cls.PFLICHT:
            p.add_argument('--' + name, required=True)
        for name, (vorgabe, zulaessig) in cls.WAHLEN.items():
            p.add_argument('--' + name, default=vorgabe, choices=list(zulaessig))
        for name, typ, vorgabe, _k, _g, _b, hinweis in cls.FELDER:
            p.add_argument('--' + name, type=cls.wahr if typ is bool else typ,
                           default=vorgabe, help=hinweis)
        return p

    @classmethod
    def aus_argv(cls, argv):
        u"""Die Argumente hinter `--` (Blender behaelt alles davor)."""
        rest = argv[argv.index('--') + 1:] if '--' in argv else argv
        ns = cls.parser().parse_args(rest)
        return cls(**vars(ns))
