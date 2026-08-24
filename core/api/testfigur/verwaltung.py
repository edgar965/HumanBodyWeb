# -*- coding: utf-8 -*-
"""Fassung anzeigen, neu laden, Figur wechseln.

Aus `core/test_character_api.py` herausgelöst (17.08.2026).
`test_switch_character` hatte 85 Zeilen: Prüfen, Verzeichnis leeren, kopieren,
`commit_info.json` fortschreiben und sechs `global`-Angaben zum Zurücksetzen.
Das Kopieren steht jetzt in `Figurenwechsel`, das Zurücksetzen in
`Testkern.vergessen()` — es stand vorher zweimal wörtlich da.
"""

import logging
import os
import shutil

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .quellenschau import Quellenschau
from .testkern import Testkern

logger = logging.getLogger(__name__)


class Figurenwechsel:
    """Setzt eine der abgelegten CharMorph-Figuren als aktive Testdaten."""

    #: Ohne diese Datei ist ein Ordner keine brauchbare Figur.
    KENNDATEI = 'faces.npy'

    def __init__(self, name):
        self.name = name or ''
        self.ablage = os.path.join(Testkern.WURZEL, 'charmorph_data')
        self.quelle = os.path.join(self.ablage, self.name)
        self.ziel = Testkern.datenordner()

    @property
    def vorhanden(self):
        return bool(self.name) and os.path.isdir(self.quelle)

    def auswahl(self):
        """Die Figuren, die zur Verfügung stehen."""
        if not os.path.isdir(self.ablage):
            return []
        return sorted(
            d for d in os.listdir(self.ablage)
            if os.path.isdir(os.path.join(self.ablage, d))
            and os.path.isfile(os.path.join(self.ablage, d, self.KENNDATEI)))

    def umschalten(self):
        """Zielordner leeren, Figur hineinkopieren, Fassungsinfo fortschreiben."""
        if os.path.isdir(self.ziel):
            shutil.rmtree(self.ziel)
        os.makedirs(self.ziel, exist_ok=True)
        self._kopieren()
        self._fassung_vermerken()
        Testkern.vergessen()
        logger.info('Testfigur gewechselt auf %s', self.name)

    def _kopieren(self):
        for ordner, _unterordner, dateien in os.walk(self.quelle):
            for name in dateien:
                quelle = os.path.join(ordner, name)
                ziel = os.path.join(self.ziel,
                                    os.path.relpath(quelle, self.quelle))
                os.makedirs(os.path.dirname(ziel), exist_ok=True)
                shutil.copy2(quelle, ziel)

    def _fassung_vermerken(self):
        daten = Quellenschau.fassung()
        if daten is None:
            return
        daten['character'] = self.name
        daten['message'] = 'CharMorphPlugin %s character' % self.name
        Quellenschau.fassung_schreiben(daten)


@require_GET
def test_version_info(request):
    """Welche Fassung liegt gerade unter `TestCharakter/`?"""
    daten = Quellenschau.fassung()
    if daten is None:
        return JsonResponse({'error': 'No test version downloaded'}, status=404)
    return JsonResponse(daten)


@require_GET
def test_character_source(request):
    """Quelltext und Datenbestand der Testfassung (siehe `Quellenschau`)."""
    schau = Quellenschau()
    if not schau.vorhanden:
        return JsonResponse({'error': 'No test version downloaded'}, status=404)
    return JsonResponse(schau.bericht())


@require_GET
def test_reload(request):
    """Zwischenstände fallen lassen — für einen Fassungswechsel ohne Neustart."""
    Testkern.vergessen()
    return JsonResponse({'ok': True, 'message': 'Test singletons reloaded'})


@csrf_exempt
@require_POST
def test_switch_character(request):
    """Aktive CharMorph-Figur wechseln und die Zwischenstände fallen lassen.

    NUR POST (17.08.2026). Diese Ansicht macht ein `shutil.rmtree` auf
    `TestCharakter/data/humanBody` und baut das Verzeichnis danach neu auf. Sie
    stand auf `@require_GET` — ein `<img src="…/switch/?name=x">` auf einer
    fremden Seite hat damit ein Verzeichnis geleert. Gefunden vom Werkzeug
    `schreibrouten`.

    `csrf_exempt` + Methodenschutz ist hier das Hausmuster: Die
    `GleicherUrsprung`-Middleware prüft bei schreibenden Methoden den Ursprung
    der Anfrage, nicht ein Formular-Token.

    Der Name kommt weiter aus der Abfragezeichenkette, damit die zwei
    Aufrufstellen in `test_character.html` sich nur in der Methode ändern.
    """
    wechsel = Figurenwechsel(request.GET.get('name', ''))
    if not wechsel.vorhanden:
        return JsonResponse({'error': 'Character "%s" not found' % wechsel.name,
                             'available': wechsel.auswahl()}, status=400)
    wechsel.umschalten()
    return JsonResponse({'ok': True, 'character': wechsel.name,
                         'message': 'Switched to %s' % wechsel.name})
