# -*- coding: utf-8 -*-
"""Blendimportschamregister — das Scham-Stück passt sich der Figur an, nicht umgekehrt (09.10.2026).

Das Stück ist aus dem ORIGINAL geschnitten, das Loch ist in der HAUT DER FIGUR. Passt die Figur dort nicht zum Original, liegen
beide aneinander vorbei, und der Rand des Stücks erreicht den Ring des Lochs nur, wenn man ihn über Zentimeter zieht (Keile).

Gemessen 09.10.2026 an einem Import ohne Umposen („Asian Female", Datei ohne Skelett; `asian_dump.py`, `asian_verschiebung.py`): Die
Stück-Punkte liegen im Median 42 mm von der Haut der Figur, die Randpunkte im Median 9 mm, 90. Perzentil 53 mm, größter 74 mm — und
die Abweichung geht fast nur ENTLANG DER HAUTNORMALEN (in der Fläche Median 0,0 mm): die Figur steht dort vor dem Original (Median
34 mm). Eine glatte Verschiebung der Umgebung, kein Formfehler des Stücks.

`anwenden` (kein Wissen über ein Modell): Die Originalpunkte in der Umgebung des Stücks (außerhalb der Kontur, höchstens `BAND_MM` von
ihm) sind dort, wo Original und Figur dasselbe Körperteil sind, ein Maß für die Abweichung: der Vektor von jedem zum nächsten Punkt der
Figurfläche. Das ganze Stück wandert um den MEDIAN dieser Vektoren — eine Verschiebung, keine Verformung. Passen Original und Figur
(Normalfall), sind die Vektoren Millimeter und das Stück bleibt, wo es war; weichen sie um mehr als `MAX_SCHUB_MM` ab, gibt es kein Stück.

NICHT MEHR: eine ortsabhängige Verschiebung (1/d²-gewichtet über die Vektoren der Umgebung, danach noch einmal über die Randpunkte). Gemessen
09.10.2026 an „cute girl" (`ProjektTemp/_wegwerf/scham_naht/register_proto.py`; Original ist symmetrisch: Spiegelabstand 0,34 mm): sie
schob die Lippen (|x| < 10 mm) im Median um 9,8 mm (größte 22,4 mm) und machte sie unsymmetrisch (Spiegelabstand 90. Perzentil 5,6 mm) —
Edgar: „warum so unregelmäßig???", „der schlechteste Stand bei cute girl seit heute morgen". Eine Verschiebung als Ganzes lässt die Lippen
bei 1,1 mm (Spiegelabstand 0,43 mm). Preis: der Rand liegt etwas weiter vom Ring (Rand-Weg im Bau 90. Perzentil 11,3 mm, größter 13,8 mm,
statt 6,0 / 7,4 mm; Grenze `Blendimportschamgeograft.MAX_RAND_WEG_MM` 20 mm) — das Verschweißen holt ihn auf den Ring.

`beschneiden`: Teile des Stücks, die nicht über dem Loch liegen, ersetzen keine Haut und entfallen (gemessen nach `anwenden`: eine Zunge
des Stücks lag bis 53 mm hinter dem Loch).
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportschamregister']


class Blendimportschamregister:
    #: Originalpunkte außerhalb der Kontur bis so weit (mm, im Raum) vom Stück sind Stützpunkte.
    BAND_MM = 25.0
    #: Weiter als das vom Original entfernte Punkte der Figur (m) sind kein Gegenstück, sondern ein anderes Körperteil.
    AUSREISSER_M = 0.08
    #: Zahl der nächsten Stützpunkte je Stückpunkt und Dämpfung der Gewichte 1/(d + EPS)² (m).
    NACHBARN = 24
    EPS_M = 0.002
    #: Weniger Stützpunkte: keine Aussage über die Umgebung, das Stück bleibt.
    MINDEST = 12
    #: Weicht die Umgebung im Median um mehr (mm) von der Figur ab, gibt es kein Stück: es müsste als Ganzes um Zentimeter wandern, und
    #: seine Form (Lippen, Damm) stimmte nicht mehr zur Haut daneben. Gemessen 09.10.2026: „cute girl" 5,6 mm, „Fallout ranger" 2,6 mm,
    #: ein Import ohne Umposen („Asian Female") 39,8 mm — das Stück sah grotesk aus (Edgar). Die Grenze dazwischen ist eine Setzung.
    MAX_SCHUB_MM = 20.0

    @classmethod
    def anwenden(cls, flaeche, original, schnitt, stueck):
        """`(neue Punkte des Stücks, bericht)` — EINE Verschiebung für das ganze Stück (Median der Umgebung): die Lippen behalten die Form
        des Originals.

        `flaeche`: Haut der Figur (trimesh); `original`: alle Punkte des Originals; `schnitt`: Schnittwert je Originalpunkt
        (`Blendimportscham.schnittwerte`, negativ = im Stück); `stueck`: Punkte des Stücks."""
        from scipy.spatial import cKDTree

        nah_am_stueck, _ = cKDTree(stueck).query(original)
        band = np.flatnonzero((schnitt > 0.0) & (nah_am_stueck <= cls.BAND_MM / 1000.0))
        feld, umgebung = cls._schritt(flaeche, original[band], stueck)
        if umgebung.get('schub_median_mm', 0.0) > cls.MAX_SCHUB_MM:
            return stueck, {'aus': 'Figur und Original weichen am Becken im Median um %.0f mm voneinander ab (Grenze %.0f mm): das Stück passt '
                                   'nicht zur Figur, die Figur behält ihre eigene Anatomie' % (umgebung['schub_median_mm'], cls.MAX_SCHUB_MM)}
        neu, umgebung['verschiebung_mm'] = cls._verschieben(flaeche, original[band], stueck)
        bericht = {'umgebung': umgebung}
        logger.info('Scham-Stück registriert: %s', bericht)
        return neu, bericht

    @classmethod
    def beschneiden(cls, haut, im_loch, punkte, dreiecke, uv_ecken):
        """`(punkte, dreiecke, uv_ecken, entfernt)`: nur Dreiecke des Stücks behalten, von denen mindestens ein Punkt über dem Loch liegt
        (sein nächster Punkt der Haut gehört zu einem Dreieck des Lochs, den Ring eingeschlossen).

        `haut`: `Blendimportschamloch`; `im_loch`: Maske der Dreiecke des Lochs."""
        from scipy.spatial import cKDTree

        im_loch_punkt = np.zeros(len(haut.punkte), dtype=bool)
        im_loch_punkt[haut.dreiecke[im_loch].ravel()] = True
        nah = cKDTree(haut.punkte).query(punkte)[1]
        behalten = im_loch_punkt[nah][dreiecke].any(axis=1)
        if behalten.all():
            return punkte, dreiecke, uv_ecken, 0
        benutzt, neu = np.unique(dreiecke[behalten], return_inverse=True)
        return punkte[benutzt], neu.reshape(-1, 3), uv_ecken[behalten], int((~behalten).sum())

    @classmethod
    def _verschieben(cls, flaeche, stuetz, stueck):
        """`(Punkte + Median-Vektor der Umgebung, Länge des Vektors in mm)`: das ganze Stück um denselben Betrag, ohne Verformung."""
        import trimesh

        ziel, abstand, _ = trimesh.proximity.closest_point(flaeche, stuetz)
        gut = abstand <= cls.AUSREISSER_M
        if int(gut.sum()) < cls.MINDEST:
            return stueck, 0.0
        vektor = np.median((ziel - stuetz)[gut], axis=0)
        return stueck + vektor, round(float(np.linalg.norm(vektor)) * 1000.0, 2)

    @classmethod
    def _schritt(cls, flaeche, stuetz, stueck):
        """`(Punkte + Verschiebung, bericht)`: Vektoren der Stützpunkte zur Figurfläche, 1/d²-gewichtet auf alle Punkte des Stücks.
        Hier nur noch das Maß für die Grenze `MAX_SCHUB_MM` (Median der Verschiebung am Stück); verschoben wird es mit `_verschieben`."""
        import trimesh
        from scipy.spatial import cKDTree

        if len(stuetz) < cls.MINDEST:
            return stueck, {'aus': 'nur %d Stützpunkte' % len(stuetz)}
        ziel, abstand, _ = trimesh.proximity.closest_point(flaeche, stuetz)
        gut = abstand <= cls.AUSREISSER_M
        if int(gut.sum()) < cls.MINDEST:
            return stueck, {'aus': 'nur %d Stützpunkte nahe der Figur' % int(gut.sum())}
        stuetz, vektor = stuetz[gut], (ziel - stuetz)[gut]
        k = min(cls.NACHBARN, len(stuetz))
        d, i = cKDTree(stuetz).query(stueck, k=k)
        d, i = d.reshape(len(stueck), k), i.reshape(len(stueck), k)
        gewicht = 1.0 / (d + cls.EPS_M) ** 2
        schub = (gewicht[:, :, None] * vektor[i]).sum(axis=1) / gewicht.sum(axis=1)[:, None]
        betrag = np.linalg.norm(schub, axis=1) * 1000.0
        return stueck + schub, {'stuetz': int(len(stuetz)), 'ausreisser': int((~gut).sum()),
                                'schub_median_mm': round(float(np.median(betrag)), 2), 'schub_max_mm': round(float(betrag.max()), 1)}
