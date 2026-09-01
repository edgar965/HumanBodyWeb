# -*- coding: utf-8 -*-
"""Netz punktweise bearbeiten: glaetten, nach aussen druecken.

Aus core/api/netz.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `doppelcode`): zwei freie
Funktionen, die beide dasselbe taten — das ganze Netz rechnen und danach nur
die AUSGEWAEHLTEN Punkte uebernehmen. Diese Uebernahme steht jetzt einmal in
`_nur_ausgewaehlte`.
"""

import base64

import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from humanbody_core.cloth import _laplacian_smooth

from ..daten.netzantwort import Netzantwort
from ..dienste.charakterdaten import Charakterdaten
from ..daten.anfragerumpf import Anfragerumpf
from humanbody_core.koerperabstand import Koerperabstand


class Netzbearbeitung:
    """Punktweise Aenderungen am Stoffnetz — immer nur auf der Auswahl."""

    #: Durchgaenge der Laplace-Glaettung, wenn nichts mitkommt.
    VORGABE_DURCHGAENGE = 3
    #: Staerke der Glaettung.
    VORGABE_STAERKE = 0.3
    #: Mindestabstand zur Haut in Metern.
    VORGABE_ABSTAND = 0.006

    # ------------------------------------------------------------ Hilfsmittel

    @staticmethod
    def _punkte(text):
        """base64-Float32 als (N, 3)-Feld in float64 — eine eigene Kopie."""
        roh = np.frombuffer(base64.b64decode(text), dtype=np.float32).copy()
        return roh.reshape(-1, 3).astype(np.float64)

    @staticmethod
    def _nur_ausgewaehlte(vorher, nachher, auswahl):
        """Gerechnet wird auf ALLEN Punkten, uebernommen nur die Auswahl.

        Das ist Absicht: Glaettung und Herausschieben brauchen die Nachbarn.
        Wer nur die Auswahl rechnete, bekaeme an ihrem Rand einen Absatz.
        """
        ergebnis = vorher.copy()
        for platz in set(auswahl):
            if 0 <= platz < len(ergebnis):
                ergebnis[platz] = nachher[platz]
        return JsonResponse({'vertices': Netzantwort.feld(
            ergebnis.astype(np.float32), 'vertices')})

    # ---------------------------------------------------------------- Aktionen

    @staticmethod
    @csrf_exempt
    @require_POST
    def glaetten(request):
        """Laplace-Glaettung auf den ausgewaehlten Punkten.

        POST (JSON): {vertices (base64 Float32), faces (base64 Uint32),
                      selected (Liste von int), iterations, factor}
        """
        rumpf, fehler = Anfragerumpf.lesen(request, 'Invalid JSON body')
        if fehler:
            return fehler
        punkte_roh = rumpf.get('vertices')
        flaechen_roh = rumpf.get('faces')
        if not punkte_roh or not flaechen_roh:
            return JsonResponse({'error': 'vertices and faces are required'},
                                status=400)
        punkte = Netzbearbeitung._punkte(punkte_roh)
        flaechen = np.frombuffer(base64.b64decode(flaechen_roh),
                                 dtype=np.uint32).reshape(-1, 3)
        geglaettet = _laplacian_smooth(
            punkte, flaechen,
            iterations=int(rumpf.get('iterations',
                                     Netzbearbeitung.VORGABE_DURCHGAENGE)),
            factor=float(rumpf.get('factor',
                                   Netzbearbeitung.VORGABE_STAERKE)))
        return Netzbearbeitung._nur_ausgewaehlte(punkte, geglaettet,
                                                 rumpf.get('selected', []))

    @staticmethod
    @csrf_exempt
    @require_POST
    def herausschieben(request):
        """Die ausgewaehlten Stoffpunkte aus dem Koerper schieben.

        POST (JSON): {vertices (base64 Float32), selected, min_dist}
        Abfrageparameter: body_type, morph_* fuer den Koerper.
        """
        rumpf, fehler = Anfragerumpf.lesen(request, 'Invalid JSON body')
        if fehler:
            return fehler
        punkte_roh = rumpf.get('vertices')
        if not punkte_roh:
            return JsonResponse({'error': 'vertices is required'}, status=400)
        stoff = Netzbearbeitung._punkte(punkte_roh)
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute body mesh'},
                                status=500)
        # Der unterteilte Koerper loest feiner auf — die Kollision trifft
        # dadurch auch schmale Stellen.
        punkte = np.asarray(koerper.vertices, dtype=np.float64)
        unterteiler = Charakterdaten.unterteiler(koerper.geschlecht)
        if unterteiler is not None:
            punkte = unterteiler.subdivide(punkte)
        geschoben = Koerperabstand.radial(
            stoff, punkte,
            mindestabstand=float(rumpf.get(
                'min_dist', Netzbearbeitung.VORGABE_ABSTAND)))
        return Netzbearbeitung._nur_ausgewaehlte(
            stoff, geschoben, rumpf.get('selected', []))
