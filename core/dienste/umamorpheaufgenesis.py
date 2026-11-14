# -*- coding: utf-8 -*-
u"""Umamorpheaufgenesis — die UMA-Regler als Genesis-9-Morphs bauen (17.10.2026).

Edgar, 17.10.2026: „du solltest ALLE Morphs und Regler aus den anderen Projekten portieren und als neue Morphs fuer Genesis nachbauen“.

WAS UMA TUT: Alle 62 DNA-Regler (Koerper 28, Gesicht 34) und die drei Kinder-Posen skalieren, verschieben und drehen KNOCHEN; die Haut folgt der Bindung. Es gibt keine
Verschiebungsziele. Hier laufen dieselben Knochenoperationen auf Genesis 9 (`G9knochenfeld`: Knochen → Haut → Verschiebung je Kaefigpunkt, dazu EXAKTE Gelenkversaetze) —
ein UMA-Regler wird damit ein Morph wie die anderen Familien. Die Zuordnung UMA-Knochen → Genesis-Knochen: `Umaabbildung`; die Werte aus den Assets: `Umaregler`.

DER REGLER: DNA-Wert `v` ∈ [0, 1], Vorgabe 0,5 (bei den Pose-Reglern mit Abbildung 0…1 steht die Vorgabe also auf Pose-Gewicht 0,5). Plus-Seite = Feld(v=1) − Feld(Vorgabe),
Minus-Seite = Feld(v=0) − Feld(Vorgabe), jede mit der Kurve des Effekts (`Umaregler.wert`). Die Kinder-Posen: Gewicht 1, nur Plus.

WAS DAS NICHT IST: eine Messung gegen UMA. Die Achsen der UMA-Knochen stehen in einer Unity-Binaerdatei (siehe `Umaabbildung`, Annahme), Genesis hat andere Haut-Gewichte als das UMA-Netz,
und die „Adjust“-Huellen heissen hier „Haut des Knochens ohne seine Nachfahren“. Das ist eine Uebertragung der Knochenvorgaben, kein Abbild von UMAs Netz — der Steckbrief sagt es
(`quelle`). Ob Kind (UMA 3) die richtige Groesse trifft, steht im Bestand (`hoehe_verhaeltnis`).

Bauen: `manage.py umamorphe_bauen`.
"""
import logging
import re
import time

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from Genesis9.knochenfeld import G9knochenfeld
from Genesis9.umamorphe import G9umamorphe

from .umaabbildung import Umaabbildung
from .umaregler import Umaregler

logger = logging.getLogger('core')

__all__ = ['Umamorpheaufgenesis']


class Umamorpheaufgenesis:
    u"""Alle UMA-Regler und Kinder-Posen als Genesis-9-Morphs."""

    #: Unity (links-haendig, x = rechts der Figur) → Genesis (x = links): die x-Achse kehrt sich um.
    SPIEGEL = Torchfeld.feld([-1.0, 1.0, 1.0], copy=True)
    NULL_M = 2e-5

    def __init__(self, melden=None):
        self.melden = melden or (lambda *a: None)
        self.feld = None

    def vorbereiten(self):
        if self.feld is None:
            self.feld = G9knochenfeld()
        return self

    # ------------------------------------------------------------ Operationen

    def op(self, uma_knochen, art, wert, **zusatz):
        u"""Eine Operation auf den Genesis-Knochen zu `uma_knochen` — oder None."""
        z = Umaabbildung.ziel(uma_knochen)
        if z is None or z['knochen'] not in self.feld.kopf:
            return None
        op = {'knochen': z['knochen'], 'art': art, 'wert': wert, 'welt': z['welt'] or art != 'skalieren'}
        if z.get('wirkt'):
            op['wirkt'] = list(z['wirkt'])
        if z.get('pivot') is not None:
            op['pivot'] = z['pivot']
        elif z.get('mitte'):
            op['pivot'] = Torchfeld.mean([self.feld.kopf[b] for b in z['mitte'] if b in self.feld.kopf], axis=0)
        op.update(zusatz)
        return op

    def drehung(self, achse, grad):
        u"""Unity-Drehung (Achse, Grad) als Genesis-Drehung: Achse an der x-Ebene gespiegelt, Winkel umgekehrt (M·R(a, θ)·M = R(M·a, −θ))."""
        return ((float(achse[0]) * -1.0, float(achse[1]), float(achse[2])), -float(grad))

    def pose_ops(self, pose, gewicht):
        u"""Operationen einer `UMABonePose` mit Gewicht `gewicht` (`UMASkeleton.Morph`)."""
        aus = []
        for p in pose:
            skala = 1.0 + (Torchfeld.feld(p['skala']) - 1.0) * gewicht
            if Torchfeld.abs(skala - 1.0).max() > 1e-6:
                aus.append(self.op(p['knochen'], 'skalieren', tuple(skala)))
            pos = Torchfeld.feld(p['position']) * gewicht * self.SPIEGEL
            if Torchfeld.abs(pos).max() > 1e-6:
                aus.append(self.op(p['knochen'], 'verschieben', tuple(pos)))
            x, y, z, w = p['rotation']
            winkel = 2.0 * Torchfeld.degrees(Torchfeld.arccos(max(-1.0, min(1.0, w))))
            if abs(winkel) > 1e-3 and Torchfeld.linalg_norm(Torchfeld.feld((x, y, z))) > 1e-9:
                aus.append(self.op(p['knochen'], 'drehen', self.drehung((x, y, z), winkel * gewicht)))
        return [o for o in aus if o]

    def effekt_ops(self, effekt, v):
        u"""Operationen eines DNA-Effekts bei DNA-Wert `v`."""
        m = Umaregler.wert(effekt, v)
        art = effekt['art']
        if art == 'skalieren':
            o = self.op(effekt['knochen'], 'skalieren', tuple((1.0 + Torchfeld.feld(effekt['wert']) * m).tolist()))
        elif art == 'verschieben':
            o = self.op(effekt['knochen'], 'verschieben', tuple((Torchfeld.feld(effekt['wert']) * m * self.SPIEGEL).tolist()))
        elif art == 'drehen':
            o = self.op(effekt['knochen'], 'drehen', self.drehung(effekt['achse'], effekt['grad'] * m))
        else:
            return self.pose_ops(effekt['pose'], m)
        return [o] if o else []

    def regler_ops(self, regler, v):
        return [o for e in regler['effekte'] for o in self.effekt_ops(e, v)]

    # ------------------------------------------------------------------ Bauen

    def seite(self, ops_v, ops_vorgabe):
        u"""`(delta, (kopf, ende))` — Feld der Stellung gegen das der Vorgabe; Gelenkversaetze je Knochen."""
        d1, g1 = self.feld.feld(ops_v)
        d0, g0 = self.feld.feld(ops_vorgabe)
        return d1 - d0, {n: (g1[n][0] - g0[n][0], g1[n][1] - g0[n][1]) for n in g1}

    def gelenke(self, plus, minus):
        u"""`(namen, kopf_plus, ende_plus, kopf_minus, ende_minus)` fuer die Knochen mit merklichem Versatz — oder None."""
        halten = [n for n in self.feld.namen if max(Torchfeld.linalg_norm(plus[n][0]), Torchfeld.linalg_norm(plus[n][1]),
                                                    Torchfeld.linalg_norm(minus[n][0]), Torchfeld.linalg_norm(minus[n][1])) >= 2e-4]
        if not halten:
            return None
        return (Torchfeld.feld(halten), Torchfeld.feld([plus[n][0] for n in halten]), Torchfeld.feld([plus[n][1] for n in halten]),
                Torchfeld.feld([minus[n][0] for n in halten]), Torchfeld.feld([minus[n][1] for n in halten]))

    @staticmethod
    def anzeige(titel, name):
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)
        return u'%s: %s' % (titel, text[:1].upper() + text[1:])

    def bauen(self):
        u"""Alle Regler bauen; gibt `[{name, punkte, plus_mm, minus_mm}]` zurueck."""
        start = time.perf_counter()
        self.vorbereiten()
        G9umamorphe.leeren()
        aus, reihe = [], 0
        hoehe0 = float(Torchfeld.ptp(self.feld.basis[:, 1]))
        auftraege = []
        for p in Umaregler.kinderposen():
            auftraege.append({'kennung': p['kennung'], 'anzeige': p['anzeige'], 'kategorie': 'Kind', 'bereich': 'uma_kind', 'min': 0.0,
                              'plus': self.pose_ops(p['pose'], 1.0), 'minus': None, 'vorgabe': []})
        for r in Umaregler.regler():
            ops = {v: self.regler_ops(r, v) for v in (0.0, r['vorgabe'], 1.0)}
            auftraege.append({'kennung': '%s_%s' % ('Body' if r['bereich'] == u'Körper' else 'Face', r['name']), 'anzeige': self.anzeige(r['bereich'], r['name']),
                              'kategorie': r['bereich'], 'bereich': 'uma_dna', 'min': -1.0, 'plus': ops[1.0], 'minus': ops[0.0], 'vorgabe': ops[r['vorgabe']]})
        for nr, a in enumerate(auftraege, 1):
            d_plus, g_plus = self.seite(a['plus'], a['vorgabe'])
            if a['minus'] is not None:
                d_minus, g_minus = self.seite(a['minus'], a['vorgabe'])
            else:
                d_minus, g_minus = torch.zeros_like(d_plus), {n: (torch.zeros(3, dtype=torch.float64, device='cuda'), torch.zeros(3, dtype=torch.float64, device='cuda')) for n in g_plus}
            d_plus[Torchfeld.linalg_norm(d_plus, dim=1) < self.NULL_M] = 0.0
            d_minus[Torchfeld.linalg_norm(d_minus, dim=1) < self.NULL_M] = 0.0
            nummern = torch.nonzero((Torchfeld.amax(Torchfeld.abs(d_plus), dim=1) > 0) | (Torchfeld.amax(Torchfeld.abs(d_minus), dim=1) > 0), as_tuple=True)[0]
            if not len(nummern):
                logger.info('UMA-Morphs: %s bewegt keinen Kaefigpunkt (kein Knochen zugeordnet?) — uebergangen', a['kennung'])
                self.melden(nr, len(auftraege), a['kennung'], None)
                continue
            quelle = {'quelle': 'UMA 3 (Knochenvorgaben, auf Genesis uebertragen — Achsen angenommen)', 'anzeige': a['anzeige'], 'kategorie': a['kategorie'],
                      'bereich': a['bereich'], 'reihe': reihe, 'min': a['min'], 'max': 1.0, 'rig': True,
                      # Koerperhoehe der Genesis-Figur bei +1 und −1 im Verhaeltnis zur Vorgabe — Kontrolle der Groessenwirkung
                      'hoehe_verhaeltnis': [round(float(Torchfeld.ptp(self.feld.basis[:, 1] + d_plus[:, 1])) / hoehe0, 3),
                                            round(float(Torchfeld.ptp(self.feld.basis[:, 1] + d_minus[:, 1])) / hoehe0, 3)]}
            G9umamorphe.ablegen(a['kennung'], nummern, d_plus[nummern], d_minus[nummern], quelle, self.gelenke(g_plus, g_minus))
            brief = G9umamorphe.steckbrief(a['kennung'])
            aus.append({'name': a['kennung'], 'punkte': brief['punkte'], 'plus_mm': brief['plus_mm'], 'minus_mm': brief['minus_mm']})
            self.melden(nr, len(auftraege), a['kennung'], brief)
            reihe += 1
        G9umamorphe.bestand_schreiben({'zahl': len(aus), 'sekunden': round(time.perf_counter() - start, 1), 'achsen': 'Unity y = Knochenachse, x = rechts, z = vorn (Annahme)'})
        logger.info('UMA-Morphs auf Genesis 9: %d Regler in %.1f s nach %s', len(aus), time.perf_counter() - start, G9umamorphe.ordner())
        return aus
