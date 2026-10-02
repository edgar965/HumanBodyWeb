# -*- coding: utf-8 -*-
"""Engine2d3dKleidergrundfigur — Schritt „grundfigur" von „Haar Engine": die Genesis-9-Grundfigur MIT Rig
(30.09.2026).

Der Körper ist die gewählte Grundfigur (Option „Grundfigur", `Meshfigurregler.GRUNDFIGUREN`); die
Iterationen bauen das Haar darüber (`Iterationskreislauf`). Ohne Netz aus Fotos — die Fotos sind Vorlagen,
gegen die die Iterationen ihre Renders benoten.

Ergebnis: `arbeit/grundkoerper.glb` (Netz mit Rig, `G9figurrigglb`; die Engine stellt daran die Arme für den
Vergleich) und `ergebnis['regler']['stellung']` (so zeigt die Bühne die Figur, und „export" baut daraus die
GLB mit Rig). Die Ergebnisse der späteren Schritte (`kreislauf`, `iterationen`) bleiben stehen: Jeder Lauf der
Iterationen setzt beim besten bisherigen Modell an.
"""

import time

__all__ = ['Engine2d3dKleidergrundfigur']


class Engine2d3dKleidergrundfigur:
    DATEI = 'grundkoerper.glb'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def ausfuehren(self):
        from Genesis9.figurrigglb import G9figurrigglb

        from .meshfigurregler import Meshfigurregler

        basis = self.lauf.optionen.get('basis') or 'masculine'
        # Hat der Schritt „koerper" eine Figur geliefert (übernommen oder gerechnet, `ergebnis.regler`), ist SIE die
        # Grundfigur — samt Eigenmorph (`job.stellung()`) und gebackenen Kacheln. Sonst die nackte Grundfigur.
        stellung = self.job.stellung()
        kacheln = {}
        if stellung:
            for k, name in ((self.job.ergebnis.get('fototextur') or {}).get('kacheln') or {}).items():
                if str(k).isdigit() and self.ablage.ergebnis(name).is_file():
                    kacheln[int(k)] = str(self.ablage.ergebnis(name))
            self.lauf.melden(0.1, 'Grundfigur aus dem Körper-Fit (%d Regler) mit Rig' % len(stellung))
        else:
            stellung = dict(Meshfigurregler.GRUNDFIGUREN.get(basis, Meshfigurregler.GRUNDFIGUREN['masculine']))
            self.lauf.melden(0.1, 'Grundfigur Genesis 9 (%s) mit Rig' % basis)
        t = time.perf_counter()
        bericht = G9figurrigglb(stellung, kacheln, name=self.job.name).schreiben(self.ablage.arbeit(self.DATEI))
        if not self.job.ergebnis.get('regler'):
            self.job.ergebnis['regler'] = {'stellung': stellung}
        self.job.ergebnis['grundfigur'] = {
            'basis': basis if not self.job.ergebnis.get('koerperquelle') else 'koerper (%s)' % basis,
            'datei': self.DATEI,
            'sekunden': round(time.perf_counter() - t, 1),
            **{k: v for k, v in (bericht or {}).items() if k != 'datei' and isinstance(v, (int, float))},
        }
        self.lauf.melden(1.0, 'Grundfigur %s bereit' % basis)
