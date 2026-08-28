# -*- coding: utf-8 -*-
"""Stoffvorlagen der Kleidung: Bereiche, gespeicherte Voreinstellungen.

Aus core/api/kleidung.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): fuenf freie Funktionen und eine
Modultabelle. Die Pfadpruefung („normpath, dann Praefixvergleich") stand
zweimal da und kommt jetzt aus `daten/modellpfad.Modellpfad`.
"""

import json
import logging
import os
import re

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core.cloth import (TEMPLATE_TYPES, PRIMITIVE_TYPES,
                                  BUILDER_REGIONS)

from ..daten.modellpfad import Modellpfad
from ..daten.anfragerumpf import Anfragerumpf

logger = logging.getLogger('core')


class Kleidungsvorlagen:
    """Bereiche und gespeicherte Vorlagen des Stoffbaus."""

    #: Welche Vorlage in welchen Kategorieordner gehoert.
    KATEGORIE_JE_VORLAGE = {
        'TPL_TSHIRT': 'Top', 'TPL_DRESS': 'Top',
        'TPL_PANTS': 'Pants', 'TPL_SKIRT': 'Pants',
    }
    #: Die zwei Kategorien, die es gibt.
    KATEGORIEN = ('Top', 'Pants')

    @staticmethod
    @require_GET
    def bereiche(request):
        """Alle Stoffoptionen: Vorlagen, Grundformen, Baubereiche."""
        return JsonResponse({
            'templates': [{'key': k, 'label': v['label'],
                           'color': list(v['color'])}
                          for k, v in TEMPLATE_TYPES.items()],
            'primitives': [{'key': k, 'label': v['label'],
                            'color': list(v['color'])}
                           for k, v in PRIMITIVE_TYPES.items()],
            'builder_regions': [{'key': k, 'label': k.replace('_', ' ').title(),
                                 'color': list(v['color'])}
                                for k, v in BUILDER_REGIONS.items()],
        })

    @classmethod
    def _ordner(cls, kategorie):
        """Der Vorlagenordner einer Kategorie — wird angelegt, wenn er fehlt."""
        pfad = (settings.HUMANBODY_ASSETS_INSTANCE_DIR / kategorie
                / 'clothFromTemplate')
        pfad.mkdir(parents=True, exist_ok=True)
        return pfad

    @staticmethod
    @require_GET
    def liste(request):
        """Alle Vorlagen einer Kategorie (Top oder Pants)."""
        kategorie = request.GET.get('category', '')
        if kategorie not in Kleidungsvorlagen.KATEGORIEN:
            return JsonResponse({'error': 'category must be Top or Pants'},
                                status=400)
        vorlagen = []
        for datei in sorted(Kleidungsvorlagen._ordner(kategorie).glob('*.json')):
            try:
                daten = json.loads(datei.read_text(encoding='utf-8'))
                bezeichnung = daten.get('name', datei.stem)
            except (json.JSONDecodeError, IOError):
                logger.warning('Kleidervorlage %s nicht lesbar — Dateiname als '
                               'Bezeichnung', datei, exc_info=True)
                bezeichnung = datei.stem
            vorlagen.append({'name': datei.stem, 'label': bezeichnung})
        return JsonResponse({'presets': vorlagen})

    @staticmethod
    @csrf_exempt
    @require_POST
    def sichern(request):
        """Eine Stoffvorlage speichern."""
        name, daten, fehler = Anfragerumpf.name_und_daten(request)
        if fehler:
            return fehler
        vorlage = daten.get('template', '')
        kategorie = Kleidungsvorlagen.KATEGORIE_JE_VORLAGE.get(vorlage)
        if not kategorie:
            return JsonResponse({'error': 'Unknown template: %s' % vorlage},
                                status=400)
        sauber = re.sub(r'[^\w\s\-]', '', name).strip()
        ordner = Kleidungsvorlagen._ordner(kategorie)
        pfad = Modellpfad.geprueft(ordner, sauber, '.json') if sauber else None
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        # Der ANGEZEIGTE Name bleibt stehen; der Dateiname ist die bereinigte
        # Fassung.
        daten['name'] = name
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei, indent=2, ensure_ascii=False)
        return JsonResponse({'ok': True, 'filename': '%s.json' % sauber,
                             'category': kategorie})

    @staticmethod
    @require_GET
    def vorlage(request, category, name):
        """EINE Stoffvorlage laden."""
        if category not in Kleidungsvorlagen.KATEGORIEN:
            return JsonResponse({'error': 'Invalid category'}, status=400)
        ordner = Kleidungsvorlagen._ordner(category)
        pfad = Modellpfad.geprueft(ordner, name, '.json')
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('Preset not found: %s/%s'
                                        % (category, name))
        with open(pfad, 'r', encoding='utf-8') as datei:
            return JsonResponse(json.load(datei))
