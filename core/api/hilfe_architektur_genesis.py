# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Genesis: ein Blender-Modell als Genesis-9-Figur mit eigenen Bibliotheksstücken.

Edgar (08.10.2026): „schreibe das hinein in eine neue Seite Hilfe - Architektur - Genesis" — das Konzept zum Import
von `cute girl` (`Docu/konzepte/2026-10-08_blend-import-als-genesis-figur-konzept.md`). Die Bausteine, auf die es
aufsetzt, kommen aus `core.dienste.architekturgenesis` und werden beim Aufruf gegen den Code geprüft.
"""

from ..dienste.architekturgenesis import Architekturgenesis
from .hilfeseite import Hilfeseite


class HilfeArchitekturGenesis(Hilfeseite):
    template_name = 'hilfe/architektur_genesis.html'
    AKTIV = 'hilfe_architektur_genesis'

    def kontext(self):
        return Architekturgenesis.kontext()
