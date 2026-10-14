# -*- coding: utf-8 -*-
"""Meshfigurtexeldetail — die feine Zeichnung der echten Haut auf die gefüllten Hauttexel übertragen (14.10.2026).

Anlass (Edgar, Edgar1: „Textur bei Beinen unterhalb und oberhalb der Unterhose schlecht“): Die Texelprüfung (`Meshfigurtexelpruefung`) ersetzt verworfene und nie getroffene Hauttexel durch das glatte Feld der guten Nachbarn.
In der Beinkachel stehen diese Füllungen als glatte rosa Inseln mit scharfem Rand und einem Staubsaum einzelner verworfener Texel in der behaarten Fotohaut (Kachel 1003, Oberschenkel), eine glatte Fläche unter dem Saum der Hose
gegen die behaarte Haut darüber. Der Farbton stimmt (das Feld IST das Mittel der Nachbarn) — es fehlt die Zeichnung: Härchen, Poren, Schatten der Hautlinien.

Hier bekommt jedes gefüllte Texel das Verhältnis „Farbe zu ihrem eigenen Tiefpass“ eines guten Texels aus der Nachbarschaft derselben UV-Insel — in zusammenhängenden Kacheln von `BLOCK_PX` Pixeln mit demselben Versatz, damit
ein Härchen über mehrere Texel durchläuft. Die Farbe bleibt das Feld (Helligkeit und Ton der Umgebung), nur die Helligkeit schwankt wie in der Nachbarschaft. Wo keine passende Quelle in Reichweite liegt, bleibt das Texel glatt.
"""
import numpy as np

__all__ = ['Meshfigurtexeldetail']


class Meshfigurtexeldetail:
    #: Tiefpass (Pixel der 2048er-Kachel), gegen den die Zeichnung gemessen wird — kleiner als ein Haarbüschel, größer als ein Härchen.
    SIGMA_PX = 5.0
    #: Das Verhältnis Farbe / Tiefpass bleibt in diesem Rahmen (ein dunkler Punkt zieht seine Umgebung sonst mit).
    GRENZEN = (0.55, 1.6)
    #: Kantenlänge der Kacheln mit gleichem Versatz, und die Versätze (Pixel): Spirale mit dem Goldenen Winkel, damit benachbarte Kacheln verschiedene Quellen haben.
    BLOCK_PX = 32
    VERSAETZE = 64
    NAHE_PX, FERNE_PX = 40.0, 400.0
    #: So viele Durchgänge mit anderen Versätzen, bis fast jedes Texel eine Quelle hat; ein Texel zählt als versorgt ab dieser Summe der Gewichtsquadrate.
    SCHICHTEN = 4
    ABDECKUNG_MIN = 0.2
    #: Eine Quelle zählt, wo mindestens so viel gute Texel im Tiefpass stehen.
    STUETZE_MIN = 0.2

    def __init__(self, seite, glatt):
        """`glatt(bild, maske, sigma) → (Farbe, Stütze)`: die normierte Faltung der Texelprüfung."""
        self.seite = int(seite)
        self.glatt = glatt

    @classmethod
    def versaetze(cls):
        """(V, 2) int — (dy, dx) auf einer Spirale von `NAHE_PX` bis `FERNE_PX`."""
        k = np.arange(cls.VERSAETZE)
        radius = cls.NAHE_PX + (cls.FERNE_PX - cls.NAHE_PX) * np.sqrt((k + 0.5) / cls.VERSAETZE)
        winkel = k * 2.399963229728653
        return np.stack([np.round(radius * np.sin(winkel)), np.round(radius * np.cos(winkel))], axis=1).astype(np.int64)

    def anwenden(self, drin, ziel, gut, farbe, fuellung):
        """Ändert `fuellung` (n, 3; Rohwerte 0..255) an den Texeln `ziel` (n,) bool; gibt die Zahl der Texel mit übertragener Zeichnung zurück.
        `drin` wählt die Texel der UV-Inseln im (S, S)-Bild, `gut` (n,) bool die echten, geprüften Hauttexel, `farbe` (n, 3) ihre Werte."""
        from scipy import ndimage

        s = self.seite
        if not (ziel.any() and gut.any()):
            return 0
        bild = np.zeros((s, s, 3))
        maske = np.zeros((s, s), dtype=bool)
        bild[drin] = farbe
        maske[drin] = gut
        tief, stuetze = self.glatt(bild, maske, self.SIGMA_PX)
        hell = np.array([0.299, 0.587, 0.114])
        quelle = maske & (stuetze > self.STUETZE_MIN)
        verhaeltnis = np.ones((s, s), dtype=np.float32)
        verhaeltnis[quelle] = np.clip((bild[quelle] @ hell) / np.maximum(tief[quelle] @ hell, 1.0), *self.GRENZEN)
        inselmaske = np.zeros((s, s), dtype=bool)
        inselmaske[drin] = True
        insel, _ = ndimage.label(inselmaske)
        ziel_bild = np.zeros((s, s), dtype=bool)
        ziel_bild[drin] = ziel
        zy, zx = np.nonzero(ziel_bild)
        eigene = insel[zy, zx]
        v_alle = self.versaetze()
        # Weiche Überlagerung statt harter Kacheln: jede Stützstelle (Raster `BLOCK_PX`) liefert die Zeichnung ihrer Quelle, die vier nächsten Stützstellen gehen mit weichen Gewichten ein; die Summe wird durch die Wurzel der
        # Gewichtsquadrate geteilt, sodass die Streuung der Zeichnung erhalten bleibt (unabhängige Quellen).
        fy, fx = zy / self.BLOCK_PX, zx / self.BLOCK_PX
        y0, x0 = np.floor(fy).astype(np.int64), np.floor(fx).astype(np.int64)
        ty, tx = fy - y0, fx - x0
        wy = np.stack([1.0 - ty * ty * (3.0 - 2.0 * ty), ty * ty * (3.0 - 2.0 * ty)])
        wx = np.stack([1.0 - tx * tx * (3.0 - 2.0 * tx), tx * tx * (3.0 - 2.0 * tx)])
        summe = np.zeros(len(zy))
        quadrate = np.zeros(len(zy))
        for salz in range(self.SCHICHTEN):
            for dy in (0, 1):
                for dx in (0, 1):
                    k = (((y0 + dy) * 73856093) ^ ((x0 + dx) * 19349663) ^ (salz * 83492791)) % len(v_alle)
                    v = v_alle[k]
                    qy, qx = zy + v[:, 0], zx + v[:, 1]
                    innen = (qy >= 0) & (qy < s) & (qx >= 0) & (qx < s)
                    ok = np.zeros(len(zy), dtype=bool)
                    ok[innen] = quelle[qy[innen], qx[innen]] & (insel[qy[innen], qx[innen]] == eigene[innen])
                    gewicht = np.where(ok, wy[dy] * wx[dx], 0.0)
                    abweichung = np.zeros(len(zy))
                    abweichung[ok] = verhaeltnis[qy[ok], qx[ok]] - 1.0
                    summe += gewicht * abweichung
                    quadrate += gewicht * gewicht
            if float(np.mean(quadrate >= self.ABDECKUNG_MIN)) >= 0.999:
                break
        gefunden = quadrate >= 1e-4
        if not gefunden.any():
            return 0
        faktor = np.ones((s, s), dtype=np.float32)
        faktor[zy[gefunden], zx[gefunden]] = np.clip(1.0 + summe[gefunden] / np.sqrt(quadrate[gefunden]), *self.GRENZEN)
        fuellung[ziel] = np.clip(fuellung[ziel] * faktor[drin][ziel][:, None], 0.0, 255.0)
        return int(gefunden.sum())
