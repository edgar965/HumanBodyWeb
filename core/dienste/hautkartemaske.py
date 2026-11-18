# -*- coding: utf-8 -*-
u"""Hautkartemaske — `Hautmaske.verdeckt` (mit `Hautmaskeersatz`, `Maskeninseln`) und `Hautdurchsicht` auf der Karte (18.11.2026, `Hautkarterechnung`).

Je Stück wie JS, in derselben Reihenfolge: Randpunkte (Kanten mit einem Dreieck) und Nachbarn, lockere Randpunkte (`locker`), `RANDRINGE` Ringe um sie
gesperrt (starr: keine), die erlaubten Dreiecke je Punkt, dann je Körperpunkt der Kern `stueck`; ein Ersatzstück danach mit seinem Randabstand
(`Stueckrand.randabstand`: Punkte auf 1e-5 m verschweißt, Rand = Kanten mit einem Dreieck, Wege über das Netz bis `RING_M` + 4 mm) und dem Kern
`ersatz`. Zuletzt die Inseln. Konstanten wie in `hautmaske.js`, `hautmaskeersatz.js`, `hautmaskegeometrie.js`, `hautdurchsicht.js`.
"""
import torch
import warp as wp

from . import hautkartewarpmaske as kern
from .hautkartegitter import Hautkartegitter
from .hautkarteinseln import Hautkarteinseln
from .hautkartewege import Hautkartewege

__all__ = ['Hautkartemaske']


def _a(t, typ):
    return wp.from_torch(t.contiguous(), dtype=typ)


class Hautkartemaske:
    ABSTAND_M = 0.025
    TIEFE_M = 0.005
    RANDRINGE = 2
    ENG_M = 0.004
    INSEL_MAX = 200
    INSEL_FLAECHE_M2 = 0.005
    NAHE_M = 0.012
    ZELLE_M = 0.03
    ERSATZ_RADIUS_M = 0.004
    ERSATZ_SENKUNG_M = 0.009
    RING_M = 0.03
    LUFT_M = 0.001

    @staticmethod
    def _strom(g):
        return wp.stream_from_torch(torch.cuda.current_stream(g))

    @staticmethod
    def huelle(S, rand):
        lo, hi = S.min(0).values - rand, S.max(0).values + rand
        return torch.cat([lo, hi])

    @classmethod
    def _netz(cls, S, ST, alle_erlaubt=False, locker=None, ringe=0):
        u"""(Nachbarn-CSR, erlaubte Dreiecke je Punkt-CSR) eines Stücks — erlaubt: keine Ecke in `ringe` Ringen um `locker`."""
        n, g = len(S), S.device
        einzeln, zahl, _stelle = Hautkartegitter.kanten(ST, n)
        ka, kb = einzeln // n, einzeln % n
        nach_a, nach_z = Hautkartegitter.csr(torch.cat([ka, kb]), torch.cat([kb, ka]), n)
        rand = torch.zeros(n, dtype=torch.bool, device=g)
        einmal = zahl == 1
        rand[ka[einmal]] = True
        rand[kb[einmal]] = True
        ok = torch.ones(len(ST), dtype=torch.bool, device=g)
        if not alle_erlaubt and locker is not None:
            gesperrt = locker.clone()
            for _ in range(ringe):
                neu = gesperrt.clone()
                neu[kb[gesperrt[ka]]] = True
                neu[ka[gesperrt[kb]]] = True
                gesperrt = neu
            ok = ~(gesperrt[ST[:, 0]] | gesperrt[ST[:, 1]] | gesperrt[ST[:, 2]])
        nummer = torch.arange(len(ST), device=g)
        ecke = ST[ok].reshape(-1)
        inz_a, inz_z = Hautkartegitter.csr(ecke, nummer[ok].repeat_interleave(3), n)
        return (nach_a, nach_z), (inz_a, inz_z), rand

    @classmethod
    def verdeckt(cls, K, N, KT, kgitter, stoffe, ersatz, hoehe, rand, nachgeben, pos32):
        u"""(n,) uint8 Maske; `ersatz`, `hoehe`, `rand`, `nachgeben` werden gefüllt; je Ersatzstück `stoff['randabstand']`."""
        n, g = len(K), K.device
        maske = torch.zeros(n, dtype=torch.uint8, device=g)
        strom = cls._strom(g)
        for stoff in stoffe:
            S, ST = stoff['punkte'], stoff['dreiecke']
            if not len(S) or not len(ST):
                continue
            starr = bool(stoff['starr'])
            ringe, nahe = (0, stoff['nahe'] if stoff['nahe'] is not None else cls.NAHE_M) if starr else (cls.RANDRINGE, 0.0)
            tiefe = max(cls.TIEFE_M, stoff['tiefe'] or 0.0)
            abstand = max(cls.ABSTAND_M, stoff.get('abstand') or 0.0)       # je Stück wie `hautmaske.js` (18.11.2026, `Bauart.deckAbstandM`)
            weite = max(abstand, tiefe, cls.NAHE_M)
            wert = float(stoff['nachgeben'] or 0.0)
            (nach_a, nach_z), _inz, randpunkt = cls._netz(S, ST)
            locker = torch.zeros(len(S), dtype=torch.uint8, device=g)
            rnr = torch.nonzero(randpunkt).reshape(-1)
            if len(rnr):
                wp.launch(kern.locker, dim=len(rnr), inputs=[_a(S, wp.float64), _a(rnr, wp.int64), _a(K, wp.float64), _a(N, wp.float64),
                                                             _a(kgitter.schl, wp.int64), _a(kgitter.folge, wp.int64), cls.ZELLE_M, cls.ENG_M,
                                                             _a(locker, wp.uint8)], stream=strom)
            _nach, (inz_a, inz_z), _r = cls._netz(S, ST, locker=locker.bool(), ringe=ringe)
            sg = Hautkartegitter(S, cls.ZELLE_M)
            wp.launch(kern.stueck, dim=n, inputs=[_a(K, wp.float64), _a(N, wp.float64), _a(S, wp.float64), _a(ST, wp.int64), _a(sg.schl, wp.int64),
                                                  _a(sg.folge, wp.int64), cls.ZELLE_M, _a(cls.huelle(S, weite), wp.float64), weite * weite, tiefe,
                                                  abstand, float(nahe), _a(nach_a, wp.int64), _a(nach_z, wp.int64), _a(inz_a, wp.int64),
                                                  _a(inz_z, wp.int64), wert, _a(maske, wp.uint8), _a(nachgeben, wp.float32)], stream=strom)
            if stoff['ersatz']:
                stoff['randabstand'] = cls.randabstand(S, ST, cls.RING_M + 0.004)
                wp.launch(kern.ersatz, dim=n, inputs=[_a(K, wp.float64), _a(N, wp.float64), _a(S, wp.float64), _a(sg.schl, wp.int64),
                                                      _a(sg.folge, wp.int64), cls.ZELLE_M, _a(cls.huelle(S, max(cls.ABSTAND_M, tiefe)), wp.float64),
                                                      cls.ABSTAND_M, tiefe, cls.ERSATZ_RADIUS_M ** 2, cls.ERSATZ_SENKUNG_M ** 2,
                                                      _a(stoff['randabstand'], wp.float64), _a(maske, wp.uint8), _a(ersatz, wp.uint8),
                                                      _a(hoehe, wp.float32), _a(rand, wp.float32)], stream=strom)
        maske, _zu = Hautkarteinseln.schliessen(maske, KT, cls.INSEL_MAX, pos32, cls.INSEL_FLAECHE_M2)
        return maske

    @staticmethod
    def _schweiss(S):
        u"""Je Punkt der erste Punkt gleicher Lage auf 1e-5 m — `Math.round` wie JS (halb aufwärts)."""
        x = S * 1e5
        f = torch.floor(x)
        r = f + ((x - f) >= 0.5).to(f.dtype)
        return Hautkartegitter.gleiche_zeilen(r)

    @classmethod
    def randabstand(cls, S, ST, reichweite):
        u"""`Stueckrand.randabstand`: je Punkt der Weg über das Netz zum nächsten Randpunkt (verschweißt), höchstens `reichweite`."""
        n, g = len(S), S.device
        sw = cls._schweiss(S)
        t = sw[ST]
        a = torch.cat([t[:, 0], t[:, 1], t[:, 2]])
        b = torch.cat([t[:, 1], t[:, 2], t[:, 0]])
        echt = a != b
        schl = torch.minimum(a, b)[echt] * n + torch.maximum(a, b)[echt]
        einzeln, zahl = torch.unique(schl, return_counts=True)
        quelle = torch.zeros(n, dtype=torch.bool, device=g)
        einmal = einzeln[zahl == 1]
        quelle[einmal // n] = True
        quelle[einmal % n] = True
        return Hautkartewege.wege(S, ST, quelle, reichweite)

    @classmethod
    def durchsicht(cls, K, N, stoffe, bis_tiefe=False):
        u"""`Hautdurchsicht.alle`: je Körperpunkt die nötige Tiefe unter den Stücken (float32) — None ohne solche. Höchstens bis `nachgeben` hinter die
        tiefste Lage, mit `bis_tiefe` (deckende Stücke, `Hautdurchsicht.anheben`) bis zur `tiefe` des Stücks hinter die nächste."""
        liste = [s for s in stoffe if len(s['punkte']) and len(s['dreiecke'])]
        if not liste:
            return None
        n, g = len(K), K.device
        aus = torch.zeros(n, dtype=torch.float32, device=g)
        strom = cls._strom(g)
        for s in liste:
            tiefe = max(cls.TIEFE_M, s['tiefe'] or 0.0)
            grenze = tiefe if bis_tiefe else max(0.0, float(s['nachgeben'] or 0.0))
            if not grenze:
                continue
            S, ST = s['punkte'], s['dreiecke']
            weite = max(tiefe, cls.ABSTAND_M)
            (nach_a, nach_z), (inz_a, inz_z), _r = cls._netz(S, ST, alle_erlaubt=True)
            sg = Hautkartegitter(S, cls.ZELLE_M)
            wp.launch(kern.durch, dim=n, inputs=[_a(K, wp.float64), _a(N, wp.float64), _a(S, wp.float64), _a(ST, wp.int64), _a(sg.schl, wp.int64),
                                                 _a(sg.folge, wp.int64), cls.ZELLE_M, _a(cls.huelle(S, weite), wp.float64), weite * weite, tiefe,
                                                 cls.LUFT_M, grenze, _a(nach_a, wp.int64), _a(nach_z, wp.int64), _a(inz_a, wp.int64), _a(inz_z, wp.int64),
                                                 int(bis_tiefe), _a(aus, wp.float32)], stream=strom)
        return aus
