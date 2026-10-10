# -*- coding: utf-8 -*-
"""Blendimportfingermodell — die Genesis-Hand einer Seite als Vorwärtsmodell der Fingerhaltung (10.10.2026).

Warum: „Mesh to 3D" stellt nur 22 Körperknochen (`Meshfigurgenesis.FREI`), keine Finger, und gewichtet Finger mit 0,0 und Hand mit 0,1
(`Meshfigurabstand.GEWICHT`). Die Figur trägt darum immer Genesis' gestreckte Ruhehand — greift das Original (Katana, Faust), stimmt
dort nichts mehr: in allen acht Importen sind die Hände die am schlechtesten passende Region (Rosemary rechts, Median 9,3 mm, 56 % der
Punkte über 8 mm, die Handkachel zu 45–52 % ohne Treffer; das Katana ging durch die Hand). Dieses Modell posiert NUR die Handpunkte
des Käfigs: Haltung des Imports (`Blendimporthaltung.drehung`) plus Fingerdrehungen φ, Lage des Netzes (`Blendimporthaltung.abbilden`).

PARAMETER (21 je Hand, Daz-Kanalwerte in Grad): Beugung `rotation/z` der drei Fingerglieder je Finger, Spreizung `rotation/y` am Grundglied, Daumen
`thumb1` x/y/z, `thumb2` y, `thumb3` y. Vorzeichen und Grenzen aus Dazʼ eigenen Formeln: `CTRL<r|l>HandGrasp` und `CTRL<r|l>FingersFist` auf 1 geben die
Beugung (rechts positiv, links negativ; Grundglied 82°, Mittelglied 93°, Endglied 72°; Faust 75°/100°/90°, gemessen 10.10.2026); erlaubt sind −10 % …
+110 % davon. Die Greifpose ist zugleich ein Startwert (`griffpose`). Dazu ein 22. Wert, **kein Knochenwinkel**: die Größe der Hand in Prozent (`SKALA`).

GRÖSSE: Die Figurhand ist nicht an die Hand des Originals angepasst (Hand 0,1, Finger 0,0 im Maß von „Mesh to 3D"): bei Rosemary links 15,8 cm
gegen 11,6 cm des Originals. Ohne die Größe im Maß deutete die Suche gestreckte, aber kürzere Original-Finger als Klaue (die erste Fassung). Die
Größe wirkt nur im Maß (Skalierung der Proben um den Handteller); `kaefig` und `als_griff` kennen sie nicht — die Figur behält ihre Hand.

MAẞ: Abstand der Originalpunkte zur FLÄCHE der Figurhand (Käfigdreiecke, vier Proben je Dreieck: Schwerpunkt und Kantenmitten) und umgekehrt, je auf
`STUTZ_M` gekappt. **Nicht gegen die Käfigpunkte:** sie liegen nur alle 5 mm; ein zusammengeballter Käfig lag dichter und „verbesserte" das Maß.
"""

import numpy as np
from scipy.spatial import cKDTree

__all__ = ['Blendimportfingermodell']


class Blendimportfingermodell:
    TEILE = ('hand', 'thumb', 'index', 'mid', 'ring', 'pinky', 'metacarpal', 'carpal')
    FINGER = ('index', 'mid', 'ring', 'pinky')
    #: Schwerpunkt und Kantenmitten eines Dreiecks.
    PROBEN = np.array([[1 / 3, 1 / 3, 1 / 3], [0.5, 0.5, 0.0], [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]])
    #: Beugung: −10 % … +110 % der Greif-/Faustpose (Grundglied ≤ 90°, Mittelglied ≤ 110°, Endglied ≤ 99°). Vorher −25 % … +130 %: die Suche
    #: stellte das Mittelglied der linken Hand auf 130° (anatomisch unmöglich).
    BEUGUNG_UNTEN = 0.1
    BEUGUNG_OBEN = 1.1
    SPREIZUNG_GRAD = 15.0
    DAUMEN_MIN_GRAD = 60.0
    #: Größe der Hand im Maß (Prozent): Figurhand gegen Original (Rosemary links 73 %, rechts nahe 100 %).
    SKALA = (-30.0, 10.0)
    #: Abstände über dieser Grenze zählen nicht mehr (m): ein Original-Punkt ohne Gegenstück zieht nicht, ein Modellpunkt ohne Original auch nicht.
    STUTZ_M = 0.03
    #: Punkte je Richtung (zufällig, fest): 4.000 Ziel- und ebenso viele Modellproben.
    PUNKTE = 4000
    #: Gewicht der Vorliebe für die gestreckte, unskalierte Hand (m je ganzem Spielraum): die Daten sollen eine Faust BELEGEN, bevor sie gilt.
    VORLIEBE_M = 0.05

    def __init__(self, halt, seite, ziel):
        """`halt`: vorbereitete `Blendimporthaltung`; `seite`: 'r' oder 'l'; `ziel`: Originalpunkte dieser Hand in der Lage des Netzes."""
        from Genesis9.haut import G9haut
        from Genesis9.kaefigumriss import G9kaefigumriss

        self.halt = halt
        self.seite = seite
        bereit = halt.vorbereiten()
        figur = halt.figur()
        self.morph = figur.morphpunkte()
        self.posen, self.versatz = figur.formeln.posen(), figur.formeln.knochen()
        self.boden = np.array([0.0, bereit['boden'], 0.0])
        self.koerper = halt.drehung()
        haut = G9haut.holen()
        namen = list(haut.knochen)
        index, gewicht = np.asarray(haut.index), np.asarray(haut.gewicht, dtype=np.float64)
        hand = [i for i, n in enumerate(namen) if n.startswith(seite + '_') and 'toe' not in n and any(s in n for s in self.TEILE)]
        anteil = np.zeros(len(self.morph))
        for k in range(index.shape[1]):
            anteil += np.where(np.isin(index[:, k], hand), gewicht[:, k], 0.0)
        #: Alle Käfigpunkte, die ein Hand-/Fingerknochen bewegt, und davon die Mehrheit (Hand, Finger — Grundlage des Maßes).
        self.idx = np.flatnonzero(anteil > 0.0)
        im_fit = anteil[self.idx] > 0.5
        self.teilhaut = type('Teilhaut', (), {'knochen': namen, 'index': index[self.idx], 'gewicht': gewicht[self.idx]})
        #: Stelle von `idx`, an der die Punkte des Maßes stehen, und die Käfigdreiecke aus lauter solchen Punkten (Nummern in dieser Reihenfolge).
        self.fit_nach_idx = np.flatnonzero(im_fit)
        nummer = -np.ones(len(self.morph), dtype=np.int64)
        nummer[self.idx[self.fit_nach_idx]] = np.arange(len(self.fit_nach_idx))
        dreiecke = np.asarray(G9kaefigumriss.dreiecke(), dtype=np.int64)
        self.flaechen = nummer[dreiecke[(nummer[dreiecke] >= 0).all(axis=1)]]
        rng = np.random.default_rng(1)
        self.ziel = ziel
        self.ziel_s = ziel[rng.choice(len(ziel), min(len(ziel), self.PUNKTE), replace=False)]
        self.baum_ziel = cKDTree(ziel)
        self.parameter = self._parameter()
        self.n = len(self.parameter)
        self.anzahl = self.n + 1
        self.schluessel = [(p['knochen'], p['kanal']) for p in self.parameter]
        self.unten = np.array([p['unten'] for p in self.parameter] + [self.SKALA[0]])
        self.oben = np.array([p['oben'] for p in self.parameter] + [self.SKALA[1]])
        self.griffpose = np.array([p['griff'] for p in self.parameter] + [0.0])
        self.spiel = np.maximum(np.abs(self.unten), np.abs(self.oben))
        # Drehpunkt der Größe: der Handteller (Käfigpunkte ohne Finger- und Daumenknochen) bei gestreckten Fingern.
        dominant = index[self.idx][np.arange(len(self.idx)), np.argmax(gewicht[self.idx], axis=1)]
        teller = np.array([not any(s in namen[b] for s in ('thumb', 'index', 'mid', 'ring', 'pinky')) for b in dominant])
        self.pivot = self.posiert(np.zeros(self.anzahl))[teller].mean(axis=0)

    # ------------------------------------------------------------- Parameter

    def _parameter(self):
        """`[{knochen, kanal, unten, oben, griff}]` aus Dazʼ Formeln für `CTRL<seite>HandGrasp` und `…FingersFist`."""
        from Genesis9.formeln import G9formeln

        s = self.seite
        griff = G9formeln({'CTRL%sHandGrasp' % s: 1.0}).posen()
        faust = G9formeln({'CTRL%sFingersFist' % s: 1.0}).posen()
        liste = []

        def eintrag(knochen, kanal, unten, oben, start):
            liste.append({'knochen': knochen, 'kanal': kanal, 'unten': float(unten), 'oben': float(oben), 'griff': float(start)})

        for finger in self.FINGER:
            for glied in (1, 2, 3):
                b = '%s_%s%d' % (s, finger, glied)
                v = max(griff.get(b, {}).get('rotation/z', 0.0), faust.get(b, {}).get('rotation/z', 0.0), key=abs)
                unten, oben = sorted((-self.BEUGUNG_UNTEN * v, self.BEUGUNG_OBEN * v))
                eintrag(b, 'rotation/z', unten, oben, griff.get(b, {}).get('rotation/z', 0.0))
            eintrag('%s_%s1' % (s, finger), 'rotation/y', -self.SPREIZUNG_GRAD, self.SPREIZUNG_GRAD, 0.0)
        for glied, kanaele in ((1, ('rotation/x', 'rotation/y', 'rotation/z')), (2, ('rotation/y',)), (3, ('rotation/y',))):
            b = '%s_thumb%d' % (s, glied)
            for kanal in kanaele:
                v = griff.get(b, {}).get(kanal, 0.0)
                grenze = max(self.DAUMEN_MIN_GRAD, 1.5 * abs(v))
                eintrag(b, kanal, -grenze, grenze, v)
        return liste

    # ----------------------------------------------------------------- Modell

    def drehung(self, phi):
        """Die Haltung des Imports plus Fingerdrehung `phi` (Grad, Reihenfolge von `parameter`; ein 22. Wert, die Größe, bleibt außen vor)."""
        d = {b: dict(k) for b, k in self.koerper.items()}
        for (b, kanal), w in zip(self.schluessel, phi[:self.n], strict=True):
            d.setdefault(b, {})
            d[b][kanal] = d[b].get(kanal, 0.0) + float(w)
        return d

    def posiert(self, phi):
        """`(len(idx), 3)`: die Käfigpunkte der Hand in der Haltung mit Fingerdrehung, in der Lage des Netzes (m) — in Lebensgröße."""
        from Genesis9.knochenmatrizen import G9knochenmatrizen

        matrizen = G9knochenmatrizen(self.posen, self.versatz, drehung=self.drehung(phi))
        return self.halt.abbilden(matrizen.anwenden(self.morph[self.idx], self.teilhaut) - self.boden)

    def proben(self, x):
        """Punkte auf den Käfigdreiecken der Hand (vier je Dreieck) aus den posierten Punkten `x`."""
        ecken = x[self.fit_nach_idx][self.flaechen]
        return np.einsum('pk,tkc->tpc', self.PROBEN, ecken).reshape(-1, 3)

    def abstaende(self, phi):
        """`(Original → Fläche, Fläche → Original)` in m, auf `STUTZ_M` gekappt; die Fläche in der Größe `phi[-1]` Prozent um den Handteller."""
        s = self.proben(self.posiert(phi))
        s = self.pivot + (1.0 + phi[self.n] / 100.0) * (s - self.pivot)
        schritt = max(1, len(s) // self.PUNKTE)
        d1, _ = cKDTree(s).query(self.ziel_s, workers=-1)
        d2, _ = self.baum_ziel.query(s[::schritt], workers=-1)
        return np.minimum(d1, self.STUTZ_M), np.minimum(d2, self.STUTZ_M)

    def wert(self, phi):
        d1, d2 = self.abstaende(phi)
        return float(np.mean(d1 ** 2) + np.mean(d2 ** 2))

    def reste(self, phi):
        """Der Rest für die kleinsten Quadrate: beide Abstände plus die Vorliebe für die gestreckte, unskalierte Hand."""
        d1, d2 = self.abstaende(phi)
        return np.concatenate([d1, d2, self.VORLIEBE_M * np.asarray(phi) / self.spiel])

    def kennzahlen(self, phi):
        """`{original_median_mm, original_p90_mm, modell_median_mm, skala_prozent}` — für den Bericht."""
        d1, d2 = self.abstaende(phi)
        return {'original_median_mm': round(float(np.median(d1)) * 1000.0, 2), 'original_p90_mm': round(float(np.percentile(d1, 90)) * 1000.0, 2),
                'modell_median_mm': round(float(np.median(d2)) * 1000.0, 2), 'skala_prozent': round(float(phi[self.n]), 1)}

    def kaefig(self, phi):
        """`(idx, delta)`: um wie viel sich jeder Käfigpunkt, den ein Handknochen bewegt, durch `phi` gegen die gestreckte Hand verschiebt (Lage des Netzes, m)."""
        return self.idx, self.posiert(phi) - self.posiert(np.zeros(self.anzahl))

    def als_griff(self, phi, mindest_grad=0.5):
        """`{knochen: {'rotation/z': Grad}}` — das Format von `G9stueckersatz.griff`; Drehungen unter `mindest_grad` fallen weg."""
        aus = {}
        for (b, kanal), w in zip(self.schluessel, phi[:self.n], strict=True):
            if abs(w) >= mindest_grad:
                aus.setdefault(b, {})[kanal] = round(float(w), 2)
        return aus

    def vektor(self, griff):
        """Die Umkehrung von `als_griff`: der Vektor aller Winkel (Größe 0) zu einem Griff."""
        return np.array([griff.get(b, {}).get(k, 0.0) for b, k in self.schluessel] + [0.0])
