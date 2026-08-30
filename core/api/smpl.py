# -*- coding: utf-8 -*-
"""SMPL-Koerper und SMPL-Kleidungsbibliothek.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

UMBAU 27.08.2026 (Befund `freie-funktionen`): sieben freie Funktionen, keine
Klasse. Sie stehen jetzt als Methoden in `Smplendpunkte`; das dreimal
ausgeschriebene „Netz als base64-Bloecke" liegt in `_netzantwort`.
"""

import json
import logging

from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.netzantwort import Netzantwort
from ..daten.smplvorgaben import Smplvorgaben
from ..daten.stoffantwort import Stoffantwort
from ..dienste.charakterdaten import Charakterdaten
from ..models import AppSettings

logger = logging.getLogger(__name__)


class Smplendpunkte:
    """Einstellungen, Koerpernetz und Kleiderbestand der SMPL-Seite."""

    #: Weitergereicht — die Listen stehen in `Smplvorgaben`, weil dort auch
    #: geprueft wird, was hineindarf.
    GESCHLECHTER = Smplvorgaben.GESCHLECHTER
    BETAS = Smplvorgaben.BETAS
    #: Abstand des Stoffs zur Haut in Metern.
    VORGABE_ABSTAND = 0.006
    #: Steifigkeit des Stoffs (0…1).
    VORGABE_STEIFE = 0.5
    #: Stofffarbe (r, g, b) als Anteile 0…1.
    VORGABE_FARBE = (0.30, 0.50, 0.40)

    # --------------------------------------------------------- Einstellungen

    @staticmethod
    @require_GET
    def einstellungen(request):
        """Die gespeicherten Vorgaben des SMPL-Koerpers."""
        gespeichert = AppSettings.load()
        antwort = {
            'gender': gespeichert.smpl_default_gender,
            'betas': Smplendpunkte._betas(gespeichert.smpl_default_betas),
            'opacity': gespeichert.smpl_default_opacity,
            'color': gespeichert.smpl_default_color,
            'wireframe': gespeichert.smpl_default_wireframe,
            'xoffset': gespeichert.smpl_default_xoffset,
            'humanbody_preset': gespeichert.smpl_default_humanbody_preset,
        }
        if gespeichert.smpl_default_scene:
            try:
                antwort['scene'] = json.loads(gespeichert.smpl_default_scene)
            except (json.JSONDecodeError, TypeError):
                logger.debug('uebergangen', exc_info=True)
        return JsonResponse(antwort)

    @staticmethod
    def _betas(text):
        """Zehn Formparameter aus einer Komma-Zeichenkette."""
        werte = [0.0] * Smplendpunkte.BETAS
        try:
            for platz, roh in enumerate(text.split(',')[:Smplendpunkte.BETAS]):
                werte[platz] = float(roh.strip())
        except (ValueError, IndexError):
            logger.debug('uebergangen', exc_info=True)
        return werte

    @staticmethod
    @csrf_exempt
    @require_POST
    def einstellungen_sichern(request):
        """Koerper- und Szenenvorgaben der SMPL-Seite speichern."""
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                status=400)
        gespeichert = AppSettings.load()
        # Welche Felder es gibt und was fuer sie gilt, steht in
        # `Smplvorgaben` — hier standen bis zum 30.08.2026 sieben `if`-Bloecke
        # mit ihren Grenzen mitten im Rumpf.
        Smplvorgaben.uebernehmen(daten, gespeichert)
        gespeichert.save()
        return JsonResponse({'ok': True})

    # ------------------------------------------------------------ Koerpernetz

    @staticmethod
    def _netzantwort(netz, **zusatz):
        """Vertices, Faces und Normalen als base64-Bloecke."""
        antwort = {
            'vertices': Netzantwort.feld(netz['vertices'], 'vertices'),
            'faces': Netzantwort.feld(netz['faces'], 'faces'),
            'normals': Netzantwort.feld(netz['normals'], 'normals'),
        }
        antwort.update(zusatz)
        return antwort

    @staticmethod
    @require_GET
    def koerpernetz(request):
        """Das SMPL-Koerpernetz als base64-JSON.

        `gender`: female/male/neutral (Vorgabe female)
        `betas`: Kommaliste, z. B. "1.5,-0.3,0,0,0,0,0,0,0,0"
        """
        geschlecht = request.GET.get('gender', 'female')
        roh = request.GET.get('betas', '')
        betas = None
        if roh:
            try:
                betas = [float(x) for x in roh.split(',')]
            except ValueError:
                return JsonResponse({'error': 'Invalid betas format'},
                                    status=400)
        try:
            erzeuger = Charakterdaten.smpl_koerpergenerator()
            netz = erzeuger.generate(gender=geschlecht, betas=betas)
        except FileNotFoundError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(Smplendpunkte._netzantwort(
            netz, vertex_count=netz['vertex_count'],
            face_count=netz['face_count'], gender=geschlecht))

    # --------------------------------------------------------- Kleiderbestand

    @staticmethod
    @require_GET
    def kleiderbestand(request):
        """Der SMPL-Kleiderkatalog, nach Kategorie gruppiert."""
        return JsonResponse(Charakterdaten.smpl_bibliothek().get_catalog())

    @staticmethod
    @require_GET
    def kleidernetz(request):
        """Das Netz EINES SMPL-Kleides als base64-JSON."""
        kennung = request.GET.get('garment_id', '')
        if not kennung:
            return JsonResponse({'error': 'garment_id required'}, status=400)
        try:
            netz = Charakterdaten.smpl_bibliothek().get_garment_mesh(kennung)
        except Exception as fehler:
            logger.error('Error loading SMPL garment %s: %s', kennung, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        return JsonResponse(Smplendpunkte._netzantwort(
            netz, garment_id=kennung,
            vertex_count=len(netz['vertices']) // 3,
            face_count=len(netz['faces']) // 3))

    @staticmethod
    @require_GET
    def kleid_anpassen(request):
        """Ein SMPL-Kleid an den Projektkoerper anpassen.

        `garment_id` — Kennung aus der SmplGarmentLibrary
        `body_type`  — z. B. 'Female_Caucasian'
        `offset`     — Abstand zur Oberflaeche in Metern
        `stiffness`  — Steifigkeit 0…1
        `color_r/g/b`, `morph_*`, `meta_*`
        """
        kennung = request.GET.get('garment_id', '')
        if not kennung:
            return JsonResponse({'error': 'garment_id required'}, status=400)
        try:
            roh = Charakterdaten.smpl_bibliothek().get_garment_mesh_raw(kennung)
        except Exception as fehler:
            logger.error('Error loading SMPL garment raw %s: %s',
                         kennung, fehler)
            return JsonResponse({'error': str(fehler)}, status=500)
        # Koerper aus der Anfrage — derselbe Weg wie ueberall
        # (`Charakterdaten.koerper_aus`); der Reglerblock stand hier ein
        # viertes Mal.
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute body mesh'},
                                status=500)
        farbe = Smplendpunkte._farbe(request.GET)
        from GarmentFitter import fit_garment
        ergebnis = fit_garment(
            roh['vertices'], roh['faces'], koerper.vertices,
            body_faces=Charakterdaten.netzdaten(koerper.geschlecht).faces,
            offset=float(request.GET.get('offset',
                                         Smplendpunkte.VORGABE_ABSTAND)),
            stiffness=float(request.GET.get('stiffness',
                                            Smplendpunkte.VORGABE_STEIFE)),
            color=farbe, coordinate_system='smpl')
        if ergebnis is None:
            return JsonResponse({'error': 'Fitting failed'}, status=500)
        return JsonResponse(Stoffantwort.aus(ergebnis, koerper.vertices,
                                             koerper.geschlecht, farbe=farbe,
                                             garment_id=kennung))

    @classmethod
    def _farbe(cls, werte):
        r, g, b = cls.VORGABE_FARBE
        return (float(werte.get('color_r', r)), float(werte.get('color_g', g)),
                float(werte.get('color_b', b)))

    @staticmethod
    @require_GET
    def vorschaubild(request, garment_path):
        """Das Vorschaubild eines SMPL-Kleides."""
        kennung = garment_path.rstrip('/')
        try:
            bild = Charakterdaten.smpl_bibliothek().get_thumbnail(kennung)
        except Exception as fehler:
            return HttpResponseNotFound('Garment not found: %s' % fehler)
        if bild is None:
            return HttpResponseNotFound('No thumbnail')
        return HttpResponse(bild, content_type='image/png')
