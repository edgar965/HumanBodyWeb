# -*- coding: utf-8 -*-
"""Fotogenesisdurchstoss — sticht der Körper der Genesis-Figur durch die Hüllen über Haar und Kleidung? (30.10.2026, Edgar mit einem Bild der Figur von schräg hinten: „Textur T-Shirt
hinten kaputt“, „Füße vorne kaputt“, „texturfehler am Hals und oberen T-shirt (weisse flecken)“ — gesehen in `diag_genesis_ansicht.py`: wo die Flecken sind, liegt der Körper AUF
oder VOR der Hülle; die Zehen stehen aus der Socke, der Rücken aus dem Hemd.)

Je Ansicht zwei Raster (`Fotogenesisgenesisansicht`): nur der Körper samt Augäpfeln (KOERPER), nur die Hüllen (alle Stücke außer Körper und Augen). Ein Pixel ist durchgestoßen, wo
beide da sind und
  - beide Flächen bis GLEICH_MM gleich tief liegen: dort kämpfen sie um denselben Pixel, und die Seite zeigt Flecken — gleich, welcher Punkt des Körpers es ist; oder
  - der Körper vor der Hülle liegt, aber weniger als VOR_MM (weiter vorn ist es ein anderes Glied, etwa der Arm vor dem Hemd), und der Körperpunkt am Pixel selbst bedeckt ist
    (seine Klasse ist Haar oder Kleidung, `bedeckt`): nur dann gehört er unter die Hülle.
Seit 30.10.2026 abends (beides an Lauf 18.36 nachgesehen, `ProjektTemp/_wegwerf/fotogenesis/diag_durchstoss_bild.py 1 0`): ohne Augäpfel sah der Körperraster durch die Augenlöcher
auf die Innenseite des Hinterkopfs, der Hüllenraster auf die Innenseite der Haarkappe dahinter — 712 von 886 Pixeln in 1.jpg, eine Zelle an jedem Auge. Und die Lippe vor dem
Schnurrbart, das Ohr vor dem Haar dahinter sind Haut, die zu Recht vorn liegt (Zellen an Mund und Ohr, in −45° und +45°).
Ansichten: jedes Foto in seiner Kamera und um DREHUNGEN um die Hochachse gedreht (Schrägansichten wie auf der Seite). Zellen von ZELLE_MM; eine Zelle mit mindestens MIN_MM2
durchgestoßener Fläche ist ein Fehler.

    erg = Fotogenesisdurchstoss(ansicht).messen()     # {'zellen': [(Foto, Drehung, Mitte px, mm²)], 'mm2': Summe}
"""
import numpy as np

__all__ = ['Fotogenesisdurchstoss']


class Fotogenesisdurchstoss:
    VOR_MM, GLEICH_MM = 6.0, 0.5
    DREHUNGEN = (0, 45, -45)
    ZELLE_MM, MIN_MM2 = 30.0, 100.0
    HUELLE_NICHT = ('koerper', 'augen')
    KOERPER = ('koerper', 'augen')
    #: Farbklassen der Genesis-Figur (`genesis.farbklassen`, Reihenfolge wie `Figurfarben.KLASSEN`), unter denen ein Körperpunkt bedeckt ist
    BEDECKT = ('haar', 'kleid', 'oberteil', 'unterteil', 'socken')
    FARBKLASSEN = ('haut', 'haar', 'kleid', 'person', 'oberteil', 'unterteil', 'socken')

    def __init__(self, ansicht):
        self.a = ansicht
        self.p = ansicht.p

    def bedeckt(self):
        """(V,) bool je Körperpunkt: Haar oder Kleidung — ohne Farbklassen (ältere Läufe) True = jeder Punkt."""
        fk = (self.a.g or {}).get('farbklassen')
        if not fk:
            return True
        k = self.p.feld(fk, 'u1').astype(np.int64)
        return np.isin(k, [self.FARBKLASSEN.index(n) for n in self.BEDECKT])

    def messen(self, stuecke_von=None, bedeckt=None):
        """`stuecke_von(nr, f)` ersetzt die Stücke (Gegenproben), `bedeckt` (V,) bool die bedeckten Körperpunkte (Vorgabe `bedeckt()`; True = alle)."""
        zellen, summe = [], 0.0
        bedeckt = self.bedeckt() if bedeckt is None else bedeckt
        for nr, f in self.p.fotos():
            teile = stuecke_von(nr, f) if stuecke_von else self.a.stuecke(nr)
            mm_px = self.p.mm_je_px(nr) / self.a.m
            for grad in self.DREHUNGEN:
                gedreht = self.a.gedreht(nr, f, grad, teile) if grad else teile
                koerper = [t for t in gedreht if t[0] in self.KOERPER]
                huellen = [t for t in gedreht if t[0] not in self.HUELLE_NICHT]
                if not any(t[0] == 'koerper' for t in koerper) or not huellen:
                    continue
                rk, rh = self.a.rastern(nr, f, koerper), self.a.rastern(nr, f, huellen)
                d = rk['tiefe'] - rh['tiefe']
                da = (rk['stueck'] >= 0) & (rh['stueck'] >= 0)
                am_koerper = rk['stueck'] == self.a.namen.index('koerper')
                zu = am_koerper if bedeckt is True else am_koerper & bedeckt[np.clip(rk['punkt'], 0, len(bedeckt) - 1)]
                gleich = np.abs(d) < self.GLEICH_MM / 1000
                vor = (d > -self.VOR_MM / 1000) & (d <= -self.GLEICH_MM / 1000) & zu
                stoss = da & (gleich | vor)
                summe += stoss.sum() * mm_px ** 2
                zelle = self.a.zellen(nr, stoss.shape, self.ZELLE_MM)
                b = np.bincount(zelle[stoss], minlength=zelle.max() + 1)
                for z in np.nonzero(b * mm_px ** 2 >= self.MIN_MM2)[0]:
                    yx = np.argwhere(stoss & (zelle == z)).mean(0) / self.a.m
                    zellen.append((f['datei'], grad, (int(yx[1]), int(yx[0])), int(b[z] * mm_px ** 2)))
        return {'zellen': sorted(zellen, key=lambda z: -z[3]), 'mm2': int(summe)}
