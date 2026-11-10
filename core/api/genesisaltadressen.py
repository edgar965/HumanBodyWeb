"""Genesisaltadressen — die alten Adressen von „Mesh3D-AI“ und „2d-3d-AI“ leiten auf Mesh-Genesis und Foto-Genesis weiter (09.11.2026, Edgar: „Benenne die um in foto-genesis und
mesh-genesis, alle klassen, alle Seiten, alle links“, zu „Alte Adressen weiterleiten?“: „Ja“; Konzept `Docu/konzepte/2026-11-09_foto-genesis-mesh-genesis.md`).

Seiten mit 301. Die API mit 308: Er behält Methode und Körper, aus einem 301 macht der Browser bei POST einen GET. Die Weiterleitung selbst braucht kein CSRF-Zeichen, die Zieladresse
prüft es. Die Abfrage (`?…`) geht mit. Diese Datei steht in `Docu/umbau/genesis_umbenennung.py` unter `NIE`, sonst schriebe ein weiterer Lauf die alten Anfänge um.
"""
from django.http import HttpResponsePermanentRedirect
from django.http.response import HttpResponseRedirectBase
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

__all__ = ['Genesisaltadressen']


class Weiterleitung308(HttpResponseRedirectBase):
    status_code = 308


class Genesisaltadressen:
    #: (alter Anfang, neuer Anfang, Antwort)
    PRAEFIXE = (
        ('mesh-3D-AI/', 'mesh-genesis/', HttpResponsePermanentRedirect),
        ('2d-3d-AI/', 'foto-genesis/', HttpResponsePermanentRedirect),
        ('hilfe/architektur/mesh3dai/', 'hilfe/architektur/mesh-genesis/', HttpResponsePermanentRedirect),
        ('hilfe/architektur/2d-3d-ai/', 'hilfe/architektur/foto-genesis/', HttpResponsePermanentRedirect),
        ('settings/mesh3dai/', 'settings/mesh-genesis/', HttpResponsePermanentRedirect),
        ('settings/2d-3d-ai/', 'settings/foto-genesis/', HttpResponsePermanentRedirect),
        ('api/mesh3dai/', 'api/meshgenesis/', Weiterleitung308),
        ('api/2d3dai/', 'api/fotogenesis/', Weiterleitung308),
    )

    @staticmethod
    def _sicht(neu, antwort):
        @csrf_exempt
        def sicht(request, rest=''):
            ziel = '/' + neu + rest
            if request.META.get('QUERY_STRING'):
                ziel += '?' + request.META['QUERY_STRING']
            return antwort(ziel)
        return sicht

    @classmethod
    def muster(cls):
        aus = []
        for alt, neu, antwort in cls.PRAEFIXE:
            sicht = cls._sicht(neu, antwort)
            aus += [path(alt, sicht), path(alt + '<path:rest>', sicht)]
        return aus
