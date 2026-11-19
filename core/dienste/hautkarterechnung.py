# -*- coding: utf-8 -*-
u"""Hautkarterechnung — `Hautrechnung.rechnen` (gemeinsam/hautrechnung.js) auf der Grafikkarte des Servers (18.11.2026).

Edgar, 18.11.2026: „Hautverdeckung auf GPU, alles auf GPU!“ Die Haut-Maske rechnete ein Worker im Browser (am feinen Körper 2,8 s im Leerlauf, 7–14 s bei
belasteter CPU, `hautrechnung.js`); jede neue Reglerstellung ist ein neuer Schlüssel im Vorrat, also eine neue Rechnung. Hier dieselbe Rechnung mit
denselben Eingaben (Punkte und voller Index des Körpers in Ruhe, die Stücke mit ihren Einstellungen) und demselben Ergebnis (`maske`, `ersatz`, `hoehe`,
`rand`, `normalen` — nur mit Ersatzstück, nur dann liest der Browser sie —, `einzug`, `randabstaende`, `ms`): Normalen (`Hautkartenormalen`), Maske
(`Hautkartemaske`), Einzug (`Hautkarteeinzug`), Durchsicht. Die Kerne bilden die Schleifen von JS nach, in double ohne FMA (`Hautkartewarphilfe`).
Abweichen kann, was JS in anderer Reihenfolge summiert (Fläche einer Insel) — gemessen im Browser gegen den Worker (`_wegwerf/hautkarte_vergleich.js`).
"""
import time

import torch

from ..daten.feldpaket import Feldpaket
from .hautkarteeinzug import Hautkarteeinzug
from .hautkartegitter import Hautkartegitter
from .hautkartemaske import Hautkartemaske
from .hautkartenormalen import Hautkartenormalen

__all__ = ['Hautkarterechnung']


class Hautkarterechnung:

    @staticmethod
    def _stoff(s, g):
        punkte = s['punkte'].reshape(-1, 3).to(device=g, dtype=torch.float64)
        dreiecke = s['dreiecke'].to(device=g, dtype=torch.int64).reshape(-1, 3)
        zahl = lambda w: None if w is None else float(w)  # noqa: E731
        return {'schluessel': s.get('schluessel'), 'punkte': punkte, 'dreiecke': dreiecke, 'tiefe': zahl(s.get('tiefe')), 'starr': bool(s.get('starr')),
                'nahe': zahl(s.get('nahe')), 'ersatz': bool(s.get('ersatz')), 'nachgeben': zahl(s.get('nachgeben')), 'durchsicht': bool(s.get('durchsicht')),
                'abstand': zahl(s.get('abstand')), 'randabstand': None}

    @classmethod
    def rechnen(cls, eingabe, geraet='cuda'):
        u"""`eingabe`: `{pos, index, stoffe}` (Tensoren, `Feldpaket.entpacken`) → das Ergebnis wie `Hautrechnung.rechnen` (Tensoren und Zahlen)."""
        t0 = time.perf_counter()
        g = torch.device(geraet)
        pos32 = eingabe['pos'].reshape(-1, 3).to(device=g, dtype=torch.float32)
        K = pos32.to(torch.float64)
        KT = eingabe['index'].to(device=g, dtype=torch.int64).reshape(-1, 3)
        n = len(K)
        stoffe = [cls._stoff(s, g) for s in eingabe.get('stoffe') or []]
        N = Hautkartenormalen.rechnen(K, KT)
        ersatz = torch.zeros(n, dtype=torch.uint8, device=g)
        hoehe = torch.full((n,), float('-inf'), dtype=torch.float32, device=g)
        rand = torch.full((n,), float('inf'), dtype=torch.float32, device=g)
        nachgeben = torch.zeros(n, dtype=torch.float32, device=g)
        deckend = [s for s in stoffe if not s['durchsicht']]
        kgitter = Hautkartegitter(K, Hautkartemaske.ZELLE_M)
        maske = Hautkartemaske.verdeckt(K, N, KT, kgitter, deckend, ersatz, hoehe, rand, nachgeben, pos32)
        # Deckende Stücke ohne Ersatzstücke: verdeckte Haut vor dem Stoff darf bis hinter ihn nachgeben (`Hautdurchsicht.anheben`, 18.11.2026, Cyborg Suit)
        tief = Hautkartemaske.durchsicht(K, N, [s for s in deckend if not s['ersatz']], bis_tiefe=True)
        if tief is not None:
            nachgeben = torch.where((maske != 0) & (tief > nachgeben), tief, nachgeben)
        nachgeben = cls.inseln_erben(nachgeben, maske, KT)                 # Inselpunkte ohne Stück (`Hautdurchsicht.inselnErben`, 18.11.2026)
        einzug = Hautkarteeinzug.rechnen(K, N, KT, maske, deckend, nachgeben)
        durch = Hautkartemaske.durchsicht(K, N, [s for s in stoffe if s['durchsicht']])
        if durch is not None:
            nur = (maske == 0) & (durch > 0)
            einzug['werte'] = torch.where(nur[:, None], (-durch.to(torch.float64)[:, None] * N).to(torch.float32), einzug['werte'])
            einzug['gesetzt'] = einzug['gesetzt'] + nur.sum()
        mit_ersatz = any(s['ersatz'] for s in stoffe)
        zahlen = torch.stack([einzug['gesetzt'], einzug['geschnappt'], einzug['band']]).tolist()      # eine Abholung für die drei Zahlen
        return {'maske': maske, 'ersatz': ersatz, 'hoehe': hoehe, 'rand': rand, 'normalen': N.reshape(-1) if mit_ersatz else None,
                'einzug': {'werte': einzug['werte'].reshape(-1), 'gesetzt': int(zahlen[0]), 'geschnappt': int(zahlen[1]), 'band': int(zahlen[2]),
                           'weg': einzug['weg']},
                'randabstaende': [s['randabstand'] for s in stoffe], 'ms': round((time.perf_counter() - t0) * 1000), 'aufKarte': True}

    #: wie `Hautdurchsicht.RUNDEN`
    RUNDEN = 40

    @classmethod
    def inseln_erben(cls, nachgeben, maske, KT):
        u"""`Hautdurchsicht.inselnErben`: verdeckte Punkte ohne `nachgeben` erben den größten Wert ihrer Nachbarn über die Dreiecke, Runde für Runde."""
        offen = (maske != 0) & ~(nachgeben > 0)
        if not bool(offen.any()):
            return nachgeben
        ecken = KT.reshape(-1)
        for _ in range(cls.RUNDEN):
            w = nachgeben[KT].amax(dim=1).repeat_interleave(3)
            neu = torch.zeros_like(nachgeben).scatter_reduce(0, ecken, w, reduce='amax', include_self=True)
            besser = offen & (neu > nachgeben)
            if not bool(besser.any()):
                break
            nachgeben = torch.where(besser, neu, nachgeben)
        return nachgeben

    @classmethod
    def aus_bytes(cls, roh):
        u"""Bytes der Anfrage (gzip, Feldpaket) → gepackte Antwort (gzip, Feldpaket)."""
        return Feldpaket.packen(cls.rechnen(Feldpaket.entpacken(roh)))
