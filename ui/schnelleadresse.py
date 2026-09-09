# -*- coding: utf-8 -*-
u"""Die Seite kommt ueber 127.0.0.1, nicht ueber `localhost`.

DER BEFUND (Edgar, 09.09.2026: „http://localhost:8081/humanbody/scene/ baut
sich sehr langsam auf")
=====================================================================
Gemessen im laufenden Browser, dieselbe Seite, unmittelbar nacheinander:

    erster Aufruf ueber localhost      DOMContentLoaded  12.692 ms
    erster Aufruf ueber 127.0.0.1      DOMContentLoaded     408 ms
    warm, localhost / 127.0.0.1                4.371 / 2.718 ms

Die Ursache steht in `netstat`: Der Entwicklungsserver lauscht NUR auf
`127.0.0.1:8081`. `getaddrinfo('localhost')` liefert unter Windows
`['::1', '127.0.0.1']`, und der Versuch auf `[::1]` laeuft nicht in ein
schnelles „refused", sondern in einen Timeout — dreimal gemessen mit
2.085 / 2.078 / 2.050 ms, waehrend `127.0.0.1` in 10 bis 13 ms antwortet.
Die Szene-Seite holt 217 Module; jede neue Verbindung zahlt den Aufschlag,
bis Chrome sich die Sackgasse gemerkt hat.

Das ist dieselbe Falle, die in `~/.claude/rules/zeit-messen.md` steht — dort
kostete sie in einem anderen Projekt Monate an Ollama-Aufrufen.

WARUM EINE WEITERLEITUNG UND NICHT EIN ZWEITER LAUSCHER
=======================================================
`manage.py runserver` bindet genau EINE Adresse. Auf `[::]` umzustellen
loeste es nicht: Unter Windows ist `IPV6_V6ONLY` fuer einen frischen Socket
gesetzt, IPv4 waere dann tot. Zwei Serverprozesse waeren zwei Django-
Instanzen mit getrennten Zwischenspeichern — genau die Sorte stiller
Doppelzustand, die dieses Projekt schon mehrfach Zeit gekostet hat.

WAS SIE NICHT ANFASST
=====================
* Nur `GET`/`HEAD` und nur Anfragen, die HTML erwarten. Ein POST verloere
  beim Weiterleiten seinen Rumpf, und Modulanfragen einer noch offenen
  `localhost`-Seite umzuleiten braeche sie: Ein ES-Modul von einer anderen
  Herkunft laedt nur mit CORS-Kopf.
* Nur bei `DEBUG`. Im Betrieb entscheidet der Vorschaltserver ueber Namen.
* `302`, nicht `301`: Ein dauerhafter Umzug bliebe im Browser stehen, auch
  wenn der Server spaeter auf beiden Familien lauscht.

DIE NEBENWIRKUNG, DIE MAN WISSEN MUSS: `localStorage` und `sessionStorage`
haengen an der Herkunft. Wer bisher ueber `localhost` gearbeitet hat, findet
seine gemerkten Reitereinstellungen einmalig nicht wieder — sie liegen unter
der alten Herkunft. Ab dann ist es EINE Ablage statt zweier, die je nach
Tippweise auseinanderliefen.
"""
from django.conf import settings
from django.http import HttpResponseRedirect


class Schnelleadresse(object):

    #: Der Name, der ueber IPv6 in die Sackgasse laeuft.
    LANGSAM = 'localhost'
    #: Wohin stattdessen.
    SCHNELL = '127.0.0.1'
    #: Nur diese Methoden — ein POST verliert beim Weiterleiten den Rumpf.
    METHODEN = ('GET', 'HEAD')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ziel = self.ziel(request)
        if ziel:
            return HttpResponseRedirect(ziel)
        return self.get_response(request)

    def ziel(self, request):
        u"""Die Adresse, auf die weiterzuleiten ist — oder `None`."""
        if not settings.DEBUG:
            return None
        if request.method not in Schnelleadresse.METHODEN:
            return None
        host = request.get_host()
        name = host.split(':')[0]
        if name != Schnelleadresse.LANGSAM:
            return None
        if not self.will_html(request):
            return None
        neuer_host = host.replace(Schnelleadresse.LANGSAM,
                                  Schnelleadresse.SCHNELL, 1)
        return '%s://%s%s' % (request.scheme, neuer_host,
                              request.get_full_path())

    @staticmethod
    def will_html(request):
        u"""Ist das die Anfrage nach einer SEITE?

        Ein Browser schickt fuer das Dokument `Accept: text/html,…`; fuer ein
        Modul, ein Bild oder `fetch` steht dort etwas anderes. Fehlt der Kopf
        ganz (curl), wird nicht weitergeleitet: Wer die Adresse ausdruecklich
        so aufruft, meint sie auch so.
        """
        return 'text/html' in request.META.get('HTTP_ACCEPT', '')
