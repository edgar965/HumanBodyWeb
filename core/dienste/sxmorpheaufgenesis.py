# -*- coding: utf-8 -*-
u"""Sxmorpheaufgenesis — die SMPL-X-Regler als Genesis-9-Morphs bauen (17.10.2026).

Edgar, 17.10.2026: „du solltest ALLE Morphs und Regler aus den anderen Projekten portieren und als neue Morphs fuer Genesis nachbauen“.

WELCHE REGLER: Die, die 3dTools auf SMPL-X selbst anbietet (`SMPL/form.py`, `SMPL/xmassregler.py`):
- **Form 1…10** — die ersten zehn Formkomponenten des Modells (`Smplform.ANZAHL_BETAS`), voller Ausschlag ±2 Beta (`JE_BETA` 50 → ±100). Beta 0 und 1 sind
  Groesse und Fuelle (am weiblichen Modell: Beta 0 + = hoeher, Beta 1 + = fuelliger, gemessen 15.09.2026, siehe `SMPL/form.py`); 2…9 sind ungemessen und bleiben „Form 3…10“.
- **23 Massregler** in Zentimetern (Armlaenge, Brustumfang …): je eine Richtung im 300-dimensionalen Formraum, die ein Mass um 15 % (Laengen) bzw. 20 %
  (Umfaenge) bewegt und die anderen festhaelt. Die Richtungen kommen aus `massregler_f1_female.npz` (Smplxmassregler.berechnen).
Die 100 Ausdruecke des Modells fehlen mit Absicht: Genesis hat FACS-Morphs, und die SMPL-X-Mimik von 3dTools ist selbst eine Uebertragung der HumanBody-Ausdruecke.

DER WEG: A-Haltung wie Genesis (`Smplxkoerper.a40`, Arme 45,3°), Differenz zur Grundfigur, mal dem Hoehenverhaeltnis Genesis/SMPL-X, ueber die Netzpaarung
(`G9netzpaarung`: je Kaefigpunkt sein SMPL-X-Punkt, bei Gewicht unter `GEWICHT_AB` ohne Gegenstueck — Mundinnenraum, Augenhoehlen) auf den Kaefig, Luecken aus
den Nachbarn (`G9feldputz`). Weibliches Modell als Bezug (Genesis ist eine Frau); die Paarung selbst steht am neutralen Netz (gleiche Punktnummern in allen
drei Modellen). SMPL-X: nur nicht-kommerzielle Forschung (`SMPL/HERKUNFT.md`).

Bauen: `manage.py sxmorphe_bauen`.
"""
import logging
import time

import numpy as np
from Genesis9.feldputz import G9feldputz
from Genesis9.gelenkversatz import G9gelenkversatz
from Genesis9.kollision import G9kollision
from Genesis9.netzpaarung import G9netzpaarung
from Genesis9.pfade import G9pfade
from Genesis9.sxmorphe import G9sxmorphe

logger = logging.getLogger('core')

__all__ = ['Sxmorpheaufgenesis']


class Sxmorpheaufgenesis:
    u"""Alle SMPL-X-Regler als Genesis-9-Morphs."""

    #: Rechnungen am weiblichen Modell; Beta-Ausschlag, der +100 am Regler entspricht.
    MODELL = 'female'
    BETA_VOLL = 2.0
    FORMEN = 10
    #: Paarungsgewicht, ab dem ein Kaefigpunkt ein SMPL-X-Gegenstueck hat.
    GEWICHT_AB = 0.5
    GLAETTUNG = 6
    NULL_M = 2e-5

    def __init__(self, melden=None):
        self.melden = melden or (lambda *a: None)
        self.paarung = None
        self.modell = None
        self._gelenke = None

    # ---------------------------------------------------------- Vorbereiten

    def vorbereiten(self):
        if self.paarung is not None:
            return self
        from Genesis9.zielnetz import G9zielnetz
        from SMPL.xkoerper import Smplxkoerper
        self.paarung = G9netzpaarung.holen()
        self.modell = Smplxkoerper.laden(self.MODELL, str(G9pfade.smplx()))
        self.arm = G9zielnetz.ARMWINKEL
        self.null = self.modell.a40(np.zeros(self.modell.BETAS_MAX), grad=self.arm)
        self.massstab = self.paarung.hoehe_basis / self.paarung.hoehe_neutral
        self.ungueltig = (self.paarung.zuordnung < 0) | (self.paarung.gewicht < self.GEWICHT_AB)
        self.putz = G9feldputz.vom_kaefig()
        from Genesis9.basisnetz import G9basisnetz
        punkte = G9basisnetz.holen().punkte
        _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte, k=self.GLAETTUNG)
        self.nachbar = np.asarray(nachbar, dtype=np.int64)
        return self

    def auftraege(self):
        u"""`[{kennung, anzeige, kategorie, bereich, reihe, plus, minus}]` — `plus`/`minus` sind Beta-Vektoren (300,)."""
        from SMPL.xmassregler import Smplxmassregler
        aus = []
        gespeichert = Smplxmassregler.laden(str(G9pfade.smplx()), self.MODELL)
        if gespeichert is None:
            raise RuntimeError('SMPL-X-Massregler fehlen (Smplxmassregler.berechnen)')
        for schluessel, anzeige, _ziel, links, rechts in Smplxmassregler.REGLER:
            plus, minus = gespeichert['richtungen'][schluessel]
            aus.append({'kennung': 'Mass_' + schluessel, 'anzeige': u'%s (%s … %s)' % (anzeige, links, rechts), 'kategorie': 'Mass',
                        'bereich': 'sx_mass', 'reihe': len(aus), 'plus': np.asarray(plus, dtype=np.float64), 'minus': np.asarray(minus, dtype=np.float64),
                        'wirkung': gespeichert['wirkung'].get(schluessel)})
        namen = {0: u'Größe', 1: u'Fülle'}
        for k in range(self.FORMEN):
            b = np.zeros(self.modell.BETAS_MAX)
            b[k] = self.BETA_VOLL
            titel = u'Form %d' % (k + 1) + (u' (%s)' % namen[k] if k in namen else u' (nicht benannt)')
            aus.append({'kennung': 'Form_%02d' % (k + 1), 'anzeige': titel, 'kategorie': 'Form', 'bereich': 'sx_form', 'reihe': len(aus),
                        'plus': b, 'minus': -b, 'wirkung': None})
        return aus

    # ------------------------------------------------------------ Rechnen

    def verschiebung(self, betas):
        u"""(10475, 3) SMPL-X-Verschiebung gegen die Grundfigur, in Genesis-Metern, und die Gelenke dazu."""
        v = self.modell.a40(betas, grad=self.arm)
        return (v - self.null) * self.massstab, (self.modell.J_regressor @ v - self.modell.J_regressor @ self.null) * self.massstab

    def uebertragen(self, delta):
        u"""(25182, 3) Kaefigfeld aus einer SMPL-X-Verschiebung."""
        zu = self.paarung.zuordnung
        feld = np.zeros((len(zu), 3))
        gueltig = ~self.ungueltig
        feld[gueltig] = delta[zu[gueltig]]
        feld = self.putz.fuellen(feld, self.ungueltig)
        feld = feld[self.nachbar].mean(axis=1)
        feld, _zacken = self.putz.putzen(feld)
        feld[np.linalg.norm(feld, axis=1) < self.NULL_M] = 0.0
        return feld

    def mass(self, gelenk_delta):
        u"""`{kopf_mm, laenge_mm}` an SMPL-X' eigenen Gelenken (Kopf = Gelenk 15, Knochen nach `parents`)."""
        p = self.modell.parents
        grund = self.modell.J_regressor @ self.null
        alt = np.linalg.norm(grund[1:] - grund[p[1:]], axis=1)
        neu = np.linalg.norm((grund + gelenk_delta)[1:] - (grund + gelenk_delta)[p[1:]], axis=1)
        return {'kopf_mm': round(float(np.linalg.norm(gelenk_delta[15])) * 1000, 2), 'laenge_mm': round(float(np.abs(neu - alt).max()) * 1000, 2)}

    def gelenkversatz(self):
        if self._gelenke is None:
            self._gelenke = G9gelenkversatz()
        return self._gelenke

    # -------------------------------------------------------------- Bauen

    def bauen(self):
        u"""Alle Regler bauen; gibt `[{name, punkte, plus_mm, minus_mm}]` zurueck."""
        start = time.perf_counter()
        self.vorbereiten()
        auftraege = self.auftraege()
        G9sxmorphe.leeren()
        aus, skelett = [], []
        for nr, a in enumerate(auftraege, 1):
            d_plus, j_plus = self.verschiebung(a['plus'])
            d_minus, j_minus = self.verschiebung(a['minus'])
            plus, minus = self.uebertragen(d_plus), self.uebertragen(d_minus)
            nummern = np.nonzero((np.abs(plus).max(axis=1) > 0) | (np.abs(minus).max(axis=1) > 0))[0]
            if not len(nummern):
                self.melden(nr, len(auftraege), a['kennung'], None)
                continue
            m1, m2 = self.mass(j_plus), self.mass(j_minus)
            mass = {k: max(m1[k], m2[k]) for k in m1}
            rig = mass['kopf_mm'] >= G9gelenkversatz.KOPF_MM or mass['laenge_mm'] >= G9gelenkversatz.LAENGE_MM
            gelenke = self.gelenkversatz().fuer_morph(nummern, plus[nummern], minus[nummern]) if rig else None
            if rig:
                skelett.append(a['kennung'])
            quelle = {'quelle': 'SMPL-X %s (A-Haltung %.1f°)' % (self.MODELL, self.arm), 'anzeige': a['anzeige'], 'kategorie': a['kategorie'],
                      'bereich': a['bereich'], 'reihe': a['reihe'], 'min': -1.0, 'max': 1.0, 'rig': rig, **mass}
            if a['wirkung']:
                quelle['wirkung'] = a['wirkung']
            G9sxmorphe.ablegen(a['kennung'], nummern, plus[nummern], minus[nummern], quelle, gelenke)
            brief = G9sxmorphe.steckbrief(a['kennung'])
            aus.append({'name': a['kennung'], 'punkte': brief['punkte'], 'plus_mm': brief['plus_mm'], 'minus_mm': brief['minus_mm']})
            self.melden(nr, len(auftraege), a['kennung'], brief)
        G9sxmorphe.bestand_schreiben({'zahl': len(aus), 'mit_skelett': skelett, 'modell': self.MODELL, 'massstab': round(float(self.massstab), 4),
                                      'ungueltige_kaefigpunkte': int(self.ungueltig.sum()), 'sekunden': round(time.perf_counter() - start, 1)})
        logger.info('SX-Morphs auf Genesis 9: %d Regler in %.1f s nach %s', len(aus), time.perf_counter() - start, G9sxmorphe.ordner())
        return aus
