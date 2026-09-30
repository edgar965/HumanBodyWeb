# -*- coding: utf-8 -*-
u"""Netzausgabe — eine Netzantwort ausliefern: binär, sonst JSON.

WARUM BEIDE WEGE BLEIBEN (30.09.2026)
=====================================
Die Netzdaten gehen seit heute als Binärpaket (`Netzpaket`). Der Browser fragt
danach mit einem `Accept`-Kopf; wer das nicht tut, bekommt weiter JSON mit
base64 (`Netzjson`).

Das ist kein halber Umstieg aus Vorsicht, sondern die einzige Art, ihn ohne
stillen Bruch zu machen: Die Netzantworten werden an rund zwanzig Stellen
gebaut und an ebenso vielen im Browser gelesen. Eine übersehene Lesestelle
bekäme sonst Binärdaten in einen `JSON.parse` — und was dabei herauskommt, ist
kein Netz und keine brauchbare Fehlermeldung. Mit der Aushandlung bekommt sie
weiterhin JSON und arbeitet, bis sie umgestellt ist.

Dass der Weg wirklich gegangen wird, prüft man nicht am Code, sondern am
Netzwerk-Reiter des Browsers: Was dort mit `application/x-humanbody-netz`
ankommt, ist binär; alles andere ist eine Stelle, die noch fehlt.
"""
from django.http import HttpResponse, JsonResponse

from .netzjson import Netzjson
from .netzpaket import Netzpaket

__all__ = ['Netzausgabe']


class Netzausgabe:
    u"""Entscheidet zwischen Binärpaket und JSON und baut die Antwort."""

    @staticmethod
    def will_binaer(request):
        u"""Nimmt der Aufrufer das Binärpaket?

        Kein `request` heißt: ein Aufruf aus dem Code (Vorausrechnen, Test) —
        dann JSON, damit niemand ungefragt ein Format bekommt, das er nicht
        liest.
        """
        if request is None:
            return False
        return Netzpaket.INHALTSTYP in request.headers.get('Accept', '')

    @classmethod
    def antwort(cls, daten, request=None, status=200):
        u"""Das Antwort-Wörterbuch als `HttpResponse`.

        Steht auch an Stellen richtig, die gar keine Netzfelder liefern (etwa
        eine Fehlermeldung): Ohne Träger im Wörterbuch ist das Binärpaket ein
        JSON-Kopf ohne Nutzlast, und ohne passenden `Accept`-Kopf kommt
        ohnehin JSON heraus.
        """
        if cls.will_binaer(request):
            return HttpResponse(Netzpaket.packen(daten), status=status,
                                content_type=Netzpaket.INHALTSTYP)
        return JsonResponse(daten, encoder=Netzjson, status=status)

    @classmethod
    def kodieren(cls, daten, binaer):
        u"""Nur die Bytes — für den Antwortvorrat, der sie ablegt.

        Er merkt sich die FERTIGE Antwort, also muss das Format mit in den
        Schlüssel (`G9antworten.schluessel`): Sonst bekäme der zweite Aufrufer
        das Paket des ersten in seinem Format vorgesetzt.
        """
        if binaer:
            return (Netzpaket.packen(daten), Netzpaket.INHALTSTYP)
        return (Netzjson.bytes(daten), 'application/json')
