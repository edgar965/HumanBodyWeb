# -*- coding: utf-8 -*-
"""Hautbackenmaterial — was der Nachbau aus dem Inventar eines Körper-Netzes braucht, und ob er es OHNE Blender gleich backen kann.

Blenders „Emission"-Backen wertet den ganzen Knotenbaum des Materials aus; der Nachbau liest nur Bilder. Er backt ein Material deshalb nur, wenn der Export (`blendexport.py`,
`Blendexport.einfach`) bestätigt hat, dass jeder Eingang ein fester Wert ist oder DIREKT an einem Bildknoten hängt (Linear, Wiederholen, flach, ohne Mapping; die Normale über einen
Normal-Map-Knoten im Tangentenraum). Ein Inventar OHNE diese Kennzeichnung (älter als der Nachbau) gilt als nicht einfach — dann backt Blender wie bisher, nie eine Vermutung.
Mehr als ein Material am Körper (Character Creator: Kopf, Rumpf, Arme, Beine) backt der Nachbau noch nicht.
"""

import os

__all__ = ['Hautbackenmaterial']


class Hautbackenmaterial:
    def __init__(self, netz):
        """`netz`: der Eintrag des Körper-Netzes im Inventar (`inventar['netze']`)."""
        self.netz = netz or {}
        self.materialien = self.netz.get('materialien') or []
        self.material = self.materialien[0] if len(self.materialien) == 1 else {}

    def moeglich(self):
        """`(bool, Grund)`: Der Nachbau darf diesen Körper backen."""
        if len(self.materialien) != 1:
            return False, 'der Körper hat %d Materialien (der Nachbau backt eines)' % len(self.materialien)
        if 'einfach' not in self.material:
            return False, 'das Inventar kennt „einfach" nicht (Export vor dem Nachbau) — Blender backt'
        if not self.material['einfach']:
            return False, 'Material nicht einfach: %s' % (self.material.get('einfach_grund') or 'ohne Angabe')
        for kanal in ('farbe', 'normalen'):
            pfad = self.material.get(kanal)
            if pfad and not os.path.isfile(pfad):
                return False, 'Bild fehlt: %s' % pfad
        if not self.material.get('farbe'):
            return False, 'keine Farbtextur'
        if not self.material.get('rauheit') and self.material.get('rauheit_wert') is None:
            return False, 'weder Rauheitsbild noch Rauheitswert'
        if self.material.get('rauheit') and not os.path.isfile(self.material['rauheit']):
            return False, 'Bild fehlt: %s' % self.material['rauheit']
        return True, ''

    @property
    def farbe(self):
        return self.material.get('farbe')

    @property
    def rauheit(self):
        return self.material.get('rauheit')

    @property
    def rauheit_wert(self):
        """Der feste Wert am Rauheitseingang (0…1) — nur ohne Rauheitsbild."""
        return self.material.get('rauheit_wert')

    @property
    def normalen(self):
        return self.material.get('normalen')
