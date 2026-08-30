# -*- coding: utf-8 -*-
u"""Die Vorgabewerte der SMPL-Seite — welche es gibt und was gilt.

WARUM EIGENE KLASSE (30.08.2026, Befund `code-qualitaet`):
``Smplendpunkte.einstellungen_sichern`` hatte dreizehn Verzweigungen, und jede
war dieselbe Bauart — Feld aus der Anfrage holen, prüfen, ins Modell schreiben.
Sieben Felder, sieben ``if``-Blöcke, jeder mit seiner eigenen Grenze irgendwo im
Rumpf.

WAS DIE PRÜFUNGEN VERHINDERN: Die Werte kommen aus dem Browser und gehen
ungefiltert in die Anzeige der nächsten Sitzung. Eine Deckkraft über 1 lässt den
Körper verschwinden, ein Versatz von 500 schiebt ihn aus dem Bild — beides ohne
Fehlermeldung, und die Seite sieht danach kaputt aus, ohne dass jemand die
Ursache in einem gespeicherten Wert vermutet.

ZWEI ARTEN VON FELDERN, und der Unterschied ist gewollt:

    Geschlecht und Drahtgitter  werden IMMER geschrieben. Beide haben einen
                                sinnvollen Rückfall („female", aus), und die
                                Seite meldet sie bei jedem Speichern.
    Alles Übrige                bleibt unverändert, wenn es nicht gemeldet wird.
                                Ein Rückfall würde hier einen Wert löschen, den
                                eine ältere Fassung der Seite gar nicht kennt.
"""
import json


class Smplvorgaben:
    u"""Was die SMPL-Seite speichern darf — als Tabelle statt als if-Kette."""

    #: Zulaessige Geschlechter des SMPL-Modells.
    GESCHLECHTER = ('female', 'male', 'neutral')
    #: So viele Formparameter fuehrt SMPL.
    BETAS = 10

    #: „Nicht gemeldet" — unterscheidbar von einem gemeldeten ``None``.
    FEHLT = object()

    @staticmethod
    def _geschlecht(wert):
        return wert if wert in Smplvorgaben.GESCHLECHTER else 'female'

    @staticmethod
    def _betas(wert):
        u"""Genau zehn Zahlen, sonst gar nichts.

        Eine kürzere Liste würde beim Lesen mit Nullen aufgefüllt — die
        fehlenden Formparameter wären still auf Standard zurückgesetzt.
        """
        if not isinstance(wert, list) or len(wert) != Smplvorgaben.BETAS:
            return None
        return ','.join('%.2f' % b for b in wert)

    @staticmethod
    def _anteil(wert):
        u"""0…1 — die Deckkraft."""
        return None if wert is None else max(0.0, min(1.0, float(wert)))

    @staticmethod
    def _versatz(wert):
        u"""±2 Meter. Weiter draußen ist der Körper aus dem Bild."""
        return None if wert is None else max(-2.0, min(2.0, float(wert)))

    @staticmethod
    def _farbe(wert):
        u"""Nur Hexfarben. Ein Farbname käme im CSS an und im Renderer nicht."""
        if not (wert and isinstance(wert, str) and wert.startswith('#')):
            return None
        return wert

    @staticmethod
    def _szene(wert):
        u"""Das Szenen-Wörterbuch als JSON-Text im Modellfeld."""
        return json.dumps(wert) if isinstance(wert, dict) and wert else None

    @staticmethod
    def _schalter(wert):
        return bool(wert)

    @classmethod
    def uebernehmen(cls, daten, einstellungen):
        u"""Die gemeldeten Werte ins Modell schreiben. Speichert NICHT.

        @param daten Wörterbuch aus der Anfrage
        @param einstellungen ``AppSettings``-Objekt
        @returns Namen der Felder, die geschrieben wurden
        """
        geschrieben = []
        for schluessel, feld, pruefung, wenn_fehlt in cls.FELDER:
            if schluessel in daten:
                roh = daten[schluessel]
            elif wenn_fehlt is cls.FEHLT:
                continue
            else:
                roh = wenn_fehlt
            wert = pruefung(roh)
            if wert is None:
                continue
            setattr(einstellungen, feld, wert)
            geschrieben.append(feld)
        return geschrieben


#: Die Feldtabelle. Steht NACH der Klasse, weil sie deren eigene Pruefungen
#: nennt — im Klassenrumpf waeren sie noch nicht gebunden.
#:
#: (Schluessel in der Anfrage, Feld am Modell, Pruefung, Wert wenn die Seite
#: nichts meldet). ``FEHLT`` heisst „dann nichts anfassen"; gibt die Pruefung
#: ``None`` zurueck, bleibt das Feld ebenfalls unveraendert.
Smplvorgaben.FELDER = (
    ('gender', 'smpl_default_gender', Smplvorgaben._geschlecht, 'female'),
    ('betas', 'smpl_default_betas', Smplvorgaben._betas, Smplvorgaben.FEHLT),
    ('opacity', 'smpl_default_opacity', Smplvorgaben._anteil, Smplvorgaben.FEHLT),
    ('color', 'smpl_default_color', Smplvorgaben._farbe, Smplvorgaben.FEHLT),
    ('wireframe', 'smpl_default_wireframe', Smplvorgaben._schalter, False),
    ('xoffset', 'smpl_default_xoffset', Smplvorgaben._versatz, Smplvorgaben.FEHLT),
    ('scene', 'smpl_default_scene', Smplvorgaben._szene, Smplvorgaben.FEHLT),
)
