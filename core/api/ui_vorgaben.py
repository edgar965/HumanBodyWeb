# -*- coding: utf-8 -*-
"""Zwei JSON-Endpunkte, die die Oberfläche beim Laden braucht.

Sie standen in `core/api/einstellungen.py`, weil sie „Einstellungen" im Namen
tragen — mit den sechs EinstellungsSEITEN haben sie aber nichts zu tun: Der eine
merkt Panelbreiten, der andere liefert Animationen nach. Beim Aufteilen der
Seiten in ein Paket (17.08.2026) wären sie dort das Beiwerk gewesen, das man
beim Suchen nicht findet.

UMBAU 27.08.2026 (Befund `freie-funktionen`): zwei freie Funktionen, jetzt
Methoden von `Uivorgaben`.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..dienste.animationsauswahl import Animationsauswahl
from ..models import AppSettings

logger = logging.getLogger('core')


class Uivorgaben:
    """Was die Oberfläche sich merkt, und was sie nachlädt."""

    @staticmethod
    @csrf_exempt
    def vorlieben(request):
        """GET liest die Oberflächen-Vorlieben, POST ergänzt sie.

        POST überschreibt nur die mitgeschickten Schlüssel — die Seiten
        speichern einzelne Werte (Panelbreite, letzte Auswahl) und dürfen dabei
        nicht die Vorlieben der anderen Seiten löschen.
        """
        gespeichert, _ = AppSettings.objects.get_or_create(pk=1)
        if request.method == 'POST':
            vorlieben = gespeichert.ui_prefs or {}
            vorlieben.update(json.loads(request.body))
            gespeichert.ui_prefs = vorlieben
            gespeichert.save(update_fields=['ui_prefs'])
            return JsonResponse({'ok': True})
        return JsonResponse(gespeichert.ui_prefs or {})

    @staticmethod
    def animationen(request, kategorie):
        """Die Animationen EINER Kategorie — Nachschub für das Auswahlfeld.

        Der Baustein `_anim_selector.html` liefert seit dem 16.08.2026 nur noch
        die Kategorieköpfe mit; die Einträge holt `animationsauswahl.js` beim
        ersten Aufklappen hier ab. Vorher standen alle 7.067 in jeder
        Einstellungsseite.
        """
        auswahl = Animationsauswahl.aus_anfrage(request)
        return JsonResponse({'animationen': auswahl.eintraege(kategorie)})
