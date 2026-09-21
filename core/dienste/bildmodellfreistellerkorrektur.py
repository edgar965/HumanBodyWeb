# -*- coding: utf-8 -*-
"""Bildmodellfreistellerkorrektur — die Maske des Freistellers halbautomatisch und von Hand
nachbessern (21.09.2026).

Edgar: „Das Hintergrund entfernen feature könnte mehr automatische, halbautomatischen und
manuelle Möglichkeiten enthalten zur Korrektur?" — die grauen Ränder der Textur kamen von
Maskenkanten, die neben der Person lagen. Drei Stufen, alle auf der weichen rembg-Maske
(`Bildmodellfreisteller.maske`), alle mit cv2 in python14, ohne Netz:

    weisskey(rgb)             automatisch für gerenderte Vorlagen auf einfarbigem Grund: die
                              Hintergrundfarbe aus den vier Ecken, alles im Abstand `KEY_TOLERANZ`
                              davon ist Hintergrund — exakte Kante, kein Netz nötig
    grabcut(rgb, alpha, …)    halbautomatisch: GrabCut (Rother 2004) mit der Maske als Start
                              (sicher innen / sicher außen / unsicher am Rand) und den Strichen
                              als feste Vorgabe, auf höchstens `GRABCUT_PX` Pixel Kante
    striche(alpha, striche)   von Hand: Pinselstriche `drin` (Alpha 1) und `draussen` (Alpha 0),
                              Punkte normiert 0..1, Breite als Anteil der Bildbreite — sie
                              gelten zuletzt und immer

Die Striche kommen aus `freistellerpinsel.js` als `[{art, breite, punkte: [[x, y], …]}]`.
"""

import numpy as np

__all__ = ['Bildmodellfreistellerkorrektur']


class Bildmodellfreistellerkorrektur:
    KEY_TOLERANZ = 28.0
    GRABCUT_PX = 900
    GRABCUT_RUNDEN = 3
    #: Unsicher ist das Band um die Kante: Alpha zwischen diesen Werten.
    UNSICHER = (0.05, 0.95)
    ARTEN = ('drin', 'draussen')

    # ----------------------------------------------------------- Striche

    @classmethod
    def striche_pruefen(cls, roh, hoechstens=400):
        """Nur wohlgeformte Striche: Art bekannt, Breite 0–0,2, Punkte als Paare 0..1."""
        aus = []
        for s in (roh if isinstance(roh, list) else [])[:hoechstens]:
            if not isinstance(s, dict) or s.get('art') not in cls.ARTEN:
                continue
            try:
                breite = float(s.get('breite') or 0.02)
            except (TypeError, ValueError):
                breite = 0.02
            punkte = []
            for p in (s.get('punkte') or [])[:5000]:
                try:
                    x, y = float(p[0]), float(p[1])
                except (TypeError, ValueError, IndexError):
                    continue
                if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                    punkte.append([x, y])
            if punkte:
                # Mindestbreite 0,0002 = 1 px bei 5000 px (Edgar: „der Stift ist viel zu dick").
                aus.append({'art': s['art'], 'breite': max(0.0002, min(0.2, breite)), 'punkte': punkte})
        return aus

    @classmethod
    def punkte_pruefen(cls, roh, hoechstens=50):
        """SAM-Klickpunkte `[[x, y, l], …]` normiert, l = 1 Person / 0 Hintergrund."""
        aus = []
        for p in (roh if isinstance(roh, list) else [])[:hoechstens]:
            try:
                x, y, l = float(p[0]), float(p[1]), int(p[2])
            except (TypeError, ValueError, IndexError):
                continue
            if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
                aus.append([round(x, 4), round(y, 4), 1 if l else 0])
        return aus

    @classmethod
    def _strichmaske(cls, form, striche, art):
        """uint8 (H, W): 1, wo Striche dieser Art liegen."""
        import cv2

        h, w = form
        maske = np.zeros((h, w), dtype=np.uint8)
        for s in striche:
            if s['art'] != art:
                continue
            dicke = max(1, int(round(s['breite'] * w)))
            punkte = np.asarray([[p[0] * (w - 1), p[1] * (h - 1)] for p in s['punkte']], dtype=np.int32)
            if len(punkte) == 1:
                cv2.circle(maske, tuple(int(v) for v in punkte[0]), max(1, dicke // 2), 1, -1)
            else:
                cv2.polylines(maske, [punkte.reshape(-1, 1, 2)], False, 1, thickness=dicke,
                              lineType=cv2.LINE_AA)
        return maske

    @classmethod
    def striche(cls, alpha, striche):
        """Die Striche auf die Alphamaske (float 0..1) — `drin` → 1, `draussen` → 0."""
        if not striche:
            return alpha
        aus = np.asarray(alpha, dtype=np.float32).copy()
        drin = cls._strichmaske(aus.shape, striche, 'drin') > 0
        draussen = cls._strichmaske(aus.shape, striche, 'draussen') > 0
        aus[drin] = 1.0
        aus[draussen] = 0.0
        return aus

    # ----------------------------------------------------------- GrabCut

    @classmethod
    def grabcut(cls, rgb, alpha, striche=None):
        """Die Maske mit GrabCut an die Bildkanten legen; Striche als sichere Vorgabe."""
        import cv2

        h, w = alpha.shape[:2]
        f = min(1.0, cls.GRABCUT_PX / float(max(h, w)))
        klein = (max(2, int(w * f)), max(2, int(h * f)))
        bild = cv2.resize(np.asarray(rgb, dtype=np.uint8), klein, interpolation=cv2.INTER_AREA)
        a = cv2.resize(np.asarray(alpha, dtype=np.float32), klein, interpolation=cv2.INTER_AREA)
        maske = np.full(a.shape, cv2.GC_PR_BGD, dtype=np.uint8)
        maske[a >= cls.UNSICHER[0]] = cv2.GC_PR_FGD
        maske[a >= cls.UNSICHER[1]] = cv2.GC_FGD
        maske[a < cls.UNSICHER[0]] = cv2.GC_BGD
        # Ein Band um die Kante bleibt unsicher, sonst hat GrabCut nichts zu entscheiden.
        kante = cv2.dilate((a >= 0.5).astype(np.uint8), np.ones((9, 9), np.uint8)) \
            - cv2.erode((a >= 0.5).astype(np.uint8), np.ones((9, 9), np.uint8))
        maske[(kante > 0) & (maske == cv2.GC_FGD)] = cv2.GC_PR_FGD
        maske[(kante > 0) & (maske == cv2.GC_BGD)] = cv2.GC_PR_BGD
        if striche:
            maske[cls._strichmaske(a.shape, striche, 'drin') > 0] = cv2.GC_FGD
            maske[cls._strichmaske(a.shape, striche, 'draussen') > 0] = cv2.GC_BGD
        hinten = np.zeros((1, 65), np.float64)
        vorn = np.zeros((1, 65), np.float64)
        try:
            cv2.grabCut(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR), maske, None, hinten, vorn,
                        cls.GRABCUT_RUNDEN, cv2.GC_INIT_WITH_MASK)
        except cv2.error:
            return alpha      # z. B. alles sicher: nichts zu rechnen
        neu = ((maske == cv2.GC_FGD) | (maske == cv2.GC_PR_FGD)).astype(np.float32)
        # GrabCuts Entscheidung ist hart; das Hochrechnen macht die Kante einen Pixel weich,
        # den Rest tut der Regler „Weich" danach.
        return cv2.resize(neu, (w, h), interpolation=cv2.INTER_LINEAR)

    # ----------------------------------------------------------- Weiß-Key

    @classmethod
    def weisskey(cls, rgb):
        """Maske (uint8 0/255) aus der Hintergrundfarbe der Ecken — für Renderings auf Weiß."""
        import cv2

        bild = np.asarray(rgb, dtype=np.float32)
        h, w = bild.shape[:2]
        r = max(2, min(h, w) // 40)
        ecken = np.concatenate([bild[:r, :r].reshape(-1, 3), bild[:r, -r:].reshape(-1, 3),
                                bild[-r:, :r].reshape(-1, 3), bild[-r:, -r:].reshape(-1, 3)])
        farbe = np.median(ecken, axis=0)
        abstand = np.linalg.norm(bild - farbe[None, None, :], axis=2)
        hinter = (abstand <= cls.KEY_TOLERANZ).astype(np.uint8)
        # Nur der Hintergrund, der mit dem Rand verbunden ist — Weiß IM Motiv bleibt Motiv.
        markiert = np.zeros((h + 2, w + 2), np.uint8)
        verbunden = np.zeros_like(hinter)
        for y, x in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1), (0, w // 2), (h - 1, w // 2),
                     (h // 2, 0), (h // 2, w - 1)):
            if hinter[y, x] and not verbunden[y, x]:
                flut = hinter.copy()
                cv2.floodFill(flut, markiert, (x, y), 2)
                verbunden |= (flut == 2).astype(np.uint8)
                markiert[:] = 0
        return ((1 - verbunden) * 255).astype(np.uint8)
