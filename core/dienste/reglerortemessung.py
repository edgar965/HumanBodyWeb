# -*- coding: utf-8 -*-
"""Reglerortemessung — was EIN Regler am Genesis-9-Käfig bewirkt und wo (18.10.2026, für `Reglerortebau`).

Gemessen gegen eine Grundstellung (Vorgabe: die nackte Grundfigur `{}`), beide auf den Boden gestellt wie im Browser:

    mm        größte Verschiebung eines Käfigpunkts
    anteile   wo die Haut GEDEHNT wird, je Region (`G9reglerregionen`) — die Kantenlänge, nicht die Verschiebung: eine Armdrehung verschiebt
              die Hand am weitesten, verformt aber nur das Gelenk
    skal      Anteil des Felds, der gleichmäßige Skalierung ist (≥ 0,8: ein Größenregler)
    feld      das Verschiebungsfeld auf 4.000 festen Punkten (für die Doppelten)

Herkunft: `ProjektTemp/_wegwerf/regler_inventur/inventur.py` und `auswertung.py` (Inventur vom 18.10.2026), hier als Klasse.
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.zufallsstrom import Zufallsstrom

__all__ = ['Reglerortemessung']


class Reglerortemessung:
    PROBE = 4000
    SAAT = 18

    def __init__(self):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.reglerregionen import G9reglerregionen

        self.basis = self.punkte({})
        # `vierecke` zeigen auf die 25.182 Käfigpunkte (`dreiecke` auf die UV-Punkte, 27.087 — gemessen 18.10.2026).
        vier = Torchfeld.feld(G9basisnetz.holen().vierecke, dtype=torch.int64)
        if int(vier.max()) >= len(self.basis):
            raise ValueError('Vierecke zeigen über den Käfig hinaus (%d >= %d)' % (int(vier.max()), len(self.basis)))
        kanten = Torchfeld.vstack([vier[:, [0, 1]], vier[:, [1, 2]], vier[:, [2, 3]], vier[:, [3, 0]]])
        self.kanten = Torchfeld.unique(torch.sort(kanten, dim=1, stable=True).values, axis=0)
        self.laenge0 = self._laengen(self.basis)
        self.region = G9reglerregionen.holen()
        self.wahl = torch.sort(Zufallsstrom.default_rng(self.SAAT).choice(len(self.basis), self.PROBE, replace=False), stable=True).values
        probe = self.basis[self.wahl]
        self.mitte = probe - probe.mean(axis=0)

    @staticmethod
    def punkte(stellung):
        from Genesis9.formung import G9formung

        p = Torchfeld.feld(G9formung(stellung).punkte(), dtype=torch.float64)
        return p - Torchfeld.feld([0.0, p[:, 1].min(), 0.0], copy=True)

    def _laengen(self, p):
        return Torchfeld.linalg_norm(p[self.kanten[:, 0]] - p[self.kanten[:, 1]], dim=1)

    def messen(self, stellung, grund=None):
        """`{mm, anteile, skal, feld}` von `stellung` gegen `grund` (Punkte, Vorgabe die Grundfigur)."""
        grund_p = self.basis if grund is None else grund
        laenge0 = self.laenge0 if grund is None else self._laengen(grund_p)
        neu = self.punkte(stellung)
        d = neu - grund_p
        dehn = Torchfeld.abs(self._laengen(neu) - laenge0)
        je_punkt = Torchfeld.bincount(self.kanten.ravel(), weights=Torchfeld.repeat_interleave(dehn, 2), minlength=len(grund_p))
        from Genesis9.reglerregionen import G9reglerregionen

        anteile = G9reglerregionen.anteile(je_punkt, self.region)
        feld = d[self.wahl]
        return {'mm': float(Torchfeld.linalg_norm(d, dim=1).max()) * 1000.0,
                'anteile': {o: round(a, 3) for o, a in anteile.items() if a >= 0.01},
                'skal': round(self.skalierung(feld), 3), 'feld': Torchfeld.astype(feld, torch.float32)}

    def skalierung(self, feld):
        """Anteil des Felds (nach Abzug der Verschiebung), den eine gleichmäßige Skalierung um die Mitte erklärt."""
        d = Torchfeld.feld(feld, dtype=torch.float64)
        d = d - d.mean(axis=0)
        ganz = float((d * d).sum())
        if ganz <= 0:
            return 0.0
        s = float((d * self.mitte).sum() / (self.mitte * self.mitte).sum())
        rest = d - s * self.mitte
        return max(0.0, 1.0 - float((rest * rest).sum()) / ganz)

    @staticmethod
    def drehung(stellung):
        """Größte Knochendrehung (Grad), die `stellung` über die Formeln stellt — eine Drehung ist Wirkung, auch ohne Käfigverschiebung."""
        from Genesis9.formung import G9formung

        posen = G9formung(stellung).formeln.posen()
        return max((abs(v) for k in posen.values() for p, v in k.items() if p.startswith('rotation/')), default=0.0)
