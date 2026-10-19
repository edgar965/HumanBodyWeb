# -*- coding: utf-8 -*-
u"""G9vorratanfrage — was eine Netzanfrage mit dem dauerhaften Vorrat (`G9modellvorrat`) zu tun hat (19.10.2026).

Aus `G9antworten.liefern` herausgelöst (die Datei hatte 316 Zeilen). Je Anfrage:

* `stabil`     der Schlüssel ohne Code-Fassung (`G9antworten.schluessel(…, fassung='stabil')`),
* `behalten`   die Stufe dieser Anfrage liegt innerhalb der Einstellung (`Netzvorratwahl`),
* `markiert`   der Browser zeigt mit dieser Antwort eine Figur an (Kopf `X-G9-Vorrat`, `gemeinsam/genesis9vorrat.js`) — nur dann wird abgelegt,
* `nur`        Vorab-Füllen (Kopf `X-G9-Vorrat-Nur`): rechnen und ablegen, aber nichts ausliefern (204) — der Browser braucht die Bytes jetzt nicht.

Liegt die Antwort nur noch hier (der Code hat sich seit dem Ablegen geändert), geht sie sofort hinaus, und `G9vorratnachlauf` rechnet sie im Hintergrund
mit dem jetzigen Code neu — sobald der Server ruhig ist.
"""
import contextvars
import logging

from django.http import HttpResponse

from .g9modellvorrat import G9modellvorrat
from .netzvorratwahl import Netzvorratwahl

__all__ = ['G9vorratanfrage']

logger = logging.getLogger('core')


class G9vorratanfrage:

    KOPF = 'X-G9-Vorrat'
    KOPF_NUR = 'X-G9-Vorrat-Nur'

    def __init__(self, request, stabil):
        self.stabil = stabil
        self.markiert = bool(request is not None and request.headers.get(self.KOPF))
        self.nur = bool(request is not None and request.headers.get(self.KOPF_NUR))
        self.behalten = Netzvorratwahl.behalten(self.stufe())
        self.alt = False

    @staticmethod
    def stufe():
        u"""Die wirksame Genesis-Stufe dieser Anfrage (0 Käfig, 1 Ansicht, 2 Renderstufe)."""
        from Genesis9.netzstufe import G9netzstufe
        return G9netzstufe.browser()

    def holen(self, neu_rechnen):
        u"""Die abgelegten Bytes — oder None. Bei einem Treffer wird `neu_rechnen()` (liefert Bytes oder eine Fehlerantwort) im Hintergrund vorgemerkt."""
        if not self.behalten:
            return None
        daten = G9modellvorrat.holen(self.stabil)
        if daten is None:
            return None
        self.alt = True
        from .g9vorratnachlauf import G9vorratnachlauf
        kontext = contextvars.copy_context()             # die Stufe der Anfrage (`Netzstufenwahl`) gilt auch im Nachlauf
        G9vorratnachlauf.vormerken(self.stabil, lambda: kontext.run(neu_rechnen), self.stabil)
        return daten

    def ablegen(self, daten, frisch):
        u"""Bytes ablegen, wenn die Stufe dazugehört und die Anfrage eine Anzeige ist. `frisch`: eben gerechnet — dann ersetzt es auch einen alten Eintrag
        (ohne Markierung; er lag ja schon hier). Aus dem Vorrat der Fassung (`frisch` False) nur, wenn hier noch nichts liegt. Nach einer Antwort von hier
        (`alt`) nichts: das tut der Nachlauf."""
        if not self.behalten or self.alt:
            return
        da = G9modellvorrat.vorhanden(self.stabil)
        if (frisch and (self.markiert or da)) or (self.markiert and not da):
            G9modellvorrat.merken(self.stabil, daten)

    def liefern(self, daten, neu_rechnen, inhaltstyp):
        u"""Die Antwort: `daten` (aus dem Vorrat der Fassung) — sonst von hier (`holen`) — sonst `neu_rechnen()` (Bytes oder eine Fehlerantwort, die
        unverändert durchgeht). Abgelegt wird nach `ablegen`; beim Vorab-Füllen geht nichts hinaus (204)."""
        frisch = False
        if daten is None:
            daten = self.holen(neu_rechnen)
        if daten is None:
            daten, frisch = neu_rechnen(), True
            if isinstance(daten, HttpResponse):
                return daten
        self.ablegen(daten, frisch)
        if self.nur:
            return HttpResponse(status=204)
        return HttpResponse(daten, content_type=inhaltstyp)
