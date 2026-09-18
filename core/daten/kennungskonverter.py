# -*- coding: utf-8 -*-
"""Kennungskonverter — `<kennung:…>` in den URL-Mustern.

Nimmt nur die Form `JJJJ.MM.TT.hh.mm.ss` von `Auftragskennung` an. Eine UUID
passt nicht — die alten Adressen `/process/<uuid>/…` landen dadurch bei
`Auftragsweiterleitung`, nicht bei den Seiten.
"""

from .auftragskennung import Auftragskennung


class Kennungskonverter:
    regex = Auftragskennung.MUSTER

    @staticmethod
    def to_python(wert):
        return wert

    @staticmethod
    def to_url(wert):
        return str(wert)
