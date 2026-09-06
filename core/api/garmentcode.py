# -*- coding: utf-8 -*-
"""GarmentCode: Zustand, Koerpermasse, Schnitt erzeugen, Vorschau ausliefern.

Kleidung wird hier KONSTRUIERT, nicht angepasst — der Gegenentwurf zur
Garderobe in `api/kleidung.py`. Warum das der Weg ist, steht in
`dienste/garmentcode.py`.
"""

import json
import logging
import os

from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.garmentcode import GarmentcodeDienst

logger = logging.getLogger(__name__)


class Garmentcode:
    """Die Endpunkte des GarmentCode-Reiters."""

    #: Nur diese Dateien darf die Vorschau ausliefern — der Ordnername kommt
    #: aus dem Browser, also wird der Pfad nie aus der Anfrage zusammengebaut,
    #: sondern gegen den Ausgabeordner geprueft.
    ERLAUBTE_ENDUNGEN = ('.png', '.svg', '.pdf', '.json', '.yaml')

    @staticmethod
    @require_GET
    def zustand(request):
        """Ist GarmentCode da, und welche Vorlagen bringt es mit?"""
        zustand = GarmentcodeDienst.zustand()
        # Die Simulation haengt an einer eigenen Python-Umgebung und dem
        # selbst gebauten Warp — sie kann fehlen, waehrend Schnittmuster
        # laengst gehen. Die Seite soll das unterscheiden koennen.
        try:
            zustand['drapierbereit'] = GarmentcodeDienst.drapierbereit()
        except Exception:
            logger.exception('GarmentCode: Drapier-Pruefung gescheitert')
            zustand['drapierbereit'] = False
        return JsonResponse(zustand)

    @classmethod
    @require_POST
    def drapieren(cls, request):
        """Aus einem erzeugten Schnittmuster ein 3D-Netz rechnen."""
        from GarmentCode.drapierung import DrapierFehler
        spez = request.POST.get('spezifikation') or ''
        if not spez:
            return JsonResponse({'fehler': 'Kein Schnittmuster angegeben'},
                                status=400)
        try:
            anfrage = cls._anfrage(request)
            ergebnis = GarmentcodeDienst.drapieren(
                spez, koerper=request.POST.get('koerper') or None,
                geschlecht=anfrage['geschlecht'], morphs=anfrage['morphs'],
                bauart=anfrage['bauart'])
        except DrapierFehler as fehler:
            logger.warning('Drapierung gescheitert: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:
            logger.exception('Drapierung: unerwarteter Fehler')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        return JsonResponse(ergebnis)

    @classmethod
    @require_POST
    def masse(cls, request):
        """Die Masse der gewaehlten Figur — mit ihren Reglerwerten."""
        anfrage = cls._anfrage(request)
        werte, herkunft = GarmentcodeDienst.masse(
            anfrage['geschlecht'], morphs=anfrage['morphs'],
            bauart=anfrage['bauart'])
        return JsonResponse({
            'masse': {name: round(float(wert), 2)
                      for name, wert in sorted(werte.items())
                      if not name.startswith('_')},
            'herkunft': herkunft,
            'morphs': len(anfrage['morphs'] or {}),
        })

    @staticmethod
    def _anfrage(request):
        """Geschlecht, Bauart und Morphs aus dem Rumpf der Anfrage.

        Die Morphs kommen als JSON, weil es Dutzende sind und sie sonst
        einzeln im Formular staenden.
        """
        try:
            morphs = json.loads(request.POST.get('morphs') or '{}')
        except ValueError:
            logger.warning('GarmentCode: Morphs unlesbar, nehme Grundkoerper')
            morphs = {}
        return {
            'vorlage': request.POST.get('vorlage', 't-shirt'),
            'geschlecht': request.POST.get('geschlecht', 'female'),
            'bauart': request.POST.get('bauart') or None,
            'morphs': morphs if isinstance(morphs, dict) else {},
        }

    @classmethod
    @require_POST
    def erzeugen(cls, request):
        """Einen Schnitt bauen. Antwort nennt Ordner und Vorschaubild."""
        from GarmentCode.entwurf import EntwurfFehler
        anfrage = cls._anfrage(request)
        try:
            ergebnis = GarmentcodeDienst.erzeugen(
                anfrage['vorlage'], geschlecht=anfrage['geschlecht'],
                morphs=anfrage['morphs'], bauart=anfrage['bauart'])
        except EntwurfFehler as fehler:
            logger.warning('GarmentCode gescheitert: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:
            logger.exception('GarmentCode: unerwarteter Fehler')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)

        ordner = ergebnis.get('ordner', '')
        bild = GarmentcodeDienst.vorschaubild(ordner)
        ergebnis['spezifikation'] = GarmentcodeDienst.spezifikation(ergebnis) or ''
        ergebnis['vorschau'] = (
            '/api/garmentcode/datei/%s/%s/' % (os.path.basename(ordner), bild)
            if bild else '')
        return JsonResponse(ergebnis)

    @classmethod
    @require_GET
    def datei(cls, request, ordner, name):
        """Eine Datei aus einem Ergebnisordner ausliefern."""
        from GarmentCode.entwurf import Entwurf
        if not name.lower().endswith(cls.ERLAUBTE_ENDUNGEN):
            return JsonResponse({'fehler': 'Dateityp nicht erlaubt'}, status=400)
        wurzel = os.path.abspath(Entwurf.AUSGABE)
        pfad = os.path.abspath(os.path.join(wurzel, ordner, name))
        # Der Ordnername kommt aus dem Browser: nur unterhalb der Wurzel.
        if not pfad.startswith(wurzel + os.sep) or not os.path.isfile(pfad):
            return JsonResponse({'fehler': 'Nicht gefunden'}, status=404)
        return FileResponse(open(pfad, 'rb'))
