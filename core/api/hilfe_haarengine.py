# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> Haar Engine: wie aus Fotos eine Genesis-Frisur wird.

Edgar (30.09.2026): „schreibe den Plan in eine neue Seite Hilfe - Kleidung -
Haar Engine". Die Daten kommen aus `kleidung.haarengine.Kleidungshaarengine`,
nicht aus der Vorlage — dieselbe Regel wie bei `KleidungGenesis`.
"""

from kleidung.haarengine import Kleidungshaarengine

from .hilfeseite import Hilfeseite


class KleidungHaarEngine(Hilfeseite):
    """Der Befund, die drei Schichten, was die Engine verstellt, was offen ist."""

    template_name = 'hilfe/kleidung_haarengine.html'
    AKTIV = 'hilfe_kleidung_haarengine'

    def kontext(self):
        return {
            'haare': Kleidungshaarengine.haare(),
            'mehrteilig': Kleidungshaarengine.mehrteilig(),
            'klone': Kleidungshaarengine.klone(),
            'warum_nicht': Kleidungshaarengine.warum_nicht(),
            'schichten': Kleidungshaarengine.schichten(),
            'wo': Kleidungshaarengine.wo(),
            'achsen': Kleidungshaarengine.achsen(),
            'gemessen': Kleidungshaarengine.gemessen(),
            'engine': Kleidungshaarengine.engine(),
            'parameter': Kleidungshaarengine.parameter(),
            'offen': Kleidungshaarengine.offen(),
            'grenzen_offen': Kleidungshaarengine.grenzen_offen(),
            'katalog': Kleidungshaarengine.KATALOG,
            'frisuren': Kleidungshaarengine.FRISUREN,
            'regler': Kleidungshaarengine.REGLER,
            'stile': Kleidungshaarengine.STILE,
            'varianten': Kleidungshaarengine.VARIANTEN,
            'morphdateien': Kleidungshaarengine.MORPHDATEIEN,
            'gruppen': Kleidungshaarengine.GRUPPEN,
            'achsen_zahl': Kleidungshaarengine.ACHSEN,
            'asset_name': Kleidungshaarengine.ASSET_NAME,
            'asset_kennung': Kleidungshaarengine.ASSET_KENNUNG,
        }
