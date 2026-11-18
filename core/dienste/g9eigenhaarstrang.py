# -*- coding: utf-8 -*-
u"""G9eigenhaarstrang — „Eigen Haar“ und „Eigen Bart“ als Stranghaar einer Genesis-9-Figur: die Strähnen der Haar-Engine (`haar_Bart/eigenhaar.py`, `eigenbart.py`) als
`G9strang` (16.11.2026 abends; der Bart seit 16.11.2026 spät).

Edgar: „bei dem Genesis Objekt ‚Eigen Haar‘ möchte ich einstellungen haben, die du mit deiner Klasse zur verfügung stellst, das Haar soll dann auf das aktuelle Modell gebaut
werden im Character“. Ein Daz-Stranghaar (dForce Pixie) läuft im Charakter schon als Linien mit Hautgewichten (`G9strang`, `G9koerpernetz.folgernetz`, Browser `wireframe`);
diese Unterklasse füllt dieselben Felder aus der Engine statt aus einer Datei — Segmente und Gruppen (`dreiecke_und_gruppen`), Haut (`hautantwort`) und Steckbrief erbt sie:
  Punkte      die sichtbaren Teile der Mittellinien aller Strähnen (`Haarstraehnen.linien`), ungenutzte Punkte weg
  Segmente    je Strähne die Schritte bis zu ihrer sichtbaren Länge, ein Material
  anteil      0 an der Wurzel … 1 an der Spitze (Wurzel- und Spitzenfarbe im Browser)
  Haut        je Leitpunkt die Gewichte des nächsten Hautpunkts der Anlage, längs der Leitsträhne geglättet (`Haarstraehnengewichte.glaetten`); jede Strähne die ihrer
              Leitsträhne am selben Schritt — die Büschel schwingen zusammen
Gebaut auf der Ruhelage DIESER Figur (`G9formung.morphpunkte`); `punkte_zu` stellt sie nur noch mit den Knochenmatrizen der Stellung (keine Projektion wie bei Daz-Strängen,
die für die Grundfigur modelliert sind). In torch auf der Karte.
"""
import torch
from Genesis9.strang import G9strang

__all__ = ['G9eigenhaarstrang']


class G9eigenhaarstrang(G9strang):
    JE_PUNKT = 4
    koerperhaut = False
    dynamisch = False
    unsichtbar = False

    def __init__(self, li, ruhe, name=u'Eigen Haar'):           # bewusst ohne `G9strang.__init__`: keine Datei, die Felder kommen aus der Engine
        self.name = self.kennung = self.pfad = name
        mitte, sicht, se, zu = (li[x] for x in ('mitte', 'sicht', 'se', 'zu'))
        n, k1 = mitte.shape[:2]
        schritt = torch.arange(k1 - 1, device=mitte.device)
        an = schritt[None] < sicht[:, None]                                                # (n, K) sichtbare Segmente
        basis = torch.arange(n, device=mitte.device)[:, None] * k1
        seg = torch.stack([(basis + schritt[None])[an], (basis + schritt[None] + 1)[an]], 1)
        benutzt = torch.unique(seg.reshape(-1))
        neu = torch.full((n * k1,), -1, dtype=torch.long, device=mitte.device)
        neu[benutzt] = torch.arange(len(benutzt), device=mitte.device)
        self.segmente = neu[seg]
        self.material = torch.zeros(len(self.segmente), dtype=torch.long, device=mitte.device)
        self.materialnamen = [name]
        self.punkte = mitte.reshape(-1, 3)[benutzt].double()
        self.anteil = se.reshape(-1)[benutzt].float()
        leitpunkt = (zu[:, None] * k1 + torch.arange(k1, device=mitte.device)[None]).reshape(-1)[benutzt]
        self.haut = self._haut(li, ruhe, leitpunkt)
        self.morphe = self.klon = None
        self.zahlen = {'straehnen': int(n), 'leitstraehnen': int(li['gs'].shape[0])}

    def _haut(self, li, ruhe, leitpunkt):
        u"""`G9haut` der Strähnenpunkte: je Leitpunkt der nächste Punkt der Anlage, dicht über alle Knochen, längs der Leitsträhne geglättet, je Punkt die seines Leitpunkts."""
        from Genesis9.haut import G9haut
        from haar_Bart.haarstraehnengewichte import Haarstraehnengewichte
        from meshgenesis_kleidergpu import Kleidergpu
        h = G9haut.holen()
        idx, gw = torch.as_tensor(h.index, device='cuda').long(), torch.as_tensor(h.gewicht, device='cuda').double()
        gs = li['gs']
        anlage = torch.unique(li['anlage'].reshape(-1))
        nah = anlage[Kleidergpu.an().naechste(gs.reshape(-1, 3).double().contiguous(), ruhe.double()[anlage].contiguous(), 1)[1][:, 0].clamp(max=len(anlage) - 1)]
        dicht = torch.zeros((len(nah), len(h.knochen)), dtype=torch.float64, device='cuda').scatter_add_(1, idx[nah], gw[nah]).reshape(gs.shape[0], gs.shape[1], -1)
        gk, gwl = Haarstraehnengewichte.glaetten(dicht, self.JE_PUNKT)
        gewicht = gwl[leitpunkt]
        return G9haut(h.knochen, gk[leitpunkt], gewicht / gewicht.sum(1, keepdim=True).clamp_min(1e-12))

    def punkte_zu(self, formung, zusatz=None, drehung=None, lage=None):
        u"""Die Strähnen in der Stellung der Formung: Ruhelage (auf DIESER Figur gebaut) mit den Knochenmatrizen und der eigenen Haut."""
        matrizen = formung.matrizen()
        return self.punkte if matrizen.leer else matrizen.anwenden(self.punkte, self.haut)

    def steckbrief(self):
        return dict(super().steckbrief(), **self.zahlen)
