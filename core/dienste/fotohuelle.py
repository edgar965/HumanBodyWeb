# -*- coding: utf-8 -*-
"""Fotohuelle — ein Kleidungsstück der Fotos als HÜLLE der angepassten Figur: die Hautfläche unter dem Stück, um den
gemessenen Abstand zum Netz nach außen versetzt, Farben aus der Netztextur (01.10.2026 abends).

Warum nicht das Netz selbst (`Fotostuecke` bis Fassung 12): Wo die Arme am Rumpf liegen, ist das TRELLIS-Netz ein
Geflecht aus Ärmel, Arm und Rumpf. Zurückgerechnet in die A-Pose rissen dort Löcher, Fetzen standen ab, der Hosenbund
trug einen Hautstreifen (Testauftrag 2026.10.01.12.38.09 in Mitsuba, drei Seiten) — Filter für gezerrte und
umgeklappte Flächen nahmen Flächen weg, flickten aber nichts.

Die Hülle hat die Topologie der Figur: keine Risse, und die Ruhelage ist exakt die der Figur (`genesis_ende.npz` und
`posiert.npy` sind Punkt für Punkt derselbe Käfig). Vom Netz kommen nur Zugehörigkeit, Abstand und Farbe:

1. je Figurpunkt (Haltung des Netzes) die nächste Netzfläche bis `REICHWEITE` — deren Stück (`kleidung_maske.stueck`,
   ohne Haut) ist das des Punkts; eine Figurfläche gehört zum Stück, wenn ihre drei Punkte es tun
2. Ränder glätten (`RINGE` Ringe schließen, dann öffnen), kleine Teile weg
3. einmal unterteilen (vier Flächen je Fläche), Abstand zum Netz je Punkt in [`ABSTAND_MIN`, `ABSTAND_MAX`], über
   Nachbarn geglättet — Bauch und Falten bleiben grob erhalten, abstehende Fetzen nicht
4. Farbe je Punkt: Mittel der `NACHBARN` nächsten Netzflächen DESSELBEN Stücks (kein Hautton an den Rändern)
5. Textur: je Fläche eine Zelle `ZELLE` × `ZELLE` px, Farben baryzentrisch hineingerechnet

    Fotohuelle(scan, stueck, haut, ruhe, posiert, dreiecke).bauen(nummer) → (punkte, flaechen, uv_ecken, textur) | None
"""

import numpy as np

from .huellenschnitt import Huellenschnitt

__all__ = ['Fotohuelle']


class Fotohuelle:
    REICHWEITE = 0.05
    RINGE = 2
    TEIL_MIN = 0.05
    ABSTAND_MIN = 0.003
    ABSTAND_MAX = 0.03
    GLAETTEN = 6
    NACHBARN = 12
    ZELLE = 8

    def __init__(self, scan, stueck, haut, ruhe, posiert, dreiecke, farbsperre=None, halsgewicht=None):
        """`farbsperre` (F,) bool: Netzflächen, die nicht zur Farbe beitragen (Hautton) — für die Zugehörigkeit zählen
        sie (die gebackene Textur hat warme Flecken mitten im Shirt; als Lücken gerechnet wurden es Löcher)."""
        from scipy.spatial import cKDTree
        self.scan = scan
        self.stueck = np.where(np.asarray(haut, dtype=bool), 0, np.asarray(stueck))
        self.farbsperre = np.zeros(len(self.stueck), bool) if farbsperre is None else np.asarray(farbsperre, bool)
        self.halsgewicht = halsgewicht                  # (V,) für den Rundhals (`Huellenschnitt.halsgewichte`)
        self.ruhe = np.asarray(ruhe, dtype=np.float64)
        self.posiert = np.asarray(posiert, dtype=np.float64)
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64)
        self.mitten = scan.punkte[scan.flaechen].mean(axis=1)
        abstand, index = cKDTree(self.mitten).query(self.posiert, workers=-1)
        self.marke = np.where(abstand < self.REICHWEITE, self.stueck[index], 0)

    # ------------------------------------------------------------ Auswahl

    def _nachbarn(self, flaechen, n_punkte):
        from scipy.sparse import coo_matrix
        zeilen = np.repeat(np.arange(len(flaechen)), 3)
        return coo_matrix((np.ones(len(zeilen)), (zeilen, flaechen.reshape(-1))),
                          shape=(len(flaechen), n_punkte)).tocsr()

    #: Das obere Stück schließt die Lücke zum unteren (Haut zwischen Shirtsaum und Hosenbund, Testauftrag: ein Streifen
    #: rundum): Figurflächen, höchstens `LUECKE` Ringe von beiden entfernt, gehören zum oberen.
    UEBER = {1: (2,)}
    #: Stücke mit Rundhals (`Huellenschnitt._rundhals`): das Oberteil.
    HALS = {1: True}
    LUECKE = 4
    #: Spielraum um den Höhenbereich des Stücks im Netz (`hoehen`, Höhenkern der Netzflächen), Meter.
    HOEHE_RAND = 0.02

    def _auswahl(self, nummer, hoehen=None):
        """(F,) bool der Figurflächen des Stücks — im Höhenbereich `hoehen` (von, bis), geschlossen, geöffnet, Lücken
        zum Stück darunter gefüllt, ohne kleine Teile."""
        from scipy.sparse.csgraph import connected_components
        inzidenz = self._nachbarn(self.dreiecke, len(self.ruhe))
        wahl = (self.marke[self.dreiecke] == nummer).all(axis=1)
        y = self.posiert[self.dreiecke].mean(axis=1)[:, 1]
        if hoehen is not None:                          # Socken: die grauen Schienbeine des Netzes sind keine Socke
            wahl &= (y >= hoehen[0] - self.HOEHE_RAND) & (y <= hoehen[1] + self.HOEHE_RAND)

        def wachsen(w, innerhalb=None):
            punkte = np.zeros(len(self.ruhe))
            punkte[np.unique(self.dreiecke[w])] = 1.0
            neu = (inzidenz @ punkte) > 0
            return neu if innerhalb is None else neu & innerhalb

        def schrumpfen(w):
            draussen = np.zeros(len(self.ruhe))
            draussen[np.unique(self.dreiecke[~w])] = 1.0
            return w & ~((inzidenz @ draussen) > 0)

        for _ in range(self.RINGE):                     # schließen: Löcher und Kerben zu
            wahl = wachsen(wahl)
        for _ in range(2 * self.RINGE):                 # öffnen: Fransen und Stege weg
            wahl = schrumpfen(wahl)
        for _ in range(self.RINGE):
            wahl = wachsen(wahl)
        for unten in self.UEBER.get(nummer, ()):
            unter = (self.marke[self.dreiecke] == unten).all(axis=1)
            a, b = wahl, unter
            for _ in range(self.LUECKE):
                a, b = wachsen(a), wachsen(b)
            luecke = a & b & ~unter                     # nur die Lücke, nicht in die Hose hinein
            if hoehen is not None:                      # und nicht unter den Saum des Netzes (Auftrag 20.10.04: das
                luecke &= y >= hoehen[0] - 2 * self.HOEHE_RAND     # Shirt reichte bis in den Schritt)
            wahl = wahl | luecke
        index = np.flatnonzero(wahl)
        if not len(index):
            return wahl
        teil_inz = inzidenz[index]
        n, teil = connected_components(teil_inz @ teil_inz.T, directed=False)
        groesse = np.bincount(teil, minlength=n)
        aus = np.zeros_like(wahl)
        aus[index[groesse[teil] >= self.TEIL_MIN * len(index)]] = True
        return aus

    # ------------------------------------------------------------- Bauen

    @staticmethod
    def _normalen(punkte, flaechen):
        e = punkte[flaechen]
        n = np.zeros_like(punkte)
        kreuz = np.cross(e[:, 1] - e[:, 0], e[:, 2] - e[:, 0])
        for i in range(3):
            np.add.at(n, flaechen[:, i], kreuz)
        return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)

    def _glatt(self, werte, flaechen, runden=None, faktoren=(1.0,)):
        """Werte je Punkt über die Nachbarn (gemeinsame Fläche) mitteln, `runden` (Vorgabe `GLAETTEN`) Runden mit je
        einem Schritt pro Faktor; ein Faktor < 0 ist der Gegenschritt des Taubin-Glättens (bläht wieder auf, was das
        Mitteln schrumpfte)."""
        inzidenz = self._nachbarn(flaechen, len(werte))
        nachbar = (inzidenz.T @ inzidenz).tocsr()
        anzahl = np.maximum(np.asarray(nachbar.sum(axis=1)).ravel()[:, None], 1e-12)
        w = werte.reshape(len(werte), -1).astype(np.float64)
        for _ in range(self.GLAETTEN if runden is None else runden):
            for faktor in faktoren:
                w = w + faktor * ((nachbar @ w) / anzahl - w)
        return w.reshape(werte.shape)

    #: Kein „zweite Haut" (Befund Edgar: das Shirt folgte Brustfalte, Nabel und Gesäßfalte). Stoff überbrückt Mulden:
    #: die versetzte Fläche Taubin-geglättet (schrumpft nicht), davon nur der Anteil längs der Normale (Säume
    #: wandern nicht), nie näher als `ABSTAND_MIN` an der Haut.
    DRAPIER_RUNDEN = 30
    #: Anteil der örtlichen Netzfarbe an der Stofffarbe (Befund Edgar „Textur miserabel": lila-braune Flecken auf dem
    #: dunkelgrauen Shirt — die Textur des TRELLIS-Netzes ist gebackenes Licht und Rauschen, der Stoff ist einfarbig;
    #: Falten zeichnet das Licht des Renders). 0 = nur der Median des Stücks.
    FLECKEN = 0.25
    TAUBIN = (0.5, -0.53)

    #: Mindestluft je Stück (m) — ein T-Shirt fällt locker (Fotos: über Brust und Bauch gerade herab), Hose und Socke
    #: sitzen eng. Gilt statt `ABSTAND_MIN`, wo größer.
    LUFT = {1: 0.010, 2: 0.004, 3: 0.002}

    #: Stoff liegt auf, wo die Haut nach oben zeigt (Normale y in der Ruhelage): ab `OBEN[0]` beginnt die Grenze, ab
    #: `OBEN[1]` gilt nur noch `luft`. Prüfung Runde 18 (02.10.2026): auf den Schultern folgte die Hülle dem
    #: TRELLIS-Netz, das Hals, Haar und Shirt verschmilzt — das Shirt stand bis 30 mm über der Schulter, von vorn als
    #: dunkler Rand hinter den Schultern, durch den Ausschnitt schwarz (Innenseite).
    OBEN = (0.35, 0.7)

    def _aufliegen(self, normalen, luft):
        oben = np.clip((normalen[:, 1] - self.OBEN[0]) / (self.OBEN[1] - self.OBEN[0]), 0.0, 1.0)
        return self.ABSTAND_MAX * (1.0 - oben) + luft * oben

    def _drapieren(self, ruhe, normalen, versatz, flaechen, luft):
        punkte = self._glatt(ruhe + normalen * versatz[:, None], flaechen, self.DRAPIER_RUNDEN, self.TAUBIN)
        # Taubins Gegenschritt schießt am Rand über (Kunstnetz: 30,1 mm bei 30 mm Grenze, test_fotohuelle Fall 1)
        tiefe = np.clip(np.einsum('ij,ij->i', punkte - ruhe, normalen), luft, self.ABSTAND_MAX)
        return ruhe + normalen * tiefe[:, None]

    def bauen(self, nummer, hoehen=None):
        import trimesh
        from scipy.spatial import cKDTree
        wahl = self._auswahl(nummer, hoehen)
        if not wahl.any():
            return None
        schnitt = Huellenschnitt(self.ruhe, self.dreiecke, self.halsgewicht)    # glatte, ebene Säume statt Treppe
        feld = schnitt.feld(wahl, hals=self.HALS.get(nummer, False))
        nah = (feld[self.dreiecke] >= schnitt.SCHNITT).any(axis=1)
        genutzt, neu = np.unique(self.dreiecke[nah].reshape(-1), return_inverse=True)
        flaechen = neu.reshape(-1, 3)
        lagen = np.hstack([self.ruhe[genutzt], self.posiert[genutzt], feld[genutzt][:, None]])   # gemeinsam teilen
        lagen, flaechen = trimesh.remesh.subdivide(lagen, flaechen)
        lagen, flaechen = schnitt.schneiden(lagen, flaechen, 6)
        ruhe, posiert = lagen[:, :3], lagen[:, 3:6]
        eigene = np.flatnonzero(self.stueck == nummer)
        baum = cKDTree(self.mitten[eigene])
        abstand, _ = baum.query(posiert, workers=-1)
        luft = max(self.ABSTAND_MIN, self.LUFT.get(nummer, 0.0))
        normalen = self._normalen(ruhe, flaechen)
        versatz = self._glatt(np.clip(np.minimum(abstand, self._aufliegen(normalen, luft)), luft, self.ABSTAND_MAX),
                              flaechen)
        punkte = self._drapieren(ruhe, normalen, versatz, flaechen, luft)
        bunt = eigene[~self.farbsperre[eigene]]
        bunt = bunt if len(bunt) >= self.NACHBARN else eigene
        _, nah = cKDTree(self.mitten[bunt]).query(posiert, k=self.NACHBARN, workers=-1)
        bary = np.full((nah.size, 3), 1.0 / 3.0)
        farben = self.scan.farben(bunt[nah.reshape(-1)], bary).astype(np.float64).reshape(len(posiert), -1, 3)
        farben = self._glatt(np.median(farben, axis=1), flaechen)
        grund = np.median(farben, axis=0)                     # einfarbiger Stoff, Netzflecken nur gedämpft
        farben = grund + self.FLECKEN * (farben - grund)
        uv_ecken, textur = self._atlas(flaechen, farben)
        return punkte, flaechen, uv_ecken, textur

    def _atlas(self, flaechen, farben):
        """Je Fläche eine Zelle; das untere linke Dreieck der Zelle trägt die Fläche, die ganze Zelle die baryzentrisch
        fortgesetzte Farbe (kein Rand, der beim Filtern hineinblutet) → (uv_ecken (F, 3, 2), Bild uint8)."""
        z = self.ZELLE
        spalten = int(np.ceil(np.sqrt(len(flaechen))))
        zeilen = int(np.ceil(len(flaechen) / spalten))
        breite, hoehe = spalten * z, zeilen * z
        ecke = np.array([[0.5, 0.5], [z - 1.5, 0.5], [0.5, z - 1.5]])          # Pixelmitten in der Zelle (x, y)
        y, x = np.mgrid[0:z, 0:z] + 0.5
        # Baryzentrische Koordinaten jedes Zellpixels bezüglich `ecke` (fortgesetzt, dann geklemmt)
        b1 = (x - ecke[0, 0]) / (ecke[1, 0] - ecke[0, 0])
        b2 = (y - ecke[0, 1]) / (ecke[2, 1] - ecke[0, 1])
        b0 = 1.0 - b1 - b2
        b = np.clip(np.stack([b0, b1, b2], axis=-1), 0.0, None)
        b /= b.sum(axis=-1, keepdims=True)
        zellfarben = np.einsum('yxk,fkc->fyxc', b, farben[flaechen])          # (F, z, z, 3)
        bild = np.zeros((zeilen * spalten, z, z, 3))
        bild[:len(flaechen)] = zellfarben
        bild = bild.reshape(zeilen, spalten, z, z, 3).transpose(0, 2, 1, 3, 4).reshape(hoehe, breite, 3)
        f = np.arange(len(flaechen))
        x0, y0 = (f % spalten) * z, (f // spalten) * z
        px = x0[:, None] + ecke[None, :, 0]
        py = y0[:, None] + ecke[None, :, 1]
        uv = np.stack([px / breite, 1.0 - py / hoehe], axis=-1)                # v nach oben (OBJ)
        return uv, np.clip(bild + 0.5, 0, 255).astype(np.uint8)
