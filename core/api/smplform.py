# -*- coding: utf-8 -*-
"""Ein SMPL-Koerper in anderer Form: alle zehn Shape-Betas als Regler.

    POST /api/character/smpl-figur/formen/
         {geschlecht: 'male'|'female', groesse: -100..100, fuelle: -100..100,
          form3..form10: -100..100 (optional, Vollausstattung 25.09.2026)}
      -> {name, geschlecht, betas, punkte, dreiecke, hoehe, masse,
          regler, skelett, uv, uv_dreiecke, uv_ursprung}

WARUM ES DIESEN ENDPUNKT GIBT (Edgar, 06.09.2026: „der mann in Fall 2 soll
schlank sein, finde den Regler, dass du ihn schlank machst!"): Im
Online-Tool gibt es diesen Regler nicht — gemessen im laufenden Tool bleibt
der 3D-Koerper bei Bust 70 / Waist 55 / Hips 70 Punkt fuer Punkt derselbe
(142.500 Punkte, 172 cm). Formbar ist ein SMPL-Koerper nur ueber seine
Blendshapes; welcher Regler welches Beta mit welchem Vorzeichen bewegt,
steht gemessen in `GarmentCode/smplform.py`.

Der erzeugte Koerper wird abgelegt (`GarmentCode/koerper/smpl/<name>.obj`
und `.yaml`) und traegt einen Fingerabdruck der Betas im Namen — zwei
gleiche Regler ergeben dieselbe Datei, zwei verschiedene nie dieselbe.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger('core')

__all__ = ['Smplformung']


class Smplformung:
    """Erzeugt eine geformte SMPL-Variante und liefert ihr Netz."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def formen(request):
        from GarmentCode.smplform import Smplform

        from ..daten.netzantwort import Netzantwort
        from ..dienste.smplfigur import Smplfiguren
        from ..dienste.smplvarianten import Smplvarianten

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
            daten = Smplvarianten.aus_reglern(geschlecht, groesse, fuelle, weitere, masse)
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
            'punkte': punkte.tolist(),
            'dreiecke': dreiecke.tolist(),
            'hoehe': float(daten['hoehe']),
            'masse': {k: float(v) for k, v in daten['masse'].items()},
            # Auch die geformte Variante bekommt ihr Skelett — sonst
            # verschwaende die Figur ihre Knochen beim ersten Reglerzug
            # (dieser Endpunkt loest den Netz-Endpunkt dann ab).
            'skelett': Smplfiguren.skelett(daten['name'], punkte),
            # Auch die Variante bekommt Hautgewichte — sonst waere
            # ausgerechnet die geformte Figur die einzige, die beim
            # Abspielen starr bleibt.
            'hautgewichte': Netzantwort.hautgewichte(Smplfiguren.haut(daten['name'], punkte)),
        }
        # UV auch fuer geformte Varianten — Betas aendern nur die Punktlage,
        # nie die Topologie (25.09.2026, „SMPL-X-Texturen").
        uv_felder = Smplfiguren.uv_felder(dreiecke)
        if uv_felder:
            antwort.update(uv_felder)
        return JsonResponse(antwort)

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
