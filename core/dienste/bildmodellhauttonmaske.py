# -*- coding: utf-8 -*-
"""Bildmodellhauttonmaske — Freisteller-Maske aus einer Positivliste von Hauttönen (21.09.2026).

Edgar: „mach mir auf dem Hintergrund entfernen ein halbautomatisches Tool anhand der
‚Positiv'-Liste. Alles außer den Hauttönen (mit Slider veränderbar) soll als Hintergrund
weiß werden." Und (abends): „die Positivliste soll NUR außerhalb der Figur gelten, also markiere
die Figur, den Kopf, merke dir die Pixel, und suche nach Pixeln, die anders in der Farbe sind."
Regler `positiv` im Freisteller:

    Kern (Figur)   das erodierte Innere der Netzmaske (`innen`) UND die Marken unter „Pinsel
                   Person"-Strichen / „Punkt Person"-Klicks (`proben`) — alles darin bleibt,
                   auch Haar, Augen, Kleidung. Bis 21.09.2026 abends war die Hautmaske allein
                   die Maske und nahm Pixel IM Kopf weg.
    Palette        k-Means (bis `K` Farben) der Kernpixel im Lab-Raum — mehrere Hauttöne
                   (Licht/Schatten) statt eines Mittelwerts; Grau fliegt raus (`CHROMA_MIN`)
    Hautmaske      Pixel, deren Lab-Abstand (ΔE76) zur nächsten Palettenfarbe ≤ `toleranz`
                   ist; Schließen (Poren, Härchen), Öffnen (Streupixel), und nur die Flecken,
                   die am Kern HÄNGEN (`verbunden` — Bereichswachstum wie der Zauberstab:
                   ein hautfarbener Fleck weit weg ist Wand, kein Arm)
    Ergebnis       max(Kern, Hautmaske): außerhalb des Kerns bleibt nur, was Hautton hat

Gerechnet auf höchstens `RECHEN_PX` Pixel Kante (Lab + Abstände zu K Farben über 24 Mio.
Pixel wären Gigabytes), die Maske dann auf Bildgröße gebracht.
"""
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Bildmodellhauttonmaske']


class Bildmodellhauttonmaske:
    K = 5
    PROBEN_MAX = 20000
    RECHEN_PX = 1500
    TOLERANZ = (0, 60)
    VORGABE_TOLERANZ = 20
    #: Palettenfarben unter dieser Buntheit (√(a² + b²)) sind Grau, nicht Haut.
    CHROMA_MIN = 12.0
    #: Klickpunkt-Probe: Kreisradius als Anteil der Bildbreite.
    PUNKT_RADIUS = 0.01
    #: Rückfall ohne Marken: die rembg-Maske um diesen Anteil der Bildbreite erodiert.
    INNEN_RAND = 0.03

    @classmethod
    def proben(cls, form, regler):
        """bool (H, W) der Positivmarken (Striche `drin`, Punkte mit l = 1) — None ohne Marken."""
        import cv2

        from .bildmodellfreistellerkorrektur import Bildmodellfreistellerkorrektur as Kor

        h, w = form
        maske = Kor._strichmaske(form, regler.get('striche') or [], 'drin')
        r = max(2, int(round(cls.PUNKT_RADIUS * w)))
        for x, y, person in regler.get('punkte') or []:
            if person:
                cv2.circle(maske, (int(round(x * (w - 1))), int(round(y * (h - 1)))), r, 1, -1)
        return maske > 0 if maske.any() else None

    @classmethod
    def innen(cls, maske):
        """bool (H, W): das Innere einer weichen Maske (≥ 200, erodiert) — Rückfall-Positivliste."""
        import cv2

        h, w = maske.shape
        f = min(1.0, cls.RECHEN_PX / float(max(h, w)))     # erodieren auf Rechengröße: 241er-Kern
        klein = (maske >= 200).astype(np.uint8)              # auf 4000 px kostete 2 s (21.09.2026)
        if f < 1.0:
            klein = cv2.resize(klein, (max(1, int(w * f)), max(1, int(h * f))), interpolation=cv2.INTER_NEAREST)
        r = max(1, int(round(cls.INNEN_RAND * klein.shape[1])))
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        drin = cv2.erode(klein, k)
        if f < 1.0:
            drin = cv2.resize(drin, (w, h), interpolation=cv2.INTER_NEAREST)
        return drin > 0 if drin.any() else maske >= 128

    @classmethod
    def palette(cls, lab, proben):
        """(K, 3) float32 Lab-Farben der Proben (k-Means); weniger, wenn es weniger Proben gibt."""
        import cv2

        farben = lab[proben].reshape(-1, 3).astype(np.float32)
        if len(farben) > cls.PROBEN_MAX:
            farben = farben[np.random.default_rng(0).choice(len(farben), cls.PROBEN_MAX, replace=False)]
        k = int(min(cls.K, max(1, len(farben) // 50)))
        if k <= 1:
            return farben.mean(axis=0, keepdims=True)
        kriterium = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
        _guete, _zuordnung, mitten = cv2.kmeans(farben, k, None, kriterium, 3, cv2.KMEANS_PP_CENTERS)
        mitten = mitten.astype(np.float32)
        # Haut hat Buntheit; eine graue Palettenfarbe (Schatten, Haar im Rückfall) zöge den grauen
        # Hintergrund mit — Damira 09: Lab (22, 5, 9) hielt den ganzen Grund (gemessen 21.09.2026).
        bunt = np.hypot(mitten[:, 1], mitten[:, 2]) >= cls.CHROMA_MIN
        return mitten[bunt] if bunt.any() else mitten

    @classmethod
    def abstandskarte(cls, rgb, proben):
        """`(abstand (h', w') float32 ΔE zur nächsten Palettenfarbe, f)` auf Rechengröße (f ≤ 1) —
        None ohne Proben. Die Vorschau im Browser schwellt diese Karte selbst (sofort, ohne Server)."""
        import cv2

        h, w = rgb.shape[:2]
        f = cls.RECHEN_PX / float(max(h, w))
        klein, proben_klein = rgb, proben
        if f < 1.0:
            groesse = (max(1, int(w * f)), max(1, int(h * f)))
            klein = cv2.resize(rgb, groesse, interpolation=cv2.INTER_AREA)
            # INTER_AREA + „> 0": auch ein 1-px-Strich überlebt das Verkleinern.
            proben_klein = cv2.resize(proben.astype(np.uint8) * 255, groesse,
                                      interpolation=cv2.INTER_AREA) > 0
        lab = cv2.cvtColor(np.ascontiguousarray(klein), cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[..., 0] *= 100.0 / 255.0                        # OpenCV: L 0..255, a/b um 128
        lab[..., 1:] -= 128.0
        mitten = cls.palette(lab, proben_klein) if proben_klein.any() else None
        if mitten is None:
            logger.warning('Hauttonmaske: keine Proben — Maske leer')
            return None
        abstand = np.full(klein.shape[:2], np.inf, dtype=np.float32)
        for m in mitten:
            abstand = np.minimum(abstand, np.sqrt(((lab - m) ** 2).sum(axis=2)))
        logger.info('Hauttonmaske: %d Palettenfarben, Karte %dx%d', len(mitten), *abstand.shape[::-1])
        return abstand, f

    @classmethod
    def schwellen(cls, abstand, toleranz):
        """uint8 Maske aus der Abstandskarte: ≤ toleranz → 255, dann Schließen 7 / Öffnen 5."""
        import cv2

        toleranz = float(max(cls.TOLERANZ[0], min(cls.TOLERANZ[1], toleranz)))
        maske = (abstand <= toleranz).astype(np.uint8) * 255
        # Poren und Härchen schließen, Streupixel öffnen (in Rechenpixeln).
        maske = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        return cv2.morphologyEx(maske, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

    @classmethod
    def verbunden(cls, maske, figur):
        """uint8: nur die Flecken von `maske` (> 127), die die Figur (bool, gleiche Form) berühren."""
        import cv2

        anzahl, marken = cv2.connectedComponents((maske > 127).astype(np.uint8), connectivity=8)
        if anzahl <= 1:
            return np.zeros_like(maske)
        dran = np.zeros(anzahl, dtype=bool)
        dran[np.unique(marken[figur])] = True
        dran[0] = False
        return np.where(dran[marken], 255, 0).astype(np.uint8)

    @classmethod
    def kern(cls, maske, regler):
        """bool (H, W) — die Figur, die ganz bleibt: das erodierte Innere der Netzmaske UND die
        Marken (Striche/Punkte „Person"). Der Kopf ist bei 3 % Bildbreite Erosion oft weg —
        deshalb markiert Edgar ihn („markiere die Figur, den Kopf, merke dir die Pixel")."""
        marken = cls.proben(maske.shape, regler)
        drin = cls.innen(maske)
        return drin if marken is None else (marken | drin)

    @classmethod
    def aus(cls, rgb, proben, toleranz, figur=None):
        """uint8 (H, W) Maske: 255, wo die Farbe einem Hautton der Positivliste nahe ist — mit
        `figur` (uint8 Netzmaske) nur die Flecken, die an ihr hängen."""
        import cv2

        h, w = rgb.shape[:2]
        karte = cls.abstandskarte(rgb, proben)
        if karte is None:
            return np.zeros((h, w), dtype=np.uint8)
        abstand, f = karte
        maske = cls.schwellen(abstand, toleranz)
        if figur is not None:
            klein = figur if f >= 1.0 else cv2.resize(figur, maske.shape[::-1], interpolation=cv2.INTER_AREA)
            maske = cls.verbunden(maske, klein > 127)
        if f < 1.0:
            maske = cv2.resize(maske, (w, h), interpolation=cv2.INTER_LINEAR)
        logger.info('Hauttonmaske: Toleranz %.0f, Vordergrund %.1f %%', float(toleranz),
                    100.0 * (maske > 127).mean())
        return maske

    @classmethod
    def erweitern(cls, rgb, kern, regler):
        """uint8 Maske: der Kern (bool, `kern`) ganz, dazu hautfarbene Flecken, die an ihm hängen —
        alles andere ist Hintergrund (Edgar: „NUR außerhalb der Figur … suche nach Pixeln, die
        anders in der Farbe sind")."""
        figur = kern.astype(np.uint8) * 255
        haut = cls.aus(rgb, kern, regler.get('toleranz', cls.VORGABE_TOLERANZ), figur)
        return np.maximum(figur, haut)
