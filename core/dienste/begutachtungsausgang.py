# -*- coding: utf-8 -*-
"""Begutachtungsausgang — „Iteration 0": die Vorlage und das Modell, BEVOR die erste Iteration etwas ändert (05.10.2026).

Edgar: „baue mir eine Iteration 0 ein, wo du die Vorlage und das Modell machst VOR der Iteration 1." Bis dahin gab es vor Iteration 1 kein Bild des Modells in den Blickwinkeln der Fotos:
Die erste Runde war schon eine Änderung (das Startrezept samt Rezept der KI), und wer wissen wollte, wo das Modell VOR der Iteration steht — der Berater, die Note, Edgar —, hatte nur die Bühne.

Iteration 0 ist eine ganz normale Runde der Begutachtung (`Begutachtungsrunde._runde`: bauen, rendern aus den Blickwinkeln der Fotos, benoten, messen, Tafel und Kopfbild ablegen) mit der Nummer 0 und dem
Rezept `Standvorabkleider.rezept` — die Figur, die der Stand vor den Iterationen zeigt: Haltung der Fotos, Stücke aus dem Netz, Frisur, Farben. Sie zählt nicht als Iteration (die Anzahl der Iterationen der
Nachbesserung zählt ab 1), ist aber die erste „beste Runde": Iteration 1 muss sie schlagen (`Rundenauswahl`), sonst bleibt das Modell, wie es in Iteration 0 war.

Wann sie läuft:
  * auf Bestellung (`POST …/begutachtung/ {ausgang: true}`, Knopf „Iteration 0 rechnen", die Nachbesserung vor ihrer ersten Iteration);
  * von selbst, wenn die ERSTE Runde eines Auftrags bestellt wird, der noch keine Runde hat (`fehlt`): dann rechnet der Lauf erst Iteration 0 und danach die bestellte Runde auf deren Modell.
Hat der Auftrag schon Runden (Aufträge von vor diesem Datum), rechnet eine Bestellung Iteration 0 NACHTRÄGLICH (`nachtraeglich`): Der Stand der Iterationen (bestes Modell, Verlauf, Auswahl) bleibt, wie er war — Iteration 0 ist
dann nur ein Bild und eine Note der Ausgangslage, ersetzt eine frühere Iteration 0 und ändert keine Auswahl.
"""

import copy

__all__ = ['Begutachtungsausgang']


class Begutachtungsausgang:
    RUNDE = 0
    KOMMENTAR = 'Iteration 0: Vorlage und Modell — die Ausgangslage vor der ersten Iteration (Startrezept: Haltung der Fotos, Stücke aus dem Netz, Frisur, Farben)'

    @staticmethod
    def verlangt(naechste):
        """True, wenn die Bestellung Iteration 0 meint (`naechste.ausgang`)."""
        return bool((naechste or {}).get('ausgang'))

    @classmethod
    def eintrag(cls, job):
        """Der Eintrag von Iteration 0 in `ergebnis.iterationen` — None, wenn es keinen gibt."""
        return next((e for e in (job.ergebnis or {}).get('iterationen') or [] if int(e.get('runde') or 0) == cls.RUNDE and e.get('art') == 'ausgang'), None)

    @classmethod
    def fehlt(cls, job):
        """True, wenn der Auftrag noch KEINE Runde hat — weder eine gerechnete noch ein gemerktes Modell: dann gehört Iteration 0 vor die bestellte Runde."""
        ergebnis = job.ergebnis or {}
        kreislauf = ergebnis.get('kreislauf') or {}
        return not (ergebnis.get('iterationen') or []) and not (kreislauf.get('weiter') or {}).get('modell') and not kreislauf.get('modell')

    #: Weite der Kleidung in Iteration 0 (cm, `passform`): negativ = enger an der Haut — gemessen: bei −1,5 cm lag der Bauch des Hemds auf der Silhouette des Seitenfotos, ab −3 cm ändert sich nichts mehr (`G9passform`: nie näher als 3 mm).
    WEITE_CM = -3.0

    @classmethod
    def rezept(cls, job):
        """Das Rezept von Iteration 0 als Text: das Startrezept (`Standvorabkleider.rezept`), dazu bei der Option `iterationen.rumpftiefe` die Tiefe des Rumpfs nach der Seitenansicht (`koerper_rumpftiefe`) und enger
        anliegende Kleidung (`passform`). Edgar, 05.10.2026, „Bauch ist bei dir sehr dick" — gemessen im Modell der Iteration 0 gegen die Silhouette des Seitenfotos: der Körper 20–45 mm zu flach, das Hemd am Unterbauch
        bis 41 mm zu tief. Leer ohne Fotostücke (dann trägt Iteration 0 die Frisur aus „Mesh to 3D" und keine Kleider, `_start`)."""
        from .iterationsoptionen import Iterationsoptionen
        from .standvorabkleider import Standvorabkleider
        zeilen = list(Standvorabkleider.rezept(job))
        if zeilen and Iterationsoptionen.rumpftiefe(job):
            zeilen += ['m.koerper_rumpftiefe()', 'm.passform(weite_cm=%s)' % cls.WEITE_CM]
        if zeilen and Iterationsoptionen.gesichtsprofil(job):
            zeilen.append('m.koerper_gesichtsprofil()')
        return '\n'.join(zeilen) + ('\n' if zeilen else '')

    @classmethod
    def bestellung(cls, job):
        """`naechste` einer Runde für Iteration 0."""
        return {'aufrufe': cls.rezept(job), 'automatisch': False, 'runden': 1, 'kommentar': cls.KOMMENTAR, 'ausgang': True}

    @classmethod
    def vorher(cls, job):
        """Der Stand der Iterationen VOR einer nachträglichen Iteration 0 — `nachher` stellt ihn wieder her."""
        ergebnis = job.ergebnis or {}
        return copy.deepcopy((ergebnis.get('kreislauf'), ergebnis.get('begutachtung')))

    @classmethod
    def nachher(cls, job, vorher):
        """Nach einer nachträglichen Iteration 0: Kreislauf (bestes Modell, Verlauf, Auswahl) und Begutachtung wie vorher; eine frühere Iteration 0 ist ersetzt (der neue Eintrag steht hinten, die Liste wird
        nach Runde geordnet)."""
        kreislauf, begutachtung = vorher
        ergebnis = job.ergebnis
        eintraege = ergebnis.get('iterationen') or []
        neu = eintraege[-1]
        rest = [e for e in eintraege[:-1] if not (int(e.get('runde') or 0) == cls.RUNDE and e.get('art') == 'ausgang')]
        ergebnis['iterationen'] = sorted(rest + [neu], key=lambda e: int(e.get('runde') or 0))
        if kreislauf is not None:
            ergebnis['kreislauf'] = kreislauf
        if begutachtung is not None:
            ergebnis['begutachtung'] = dict(begutachtung, zustand='wartet')
