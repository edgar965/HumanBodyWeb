# -*- coding: utf-8 -*-
"""Blendimportrequisit — ein Stück, das zu weit vom Körper hängt für die Käfig-Nachbarschaft, geht starr mit dem Teil, das es berührt.

Die vierte Klasse des Konzepts (`Docu/konzepte/2026-10-09_blend-import-kleidung-in-die-ruhelage-konzept.md`, Abschnitt 2): starr an EINEM Teil,
erkennbar am Abstand zum Käfig, nicht am Namen. Anlass (09.10.2026, drittes Modell „Fallout ranger"): die Laserwaffe in der Hand hängt zu 98 %
mehr als 3 h (12 mm) vom Käfig, im Median 77 mm; ihre nächsten Käfigpunkte liegen am Rumpf, nicht an der Hand — die Käfig-Nachbarschaft
(Kabsch über 40 posierte Käfigpunkte, σ 5 cm) stellte sie an den Rumpf zurück: Haltungstreue Median 3,9 mm, p90 35,5, max 90,9 mm
(18 % über 25 mm), in der Ruhe ein Ding vor der Brust statt in der Hand. Der Helm (105 mm im Median) ging bisher über dieselbe Nachbarschaft
am Kopf; Haar und Augen sind starr am Kopf (`Blendimportlage.kopf_starr`), das gilt hier für alles, was so weit abhängt.

    erkennen   mindestens `FREI_ANTEIL` der Punkte weiter als `FREI_H · h` vom Käfig UND Abstand im Median ab `ABSTAND_H · h` →
               das Teil ist das, dem ein Punkt am nächsten kommt: unter den `NAH_ANTEIL` nächsten Punkten das häufigste (die
               Berührung zählt, nicht der Mittelwert). Gemessen: die Waffe des „Fallout ranger" berührt den RUMPF (nicht die Hand, Rundlauf
               6,8 mm); an „Asian Female" und „cute girl" erkennt es nichts, am Helm auch nicht (er liegt am Kopf an, im Käfig nahe genug)
    ruhelage   EINE Starrkörperbewegung (Kabsch ohne Maßstab) über die Käfigpunkte dieses Teils, Haltung → Ruhe
    Bindung    das Stück hängt ganz an dem Knochen, der das Teil führt (`Blendimportteile.KNOCHEN`, wie das Haar an `head`)
"""

import numpy as np
from Genesis9.koerperteile import G9koerperteile

__all__ = ['Blendimportrequisit']


class Blendimportrequisit:
    FREI_H = 3.0
    #: 0,9 → 0,75 (10.10.2026): das Katana von Rosemary Winters (115 cm, Griff dicht vernetzt IN der Hand) hat 19 % seiner Punkte näher als 3 h am Käfig
    #: (frei 0,812, Median 16,0 h) und lief darum als Kleid durch die Käfig-Nachbarschaft — Klinge am Oberschenkel mitgezogen, Kanten 3,1 % gedehnt.
    #: Gemessen an acht Importen (`ProjektTemp/_wegwerf/requisit_kalibrierung.py`): außer dem Katana liegt kein gesundes Stück (Rolle nicht Haar) mit
    #: Median ≥ 8 h unter 0,9 frei; die größten Kleider (Mantel 4,9 h, Rüstung, Seil 5,2 h, Hemd 6,0 h) bleiben weit unter 8 h.
    FREI_ANTEIL = 0.75
    ABSTAND_H = 8.0
    NAH_ANTEIL = 0.02
    #: Mindestzahl Käfigpunkte des Handtellers für die Starrkörperbewegung (sonst alle Punkte des Teils).
    HANDTELLER_MIN = 100

    def __init__(self, lage):
        self.lage = lage

    def erkennen(self, punkte_blender):
        """`{teil, nummer, knochen, abstand_median_mm, frei_anteil}` für ein Requisit, sonst None."""
        from .blendimportteile import Blendimportteile

        lage = self.lage
        netz = lage.ins_netz(punkte_blender)
        d, i = lage.entposen().baum.query(netz, workers=-1)
        h = lage.h
        frei = float((d > self.FREI_H * h).mean())
        if frei < self.FREI_ANTEIL or float(np.median(d)) < self.ABSTAND_H * h:
            return None
        nah = np.argsort(d)[:max(10, int(self.NAH_ANTEIL * len(d)))]
        teile = lage.teil[i[nah]]
        teile = teile[teile >= 0]
        if not len(teile):
            return None
        nummer = int(np.bincount(teile).argmax())
        name = G9koerperteile.TEILE[nummer]
        knochen = Blendimportteile.KNOCHEN.get(name)
        if knochen is None:
            return None
        return {'teil': name, 'nummer': nummer, 'knochen': knochen,
                'abstand_median_mm': round(float(np.median(d)) * 1000.0, 1), 'frei_anteil': round(frei, 3)}

    def ruhelage(self, punkte_blender, nummer):
        """`(Punkte in der Ruhelage, Rundlauf des Teils in mm RMS)` — Starrkörperbewegung des Käfigteils (ohne Maßstab)."""
        lage = self.lage
        teil = lage.teil == nummer
        # Ohne die Punkte, die die Fingerhaltung bewegt (`Blendimportfinger`): Handteller und Handgelenk sind starr, die gebeugten Finger nicht —
        # sie bogen die Starrkörperbewegung der Hand (Käfig der Haltung mit Faust, Ruhe mit gestreckter Hand).
        handteller = teil & ~lage.finger_bewegt
        if handteller.sum() >= self.HANDTELLER_MIN:
            teil = handteller
        a, b = lage.kaefig_posiert[teil], lage.kaefig_ruhe[teil]
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        s = np.sign(np.linalg.det(vt.T @ u.T)) or 1.0
        r = vt.T @ np.diag([1.0, 1.0, s]) @ u.T
        rms = float(np.sqrt((np.linalg.norm((a - ma) @ r.T + mb - b, axis=1) ** 2).mean())) * 1000.0
        return (lage.ins_netz(punkte_blender) - ma) @ r.T + mb, round(rms, 2)
