# -*- coding: utf-8 -*-
u"""G1morpheaufgenesis — die Kinder von Genesis 1 als Genesis-9-Morphs bauen (18.10.2026).

Edgar, 17./18.10.2026: „überlege die Genesis 1 Portierung für Kind“, „Basic Child als Regler bei ‚Alter‘“, „Kids 4 auch als Regler bei ‚Alter‘ Kategorie“. Für Genesis 9 hat die
Bibliothek keine Kinder (`ProjektTemp/_wegwerf/hautebenen/kinder_suche.py`); Genesis 1 hat zwei (gemessen `genesis1_kind.py`, `genesis1_formeln.py`):

    BasicChild  `FBMBasicChild`: Form in Erwachsenengröße (Netz 180,9 cm, Verschiebung bis 16,8 cm), Größe über die Figurformel `scale/general` = −0,46·Wert (also 0,54),
                400 Gelenkformeln (`center_point`/`end_point`), 175 Ausrichtungsformeln — `Basic Child.duf` stellt nur diesen Morph auf 1.
    Kids4       `CloneKids4`: Genesis 1 in der Gestalt von DAZ Kids 4 (Netz 103,2 cm), ohne Formeln.

DER WEG: Wie die MakeHuman-Kinder als ÄHNLICHKEIT PLUS FORM (`Mhaehnlichkeit`, `G9aehnlichkeit`): die Verkleinerung `s` geht exakt auf den Käfig, nur die Form (Proportionen, Gesicht) in
Erwachsenengröße wandert über Daz' Klon (`G1klonuebertragung`). Basic Child trennt beides schon selbst (Form + Figurskalierung um den Ursprung); bei Kids 4 wird die Ähnlichkeit abgespalten
(Höhenverhältnis, Mittelpunkt auf der Körperachse nach kleinsten Quadraten) und der Rest durch `s` geteilt — so ist auch sie eine Form in Erwachsenengröße:

    Kind = C + s·(P + Form − C)        Käfigfeld = (s − 1)·(Käfig − C9) + s·Form9

Die Gelenke: Basic Child dreht mit Daz' Gelenkformeln in die G9-Stellung, Kids 4 mit geschätzten (`G1klonuebertragung.gelenke_schaetzen`); das G9-Skelett folgt der Ähnlichkeit exakt und
der Form geschätzt (`G9gelenkversatz.fuer_morph(…, aehnlich=…)`). Bauen: `manage.py g1morphe_bauen`.
"""
import logging
import time
from urllib.parse import unquote

import numpy as np
from Genesis9.aehnlichkeit import G9aehnlichkeit
from Genesis9.basisnetz import G9basisnetz
from Genesis9.dson import G9dson
from Genesis9.g1morphe import G9g1morphe
from Genesis9.gelenkversatz import G9gelenkversatz
from Genesis9.pfade import G9pfade

from .g1klonuebertragung import G1klonuebertragung

logger = logging.getLogger('core')

__all__ = ['G1morpheaufgenesis']


class G1morpheaufgenesis:
    u"""Basic Child und Kids 4 als Genesis-9-Morphs (`g1:`)."""

    AUFTRAEGE = (
        {'kennung': 'BasicChild', 'datei': 'FBMBasicChild', 'reihe': 0, 'anzeige': u'Basic Child  (Genesis 1)'},
        {'kennung': 'Kids4', 'datei': 'CloneKids4', 'reihe': 1, 'anzeige': u'Kids 4  (Genesis 1)'},
    )
    MORPHORDNER = ('DAZ 3D', 'Genesis', 'Base', 'Morphs', 'DAZ 3D', 'Base')
    CM = 0.01

    def __init__(self, melden=None):
        self.melden = melden or (lambda *a: None)
        self.uebertragung = None
        self.basis = None

    def vorbereiten(self):
        if self.uebertragung is None:
            self.uebertragung = G1klonuebertragung()
            self.basis = np.asarray(G9basisnetz.holen().punkte, dtype=np.float64)
        return self

    # ------------------------------------------------------------ Lesen

    def morph(self, datei):
        u"""`(delta (19296, 3) m, formeln)` eines Genesis-1-Morphs."""
        d = G9dson.roh(G9pfade.daten().joinpath(*self.MORPHORDNER) / (datei + '.dsf'))
        m = d['modifier_library'][0]
        werte = np.asarray(m['morph']['deltas']['values'], dtype=np.float64)
        delta = np.zeros_like(self.uebertragung.grund)
        delta[werte[:, 0].astype(np.int64)] = werte[:, 1:] * self.CM
        return delta, m.get('formulas') or []

    @staticmethod
    def formelwerte(formeln):
        u"""`(s, versatz {knochen: {'center_point': [cm]}}, ausrichtung {knochen: [Grad]}, übergangen)` aus Daz-Formeln der Form `push Morphwert, push Zahl, mult` (bei Wert 1: die Zahl).
        `scale/general` addiert sich zu `s = 1 + Σ`; `end_point` und Wölbungsgewichte (`bulge_weights`) braucht die Stellung nicht."""
        s, versatz, ausrichtung, uebergangen = 1.0, {}, {}, 0
        for f in formeln:
            ziel = unquote(str(f.get('output') or ''))
            if '?' not in ziel:
                continue
            knoten, eigenschaft = ziel.split('#')[-1].split('?')[0], ziel.split('?')[-1]
            ops = f.get('operations') or []
            zahlen = [o['val'] for o in ops if o.get('op') == 'push' and 'val' in o]
            if not zahlen or [o.get('op') for o in ops][-1:] != ['mult']:
                uebergangen += 1
                continue
            wert = float(zahlen[-1])
            art, _, achse = eigenschaft.partition('/')
            if eigenschaft == 'scale/general':
                s += wert
            elif art in ('center_point', 'orientation') and achse in ('x', 'y', 'z'):
                if art == 'center_point':
                    ziel_d = versatz.setdefault(knoten, {'center_point': [0.0, 0.0, 0.0]})['center_point']
                else:
                    ziel_d = ausrichtung.setdefault(knoten, [0.0, 0.0, 0.0])
                ziel_d['xyz'.index(achse)] += wert
        return s, versatz, ausrichtung, uebergangen

    # ----------------------------------------------------------- Rechnen

    def zerlegen(self, auftrag):
        u"""`(s, unter_m, form (19296, 3) m in T-Stellung und Erwachsenengröße, versatz, ausrichtung)`."""
        u = self.uebertragung
        p = u.grund
        delta, formeln = self.morph(auftrag['datei'])
        if formeln:
            s, versatz, ausrichtung, uebergangen = self.formelwerte(formeln)
            logger.info('G1-Morphs: %s — s %.3f, %d Gelenke, %d Ausrichtungen aus Formeln, %d Formeln übergangen', auftrag['kennung'], s, len(versatz), len(ausrichtung), uebergangen)
            return s, float(p[u.hautpunkte, 1].min()), delta, versatz, ausrichtung          # Daz skaliert die Figur um den Ursprung (0, 0, 0)
        h = u.hautpunkte
        s = float(np.ptp((p + delta)[h, 1])) / float(np.ptp(p[h, 1]))
        hoehe = float((p[h, 1] - delta[h, 1] / (s - 1.0)).mean())                             # kleinste Quadrate auf der Körperachse (wie `Mhaehnlichkeit.zerlegen`)
        form = (delta - (s - 1.0) * (p - np.array([0.0, hoehe, 0.0]))) / s
        return s, float(p[h, 1].min()) - hoehe, form, u.gelenke_schaetzen(form), {}

    def feld(self, auftrag):
        u"""`(feld, rest, s, unter, zentrum)` auf dem Käfig (m): Ähnlichkeit um `zentrum` plus `rest` = s·übertragene Form."""
        s, unter, form, versatz, ausrichtung = self.zerlegen(auftrag)
        u = self.uebertragung
        gedreht = u.stellen(u.grund + form, versatz, ausrichtung) - u.stellen(u.grund)
        rest = s * u.uebertragen(gedreht)
        zentrum = G9aehnlichkeit.zentrum(float(self.basis[:, 1].min()), unter)
        return (s - 1.0) * (self.basis - zentrum) + rest, rest, s, unter, zentrum

    # -------------------------------------------------------------- Bauen

    def bauen(self):
        u"""Beide Regler bauen; gibt `[{name, punkte, plus_mm, minus_mm}]` zurück."""
        start = time.perf_counter()
        self.vorbereiten()
        G9g1morphe.leeren()
        aus = []
        gelenkversatz = G9gelenkversatz()
        for nr, a in enumerate(self.AUFTRAEGE, 1):
            plus, rest, s, unter, zentrum = self.feld(a)
            nummern = np.nonzero(np.abs(plus).max(axis=1) > 0)[0]
            null = np.zeros((len(nummern), 3))
            gelenke = gelenkversatz.fuer_morph(nummern, rest[nummern], null, aehnlich=(s, zentrum))
            hoehe = float(np.ptp(self.basis[:, 1] + plus[:, 1]))
            quelle = {'quelle': u'Genesis 1 (Daz), über den Klon CloneGenesis', 'anzeige': a['anzeige'], 'kategorie': 'Alter', 'bereich': 'g1_alter', 'reihe': a['reihe'],
                      'min': 0.0, 'max': 1.0, 'rig': True, 'aehnlichkeit': round(s, 4), 'aehnlichkeit_unter': round(unter, 4), 'hoehe_m': round(hoehe, 3),
                      'hinweis': u'%s von Genesis 1 (Daz): Proportionen und Gesicht eines Kindes, Größe %d %% — auf der Grundfigur %.2f m. Übertragen über Daz’ Klon von Genesis 1. '
                                 u'Wirkt zusätzlich zu „Alter“ in Jahren; beides zugleich verkleinert doppelt.' % (a['anzeige'].split('  ')[0], round(s * 100), hoehe)}
            G9g1morphe.ablegen(a['kennung'], nummern, plus[nummern], null, quelle, gelenke)
            brief = G9g1morphe.steckbrief(a['kennung'])
            aus.append({'name': a['kennung'], 'punkte': brief['punkte'], 'plus_mm': brief['plus_mm'], 'minus_mm': brief['minus_mm']})
            self.melden(nr, len(self.AUFTRAEGE), a['kennung'], brief)
        G9g1morphe.bestand_schreiben({'zahl': len(aus), 'sekunden': round(time.perf_counter() - start, 1)})
        logger.info('G1-Morphs auf Genesis 9: %d Regler in %.1f s nach %s', len(aus), time.perf_counter() - start, G9g1morphe.ordner())
        return aus
