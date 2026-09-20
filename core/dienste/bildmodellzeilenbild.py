# -*- coding: utf-8 -*-
"""Bildmodellzeilenbild — Knopf „Bild neu" je Tabellenzeile: nur die Bilder dieser Ansicht.

Edgar (20.09.2026): „wenn ich in den Zeilen auf Bild neu klicke, soll nicht das
gesamte 3D-Modell gerechnet werden, sondern eine schnelle Bildberechnung der
einzelnen Zeile." Also KEIN Lauf — keine Reglerableitung, kein Restmorph, kein
Speichern: das rohe Zielnetz bekommt den Umriss und die aktuellen Proportionen
(wie zu Beginn der Anpassung; schreibt `ziel_prop.npz`), dann werden Vorher-
(Ziel) und Nachher-Bild (das Modell aus dem gespeicherten Ergebnis) NUR dieser
Ansicht gerendert und gemessen (`Bildmodellproportionen.alle(nur=…)`); die
anderen Ansichten bleiben stehen. Synchron in der Anfrage, Sekunden. Das Modell
selbst ändert sich dabei nicht — dafür „Übernehmen und neu berechnen".

POST `api/bildmodell/<id>/zeilenbild/<ansicht>/` mit `{proportionen: {schluessel: cm}}`
(die aktuellen Popup-Werte, optional) → `{ok, ansicht, eintrag, formung}`.
"""

import logging

from .bildmodellanpassung import Bildmodellanpassung
from .bildmodelloptionen import Bildmodelloptionen
from .bildmodellproportionen import Bildmodellproportionen
from .bildmodellumriss import Bildmodellumriss
from .bildmodellzielproportionen import Bildmodellzielproportionen

logger = logging.getLogger('core')

__all__ = ['Bildmodellzeilenbild']


class Bildmodellzeilenbild:
    ANSICHTEN = Bildmodellproportionen.ANSICHTEN

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def rechnen(self, ansicht, proportionen=None):
        """Zielnetz formen, Bilder dieser Ansicht rendern — `(eintrag, formung)`."""
        if ansicht not in self.ANSICHTEN:
            raise ValueError('Unbekannte Ansicht: %s' % ansicht)
        if proportionen is not None:
            optionen = dict(self.job.optionen or {})
            optionen['proportionen'] = Bildmodelloptionen.proportionen_pruefen(proportionen)
            self.job.optionen = optionen
            self.job.save(update_fields=['optionen', 'updated_at'])  # bleibt auch, wenn das Formen scheitert
        anpassung = Bildmodellanpassung(self.job, self.ablage, Bildmodelloptionen.pruefen(self.job.optionen))
        punkte, gewicht, gelenke = anpassung._ziel_laden(roh=True)
        punkte, gelenke, umriss = Bildmodellumriss(self.job, anpassung.optionen).formen(punkte, gelenke)
        punkte, gelenke, formung = Bildmodellzielproportionen(
            self.job, self.ablage, anpassung.optionen
        ).formen(punkte, gewicht, gelenke, vorgeformt=umriss is not None)
        bericht = dict(self.job.ergebnis.get('anpassung') or {})
        bericht['proportionen'] = formung
        if umriss is not None:
            bericht['umriss'] = umriss
        self.job.ergebnis['anpassung'] = bericht
        alle = Bildmodellproportionen(
            self.job, self.ablage, anpassung.stellung(), anpassung._ziel_laden
        ).alle(nur=ansicht)
        self.job.ergebnis['proportionen'] = alle
        self.job.save(update_fields=['optionen', 'ergebnis', 'updated_at'])
        logger.info('Bildmodell %s: Zeilenbild %s neu (Formung %s)', self.job.kennung, ansicht, formung)
        return alle['ansichten'].get(ansicht), formung
