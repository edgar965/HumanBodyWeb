# -*- coding: utf-8 -*-
"""Makehumangenitalquelle — MakeHumans Genitalhelfer und seine drei Ziele, als Käfig im Daz-Format (18.10.2026).

Gelesen (nie beschrieben) aus `MakeHuman/makehuman/data` (MakeHuman 1.3.0, CC0):

    3dobjs/base.obj           Gruppe `helper-genital` von hm08: 200 Punkte, 182 Vierecke, 34 offene Kanten (der Ansatz am Körper), UV in einem
                              kleinen Feld (u 0,781–0,803, v 0,966–0,992) — gemessen 18.10.2026, `ProjektTemp/_wegwerf/mh_genital_probe.py`
    targets/genitals/*.target `penis-length|circ|testicles-decr|incr`: 49/105/78 Punkte, alle im Helfer; Länge+ bis 16,2 cm

Mehr Genitalien hat MakeHuman nicht: der Genital-Proxy der Community-Seite ist nicht mehr zu laden (`.claude/rules/recherche-modelle-internet.md`).
MakeHuman rechnet in Dezimetern (`Mhbasisnetz.MASSSTAB`). Der Käfig kommt im Format von `G9netzstufe` heraus (`polys` je Viereck
`[Gruppe, Material, a, b, c, d]`, `uvs` je Punkt, `ueber` = `{(Fläche, Punkt): UV}` für Ecken an einer UV-Naht) — so unterteilt er wie jedes Daz-Netz.
"""
import numpy as np

__all__ = ['Makehumangenitalquelle']


class Makehumangenitalquelle:
    GRUPPE = 'helper-genital'
    #: `(Endung des Reglers, Ziel, Anzeige)`; jede Seite eines Ziels ein eigener Regler 0 … 1 (ein Stückmorph ist linear, MakeHumans Seiten sind verschieden).
    ZIELE = (('laenge_plus', 'penis-length-incr', 'Länge +'), ('laenge_minus', 'penis-length-decr', 'Länge −'),
             ('umfang_plus', 'penis-circ-incr', 'Umfang +'), ('umfang_minus', 'penis-circ-decr', 'Umfang −'),
             ('hoden_plus', 'penis-testicles-incr', 'Hoden +'), ('hoden_minus', 'penis-testicles-decr', 'Hoden −'))

    def __init__(self):
        from MakeHuman.basisnetz import Mhbasisnetz

        self.massstab = Mhbasisnetz.MASSSTAB
        self.nummern, self.vierecke, self.uv_ecken = self._lesen(self._obj())

    def _obj(self):
        from MakeHuman.basisnetz import Mhbasisnetz
        return Mhbasisnetz.pfad()

    def _lesen(self, pfad):
        """`(nummern, vierecke, uv_ecken)`: hm08-Nummern der Helferpunkte, Vierecke darauf (lokal), UV je Ecke `(F, 4, 2)`."""
        uv, flaechen, gruppe = [], [], None
        with open(pfad, encoding='utf-8', errors='replace') as datei:
            for zeile in datei:
                if zeile.startswith('vt '):
                    uv.append([float(x) for x in zeile.split()[1:3]])
                elif zeile.startswith('g '):
                    gruppe = zeile[2:].strip()
                elif zeile.startswith('f ') and gruppe == self.GRUPPE:
                    ecken = [e.split('/') for e in zeile.split()[1:]]
                    flaechen.append([(int(e[0]) - 1, int(e[1]) - 1) for e in ecken])
        if not flaechen or any(len(f) != 4 for f in flaechen):
            raise ValueError('%s: Gruppe %s fehlt oder hat Flächen, die keine Vierecke sind' % (pfad, self.GRUPPE))
        roh = np.asarray(flaechen, dtype=np.int64)                       # (F, 4, 2): Punkt, UV
        nummern, lokal = np.unique(roh[:, :, 0], return_inverse=True)
        uv_ecken = np.asarray(uv, dtype=np.float64)[roh[:, :, 1]]
        return nummern, lokal.reshape(-1, 4), uv_ecken

    def kaefig_daz(self):
        """`(polys, uvs, ueber)` für `G9netzstufe`; UV auf das Feld 0 … 1 gezogen (Seitenverhältnis bleibt), damit eine gebackene Karte Auflösung hat."""
        lo = self.uv_ecken.reshape(-1, 2).min(axis=0)
        weite = float(np.ptp(self.uv_ecken.reshape(-1, 2), axis=0).max()) or 1.0
        uv_ecken = (self.uv_ecken - lo) / weite
        uvs = np.zeros((len(self.nummern), 2))
        gesetzt = np.zeros(len(self.nummern), dtype=bool)
        extra, ueber = [], {}
        for f, (viereck, uv4) in enumerate(zip(self.vierecke, uv_ecken, strict=True)):
            for punkt, t in zip(viereck, uv4, strict=True):
                if not gesetzt[punkt]:
                    uvs[punkt], gesetzt[punkt] = t, True
                elif np.abs(uvs[punkt] - t).max() > 1e-9:            # UV-Naht: die Ecke bekommt ihren eigenen UV-Eintrag
                    extra.append(t)
                    ueber[(f, int(punkt))] = len(self.nummern) + len(extra) - 1
        polys = [[0, 0] + [int(p) for p in viereck] for viereck in self.vierecke]
        return polys, np.vstack([uvs] + ([np.asarray(extra)] if extra else [])), ueber

    def ziel(self, name):
        """`(P, 3)` Verschiebung der Helferpunkte durch das Ziel `name` in MakeHumans Einheiten (dm); Punkte außerhalb des Helfers: `ValueError`."""
        pfad = self._ordner_ziele() / (name + '.target')
        d = np.zeros((len(self.nummern), 3))
        stelle = {int(n): i for i, n in enumerate(self.nummern)}
        for zeile in pfad.read_text(encoding='utf-8').splitlines():
            teile = zeile.split()
            if not teile or teile[0].startswith('#'):
                continue
            if int(teile[0]) not in stelle:
                raise ValueError('%s verschiebt hm08-Punkt %s außerhalb des Helfers' % (pfad.name, teile[0]))
            d[stelle[int(teile[0])]] = [float(x) for x in teile[1:4]]
        return d

    @staticmethod
    def _ordner_ziele():
        from MakeHuman.pfade import Mhpfade
        return Mhpfade.ziele() / 'genitals'
