# -*- coding: utf-8 -*-
"""BVH als Text lesen und schreiben, glaetten, Effekte anwenden.

Aus core/api/retarget.py herausgeloest (Umbau 16.08.2026): Der Texteditor der
Bibliothek und die beiden Effekt-Endpunkte sind eine eigene Aufgabe — sie
arbeiten auf der Datei, nicht auf dem Retargeting.

UMBAU 27.08.2026 (Befund `freie-funktionen`): fuenf freie Funktionen, jetzt
Methoden von `Bvhtext`.
"""

import json
import logging
import os
import tempfile
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..atomic_write import AtomarSchreiber
from ..dienste.bvh_datei import BvhDatei
from ..dienste.bvhablage import Bvhablage
from ..dienste.retargetdaten import Retargetdaten
from ..projekt_temp import ProjektTemp
from ..safe_paths import SafePath, PfadAbgelehnt

logger = logging.getLogger(__name__)


class Bvhtext:
    """Der Texteditor der BVH-Bibliothek und die beiden Effekt-Endpunkte."""

    #: Koerpergroesse in Metern, wenn keine mitkommt.
    VORGABE_GROESSE = 1.68
    #: Glaettungsstaerke, wenn nur geglaettet wird.
    VORGABE_SIGMA = 2.0

    @staticmethod
    @csrf_exempt
    @require_POST
    def umsetzen(request):
        """Retarget direkt aus BVH-Text, ohne Datei in der Bibliothek.

        POST /api/character/retarget-bvh-text/
        JSON: { bvh_text: "HIERARCHY\\nROOT ...", body_height: 1.68,
                foot_correction: false, format: null }
        """
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        text = daten.get('bvh_text', '')
        if not text:
            return JsonResponse({'error': 'bvh_text is required'}, status=400)
        # `parse_bvh` will einen Pfad. Die Datei geht INS PROJEKT statt nach
        # System-Temp (Projektregel, siehe ProjektTemp).
        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.bvh', delete=False,
                dir=str(ProjektTemp.verzeichnis()), encoding='utf-8') as ablage:
            ablage.write(text)
            pfad = ablage.name
        try:
            return JsonResponse(Retargetdaten(
                pfad,
                float(daten.get('body_height', Bvhtext.VORGABE_GROESSE)),
                daten.get('format', None),
                bool(daten.get('foot_correction', False))).holen())
        finally:
            os.unlink(pfad)

    @staticmethod
    @csrf_exempt
    @require_POST
    def sichern(request):
        """Geaenderten BVH-Text in eine Datei schreiben.

        POST /api/character/save-bvh-text/
        JSON: { path: "/abs/pfad/datei.bvh", bvh_text: "HIERARCHY\\n..." }
        oder  { category, name, bvh_text }
        """
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        text = daten.get('bvh_text', '')
        if not text:
            return JsonResponse({'error': 'bvh_text required'}, status=400)
        ziel = Bvhtext._zielpfad(daten)
        if not ziel:
            return JsonResponse({'error': 'path or category+name required'},
                                status=400)
        # Pfadpruefung ueber SafePath. Vorher stand hier ein
        # String-Praefix-Vergleich (`str(sp).startswith(str(media))`) — den
        # besteht auch `<media>_evil\x.bvh`, weil "media_evil" mit "media"
        # beginnt. SafePath vergleicht Pfade, nicht Zeichenketten
        # (`is_relative_to`, gross/klein normalisiert).
        try:
            geprueft = SafePath.fuer_bvh().pruefe(ziel)
        except PfadAbgelehnt as fehler:
            return JsonResponse({'error': str(fehler)}, status=403)
        try:
            # Zeilenenden auf \n normalisieren (BVH-Dateien duerfen kein \r\n
            # haben); AtomarSchreiber ersetzt die Datei erst, wenn sie
            # vollstaendig auf der Platte liegt.
            sauber = text.replace('\r\n', '\n').replace('\r', '\n')
            AtomarSchreiber.text_schreiben(geprueft, sauber, zeilenende='\n')
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('save_bvh_text fehlgeschlagen: %s', geprueft)
            return JsonResponse({'error': str(fehler)}, status=500)
        return JsonResponse({'ok': True, 'path': str(geprueft)})

    @staticmethod
    def _zielpfad(daten):
        """Der angegebene Pfad — oder einer aus Kategorie und Name."""
        pfad = daten.get('path', '')
        if pfad:
            return pfad
        kategorie = daten.get('category', '')
        name = daten.get('name', '')
        if not (kategorie and name):
            return ''
        wurzel = Path(str(settings.HUMANBODY_BVH_DIR)).parent
        return str(wurzel / kategorie / ('%s.bvh' % name))

    # ---------------------------------------------------------------- Effekte

    @staticmethod
    @csrf_exempt
    @require_POST
    def glaetten(request):
        """Eine BVH-Datei glaetten und ueberschreiben.

        POST /api/retarget/smooth-bvh/  { category, name, sigma }
        """
        return Bvhtext._bearbeiten(request, nur_glaetten=True)

    @staticmethod
    @csrf_exempt
    @require_POST
    def effekte_sichern(request):
        """Glaettung und festgehaltene Wurzel anwenden und speichern.

        POST /api/retarget/save-bvh-effects/
        { category, name, sigma?, fixed_radius? }
        """
        return Bvhtext._bearbeiten(request, nur_glaetten=False)

    @staticmethod
    def _bearbeiten(request, nur_glaetten):
        """Gemeinsamer Weg beider Endpunkte (Umbau 15.08.2026).

        Vorher waren das zwei Funktionen mit zusammen 300 Zeilen, die sich zu
        neun Zehnteln glichen — inklusive der Pfadpruefung, die am 13.08.2026
        in BEIDEN nachgezogen werden musste.
        """
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        kategorie = daten.get('category', '')
        name = daten.get('name', '')
        if not kategorie or not name:
            return JsonResponse({'error': 'category + name required'},
                                status=400)
        # Die Pfadpruefung ist der Grund, warum diese beiden Endpunkte am
        # 13.08.2026 auffielen: `category='../../..'` landete in den
        # Produktivdaten, und am Ende wird die Datei UEBERSCHRIEBEN.
        pfad = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / kategorie
                                      / ('%s.bvh' % name))
        if pfad is None:
            return JsonResponse(
                {'error': 'Pfad liegt ausserhalb der BVH-Bibliothek'},
                status=403)
        if not pfad.is_file():
            # Kein voller Pfad in der Antwort — das waere eine Auskunft ueber
            # das Dateisystem. Er steht im Protokoll.
            logger.info('BVH nicht gefunden: %s', pfad)
            return JsonResponse({'error': 'BVH not found'}, status=404)
        return Bvhtext._anwenden(pfad, daten, nur_glaetten, kategorie, name)

    @staticmethod
    def _anwenden(pfad, daten, nur_glaetten, kategorie, name):
        sigma = (daten.get('sigma', Bvhtext.VORGABE_SIGMA) if nur_glaetten
                 else daten.get('sigma'))
        radius = None if nur_glaetten else daten.get('fixed_radius')
        try:
            bvh = BvhDatei(pfad)
            if sigma:
                bvh.glaetten(sigma)
            if radius:
                bvh.wurzel_festhalten(radius)
            if not bvh.angewandt:
                return JsonResponse({'error': 'No effects to apply'},
                                    status=400)
            bilder = bvh.speichern()
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('BVH-Bearbeitung fehlgeschlagen: %s/%s',
                             kategorie, name)
            return JsonResponse({'error': str(fehler)}, status=500)
        logger.info('BVH bearbeitet: %s/%s — %s, %d Frames', kategorie, name,
                    ', '.join(bvh.angewandt), bilder)
        antwort = {'ok': True, 'frames': bilder}
        if not nur_glaetten:
            antwort['applied'] = bvh.angewandt
        return JsonResponse(antwort)
