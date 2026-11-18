# -*- coding: utf-8 -*-
u"""Meshgenesissuchpfad — `meshgenesis/` (Rechencode der Mesh-Genesis-Kette) in den Suchpfad des Servers, EINE Stelle (16.11.2026, Edgar: „Kein Doppelcode“).

Bis dahin stand derselbe Dreizeiler in `Meshgenesistestkikleider._regel`, `Exportleistekollision` und `G9eigenhaarbau`. Die Module der Kette importieren ihre Geschwister ohne
Paket (`meshgenesis_kleidergpu`, Paket `haar_Bart`), deshalb vorn in `sys.path`.

    Meshgenesissuchpfad.einhaengen()
"""
import sys

__all__ = ['Meshgenesissuchpfad']


class Meshgenesissuchpfad:

    @staticmethod
    def einhaengen():
        from django.conf import settings
        mesh = str(settings.TOOLS_ROOT / 'meshgenesis')
        if mesh not in sys.path:
            sys.path.insert(0, mesh)
