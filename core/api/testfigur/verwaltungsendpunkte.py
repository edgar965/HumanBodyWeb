# -*- coding: utf-8 -*-
"""Die Endpunkte der Testfassung: Fassung zeigen, neu laden, Figur wechseln.

Aus `testfigur/verwaltung.py` herausgeloest (27.08.2026, Befunde
`freie-funktionen` und `klassen-je-datei`). Dort steht mit `Figurenwechsel` die
Arbeit; hier die HTTP-Schale.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .quellenschau import Quellenschau
from .testkern import Testkern
from .verwaltung import Figurenwechsel


class Testverwaltung:
    """Fassung, Quelltextbericht, Zwischenstaende und Figurenwechsel."""

    @staticmethod
    @require_GET
    def fassung(request):
        """Welche Fassung liegt gerade unter `TestCharakter/`?"""
        daten = Quellenschau.fassung()
        if daten is None:
            return JsonResponse({'error': 'No test version downloaded'},
                                status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def quelltext(request):
        """Quelltext und Datenbestand der Testfassung (siehe `Quellenschau`)."""
        schau = Quellenschau()
        if not schau.vorhanden:
            return JsonResponse({'error': 'No test version downloaded'},
                                status=404)
        return JsonResponse(schau.bericht())

    @staticmethod
    @require_GET
    def neu_laden(request):
        """Zwischenstaende fallen lassen — Fassungswechsel ohne Neustart."""
        Testkern.vergessen()
        return JsonResponse({'ok': True,
                             'message': 'Test singletons reloaded'})

    @staticmethod
    @csrf_exempt
    @require_POST
    def figur_wechseln(request):
        """Aktive CharMorph-Figur wechseln und die Zwischenstaende leeren.

        NUR POST (17.08.2026). Diese Ansicht macht ein `shutil.rmtree` auf
        `TestCharakter/data/humanBody` und baut das Verzeichnis danach neu auf.
        Sie stand auf `@require_GET` — ein `<img src="…/switch/?name=x">` auf
        einer fremden Seite hat damit ein Verzeichnis geleert. Gefunden vom
        Werkzeug `schreibrouten`.

        `csrf_exempt` + Methodenschutz ist hier das Hausmuster: Die
        `GleicherUrsprung`-Middleware prueft bei schreibenden Methoden den
        Ursprung der Anfrage, nicht ein Formular-Token.

        Der Name kommt weiter aus der Abfragezeichenkette, damit die zwei
        Aufrufstellen in `test_character.html` sich nur in der Methode aendern.
        """
        wechsel = Figurenwechsel(request.GET.get('name', ''))
        if not wechsel.vorhanden:
            return JsonResponse(
                {'error': 'Character "%s" not found' % wechsel.name,
                 'available': wechsel.auswahl()}, status=400)
        wechsel.umschalten()
        return JsonResponse({'ok': True, 'character': wechsel.name,
                             'message': 'Switched to %s' % wechsel.name})
