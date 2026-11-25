# -*- coding: utf-8 -*-
"""Ein SMPL-Koerper in anderer Form: alle zehn Shape-Betas als Regler.

    POST /api/character/smpl-figur/formen/
         {geschlecht: 'male'|'female', groesse: -100..100, fuelle: -100..100,
          form3..form10: -100..100 (optional, Vollausstattung 25.09.2026),
          nur: 'form' (Reglerzug, 25.11.2026): punkte als Binaerfeld, ohne Dreiecke, UV und Gewichte — die stehen im Browser}
      -> {name, geschlecht, betas, punkte, dreiecke, hoehe, masse,
          regler, skelett, uv, uv_dreiecke, uv_ursprung}

WARUM ES DIESEN ENDPUNKT GIBT (Edgar, 06.09.2026: „der mann in Fall 2 soll
schlank sein, finde den Regler, dass du ihn schlank machst!"): Im
Online-Tool gibt es diesen Regler nicht — gemessen im laufenden Tool bleibt
der 3D-Koerper bei Bust 70 / Waist 55 / Hips 70 Punkt fuer Punkt derselbe
(142.500 Punkte, 172 cm). Formbar ist ein SMPL-Koerper nur ueber seine
Blendshapes; welcher Regler welches Beta mit welchem Vorzeichen bewegt,
steht gemessen in `GarmentCode/smplform.py`.

Der Koerper traegt einen Fingerabdruck der Betas im Namen — zwei gleiche
Regler ergeben denselben, zwei verschiedene nie denselben. Gemessen und
abgelegt (`koerper/smplx/<name>.obj` und `.yaml`) wird er erst, wenn es jemand
braucht (`Smplvarianten.sicherstellen`, 25.11.2026): In der Antwort stand es
bis dahin vor jedem Zug, gemessen 13,5 s. `masse` ist leer, solange nicht
gemessen; der Browser holt sie ueber `…/<name>/masse/`.

Async mit eigenem Faden: Synchrone Ansichten teilen sich EINEN, dahinter
wartete der Zug auf jede andere Anfrage der Seite (wie `G9reglerzugapi`).
"""

import json
import logging

import torch
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.netzausgabe import Netzausgabe

logger = logging.getLogger('core')

__all__ = ['Smplformung']


class Smplformung:
    """Erzeugt eine geformte SMPL-Variante und liefert ihr Netz."""

    @staticmethod
    @csrf_exempt
    @require_POST
    async def formen(request):
        return await sync_to_async(Smplformung._formen, thread_sensitive=False)(request)

    @staticmethod
    def _formen(request):
        from GarmentCode.smplform import Smplform

        from ..daten.netzantwort import Netzantwort
        from ..daten.netzfeld import Netzfeld
        from ..dienste.smplfigur import Smplfiguren
        from ..dienste.smplvarianten import Smplvarianten
        from ..dienste.smplvariantenmasse import Smplvariantenmasse

        try:
            anfrage = json.loads(request.body.decode('utf-8') or '{}')
        # stumm gewollt: kaputtes JSON aus dem Browser heisst 'keine Angaben'
        except ValueError:
            anfrage = {}
        geschlecht = 'male' if str(anfrage.get('geschlecht')) == 'male' else 'female'
        groesse = anfrage.get('groesse', 0)
        fuelle = anfrage.get('fuelle', 0)
        weitere = [anfrage.get(schluessel, 0) for schluessel in Smplform.WEITERE_SCHLUESSEL]
        from SMPL.xmassregler import Smplxmassregler

        masse = {schluessel: anfrage.get(schluessel, 0) for schluessel in Smplxmassregler.SCHLUESSEL}

        try:
            daten = Smplvarianten.form(geschlecht, Smplvarianten.betas_aus_reglern(geschlecht, groesse, fuelle, weitere, masse))
        except (OSError, ValueError) as fehler:
            logger.warning('SMPL-Formung fehlgeschlagen (%s, %s/%s): %s', geschlecht, groesse, fuelle, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)

        punkte = daten['punkte']
        dreiecke = daten['dreiecke']
        antwort = {
            'name': daten['name'],
            'geschlecht': geschlecht,
            'smpl': True,
            'betas': daten['betas'],
            # Die Massregler lassen sich aus den Betas nicht zurueckrechnen
            # (Summe von Richtungen) — sie gehen so zurueck, wie sie kamen.
            'regler': {**Smplform.regler(geschlecht, daten['betas'][:Smplform.ANZAHL_BETAS]),
                       **{k: float(v or 0) for k, v in masse.items()}},
            'hoehe': float(daten['hoehe']),
            'masse': {k: float(v) for k, v in Smplvarianten.masse_abgelegt(daten['name']).items()},
            # Auch die geformte Variante bekommt ihr Skelett — sonst
            # verschwaende die Figur ihre Knochen beim ersten Reglerzug
            # (dieser Endpunkt loest den Netz-Endpunkt dann ab).
            'skelett': Smplfiguren.skelett(daten['name'], punkte),
        }
        if anfrage.get('nur') == 'form':
            Smplvariantenmasse.vorwaermen(geschlecht)
            antwort.update(punkte=Netzfeld.aus(punkte, torch.float32, genau=True), punktzahl=len(punkte))
            return Netzausgabe.antwort(antwort, request)
        antwort.update(
            punkte=punkte.tolist(),
            dreiecke=dreiecke.tolist(),
            # Auch die Variante bekommt Hautgewichte — sonst waere
            # ausgerechnet die geformte Figur die einzige, die beim
            # Abspielen starr bleibt.
            hautgewichte=Netzantwort.hautgewichte(Smplfiguren.haut(daten['name'], punkte)),
        )
        # UV auch fuer geformte Varianten — Betas aendern nur die Punktlage,
        # nie die Topologie (25.09.2026, „SMPL-X-Texturen").
        uv_felder = Smplfiguren.uv_felder(dreiecke)
        if uv_felder:
            antwort.update(uv_felder)
        return Netzausgabe.antwort(antwort, request)

    @staticmethod
    @require_GET
    def massregler(request, geschlecht):
        """Die benannten Massregler mit ihrer GEMESSENEN Wirkung (cm bei
        +-100) — `verfuegbar: false`, wenn die Ablage dieser Fassung fehlt."""
        from SMPL.xmassregler import Smplxmassregler

        from ..dienste.smplvarianten import Smplvarianten

        geschlecht = 'male' if geschlecht == 'male' else 'female'
        abgelegt = Smplvarianten.massregler(geschlecht)
        wirkung = abgelegt['wirkung'] if abgelegt else {}
        regler = [
            {'schluessel': schluessel, 'name': anzeige, 'links': links, 'rechts': rechts,
             'wirkung': wirkung.get(schluessel)}
            for schluessel, anzeige, _ziel, links, rechts in Smplxmassregler.REGLER
        ]
        return JsonResponse({'verfuegbar': bool(abgelegt), 'regler': regler})
