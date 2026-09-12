# -*- coding: utf-8 -*-
u"""UMA-Kleidung: was es je Rasse anzuziehen gibt.

    GET /api/character/uma-garderobe/?rasse=Human%20Female%203.0
        {rasse, vertraeglich, plaetze: [{platz, rezepte: [{name}]}], anzahl}
    GET /api/character/uma-garderobe/?figur=<name>.glb    Rasse aus dem Zettel

Die Rezepte kommen aus den Text-Assets des UMA-Projekts
(`UMA_Python.Garderobe`, einmal je Prozess gelesen); angezogen wird
in Unity (`core/dienste/umabauer.py`, Argument `-kleidung`). 06.09.2026.
"""
import threading

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from UMA_Python import Garderobe

from ..dienste.umabauer import Umabauer
from .umafigur import Umafigur

__all__ = ['Umakleidung']


class Umakleidung:
    u"""Lesende Endpunkte auf die Garderobe des UMA-Projekts."""

    _schloss = threading.Lock()
    _garderobe = None

    @classmethod
    def garderobe(cls):
        with cls._schloss:
            ordner = str(settings.UMA_UMA3_ORDNER)
            if cls._garderobe is None or cls._garderobe.ordner != ordner:
                cls._garderobe = Garderobe(settings.UMA_UMA3_ORDNER)
            return cls._garderobe

    @classmethod
    def vergessen(cls):
        with cls._schloss:
            cls._garderobe = None

    @staticmethod
    @require_GET
    def angebot(request):
        rasse = request.GET.get('rasse')
        figur = request.GET.get('figur')
        if figur and not rasse:
            pfad, antwort = Umafigur._pfad_oder_antwort(figur)
            if antwort:
                return antwort
            rasse = Umafigur._rasse_der_datei(pfad)
        if not rasse:
            return JsonResponse({'error': 'rasse oder figur angeben'}, status=400)
        # Eine Rasse ohne eigene Rezepte (ElfFemale30) trägt die Kleidung der
        # Rassen, die Unity als verträglich nennt (`rassen.json`, 06.09.2026).
        vertraeglich = (Umabauer.rassen_details() or {}).get(rasse, [])
        plaetze = Umakleidung.garderobe().fuer_rassen([rasse] + vertraeglich)
        return JsonResponse({
            'rasse': rasse,
            'vertraeglich': vertraeglich,
            'plaetze': plaetze,
            'anzahl': sum(len(p['rezepte']) for p in plaetze),
        })
