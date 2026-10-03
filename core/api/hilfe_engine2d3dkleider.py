# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> 2D3D Kleider: wie aus Fotos eine Genesis-Frisur wird.

Edgar (30.09.2026): „schreibe den Plan in eine neue Seite Hilfe - Kleidung -
2D3D Kleider". Die Daten kommen aus `kleidung.engine2d3dkleider.Kleidungsengine2d3dkleider`,
nicht aus der Vorlage — dieselbe Regel wie bei `KleidungGenesis`.
"""

from kleidung.engine2d3dkleider import Kleidungsengine2d3dkleider

from .hilfeseite import Hilfeseite


class KleidungEngine2d3dKleider(Hilfeseite):
    """Der Befund, die drei Schichten, was die Engine verstellt, was offen ist."""

    template_name = 'hilfe/kleidung_engine2d3dkleider.html'
    AKTIV = 'hilfe_kleidung_engine2d3dkleider'

    def kontext(self):
        return {
            'haare': Kleidungsengine2d3dkleider.haare(),
            'mehrteilig': Kleidungsengine2d3dkleider.mehrteilig(),
            'klone': Kleidungsengine2d3dkleider.klone(),
            'warum_nicht': Kleidungsengine2d3dkleider.warum_nicht(),
            'schichten': Kleidungsengine2d3dkleider.schichten(),
            'wo': Kleidungsengine2d3dkleider.wo(),
            'achsen': Kleidungsengine2d3dkleider.achsen(),
            'gemessen': Kleidungsengine2d3dkleider.gemessen(),
            'engine': Kleidungsengine2d3dkleider.engine(),
            'parameter': Kleidungsengine2d3dkleider.parameter(),
            'offen': Kleidungsengine2d3dkleider.offen(),
            'grenzen_offen': Kleidungsengine2d3dkleider.grenzen_offen(),
            'katalog': Kleidungsengine2d3dkleider.KATALOG,
            'frisuren': Kleidungsengine2d3dkleider.FRISUREN,
            'regler': Kleidungsengine2d3dkleider.REGLER,
            'stile': Kleidungsengine2d3dkleider.STILE,
            'varianten': Kleidungsengine2d3dkleider.VARIANTEN,
            'morphdateien': Kleidungsengine2d3dkleider.MORPHDATEIEN,
            'gruppen': Kleidungsengine2d3dkleider.GRUPPEN,
            'achsen_zahl': Kleidungsengine2d3dkleider.ACHSEN,
            'asset_name': Kleidungsengine2d3dkleider.ASSET_NAME,
            'asset_kennung': Kleidungsengine2d3dkleider.ASSET_KENNUNG,
        }
