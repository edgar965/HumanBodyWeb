# -*- coding: utf-8 -*-
u"""Brauenbogen — wo die Braue im UV-Raum liegt: Mittellinie, Fenster, Maßstab.

Die Vorgabe für die gezeichnete Braue (`Brauendecal`) ist die Braue, die
MB-Lab in die Referenz-Albedo (`hum_f_cauc` / `hum_m_cauc`) gemalt hat —
anatomisch an der richtigen Stelle, im selben UV-Raum wie das Netz. Aus
ihrer Maske (`Brauenretusche.brauenmaske`) kommt je Seite die Mittellinie
(Spalte für Spalte die mittlere Zeile, geglättet), von INNEN (Nase, u nahe
0,5) nach AUSSEN. Das Fenster ist die Zone der Brauenpunkte plus Rand; der
Maßstab mm je UV-Einheit kommt aus dem Netz (3D-Abstand zu UV-Abstand
benachbarter Brauenpunkte).

Ergebnis als JSON unter `media/hauttexturen/brauenbogen_<geschlecht>.json`
(Projekt, nicht System-Temp), neu bei höherer `FASSUNG`.
"""
import json
import logging
from pathlib import Path

import numpy as np
from django.conf import settings

from .brauenretusche import Brauenretusche

logger = logging.getLogger('core')


class Brauenbogen:

    FASSUNG = 1
    REFERENZ = {'female': 'hum_f_cauc_albedo.png', 'male': 'hum_m_cauc_albedo.png'}
    #: Rand ums Fenster in Pixeln der 2048²-Textur (Regler schieben bis ±20 mm).
    RAND_PX = 48
    GLAETTUNG = 9
    ORDNER = Brauenretusche.ORDNER

    @classmethod
    def laden(cls, geschlecht):
        u"""`{fenster: [u0, v0, u1, v1], links: [[u, v], …], rechts: […],
        mm_je_uv: float, form: [h, w]}` — aus der Ablage oder frisch."""
        geschlecht = 'male' if geschlecht == 'male' else 'female'
        ziel = cls.ORDNER / ('brauenbogen_%s.json' % geschlecht)
        if ziel.is_file():
            with open(ziel, encoding='utf-8') as datei:
                daten = json.load(datei)
            if daten.get('fassung') == cls.FASSUNG:
                return daten
        daten = cls.bestimmen(geschlecht)
        cls.ORDNER.mkdir(parents=True, exist_ok=True)
        with open(ziel, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei)
        return daten

    @classmethod
    def bestimmen(cls, geschlecht):
        from .lippenmaske import Lippenmaske
        from scipy import ndimage
        quelle = Lippenmaske.ordner() / cls.REFERENZ[geschlecht]
        maske, zone = Brauenretusche.brauenmaske(quelle)
        hoehe, breite = maske.shape
        marken, anzahl = ndimage.label(maske)
        groessen = ndimage.sum(maske, marken, range(1, anzahl + 1))
        beste = np.argsort(groessen)[::-1][:2] + 1
        seiten = {}
        for marke in beste:
            linie = cls.mittellinie(marken == marke)
            mitte_u = float(np.mean(linie[:, 0]))
            seiten['links' if mitte_u < breite / 2 else 'rechts'] = linie
        ys, xs = np.nonzero(zone)
        u0 = max(0, xs.min() - cls.RAND_PX)
        u1 = min(breite - 1, xs.max() + cls.RAND_PX)
        w0 = max(0, ys.min() - cls.RAND_PX)
        w1 = min(hoehe - 1, ys.max() + cls.RAND_PX)
        daten = {'fassung': cls.FASSUNG, 'form': [hoehe, breite],
                 'fenster': [float(u0 / (breite - 1)), float(1 - w1 / (hoehe - 1)),
                             float(u1 / (breite - 1)), float(1 - w0 / (hoehe - 1))],
                 'mm_je_uv': cls.massstab()}
        for seite, linie in seiten.items():
            # von innen (Nasenseite) nach außen
            innen_rechts = seite == 'links'
            reihe = linie[np.argsort(linie[:, 0])]
            if innen_rechts:
                reihe = reihe[::-1]
            daten[seite] = [[float(u / (breite - 1)), float(1 - w / (hoehe - 1))]
                            for u, w in reihe]
        logger.info('Brauenbogen %s: %s, Fenster %s, %.0f mm/UV', geschlecht,
                    {k: len(v) for k, v in seiten.items()}, daten['fenster'],
                    daten['mm_je_uv'])
        return daten

    @classmethod
    def mittellinie(cls, komponente):
        u"""Je Spalte die mittlere Zeile → (n, 2) Pixelkoordinaten (u, w)."""
        ys, xs = np.nonzero(komponente)
        spalten = np.unique(xs)
        mitten = np.array([ys[xs == x].mean() for x in spalten])
        k = min(cls.GLAETTUNG, len(mitten) if len(mitten) % 2 else len(mitten) - 1)
        if k >= 3:
            kern = np.ones(k) / k
            innen = np.convolve(mitten, kern, mode='valid')
            mitten = np.concatenate([mitten[:k // 2], innen, mitten[-(k // 2):]])
        return np.column_stack([spalten, mitten])

    @classmethod
    def massstab(cls):
        u"""mm je UV-Einheit im Brauenbereich: Median über nächste Nachbarn."""
        from scipy.spatial import cKDTree
        einheiten, uvs = Brauenretusche.zutaten()
        punkte = np.load(str(Path(settings.HUMANBODY_ROOT) / 'data' / 'humanBody'
                             / 'vertices_tpose.npy')).astype(np.float64)
        idx = Brauenretusche.brauenpunkte(einheiten)
        uv, p = uvs[idx], punkte[idx]
        abstand_uv, nachbar = cKDTree(uv).query(uv, k=2, workers=-1)
        d_uv = abstand_uv[:, 1]
        d_mm = np.linalg.norm(p - p[nachbar[:, 1]], axis=1) * 1000
        gueltig = d_uv > 1e-6
        return float(np.median(d_mm[gueltig] / d_uv[gueltig]))
