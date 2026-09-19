# -*- coding: utf-8 -*-
"""Bildmodellmischung — aus den Schätzungen je Bild EINE Form: Betas, Kopf, Geschlecht.

Aus `Bildmodellschaetzung` herausgelöst (19.09.2026, die Datei stand bei 307
Zeilen). Mischung der Körperparameter: Median (Vorgabe), gewichtetes Mittel
(Gewicht × Zuversicht) oder das beste Bild; der FLAME-Kopf des Bildes mit
dem größten Gesicht; das Geschlecht aus den Betas
(`Morphzuordnung.geschlecht_schaetzen`), sonst aus dem Schulter-Hüft-
Verhältnis der Landmarken.
"""

import logging

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')

__all__ = ['Bildmodellmischung']


class Bildmodellmischung:
    #: Schulter zu Hüfte (Bildbreite der Landmarken) — darüber „masculine".
    MASKULIN_AB = 1.25

    def __init__(self, optionen):
        self.optionen = optionen

    def mischen(self, koerper, koepfe):
        art = self.optionen.get('mischung', 'median')
        reihen, gewichte, quellen = [], [], []
        for b in koerper:
            s = b.get('schaetzung') or {}
            if s.get('betas'):
                reihen.append(np.asarray(s['betas'], dtype=float)[:10])
                gewichte.append(float(b.get('gewicht') or 0) * float(s.get('confidence') or 1.0))
                quellen.append(b['datei'])
        betas = None
        if reihen:
            m = np.array([np.pad(r, (0, 10 - len(r))) for r in reihen])
            w = np.array(gewichte)
            if art == 'bestes':
                betas = m[int(w.argmax())]
            elif art == 'mittel' and w.sum() > 0:
                betas = (m * w[:, None]).sum(0) / w.sum()
            else:
                betas = np.median(m, axis=0)
        kopf = self._kopf(koepfe + koerper)
        return {
            'betas': [round(float(v), 5) for v in betas] if betas is not None else None,
            'bilder': quellen,
            'mischung': art,
            'anzahl': len(reihen),
            'kopf': kopf,
            'geschlecht': self.geschlecht(betas, koerper),
        }

    def _kopf(self, bilder):
        """Der FLAME-Kopf des Bildes mit dem größten Gesicht — Dateiname oder None."""
        beste, groesse = None, 0.0
        for b in bilder:
            p = (b.get('gesichtsschaetzung') or {}).get('flame_vertices_path') or (
                b.get('schaetzung') or {}
            ).get('flame_vertices_path')
            if not p:
                continue
            kasten = b.get('gesicht') or {}
            h = float(kasten.get('hoehe') or 0.1) * float(b.get('gewicht') or 0)
            if h > groesse:
                beste, groesse = p, h
        return beste

    def geschlecht(self, betas, koerper):
        """`feminine`/`masculine` — aus den SMPL-X-Parametern
        (`Morphzuordnung.geschlecht_schaetzen`: welchem Grundkörper die
        Gestalt näher liegt), sonst aus dem Schulter-Hüft-Verhältnis der
        Landmarken (über 1,25 masculine).

        Erst Landmarken allein: Damira (Frau) kam auf 1,3 — MediaPipes
        Hüftpunkte sind die Gelenke, nicht die Hüftbreite (19.09.2026).
        """
        if betas is not None:
            try:
                with Wrapperpfad():
                    from morphzuordnung import Morphzuordnung

                    return (
                        'masculine'
                        if Morphzuordnung.geschlecht_schaetzen([float(b) for b in betas]) == 'male'
                        else 'feminine'
                    )
            except Exception as fehler:  # noqa: BLE001
                logger.warning('Geschlecht aus Betas nicht schätzbar: %s', fehler)
        werte = []
        for b in koerper:
            lm = b.get('landmarken')
            if not lm or len(lm) < 29:
                continue
            schulter = abs(lm[11][0] - lm[12][0])
            huefte = abs(lm[23][0] - lm[24][0])
            if huefte > 1e-6 and b.get('ansicht') in ('vorne', 'hinten'):
                werte.append(schulter / huefte)
        if not werte:
            return 'feminine'
        return 'masculine' if float(np.median(werte)) > self.MASKULIN_AB else 'feminine'
