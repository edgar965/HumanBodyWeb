# -*- coding: utf-8 -*-
"""Haarknotenauftrag — was ein Blender-Haarknoten (`Engine2d3dKleiderblender.haar`) VOR und NACH Blender braucht
(01.10.2026, herausgelöst, als Zielobjekt und Topologieänderung dazukamen): die Strähnen eines Teils als `.npz`
(Punkte in Strähnenreihenfolge, Längen, Ortsmaske), das Zielobjekt (Grundfigur) für Shrinkwrap und Duplicate, die
KOPFHAUT mit echter UV (`G9kopfhaut`: Daz-Kappe oder Kopf der Grundfigur) für Attach, Interpolate und Generate, und
danach die Rückführung — ein Delta je Punkt für die verformenden Knoten (`G9kleidmorphe`) oder neue Strähnen als Rezept
aus den alten Punkten (`G9haarzusatz.aus_blender`) für die erzeugenden.

Startet Blender NICHT selbst — das bleibt `Engine2d3dKleiderblender` (`BlenderNurUeberEinenArbeiterTest`).
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

from ..atomic_write import AtomarSchreiber

__all__ = ['Haarknotenauftrag']


class Haarknotenauftrag:
    #: Knoten, die die Grundfigur als Zielobjekt brauchen (Shrinkwrap: Abstand zur ganzen Figur).
    MIT_ZIEL = ('shrinkwrap', 'duplicate')
    #: Knoten, die die KOPFHAUT mit ihrer echten UV brauchen (`G9kopfhaut`, 01.10.2026): Attach legt sie an den Kurven
    #: ab, Interpolate und Generate lesen sie dort — für die beiden rechnet Blender erst Attach (ohne Einrasten).
    MIT_KOPFHAUT = ('attach', 'generate', 'interpolate')
    #: Knoten, die Strähnen erzeugen — die Ausgabe hat mehr Punkte, Ergebnis ist ein Zusatz (`str.<name>`).
    ZUSATZ = ('duplicate', 'interpolate', 'generate')
    #: Interpolate/Generate verteilen `Density` Strähnen JE QUADRATMETER (Blender-Vorgabe 10 — auf einer Kopfhaut von
    #: 0,04 m² keine einzige). Ohne Angabe: so viele neue, wie dieser Anteil der vorhandenen.
    DICHTE_ANTEIL = 0.5

    def __init__(self, ordner, sorte, knoten, werte, teile=None, kaefige=None, y0=None):
        self.ordner = ordner
        self.sorte = sorte
        self.knoten = str(knoten)
        self.werte = dict(werte)
        self._koerper = None
        self._quelle = (teile, kaefige, y0)
        self._kopfhaut = None
        #: Steckbrief der Kopfhaut (Quelle, Fläche) für den Brief des Morphs.
        self.kopfhaut = None

    def kopfhautdatei(self):
        """Die Kopfhaut (`G9kopfhaut`: Kappe oder Kopf der Grundfigur) als `.npz` mit UV je Dreiecksecke."""
        if self._kopfhaut is None:
            from Genesis9.kopfhaut import G9kopfhaut
            teile, kaefige, y0 = self._quelle
            haut = G9kopfhaut.aus_teilen(teile, kaefige, y0)
            pfad = self.ordner / ('%s_kopfhaut.npz' % self.sorte)
            Npztorch.speichern(pfad, punkte=Torchfeld.feld(haut['punkte'], dtype=torch.float32), dreiecke=Torchfeld.feld(haut['dreiecke'], dtype=torch.int32), uv=Torchfeld.feld(haut['uv'], dtype=torch.float32), komprimiert=True, fuer_numpy=True)          # Blender (`haarknoten.py`) liest mit numpy
            self.kopfhaut = {'quelle': haut['quelle'], 'flaeche_m2': round(haut['flaeche_m2'], 5),
                             'dreiecke': int(len(haut['dreiecke']))}
            self._kopfhaut = pfad
        return self._kopfhaut

    def _werte(self, punkte, ketten):
        """Die Werte dieses Teils: Dichte und Haarlänge aus den Strähnen, wenn das Rezept sie nicht nennt."""
        werte = dict(self.werte)
        if self.knoten in ('interpolate', 'generate') and 'Density' not in werte and self.kopfhaut:
            werte['Density'] = round(self.DICHTE_ANTEIL * len(ketten) / max(self.kopfhaut['flaeche_m2'], 1e-4), 1)
        if self.knoten == 'generate' and 'Hair Length' not in werte:
            laengen = [float(Torchfeld.linalg_norm(Torchfeld.diff(punkte[k], dim=0), dim=1).sum()) for k in ketten]
            werte['Hair Length'] = round(float(Torchfeld.median(laengen)), 4)
        return werte

    # -------------------------------------------------------------- hin

    def koerperdatei(self):
        if self._koerper is None:
            from Genesis9.kleidmorphe import G9kleidmorphe
            k_punkte, k_dreiecke, _n, _b, _boden = G9kleidmorphe.koerper()
            pfad = self.ordner / ('%s_koerper.npz' % self.sorte)
            Npztorch.speichern(pfad, punkte=Torchfeld.feld(k_punkte, dtype=torch.float32), dreiecke=Torchfeld.feld(k_dreiecke, dtype=torch.int32), komprimiert=True, fuer_numpy=True)          # Blender (`haarknoten.py`) liest mit numpy
            self._koerper = pfad
        return self._koerper

    def schreiben(self, nummer, punkte, ketten, maske):
        """→ (Pfad der auftrag.json, Auftrag) für ein Strang-Teil; `ketten` aus `G9haarzusatz.ketten`."""
        reihe = Torchfeld.cat(ketten)
        stamm = self.ordner / ('%s_%d_%s' % (self.sorte, nummer, self.knoten))
        Npztorch.speichern(str(stamm) + '_straehnen.npz', punkte=Torchfeld.astype(punkte[reihe], torch.float32), laengen=Torchfeld.feld([len(k) for k in ketten], dtype=torch.int32), maske=Torchfeld.astype(maske[reihe], torch.float32), komprimiert=True, fuer_numpy=True)          # Blender (`haarknoten.py`) liest mit numpy
        auftrag = {'straehnen': str(stamm) + '_straehnen.npz', 'aus': str(stamm) + '_nachher.npz',
                   'bericht': str(stamm) + '_bericht.json', 'knoten': self.knoten,
                   'zusatz': self.knoten in self.ZUSATZ}
        if self.knoten in self.MIT_ZIEL:
            auftrag['koerper'] = str(self.koerperdatei())
        if self.knoten in self.MIT_KOPFHAUT:
            auftrag['koerper'] = str(self.kopfhautdatei())
            auftrag['anheften'] = self.knoten != 'attach'
        auftrag['werte'] = self._werte(punkte, ketten)
        pfad = stamm.parent / (stamm.name + '_auftrag.json')
        AtomarSchreiber.json_schreiben(pfad, auftrag)
        return pfad, auftrag

    # ------------------------------------------------------------ zurück

    @staticmethod
    def delta(auftrag, punkte, reihe, maske):
        """Verformender Knoten: Delta je Punkt, mit dem Ortsgewicht je Punkt (Blender wertet `Mask` je Strähne —
        gemessen 01.10.2026 am Pixie: 82 % der Punkte bewegt bei 30 % im Sektor)."""
        with Npztorch.lesen(auftrag['aus']) as d:
            nachher = Torchfeld.feld(d['punkte'], dtype=torch.float64)
        delta = torch.zeros_like(punkte)
        delta[reihe] = (nachher - punkte[reihe]) * maske[reihe][:, None]
        return delta

    @staticmethod
    def zusatz(auftrag, folger, punkte):
        """Erzeugender Knoten: die neuen Strähnen als Rezept aus den alten Punkten (`G9haarzusatz.aus_blender`)."""
        from Genesis9.haarzusatz import G9haarzusatz
        with Npztorch.lesen(auftrag['aus']) as d:
            nachher = Torchfeld.feld(d['punkte'], dtype=torch.float64)
            laengen = Torchfeld.feld(d['laengen'], dtype=torch.int64)
        return G9haarzusatz.aus_blender(folger, punkte, nachher, laengen)
