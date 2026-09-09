# -*- coding: utf-8 -*-
u"""Daten kommen nie aus dem Zwischenspeicher des Browsers.

DER BEFUND (Edgar, 09.09.2026: „FemaleGarmentCode gerade gespeichert, nach
dem Speichern keine GarmentCode Dinger! Das habe ich schon zum 4. Mal
aufgetragen!!!")
=====================================================================
Am Code lag es nicht. Die gespeicherte Datei fuehrte das Stueck, der
Ladeweg zog es an, und beides ist im Browser nachgemessen. Der Serverlog
zeigt, was wirklich passierte:

    12:34:10  POST /api/character/model/save/          gespeichert
    12:34:37  GET  /api/character/mesh/?...            Figur neu gebaut
    12:34:37  GET  /api/character/hairstyle/ballerina/ Haare
              (KEIN GET auf /api/character/model/FemaleGarmentCode/,
               KEIN GET auf die rig-Datei des T-Shirts)

Der Modell-GET fehlt, weil der Browser ihn NICHT GESTELLT hat: Er hat die
Antwort von vor dem Speichern aus seinem Zwischenspeicher genommen — und
darin gab es die GarmentCode-Liste noch nicht. Die Figur kam nackt, ohne
Fehler und ohne Meldung.

MOEGLICH IST DAS, WEIL DIE API KEINEN EINZIGEN CACHE-HEADER SETZTE
==================================================================
Gemessen am laufenden Server (09.09.2026):

    GET /api/character/model/FemaleGarmentCode/   -> kein Cache-Control,
                                                     kein ETag,
                                                     kein Last-Modified

Ohne Angabe zur Frische darf der Browser selbst schaetzen, und er schaetzt
10 % des Alters der Ressource (RFC 9111, „heuristic freshness"). Genau
diese Falle steht im Kopf von `djangobase/cache_middleware.py` fuer Statik
beschrieben; dort endet die Behandlung aber bei `text/html` und der Statik
— „alles andere unangetastet". JSON ist „alles andere".

Deshalb hier: **Antworten unter `/api/` werden nicht gespeichert.** Sie
sind Daten, nicht Seiten; ihr Wert aendert sich, ohne dass die URL sich
aendert. Genau das ist die Voraussetzung, unter der ein Zwischenspeicher
falsch antwortet.

DIE STATIK BLEIBT UNBERUEHRT. Sie soll aus dem Zwischenspeicher kommen —
eine Middleware, die pauschal `no-store` setzt, laedt bei jedem
Seitenaufruf saemtliche Module neu. Das war die alte `ui/no_cache.py`, und
sie ist aus genau diesem Grund entfallen (CLAUDE.md, 28.08.2026).

WARUM NICHT IN DJANGOBASE: Das Paket haengt in sechs Projekten als
editable Install; eine Aenderung dort wirkt sofort in allen
(`A:/shared/djangoBase/CLAUDE.md`). Die Regel ist ein Kandidat dafuer —
aber erst nach Ruecksprache, nicht als Nebenwirkung einer Fehlerbehebung.
"""


class Datenfrische:
    u"""`Cache-Control: no-store` fuer alles unter `/api/`."""

    #: Was als Datenweg gilt. Bewusst der Pfad und nicht der Inhaltstyp:
    #: Die Seiten liefern ihre Vorlagen als `text/html`, und `djangobase`
    #: setzt dort schon `no-store`; eine zweite Zustaendigkeit fuer
    #: dieselbe Antwort waere eine Quelle fuer Widersprueche.
    PRAEFIXE = ('/api/',)

    WERT = 'no-store, no-cache, must-revalidate'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        antwort = self.get_response(request)
        if not request.path.startswith(Datenfrische.PRAEFIXE):
            return antwort
        # Ein Endpunkt, der seine Frische selbst regelt, behaelt sie: Es
        # gibt Antworten, die absichtlich lange gelten (ausgelieferte
        # Netze mit Fingerabdruck im Pfad). Ueberschreiben hiesse, deren
        # Entscheidung stillschweigend zu kassieren.
        if antwort.has_header('Cache-Control'):
            return antwort
        antwort['Cache-Control'] = Datenfrische.WERT
        antwort['Pragma'] = 'no-cache'
        antwort['Expires'] = '0'
        return antwort
