# -*- coding: utf-8 -*-
"""Dazgeograftmorphbasis — die übernommenen Regler `sch_*` vom angepassten Daz-Stück auf das Basis-Stück „Daz Anatomie Frau" legen (10.10.2026).

Edgar: „Portiere auf jeden Fall unsere Morphs, sowohl für weiblich als auch für männlich". Das Basis-Stück (Grundfigur, alle Daz-Charaktere) und das an eine Scham angepasste Stück
(`Dazgeograftangepasst`) kommen aus demselben Geograft: dieselben Punkte der Stufe 1 (4.211 bei der Frau) in derselben Reihenfolge — die Naht (`Blendimportschamnaht`) verschiebt sie nur
und hängt die Ringecken, die dem Rand fehlen, HINTEN an (Basis 17, angepasst 41–66 Punkte). Die Entsprechung ist deshalb Punkt für Punkt über die Nummer: Punkt `i` des Basis-Stücks ↔ Punkt `i`
des angepassten, solange `i` unter den Stufe-1-Punkten liegt; die angehängten Ringecken haben kein Gegenstück (Delta 0, sie sitzen auf der Haut). Ein Regler des angepassten Stücks
(`Dazgeograftmorphuebertrag`: Deltas der alten Scham) gilt damit auch für das Basis-Stück, das heißt auf demselben Teil der Anatomie (Haube, Lippen, Eingang, Damm). Die Vektoren werden
unverändert übernommen (beide Stücke liegen in der Lage der Figur: Y oben, +z vorn); `pruefen` misst bei den Reglern „entlang der Normale" den Winkel zur Fläche beider Stücke.

GEÄNDERT 11.10.2026: bisher verlangte die Klasse, dass 85 % der DREIECKE dieselben Punktnummern tragen, und nahm die Zuordnung Ecke für Ecke. Das hing am Zufall: die Naht ersetzt beim Einfügen
der Ringecken ein Dreieck durch mehrere und verschiebt damit die Dreiecksnummern danach — bei Nachformung 0,2 stimmten 90,5 % (zufällig), bei 0 und 0,4 nur 45–46 %, und die Ecke-für-Ecke-
Zuordnung gab je Basis-Punkt bis zu neun verschiedene Partner (Spanne bis 140 mm). Die Punktnummern der Stufe-1-Punkte dagegen sind in beiden Stücken gleich (gemessen: Punkt i ↔ Punkt i, Abstand
nach Abzug der Mittellage Median 9 mm, p99 16 mm gegen 29 mm bei zufälliger Paarung); geprüft wird jetzt, dass die Punkte gleich viele Dreiecke tragen (`MIN_VALENZ`).
"""
import json
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Dazgeograftmorphbasis']


class Dazgeograftmorphbasis:
    #: Mindestanteil der Stufe-1-Punkte, die in beiden Stücken in gleich vielen Dreiecken stehen (die Naht ändert das nur am Rand), sonst gelten die Stücke nicht als dasselbe Geograft.
    MIN_VALENZ = 0.95
    #: Ein Punkt gilt als Ringecke, wenn er höchstens so weit (m) von ihr liegt.
    LAGE_M = 1e-7

    def __init__(self, angepasst, basis):
        """`angepasst`, `basis`: Kennungen (`cute_girl_daz_scham`, `daz_anatomie_frau`)."""
        from Genesis9.kleidmorphe import G9kleidmorphe

        from .dazgeograftmorphuebertrag import Dazgeograftmorphuebertrag as U

        self.angepasst, self.basis = angepasst, basis
        teile_a, kaefige_a, _y0, _y1, _mitte, eintrag_a = G9kleidmorphe.kaefige(angepasst)
        self.teile_b, kaefige_b, _y0, _y1, _mitte, eintrag_b = G9kleidmorphe.kaefige(basis)
        if len(teile_a) != 1 or len(self.teile_b) != 1:
            raise ValueError('nur für Stücke aus einem Teil')
        self.p_a, self.p_b = kaefige_a[0], kaefige_b[0]
        da, db = U._dreiecke(teile_a[0][0].polys), U._dreiecke(self.teile_b[0][0].polys)
        if da.shape != db.shape:
            raise ValueError('verschiedene Zahl der Dreiecke (%d / %d): nicht dasselbe Geograft' % (len(da), len(db)))
        #: Zahl der Punkte der Stufe 1 (vor den angehängten Ringecken) — so weit gilt „Punkt i ↔ Punkt i".
        self.stufe = min(self._stufe_punkte(self.p_a, eintrag_a), self._stufe_punkte(self.p_b, eintrag_b))
        valenz_a, valenz_b = (np.bincount(d.ravel(), minlength=n)[:self.stufe] for d, n in ((da, len(self.p_a)), (db, len(self.p_b))))
        self.gleich = float((valenz_a == valenz_b).mean())
        if self.gleich < self.MIN_VALENZ:
            raise ValueError('nur %.0f %% der Punkte der Stufe 1 tragen in beiden Stücken gleich viele Dreiecke (nötig %.0f %%)' % (self.gleich * 100, self.MIN_VALENZ * 100))
        self.dreiecke_a, self.dreiecke_b = da, db
        self.zu = np.full(len(self.p_b), -1, dtype=np.int64)
        self.zu[:self.stufe] = np.arange(self.stufe)
        from Genesis9.schammorphe import G9schammorphe

        #: Flächennormalen (nach außen, wie die Regler sie rechnen) beider Stücke — für die Regler „entlang der Normale".
        self.n_a = G9schammorphe.normalen(self.p_a, teile_a[0][0].polys)
        self.n_b = G9schammorphe.normalen(self.p_b, self.teile_b[0][0].polys)

    @classmethod
    def _stufe_punkte(cls, punkte, eintrag):
        """Zahl der Punkte vor dem Schwanz aus Ringecken: die Naht hängt die Ecken des Rings, die dem Rand fehlen, hinten an (`Blendimportschamnaht._einfuegen`)."""
        from Genesis9.stueckersatz import G9stueckersatz

        ring = np.asarray((G9stueckersatz.loch_fuer(eintrag).get('ring') or {}).get('lage') or [], dtype=np.float64).reshape(-1, 3)
        if not len(ring):
            raise ValueError('das Stück hat kein Loch mit Ring: keine Naht, keine Zuordnung')
        auf_ring = np.zeros(len(punkte), dtype=bool)
        from scipy.spatial import cKDTree

        auf_ring[np.unique(np.concatenate([np.asarray(x, dtype=np.int64) for x in cKDTree(punkte).query_ball_point(ring, cls.LAGE_M)] or [np.zeros(0, dtype=np.int64)]))] = True
        ende = len(punkte)
        while ende > 0 and auf_ring[ende - 1]:
            ende -= 1
        return ende

    def _voll(self, kennung, name, n):
        from Genesis9.kleidmorphe import G9kleidmorphe

        felder = G9kleidmorphe.deltas(kennung, name)
        if not felder:
            raise ValueError('Regler %s/%s nicht lesbar' % (kennung, name))
        d = np.zeros((n, 3))
        for nummern, deltas in felder.values():
            d[np.asarray(nummern, dtype=np.int64)] = deltas
        return d

    def uebertragen(self, name):
        """Den Regler `name` vom angepassten Stück auf das Basis-Stück übertragen und ablegen → Steckbrief."""
        from Genesis9.kleidmorphe import G9kleidmorphe

        from .dazgeograftmorphuebertrag import Dazgeograftmorphuebertrag as U

        zusatz = {'uebernommen_von': self.angepasst}
        try:
            with open(G9kleidmorphe._pfad(self.angepasst, name, '.json'), encoding='utf-8') as datei:
                zusatz['scham'] = json.load(datei).get('scham')
        except (OSError, ValueError) as fehler:
            logger.warning('Übernahme %s: Steckbrief von %s/%s nicht lesbar (%s)', self.basis, self.angepasst, name, fehler)
        d_a = self._voll(self.angepasst, name, len(self.p_a))
        hat = (self.zu >= 0)[:, None]
        if (zusatz.get('scham') or {}).get('art') in U.NORMAL_ARTEN:      # als Betrag entlang der Normale des Basis-Stücks
            betrag = np.einsum('ij,ij->i', d_a, self.n_a)[np.maximum(self.zu, 0)]
            d_b = np.where(hat, betrag[:, None] * self.n_b, 0.0)
        else:
            d_b = np.where(hat, d_a[np.maximum(self.zu, 0)], 0.0)
        return G9kleidmorphe.ablegen(self.basis, name, [f.kennung for f, _lage in self.teile_b], [d_b], zusatz)

    def alle(self, namen):
        """Alle Regler `namen` übertragen → `(uebernommen, gescheitert)`."""
        uebernommen, gescheitert = [], {}
        for name in namen:
            try:
                self.uebertragen(name)
                uebernommen.append(name)
            except (ValueError, OSError, KeyError, IndexError) as fehler:
                gescheitert[name] = str(fehler)[:160]
                logger.warning('Übernahme auf %s/%s gescheitert: %s', self.basis, name, fehler)
        return uebernommen, gescheitert

    def pruefen(self, namen):
        """Je Regler `{bewegt, weg_max_mm, normal_grad_basis, normal_grad_angepasst}` — die letzten zwei nur bei Reglern „entlang der Normale": Winkel (Grad, Median) zwischen Delta und
        Flächennormale an den bewegten Punkten (0 = genau entlang; das Vorzeichen zählt nicht)."""
        import trimesh

        normalen_b = np.asarray(trimesh.Trimesh(self.p_b, self.dreiecke_b, process=False).vertex_normals)
        normalen_a = np.asarray(trimesh.Trimesh(self.p_a, self.dreiecke_a, process=False).vertex_normals)
        aus = {}
        for name in namen:
            try:
                d_b = self._voll(self.basis, name, len(self.p_b))
                d_a = self._voll(self.angepasst, name, len(self.p_a))
                with open(self._steckbrief(name), encoding='utf-8') as datei:
                    art = ((json.load(datei).get('scham') or {}).get('art'))
            except (ValueError, OSError, KeyError) as fehler:
                aus[name] = {'fehler': str(fehler)[:120]}
                continue
            weg = np.linalg.norm(d_b, axis=1) * 1000.0
            eintrag = {'bewegt': int((weg > 0.05).sum()), 'weg_max_mm': round(float(weg.max()), 2)}
            if art in ('normal', 'kraeuseln'):
                eintrag['normal_grad_basis'] = self._winkel(d_b, normalen_b)
                eintrag['normal_grad_angepasst'] = self._winkel(d_a, normalen_a)
            aus[name] = eintrag
        return aus

    def _steckbrief(self, name):
        from Genesis9.kleidmorphe import G9kleidmorphe

        return G9kleidmorphe._pfad(self.basis, name, '.json')

    @staticmethod
    def _winkel(delta, normalen):
        laenge = np.linalg.norm(delta, axis=1)
        wahl = laenge > 5e-5
        if not wahl.any():
            return None
        cos = np.abs(np.einsum('ij,ij->i', delta[wahl], normalen[wahl]) / laenge[wahl])
        return round(float(np.degrees(np.arccos(np.clip(np.median(cos), 0.0, 1.0)))), 1)
