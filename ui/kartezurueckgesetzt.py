# -*- coding: utf-8 -*-
"""Meldung statt Fehler 500, wenn die Grafikkarte zurückgesetzt wurde.

DER VORFALL (17.11.2026, Edgar: „fehler http://127.0.0.1:8081/foto-genesis/")
==========================================================================
Windows hat die Karte um 20:39 zurückgesetzt (Ereignisanzeige, System,
nvlddmkm 14 und 153 „Reset TDR occurred on GPUID:100"). Der Server lief seit
14:55 im selben Prozess; sein CUDA-Kontext war danach unbrauchbar, und JEDER
Zugriff auf die Karte endete in

    torch.AcceleratorError: CUDA error: unknown error

um 23:42 zuerst beim Lesen von `form.npz` für die Foto-Genesis-Liste
(`Meshgenesistest.form` → `Npztorch.lesen`). Der Autoreload hilft nicht, weil
sich kein Code ändert; nur ein neuer Prozess bekommt einen neuen Kontext.

WAS DIESE MIDDLEWARE TUT
========================
Sie fängt Ausnahmen der Ansichten ab, deren Text „CUDA" enthält, und fragt
die Karte mit einer Ein-Element-Rechnung, ob sie in diesem Prozess noch
antwortet. Antwortet sie, war es ein gewöhnlicher Fehler (etwa „CUDA out of
memory") und Django behandelt ihn wie bisher. Antwortet sie nicht, kommt
statt der 500 eine 503 mit der Meldung, dass der Server neu starten muss —
als JSON unter `/api/`, sonst als Seite.

Sie startet den Server NICHT selbst neu: Ein Neustart beendet laufende
Aufträge und lässt alle offenen Tabs aufwärmen (`.claude/rules/projekt.md`).
"""

import logging
import sys

from django.http import JsonResponse
from django.shortcuts import render
from djangobase.middleware_basis import ZweiwegMiddleware

log = logging.getLogger('core.karte')


class Kartezurueckgesetzt(ZweiwegMiddleware):
    """503 mit Neustart-Hinweis, wenn der CUDA-Kontext des Prozesses tot ist."""

    MELDUNG = ('Die Grafikkarte wurde zurückgesetzt (Windows-Treiber, TDR). Dieser Serverprozess kann sie '
               'seitdem nicht mehr benutzen — bitte den Server neu starten: HumanBodyWeb\\restart_server.ps1')

    #: Wie `Datenfrische`: was als Datenweg gilt und JSON bekommt.
    PRAEFIXE = ('/api/',)

    #: Ein Fehler in dieser Middleware wäre ein Programmfehler.
    fehler_schlucken = False

    #: Den vollen Traceback nur beim ersten Mal ins Log, danach eine Zeile je Anfrage.
    _gemeldet = False

    def process_exception(self, request, fehler):
        """Django ruft das immer synchron auf (`BaseHandler.load_middleware`), auch unter ASGI."""
        if not self.karte_tot(fehler):
            return None
        if Kartezurueckgesetzt._gemeldet:
            log.error('Karte zurückgesetzt, %s %s: %s', request.method, request.path, fehler)
        else:
            Kartezurueckgesetzt._gemeldet = True
            log.error('Karte zurückgesetzt, %s %s', request.method, request.path, exc_info=fehler)
        if request.path.startswith(self.PRAEFIXE):
            # Beide Schlüssel: Die Seiten lesen teils `error`, teils `fehler`
            # (gezählt 18.11.2026 in core/api: 431 gegen 141 Antworten).
            return JsonResponse({'error': self.MELDUNG, 'fehler': self.MELDUNG, 'karte_zurueckgesetzt': True},
                                status=503)
        return render(request, 'karte_zurueckgesetzt.html', {'meldung': self.MELDUNG, 'fehler': str(fehler)},
                      status=503)

    @staticmethod
    def karte_tot(fehler):
        """True, wenn `fehler` von CUDA kommt und die Karte in DIESEM Prozess nicht mehr rechnet."""
        if not isinstance(fehler, RuntimeError) or 'CUDA' not in str(fehler):
            return False
        torch = sys.modules.get('torch')
        if torch is None:
            return False
        try:
            torch.ones(1, device='cuda').add_(1).item()
            torch.cuda.synchronize()
        except Exception:  # noqa: BLE001 — jede Art, an der die Probe scheitert, heißt „tot"
            return True
        return False
