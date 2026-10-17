# -*- coding: utf-8 -*-
u"""Mhmorpheaufgenesis — alle MakeHuman-Regler als Genesis-9-Morphs bauen (17.10.2026).

Edgar, 17.10.2026: „du solltest ALLE Morphs und Regler aus den anderen Projekten portieren und als neue Morphs fuer Genesis nachbauen“.

Je Regler des Plans (`Mhmorphplan`: 12 Makros, 257 Detailregler, 22 Koerperformen) wird MakeHumans Netz in der Reglerstellung gerechnet (`Mhformung`, also mit
MakeHumans eigenen Gewichten), gegen die weibliche Vorgabefigur abgezogen und ueber den Klon auf den Genesis-Kaefig gelegt (`Mhklonuebertragung`).
Abgelegt als `mh:<Gruppe>_<Regler>` (`G9mhmorphe`, Ablage `Genesis9/ablage/mhmorphe/`).

DAS SKELETT: MakeHumans Gelenke sind Mittelwerte von Helferwuerfeln im Netz (`Mhskelett`) — folgen also jedem Regler von selbst. Hier dient das als
MASS: Aendert ein Regler den Abstand zweier Gelenke um 7,5 mm oder das Kopfgelenk um 5 mm (die Schwellen von `Hbmorphrig`), traegt der Morph auch
Gelenkversaetze fuer Genesis (`G9gelenkversatz`, geschaetzt aus der Haut am Kaefig); sonst nicht — ein Volumenregler verschiebt die Oberflaeche, nicht das Gelenk.

Bauen: `manage.py mhmorphe_bauen`. Gemessen wird im Lauf (Zahlen in `bestand.json`).
"""
import logging
import time

import numpy as np
from Genesis9.gelenkversatz import G9gelenkversatz
from Genesis9.mhmorphe import G9mhmorphe

from .mhklonuebertragung import Mhklonuebertragung
from .mhmorphplan import Mhmorphplan

logger = logging.getLogger('core')

__all__ = ['Mhmorpheaufgenesis']


class Mhmorpheaufgenesis:
    u"""Alle MakeHuman-Regler als Genesis-9-Morphs."""

    #: MakeHuman rechnet in Dezimetern.
    METER = 0.1
    #: Ab dieser Aenderung der Koerperhoehe (m) wird die Hoehe an MakeHumans Verhaeltnis angeglichen.
    HOEHE_AB_M = 0.05

    def __init__(self, melden=None):
        self.melden = melden or (lambda *a: None)
        self.uebertragung = Mhklonuebertragung()
        self._gelenke = None
        self._skelett = None

    # ------------------------------------------------------------ Rechnen

    def vorbereiten(self):
        self.uebertragung.vorbereiten()
        self.vorgabe = self.uebertragung.formung.punkte()
        return self

    def stellung(self, spec):
        u"""Das verformte hm08-Netz (dm) zu einer Angabe aus dem Plan."""
        from MakeHuman.formung import Mhformung
        from MakeHuman.zielablage import Mhzielablage
        gender = {'gender': self.uebertragung.GESCHLECHT}
        if 'makro' in spec:
            return Mhformung({**gender, **spec['makro']}).punkte()
        if 'regler' in spec:
            return Mhformung(gender, spec['regler']).punkte()
        punkte = self.vorgabe.copy()
        nummern, verschiebung = Mhzielablage.ziel(spec['ziel'])
        gueltig = nummern < len(punkte)
        np.add.at(punkte, nummern[gueltig], verschiebung[gueltig])
        return punkte

    def delta(self, spec):
        u"""(M, 3) Verschiebung gegen die Vorgabefigur in Dezimetern."""
        return self.stellung(spec) - self.vorgabe

    # --------------------------------------------------------- MakeHuman-Skelett

    def skelett(self):
        u"""`(joint_verts, kopf_joint, schwanz_joint, eltern, positionen)` — das Rig als Indexfelder, Positionen der Vorgabefigur in Metern."""
        if self._skelett is None:
            from MakeHuman.skelett import Mhskelett
            rig = Mhskelett.rig()
            namen = [j for j, v in rig['joints'].items() if v]
            index = {j: i for i, j in enumerate(namen)}
            verts = [np.array([n for n in rig['joints'][j] if 0 <= n < len(self.vorgabe)], dtype=np.int64) for j in namen]
            pos = np.array([self.vorgabe[v].mean(axis=0) * self.METER for v in verts])
            knochen = [(b['head'], b['tail']) for b in rig['bones'].values() if b.get('head') in index and b.get('tail') in index]
            self._skelett = (verts, np.array([index[h] for h, _t in knochen]), np.array([index[t] for _h, t in knochen]), pos,
                             index.get(rig['bones'].get('head', {}).get('head'), 0))
        return self._skelett

    def mass(self, delta_dm):
        u"""`{kopf_mm, laenge_mm}` — wie weit MakeHumans eigene Gelenke bei diesem Delta wandern (Kopfgelenk, groesste Aenderung eines Knochenabstands)."""
        verts, kopf, schwanz, pos, kopfgelenk = self.skelett()
        bewegt = np.array([delta_dm[v].mean(axis=0) * self.METER for v in verts])
        alt = np.linalg.norm(pos[schwanz] - pos[kopf], axis=1)
        neu = np.linalg.norm((pos + bewegt)[schwanz] - (pos + bewegt)[kopf], axis=1)
        return {'kopf_mm': round(float(np.linalg.norm(bewegt[kopfgelenk])) * 1000, 2),
                'laenge_mm': round(float(np.abs(neu - alt).max()) * 1000, 2)}

    def gelenkversatz(self):
        if self._gelenke is None:
            self._gelenke = G9gelenkversatz()
        return self._gelenke

    def hoehe_angleichen(self, feld, delta_dm):
        u"""`(feld, Faktor)` — bei einer grossen Aenderung der Koerperhoehe (Alter, Groesse) das Kaefigfeld so skalieren, dass Genesis dasselbe VERHAELTNIS erreicht wie
        MakeHuman. Der Klon bildet ein Delta durch die Rahmen der Glieder ab (Laenge nach Knochenlaenge, quer nach Hoehenverhaeltnis); fuer die kleinen Regler stimmt
        das, bei grossen Hoehenspruengen blieb Genesis zu hoch: Baby 0,73 m statt 0,64 m (MakeHuman 38 % der Vorgabe, Klon 43 %, gemessen 17.10.2026,
        `ProjektTemp/_wegwerf/familien/mh_baby_hoehe.py`). Ein einziger Faktor je Seite haelt die Proportionen des Felds."""
        from Genesis9.basisnetz import G9basisnetz
        koerper = self.uebertragung.koerper
        basis = np.asarray(G9basisnetz.holen().punkte)[:, 1]
        mh0 = float(np.ptp(self.vorgabe[koerper][:, 1]))
        mh1 = float(np.ptp((self.vorgabe + delta_dm)[koerper][:, 1]))
        h0 = float(np.ptp(basis))
        ist = float(np.ptp(basis + feld[:, 1]))
        soll = h0 * mh1 / mh0
        if abs(soll - h0) < self.HOEHE_AB_M or abs(ist - h0) < self.HOEHE_AB_M:
            return feld, 1.0
        faktor = (soll - h0) / (ist - h0)
        return feld * faktor, faktor

    # -------------------------------------------------------------- Bauen

    def bauen(self):
        u"""Alle Regler bauen; gibt `[{name, punkte, plus_mm, minus_mm}]` zurueck."""
        start = time.perf_counter()
        self.vorbereiten()
        auftraege = Mhmorphplan.auftraege()
        G9mhmorphe.leeren()
        aus, skelett = [], []
        for nr, auftrag in enumerate(auftraege, 1):
            d_plus = self.delta(auftrag['plus'])
            d_minus = self.delta(auftrag['minus']) if auftrag['minus'] else np.zeros_like(d_plus)
            plus = self.uebertragung.uebertragen(d_plus * self.METER)
            minus = self.uebertragung.uebertragen(d_minus * self.METER) if auftrag['minus'] else np.zeros_like(plus)
            plus, f_plus = self.hoehe_angleichen(plus, d_plus)
            minus, f_minus = (self.hoehe_angleichen(minus, d_minus) if auftrag['minus'] else (minus, 1.0))
            nummern = np.nonzero((np.abs(plus).max(axis=1) > 0) | (np.abs(minus).max(axis=1) > 0))[0]
            if not len(nummern):
                logger.info('MH-Morphs: %s erreicht keinen Kaefigpunkt — uebergangen', auftrag['kennung'])
                self.melden(nr, len(auftraege), auftrag['kennung'], None)
                continue
            mass = {k: max(a, b) for (k, a), b in zip(self.mass(d_plus).items(), self.mass(d_minus).values(), strict=True)}
            rig = mass['kopf_mm'] >= G9gelenkversatz.KOPF_MM or mass['laenge_mm'] >= G9gelenkversatz.LAENGE_MM
            gelenke = self.gelenkversatz().fuer_morph(nummern, plus[nummern], minus[nummern]) if rig else None
            if rig:
                skelett.append(auftrag['kennung'])
            quelle = {'quelle': 'MakeHuman 1.3 (Bezug: weibliche Vorgabefigur)', 'anzeige': auftrag['anzeige'], 'kategorie': auftrag['kategorie'],
                      'bereich': auftrag['bereich'], 'reihe': auftrag['reihe'], 'min': auftrag['min'], 'max': auftrag['max'], 'rig': rig,
                      'hoehenfaktor': [round(f_plus, 3), round(f_minus, 3)], **mass}
            G9mhmorphe.ablegen(auftrag['kennung'], nummern, plus[nummern], minus[nummern], quelle, gelenke)
            brief = G9mhmorphe.steckbrief(auftrag['kennung'])
            aus.append({'name': auftrag['kennung'], 'punkte': brief['punkte'], 'plus_mm': brief['plus_mm'], 'minus_mm': brief['minus_mm']})
            self.melden(nr, len(auftraege), auftrag['kennung'], brief)
        G9mhmorphe.bestand_schreiben({
            'zahl': len(aus), 'mit_skelett': skelett, 'bezug': 'MakeHuman weiblich (Geschlecht 0)',
            'ungueltige_kaefigpunkte': int(self.uebertragung.ungueltig().sum()), 'sekunden': round(time.perf_counter() - start, 1)})
        logger.info('MH-Morphs auf Genesis 9: %d Regler in %.1f s nach %s', len(aus), time.perf_counter() - start, G9mhmorphe.ordner())
        return aus
