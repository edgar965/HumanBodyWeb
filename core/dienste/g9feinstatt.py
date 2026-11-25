# -*- coding: utf-8 -*-
u"""G9feinstatt — liegt die gewählte Stufe fertig im Vorrat, geht sie statt des Käfigs hinaus (24.11.2026).

Edgar, 24.11.2026: „EdgarNeu laden im Charakter dauert ewig, das muss in 2 s laden“. Gemessen im Chrome (Antworten alle im Vorrat, Server 0,03–0,21 s je Anfrage): der
Käfig stand nach 0,7–0,9 s, die feine Stufe nach 2,9–3,4 s — jedes Stück kam zweimal über die Leitung (die Hose zweimal 7,7 MB, 97.235 Punkte auf beiden Stufen), wurde
zweimal gebaut und zweimal auf die Karte geladen, eines nach dem anderen. Der Käfig ist dafür da, dass die Figur steht, solange der Server RECHNET (`Genesis9aufbau`,
18.09.2026); liegt die feine Antwort schon, ist er der Umweg.

Der Browser bittet mit dem Kopf `X-G9-Fein-Gern` an der Käfig-Anfrage (`?stufen=0`, `gemeinsam/genesis9vorrat.js`):
  * `1`     ein Stück: die Antwort der gewählten Stufe, wenn sie MIT DEM JETZIGEN CODE gerechnet liegt — Antwortkopf `X-G9-Fein`;
  * `leer`  der Körper, dessen gewählte Stufe der Browser im selben Zug schon bestellt hat (`Genesis9materialabruf.vorab`): 204 mit `X-G9-Fein`, sie kommt dort.
Liegt sie nicht, gilt die Anfrage wie bisher dem Käfig. Je Antwort entschieden: Körper und Stücke dürfen verschieden ausgehen, die fehlenden holt der zweite Zug
(`Genesis9haeppchen`) wie bisher.
"""
from django.http import HttpResponse

from .g9modellvorrat import G9modellvorrat
from .netzstufenwahl import Netzstufenwahl
from .netzvorratwahl import Netzvorratwahl

__all__ = ['G9feinstatt']


class G9feinstatt:

    KOPF = 'X-G9-Fein-Gern'
    KOPF_ANTWORT = 'X-G9-Fein'
    #: Wert von `KOPF`: die Antwort der gewählten Stufe ist schon unterwegs — nur Bescheid geben.
    LEER = 'leer'

    def __init__(self, request, schluessel, antworten):
        u"""`schluessel(stufe, fassung=None)` → Schlüssel der Antwort; `antworten`: `G9antworten` (Vorrat der Fassung). `stufe` danach: die Stufe, die gilt — die der
        Anfrage oder, statt des Käfigs, die gewählte (dann gilt sie auch für den Rest der Anfrage, `Netzstufenwahl`)."""
        self.stufe = Netzstufenwahl.gewaehlt()
        self.fein = False
        wunsch = request.headers.get(self.KOPF) if request is not None else None
        if not wunsch or self.stufe != 0:
            return
        wahl = Netzstufenwahl.aus_cookies(request.COOKIES)           # None: die Einstellung
        if not self._liegt(wahl, schluessel, antworten):
            return
        self.fein, self.stufe, self.wunsch = True, wahl, wunsch
        # Für den Nachlauf nach einem Neustart (`G9neustartnachlauf`): diese Anzeige ist die der gewählten Stufe, nicht die des Käfigs.
        request.g9_abfrage = '&'.join(t for t in request.META.get('QUERY_STRING', '').split('&') if t and not t.startswith(Netzstufenwahl.ANFRAGE + '='))

    @staticmethod
    def _liegt(wahl, schluessel, antworten):
        u"""Liegt die Antwort der Stufe `wahl` mit dem jetzigen Code gerechnet — im Vorrat der Fassung oder im dauerhaften? Wenn ja, gilt `wahl` ab hier."""
        marke = Netzstufenwahl._gewaehlt.set(wahl)
        if antworten.holen(schluessel(wahl)) is not None:
            return True
        if Netzvorratwahl.behalten(G9feinstatt._stufe()) and G9modellvorrat.fassung_von(schluessel(wahl, 'stabil')) == str(antworten.fassung()):
            return True
        Netzstufenwahl._gewaehlt.reset(marke)
        return False

    @staticmethod
    def _stufe():
        from Genesis9.netzstufe import G9netzstufe
        return G9netzstufe.browser()

    def bescheid(self):
        u"""Die Antwort ohne Inhalt, wenn der Browser die gewählte Stufe schon bestellt hat — sonst None."""
        return self.zeichnen(HttpResponse(status=204)) if self.fein and self.wunsch == self.LEER else None

    def zeichnen(self, antwort):
        if self.fein:
            antwort[self.KOPF_ANTWORT] = '1'
        return antwort
