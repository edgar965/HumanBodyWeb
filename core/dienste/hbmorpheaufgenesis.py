# -*- coding: utf-8 -*-
u"""Hbmorpheaufgenesis — die HumanBody-Regler auf den Genesis-9-Kaefig uebertragen.

WARUM (Edgar, 20.09.2026: „kannst du diese Body Shapes nicht selber bauen?
… HumanBody hat doch mehr Regler als MakeHuman?" — „fang schon mal an mit
dem Bau der HumanBody Regler fuer Genesis"): Die Daz-Bibliothek hat ohne
Kaufpakete keine Einzelformregler; HumanBody hat 204 (MB-Lab). Ein Regler
ist eine Verschiebung je Netzpunkt — und die Paarung der beiden Grundnetze
gibt es schon: `G9aufhumanbody.paarung_bauen` (fuer Daz-Kleider auf
HumanBody) kennt zu jedem Genesis-Browserpunkt seinen HumanBody-Punkt, mit
lokalen Rahmen (Normale, Aufwaerts, Quer) auf beiden Seiten.

DIE UEBERTRAGUNG ist der Kleiderweg rueckwaerts, nur ohne Versatz:

    1. HumanBody-Delta des Reglers je Punkt (`CharacterState`, +1 und -1
       gegen die Grundfigur — so sind Kombis wie BreastMass x BreastTone
       gleich richtig, MB-Lab rechnet sie selbst), in Three-Lage.
    2. Je Genesis-Browserpunkt die KANDIDATEN naechsten HumanBody-Punkte
       DESSELBEN Koerperteils um seine geschaetzte Lage (`skaliert`,
       `segmente` der Paarung), gewichtet 1/Abstand; Kandidaten mit
       gegenlaeufiger Normale (Skalarprodukt < EINIG: Ober- gegen Unterlippe,
       Innenseite gegen Aussenseite) zaehlen nicht — es sei denn, keiner
       stimmt, dann der naechste. Das ist die Paarung der Kleider (`zu`, ein
       Punkt), nur ueber mehrere Punkte: Mit EINEM Punkt je Genesis-Punkt
       kamen nur 7.894 der 18.210 HumanBody-Punkte je vor, und ein Morph auf
       den uebrigen war weg (Ears Lobe 7,2 -> 0,1 mm, Mouth SizeX 14,7 -> 3,5
       mm — gemessen 20.09.2026, `_wegwerf/hbmorphe_vergleich.py`).
    3. Jedes Kandidaten-Delta in DESSEN Rahmen zerlegen und im Rahmen des
       Genesis-Punkts wieder zusammensetzen — ein Delta entlang der Normale
       bleibt entlang der Normale, auch wo die Figuren anders stehen (Arme,
       Beine). Geteilt durch den Hoehenmassstab.
    4. Von den 27.087 Browserpunkten (Naehte doppelt) auf die 25.182
       Kaefigpunkte mitteln (`ursprung`), dann das Feld ueber die GLAETTUNG
       naechsten Kaefigpunkte glaetten, DURCHGAENGE mal — HumanBody ist
       groeber, ohne Glaettung stuende die Verschiebung stufig auf dem
       feineren Kaefig.
    5. Ablegen als `hb:<HumanBody-Name>` (`G9hbmorphe.ablegen`), zweiseitig.
       Ein Regler, der keinen Kaefigpunkt erreicht (Iris, Zaehne — bei
       Genesis Anhaenge, nicht Koerper), wird uebergangen.
    6. Ein Regler, der Gelenke verschiebt (`Hbmorphrig`: Kopfgelenk ab 5 mm
       oder ein Knochenabstand ab 7,5 mm — Body Size, alle Laengen, Winkel),
       bekommt NUR den Steckbrief (`rig: true`, mit den Millimetern), keine
       Deltas: ohne Skelett-Nachzug blaehte er die projizierten Anhaenge
       auf (Mund 6,8 -> 94 cm bei Body Size -100 %, Edgar mit Bild,
       20.09.2026). `bestand.json` fuehrt sie unter `rig_uebergangen`.

Was NICHT drin ist: der Umfangsmassstab je Rumpfhoehe (`G9hbsitz`), den die
Kleider brauchen — eine Verschiebung von 2 cm bleibt 2 cm mal Hoehenmassstab.
Und die Grundfigur ist die weibliche Paarung (`female`, Standardbauart);
die maennlichen HumanBody-Pakete tragen dieselben Reglernamen.

Bauen: `manage.py hbmorphe_bauen` (Ablage `Genesis9/ablage/hbmorphe/`,
mit `bestand.json`). Gemessen wird beim ersten Lauf, siehe Befehl.
"""
import logging
import os
import time

import numpy as np
from Genesis9.basisnetz import G9basisnetz
from Genesis9.hbmorphe import G9hbmorphe
from Genesis9.kollision import G9kollision

from .g9aufhumanbody import G9aufhumanbody
from .hbmorphrig import Hbmorphrig
from .hbtraeger import Hbtraeger

logger = logging.getLogger('core')

__all__ = ['Hbmorpheaufgenesis']


class Hbmorpheaufgenesis:
    u"""Alle HumanBody-Regler als Genesis-9-Morphs bauen."""

    GESCHLECHT = 'female'
    BAUART = None
    KANDIDATEN = 6
    EINIG = G9aufhumanbody.EINIG
    GLAETTUNG = 6
    DURCHGAENGE = 1
    #: Deltas unter dieser Laenge (m) gelten als null — Rauschen der Paarung.
    NULL_M = 2e-5

    def __init__(self, melden=None):
        self.melden = melden or (lambda *a: None)
        self._paar = None
        self._hb = None
        self._ursprung = None
        self._nachbar = None
        self._zuordnung = None
        self._zustand = None
        self._basis = None
        self._rig = None

    # ---------------------------------------------------------- Vorbereiten

    def paarung(self):
        if self._paar is None:
            self._paar = G9aufhumanbody.paarung_holen(self.GESCHLECHT, self.BAUART)
        return self._paar

    def humanbody(self):
        u"""`{punkte, rahmen}` der HumanBody-Grundfigur (Three-Lage)."""
        if self._hb is None:
            figur = Hbtraeger.laden(self.GESCHLECHT, self.BAUART, {}, {})
            self._hb = {'punkte': figur['punkte'], 'normalen': figur['normalen'],
                        'rahmen': Hbtraeger.rahmen(figur['normalen'])}
        return self._hb

    def ursprung(self):
        u"""(27087,) Browserpunkt -> Kaefigpunkt."""
        if self._ursprung is None:
            self._ursprung = np.asarray(G9basisnetz.holen().netzstufe(0).ursprung,
                                        dtype=np.int64)
        return self._ursprung

    def nachbarn(self):
        u"""(25182, GLAETTUNG) die naechsten Kaefigpunkte je Kaefigpunkt."""
        if self._nachbar is None:
            punkte = G9basisnetz.holen().punkte
            _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte,
                                               k=self.GLAETTUNG)
            self._nachbar = np.asarray(nachbar, dtype=np.int64)
        return self._nachbar

    def zuordnung(self):
        u"""`(kandidaten (27087, K), gewichte (27087, K))` — je Genesis-Browserpunkt
        seine HumanBody-Punkte desselben Koerperteils, Gewichte summieren zu 1."""
        if self._zuordnung is not None:
            return self._zuordnung
        paar, hb = self.paarung(), self.humanbody()
        zahl = len(paar['g9_punkte'])
        kand = np.tile(paar['zu'][:, None], (1, self.KANDIDATEN))
        gewicht = np.zeros((zahl, self.KANDIDATEN))
        gewicht[:, 0] = 1.0
        for _teil, (g9_idx, hb_idx) in paar['segmente'].items():
            if not len(g9_idx) or len(hb_idx) < self.KANDIDATEN:
                continue
            abstand, nr = G9kollision.naechste(G9kollision.baum(hb['punkte'][hb_idx]),
                                               paar['skaliert'][g9_idx], k=self.KANDIDATEN)
            nr = hb_idx[np.asarray(nr)]
            w = 1.0 / np.maximum(np.asarray(abstand, dtype=np.float64), 1e-4)
            einig = np.einsum('ik,ijk->ij', paar['g9_normalen'][g9_idx],
                              hb['normalen'][nr]) > self.EINIG
            keiner = ~einig.any(axis=1)
            einig[keiner, 0] = True                 # sonst der naechste, wie `zu`
            w = np.where(einig, w, 0.0)
            kand[g9_idx] = nr
            gewicht[g9_idx] = w / w.sum(axis=1, keepdims=True)
        self._zuordnung = (kand, gewicht)
        return self._zuordnung

    def zustand(self):
        u"""Der HumanBody-Rechner auf der Grundfigur der Paarung."""
        if self._zustand is None:
            from GarmentCode.dienst import GarmentcodeDienst
            from humanbody_core import CharacterState

            from .charakterdaten import Charakterdaten
            zustand = CharacterState(Charakterdaten.morphdaten(),
                                     Charakterdaten.voreinstellungen())
            zustand.set_body_type(self.BAUART or GarmentcodeDienst.BAUART.get(
                self.GESCHLECHT, 'Female_Caucasian'))
            self._basis = Hbtraeger.three(np.array(zustand.compute(), dtype=np.float64))
            abweichung = float(np.abs(self._basis - self.humanbody()['punkte']).max())
            if abweichung > 1e-6:
                raise ValueError('HumanBody-Grundfigur der Paarung und des Rechners '
                                 'weichen ab (%.4f m)' % abweichung)
            self._zustand = zustand
        return self._zustand

    # ------------------------------------------------------------ Regler

    def namen(self):
        return [m['name'] for m in self.zustand().get_morph_list()]

    def hb_delta(self, name, wert):
        u"""(18210, 3) Verschiebung des Reglers bei `wert` gegen die Grundfigur."""
        zustand = self.zustand()
        zustand.set_morph(name, float(wert))
        try:
            punkte = Hbtraeger.three(np.array(zustand.compute(), dtype=np.float64))
        finally:
            zustand.set_morph(name, 0.0)
        return punkte - self._basis

    def uebertragen(self, hb_delta):
        u"""(25182, 3) das HumanBody-Delta auf dem Genesis-Kaefig, geglaettet."""
        paar, hb = self.paarung(), self.humanbody()
        kand, gewicht = self.zuordnung()
        # Je Kandidat: Delta in seinem HumanBody-Rahmen zerlegen (Anteile Normale,
        # Aufwaerts, Quer), gewichtet summieren, im Genesis-Rahmen aufbauen.
        anteile = np.einsum('ikaj,ikj->ika', hb['rahmen'][kand], hb_delta[kand])
        anteile = np.einsum('ika,ik->ia', anteile, gewicht)
        browser = np.einsum('ia,iaj->ij', anteile, paar['g9_rahmen']) / paar['massstab']
        ursprung = self.ursprung()
        zahl = len(G9basisnetz.holen().punkte)
        summe = np.zeros((zahl, 3))
        anzahl = np.zeros(zahl)
        np.add.at(summe, ursprung, browser)
        np.add.at(anzahl, ursprung, 1.0)
        feld = summe / np.maximum(anzahl, 1.0)[:, None]
        nachbar = self.nachbarn()
        for _ in range(self.DURCHGAENGE):
            feld = feld[nachbar].mean(axis=1)
        feld[np.linalg.norm(feld, axis=1) < self.NULL_M] = 0.0
        return feld

    # -------------------------------------------------------------- Bauen

    def rig(self):
        if self._rig is None:
            self._rig = Hbmorphrig()
        return self._rig

    def bauen(self):
        u"""Alle Regler bauen; gibt `[{name, punkte, plus_mm, minus_mm}]` zurueck."""
        start = time.perf_counter()
        namen = self.namen()
        G9hbmorphe.leeren()
        aus, rig_weg = [], []
        for nr, name in enumerate(namen, 1):
            plus = self.uebertragen(self.hb_delta(name, 1.0))
            minus = self.uebertragen(self.hb_delta(name, -1.0))
            nummern = np.nonzero((np.abs(plus).max(axis=1) > 0) | (np.abs(minus).max(axis=1) > 0))[0]
            if not len(nummern):
                logger.info('HB-Morphs: %s erreicht keinen Kaefigpunkt — uebergangen', name)
                self.melden(nr, len(namen), name, None)
                continue
            mass = self.rig().beide(nummern, plus[nummern], minus[nummern])
            quelle = {'quelle': 'HumanBody %s' % self.zustand().body_type, **mass}
            if mass['rig']:
                G9hbmorphe.steckbrief_schreiben(name, quelle)
                rig_weg.append(name)
                logger.info('HB-Morphs: %s verschiebt Gelenke (Kopf %.1f mm, Laenge %.1f mm) — '
                            'uebergangen, bis das Skelett folgt', name, mass['kopf_mm'], mass['laenge_mm'])
                self.melden(nr, len(namen), name, None)
                continue
            G9hbmorphe.ablegen(name, nummern, plus[nummern], minus[nummern], quelle)
            brief = G9hbmorphe.steckbrief(name)
            aus.append({'name': name, 'punkte': brief['punkte'],
                        'plus_mm': brief['plus_mm'], 'minus_mm': brief['minus_mm']})
            self.melden(nr, len(namen), name, brief)
        G9hbmorphe.bestand_schreiben({
            'paarung': '%s/%s' % (self.GESCHLECHT, self.BAUART or '-'),
            'bauart': self.zustand().body_type,
            'hb_stand': self.hb_stand(), 'zahl': len(aus),
            'rig_uebergangen': rig_weg,
            'rig_grenzen': {'kopf_mm': Hbmorphrig.KOPF_MM, 'laenge_mm': Hbmorphrig.LAENGE_MM},
            'massstab': round(float(self.paarung()['massstab']), 4),
            'kandidaten': self.KANDIDATEN,
            'glaettung': {'nachbarn': self.GLAETTUNG, 'durchgaenge': self.DURCHGAENGE},
            'sekunden': round(time.perf_counter() - start, 1)})
        logger.info('HB-Morphs auf Genesis 9: %d Regler in %.1f s nach %s',
                    len(aus), time.perf_counter() - start, G9hbmorphe.ordner())
        return aus

    @staticmethod
    def hb_stand():
        u"""Juengste Aenderung (ns) der HumanBody-Morphpakete — der Bestand."""
        from django.conf import settings
        wurzel = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'morphs')
        juengste = 0
        for ordner, _u, dateien in os.walk(wurzel):
            for datei in dateien:
                juengste = max(juengste, os.stat(os.path.join(ordner, datei)).st_mtime_ns)
        return juengste

    @classmethod
    def veraltet(cls):
        u"""Fehlt die Ablage oder ist sie aelter als die HumanBody-Morphs?"""
        bestand = G9hbmorphe.bestand()
        return (not bestand or bestand.get('fassung') != G9hbmorphe.FASSUNG
                or bestand.get('hb_stand', 0) < cls.hb_stand())
