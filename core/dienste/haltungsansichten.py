# -*- coding: utf-8 -*-
"""Haltungsansichten — die Teile einer Runde in der Haltung des Modells UND, je Foto, in der Haltung dieses Fotos (08.10.2026).

Bis dahin häutete die Runde alle Teile EINMAL in die Haltung des Modells (`G9haltungshaut`, beide Arme gleich, beide Beine gleich, gemittelt über die Fotos) und renderte, benotete und projizierte alle Fotos damit. Zeigen die Fotos
verschiedene Momente (N1: vorn ein Arm waagerecht und die Beine im Schritt, hinten hängende Arme und gerade Beine), traf diese Haltung keins; die Fotohaut deckte die Beine zu 7 % (`Haltungsansicht`, `Hautprobenmehrpose`).

`bauen` häutet die Teile zuerst wie bisher (`teile`, die Haltung des Modells — Bühne, Netznote, Befund, Gesicht und Haar rechnen damit) und dann je Foto neu, wenn dessen Gliedwinkel (`kreislauf.haltung_foto.ansichten`) die Haltung ändern
(`Haltungsansicht.drehung`); `von(referenz)` gibt die Teile für ein Foto. Ändert ein Foto nichts (kein Gliedwinkel, Seitenansicht, gleiche Werte), ist es dieselbe Liste wie `teile`. Option `iterationen.haltung_je_foto`.
Die Hose aus dem Körpernetz (`Hosenteil`) wird je Haltung neu gebaut.
"""

from Genesis9.haltungshaut import G9haltungshaut
from iterationen2d3d.haltungsansicht import Haltungsansicht

from .haarzonen import Haarzonen
from .hosenteil import Hosenteil

__all__ = ['Haltungsansichten']


class Haltungsansichten:
    def __init__(self, teile, je_datei=None):
        self.teile = teile
        self._je = dict(je_datei or {})

    def von(self, referenz):
        """Die Teile in der Haltung des Fotos `referenz` (`Iterationsreferenz`) — `teile`, wo es keine eigene gibt."""
        return self._je.get(referenz.datei, self.teile)

    @property
    def verschieden(self):
        """True, wenn mindestens ein Foto seine eigene Haltung hat."""
        return any(t is not self.teile for t in self._je.values())

    def texturen_angleichen(self):
        """Nach der Fotoprojektion der Kleider: die Kopien in den Haltungen der Fotos tragen dieselben Bilder wie ihre Ruhelage (wie bei `teile` in `Begutachtungswerkzeug.fototextur`)."""
        for liste in {id(t): t for t in self._je.values() if t is not self.teile}.values():
            for t in liste:
                t['textur'] = t.get('ruhe', t)['textur']

    @staticmethod
    def _posen(bau, drehung, roh, ordner):
        return Hosenteil.ersetzen(G9haltungshaut(bau.stellung, drehung, bau.boden).posieren(roh), ordner)

    @classmethod
    def bauen(cls, modell, bau, referenzen, haltung_foto, ordner, je_foto=True):
        """`modell`: `ModellMitKleidern`; `bau`: der `Kleidermodellbau` der Runde; `referenzen`: die Fotos der Runde; `haltung_foto`: `kreislauf.haltung_foto` (oder None); `ordner`: Ablage der Hosentextur (`Hosenteil`);
        `je_foto` False = nur die Haltung des Modells (Option `iterationen.haltung_je_foto` = aus)."""
        roh = Haarzonen.anwenden(bau.teile(modell), modell.farben)            # Haarfarbe je Kopfzone (02.10.2026)
        basis = modell.drehung()
        teile = cls._posen(bau, basis, roh, ordner)
        je = {}
        gemessen = (haltung_foto or {}).get('ansichten') or {}
        for r in referenzen if je_foto else []:
            drehung = Haltungsansicht.drehung(basis, gemessen.get(r.datei), r.winkel)
            if drehung is not basis:
                je[r.datei] = cls._posen(bau, drehung, roh, ordner)
        return cls(teile, je)
