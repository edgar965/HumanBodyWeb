# -*- coding: utf-8 -*-
"""Blendimportumfeld — die Haut-Kachel um das Scham-Stück trägt dort die FARBE DES ORIGINALS (09.10.2026).

BEFUND (Edgar: „auch die Textur und Farbe soll an die Figur / an den Rand angepasst werden", Chrome-Messung `chrome_farbvergleich.js`):
Am Rand des Scham-Stücks (103 Randpunkte) hat das Stück (201, 145, 130), die Haut daneben (233, 209, 195). Ursache im Backen
(`Blendimporthaut.nacharbeiten`): wo kein Strahl das Original trifft, gilt die helle Ersatzfarbe der Kachel von „Mesh to 3D"
(229, 206, 199); die Rohkachel trifft das Original im Scham-Bereich nur zu 91,9 % (am UV-Nahtbereich 60 % Fehlstellen), und deren
Treffer haben im Mittel (202, 151, 133) — wie das Stück. Die Haut um das Stück war also blass, das Stück originalgetreu.

HIER: Im Umfeld des Stücks füllt jede Fehlstelle die Farbe des ORIGINALS an der nächsten Stelle seiner Fläche, nicht die Ersatzkachel:

    Texel          jedes Texel einer Fehlstelle der Kachel (aus den Dreiecken der Figur um das Stück, mit `RAND` Texel Zugabe über die
                   Insel hinaus: auch der Saum, den Filter und Mip-Stufen lesen, trägt die Farbe)
    Ort            sein Punkt auf der Fläche der Figur (Schwerpunktkoordinaten × Dreieckspunkte)
    Original       der nächste Punkt auf der Fläche des Originals (`ruhe`, wie beim Backen), höchstens `ABSTAND_MAX_M` entfernt;
                   seine Farbe über die UV-Koordinaten des Originals aus dem Farbbild (bilinear)
    Mischung       volle Farbe des Originals bis `RADIUS_M` vom Stück, danach weich (`AUSLAUF_M`) zurück zur bisherigen Füllung

Wirkt nur mit einem Scham-Stück (`arbeit/scham_punkte.npy`, geschrieben von `Blendimportstuecke.scham_stueck`); ohne es bleibt die
Kachel, wie sie ist. Die Treffer des Backens bleiben unverändert — nur die Fehlstellen ändern sich. Ohne Django prüfbar
(`test_blendimport_umfeld.py`).
"""

import numpy as np

__all__ = ['Blendimportumfeld']


class Blendimportumfeld:
    #: Bis hierher (m) vom nächsten Stückpunkt gilt die Farbe des Originals voll; danach läuft sie über `AUSLAUF_M` auf 0 aus.
    RADIUS_M = 0.05
    AUSLAUF_M = 0.04
    #: Weiter als das (m) darf der nächste Punkt des Originals nicht von der Figurfläche liegen (sonst ein anderes Körperteil).
    ABSTAND_MAX_M = 0.02
    #: Größter Abstand (m) eines Flächenpunkts zum nächsten Eckpunkt des Originals (Kantenlänge des Körpernetzes) — Vorprüfung.
    PUNKTABSTAND_M = 0.012
    #: Zugabe über den Rand eines Dreiecks hinaus, als Anteil in Schwerpunktkoordinaten (≈ 20 % der Dreiecksbreite).
    RAND = 0.2
    #: Texel je Rechenblock beim nächsten-Punkt-Suchen (Speicher).
    BLOCK = 200_000

    def __init__(self, stueck, figur, original, farbbild):
        """`stueck`: Punkte des Scham-Stücks (Ruhelage, Y oben); `figur`: `{punkte, dreiecke, uv, kachel}` (`Blendimportlage.genesis`);
        `original`: `{punkte (Ruhelage, Y oben), dreiecke, uv_ecken (T, 3, 2)}`; `farbbild`: `(H, W, 3)` uint8."""
        self.stueck = np.asarray(stueck, dtype=np.float64)
        self.figur = figur
        self.original = original
        self.farbbild = farbbild
        self.bericht = {}

    # ----------------------------------------------------------- Bausteine

    def dreiecke_nahe(self, kachel):
        """Nummern der Figurdreiecke dieser Kachel, deren Ecken irgendwo höchstens `RADIUS_M + AUSLAUF_M` vom Stück liegen."""
        from scipy.spatial import cKDTree

        f = self.figur
        je_kachel = np.flatnonzero(f['kachel'] == kachel)
        if not len(je_kachel):
            return je_kachel
        d, _ = cKDTree(self.stueck).query(f['punkte'][f['dreiecke'][je_kachel]].reshape(-1, 3))
        nah = (d.reshape(-1, 3) <= self.RADIUS_M + self.AUSLAUF_M).any(axis=1)
        return je_kachel[nah]

    def texel(self, dreiecke, leer):
        """`(zeile, spalte, dreieck, schwerpunkt)` der Fehlstellen-Texel in und um die Figurdreiecke `dreiecke` (UV-Raum der Kachel);
        `dreieck` zählt in `dreiecke`. Je UV-Insel gerechnet: das Gitter eines Blocks bleibt so auf die Insel begrenzt (alle Inseln
        zusammen deckten bis zu 8192² Texel)."""
        from .blendimportatlas import Blendimportatlas

        uv = self.figur['uv'][self.figur['dreiecke'][dreiecke]]
        insel = Blendimportatlas.inseln(uv)
        teile = []
        for i in np.unique(insel):
            nr = np.flatnonzero(insel == i)
            z, s, e, lam = self._texel_insel(dreiecke[nr], leer)
            teile.append((z, s, nr[e], lam))
        if not teile:
            return (np.zeros(0, dtype=np.int64),) * 3 + (np.zeros((0, 3)),)
        return tuple(np.concatenate([t[k] for t in teile]) for k in range(4))

    def _texel_insel(self, dreiecke, leer):
        """Die Texel einer Insel; Texel innerhalb eines Dreiecks gehen vor Texeln, die nur in der Zugabe `RAND` eines anderen liegen."""
        hoehe, breite = leer.shape
        uv = self.figur['uv'][self.figur['dreiecke'][dreiecke]]                    # (T, 3, 2)
        px = np.stack([uv[..., 0] * breite, (1.0 - uv[..., 1]) * hoehe], axis=-1)  # (T, 3, 2): x, y
        z0, z1 = int(np.floor(px[..., 1].min())) - 2, int(np.ceil(px[..., 1].max())) + 3
        s0, s1 = int(np.floor(px[..., 0].min())) - 2, int(np.ceil(px[..., 0].max())) + 3
        z0, s0, z1, s1 = max(z0, 0), max(s0, 0), min(z1, hoehe), min(s1, breite)
        eigner = np.full((z1 - z0, s1 - s0), -1, dtype=np.int32)
        lam = np.zeros((z1 - z0, s1 - s0, 3), dtype=np.float32)
        for innen in (False, True):
            for t in range(len(dreiecke)):
                a, b, c = px[t]
                x0, x1 = int(np.floor(px[t][:, 0].min())) - 1, int(np.ceil(px[t][:, 0].max())) + 2
                y0, y1 = int(np.floor(px[t][:, 1].min())) - 1, int(np.ceil(px[t][:, 1].max())) + 2
                x0, y0, x1, y1 = max(x0, s0), max(y0, z0), min(x1, s1), min(y1, z1)
                if x0 >= x1 or y0 >= y1:
                    continue
                det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
                if abs(det) < 1e-9:
                    continue
                gy, gx = np.mgrid[y0:y1, x0:x1]
                x, y = gx + 0.5, gy + 0.5
                l1 = ((b[1] - c[1]) * (x - c[0]) + (c[0] - b[0]) * (y - c[1])) / det
                l2 = ((c[1] - a[1]) * (x - c[0]) + (a[0] - c[0]) * (y - c[1])) / det
                l3 = 1.0 - l1 - l2
                kleinste = np.minimum(np.minimum(l1, l2), l3)
                gilt = (kleinste >= 0.0) if innen else ((kleinste >= -self.RAND) & (kleinste < 0.0))
                ort = (slice(y0 - z0, y1 - z0), slice(x0 - s0, x1 - s0))
                if not innen:
                    gilt &= eigner[ort] < 0
                eigner[ort] = np.where(gilt, t, eigner[ort])
                lam[ort] = np.where(gilt[..., None], np.stack([l1, l2, l3], axis=-1), lam[ort])
        zeile, spalte = np.nonzero((eigner >= 0) & leer[z0:z1, s0:s1])
        return zeile + z0, spalte + s0, eigner[zeile, spalte], lam[zeile, spalte].astype(np.float64)

    def original_farbe(self, orte):
        """`(farbe (n, 3) float, gefunden (n,) bool)`: die Farbe des Originals am nächsten Punkt seiner Fläche zu jedem Ort."""
        import trimesh

        from scipy.spatial import cKDTree

        o = self.original
        flaeche = trimesh.Trimesh(o['punkte'], o['dreiecke'], process=False)
        hoehe, breite = self.farbbild.shape[:2]
        farbe = np.zeros((len(orte), 3))
        gefunden = np.zeros(len(orte), dtype=bool)
        # Der nächste PUNKT ist schnell: liegt er weiter als `ABSTAND_MAX_M` + Punktabstand weg, liegt auch die Fläche zu weit (Fallout
        # ranger, Kachel 1003: 2,29 Mio. Texel im Umfeld, davon 1,32 Mio. ohne Original — der Weg zur Fläche für alle kostete Minuten).
        nah_genug = np.flatnonzero(cKDTree(o['punkte']).query(orte)[0] <= self.ABSTAND_MAX_M + self.PUNKTABSTAND_M)
        for a in range(0, len(nah_genug), self.BLOCK):
            nr = nah_genug[a:a + self.BLOCK]
            nah, abstand, dreieck = trimesh.proximity.closest_point(flaeche, orte[nr])
            schwer = trimesh.triangles.points_to_barycentric(flaeche.triangles[dreieck], nah)
            uv = (o['uv_ecken'][dreieck] * schwer[..., None]).sum(axis=1)
            farbe[nr] = self.abtasten(uv[:, 0] * breite - 0.5, (1.0 - uv[:, 1]) * hoehe - 0.5)
            gefunden[nr] = abstand <= self.ABSTAND_MAX_M
        return farbe, gefunden

    def abtasten(self, x, y):
        """Bilinear aus dem Farbbild (Texelmitten bei ganzen Zahlen; außen geklemmt)."""
        hoehe, breite = self.farbbild.shape[:2]
        x = np.clip(x, 0, breite - 1.0001)
        y = np.clip(y, 0, hoehe - 1.0001)
        x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
        fx, fy = (x - x0)[:, None], (y - y0)[:, None]
        b = self.farbbild
        oben = b[y0, x0] * (1 - fx) + b[y0, x0 + 1] * fx
        unten = b[y0 + 1, x0] * (1 - fx) + b[y0 + 1, x0 + 1] * fx
        return oben * (1 - fy) + unten * fy

    def gewicht(self, orte):
        """Anteil der Originalfarbe 0…1 je Ort: 1 bis `RADIUS_M` vom Stück, danach weich auf 0 über `AUSLAUF_M`."""
        from scipy.spatial import cKDTree

        d, _ = cKDTree(self.stueck).query(orte)
        t = np.clip((d - self.RADIUS_M) / self.AUSLAUF_M, 0.0, 1.0)
        return 1.0 - t * t * (3.0 - 2.0 * t)

    # ----------------------------------------------------------------- Lauf

    def fuellen(self, kachel, farbe, leer):
        """Die Kachel `farbe` (H, W, 3) uint8 mit der Originalfarbe in den Fehlstellen `leer` um das Stück — verändert `farbe` und gibt
        sie zurück; `self.bericht` nennt Zahlen."""
        dreiecke = self.dreiecke_nahe(kachel)
        self.bericht = {'dreiecke': int(len(dreiecke)), 'texel': 0}
        if not len(dreiecke):
            return farbe
        zeile, spalte, eigner, lam = self.texel(dreiecke, leer)
        if not len(zeile):
            return farbe
        ecken = self.figur['punkte'][self.figur['dreiecke'][dreiecke[eigner]]]      # (n, 3, 3)
        orte = (ecken * lam[..., None]).sum(axis=1)
        gewicht = self.gewicht(orte)
        wahl = np.flatnonzero(gewicht > 0.002)
        if not len(wahl):
            return farbe
        original, gefunden = self.original_farbe(orte[wahl])
        wahl, original = wahl[gefunden], original[gefunden]
        w = gewicht[wahl][:, None]
        alt = farbe[zeile[wahl], spalte[wahl]].astype(np.float64)
        farbe[zeile[wahl], spalte[wahl]] = np.clip(np.rint(w * original + (1.0 - w) * alt), 0, 255).astype(np.uint8)
        self.bericht.update(texel=int(len(zeile)), im_umfeld=int(len(gewicht[gewicht > 0.002])), gefuellt=int(len(wahl)),
                            ohne_original=int(len(gefunden) - gefunden.sum()),
                            mittel_alt=[round(float(v), 1) for v in alt.mean(axis=0)] if len(alt) else None,
                            mittel_neu=[round(float(v), 1) for v in original.mean(axis=0)] if len(original) else None)
        return farbe
