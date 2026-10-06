# -*- coding: utf-8 -*-
"""Haarkappe — EIN Haarteil in EINER Farbe, das den ganzen Haarbereich des Kopfes deckt (05.10.2026).

Edgar (Auftrag 2026.10.04.11.11.44, zum vierten Mal): „Haar ist immer noch zu hoch in der Mitte", „Haare seitlich sind braun, mach ein Haarmodell, das alles beinhaltet und eine einheitliche Farbe hat, so wie
die Vorlage". Die Frisur der Garderobe (Mavick Hair Style) besteht aus fünf Gruppen — Kappe, vier Strähnenlagen — mit eigenen Tönen und hat an den Seiten Lücken, durch die die Kopfhaut (rosabraun) scheint; geklemmt
(`Haarklemme`) blieb sie oben bis 8 mm über der Hülle des Fotohaars.

Die Haarkappe ist die Kopfhaut selbst, nach außen geschoben: Die Dreiecke des Körpers oberhalb der Haarlinie werden um die Dicke des Netzhaars angehoben, gemessen als Abstand der Hülle des Fotohaars
(`Haarklemme.roh`, ungeglättete Hülle je 5°-Feld) zur Haut in derselben Richtung vom Kopfmittelpunkt — begrenzt auf `DICKE`. Die Haarlinie (`LINIE`) schneidet die Dreiecke genau (nicht an ihren Kanten: der
Körperkäfig hat am Kopf Dreiecke von rund 1 cm, ein Schnitt entlang der Kanten ergab eine Treppe); an ihr läuft die Dicke auf `RAND_DICKE` aus (kein Absatz, kein Flackern auf der Haut). Ein Bild aus feinem
Rauschen um die Haarfarbe gibt der Fläche das Aussehen kurzer Haare, aufgetragen je Dreieck von der Seite her, die ihm am meisten zugewandt ist (Würfelabbildung: keine Pole und keine Naht wie bei einer Kugelabbildung —
die erste Fassung zeigte hinten einen Stern); die Farbe ist überall dieselbe.

Die Haarlinie kommt aus der Abdeckung des Netzhaars: Wo die Hülle (`Haarklemme.roh`) Netzhaar hat — Felder von 5°, von Einzelfeldern befreit (Schließen und Öffnen) —, ist Haar; das Gesicht und die Stirn bis zum Haaransatz des Netzes haben keins (am Testauftrag Ansatz bei 45–55° über der Augenhöhe, hoher Haaransatz wie im Foto).
Gesicht, Ohr, Koteletten und Nacken bestimmen seit VERSION 6 die Regeln der `Haarlinie` (Ohrknochen statt fester Winkel, runder Nacken); der Abstand zur Grenze dieses Bereichs (Grad, innen positiv) ist ein Feld auf denselben 5°-Feldern; das Schneiden und die Dicke lesen es.

    teil = Haarkappe(ablage, netz).teil(rgb)      # Teil wie aus `Kleidermodellbau.teile` (art 'haar') für `Standmodellglb.teile`; None ohne Hülle des Fotohaars

Vor den Iterationen trägt das Standmodell die Kappe allein (`Standvorabkleider`). In den Runden liegt sie unter der Frisur der Garderobe, die an ihrer Haarlinie geschnitten wird (`Haarumbau`, seit 05.10.2026);
dort ist ihre Farbe die der Karten im Render (`Haarumbau.anzeigefarbe`). Ihre Textur hat Strähnen (schmal in u, lang in v; `STRAEHNE`): Die Würfelabbildung legt v an Hinterkopf, Seiten und Scheitel in die Wuchsrichtung.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Haarkappe']


class Haarkappe:
    #: Zählt hoch, wenn sich die Kappe bei gleicher Eingabe ändert (gehört in die Fassung des Standmodells). 2: Haarlinie geschnitten, Würfel-UV. 3: Haarlinie aus der Abdeckung des Netzhaars. 4: Gesicht, Wange und Schläfe frei, Zungen am Haaransatz entfernt. 5: Haar über dem Ohr ab 10° statt 20°.
    #: 6: Haarlinie nach Ohr (Ohrknochen), Koteletten und rundem Nacken (`Haarlinie`) statt fester Winkel — vorher eine Gerade über dem Ohr und eine Klippe dahinter.
    VERSION = 6
    SORTE = 'haarkappe'
    #: Höhenwinkel, bis zu dem das Haar im Nacken reicht (Grad über der Waagerechten durch den Kopfmittelpunkt) — gilt für `radius_nacken` (die Messung „kurzes Haar"); die Haarlinie selbst liegt in `Haarlinie.UNTEN_MITTE`/`UNTEN_SEITE`.
    UNTEN = -38.0
    RAND_GRAD = 8.0                # über so viele Grad über der Haarlinie wächst die Dicke von `RAND_DICKE` auf ihr Maß
    DICKE = (0.008, 0.035)          # Dicke des Haars über der Haut (m): nicht dünner als 8 mm (ein Haarschnitt), nicht dicker als 35 mm
    RAND_DICKE = 0.003              # an der Haarlinie
    #: (Höhenwinkel, ab dem die Dicke voll gilt, Höhenwinkel, unter dem nur noch `faktor` davon gilt, faktor): ein Herrenschnitt ist an Nacken und Seiten kürzer als oben. Gemessen im Seitenbild (Auftrag 2026.10.04.21.41.43):
    #: die Hülle des Netzhaars gab im Nacken (−17…−30°) 12–19 mm gegen 5–12 mm oben — im Foto läuft das Haar dort aus und die Kontur zieht zum Hals hin ein.
    VERJUENGUNG = (25.0, -30.0, 0.45)
    REICHWEITE = 0.16               # nur Hautpunkte bis so weit vom Kopfmittelpunkt (m): Kopf, nicht Schultern
    TEXTUR_PX = 512
    PERIODE = 0.60                  # Kantenlänge der Textur in der Welt (m): ein Texel ist 1,2 mm
    KONTRAST = 0.14                 # Rauschen um die Haarfarbe (Anteil)
    STRAEHNE = 4.0                  # Länge der Strähnen in der Textur (Texel, Gauß-Sigma in v; Breite 0,7 Texel)
    SAMEN = 7

    def __init__(self, ablage, netz):
        self.ablage = ablage
        self.netz = netz
        self._lage_cache = None
        self._mitte = None

    # ------------------------------------------------------------------ Hülle

    def _lage(self):
        """`(Klemme, gefüllte Hülle, Linienfeld)` — einmal je Kappe; alle None ohne Hülle des Fotohaars. Die Haarlinie (`grad_je_punkt`) und die Fläche (`flaeche`) lesen dasselbe Feld."""
        if self._lage_cache is None:
            from .haarklemme import Haarklemme
            klemme = Haarklemme.fuer(self.ablage, np.asarray(self.netz['punkte'], dtype=np.float64))
            karte = self._fuellen(klemme.roh) if klemme is not None else None
            self._mitte = klemme.mitte if klemme is not None else None
            self._lage_cache = (klemme, karte, self._linienfeld(klemme.roh) if karte is not None else None)
        return self._lage_cache

    def grad_je_punkt(self, punkte, reichweite=None):
        """Abstand zur Haarlinie in Grad je Punkt (Lage der Bühne), > 0 = im Haarbereich — None ohne Hülle des Fotohaars. Punkte weiter als `reichweite` (m) vom Kopfmittelpunkt liegen weit darunter."""
        klemme, karte, linie = self._lage()
        if karte is None:
            return None
        v = np.asarray(punkte, dtype=np.float64) - klemme.mitte
        return self._ueber_der_linie(klemme, linie, v, np.linalg.norm(v, axis=1), self.REICHWEITE if reichweite is None else reichweite)

    def radius_nacken(self):
        """Der größte Abstand des Netzhaars vom Kopfmittelpunkt (m) zwischen −37° und 0° Höhenwinkel — None ohne Hülle des Fotohaars oder ohne Netzhaar in diesem Band."""
        klemme, karte, _linie = self._lage()
        if karte is None:
            return None
        hoehe = klemme.roh.shape[0]
        el = (np.arange(hoehe) + 0.5) * 180.0 / hoehe - 90.0
        zeilen = klemme.roh[(el >= self.UNTEN) & (el <= 0.0)]
        return float(np.nanmax(zeilen)) if np.isfinite(zeilen).any() else None

    def kurzhaarig(self, grenze=0.17):
        """True, wenn das Netzhaar zwischen −37° und 0° Höhenwinkel nirgends weiter als `grenze` (m) vom Kopfmittelpunkt steht (`radius_nacken`) — kurzes Haar. Darunter liegt der Hals (Radius 0,17–0,20 m, auch ohne Haar).
        Gemessen 05.10.2026 an allen drei Aufträgen mit Hülle (`kurzhaarig_messen.py`: test4 0,126 m, Sapiens 1 und 2 je 0,127 m — alle dieselbe Frisur, Mavick Hair Style); ein Auftrag mit langem Haar hat keine Hülle, die Grenze ist dort ungeprüft."""
        radius = self.radius_nacken()
        return radius is not None and radius < grenze

    @staticmethod
    def _summe3(a):
        """Summe über die 3 × 3 Nachbarn jedes Felds: Azimut (Spalten) umlaufend, Höhenwinkel (Zeilen) am Rand wiederholt."""
        z = np.pad(np.pad(a, ((0, 0), (1, 1)), mode='wrap'), ((1, 1), (0, 0)), mode='edge')
        hoehe, breite = a.shape
        return sum(z[i:i + hoehe, j:j + breite] for i in range(3) for j in range(3))

    @classmethod
    def _fuellen(cls, roh, sigma=1.5):
        """Die Hülle je Feld lückenlos und glatt: leere Felder (kein Netzhaar) bekommen das Mittel ihrer Nachbarn, von den Rändern her; danach Gauß über die Felder (Azimut umlaufend)."""
        from scipy import ndimage

        karte = np.array(roh, dtype=np.float64)
        leer = np.isnan(karte)
        if leer.all():
            return None
        for _ in range(80):
            if not leer.any():
                break
            summe = cls._summe3(np.where(leer, 0.0, karte))
            zahl = cls._summe3((~leer).astype(np.float64))
            neu = leer & (zahl > 0)
            karte[neu] = summe[neu] / zahl[neu]
            leer = np.isnan(karte)
        return ndimage.gaussian_filter(karte, sigma, mode=('nearest', 'wrap'))

    @staticmethod
    def _weich(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    # ------------------------------------------------------------------ Haarlinie

    @staticmethod
    def _vorzeichen(maske, rand=8):
        """Entfernung jedes Felds zur Grenze der Maske in Feldern, innen positiv, außen negativ (Azimut umlaufend, Höhenwinkel am Rand wiederholt)."""
        from scipy import ndimage

        z = np.pad(np.pad(maske, ((0, 0), (rand, rand)), mode='wrap'), ((rand, rand), (0, 0)), mode='edge')
        innen = ndimage.distance_transform_edt(z)
        aussen = ndimage.distance_transform_edt(~z)
        return (innen - aussen)[rand:-rand, rand:-rand]

    def _linienfeld(self, roh):
        """Abstand (Grad) jedes 5°-Felds zur Grenze des Haarbereichs, innen positiv: Abdeckung des Netzhaars, geschlossen und geöffnet (keine Einzelfelder), dazu die Koteletten, ohne Gesicht, Ohr und Nacken —
        die Regeln stehen in `Haarlinie` (seit Fassung 6; vorher feste Winkel: Azimut 122° / Höhenwinkel 10° / −38°)."""
        from scipy import ndimage

        from .haarlinie import Haarlinie
        hoehe, _breite = roh.shape
        feld = 180.0 / hoehe
        rand = 6
        haar = np.pad(np.pad(~np.isnan(roh), ((0, 0), (rand, rand)), mode='wrap'), ((rand, rand), (0, 0)), mode='edge')
        eins = np.ones((3, 3), dtype=bool)
        haar = ndimage.binary_opening(ndimage.binary_closing(haar, eins), eins, iterations=2)[rand:-rand, rand:-rand]       # Zungen unter 25° Breite fallen weg (am Testauftrag eine am Haaransatz der Stirn)
        weg, kotelett = Haarlinie.ausschluss(self.netz, self._mitte, roh)
        bereich = ndimage.gaussian_filter(((haar | kotelett) & ~weg).astype(np.float64), Haarlinie.GLAETTEN, mode=('nearest', 'wrap')) > 0.5      # die Treppe der 5°-Felder runden (Ohr, Schläfe, Koteletten)
        return self._vorzeichen(bereich) * feld

    @staticmethod
    def _ueber_der_linie(klemme, feld, v, r, reichweite):
        """Abstand zur Haarlinie (Grad, > 0 = Haar) je Punkt — bilinear im Linienfeld; Punkte außerhalb der Reichweite liegen weit darunter."""
        return np.where(r < reichweite, klemme._grenze_je_punkt(v, r, feld), -90.0)  # noqa: SLF001 — dieselbe Nachschlagung wie die Klemme

    @staticmethod
    def _schneiden(p, d, f, normalen, index, gewicht):
        """Die Dreiecke `d` entlang f = 0 abschneiden (f > 0: Haar; f linear über die Kante). Jedes Ergebnisdreieck bekommt eigene Eckpunkte (Windung bleibt); Schnittpunkte nehmen Haut und Normale vom
        inneren Ende der Kante. → (Punkte, Normalen, Index, Gewicht), je (3 · T, …)."""
        drin = f > 0.0
        zahl = drin[d].sum(axis=1)
        ecken = []

        def kante(a, b):
            t = (f[a] / (f[a] - f[b]))[:, None]
            n = normalen[a] + t * (normalen[b] - normalen[a])
            return p[a] + t * (p[b] - p[a]), n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12), index[a], gewicht[a]

        def ecke(a):
            return p[a], normalen[a], index[a], gewicht[a]

        d3 = d[zahl == 3]
        if len(d3):
            ecken.append([ecke(d3[:, 0]), ecke(d3[:, 1]), ecke(d3[:, 2])])
        d1 = d[zahl == 1]
        if len(d1):
            zeile = np.arange(len(d1))
            k = np.argmax(drin[d1], axis=1)                                           # der innere Eckpunkt zuerst, die Reihenfolge bleibt zyklisch
            a, b, c = d1[zeile, k], d1[zeile, (k + 1) % 3], d1[zeile, (k + 2) % 3]
            ecken.append([ecke(a), kante(a, b), kante(a, c)])
        d2 = d[zahl == 2]
        if len(d2):
            zeile = np.arange(len(d2))
            k = np.argmax(~drin[d2], axis=1)                                          # der äußere Eckpunkt ist c
            c, a, b = d2[zeile, k], d2[zeile, (k + 1) % 3], d2[zeile, (k + 2) % 3]
            ecken.append([ecke(a), ecke(b), kante(b, c)])
            ecken.append([ecke(a), kante(b, c), kante(a, c)])
        if not ecken:
            return None
        # je Dreieck die drei Eckpunkte hintereinander: (T, 3, …) → (3 · T, …)
        return tuple(np.concatenate([np.stack([e[0][i], e[1][i], e[2][i]], axis=1) for e in ecken]).reshape((-1,) + ecken[0][0][i].shape[1:]) for i in range(4))

    # ------------------------------------------------------------------ Fläche

    def hautschnitt(self):
        """`(haut_p, normalen, index, gewicht)` — die Dreiecke des Körpers über der Haarlinie, an ihr genau geschnitten (jedes Dreieck mit eigenen Eckpunkten: (3 · T, …)), Haut und Normale je Eckpunkt. None ohne Hülle des Fotohaars oder ohne Dreiecke
        über der Linie. Dasselbe Stück Kopfhaut trägt die Kappe (`flaeche`) und die Wurzeln der Strähnen (`Herrenhaar`)."""
        from Genesis9.figurrigglb import G9figurrigglb

        p = np.asarray(self.netz['punkte'], dtype=np.float64)
        klemme, karte, linie = self._lage()
        if karte is None:
            return None
        d = np.asarray(self.netz['dreiecke'], dtype=np.int64).reshape(-1, 3)
        v = p - klemme.mitte
        r = np.linalg.norm(v, axis=1)
        f = self._ueber_der_linie(klemme, linie, v, r, self.REICHWEITE)
        d = d[(f[d] > 0.0).any(axis=1)]
        haut = self.netz['haut']
        index = np.asarray(haut['index'], dtype=np.int64).reshape(-1, 4)
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64).reshape(-1, 4)
        return self._schneiden(p, d, f, G9figurrigglb._normalen(p, np.asarray(self.netz['dreiecke'], dtype=np.int64).reshape(-1, 3)), index, gewicht) if len(d) else None  # noqa: SLF001

    def dicke_bei(self, haut_p):
        """`(dicke, grad_ueber_der_linie, v, r)` für Punkte der Kopfhaut (Lage der Bühne): die Dicke des Haars über der Haut — Hülle des Fotohaars minus Hautradius je Richtung, `DICKE` begrenzt, an der Linie auf `RAND_DICKE` auslaufend."""
        klemme, karte, linie = self._lage()
        v = haut_p - klemme.mitte
        r = np.maximum(np.linalg.norm(v, axis=1), 1e-9)
        el_ueber = self._ueber_der_linie(klemme, linie, v, r, self.REICHWEITE)
        huelle = klemme._grenze_je_punkt(v, r, karte)                                       # noqa: SLF001 — dieselbe Nachschlagung wie die Klemme
        dicke = self.RAND_DICKE + self._weich(el_ueber / self.RAND_GRAD) * (np.clip(huelle - r, self.DICKE[0], self.DICKE[1]) - self.RAND_DICKE)
        el = np.degrees(np.arcsin(np.clip(v[:, 1] / r, -1.0, 1.0)))
        oben, unten, faktor = self.VERJUENGUNG                                              # Nacken und Seiten sind kürzer geschnitten als oben: die Dicke nimmt nach unten ab
        return dicke * (faktor + (1.0 - faktor) * self._weich((el - unten) / (oben - unten))), el_ueber, v, r

    def flaeche(self, anteil=1.0):
        """`(punkte, dreiecke, haut, uv, normalen, daten)` der Kappe — None ohne Hülle des Fotohaars. `punkte` (3 · T, 3), `dreiecke` (T, 3), `haut` {knochen, index, gewicht} je Punkt.
        `anteil`: so viel der Dicke über der Linie (1 = die Dicke des Fotohaars; `Herrenhaar` legt die Kappe als Grund unter die Strähnen)."""
        geschnitten = self.hautschnitt()
        if geschnitten is None:
            return None
        haut = self.netz['haut']
        klemme = self._lage()[0]
        haut_p, normalen, idx, gew = geschnitten
        dicke, el_ueber, v, r = self.dicke_bei(haut_p)                                      # Verschieben nach außen: Dicke aus der Hülle des Fotohaars, an der Linie auslaufend
        dicke = self.RAND_DICKE + (dicke - self.RAND_DICKE) * anteil
        punkte = klemme.mitte + v * ((r + dicke) / r)[:, None]
        tri = np.arange(len(punkte), dtype=np.int64).reshape(-1, 3)
        # Würfelabbildung: je Dreieck die zwei Achsen, die senkrecht zu seiner Hauptrichtung stehen — v jeweils in der Wuchsrichtung: an den Seiten (Normale x) senkrecht (v = y), am Scheitel (Normale y) vor–zurück
        # (v = z), vorn und hinten (Normale z) senkrecht (v = y)
        fn = np.cross(punkte[tri[:, 1]] - punkte[tri[:, 0]], punkte[tri[:, 2]] - punkte[tri[:, 0]])
        achse = np.argmax(np.abs(fn), axis=1)
        paare = np.array([[2, 1], [0, 2], [0, 1]])[achse]                                    # (T, 2) Achsen je Dreieck (u, v)
        je_ecke = np.repeat(paare, 3, axis=0)
        uv = (punkte[np.arange(len(punkte))[:, None], je_ecke] - klemme.mitte[je_ecke]) / self.PERIODE + 0.5
        oben = el_ueber > 0.0
        daten = {'dreiecke': int(len(tri)), 'dicke_mittel_mm': round(float(dicke[oben].mean()) * 1000.0, 1),
                 'dicke_oben_mm': round(float(dicke[v[:, 1] > 0.8 * np.abs(v).max()].mean()) * 1000.0, 1) if (v[:, 1] > 0.8 * np.abs(v).max()).any() else None}
        return punkte, tri, {'knochen': haut['knochen'], 'index': idx, 'gewicht': gew}, uv, normalen, daten

    # ------------------------------------------------------------------ Bild

    @classmethod
    def bild(cls, rgb, pfad):
        """Feines Strähnenrauschen um die Haarfarbe (`rgb` 0–1) als PNG (`Haarkappenbild`)."""
        from .haarkappenbild import Haarkappenbild
        return Haarkappenbild.schreiben(rgb, pfad, cls.TEXTUR_PX, cls.KONTRAST, cls.STRAEHNE, cls.SAMEN)

    # ------------------------------------------------------------------ Teil

    def teil(self, rgb, anteil=1.0):
        """Das Haarteil (`art` 'haar', `sorte` 'haarkappe') in der Form der Teile von `Kleidermodellbau.teile`; None ohne Hülle des Fotohaars. `anteil`: siehe `flaeche`."""
        gebaut = self.flaeche(anteil)
        if gebaut is None or rgb is None:
            return None
        punkte, dreiecke, haut, uv, normalen, daten = gebaut
        # Das Bild trägt die Farbe im Namen (`artefakte-benennen`): Die Haarkappe des Standmodells (Fotofarbe) und die der Runden (Farbe des Rezepts, `Haarumbau`) teilen sich den Ordner.
        pfad = self.bild(rgb, self.ablage.arbeit('haarkappe_%s.png' % ''.join('%02x' % int(round(min(max(float(c), 0.0), 1.0) * 255)) for c in rgb[:3])))
        logger.info('Haarkappe: %d Dreiecke über der Haarlinie, Dicke im Mittel %s mm, oben %s mm', daten['dreiecke'], daten['dicke_mittel_mm'], daten['dicke_oben_mm'])
        return {'art': 'haar', 'sorte': self.SORTE, 'punkte': punkte, 'dreiecke': dreiecke.reshape(-1), 'haut': haut, 'uv': uv, 'normalen': normalen, 'farbe': (1.0, 1.0, 1.0),
                'gruppen': [{'name': 'kappe', 'index_ab': 0, 'index_anzahl': int(dreiecke.size), 'bilder': {}}],
                'textur': [{'ab': 0, 'anzahl': int(dreiecke.shape[0]), 'albedo': str(pfad), 'faktor': (1.0, 1.0, 1.0)}]}

    @classmethod
    def fingerabdruck(cls, ablage):
        """Gehört in die Fassung des Standmodells: Version und Stand der Quelle der Hülle (`haar.glb` bzw. `haar_huelle.npz`) — None ohne Quelle."""
        from .haarklemme import Haarklemme
        for name in (Haarklemme.DATEI, 'haar.glb'):
            try:
                pfad = ablage.ergebnis(name)
                if pfad.is_file():
                    return [cls.VERSION, name, pfad.stat().st_mtime_ns]
            except OSError:
                continue
        return None
