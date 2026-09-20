# -*- coding: utf-8 -*-
"""Bildmodellkopfanpassung — zweite Stufe der Anpassung: die Gesichtsregler auf den FLAME-Kopf.

Edgar (20.09.2026): „ich habe die Gesichtsregler nun bei DAZ installiert, importiere und
passe den Workflow an." Installiert ist „200 Plus Genesis 9 Edition" (DogZ & Zev0, SKU
91632): 301 Kanäle, 289 davon im Reglerplan (284 Kopf, 5 Hals), 270 mit Deltas, 152 mit
Formeln, 27 Charakterköpfe — gemessen mit `ProjektTemp/_wegwerf/mess_200plus.py`. Der
Satz `charaktere` hätte damit 448 statt 159 Variablen; deshalb zwei Stufen:

    Körper  `Bildmodellanpassung.anpassen`: Reglersatz ohne die Bereiche Kopf und Mimik
            (`teil='koerper'`), alle Punkte, Gelenke — wie bisher.
    Kopf    hier: die Kopfregler des Satzes (`teil='kopf'`: Charakterköpfe, Brauen,
            Wangen, Nase, Mund, Kinn, Ohren, Head Size), nur die Kopfpunkte des Käfigs
            (`G9koerperteile.genesis_punkte` == kopf), das Körperergebnis als Grund
            (`G9reglerableitung.mit_grund`), ohne Gelenke. Das Ziel ist derselbe
            `ziel.npz` — im Kopf steckt der FLAME-Kopf des Kopf-Hauptbilds
            (`G9zielnetz.aus(betas, kopf)`).

Ergebnis: das Gesamtergebnis (`ergebnis`, Regler Körper + Kopf, Rest über alle Punkte,
RMS über alle gewichteten Punkte) und die Kopfzahlen (`variablen`, `regler`, `verlauf`,
`rms_mm`, `aktiv`) — alles gemessen. Option `kopffit: aus` lässt die Stufe weg.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Bildmodellkopfanpassung']


class Bildmodellkopfanpassung:
    TEIL = 'kopf'

    def __init__(self, job, optionen):
        self.job = job
        self.optionen = optionen

    def anpassen(self, satz, grund, koerper, punkte, gewicht, fest, melder=None):
        """Kopfstufe nach der Körperstufe `koerper` (Ergebnis von `G9formanpassung`).

        Gibt `{ergebnis, variablen, regler, verlauf, rms_mm, aktiv}` — oder None, wenn der
        Satz keine Kopfregler hat oder das Ziel keine gewichteten Kopfpunkte.
        """
        from Genesis9.formanpassung import G9formanpassung
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.reglerableitung import G9reglerableitung

        from .bildmodelloptionen import Bildmodelloptionen

        if melder:
            melder(0.7, 'Reglerableitung Kopf')
        ableitung = G9reglerableitung.holen(satz, grund, teil=self.TEIL)
        if not ableitung.namen:
            logger.info('Kopf-Fit: der Satz %s hat keine Kopfregler', satz)
            return None
        teil = G9koerperteile.genesis_punkte(G9haut.holen())
        kopfgewicht = np.where(teil == G9koerperteile.NUMMER[self.TEIL], np.asarray(gewicht, float), 0.0)
        if not (kopfgewicht > 0).any():
            logger.warning('Kopf-Fit: das Ziel hat keine gewichteten Kopfpunkte')
            return None
        # Der Körper ist gestellt: seine Regler (samt Grundfigur) werden der Grund der Kopfstufe.
        am_koerper = ableitung.mit_grund(koerper['regler'])
        fest_kopf = {k: v for k, v in (fest or {}).items() if k in am_koerper.namen}
        if melder:
            melder(0.72, 'Ausgleichung Kopf (%d Regler, %d Punkte)' % (
                len(am_koerper.namen), int((kopfgewicht > 0).sum())))
        anpassung = G9formanpassung(
            am_koerper,
            punkte,
            kopfgewicht,
            None,
            daempfung=Bildmodelloptionen.DAEMPFUNG.get(self.optionen.get('daempfung'), 0.02),
            fest=fest_kopf,
        )
        e = anpassung.anpassen(
            lambda d, n, z: (
                melder and melder(0.72 + 0.18 * d / n, 'Kopf %d/%d: %.2f mm' % (d, n, z['rms_mm']))
            )
        )
        return {
            'ergebnis': self._gesamt(koerper, e, np.asarray(gewicht, float)),
            'variablen': len(am_koerper.namen),
            'regler': {k: v for k, v in e['regler'].items()
                       if k not in koerper['regler'] or abs(koerper['regler'][k] - v) > 1e-6},
            'verlauf': e['verlauf'],
            'rms_mm': e['punkte_rms_mm'],
            'punkte': int((kopfgewicht > 0).sum()),
            'aktiv': sum(1 for v in e['x'] if abs(v) > 1e-6),
        }

    @staticmethod
    def _gesamt(koerper, kopf, gewicht):
        """Das Ergebnis beider Stufen in der Form von `G9formanpassung.anpassen`: Regler und
        Rest aus der Kopfstufe (sie enthält den Körper als Grund), RMS neu über alle
        gewichteten Punkte, Gelenke und Teile aus der Körperstufe, der Kopfteil aus der Kopfstufe."""
        rest = np.asarray(kopf['rest'], float)
        halten = gewicht > 0
        rms = np.sqrt(((rest[halten] ** 2).sum(1) * gewicht[halten]).sum() / gewicht[halten].sum())
        teile = dict(koerper['teile'])
        teile.update(kopf['teile'])
        return {
            'regler': kopf['regler'],
            'x': kopf['x'],
            'variablen': koerper['variablen'] + kopf['variablen'],
            'verlauf': koerper['verlauf'] + [dict(stufe='kopf', **v) for v in kopf['verlauf']],
            'teile': teile,
            'punkte_rms_mm': round(float(rms) * 1000.0, 2),
            'gelenke_mm': koerper['gelenke_mm'],
            'rest': rest,
            'punkte': kopf['punkte'],
        }
