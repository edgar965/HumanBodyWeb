# -*- coding: utf-8 -*-
u"""Hbmorphuebertragung — ein HumanBody-Verschiebungsfeld auf den Genesis-9-Kaefig legen (aus `Hbmorpheaufgenesis` herausgeloest, 17.10.2026).

Die Zuordnung (Paarung der Grundfiguren, Kandidaten je Punkt, Normalen-Einigkeit: `Hbzuordnung`) und die zwei Wege der Uebertragung:

- **Rahmen** (Vorgabe): Das Delta wird in den Rahmen (Normale, Aufwaerts, Quer) des HumanBody-Punkts zerlegt und im Rahmen des Genesis-Punkts
  wieder aufgebaut — ein Delta entlang der Normale bleibt entlang der Normale, auch wo die Figuren anders stehen. Richtig fuer Formregler.
- **Welt**: das Delta unzerlegt, als gewichtetes Mittel der Kandidaten. Richtig fuer grosse, fast starre Verschiebungen (Body Size, Laengen): Die Zerlegung
  kippt sie dort, wo die Normalen der beiden Netze verschieden stehen — Zehen und Fuss bekamen aus −4,5 mm senkrecht −56 mm (Body Size −1, 17.10.2026,
  `ProjektTemp/_wegwerf/familien/hb_zacken_zerlegen.py`).

PUNKTE OHNE GEGENSTUECK (`ungueltig`, 17.10.2026): Genesis hat Mundinnenraum, Augenhoehlen und gespreizte Zehen, die HumanBody nicht oder anders hat. Dort
greift die Zuordnung einen Punkt mit gegenlaeufiger Normale oder weit weg — das Vorzeichen jedes Deltas entlang der Normale kippte (Body Size −1: +236 mm statt
−500 mm am Mundinnenraum, die Hoehe des Netzes stieg auf 1,825 m statt zu sinken). Solche Punkte (2.271 von 25.182) werden aus ihren Nachbarn gefuellt
(`G9feldputz.fuellen`), Reste von Zacken auf den Median der Nachbarn gesetzt (`putzen`).

VERSCHLUCKTE REGLER (`uebertragen_wirksam`, 17.10.2026): Ein kleiner Gesichtsregler (3 mm Hub auf 1–2 cm) fiel zwischen die Punkte, weil Genesis' Gesicht 9–25 mm anders sitzt
als HumanBodys (`Eyes_innerSinus`: 2,62 mm in der Quelle, 0,000 auf Genesis). Kommt ein Regler mit weniger als `RUECKFALL` seiner Staerke an, wird er mit der Kopfausrichtung
(`Hbzuordnung(ausgerichtet=True)`) neu uebertragen und die Fassung genommen, die mindestens `FAKTOR`-mal staerker ist. Alle anderen Regler bleiben bitgleich.
"""
import numpy as np
from Genesis9.basisnetz import G9basisnetz
from Genesis9.feldputz import G9feldputz
from Genesis9.kollision import G9kollision

from .g9aufhumanbody import G9aufhumanbody
from .hbtraeger import Hbtraeger
from .hbvorwaerts import Hbvorwaerts
from .hbzuordnung import Hbzuordnung

__all__ = ['Hbmorphuebertragung']


class Hbmorphuebertragung:
    u"""Zuordnung HumanBody -> Genesis-Kaefig und die Uebertragung eines Felds."""

    GESCHLECHT = 'female'
    BAUART = None
    KANDIDATEN = Hbzuordnung.KANDIDATEN
    EINIG = G9aufhumanbody.EINIG
    GLAETTUNG = 6
    DURCHGAENGE = 1
    #: Deltas unter dieser Laenge (m) gelten als null — Rauschen der Paarung.
    NULL_M = 2e-5
    #: Kommt weniger als dieser Anteil der Quell-Staerke an, wird mit der Kopfausrichtung neu uebertragen ...
    RUECKFALL = 0.25
    #: ... und die ausgerichtete Fassung genommen, wenn sie mindestens so viel mal staerker ist.
    FAKTOR = 2.0

    def __init__(self):
        self._paar = None
        self._hb = None
        self._ursprung = None
        self._nachbar = None
        self._zuordnungen = {}
        self._vorwaerts = {}
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

    def zuordnungsobjekt(self, ausgerichtet=False):
        u"""Die `Hbzuordnung` der Paarung, mit oder ohne Kopfausrichtung (gemerkt)."""
        if ausgerichtet not in self._zuordnungen:
            self._zuordnungen[ausgerichtet] = Hbzuordnung(self.paarung(), self.humanbody(), self.ursprung(), len(G9basisnetz.holen().punkte), ausgerichtet)
        return self._zuordnungen[ausgerichtet]

    def zuordnung(self, ausgerichtet=False):
        u"""`(kandidaten (27087, K), gewichte (27087, K))` — je Genesis-Browserpunkt seine HumanBody-Punkte desselben Koerperteils, Gewichte summieren zu 1."""
        return self.zuordnungsobjekt(ausgerichtet).kandidaten()

    def ungueltig(self, ausgerichtet=False):
        u"""(25182,) True, wo es kein HumanBody-Gegenstueck gibt (siehe `Hbzuordnung.ungueltig`)."""
        return self.zuordnungsobjekt(ausgerichtet).ungueltig()

    def putz(self):
        if self._putz is None:
            self._putz = G9feldputz.vom_kaefig()
        return self._putz

    # ------------------------------------------------------------ Uebertragen

    def uebertragen(self, hb_delta, welt=False, ausgerichtet=False):
        u"""(25182, 3) das HumanBody-Delta auf dem Genesis-Kaefig, gefuellt, geglaettet, geputzt. `welt`: siehe Kopf der Datei."""
        paar, hb = self.paarung(), self.humanbody()
        kand, gewicht = self.zuordnung(ausgerichtet)
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
        feld = putz.fuellen(feld, self.ungueltig(ausgerichtet))
        nachbar = self.nachbarn()
        for _ in range(self.DURCHGAENGE):
            feld = feld[nachbar].mean(axis=1)
        feld, _zacken = putz.putzen(feld)
        feld[np.linalg.norm(feld, axis=1) < self.NULL_M] = 0.0
        return feld

    @staticmethod
    def staerke(feld):
        u"""Groesste Verschiebung (m) eines Felds."""
        return float(np.linalg.norm(np.asarray(feld, dtype=np.float64), axis=1).max()) if len(feld) else 0.0

    def vorwaerts(self, ausgerichtet=False):
        u"""Die `Hbvorwaerts` zur Paarung, mit oder ohne Kopfausrichtung (gemerkt)."""
        if ausgerichtet not in self._vorwaerts:
            such = self.zuordnungsobjekt(ausgerichtet).suchpunkte()
            self._vorwaerts[ausgerichtet] = Hbvorwaerts(self.paarung(), self.humanbody(), such, self.ursprung(), len(G9basisnetz.holen().punkte), self.nachbarn())
        return self._vorwaerts[ausgerichtet]

    def uebertragen_vorwaerts(self, hb_delta, ausgerichtet=False):
        u"""(25182, 3) das Delta vorwaerts auf den Kaefig gelegt (siehe `Hbvorwaerts`), geputzt."""
        feld, _zacken = self.putz().putzen(self.vorwaerts(ausgerichtet).uebertragen(hb_delta))
        feld[np.linalg.norm(feld, axis=1) < self.NULL_M] = 0.0
        return feld

    def uebertragen_wirksam(self, hb_plus, hb_minus):
        u"""`(plus, minus, weg)` — beide Richtungen eines Reglers. `weg`: 'rahmen' (normal), 'ausgerichtet', 'vorwaerts' oder 'vorwaerts_ausgerichtet' (siehe Kopf der Datei).

        Reihenfolge der Rueckfaelle: Kopfausrichtung, dann die Vorwaertsuebertragung (ohne und mit Ausrichtung); genommen wird die staerkste Fassung, die mindestens `FAKTOR`-mal staerker
        ist als die bisher beste."""
        plus, minus = self.uebertragen(hb_plus), self.uebertragen(hb_minus)
        quelle = max(self.staerke(hb_plus), self.staerke(hb_minus))
        beste = max(self.staerke(plus), self.staerke(minus))
        weg = 'rahmen'
        if quelle <= 0 or beste >= self.RUECKFALL * quelle:
            return plus, minus, weg
        versuche = (('ausgerichtet', lambda d: self.uebertragen(d, ausgerichtet=True)),
                    ('vorwaerts', lambda d: self.uebertragen_vorwaerts(d)),
                    ('vorwaerts_ausgerichtet', lambda d: self.uebertragen_vorwaerts(d, ausgerichtet=True)))
        for name, uebertragen in versuche:
            if beste >= self.RUECKFALL * quelle:
                break
            p2, m2 = uebertragen(hb_plus), uebertragen(hb_minus)
            neu = max(self.staerke(p2), self.staerke(m2))
            if neu > 0 and neu >= self.FAKTOR * beste:
                plus, minus, beste, weg = p2, m2, neu, name
        return plus, minus, weg
