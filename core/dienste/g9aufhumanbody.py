# -*- coding: utf-8 -*-
u"""G9aufhumanbody — ein Daz-Stueck (Genesis 9) auf eine HumanBody-Figur.

WARUM (Edgar, 19.09.2026: „Umgekehrt auch Genesis Kleider auf HumanBody?"):
Ein Daz-Stueck ist an die Form von Genesis 9 gebunden (`G9folger` projiziert
es auf den G9-Koerper). Auf einer HumanBody-Figur braucht es eine
Entsprechung der beiden Koerper — und die gibt es hier als PAARUNG der
Grundfiguren, einmal je Geschlecht und Bauart gebaut (dasselbe Muster wie
`Genesis9/netzpaarung.py` fuer SMPL-X, nur mit dem HumanBody-Grundnetz):

    Jeder Genesis-Kaefigpunkt wird ueber den Rahmen seines Knochens in die
    HumanBody-Lage GESCHAETZT (`G9hbknochen`: die Grundfiguren stehen
    verschieden — Arme, Beine, Rumpf), dann die zwoelf naechsten
    HumanBody-Punkte DESSELBEN Koerperteils um die Schaetzung (die sechs
    GarmentCode-Segmente, auf beiden Seiten aus den Knochengewichten);
    genommen wird der erste mit gleichsinniger Normale (Skalarprodukt
    > EINIG), sonst der naechste. Ohne Knochenrahmen (Gesicht) zaehlt die
    Lage nach Hoehenmassstab.

UEBERTRAGEN wird ein Stueck ueber lokale Rahmen: Je Stoffpunkt die drei
naechsten Genesis-Koerperpunkte (NACHBARN); der Versatz zum Koerperpunkt wird
in dessen Rahmen (Normale, Aufwaertsrichtung, Querachse) zerlegt und im Rahmen
des gepaarten HumanBody-Punkts DER FIGUR (mit ihren Morphs, nicht der
Grundfigur) wieder zusammengesetzt, mit dem Hoehenmassstab; die Ergebnisse
werden nach Naehe gemittelt. So folgt das Stueck der HumanBody-Form, ohne dass
Genesis dafuer in diese Form gebracht werden muesste. Danach hebt
`G9kollision` es aus der sichtbaren HumanBody-Haut (Unterteilungsnetz), und
die Gewichte kommen vom naechsten HumanBody-Dreieck (`GarmentCode.anziehen`,
DEF-Knochennamen) — der Browser bindet das Stueck an das Rigify-Skelett.

WAS NICHT GEHT: Requisiten (haengen an Daz-Knochen) und Stranghaar (keine
Flaechen). Beides meldet `stueck` als Fehler, nicht als leeres Netz.

Die HumanBody-Figur selbst (Netz, Normalen, sichtbare Flaeche, Gewichte)
kommt aus `hbtraeger.py` (herausgeloest, als diese Datei 328 Zeilen hatte).
"""
import logging

import numpy as np

from Genesis9.formung import G9formung
from Genesis9.kollision import G9kollision

from .g9garmentfigur import G9garmentfigur
from .hbtraeger import Hbtraeger
from .g9hbknochen import G9hbknochen
from .skelettgeometrie import Skelettgeometrie

logger = logging.getLogger('core')

__all__ = ['G9aufhumanbody']


class G9aufhumanbody:
    u"""Paarung Genesis 9 <-> HumanBody und Uebertragung eines Stuecks."""

    KANDIDATEN = 12
    EINIG = 0.3
    #: Koerperpunkte je Stoffpunkt bei der Uebertragung. Nicht mehr: Mit acht
    #: zog der Mittelwert die Lagen INS Gewoelbte (Sehnenwirkung — an der Brust
    #: 6,5 mm in der Haut statt 2,5 mm davor). Gegen die Beulen der HumanBody-
    #: Haut (Bauchmuskeln als Falten im Hemd) wird stattdessen das
    #: VERSCHIEBUNGSFELD ueber den Stoff geglaettet (`GLAETTUNG` Stoffnachbarn).
    NACHBARN = 3
    GLAETTUNG = 12
    #: (geschlecht, bauart) -> Paarung der Grundfiguren.
    _paarungen = {}

    def __init__(self, geschlecht, bauart, morphs=None, meta=None):
        self.geschlecht = 'male' if geschlecht == 'male' else 'female'
        self.bauart = bauart or None
        self.morphs = dict(morphs or {})
        self.meta = dict(meta or {})
        self.paarung = self.paarung_holen(self.geschlecht, self.bauart)
        self._figur = None

    def figur(self):
        if self._figur is None:
            self._figur = Hbtraeger.laden(self.geschlecht, self.bauart, self.morphs, self.meta)
        return self._figur

    # ------------------------------------------------------------ Paarung

    @classmethod
    def paarung_holen(cls, geschlecht, bauart):
        schluessel = (geschlecht, bauart)
        if schluessel not in cls._paarungen:
            cls._paarungen[schluessel] = cls.paarung_bauen(geschlecht, bauart)
        return cls._paarungen[schluessel]

    @classmethod
    def paarung_bauen(cls, geschlecht, bauart):
        u"""`{zu (27087,), g9_punkte, g9_normalen, g9_rahmen, massstab}` an den Grundfiguren."""
        from GarmentCode.koerperdienst import Garmentkoerper
        g9 = G9garmentfigur({})
        g9_punkte = g9.punkte()
        g9_normalen = Hbtraeger.normalen(g9_punkte, g9.dreiecke())
        hb = Hbtraeger.laden(geschlecht, bauart, {}, {})
        hb_seg = Garmentkoerper.segmente(geschlecht) or {}
        massstab = float(hb['punkte'][:, 1].max() / max(g9_punkte[:, 1].max(), 1e-6))
        skaliert = cls.geschaetzt(g9, g9_punkte, massstab)
        zu = np.full(len(g9_punkte), -1, dtype=np.int64)
        ganz = G9kollision.baum(hb['punkte'])
        for teil, g9_liste in g9.segmente().items():
            g9_idx = np.asarray(g9_liste, dtype=np.int64)
            hb_idx = np.asarray(hb_seg.get(teil) or [], dtype=np.int64)
            if not len(g9_idx):
                continue
            if len(hb_idx) < cls.KANDIDATEN:
                _w, naechster = G9kollision.naechste(ganz, skaliert[g9_idx])
                zu[g9_idx] = naechster
                continue
            _w, kand = G9kollision.naechste(G9kollision.baum(hb['punkte'][hb_idx]),
                                            skaliert[g9_idx], k=cls.KANDIDATEN)
            kand = hb_idx[kand]                                   # (n, K) HB-Nummern
            einig = np.einsum('ik,ijk->ij', g9_normalen[g9_idx], hb['normalen'][kand]) > cls.EINIG
            erster = np.where(einig.any(axis=1), einig.argmax(axis=1), 0)
            zu[g9_idx] = kand[np.arange(len(g9_idx)), erster]
        logger.info('Daz auf HumanBody: Paarung %s/%s — %d Genesis-Punkte, Massstab %.3f',
                    geschlecht, bauart, len(zu), massstab)
        return {'zu': zu, 'g9_punkte': g9_punkte, 'g9_normalen': g9_normalen,
                'g9_rahmen': Hbtraeger.rahmen(g9_normalen), 'g9_baum': G9kollision.baum(g9_punkte),
                'massstab': massstab}

    @classmethod
    def geschaetzt(cls, g9, g9_punkte, massstab):
        u"""Die Genesis-Punkte in der HumanBody-Lage: ueber die Knochenrahmen
        (`G9hbknochen`), ohne Rahmen nach Hoehenmassstab."""
        haut = g9.haut()
        knochen = np.asarray(haut['knochen'])
        staerkster = np.asarray(haut['index'])[np.arange(len(g9_punkte)),
                                                np.asarray(haut['gewicht']).argmax(axis=1)]
        rahmen = G9hbknochen(G9formung({}).skelett().bauen()['knochen'],
                             Skelettgeometrie.holen().compute_world_transforms(), massstab)
        aus, getroffen = rahmen.schaetzen(g9_punkte, knochen[staerkster])
        aus[~getroffen] = g9_punkte[~getroffen] * massstab
        return aus

    # -------------------------------------------------------- Uebertragen

    def uebertragen(self, punkte_g9):
        u"""(M, 3) Stoffpunkte auf dem Genesis-Grundkoerper -> auf der HumanBody-Figur."""
        p = np.asarray(punkte_g9, dtype=np.float64)
        if not len(p):
            return p
        paar, figur = self.paarung, self.figur()
        hb_rahmen = Hbtraeger.rahmen(figur['normalen'])
        abstand, nachbar = G9kollision.naechste(paar['g9_baum'], p, k=self.NACHBARN)
        abstand = np.asarray(abstand, dtype=np.float64).reshape(len(p), -1)
        nachbar = np.asarray(nachbar).reshape(len(p), -1)
        gewicht = 1.0 / np.maximum(abstand, 1e-6)
        gewicht /= gewicht.sum(axis=1, keepdims=True)
        aus = np.zeros_like(p)
        for k in range(nachbar.shape[1]):
            j = nachbar[:, k]
            versatz = p - paar['g9_punkte'][j]
            anteile = np.einsum('ij,iaj->ia', versatz, paar['g9_rahmen'][j]) * paar['massstab']
            ziel = paar['zu'][j]
            neu = figur['punkte'][ziel] + np.einsum('ia,iaj->ij', anteile, hb_rahmen[ziel])
            aus += gewicht[:, k:k + 1] * neu
        return p + self.geglaettet(p, aus - p)

    @classmethod
    def geglaettet(cls, punkte, feld):
        u"""Das Verschiebungsfeld je Punkt als Mittel ueber seine GLAETTUNG naechsten
        Stoffpunkte — die Form des Stuecks bleibt, das Rauschen der Paarung geht."""
        if len(punkte) <= cls.GLAETTUNG:
            return feld
        _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte, k=cls.GLAETTUNG)
        return feld[np.asarray(nachbar)].mean(axis=1)

    def haut(self, punkte):
        u"""`{knochen, index (N, 4), gewicht (N, 4)}` vom naechsten HumanBody-Dreieck."""
        from GarmentCode.anziehen import Anziehen
        figur = self.figur()
        rig = Anziehen(figur['punkte'], figur['dreiecke'], figur['gewichte'],
                       figur['knochen']).anziehen(np.asarray(punkte, dtype=np.float64))
        index = np.zeros((len(punkte), 4), dtype=np.int64)
        gewicht = np.zeros((len(punkte), 4), dtype=np.float64)
        for nr, paare in enumerate(rig['gewichte']):
            beste = sorted((pa for pa in paare if pa[1] > 0), key=lambda pa: -pa[1])[:4]
            summe = sum(w for _k, w in beste) or 1.0
            for spalte, (knochen, w) in enumerate(beste):
                index[nr, spalte], gewicht[nr, spalte] = int(knochen), float(w) / summe
        return {'knochen': figur['knochen'], 'index': index, 'gewicht': gewicht}

    def koerperflaeche(self):
        u"""(Punkte, Normalen, Baum) der sichtbaren HumanBody-Haut fuer `G9kollision`."""
        figur = self.figur()
        if 'baum' not in figur:
            figur['baum'] = G9kollision.baum(figur['fein'])
        return figur['fein'], figur['fein_normalen'], figur['baum']

    #: Hoechstens so viele Durchgaenge beim Heben (`hinaus`).
    DURCHGAENGE = 12

    def hinaus(self, punkte, abstand):
        u"""Aus der Haut heben, bis kein Punkt mehr drin ist — hoechstens
        DURCHGAENGE. Zwei Durchgaenge (`G9kollision`) reichen nicht, wo die
        HumanBody-Brust 5 cm weiter vorsteht als die von Genesis: Ein Punkt
        an ihrer Wurzel wird zum Brustkorb hin gehoben und steckt danach
        noch immer in der Brust (gemessen: 28 Punkte bis 15 mm tief)."""
        haut, normalen, baum = self.koerperflaeche()
        aus = np.asarray(punkte, dtype=np.float64)
        for _ in range(self.DURCHGAENGE):
            aus = G9kollision.hinaus(aus, haut, normalen, abstand=abstand, baum=baum,
                                     durchgaenge=1)
            if G9kollision.tiefe(aus, haut, normalen, baum).min() >= abstand - 1e-4:
                break
        return aus
