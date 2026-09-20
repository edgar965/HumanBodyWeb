# -*- coding: utf-8 -*-
"""Bildmodellmischung — aus den Schätzungen je Bild EINE Form: Betas, Kopf, Geschlecht.

Aus `Bildmodellschaetzung` herausgelöst (19.09.2026, die Datei stand bei 307
Zeilen). Mischung der Körperparameter: „Nur die Hauptbilder" (Vorgabe seit
20.09.2026, `Bildmodellhauptgewicht`: nur die in der zweiten Box markierten
Hauptbilder bauen den Körper), Median, gewichtetes Mittel (Gewicht × Zuversicht) oder das beste
Bild; der FLAME-Kopf des Kopf-Hauptbilds, sonst des größten Gesichts; das
Geschlecht aus den Betas
(`Morphzuordnung.geschlecht_schaetzen`), sonst aus dem Schulter-Hüft-
Verhältnis der Landmarken.
"""

import logging
import os

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')

__all__ = ['Bildmodellmischung']


class Bildmodellmischung:
    #: Schulter zu Hüfte (Bildbreite der Landmarken) — darüber „masculine".
    MASKULIN_AB = 1.25

    def __init__(self, optionen, job=None):
        self.optionen = optionen
        self.job = job

    def mischen(self, koerper, koepfe):
        art = self.optionen.get('mischung', 'haupt')
        reihen, gewichte, quellen, mit = [], [], [], []
        for b in koerper:
            s = b.get('schaetzung') or {}
            if s.get('betas'):
                reihen.append(np.asarray(s['betas'], dtype=float)[:10])
                gewichte.append(float(b.get('gewicht') or 0) * float(s.get('confidence') or 1.0))
                quellen.append(b['datei'])
                mit.append(b)
        betas = None
        hauptgewichte = None
        if reihen:
            m = np.array([np.pad(r, (0, 10 - len(r))) for r in reihen])
            w = np.array(gewichte)
            if art == 'bestes':
                betas = m[int(w.argmax())]
            elif art == 'mittel' and w.sum() > 0:
                betas = (m * w[:, None]).sum(0) / w.sum()
            elif art == 'median':
                betas = np.median(m, axis=0)
            else:
                # „Nur die Hauptbilder" (Vorgabe seit 20.09.2026): die markierten Hauptbilder
                # bauen den Körper, die übrigen Bilder wiegen 0 (`Bildmodellhauptgewicht`).
                art = 'haupt'
                from .bildmodellhauptgewicht import Bildmodellhauptgewicht

                hg = Bildmodellhauptgewicht(self.job) if self.job is not None else None
                hauptgewichte = hg.gewichte(mit) if hg else None
                betas = hg.mittel(mit, m) if hg else np.median(m, axis=0)
        kopf = self._kopf(koepfe + koerper)
        return {
            'betas': [round(float(v), 5) for v in betas] if betas is not None else None,
            'bilder': quellen,
            'gewichte': {k: round(float(v), 3) for k, v in hauptgewichte.items()} if hauptgewichte else None,
            'mischung': art,
            'anzahl': len(reihen),
            'kopf': kopf,
            'geschlecht': self.geschlecht(betas, koerper),
        }

    def _flame(self, b):
        """Die FLAME-Datei des Bildes: der abgelegte Pfad — oder, wenn der Eintrag ihn verloren hat,
        `<stamm>_gesicht_flame.npy` in der Ablage (Damira: 12 Dateien da, 3 Einträge mit Pfad)."""
        if not b:
            return None
        p = (b.get('gesichtsschaetzung') or {}).get('flame_vertices_path') or (
            b.get('schaetzung') or {}
        ).get('flame_vertices_path')
        if p or self.job is None or not b.get('datei'):
            return p
        from ..daten.bildmodellablage import Bildmodellablage

        name = os.path.splitext(b['datei'])[0] + '_gesicht_flame.npy'
        return name if (Bildmodellablage(self.job.kennung).schaetzung() / name).is_file() else None

    def _kopf(self, bilder):
        """Der FLAME-Kopf: erst die Kopf-Hauptbilder (vorn, Seite, hinten — `Bildmodellhauptgewicht`),
        dann Körperbilder von vorn, dann das größte Gesicht — nie eine Rückansicht (Damira bekam
        den Kopf aus `09_cr1`, dem Rücken, 20.09.2026). Dateiname oder None."""
        from .bildmodellhauptgewicht import Bildmodellhauptgewicht

        if self.job is not None:
            hg = Bildmodellhauptgewicht(self.job)
            koepfe = hg.hauptbilder('kopf')
            for ansicht in hg.KOPFREIHE:
                for b in koepfe:
                    if b.get('ansicht') == ansicht and b in bilder and self._flame(b):
                        return self._flame(b)
        beste, groesse = None, 0.0
        for b in bilder:
            if b.get('ansicht') == 'hinten':
                continue
            p = self._flame(b)
            if not p:
                continue
            kasten = b.get('gesicht') or {}
            h = float(kasten.get('hoehe') or 0.1) * float(b.get('gewicht') or 0)
            if b.get('kategorie') == 'koerper' and b.get('ansicht') == 'vorne':
                h += 1.0  # das Körperbild von vorn vor jedem Ausschnitt ohne Kopf-Hauptbild
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
            # Erst Schulter-/Hüftbreite des SMPL-X-Körpers aus den Betas (`masse_aus_betas`, Schwellen
            # an den Grundkörpern gemessen): der Vergleich in `Morphzuordnung` wiegt die Höhe mit und
            # nannte die schlanke, große Damira „male" (GVHMR-Körper 1,76 m neutral).
            aus = self._geschlecht_aus_massen(betas)
            if aus:
                return aus
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

    #: Schulterbreite / Hüftbreite am SMPL-X-Maßband (`G9massband`): gemessen an den Grundkörpern
    #: SMPLX_MALE 1,08–1,14 (Betas 0, ±2 in b0 und b1), SMPLX_FEMALE 0,92–0,94; Damira (GVHMR,
    #: neutral) 0,94. Brust−Unterbrust und Hüfte/Taille trennen NICHT (male 0: 24,2 cm / 1,23,
    #: female 0: 19,0 / 1,31 — sie messen Schlankheit, nicht Geschlecht; 20.09.2026 nachgemessen).
    SCHULTER_HUEFTE_FEMININ, SCHULTER_HUEFTE_MASKULIN = 1.0, 1.05

    def _geschlecht_aus_massen(self, betas):
        """`feminine`/`masculine` aus Schulter-/Hüftbreite des neutralen SMPL-X-Körpers — None
        im Zwischenbereich (dann entscheidet der Vergleich mit den Grundkörpern)."""
        try:
            from .bildmodellmassband import Bildmodellmassband

            m = Bildmodellmassband.masse_aus_betas(betas)
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Geschlecht aus Maßen nicht schätzbar: %s', fehler)
            return None
        if not m or not m.get('schulter_breite') or not m.get('huefte_breite'):
            return None
        verhaeltnis = m['schulter_breite'] / m['huefte_breite']
        logger.info('Geschlecht aus Maßen: Schulter/Hüftbreite %.3f (%.1f / %.1f cm)',
                    verhaeltnis, m['schulter_breite'], m['huefte_breite'])
        if verhaeltnis < self.SCHULTER_HUEFTE_FEMININ:
            return 'feminine'
        if verhaeltnis > self.SCHULTER_HUEFTE_MASKULIN:
            return 'masculine'
        return None
