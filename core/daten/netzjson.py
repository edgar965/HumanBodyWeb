# -*- coding: utf-8 -*-
u"""Netzjson — der JSON-Weg für Antworten mit `Netzfeld`ern.

Seit dem 30.09.2026 tragen Netzantworten ihre Zahlenfelder als `Netzfeld`
(rohe Bytes plus Typ) statt als base64-String. Wer sie als JSON ausliefert,
braucht deshalb diesen Kodierer — er macht aus jedem Träger wieder das base64,
das der Browser seit jeher liest.

Ohne ihn wirft `json.dumps` ein `TypeError: Object of type Netzfeld is not JSON
serializable`. Das ist Absicht: Eine vergessene Auslieferstelle fällt beim
ersten Aufruf laut auf, statt eine leere Antwort zu schicken.
"""
import json

from django.core.serializers.json import DjangoJSONEncoder

from .netzfeld import Netzfeld

__all__ = ['Netzjson']


class Netzjson(DjangoJSONEncoder):
    u"""`DjangoJSONEncoder`, der `Netzfeld` als base64 schreibt."""

    def default(self, o):
        if isinstance(o, Netzfeld):
            return o.base64()
        return super().default(o)

    @classmethod
    def bytes(cls, daten):
        u"""Das Wörterbuch als UTF-8-JSON — wie `JsonResponse` es schreibt."""
        return json.dumps(daten, cls=cls, separators=(',', ':')).encode('utf-8')
