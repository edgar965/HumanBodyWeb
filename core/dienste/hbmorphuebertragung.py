# -*- coding: utf-8 -*-
u"""Hbmorphuebertragung — ein HumanBody-Verschiebungsfeld auf den Genesis-9-Kaefig legen (aus `Hbmorpheaufgenesis` herausgeloest, 17.10.2026).

Die Zuordnung (Paarung der Grundfiguren, Kandidaten je Punkt, Normalen-Einigkeit: `Hbzuordnung`) und die Uebertragung: das Delta unzerlegt (Weltraum), als
gewichtetes Mittel der Kandidaten, geteilt durch den Hoehenmassstab.

EIN WEG SEIT 08.11.2026 (Edgar: „überprüfe alle morphe die du von HB übernommen hast, ob die noch unfug anrichten“): Bis dahin zerlegten die Formregler das Delta in den
Rahmen (Normale, Aufwaerts, Quer) des HumanBody-Punkts und bauten es im Rahmen des Genesis-Punkts wieder auf. Wo die Normalen der beiden Netze im Kleinen verschieden
stehen (Finger, Zehen, Lider, Lippen, Schritt), wurde daraus Rauschen: `Shoulders_SizeX` verschob die Hand um 20 mm mit 3–9 mm Streuung je Punkt auf 3-mm-Kanten — die
Finger knitterten. Gemessen mit `ProjektTemp/_wegwerf/familien/hb_knick_alle.py` (Knick der Haut auf Stufe 1 gegen die Grundfigur, Regler bei ±1): 152 von 421
Regler-Richtungen knickten Kanten um mehr als 30°, im Weltraum 92, und von denen knickt bei 69 schon der Regler in HumanBody selbst so stark (`hb_welt_alle.py`). Die
kleinste Drehung je Kandidat (Normale auf Normale) und die Drehung der Knochenrahmen (`G9hbknochen`) waren nicht besser (`hb_uebertragung_vergleich.py`). Danach
`G9feldputz.knicke`: Kein Regler knickt die Haut des Kaefigs staerker als `KNICK_GRAD` oder als der Regler in HumanBody selbst (`quellknick`).

PUNKTE OHNE GEGENSTUECK (`ungueltig`, 17.10.2026): Genesis hat Mundinnenraum, Augenhoehlen und gespreizte Zehen, die HumanBody nicht oder anders hat. Dort
greift die Zuordnung einen Punkt mit gegenlaeufiger Normale oder weit weg — das Vorzeichen jedes Deltas entlang der Normale kippte (Body Size −1: +236 mm statt
−500 mm am Mundinnenraum, die Hoehe des Netzes stieg auf 1,825 m statt zu sinken). Solche Punkte (2.271 von 25.182) werden aus ihren Nachbarn gefuellt
(`G9feldputz.fuellen`), Reste von Zacken auf den Median der Nachbarn gesetzt (`putzen`).

VERSCHLUCKTE REGLER (`uebertragen_wirksam`, 17.10.2026): Ein kleiner Gesichtsregler (3 mm Hub auf 1–2 cm) fiel zwischen die Punkte, weil Genesis' Gesicht 9–25 mm anders sitzt
als HumanBodys (`Eyes_innerSinus`: 2,62 mm in der Quelle, 0,000 auf Genesis). Kommt ein Regler mit weniger als `RUECKFALL` seiner Staerke an, wird er mit der Kopfausrichtung
(`Hbzuordnung(ausgerichtet=True)`) neu uebertragen und die Fassung genommen, die mindestens `FAKTOR`-mal staerker ist. Alle anderen Regler bleiben bitgleich.
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld
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
    #: `G9feldputz.knicke`: Zunahme des Kantenwinkels gegen die Grundfigur (Grad), die ein Regler hoechstens erzeugt — es sei denn, er knickt in HumanBody selbst staerker (Setzung)
    KNICK_GRAD = 30.0
    #: Anteil des affinen Teils am Delta (R²), ab dem er ohne Paarung uebertragen wird (`uebertragen`; gemessen: nur `Body_Size` erreicht ihn, R² 1,000, die naechsten 0,975)
    AFFIN_R2 = 0.99

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
        u"""`{punkte, normalen, dreiecke}` der HumanBody-Grundfigur (Three-Lage)."""
        if self._hb is None:
            figur = Hbtraeger.laden(self.GESCHLECHT, self.BAUART, {}, {})
            self._hb = {'punkte': figur['punkte'], 'normalen': figur['normalen'], 'dreiecke': Torchfeld.feld(figur['dreiecke'], dtype=torch.int64)}
        return self._hb

    def quellknick(self, hb_delta):
        u"""Groesste Zunahme des Kantenwinkels (Grad), die der Regler auf dem HumanBody-Netz selbst erzeugt — so stark darf er auch auf Genesis knicken."""
        hb = self.humanbody()
        if '_kanten' not in hb:
            tri = hb['dreiecke']
            k = torch.sort(Torchfeld.cat([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]]), dim=1, stable=True).values
            f = torch.tile(Torchfeld.arange(len(tri)), (3,))
            o = Torchfeld.lexsort((k[:, 1], k[:, 0]))
            k, f = k[o], f[o]
            gleich = (k[1:] == k[:-1]).all(1)
            hb['_kanten'] = (f[:-1][gleich], f[1:][gleich])

        def winkel(p):
            tri = hb['dreiecke']
            a, b = hb['_kanten']
            n = Torchfeld.cross(p[tri[:, 1]] - p[tri[:, 0]], p[tri[:, 2]] - p[tri[:, 0]])
            n /= Torchfeld.maximum(Torchfeld.linalg_norm(n, dim=1, keepdim=True), 1e-30)
            return Torchfeld.degrees(Torchfeld.arccos(Torchfeld.clip((n[a] * n[b]).sum(1), -1.0, 1.0)))
        if 'winkel0' not in hb:
            hb['winkel0'] = winkel(Torchfeld.feld(hb['punkte'], dtype=torch.float64))
        return float((winkel(Torchfeld.feld(hb['punkte'], dtype=torch.float64) + hb_delta) - hb['winkel0']).max())

    def ursprung(self):
        u"""(27087,) Browserpunkt -> Kaefigpunkt."""
        if self._ursprung is None:
            self._ursprung = Torchfeld.feld(G9basisnetz.holen().netzstufe(0).ursprung, dtype=torch.int64)
        return self._ursprung

    def nachbarn(self):
        u"""(25182, GLAETTUNG) die naechsten Kaefigpunkte je Kaefigpunkt."""
        if self._nachbar is None:
            punkte = G9basisnetz.holen().punkte
            _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte, k=self.GLAETTUNG)
            self._nachbar = Torchfeld.feld(nachbar, dtype=torch.int64)
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

    def knicke(self, feld, hb_delta):
        u"""`G9feldputz.knicke` mit der Grenze dieses Reglers: `KNICK_GRAD` oder sein Knick in HumanBody, was groesser ist."""
        feld, _punkte, _rest = self.putz().knicke(feld, max(self.KNICK_GRAD, self.quellknick(hb_delta)))
        return feld

    def uebertragen(self, hb_delta, ausgerichtet=False):
        u"""(25182, 3) das HumanBody-Delta auf dem Genesis-Kaefig (Weltraum, siehe Kopf der Datei), gefuellt, geglaettet, geputzt, Knicke geglaettet.

        Ein (fast) affines Delta (Anteil `AFFIN_R2`, 09.11.2026) geht ohne Paarung: Der Kandidat sitzt im Gesicht 9–25 mm neben dem Genesis-Punkt, bei `Body_Size` −1 (Skalierung,
        576 mm) traegt er dort ein Delta, das um (1 − s)·25 mm ≈ 8 mm daneben liegt — an Lidern und Lippen (1–3-mm-Kanten) Falten: 1.912 Kanten ueber 30° auf Stufe 1, +1: 131. Der affine
        Teil D = M·p + t gilt auf Genesis exakt als M·p_g + (M·b + t)/Massstab (`affin_versatz`), nur der Rest geht ueber die Paarung: danach 18 bzw. 4 Kanten
        (`ProjektTemp/_wegwerf/familien/hb_affin_probe.py`). Bei R² 0,88–0,97 (Bein-, Hals-, Armlaengen: eher stueckweise Verschiebung als affin) machte die Teilung dagegen neue Knicke
        (`Legs_LowerlegLength` +1: 0 → 10 Kanten, `Neck_Angle` −1: 0 → 8) — darum nur ab `AFFIN_R2`."""
        punkte = self.humanbody()['punkte']
        x = Torchfeld.hstack([punkte, torch.ones((len(punkte), 1), dtype=torch.float64, device='cuda')])
        coef = Torchfeld.lstsq(x, hb_delta, rcond=None)[0]
        rest = hb_delta - x @ coef
        gesamt = float((hb_delta ** 2).sum())
        if gesamt <= 0 or 1.0 - float((rest ** 2).sum()) / gesamt < self.AFFIN_R2:
            return self._ueber_paarung(hb_delta, ausgerichtet)
        m, t = coef[:3].T, coef[3]
        kaefig = Torchfeld.feld(G9basisnetz.holen().punkte, dtype=torch.float64)
        feld = self._ueber_paarung(rest, ausgerichtet) + kaefig @ m.T + (m @ self.affin_versatz(ausgerichtet) + t) / self.paarung()['massstab']
        feld[Torchfeld.linalg_norm(feld, dim=1) < self.NULL_M] = 0.0
        return feld

    def affin_versatz(self, ausgerichtet=False):
        u"""(3,) b: Lage eines Genesis-Punkts im HumanBody-Rahmen = Massstab · p_g + b (Median ueber die Browserpunkte, Kandidaten gewichtet)."""
        paar = self.paarung()
        kand, gewicht = self.zuordnung(ausgerichtet)
        hb = self.humanbody()['punkte']
        return Torchfeld.median(Torchfeld.einsum('ik,ikj->ij', gewicht, hb[kand]) - paar['massstab'] * Torchfeld.feld(paar['g9_punkte'], dtype=torch.float64), axis=0)

    def _ueber_paarung(self, hb_delta, ausgerichtet=False):
        u"""Das Delta ueber die Kandidaten der Paarung (Weltraum), gefuellt, geglaettet, geputzt, Knicke geglaettet."""
        paar = self.paarung()
        kand, gewicht = self.zuordnung(ausgerichtet)
        browser = Torchfeld.einsum('ik,ikj->ij', gewicht, hb_delta[kand]) / paar['massstab']
        zahl = len(G9basisnetz.holen().punkte)
        summe = torch.zeros((zahl, 3), dtype=torch.float64, device='cuda')
        anzahl = torch.zeros(zahl, dtype=torch.float64, device='cuda')
        Torchfeld.add_at(summe, self.ursprung(), browser)
        Torchfeld.add_at(anzahl, self.ursprung(), 1.0)
        feld = summe / Torchfeld.maximum(anzahl, 1.0)[:, None]
        putz = self.putz()
        feld = putz.fuellen(feld, self.ungueltig(ausgerichtet))
        nachbar = self.nachbarn()
        for _ in range(self.DURCHGAENGE):
            feld = feld[nachbar].mean(axis=1)
        feld, _zacken = putz.putzen(feld)
        feld = self.knicke(feld, hb_delta)
        feld[Torchfeld.linalg_norm(feld, dim=1) < self.NULL_M] = 0.0
        return feld

    @staticmethod
    def staerke(feld):
        u"""Groesste Verschiebung (m) eines Felds."""
        return float(Torchfeld.linalg_norm(Torchfeld.feld(feld, dtype=torch.float64), dim=1).max()) if len(feld) else 0.0

    def vorwaerts(self, ausgerichtet=False):
        u"""Die `Hbvorwaerts` zur Paarung, mit oder ohne Kopfausrichtung (gemerkt)."""
        if ausgerichtet not in self._vorwaerts:
            such = self.zuordnungsobjekt(ausgerichtet).suchpunkte()
            self._vorwaerts[ausgerichtet] = Hbvorwaerts(self.paarung(), self.humanbody(), such, self.ursprung(), len(G9basisnetz.holen().punkte), self.nachbarn())
        return self._vorwaerts[ausgerichtet]

    def uebertragen_vorwaerts(self, hb_delta, ausgerichtet=False):
        u"""(25182, 3) das Delta vorwaerts auf den Kaefig gelegt (siehe `Hbvorwaerts`), geputzt."""
        feld, _zacken = self.putz().putzen(self.vorwaerts(ausgerichtet).uebertragen(hb_delta))
        feld = self.knicke(feld, hb_delta)
        feld[Torchfeld.linalg_norm(feld, dim=1) < self.NULL_M] = 0.0
        return feld

    def uebertragen_wirksam(self, hb_plus, hb_minus):
        u"""`(plus, minus, weg)` — beide Richtungen eines Reglers. `weg`: 'normal', 'ausgerichtet', 'vorwaerts' oder 'vorwaerts_ausgerichtet' (siehe Kopf der Datei; bis 08.11.2026 hiess 'normal' 'rahmen').

        Reihenfolge der Rueckfaelle: Kopfausrichtung, dann die Vorwaertsuebertragung (ohne und mit Ausrichtung); genommen wird die staerkste Fassung, die mindestens `FAKTOR`-mal staerker
        ist als die bisher beste."""
        plus, minus = self.uebertragen(hb_plus), self.uebertragen(hb_minus)
        quelle = max(self.staerke(hb_plus), self.staerke(hb_minus))
        beste = max(self.staerke(plus), self.staerke(minus))
        weg = 'normal'
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
