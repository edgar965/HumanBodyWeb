# -*- coding: utf-8 -*-
"""Kleiderstueckbezug — die Bezugsflächen für `Kleiderstuecknote`: was das Foto-Netz an einem Stück (und an nackter Haut) zeigt, in der RUHELAGE der Figur (04.10.2026).

Das Foto-Netz steht in der Haltung des Fotos (hängende Arme), die Figur und ihre Stücke in der Ruhelage (A-Pose). `Fotostuecke` rechnet das Netz mit `Kleidungsentposen` zurück; diese Klasse
tut dasselbe für die Bezugsflächen, mit denselben Filtern wie der Bau der Stücke: Flächen, die beim Zurückrechnen gezerrt (`Fotostuecke.DEHNUNG_MAX`) oder umgeklappt wurden (Stoff zwischen
hängendem Arm und Rumpf), zählen nicht — sie sagen etwas über die Haltung, nicht über das Stück.

    Stück (Nummer der Maske: 1 Oberteil, 2 Hose, 3 Füße/Socken)   die Flächen der Maske mit `stueck == nummer` und OHNE Hautton (`haut`) — wie `Fotostuecke` sie wählt, nur ohne dessen Höhenkern
                                                                  und Inselfilter: gemessen wird, was das Foto zeigt, nicht, was der Bau übrig ließ
    Haut                                                          die nackten Flächen (`haut` und kein Stück): Gesicht, Hände, Arme, Beine

Braucht `kleidung_maske.npz`, `genesis_ende.npz`, `posiert.npy` (Schritt „koerper"/„vorschau") und das Netz des Auftrags; fehlt etwas, sagt `fehlt()` was.
"""

import numpy as np

__all__ = ['Kleiderstueckbezug']


class Kleiderstueckbezug:
    DATEIEN = ('kleidung_maske.npz', 'genesis_ende.npz', 'posiert.npy')

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage
        self._geladen = False

    def fehlt(self):
        """Der Grund, warum nicht gemessen werden kann — oder None."""
        for name in self.DATEIEN:
            if not self.ablage.arbeit(name).is_file():
                return '%s fehlt (Schritt „Körper")' % name
        if self.ablage.netzdatei() is None:
            return 'Kein Netz'
        return None

    def _laden(self):
        if self._geladen:
            return
        from Kleidung.kleidungsentposen import Kleidungsentposen

        from .meshfigurkleidung import Meshfigurkleidung
        self.scan, _ = Meshfigurkleidung(type('Lauf', (), {'job': self.job, 'ablage': self.ablage})()).koerpernetz()
        with np.load(self.ablage.arbeit('kleidung_maske.npz')) as d:
            self.stueck_je_flaeche = np.asarray(d['stueck'])
            self.haut_je_flaeche = np.asarray(d['haut'], dtype=bool) if 'haut' in d.files else np.zeros(len(self.stueck_je_flaeche), dtype=bool)
        with np.load(self.ablage.arbeit('genesis_ende.npz')) as d:
            self.koerper = (np.asarray(d['punkte'], dtype=np.float64), np.asarray(d['dreiecke'], dtype=np.int64))
        self.entposen = Kleidungsentposen(self.koerper[0], np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64))
        if len(self.stueck_je_flaeche) != len(self.scan.flaechen):
            raise ValueError('Maske (%d Flächen) passt nicht zum Netz (%d)' % (len(self.stueck_je_flaeche), len(self.scan.flaechen)))
        self._geladen = True

    def stueck(self, nummer):
        """`(punkte, flaechen)` in der Ruhelage — die Maskenflächen des Stücks, gesund zurückgerechnet; None ohne Fläche."""
        self._laden()
        return self._ruhelage((self.stueck_je_flaeche == nummer) & ~self.haut_je_flaeche)

    def haut(self):
        """`(punkte, flaechen)` in der Ruhelage — die nackte Haut des Foto-Netzes; None ohne Fläche."""
        self._laden()
        return self._ruhelage(self.haut_je_flaeche & (self.stueck_je_flaeche == 0))

    def koerper_netz(self):
        """`(punkte, dreiecke)` des Körpers der Figur in der Ruhelage."""
        self._laden()
        return self.koerper

    def _ruhelage(self, wahl):
        from .fotostuecke import Fotostuecke
        if not wahl.any():
            return None
        flaechen = self.scan.flaechen[wahl]
        genutzt, neu = np.unique(flaechen.reshape(-1), return_inverse=True)
        posiert = self.scan.punkte[genutzt]
        ruhe = self.entposen.ruhelage(posiert)
        f = neu.reshape(-1, 3)
        heil = Fotostuecke._ungedehnt(posiert, ruhe, f) & Fotostuecke._ungeklappt(posiert, ruhe, f, self.entposen.posiert, *self.koerper)
        if not heil.any():
            return None
        genutzt, neu = np.unique(f[heil].reshape(-1), return_inverse=True)
        return ruhe[genutzt], neu.reshape(-1, 3)
