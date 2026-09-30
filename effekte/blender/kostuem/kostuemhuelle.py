# -*- coding: utf-8 -*-
"""Kostuemhuelle — der Umriss der Vorlage als Sichtkörper (visual hull): Ringe des Kostüms an die Silhouetten
anpassen.

Edgar (30.09.2026): „ergebnis mesh wie in der Vorlage". Der Optimierer trifft den Umriss eines Mantels nur so
gut, wie seine Maße es zulassen (Weite auf Kniehöhe, am Saum …) — gemessen IoU 0,81; die Ränder der
Differenzbilder liegen an den Seiten des Mantels. Die Vorlage liegt aber aus acht Blickwinkeln vor: Ein Punkt
kann nur zum Körper gehören, wenn er in (fast) jeder Ansicht innerhalb der Silhouette liegt — der Sichtkörper.
Die Ringe des Mantels werden deshalb je Punkt vom Ringmittelpunkt aus nach außen bis an den Rand des
Sichtkörpers gezogen (oder zurückgenommen), begrenzt auf ein Vielfaches des Wertes aus dem Wertesatz — der
Optimierer stellt weiter Form und Lage, die Hülle nur die Weite.

Die Masken stammen aus `Kostuemrunde.masken`: die Silhouette der Vorlage, geöffnet (dünne Teile wie der Stab
fallen weg — sonst zöge er den Mantel bis zur Hand hinaus). Abgebildet wird mit `Projektion`; die Normierung
(`abbildungen`) kommt aus einem Render des Ausgangsmodells, nicht des Kandidaten — so hängt das Ergebnis nur
von Kandidat und Ausgangsmodell ab.
"""

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

from effekte.blender.kostuem.projektion import Projektion

__all__ = ['Kostuemhuelle']


class Kostuemhuelle:
    #: Ein Punkt liegt „innen", wenn mindestens dieser Anteil der Ansichten ihn innerhalb der Silhouette sieht (eine
    #: Ansicht darf abweichen — die erzeugten Ansichten der Vorlage sind nicht ganz stimmig zueinander).
    ANTEIL = 0.85
    #: Wie weit die Ringe vom Wert des Optimierers zum Rand der Hülle wandern (0 = gar nicht, 1 = bis zum Rand). Gemessen
    #: am besten Wertesatz (Note 0,278 ohne Hülle): 1,0 → 0,2659, 0,7 → 0,2666 — mit 0,7 bleibt der Rock glatter.
    STAERKE = 0.7
    SCHRITTE = 41
    GLAETTEN = (0.25, 0.5, 0.25)

    def __init__(self, masken, projektion):
        """`masken`: {winkel: Pfad der Maske} (weiß = Figur, normierte Fläche); `projektion`: `Projektion` der Renders."""
        self.projektion = projektion
        self.masken = {float(w): self._laden(p) for w, p in masken.items()}
        self.abbildungen = None

    @staticmethod
    def _laden(pfad):
        bild = bpy.data.images.load(str(pfad), check_existing=False)
        try:
            return Projektion.pixel(bild)[..., 0] > 0.5
        finally:
            bpy.data.images.remove(bild)

    def normieren(self, abbildungen):
        """`abbildungen`: {winkel: (cx, oben, unten)} des Ausgangsmodells (`Projektion.abbildung`)."""
        self.abbildungen = {float(w): a for w, a in abbildungen.items() if float(w) in self.masken}

    def innen(self, punkte):
        """Anteil der Ansichten (0…1), in denen jeder der `punkte` (N × 3) innerhalb der Silhouette liegt."""
        summe = np.zeros(len(punkte))
        for winkel, abb in self.abbildungen.items():
            maske = self.masken[winkel]
            hf, bf = maske.shape
            u, v = self.projektion.projizieren(punkte, winkel, abb, hf, bf)
            iu, iv = np.rint(u).astype(int), np.rint(v).astype(int)
            drin = (iu >= 0) & (iu < bf) & (iv >= 0) & (iv < hf)
            summe += drin & maske[np.clip(iv, 0, hf - 1), np.clip(iu, 0, bf - 1)]
        return summe / max(len(self.abbildungen), 1)

    def _drin(self, mitte, richtung, radius, z):
        """Liegt der Punkt `mitte + radius · richtung` (je Zeile) in Höhe `z` (je Zeile) im Sichtkörper?"""
        xy = np.asarray(mitte, float) + richtung * radius[:, None]
        return self.innen(np.column_stack([xy, z])) >= self.ANTEIL

    def anpassen(self, punkte, mitte, unten, oben, zuschlag=1.0, geschlossen=True):
        """Die Punkte eines waagerechten Rings (n × 3, um `mitte` = (x, y)) auf den Rand der Hülle setzen.
        `unten`/`oben`: erlaubter Bereich als Vielfaches des bisherigen Abstands von der Mitte; `zuschlag`:
        Faktor auf den Rand (eine Borte liegt knapp außen). Ohne Normierung oder wenn die Hülle an der Stelle
        leer ist (schon der kleinste Abstand liegt außen), bleibt der Ring, wie er ist. Der Rand wird bis auf
        Zehntelmillimeter eingegabelt: zwei Ringe in derselben Höhe (Mantel und Saumborte) landen so auf
        derselben Fläche."""
        if not self.abbildungen:
            return punkte
        mitte = np.asarray(mitte, float)
        z = punkte[:, 2]  # je Punkt: ein geneigter Ring (Hutkrempe) liegt nicht in einer Ebene
        versatz = punkte[:, :2] - mitte
        r0 = np.linalg.norm(versatz, axis=1)
        richtung = versatz / np.maximum(r0, 1e-9)[:, None]
        faktoren = np.linspace(unten, oben, self.SCHRITTE)
        r = r0[:, None] * faktoren[None, :]
        xy = mitte + richtung[:, None, :] * r[:, :, None]
        raster = np.concatenate([xy, np.broadcast_to(z[:, None, None], xy.shape[:2] + (1,))], axis=2).reshape(
            -1, 3
        )
        drin = (self.innen(raster) >= self.ANTEIL).reshape(r.shape)
        # Der erste Punkt außerhalb, von innen gesehen: davor liegt der Rand. Beginnt der Bereich außerhalb,
        # bleibt es.
        alles_innen = drin.all(axis=1)
        erster_aussen = np.where(alles_innen, self.SCHRITTE - 1, np.argmax(~drin, axis=1))
        ok = drin[:, 0]
        zeile = np.arange(len(r))
        lo = r[zeile, np.clip(erster_aussen - 1, 0, self.SCHRITTE - 1)]
        hi = r[zeile, erster_aussen]
        for _ in range(7):
            mittel = (lo + hi) / 2
            gut = self._drin(mitte, richtung, mittel, z)
            lo, hi = np.where(gut, mittel, lo), np.where(gut, hi, mittel)
        rand = np.where(alles_innen, r[:, -1], lo)
        ziel = np.where(ok, rand, r0)
        neu = self._glaetten(r0 + self.STAERKE * (ziel - r0), geschlossen) * zuschlag
        aus = punkte.copy()
        aus[:, :2] = mitte + richtung * neu[:, None]
        return aus

    def _glaetten(self, radien, geschlossen):
        a, b, c = self.GLAETTEN
        if geschlossen:
            return a * np.roll(radien, 1) + b * radien + c * np.roll(radien, -1)
        rand = np.pad(radien, 1, mode='edge')
        return a * rand[:-2] + b * rand[1:-1] + c * rand[2:]
