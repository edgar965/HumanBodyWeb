# -*- coding: utf-8 -*-
"""Hautbackenblenderecken — `normals_calc_corners`: die Normale je Polygonecke aus den Fächern (und, falls vorhanden, den eigenen Normalen).

Blender v5.2.2, `mesh_normals.cc` (gelesen 10.10.2026), je Fächer:
  1. `accumulate_fan_normal`: ein Fächer mit EINER Ecke hat genau die Flächennormale (Blender: „logically unnecessary, but due to floating point precision required");
     sonst `math::normalize(Σ Flächennormale × safe_acos_approx(dot(dir_prev, dir_next)))`, in Fächerreihenfolge.
  2. Mit eigenen Normalen (`handle_fan_result_and_custom_normals`): Lnor-Raum aus Fächernormale, `dir_next` der ersten Ecke (Referenzkante) und `dir_prev` der letzten (Gegenkante),
     alpha aus dem Mittel der Winkel aller Fächerkanten zur Normale (`dir_next` jeder Ecke, dazu `dir_prev` der letzten, falls es eine andere Kante ist), danach die
     Dekodierung des GANZZAHLIG gemittelten (Division gegen Null gerundet) `custom_normal` aller Ecken des Fächers.
  3. Alle Ecken des Fächers bekommen diese Normale.
Punkte ohne Polygon haben keine Ecken und fallen weg.
"""

import math
import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .hautbackenblendermathe import Hautbackenblendermathe as M
from .hautbackenblenderraeume import Hautbackenblenderraeume as R

__all__ = ['Hautbackenblenderecken']


class Hautbackenblenderecken:
    @staticmethod
    def berechnen(p, e, faecher, flaechen_normalen, eigene=None):
        """`(L,3)` float32. `e`: `Hautbackenblendereintraege`, `faecher`: `Hautbackenblenderfaecher`, `eigene`: (L,2) int16 oder None."""
        vor, nach, faktor = e.richtungen(p)
        reihe, anfang, groesse = faecher.reihe, faecher.anfang, faecher.groesse
        erste = reihe[anfang[:-1]]
        letzte = reihe[anfang[1:] - 1]
        summe = torch.zeros((len(groesse), 3), dtype=torch.float32, device='cuda')
        for k in range(int(groesse.max())):
            aktiv = torch.flatten(groesse > k).nonzero()[:, 0]
            eintrag = reihe[anfang[aktiv] + k]
            summe[aktiv] += flaechen_normalen[e.flaeche[eintrag]] * faktor[eintrag][:, None]
        normal = M.normalisieren(summe)
        einzeln = groesse == 1
        normal[einzeln] = flaechen_normalen[e.flaeche[erste[einzeln]]]
        if eigene is not None:
            normal = Hautbackenblenderecken._eigene(e, faecher, normal, vor, nach, erste, letzte, Torchfeld.feld(eigene))
        # Eine Ecke, die nie „erste Ecke" eines Eintrags ist (zweite Nennung eines Punkts im selben Polygon), bekommt in Blender nie einen Wert: bei uns (0, 0, 0).
        ecken = torch.zeros((len(e.ecke), 3), dtype=torch.float32, device='cuda')
        ecken[e.ecke] = normal[faecher.fan]
        return ecken

    @staticmethod
    def _eigene(e, faecher, normal, vor, nach, erste, letzte, eigene):
        reihe, anfang, groesse = faecher.reihe, faecher.anfang, faecher.groesse
        mehrere = groesse > 1
        # Kanten des Fächers: dir_next jeder Ecke + dir_prev der letzten, wenn das eine andere Kante ist als dir_next der ersten.
        zusatz = mehrere & (e.punkt_vor[letzte] != e.punkt_nach[erste])
        winkel = torch.zeros(len(groesse), dtype=torch.float32, device='cuda')
        for k in range(int(groesse.max())):
            aktiv = torch.flatten((groesse > k) & mehrere).nonzero()[:, 0]
            eintrag = reihe[anfang[aktiv] + k]
            winkel[aktiv] += M.acos_naeherung(M.punkt(nach[eintrag], normal[aktiv]))
        z = torch.flatten(zusatz).nonzero()[:, 0]
        winkel[z] += M.acos_naeherung(M.punkt(vor[letzte[z]], normal[z]))
        anzahl = Torchfeld.astype(groesse + zusatz, torch.float32)
        alpha = torch.where(mehrere, winkel / torch.where(mehrere, anzahl, Torchfeld.f32(1.0)), Torchfeld.f32(math.nan))
        raum = R.definieren(normal, nach[erste], vor[letzte], Torchfeld.astype(alpha, torch.float32))
        # ganzzahliger Mittelwert der Rohdaten (int2 /= int: Division gegen Null gerundet)
        summe = Torchfeld.stack([Torchfeld.bincount(faecher.fan, weights=Torchfeld.astype(eigene[e.ecke, i], torch.float64), minlength=len(groesse)) for i in (0, 1)], axis=1)
        summe = Torchfeld.astype(Torchfeld.round(summe), torch.int64)
        mittel = Torchfeld.sign(summe) * (Torchfeld.abs(summe) // groesse[:, None])
        return R.dekodieren(raum, Torchfeld.astype(mittel, torch.int16))
