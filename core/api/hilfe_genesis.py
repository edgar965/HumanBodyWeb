# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> Genesis: die Daz-Garderobe gegen die GarmentCode-Kleiderbibliothek.

Edgar (25.09.2026): „erzeuge eine Seite Hilfe - Kleidung - Genesis wo du die
Erkenntnisse hineinschreibst und den Vergleich mit Garment Code". Die Daten
kommen aus `kleidung.genesis.Kleidungsgenesis`, nicht aus der Vorlage —
dieselbe Regel wie bei `KleidungFitting`.
"""

from kleidung.genesis import Kleidungsgenesis

from .hilfeseite import Hilfeseite


class KleidungGenesis(Hilfeseite):
    """Zwei Bibliotheken, warum sie nicht zusammenpassen, der Leser, der Vergleich, der Weg."""

    template_name = 'hilfe/kleidung_genesis.html'
    AKTIV = 'hilfe_kleidung_genesis'

    def kontext(self):
        return {
            'bibliotheken': Kleidungsgenesis.bibliotheken(),
            'warum_nicht': Kleidungsgenesis.warum_nicht(),
            'leser': Kleidungsgenesis.leser(),
            'vergleich': Kleidungsgenesis.vergleich(),
            'weg': Kleidungsgenesis.weg(),
            'stand': Kleidungsgenesis.stand(),
            'risiken': Kleidungsgenesis.risiken(),
            'daz_stuecke': Kleidungsgenesis.DAZ_STUECKE,
            'mh_stuecke': Kleidungsgenesis.MH_STUECKE,
            'paarung_mm': Kleidungsgenesis.PAARUNG_MM,
            'mh_karte_mm': Kleidungsgenesis.MH_KARTE_MM,
        }
