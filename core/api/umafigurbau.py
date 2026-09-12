# -*- coding: utf-8 -*-
u"""UMA-Figuren in Python bauen — Rasse waehlen, Regler stellen.

    GET  /api/umapython/rassen/
      -> {rassen: [{name, gruppe}], beispiele: [...]}

    POST /api/umapython/figur/
         {rasse, dna: {name: 0..1}}
      -> {rasse, netz, skelett, bilanz, regler}

WARUM (Edgar, 08.09.2026: „Beim Modell UMA Python habe ich immer noch keine
Portierung. Ich moechte doch ein Male, Female, Elf usw. auswaehlen, genau so
wie UMA das macht!")

Der Reiter „UMA Python" war bis dahin ein Pruefstand fuer die
Kleidungs-Anpassung — er zeigte einen GarmentCode-Referenzkoerper mit einem
drapierten Stueck. Der Name versprach etwas anderes, und Edgar hat zu Recht
gefragt, warum da ein SMPL-Modell kommt.

Jetzt baut er wirklich: Rasse aus UMAs Katalog (20 Stueck, darunter Elf,
HalfOrc, Sylvan, Sprite), Netz und Skelett aus den binaeren Assets, Form
ueber die 62 DNA-Regler. Ohne Unity.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger('core')

__all__ = ['Umafigurbau']


class Umafigurbau:
    u"""Rassen listen, Figuren bauen, Regler anwenden."""

    #: Die drei, die Edgar nennt („Male, Female, Elf"). Sie stehen oben in
    #: der Liste und liegen als Beispiel auf der Platte.
    #:
    #: Die Namen sind die des KATALOGS, nicht der Dateien: `RaceData._Name`
    #: heisst „Human Female 3.0", die Datei `HumanFemale30.asset`. Wer die
    #: Dateinamen nimmt, findet nichts (Befund 08.09.2026).
    BEISPIELE = ('Human Male 3.0', 'Human Female 3.0', 'Elf Male')

    #: Rassen, die keine Figur sind. `SkyCar` ist ein Auto aus UMAs
    #: SRP-Beispielszene — es steht im selben Katalog.
    AUS = ('SkyCar',)

    @staticmethod
    @require_GET
    def rassen(request):
        from core.dienste.umapythonfiguren import Umapythonfiguren
        try:
            alle = [r for r in Umapythonfiguren.rassen()
                    if r not in Umafigurbau.AUS]
        except (OSError, ValueError) as fehler:
            logger.warning('UMA Python: Katalog nicht lesbar: %s', fehler)
            return JsonResponse({'rassen': [], 'fehler': str(fehler)})
        beispiele = [r for r in Umafigurbau.BEISPIELE if r in alle]
        uebrige = sorted(r for r in alle if r not in beispiele)
        return JsonResponse({
            'rassen': beispiele + uebrige,
            'beispiele': beispiele,
        })

    @staticmethod
    @csrf_exempt
    @require_POST
    def figur(request):
        u"""Eine Figur bauen und ihre Regler stellen."""
        from core.dienste.umapythonfiguren import Umapythonfiguren
        from UMA_Python.szene import Szenenfigur
        try:
            wunsch = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'fehler': 'Anfrage nicht lesbar'}, status=400)

        rasse = str(wunsch.get('rasse') or '').strip()
        if not rasse:
            return JsonResponse({'fehler': 'Keine Rasse angegeben'},
                                status=400)
        dna = Umafigurbau._dna(wunsch.get('dna'))
        try:
            gebaut = Umapythonfiguren.bauen(rasse)
        except (OSError, ValueError) as fehler:
            logger.warning('UMA Python: %s nicht baubar: %s', rasse, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:                        # noqa: BLE001
            logger.exception('UMA Python: unerwarteter Fehler bei %s', rasse)
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)

        antwort = Szenenfigur.alles(gebaut, dna)
        antwort['regler'] = Szenenfigur.regler(gebaut)
        return JsonResponse(antwort)

    @staticmethod
    def _dna(roh):
        u"""Reglerwerte aus der Anfrage, auf 0..1 begrenzt.

        Begrenzt, weil die Werte aus dem Browser kommen: `abbilden` rechnet
        `von + kurve(wert) * (bis - von)`, und eine Kurve ausserhalb ihres
        Bereichs liefert ihren Randwert — das faellt nicht auf, ergibt aber
        eine Figur, die zu keiner Reglerstellung gehoert.
        """
        if not isinstance(roh, dict):
            return {}
        werte = {}
        for name, wert in roh.items():
            try:
                werte[str(name)] = min(1.0, max(0.0, float(wert)))
            # stumm gewollt: fremde Reglerwerte aus dem Browser, ein unbrauchbarer
            # wird uebergangen
            except (TypeError, ValueError):
                continue
        return werte
