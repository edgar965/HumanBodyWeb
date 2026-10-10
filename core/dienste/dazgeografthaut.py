# -*- coding: utf-8 -*-
"""Dazgeografthaut — das Loch, das ein Daz-Geograft in die Haut der Grundfigur schneidet (10.10.2026).

Das Geograft nennt die Käfigflächen der Figur, die unter ihm entfallen (`graft.hidden_polys`, beim männlichen 180). Der Browser rechnet aber
auf Stufe 1 (Catmull-Clark, 201.248 Dreiecke — dieselbe Folge wie `Blendimportschamloch`): jede Käfigfläche wird dort zu acht Dreiecken (ein Viereck
vier Vierecke), und ihre Reihenfolge folgt NICHT der der Käfigflächen — gemessen 10.10.2026: `8·p … 8·p+7` liegt im Median 353 mm neben der
Fläche `p`. Zugeordnet wird deshalb über die UV: ein Dreieck der Stufe 1 gehört zur Käfigfläche, in deren UV-Viereck seine UV-Mitte liegt (die Kinder einer
Fläche liegen im UV-Viereck der Mutter), nach einer Vorauswahl über die Lage (UV-Inseln verschiedener Kacheln überlagern sich).
"""
import numpy as np

__all__ = ['Dazgeografthaut']


class Dazgeografthaut:
    #: Vorauswahl: Dreiecke, deren Mitte höchstens so weit (m) von der Mitte der Käfigfläche liegt.
    SUCHE_M = 0.04
    #: Toleranz der UV-Prüfung (Anteil der Seitenlänge des UV-Vierecks).
    TOL = 1e-6

    @staticmethod
    def grundfigur(regler=None):
        """`{kaefig, punkte, dreiecke, uv, polys}` — die Grundfigur (alle Regler 0) auf Stufe 1: Käfig und Haut in Metern, Y oben, Füße 0.
        Mit `regler` (die Regler eines gespeicherten Modells, `figur.regler`) die Figur dieses Modells in Ruhe — dieselbe Topologie, andere Lage."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        kaefig, _, _ = G9reglerableitung.lage(G9formung(dict(regler or {})))
        kaefig = np.asarray(kaefig, dtype=np.float64)
        stufe = G9basisnetz.holen().netzstufe(1)
        punkte = np.asarray(stufe.punkte(kaefig), dtype=np.float64)
        dreiecke = np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3)
        kachel = np.zeros(len(dreiecke), dtype=np.int64)          # UDIM-Kachel je Dreieck (`Blendimportlage.genesis`)
        for g in stufe.gruppen:
            ab = int(g['index_ab']) // 3
            kachel[ab:ab + int(g['dreiecke'])] = int(g['kachel'])
        return {'kaefig': kaefig, 'punkte': punkte, 'dreiecke': dreiecke, 'uv': np.asarray(stufe.uv, dtype=np.float64), 'kachel': kachel,
                'polys': G9basisnetz.holen().netzstufe(0).polys}

    @classmethod
    def loch(cls, figur, versteckt):
        """`(maske, bericht)`: bool je Dreieck der Stufe 1 — unter dem Geograft — und wie viele Dreiecke je Käfigfläche zugeordnet wurden."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.dson import G9dson
        from Genesis9.pfade import G9pfade
        from Genesis9.unterteilung import G9unterteilung
        from scipy.spatial import cKDTree

        polys, kaefig, dreiecke = figur['polys'], figur['kaefig'], figur['dreiecke']
        uvs, ueber = G9basisnetz.uvsatz(G9dson.lesen(G9pfade.figur()).geometrie().get('default_uv_set'))
        ecken_uv = G9unterteilung.uv_ecken(G9unterteilung.flaechen(polys), polys, uvs, ueber)
        mitte = figur['punkte'][dreiecke].mean(axis=1)
        mitte_uv = figur['uv'][dreiecke].mean(axis=1)
        baum = cKDTree(mitte)
        maske = np.zeros(len(dreiecke), dtype=bool)
        je_flaeche = {}
        for p in versteckt.tolist():
            ecken = [int(i) for i in polys[p][2:]]
            kandidaten = np.asarray(baum.query_ball_point(kaefig[ecken].mean(axis=0), cls.SUCHE_M), dtype=np.int64)
            innen = cls._im_viereck(mitte_uv[kandidaten], ecken_uv[p][:len(ecken)])
            maske[kandidaten[innen]] = True
            je_flaeche[p] = int(innen.sum())
        zahlen = sorted(set(je_flaeche.values()))
        return maske, {'flaechen': int(len(versteckt)), 'dreiecke': int(maske.sum()), 'je_flaeche': zahlen,
                       'ohne': [p for p, n in je_flaeche.items() if n == 0]}

    @classmethod
    def _im_viereck(cls, punkte, ecken):
        """Bool je Punkt: liegt er im (konvexen) Vieleck `ecken`? Alle Kreuzprodukte tragen dasselbe Vorzeichen."""
        n = len(ecken)
        kante = np.roll(ecken, -1, axis=0) - ecken
        seiten = np.stack([kante[k, 0] * (punkte[:, 1] - ecken[k, 1]) - kante[k, 1] * (punkte[:, 0] - ecken[k, 0]) for k in range(n)])
        toleranz = cls.TOL * float(np.abs(kante).max())
        return (seiten >= -toleranz).all(axis=0) | (seiten <= toleranz).all(axis=0)
