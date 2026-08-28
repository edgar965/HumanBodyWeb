# -*- coding: utf-8 -*-
u"""Anfragerumpf — den JSON-Rumpf EINMAL lesen, nicht neunzehnmal.

BEFUND `doppelcode` (28.08.2026)
===============================
Diese vier Zeilen standen in neunzehn Endpunkten:

    try:
        rumpf = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

Sie waren schon auseinandergelaufen: fünfzehnmal ``'Invalid JSON'``, viermal
``'Invalid JSON body'``, zweimal ohne ``ValueError`` im ``except`` (dort wird
ein leerer Rumpf zu einem 500 statt zu einem 400), einmal mit
``AttributeError`` statt ``ValueError``, weil dort direkt ``.get()``
hinterhergerufen wurde. Dazu ein privater Helfer ``_rumpf`` in
``netzbearbeitung.py``, den niemand sonst finden konnte.

WARUM DIE MELDUNG EIN PARAMETER IST
===================================
Der Text geht an den Browser und steht dort in einer Meldung. Ihn hier
stillschweigend zu vereinheitlichen hiesse, vier Endpunkte anders antworten zu
lassen als bisher — eine Aenderung am Drahtformat, versteckt in einer
Aufraeumarbeit. Wer die Texte angleichen will, tut das sichtbar und einzeln.

WARUM (wert, antwort) UND NICHT EINE AUSNAHME
=============================================
Wie ``Fotoauftrag.mit_rumpf`` daneben: Der Aufrufer bekommt die FERTIGE
Antwort und gibt sie zurueck. Das liest sich an der Aufrufstelle wie vorher
und braucht keine eigene Ausnahmeklasse, die jeder Endpunkt fangen muesste.
"""

import json

from django.http import JsonResponse


class Anfragerumpf:
    """Der JSON-Rumpf einer Anfrage — oder die fertige 400-Antwort."""

    #: Die Meldung, die fuenfzehn der neunzehn Stellen benutzten.
    MELDUNG = 'Invalid JSON'

    @staticmethod
    def _fehler(meldung):
        return JsonResponse({'error': meldung or Anfragerumpf.MELDUNG},
                            status=400)

    @staticmethod
    def lesen(request, meldung=None):
        """Der geparste Rumpf.

        ``ValueError`` steht bewusst im ``except``: ``json.JSONDecodeError``
        erbt davon, aber ein LEERER Rumpf (``b''``) wirft je nach Weg das eine
        oder das andere. Zwei Endpunkte fingen nur den Decoder-Fehler und
        antworteten auf eine leere Anfrage mit 500.

        @returns (rumpf, antwort) — ist `antwort` gesetzt, gibt der Aufrufer
                 sie zurueck und hoert auf.
        """
        try:
            return json.loads(request.body), None
        except (json.JSONDecodeError, ValueError):
            return None, Anfragerumpf._fehler(meldung)

    @staticmethod
    def feld(request, name, vorgabe=None, meldung=None):
        """EIN Feld aus dem Rumpf — auch wenn der gar kein Objekt ist.

        ``json.loads('[1,2]').get('ids')`` wirft ``AttributeError``; genau
        deshalb stand in ``auftraege.py`` ein anderes ``except`` als ueberall
        sonst. Hier wird der Fall benannt statt gefangen: Ein Rumpf, der kein
        Objekt ist, ist eine falsche Anfrage — 400, nicht 500.
        """
        rumpf, antwort = Anfragerumpf.lesen(request, meldung)
        if antwort is not None:
            return None, antwort
        if not isinstance(rumpf, dict):
            return None, Anfragerumpf._fehler(meldung)
        return rumpf.get(name, vorgabe), None

    @staticmethod
    def name_und_daten(request, meldung=None):
        """Die Paarung ``name`` + ``data``, wie sie drei Endpunkte speichern.

        ``kleidungsvorlagen``, ``modelldateien`` und ``studio_projekt``
        schrieben dieselben acht Zeilen: Rumpf lesen, ``name`` strippen,
        ``data`` holen, beides auf „vorhanden" pruefen.

        @returns (name, daten, antwort)
        """
        rumpf, antwort = Anfragerumpf.lesen(request, meldung)
        if antwort is not None:
            return '', None, antwort
        if not isinstance(rumpf, dict):
            return '', None, Anfragerumpf._fehler(meldung)
        name = (rumpf.get('name') or '').strip()
        daten = rumpf.get('data')
        if not name or not daten:
            return '', None, JsonResponse(
                {'error': 'name and data required'}, status=400)
        return name, daten, None
