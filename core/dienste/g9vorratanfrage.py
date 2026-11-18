# -*- coding: utf-8 -*-
u"""G9vorratanfrage — was eine Netzanfrage mit dem dauerhaften Vorrat (`G9modellvorrat`) zu tun hat (19.10.2026).

Aus `G9antworten.liefern` herausgelöst (die Datei hatte 316 Zeilen). Je Anfrage:

* `stabil`     der Schlüssel ohne Code-Fassung (`G9antworten.schluessel(…, fassung='stabil')`),
* `behalten`   die Stufe dieser Anfrage liegt innerhalb der Einstellung (`Netzvorratwahl`),
* `markiert`   der Browser zeigt mit dieser Antwort eine Figur an (Kopf `X-G9-Vorrat`, `gemeinsam/genesis9vorrat.js`) — nur dann wird abgelegt,
* `nur`        Vorab-Füllen (Kopf `X-G9-Vorrat-Nur`): rechnen und ablegen, aber nichts ausliefern (204) — der Browser braucht die Bytes jetzt nicht,
* `vorschau`   der Käfig des ersten Zugs, den die gewählte Stufe gleich ersetzt (Kopf `X-G9-Vorrat-Vorschau`, nur auf Stufe 0; seit 17.11.2026).

Liegt die Antwort hier mit dem jetzigen Code gerechnet (`fassung`), geht sie sofort hinaus. Mit älterem Code gerechnet nur als Vorschau oder beim
Vorab-Füllen — dann rechnet `G9vorratnachlauf` sie im Hintergrund neu, sobald der Server ruhig ist; sonst wird sie neu gerechnet und ersetzt
(17.11.2026, Edgar: „fixe das: Nach einer Code-Änderung zeigen sie beim ersten Laden noch den alten Stand"; Kopf von `g9modellvorrat.py`).
"""
import contextvars
import logging

from django.http import HttpResponse

from ..daten.netzpaket import Netzpaket
from .g9modellvorrat import G9modellvorrat
from .g9vorratnachlauf import G9vorratnachlauf
from .netzvorratwahl import Netzvorratwahl

__all__ = ['G9vorratanfrage']

logger = logging.getLogger('core')


class G9vorratanfrage:

    KOPF = 'X-G9-Vorrat'
    KOPF_NUR = 'X-G9-Vorrat-Nur'
    KOPF_VORSCHAU = 'X-G9-Vorrat-Vorschau'
    #: An der Antwort: mit älterem Code gerechnet — der Browser hält sie nicht im RAM.
    KOPF_ALT = 'X-G9-Vorrat-Alt'

    def __init__(self, request, stabil, fassung):
        self.stabil = stabil
        self.fassung = str(fassung)
        kopf = request.headers if request is not None else {}
        self.pfad = getattr(request, 'path', '')
        self.stufe_nr = stufe = self.stufe()
        self.markiert = bool(kopf.get(self.KOPF))
        self.nur = bool(kopf.get(self.KOPF_NUR))
        self.vorschau = bool(kopf.get(self.KOPF_VORSCHAU)) and stufe == 0
        self.behalten = Netzvorratwahl.behalten(stufe)
        self.alt = False

    @staticmethod
    def stufe():
        u"""Die wirksame Genesis-Stufe dieser Anfrage (0 Käfig, 1 Ansicht, 2 Renderstufe)."""
        from Genesis9.netzstufe import G9netzstufe
        return G9netzstufe.browser()

    def holen(self, neu_rechnen):
        u"""Die abgelegten Bytes — oder None (dann rechnet der Aufrufer). Ein Eintrag älteren Codes nur als Vorschau oder beim Vorab-Füllen; dann wird
        `neu_rechnen()` (liefert Bytes oder eine Fehlerantwort) im Hintergrund vorgemerkt."""
        if not self.behalten:
            return None
        eintrag = G9modellvorrat.lesen(self.stabil)
        if eintrag is None:
            return None
        daten, fassung = eintrag
        if Netzpaket.nummern_gekuerzt(daten):
            # 12.11.2026: Eine Antwort aus der Zeit, als die Körperpunkt-Nummern der Oberflächenbindung auf 16 Bit gerundet reisten (`netzkurz.py`) — sie
            # zeigte Stacheln an Kragen und Schuh. Nicht ausliefern: Der Aufrufer rechnet jetzt neu, und `ablegen` ersetzt den Eintrag (`frisch`). Gemessen
            # am Fallout Ranger: Mit „sofort alt, im Hintergrund neu“ waren nach drei Ladungen erst zwei von sechs gebundenen Stücken geheilt.
            logger.info('Genesis 9: Antwort im dauerhaften Vorrat mit gekürzten Nummern der Bindung verworfen (%s)', self.stabil[:40])
            return None
        if fassung == self.fassung:
            return daten
        if not (self.vorschau or self.nur):
            logger.info('Genesis 9: Anzeige im dauerhaften Vorrat mit älterem Code gerechnet — wird neu gerechnet (%s)', self.stabil[:40])
            return None
        self.alt = True
        kontext = contextvars.copy_context()             # die Stufe der Anfrage (`Netzstufenwahl`) gilt auch im Nachlauf
        G9vorratnachlauf.vormerken(self.stabil, lambda: kontext.run(neu_rechnen), self.stabil)
        return daten

    def ablegen(self, daten):
        u"""Bytes des jetzigen Codes (eben gerechnet oder aus dem Vorrat der Fassung) mit dessen Fassung ablegen, wenn die Stufe dazugehört und die Anfrage
        eine Anzeige ist — oder hier ein Eintrag älteren Codes liegt (ohne Markierung; er war schon eine Anzeige). Liegt er schon mit dieser Fassung,
        nichts. Nach einer alten Antwort von hier (`alt`) nichts: das tut der Nachlauf."""
        if not self.behalten or self.alt:
            return
        da = G9modellvorrat.fassung_von(self.stabil)
        if da != self.fassung and (da is not None or self.markiert):
            G9modellvorrat.merken(self.stabil, daten, self.fassung)

    def liefern(self, daten, neu_rechnen, inhaltstyp):
        u"""Die Antwort: `daten` (aus dem Vorrat der Fassung) — sonst von hier (`holen`) — sonst `neu_rechnen()` (Bytes oder eine Fehlerantwort, die
        unverändert durchgeht). Abgelegt wird nach `ablegen`; beim Vorab-Füllen geht nichts hinaus (204). Eine Vorschau meldet dem Nachlauf, dass die gewählte
        Stufe dieses Teils folgt; deren Auslieferung meldet, dass sie da ist (`G9vorratnachlauf._ausstehend`)."""
        if self.vorschau:
            G9vorratnachlauf.vorschau_gegangen(self.pfad)
        try:
            return self._antwort(daten, neu_rechnen, inhaltstyp)
        finally:
            if self.stufe_nr > 0 and not self.nur:
                G9vorratnachlauf.stufe_geliefert(self.pfad)

    def _antwort(self, daten, neu_rechnen, inhaltstyp):
        if daten is None:
            daten = self.holen(neu_rechnen)
        if daten is None:
            daten = neu_rechnen()
            if isinstance(daten, HttpResponse):
                return daten
        self.ablegen(daten)
        if self.nur:
            return HttpResponse(status=204)
        antwort = HttpResponse(daten, content_type=inhaltstyp)
        if self.alt:
            antwort[self.KOPF_ALT] = '1'
        return antwort
