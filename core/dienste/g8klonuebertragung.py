# -*- coding: utf-8 -*-
u"""G8klonuebertragung — ein Genesis-8-Verschiebungsfeld über Daz' Klon auf den Genesis-9-Käfig legen (16.11.2026).

Dasselbe wie `G1klonuebertragung` (Stellung über die Auto-Fit-Schablone, Zuordnung Käfig in Klon-Gestalt -> nächstes Hautdreieck,
Übertragung, Feldputz) — nur mit dem Klon von Genesis 8 Female oder Male (`CloneGenesis8Female`: Genesis 9 in der Gestalt von G8F,
`Base/Tools/Clones/CloneGenesis8Female.dsj`) und den Hautgruppen von Genesis 8. Genesis 8 steht schon in A-Stellung; die Schablone dreht
nur die Unterschiede (Oberschenkel −6°, Fuß +3°, `G9autofit`).

Hautgruppen von Genesis 8 Female (gelesen 16.11.2026, `Genesis8Female.dsf`, 16 Gruppen): Torso, Face, Lips, Teeth, Ears, Legs, EyeSocket,
Mouth, Arms, Pupils, EyeMoisture, Fingernails, Cornea, Irises, Sclera, Toenails — Haut sind Torso, Face, Lips, Ears, Legs, EyeSocket, Arms
und die Nägel; Zähne, Mundraum und Auge nicht.
"""
from .g1klonuebertragung import G1klonuebertragung

__all__ = ['G8klonuebertragung']


class G8klonuebertragung(G1klonuebertragung):
    u"""Genesis-8-Feld -> Käfigfeld von Genesis 9."""

    KLON = 'CloneGenesis8Female'
    HAUT = ('Torso', 'Face', 'Lips', 'Ears', 'Legs', 'EyeSocket', 'Arms', 'nails')

    def __init__(self, klon=None):
        u"""`klon`: `CloneGenesis8Female` (Vorgabe) oder `CloneGenesis8Male`."""
        if klon:
            self.KLON = klon
        super().__init__()
