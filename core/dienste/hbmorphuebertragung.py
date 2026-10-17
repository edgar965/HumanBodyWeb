# -*- coding: utf-8 -*-
u"""Hbmorphuebertragung — ein HumanBody-Verschiebungsfeld auf den Genesis-9-Kaefig legen (aus `Hbmorpheaufgenesis` herausgeloest, 17.10.2026).

Die Zuordnung (Paarung der Grundfiguren, Kandidaten je Punkt, Normalen-Einigkeit) und die zwei Wege der Uebertragung:

- **Rahmen** (Vorgabe): Das Delta wird in den Rahmen (Normale, Aufwaerts, Quer) des HumanBody-Punkts zerlegt und im Rahmen des Genesis-Punkts
  wieder aufgebaut — ein Delta entlang der Normale bleibt entlang der Normale, auch wo die Figuren anders stehen. Richtig fuer Formregler.
- **Welt**: das Delta unzerlegt, als gewichtetes Mittel der Kandidaten. Richtig fuer grosse, fast starre Verschiebungen (Body Size, Laengen): Die Zerlegung
  kippt sie dort, wo die Normalen der beiden Netze verschieden stehen — Zehen und Fuss bekamen aus −4,5 mm senkrecht −56 mm (Body Size −1, 17.10.2026,
  `ProjektTemp/_wegwerf/familien/hb_zacken_zerlegen.py`).

PUNKTE OHNE GEGENSTUECK (`ungueltig`, 17.10.2026): Genesis hat Mundinnenraum, Augenhoehlen und gespreizte Zehen, die HumanBody nicht oder anders hat. Dort
greift die Zuordnung einen Punkt mit gegenlaeufiger Normale oder weit weg — das Vorzeichen jedes Deltas entlang der Normale kippte (Body Size −1: +236 mm statt
−500 mm am Mundinnenraum, die Hoehe des Netzes stieg auf 1,825 m statt zu sinken). Solche Punkte (2.271 von 25.182) werden aus ihren Nachbarn gefuellt
(`G9feldputz.fuellen`), Reste von Zacken auf den Median der Nachbarn gesetzt (`putzen`).
"""
import numpy as np
from Genesis9.basisnetz import G9basisnetz
from Genesis9.feldputz import G9feldputz
from Genesis9.kollision import G9kollision

from .g9aufhumanbody import G9aufhumanbody
from .hbtraeger import Hbtraeger

__all__ = ['Hbmorphuebertragung']


class Hbmorphuebertragung:
    u"""Zuordnung HumanBody -> Genesis-Kaefig und die Uebertragung eines Felds."""

    GESCHLECHT = 'female'
    BAUART = None
    KANDIDATEN = 6
    EINIG = G9aufhumanbody.EINIG
    GLAETTUNG = 6
    DURCHGAENGE = 1
    #: Deltas unter dieser Laenge (m) gelten als null — Rauschen der Paarung.
    NULL_M = 2e-5
    #: Weiter als das (m) vom Kaefigpunkt entfernt liegt kein HumanBody-Gegenstueck mehr (gemessen 17.10.2026: 572 von 25.182 Punkten).
    LUECKE_M = 0.05

    def __init__(self):
        self._paar = None
        self._hb = None
        self._ursprung = None
        self._nachbar = None
        self._zuordnung = None
        self._naehe = None
        self._ohne = None
        self._luecke = None
        self._putz = None

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
            self._ursprung = np.asarray(G9basisnetz.holen().netzstufe(0).ursprung, dtype=np.int64)
        return self._ursprung

    def nachbarn(self):
        u"""(25182, GLAETTUNG) die naechsten Kaefigpunkte je Kaefigpunkt."""
        if self._nachbar is None:
            punkte = G9basisnetz.holen().punkte
            _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte, k=self.GLAETTUNG)
            self._nachbar = np.asarray(nachbar, dtype=np.int64)
        return self._nachbar

    def zuordnung(self):
        u"""`(kandidaten (27087, K), gewichte (27087, K))` — je Genesis-Browserpunkt seine HumanBody-Punkte desselben Koerperteils, Gewichte summieren zu 1."""
        if self._zuordnung is not None:
            return self._zuordnung
        paar, hb = self.paarung(), self.humanbody()
        zahl = len(paar['g9_punkte'])
        kand = np.tile(paar['zu'][:, None], (1, self.KANDIDATEN))
        gewicht = np.zeros((zahl, self.KANDIDATEN))
        gewicht[:, 0] = 1.0
        #: Abstand (m, HumanBody-Lage) des naechsten Kandidaten je Genesis-Browserpunkt — gross = kein Gegenstueck (Mundinnenraum, Zehen).
        self._naehe = np.full(zahl, np.inf)
        self._ohne = np.zeros(zahl, dtype=bool)
        for _teil, (g9_idx, hb_idx) in paar['segmente'].items():
            if not len(g9_idx) or len(hb_idx) < self.KANDIDATEN:
                continue
            abstand, nr = G9kollision.naechste(G9kollision.baum(hb['punkte'][hb_idx]), paar['skaliert'][g9_idx], k=self.KANDIDATEN)
            self._naehe[g9_idx] = np.asarray(abstand, dtype=np.float64)[:, 0]
            nr = hb_idx[np.asarray(nr)]
            w = 1.0 / np.maximum(np.asarray(abstand, dtype=np.float64), 1e-4)
            einig = np.einsum('ik,ijk->ij', paar['g9_normalen'][g9_idx], hb['normalen'][nr]) > self.EINIG
            keiner = ~einig.any(axis=1)
            einig[keiner, 0] = True                 # sonst der naechste, wie `zu`
            # ... aber mit gegenlaeufiger Normale kippt das Vorzeichen jedes Deltas entlang der Normale — fuer Felder zaehlt so ein Punkt als „ohne Gegenstueck“.
            self._ohne[np.asarray(g9_idx)[keiner]] = True
            w = np.where(einig, w, 0.0)
            kand[g9_idx] = nr
            gewicht[g9_idx] = w / w.sum(axis=1, keepdims=True)
        self._zuordnung = (kand, gewicht)
        return self._zuordnung

    def putz(self):
        if self._putz is None:
            self._putz = G9feldputz.vom_kaefig()
        return self._putz

    def ungueltig(self):
        u"""(25182,) True, wo es kein HumanBody-Gegenstueck gibt: naechster Kandidat weiter als `LUECKE_M` oder nur mit gegenlaeufiger Normale."""
        if self._luecke is None:
            self.zuordnung()
            kaefig = np.zeros(len(G9basisnetz.holen().punkte))
            np.maximum.at(kaefig, self.ursprung(), np.where(np.isfinite(self._naehe), self._naehe, 9.0))
            ohne = np.zeros(len(kaefig))
            np.maximum.at(ohne, self.ursprung(), self._ohne.astype(float))
            self._luecke = (kaefig > self.LUECKE_M) | (ohne > 0)
        return self._luecke

    # ------------------------------------------------------------ Uebertragen

    def uebertragen(self, hb_delta, welt=False):
        u"""(25182, 3) das HumanBody-Delta auf dem Genesis-Kaefig, gefuellt, geglaettet, geputzt. `welt`: siehe Kopf der Datei."""
        paar, hb = self.paarung(), self.humanbody()
        kand, gewicht = self.zuordnung()
        if welt:
            browser = np.einsum('ik,ikj->ij', gewicht, hb_delta[kand]) / paar['massstab']
        else:
            # Je Kandidat: Delta in seinem HumanBody-Rahmen zerlegen (Anteile Normale, Aufwaerts, Quer), gewichtet summieren, im Genesis-Rahmen aufbauen.
            anteile = np.einsum('ikaj,ikj->ika', hb['rahmen'][kand], hb_delta[kand])
            anteile = np.einsum('ika,ik->ia', anteile, gewicht)
            browser = np.einsum('ia,iaj->ij', anteile, paar['g9_rahmen']) / paar['massstab']
        zahl = len(G9basisnetz.holen().punkte)
        summe = np.zeros((zahl, 3))
        anzahl = np.zeros(zahl)
        np.add.at(summe, self.ursprung(), browser)
        np.add.at(anzahl, self.ursprung(), 1.0)
        feld = summe / np.maximum(anzahl, 1.0)[:, None]
        putz = self.putz()
        feld = putz.fuellen(feld, self.ungueltig())
        nachbar = self.nachbarn()
        for _ in range(self.DURCHGAENGE):
            feld = feld[nachbar].mean(axis=1)
        feld, _zacken = putz.putzen(feld)
        feld[np.linalg.norm(feld, axis=1) < self.NULL_M] = 0.0
        return feld
