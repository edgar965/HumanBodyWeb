# -*- coding: utf-8 -*-
"""Lippenrand — die Lippen als Kantenschleifen des Basisnetzes.

WARUM (Edgar, 17.09.2026, Bild aus der Szene: „lippen: farbe nicht bis zum
lippenrand"): Bis heute bestimmte eine LINSE (`lippenlinse.py`, analytische
Form um die Mundlinie) je Punkt, ob er Lippe ist. Am Grundkörper stimmte
sie auf 1 mm; sobald ein Morph die Lippen formt (`Mouth_LowerlipSizeZ`,
`Mouth_SizeX` …), lag der Rand daneben — eine Linse kennt keine Morphs.

Das Netz kennt seinen Lippenrand: Die Lippen sind als konzentrische
KANTENSCHLEIFEN um die Mundöffnung modelliert, und der Rand des Lippenrots
ist eine davon — mit einem Knick (Diederwinkel) entlang der Schleife. Eine
Schleife ist Topologie: Sie wandert mit jedem Morph, weil die Punkte selbst
wandern. Gemessen am weiblichen Grundkörper (`ProjektTemp/lippen/`):
Mundöffnung z 1501,5 mm, Oberlippenrand Schleife 3 (Amorbogen, Mitte
1508,5, Spitzen bei x ±6 mm auf 1509,9; Knick entlang 22°, danach 11°),
Unterlippenrand Schleife 3 (1491,4; Knick 15°, danach 5°) — männlich
Schleifen 2 und 3 (1652,6 mit Bogen, 1635,8).

Der Weg:
1. Vorn ist, wessen Punktnormale nach vorn zeigt — die Innenseiten der
   Lippen zeigen zu den Zähnen (Anteil ≤ 0, die Lippen ≥ 0,1; dazwischen
   liegt am Grundkörper kein Punkt). Der Saum der Mundöffnung sind die
   vorderen Punkte im Umriss der MB-Lab-Lipmap, die einen verborgenen
   Nachbarn haben: eine geschlossene Reihe um die Öffnung.
2. Schleifen nach außen: Breitensuche über die Kanten, nur durch vordere
   Punkte — von einer geschlossenen Reihe aus sind das die Kantenschleifen.
3. Randschleife je Seite: die Schleife, hinter der die Fläche flach wird —
   der größte Abfall des Knicks (Diederwinkel entlang der Schleife) zur
   nächsten; nur wo die Lipmap noch malt, und nicht die erste Schleife (sie
   trägt den Knick der Mundlinie).
4. Je Punkt der Vorzeichenabstand (mm) zur Randschleife: innen positiv,
   außen negativ, verborgene Punkte der Mundhöhle innen (sie schließen die
   Lippen an der Mundlinie ab).

Das Feld entsteht am Basisnetz (18.210 Punkte) und geht durch dieselbe
Catmull-Clark-Matrix wie die Geometrie (`unterteiler.subdivide`): Der
Nullpunkt liegt dann auf jeder Stufe dort, wo die Schleife liegt.
"""

import logging
from collections import deque

import numpy as np

logger = logging.getLogger(__name__)

__all__ = ['Lippenrand']


class Lippenrand:
    """Vorzeichenabstand zum Lippenrand je Netzpunkt — aus den Kantenschleifen."""

    #: Lipmap-Wert (0..255), ab dem ein Punkt im Umriss der Maske liegt.
    UMRISS = 5
    #: Maskenmittel (0..255) einer Schleife, unter dem sie kein Lippenrand ist.
    MASKENREST = 3
    #: Anteil der Punktnormale nach vorn, ab dem ein Punkt „vorn" ist.
    VORN = 0.1
    #: Zahl der Schleifen nach außen.
    SCHLEIFEN = 8
    #: Verborgene Punkte bis hierhin (m) hinter der Mundlinie sind Mundhöhle.
    HOEHLE = 0.025
    #: Abstand (mm) ohne Rechnung: weit außen bzw. verborgen innen.
    AUSSEN = -10.0
    INNEN = 10.0

    _basis = {}  # geschlecht -> Feld am Basisnetz (mm)

    # ---------------------------------------------------------------- Zugang

    @classmethod
    def abstand(cls, geschlecht, unterteiler=None):
        """Das Feld (mm) für das Netz des Geschlechts — unterteilt, wenn ein
        Unterteiler mitkommt; None, wenn sich kein Rand bestimmen lässt."""
        basis = cls.basis(geschlecht)
        if basis is None or unterteiler is None:
            return basis
        fein = unterteiler.subdivide(basis[:, None])[:, 0]
        return np.clip(fein, cls.AUSSEN, cls.INNEN)

    @classmethod
    def basis(cls, geschlecht):
        """Das Feld am Basisnetz — je Geschlecht einmal gerechnet."""
        if geschlecht not in cls._basis:
            cls._basis[geschlecht] = cls._rechnen(geschlecht)
        return cls._basis[geschlecht]

    @classmethod
    def vergessen(cls):
        cls._basis.clear()

    @classmethod
    def _rechnen(cls, geschlecht):
        from .charakterdaten import Charakterdaten
        from .lippenmaske import Lippenmaske

        netz = Charakterdaten.netzdaten(geschlecht)
        punkte = Lippenmaske.basispunkte(geschlecht, None)
        datei = Lippenmaske.ordner() / Lippenmaske.DATEI.get(geschlecht, '')
        fehlt = punkte is None or netz.faces is None or netz.uvs is None
        if fehlt or not datei.is_file():
            logger.warning('Lippenrand (%s): Netz, UVs oder Lipmap fehlen', geschlecht)
            return None
        haut = np.asarray(netz.faces)[np.asarray(netz.face_materials) == 0]
        maske = cls.maskenwerte(np.asarray(netz.uvs), Lippenmaske.maske(datei))
        feld = cls.feld(punkte, haut, maske)
        if feld is not None:
            logger.info(
                'Lippenrand (%s): %d Punkte innen, %d im Saum',
                geschlecht,
                int((feld > 0).sum()),
                int((np.abs(feld) < 6).sum()),
            )
        return feld

    @staticmethod
    def maskenwerte(uvs, maske):
        """Der Lipmap-Wert (0..255) je Punkt — Bildzeile 0 ist oben, v = 1 auch."""
        hoehe, breite = maske.shape[:2]
        u = np.clip(np.rint(uvs[:, 0] * (breite - 1)).astype(int), 0, breite - 1)
        w = np.clip(np.rint((1 - uvs[:, 1]) * (hoehe - 1)).astype(int), 0, hoehe - 1)
        return maske[w, u]

    # ------------------------------------------------------------------ Feld

    @classmethod
    def feld(cls, punkte, quads, maske):
        """Vorzeichenabstand (mm) je Punkt aus Punkten (N, 3), Hautvierecken
        (F, 4) und Lipmap-Wert je Punkt (N) — oder None."""
        p = np.asarray(punkte, dtype=float)
        q = np.asarray(quads, dtype=np.int64)
        maske = np.asarray(maske)
        normalen = cls.flaechennormalen(p, q)
        kanten = cls.kanten(q)
        knick = cls.knick(kanten, normalen)
        vorn = cls.vorn(len(p), q, normalen)
        nachbarn = cls.nachbarn(len(p), kanten)
        umriss = maske >= cls.UMRISS
        mund = cls.mundoeffnung(nachbarn, vorn, umriss)
        if len(mund) < 10:
            logger.warning('Lippenrand: keine Mundöffnung (%d Punkte)', len(mund))
            return None
        zm = float(np.median(p[sorted(mund), 2]))
        stufe = cls.ringe(nachbarn, mund, vorn)
        schleifen = cls.schleifen(kanten, stufe)
        rand = cls.randschleifen(schleifen, p, knick, maske, zm)
        if rand is None:
            logger.warning('Lippenrand: keine Randschleife gefunden')
            return None
        logger.info(
            'Lippenrand: Mundöffnung %d Punkte auf %.4f m, Randschleife oben %d, unten %d',
            len(mund),
            zm,
            rand[0],
            rand[1],
        )
        haut = np.zeros(len(p), dtype=bool)
        haut[q.ravel()] = True
        return cls.abstaende(p, schleifen, stufe, rand, zm, vorn, haut & umriss, mund)

    @staticmethod
    def flaechennormalen(p, q):
        n = np.cross(p[q[:, 2]] - p[q[:, 0]], p[q[:, 3]] - p[q[:, 1]])
        return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)

    @staticmethod
    def kanten(q):
        """{(a, b): [Flächen]} mit a < b — je Kante die angrenzenden Vierecke."""
        kanten = {}
        for f, viereck in enumerate(q.tolist()):
            for i in range(4):
                a, b = viereck[i], viereck[(i + 1) % 4]
                kanten.setdefault((min(a, b), max(a, b)), []).append(f)
        return kanten

    @staticmethod
    def knick(kanten, normalen):
        """Diederwinkel (Grad) je Kante mit genau zwei Flächen."""
        aus = {}
        for kante, fl in kanten.items():
            if len(fl) == 2:
                c = float(np.clip(np.dot(normalen[fl[0]], normalen[fl[1]]), -1.0, 1.0))
                aus[kante] = float(np.degrees(np.arccos(c)))
        return aus

    @classmethod
    def vorn(cls, anzahl, q, normalen):
        """Ob die Punktnormale (Summe der Flächennormalen) nach vorn (−y) zeigt."""
        summe = np.zeros((anzahl, 3))
        for i in range(4):
            np.add.at(summe, q[:, i], normalen)
        return -summe[:, 1] > cls.VORN * np.linalg.norm(summe, axis=1)

    @staticmethod
    def nachbarn(anzahl, kanten):
        """Je Punkt die Nachbarn über Kanten."""
        aus = [[] for _ in range(anzahl)]
        for a, b in kanten:
            aus[a].append(b)
            aus[b].append(a)
        return aus

    @staticmethod
    def mundoeffnung(nachbarn, vorn, umriss):
        """Der Saum der Mundöffnung: vordere Punkte im Umriss der Maske mit
        einem verborgenen Nachbarn (Innenseite der Lippe)."""
        return set(int(i) for i in np.flatnonzero(vorn & umriss) if any(not vorn[j] for j in nachbarn[i]))

    @classmethod
    def ringe(cls, nachbarn, mund, vorn):
        """Schleifenstufe je Punkt: 0 = Mundöffnung, 1.. nach außen, −1 keine.
        Breitensuche nur durch vordere Punkte."""
        stufe = np.full(len(nachbarn), -1)
        start = sorted(mund)
        stufe[start] = 0
        schlange = deque(start)
        while schlange:
            i = schlange.popleft()
            if stufe[i] >= cls.SCHLEIFEN:
                continue
            for j in nachbarn[i]:
                if vorn[j] and stufe[j] < 0:
                    stufe[j] = stufe[i] + 1
                    schlange.append(j)
        return stufe

    @staticmethod
    def schleifen(kanten, stufe):
        """Je Stufe die Kanten ENTLANG der Schleife (beide Enden auf der Stufe)."""
        aus = [[] for _ in range(int(stufe.max()) + 1)]
        for a, b in kanten:
            if stufe[a] >= 0 and stufe[a] == stufe[b]:
                aus[stufe[a]].append((a, b))
        return aus

    @classmethod
    def schleifenwerte(cls, schleifen, p, knick, maske, zm, oben):
        """Je Schleife (Knick entlang, Maskenmittel) auf EINER Seite —
        Knick als Mittel der Diederwinkel ihrer Kanten, Maske als Mittel
        ihrer Punkte; ohne Kanten auf der Seite (0, 0)."""
        aus = []
        for kanten in schleifen:
            seitlich = [(a, b) for a, b in kanten if ((p[a, 2] + p[b, 2]) / 2 > zm) == oben]
            winkel = [knick[k] for k in seitlich if k in knick]
            punkte = sorted(set(i for kante in seitlich for i in kante))
            aus.append(
                (float(np.mean(winkel)) if winkel else 0.0, float(np.mean(maske[punkte])) if punkte else 0.0)
            )
        return aus

    @classmethod
    def randschleifen(cls, schleifen, p, knick, maske, zm):
        """(Schleife oben, Schleife unten): der Lippenrand ist die Schleife,
        hinter der die Fläche flach wird — der größte ABFALL des Knicks zur
        nächsten Schleife. Nur wo die Lipmap noch etwas malt (Maskenmittel
        ≥ MASKENREST), sonst gewänne die Nasenbasis; und nicht Schleife 1:
        die trägt immer den Knick der Mundlinie."""
        aus = []
        for oben in (True, False):
            werte = cls.schleifenwerte(schleifen, p, knick, maske, zm, oben)
            beste = None
            for k in range(2, len(werte) - 1):
                if werte[k][1] < cls.MASKENREST:
                    continue
                abfall = werte[k][0] - werte[k + 1][0]
                if beste is None or abfall > beste[1]:
                    beste = (k, abfall)
            if beste is None:
                return None
            aus.append(beste[0])
        return tuple(aus)

    @classmethod
    def abstaende(cls, p, schleifen, stufe, rand, zm, vorn, haut, mund):
        """Das Feld: Vorzeichenabstand zur Randschleife, Mundhöhle innen —
        `haut` sind die Hautpunkte im Umriss der Lipmap (nur die kommen als
        Mundhöhle in Frage; Wangenhaut mit seitlicher Normale nicht)."""
        oben = p[:, 2] > zm
        segmente = [
            (a, b)
            for seite, k in enumerate(rand)
            for a, b in schleifen[k]
            if ((p[a, 2] + p[b, 2]) / 2 > zm) == (seite == 0)
        ]
        A = p[[s[0] for s in segmente]]
        AB = p[[s[1] for s in segmente]] - A
        L2 = np.maximum((AB * AB).sum(axis=1), 1e-12)
        feld = np.full(len(p), cls.AUSSEN)
        for i in np.flatnonzero(stufe >= 0):
            grenze = rand[0] if oben[i] else rand[1]
            if stufe[i] == grenze:
                feld[i] = 0.0
                continue
            t = np.clip(((p[i] - A) * AB).sum(axis=1) / L2, 0.0, 1.0)
            d = 1000.0 * float(np.linalg.norm(A + t[:, None] * AB - p[i], axis=1).min())
            feld[i] = min(d, cls.INNEN) if stufe[i] < grenze else max(-d, cls.AUSSEN)
        # Verborgene Punkte der Mundhöhle: innen, damit die Lippen an der
        # Mundlinie geschlossen sind — nicht der Nacken (HOEHLE).
        mundpunkte = sorted(mund)
        xc = float(np.abs(p[mundpunkte, 0]).max()) + 0.005
        tiefe = float(np.median(-p[mundpunkte, 1]))
        nah = (np.abs(p[:, 0]) <= xc) & (np.abs(p[:, 2] - zm) <= 0.015)
        dahinter = (-p[:, 1] >= tiefe - cls.HOEHLE) & (-p[:, 1] <= tiefe)
        hoehle = haut & (~vorn) & nah & dahinter & (stufe < 0)
        feld[hoehle] = cls.INNEN
        return feld
