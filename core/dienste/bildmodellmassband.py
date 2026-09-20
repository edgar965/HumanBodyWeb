# -*- coding: utf-8 -*-
"""Bildmodellmassband — rund 40 Körpermaße: SMPL-X (GVHMR) / Zielnetz / Modell nebeneinander.

Edgar (20.09.2026): „Warum nutzt du nicht mehr Körpermaße?" — Konzept
`Docu/konzepte/2026-09-20_modell-aus-bildern-neues-konzept.md`, Schritt B.

EIN Maßband (`G9massband`) misst mit derselben Definition:
  smplx    je Bild mit GVHMR-Ergebnis und Häkchen „Verwenden" (`gvhmr_an`) den
           SMPL-X-Körper aus dessen Betas in RUHEHALTUNG (`Smplxkoerper.formen`,
           neutral — die Weltlage des Fotos wäre die Pose, in der Hocke ist die
           Taille kein Maß), skaliert auf `person.groesse_cm`, wenn angegeben;
           dazu der Median über die verwendeten Bilder und die Werte je Bild
  ziel     der Genesis-Zielkäfig (`ziel.npz`, ggf. proportionsgeformt)
  modell   der Genesis-Käfig der Reglerstellung (mit Restmorph)
Ergebnis `ergebnis.massband = {katalog, smplx, smplx_je_bild, ziel, modell,
hoehe_cm}`; Werte in cm. Läuft im Schritt „vorschau" nach `Bildmodellmasse`.
"""

import logging

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')

__all__ = ['Bildmodellmassband']


class Bildmodellmassband:
    def __init__(self, job, stellung, ziel_laden=None):
        self.job = job
        self.stellung = stellung
        self.ziel_laden = ziel_laden

    def hoehe_cm(self):
        p = (self.job.optionen or {}).get('person') or {}
        try:
            h = float(p.get('groesse_cm') or 0)
        except (TypeError, ValueError):
            h = 0.0
        return h if h > 0 else None

    # ------------------------------------------------------------ SMPL-X

    @staticmethod
    def verwendet(b):
        """Zählt das GVHMR-Ergebnis des Bildes? Häkchen `gvhmr_an` entscheidet; ohne Häkchen nur
        Körper-Hauptbilder — GVHMR auf einem Kopf- oder Handausschnitt schätzt einen Körper, den
        es nicht sieht (die ersten acht Damira-Ergebnisse mischten 3 Köpfe hinein, 20.09.2026)."""
        g = b.get('gvhmr') or {}
        if b.get('video') or not (g.get('netz') and g.get('betas')):
            return False
        if b.get('gvhmr_an') is not None:
            return bool(b['gvhmr_an'])
        return b.get('kategorie') == 'koerper'

    @staticmethod
    def masse_aus_betas(betas, hoehe_cm=None):
        """Das Maßband am neutralen SMPL-X-Körper dieser Betas (Ruhehaltung, Füße auf 0, auf
        `hoehe_cm` skaliert, wenn gegeben) — `{schluessel: cm}`; auch für die Geschlechtsschätzung."""
        from Genesis9.massband import G9massband
        from SMPL.xkoerper import Smplxkoerper
        with Wrapperpfad():
            from baum import Baum

            koerper = Smplxkoerper.laden('neutral', Baum.SMPLX)
        v = koerper.formen(betas)
        v = v - np.array([0.0, float(v[:, 1].min()), 0.0])
        if hoehe_cm:
            v = v * (hoehe_cm / 100.0 / max(1e-6, float(v[:, 1].max())))
        return G9massband.smplx(v, koerper.weights, koerper.J_regressor @ v).messen()

    def smplx(self):
        """`(median, je_bild)` über die verwendeten GVHMR-Ergebnisse — oder `(None, {})`."""
        from Genesis9.massband import G9massband
        from SMPL.xkoerper import Smplxkoerper

        bilder = [b for b in self.job.bilder if self.verwendet(b)]
        if not bilder:
            return None, {}
        with Wrapperpfad():
            from baum import Baum

            koerper = Smplxkoerper.laden('neutral', Baum.SMPLX)
        hoehe = self.hoehe_cm()
        je_bild = {}
        for b in bilder:
            v = koerper.formen(b['gvhmr']['betas'])
            v = v - np.array([0.0, float(v[:, 1].min()), 0.0])
            if hoehe:
                v = v * (hoehe / 100.0 / max(1e-6, float(v[:, 1].max())))
            gelenke = koerper.J_regressor @ v
            je_bild[b['datei']] = G9massband.smplx(v, koerper.weights, gelenke).messen()
        # Gewichtet wie die Mischung: nur die Hauptbilder zählen (`Bildmodellhauptgewicht`).
        from .bildmodellhauptgewicht import Bildmodellhauptgewicht

        gewichte = Bildmodellhauptgewicht(self.job).gewichte(bilder)
        median = {}
        for k in G9massband.SCHLUESSEL:
            paare = [(gewichte.get(b['datei'], 0.0), je_bild[b['datei']][k])
                     for b in bilder if k in je_bild.get(b['datei'], {})]
            if paare:
                w = sum(g for g, _ in paare)
                median[k] = round(float(sum(g * v for g, v in paare) / w) if w > 0
                                  else float(np.median([v for _, v in paare])), 2)
        median['bilder'] = len(je_bild)
        return median, je_bild

    # ------------------------------------------------------------ Genesis

    def ziel(self):
        from Genesis9.haut import G9haut
        from Genesis9.massband import G9massband

        if self.ziel_laden is None:
            return None
        p, _, gelenke = self.ziel_laden()
        namen = list(gelenke.keys())
        g = np.array([gelenke[n] for n in namen], float)
        return G9massband.genesis(p, G9haut.holen(), g, namen).messen()

    def modell(self):
        from Genesis9.formung import G9formung
        from Genesis9.haut import G9haut
        from Genesis9.massband import G9massband
        from Genesis9.reglerableitung import G9reglerableitung

        if not self.stellung:
            return None
        p, g, namen = G9reglerableitung.lage(G9formung(self.stellung))
        return G9massband.genesis(p, G9haut.holen(), g, namen).messen()

    # ------------------------------------------------------------ Alles

    def alle(self):
        """`{katalog, smplx, smplx_je_bild, ziel, modell, hoehe_cm}` — None, wo nichts messbar ist."""
        from Genesis9.massband import G9massband

        aus = {'katalog': [{'schluessel': k, 'name': n, 'gruppe': g} for k, n, g in G9massband.KATALOG],
               'hoehe_cm': self.hoehe_cm(), 'smplx': None, 'smplx_je_bild': {}, 'ziel': None, 'modell': None}
        try:
            aus['smplx'], aus['smplx_je_bild'] = self.smplx()
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Bildmodell %s: Maßband SMPL-X nicht messbar: %s', self.job.kennung, fehler)
        for name, fn in (('ziel', self.ziel), ('modell', self.modell)):
            try:
                aus[name] = fn()
            except Exception as fehler:  # noqa: BLE001
                logger.warning('Bildmodell %s: Maßband %s nicht messbar: %s', self.job.kennung, name, fehler)
        return aus
