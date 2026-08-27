# -*- coding: utf-8 -*-
"""Kleidung: Garderobe, Stoffbau, Anpassung.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `globaler-zustand`): drei freie
Funktionen und ZWEI tote Modulvariablen — `_TPL_CATEGORY` (steht seit dem
16.08.2026 in `api/kleidungsvorlagen.py`) und `_garment_library = None` (der
Zwischenspeicher liegt seit dem 18.08.2026 in `dienste/kleiderbibliothek.py`).
Beide wurden hier von niemandem mehr gelesen.
"""

import json
import logging
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from humanbody_core.cloth import generate_cloth

from ..daten.kleidungsregler import Kleidungsregler
from ..daten.stoffantwort import Stoffantwort
from ..dienste.charakterdaten import Charakterdaten
from ..dienste.kleiderbibliothek import Kleiderbibliothek
from ..dienste.kleidungsanpassung import Kleidungsanpassung

logger = logging.getLogger(__name__)


class Kleidung:
    """Garderobe listen, Stoff bauen, eine Vorlage anpassen."""

    #: Die Kategorieordner der Garderobe.
    KATEGORIEN = frozenset({'Tops', 'Bottoms', 'Skirts', 'Full', 'Underwear',
                            'Shoes', 'Accessories', 'Other'})

    @staticmethod
    @require_GET
    def garderobe(request):
        """Der Garderobenbestand — aus dem Manifest oder vom Dateisystem."""
        glb_ordner = str(settings.HUMANBODY_ASSETS_GLB_DIR)
        manifest = os.path.join(glb_ordner, 'manifest.json')
        if os.path.isfile(manifest):
            with open(manifest, 'r', encoding='utf-8') as datei:
                inhalt = json.load(datei)
            for stueck in inhalt.get('assets', []):
                stueck['glb_url'] = '/api/character/asset/%s/' % stueck['name']
            return JsonResponse(inhalt)
        return JsonResponse({'assets': Kleidung._aus_verzeichnis(glb_ordner)})

    @staticmethod
    def _aus_verzeichnis(glb_ordner):
        """Rueckfall ohne Manifest: die .blend-Ordner durchsehen."""
        wurzel = str(settings.HUMANBODY_ASSETS_DIR)
        stuecke = []
        if not os.path.isdir(wurzel):
            return stuecke
        for kategorie in sorted(os.listdir(wurzel)):
            ordner = os.path.join(wurzel, kategorie)
            if not (os.path.isdir(ordner)
                    and kategorie in Kleidung.KATEGORIEN):
                continue
            for name in sorted(os.listdir(ordner)):
                if not os.path.isdir(os.path.join(ordner, name)):
                    continue
                stuecke.append({
                    'name': name,
                    'category': kategorie,
                    'glb_url': '/api/character/asset/%s/' % name,
                    'has_glb': os.path.isfile(
                        os.path.join(glb_ordner, '%s.glb' % name)),
                })
        return stuecke

    # ------------------------------------------------------------- Stoffbau

    @staticmethod
    @require_GET
    def stoff(request):
        """Ein Stoffnetz bauen und als base64 zurueckgeben.

        Gemeinsam: body_type, gender, morph_*
        Vorlage (Vorgabe): method=template, template=TPL_TSHIRT, tightness,
            segments, top_extend, bottom_extend
        Baubereich:        method=builder, region=TOP, looseness
        Grundform:         method=primitive, prim_type=PRIM_SKIRT, segments,
            length, flare
        """
        art = request.GET.get('method', 'template')
        # Koerper aus der Anfrage: derselbe Weg wie in allen anderen
        # Endpunkten (`Charakterdaten.koerper_aus`). Der Reglerblock stand hier
        # ein viertes Mal.
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute mesh'},
                                status=500)
        # Nur der Baubereich braucht die Flaechen des Koerpers.
        flaechen = None
        if art == 'builder':
            netz = Charakterdaten.netzdaten(koerper.geschlecht)
            if netz.faces is not None and netz.faces.ndim == 2:
                flaechen = netz.faces
        try:
            ergebnis = generate_cloth(koerper.vertices, faces=flaechen,
                                      **Kleidung._bauwerte(request.GET, art))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        if ergebnis is None:
            return JsonResponse({'error': 'Failed to generate cloth'},
                                status=400)
        return JsonResponse(Stoffantwort.aus(ergebnis, koerper.vertices,
                                             koerper.geschlecht))

    @staticmethod
    def _bauwerte(werte, art):
        return {
            'method': art,
            'template': werte.get('template'),
            'region': werte.get('region'),
            'tightness': (float(werte['tightness'])
                          if 'tightness' in werte else None),
            'looseness': float(werte.get('looseness', 0.5)),
            'segments': int(werte.get('segments', 32)),
            'top_extend': float(werte.get('top_extend', 0)),
            'bottom_extend': float(werte.get('bottom_extend', 0)),
            'prim_type': werte.get('prim_type'),
            'length': float(werte.get('length', 0.5)),
            'flare': float(werte.get('flare', 0.3)),
        }

    # ------------------------------------------------------------ Anpassung

    @staticmethod
    @csrf_exempt
    def anpassen(request):
        """Eine Kleidungsvorlage an den aktuellen Koerper anpassen.

        Bis zum Umbau am 15.08.2026 standen hier 151 Zeilen: der Koerper wurde
        von Hand gerechnet (obwohl Charakterdaten.koerper_aus genau das kann),
        acht Regler einzeln gelesen, drei Anpassungszweige aufgeschrieben (zwei
        davon buchstabengleich) und die Knochengewichte per KD-Baum bestimmt
        (wie in zwei anderen Endpunkten auch). Das liegt jetzt in
        Kleidungsanpassung und Kleidungsregler.

        Abfrage: garment_id, body_type, offset, stiffness, min_dist,
        crotch_floor, lift, crotch_depth, color_r/g/b, fit_mode, morph_*, meta_*
        """
        kennung = request.GET.get('garment_id', '')
        if not kennung:
            return JsonResponse({'error': 'garment_id required'}, status=400)
        vorlage = Kleiderbibliothek.holen().get_template(kennung)
        if vorlage is None or vorlage.vertices is None:
            return JsonResponse({'error': 'Garment not found: %s' % kennung},
                                status=404)
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute body mesh'},
                                status=500)
        regler = Kleidungsregler.aus_parametern(request.GET, vorlage)
        anpassung = Kleidungsanpassung(vorlage, koerper)
        huelle = Kleidungsanpassung.huelle_aus_anfrage(request)
        if anpassung.anpassen(regler, huelle) is None:
            return JsonResponse({'error': 'Fitting failed'}, status=500)
        return JsonResponse(anpassung.als_antwort(kennung, regler))
