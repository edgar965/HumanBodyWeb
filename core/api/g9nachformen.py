# -*- coding: utf-8 -*-
u"""G9nachformenapi — der genaue Zug eines Reglers in EINER Antwort: Körper, Anhänge und die Stücke, die er berührt (25.11.2026, Edgar: „alle regler unter 0,2 s“).

    POST /api/character/genesis9-figur/<name>/nachformen/
         {rumpf: Rumpf wie bei `…/netz/` (null: ohne Körper), stuecke: [{kennung, rumpf: Rumpf wie bei `…/garderobe/<kennung>/netz/`}]}
         -> {koerper: Antwort wie `…/netz/` | null, stuecke: {kennung: Antwort wie `…/garderobe/<kennung>/netz/` | null}}

Ohne Dreiecke, UV und Dünne (`nur: 'form'`): der Browser schreibt sie in die stehenden Netze (`gemeinsam/genesis9nachformen.js`). Bis dahin waren es fünf Anfragen nebeneinander, die sich
einen Interpreter teilten (0,5–0,76 s je Anfrage im Server, 0,46 s die Rechnung): hier rechnet EIN Faden alles nacheinander, und alles kommt in EINER Kopie von der Karte.

Ein Stück, das die Mischungen betrifft („Haar – Generisch“, „Kleidung – Generisch“) oder nicht rechenbar ist, kommt als null — der Browser holt es wie bisher für sich. Nichts wird
abgelegt. Eigener Faden (`thread_sensitive=False`): synchrone Ansichten teilen sich einen.
"""
import logging

from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.garderobe import G9garderobe
from Genesis9.haargenerisch import G9haargenerisch
from Genesis9.kleidgenerisch import G9kleidgenerisch
from Genesis9.pfade import G9pfade

from ..daten.netzausgabe import Netzausgabe
from ..dienste.g9anatomiedrapierung import G9anatomiedrapierung
from ..dienste.g9pruefbau import G9pruefbau
from .g9figur import FEHLT, G9figur
from .g9garderobe import G9garderobeapi

logger = logging.getLogger('core')

__all__ = ['G9nachformenapi']


class G9nachformenapi:
    u"""`netz` — Endpunkt; `rechnen` — die Rechnung, ohne Anfrage prüfbar."""

    #: Mehr getragene Stücke rechnet niemand (wie `G9lagenanfrage.HOECHSTENS`).
    HOECHSTENS = 24
    #: Was die Stellung bestimmt — für alle Stücke dieselben Objekte wie für den Körper.
    STELLUNG = ('regler', 'pose', 'ausdruck', 'griffe', 'drehung')

    @staticmethod
    @csrf_exempt
    @require_POST
    async def netz(request, name):
        return await sync_to_async(G9nachformenapi._antwort, thread_sensitive=False)(request, name)

    @staticmethod
    def _antwort(request, name):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        eintrag = G9figur._eintrag(name)
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekannte Genesis-9-Figur'}, status=404)
        auftrag = G9figur._rumpf(request)
        rumpf, stuecke = auftrag.get('rumpf'), auftrag.get('stuecke')
        if rumpf is not None and not isinstance(rumpf, dict):
            return JsonResponse({'fehler': u'rumpf fehlt'}, status=400)
        aus = G9pruefbau.bauen(lambda: G9nachformenapi.rechnen(name, eintrag, rumpf, stuecke), kurz=Netzausgabe.will_binaer(request) == Netzausgabe.KURZ)
        return aus if isinstance(aus, HttpResponse) else Netzausgabe.antwort(aus, request)

    @classmethod
    def rechnen(cls, name, eintrag, rumpf, stuecke):
        koerper = None
        if rumpf is not None:
            koerper = G9figur._koerper(name, eintrag, dict(rumpf, nur='form'))
            if isinstance(koerper, HttpResponse):
                return koerper
        aus = {}
        for s in [s for s in (stuecke or []) if isinstance(s, dict) and isinstance(s.get('rumpf'), dict)][:cls.HOECHSTENS]:
            kennung = G9figur._name(s.get('kennung'))
            if kennung:
                aus[kennung] = cls._stueck(kennung, dict(s['rumpf'], nur='form', **{k: rumpf[k] for k in cls.STELLUNG if rumpf is not None and k in rumpf}))
        return {'koerper': koerper, 'stuecke': aus}

    @staticmethod
    def _stueck(kennung, rumpf):
        if G9haargenerisch.ist_generisch(kennung) or G9kleidgenerisch.ist_generisch(kennung):
            return None
        try:
            if rumpf.get('getragen'):
                rumpf = dict(rumpf, getragen=G9kleidgenerisch.getragene_aufloesen(rumpf.get('getragen')))
            antwort = G9garderobeapi._kleid(kennung, G9garderobe.eintrag(kennung) or {}, G9anatomiedrapierung.ohne_anatomie(rumpf))
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Genesis 9: Stück %s nicht nachformbar: %s', kennung, fehler)
            return None
        return None if isinstance(antwort, HttpResponse) else antwort
