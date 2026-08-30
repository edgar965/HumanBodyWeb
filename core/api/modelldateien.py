# -*- coding: utf-8 -*-
"""Gespeicherte Modelle und Frisuren auflisten, lesen, schreiben.

Aus core/api/netz.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `doppelcode`): sechs freie
Funktionen. Die Pfadpruefung („kein Schraegstrich, kein `..`, danach `normpath`
und ein Praefixvergleich") stand VIERMAL wortgleich da; sie steht jetzt einmal
in `daten/modellpfad.py` — dieselbe Frage stellt
`api/studio_projekt.py` fuer Szenendateien.
"""

import json
import logging
import os
import re

from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.modellpfad import Modellpfad
from ..daten.anfragerumpf import Anfragerumpf

logger = logging.getLogger('core')


class Modelldateien:
    """Modellvorgaben (.json), Szenen (.scene.json) und Frisuren (.glb)."""

    #: Haarfarben der Oberflaeche — Name → RGB im Viewport.
    HAARFARBEN = {
        'Silken Black':       {'viewport': (0.02, 0.02, 0.02)},
        'Dark Brown':         {'viewport': (0.08, 0.04, 0.02)},
        'Cocoa Brown':        {'viewport': (0.25, 0.12, 0.05)},
        'Light Golden Brown': {'viewport': (0.7, 0.5, 0.25)},
        'Honey Blonde':       {'viewport': (0.6, 0.26, 0.08)},
        'Light Blonde':       {'viewport': (0.6, 0.3, 0.05)},
        'Auburn':             {'viewport': (0.5, 0.2, 0.05)},
        'Natural Black':      {'viewport': (0.05, 0.05, 0.05)},
        'Burgundy':           {'viewport': (0.13, 0.085, 0.08)},
        'Plum':               {'viewport': (0.33, 0.17, 0.05)},
    }

    #: Endung einer Szenendatei (eine Modelldatei endet nur auf `.json`).
    SZENE = '.scene.json'

    # --------------------------------------------------------- Verzeichnisse

    @staticmethod
    def _modellordner():
        return str(settings.HUMANBODY_MODELS_DIR)

    @staticmethod
    def _frisurordner():
        return os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')

    # -------------------------------------------------------------- Listen

    @staticmethod
    @require_GET
    def dateiliste(request):
        """ALLE Modell- und Szenendateien mit Groesse und Datum."""
        ordner = Modelldateien._modellordner()
        eintraege = []
        if os.path.isdir(ordner):
            for name in sorted(os.listdir(ordner)):
                if not name.endswith('.json'):
                    continue
                pfad = os.path.join(ordner, name)
                if not os.path.isfile(pfad):
                    continue
                eintraege.append(Modelldateien._eintrag(pfad, name))
        return JsonResponse({'files': eintraege})

    @staticmethod
    def _eintrag(pfad, dateiname):
        szene = dateiname.endswith(Modelldateien.SZENE)
        name = (dateiname[:-len(Modelldateien.SZENE)] if szene
                else dateiname[:-5])
        angaben = os.stat(pfad)
        eintrag = {
            'name': name, 'filename': dateiname,
            'type': 'scene' if szene else 'model',
            'size': angaben.st_size, 'modified': int(angaben.st_mtime),
        }
        try:
            with open(pfad, 'r', encoding='utf-8') as datei:
                daten = json.load(datei)
            eintrag['label'] = daten.get('name', name)
            if szene:
                eintrag['character_count'] = len(daten.get('characters', []))
        except (json.JSONDecodeError, IOError):
            logger.warning('%s nicht lesbar — Dateiname als Bezeichnung',
                           pfad, exc_info=True)
            eintrag['label'] = name
        return eintrag

    @staticmethod
    @require_GET
    def modellliste(request):
        """Nur die Modellvorgaben, ohne Szenen."""
        ordner = Modelldateien._modellordner()
        vorgaben = []
        if os.path.isdir(ordner):
            for dateiname in sorted(os.listdir(ordner)):
                if (not dateiname.endswith('.json')
                        or dateiname.endswith(Modelldateien.SZENE)):
                    continue
                name = dateiname[:-5]
                try:
                    with open(os.path.join(ordner, dateiname), 'r',
                              encoding='utf-8') as datei:
                        json.load(datei)      # nur die Lesbarkeit pruefen
                except (json.JSONDecodeError, IOError):
                    logger.warning('%s nicht lesbar — Dateiname als '
                                   'Bezeichnung', dateiname, exc_info=True)
                vorgaben.append({'name': name, 'label': name})
        return JsonResponse({'presets': vorgaben})

    # ---------------------------------------------------------- Eine Datei

    @staticmethod
    @require_GET
    def modell(request, name):
        """Der Inhalt EINER Modellvorgabe."""
        pfad = Modellpfad.geprueft(Modelldateien._modellordner(),
                                   name, '.json')
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('Preset not found: %s' % name)
        with open(pfad, 'r', encoding='utf-8') as datei:
            return JsonResponse(json.load(datei))

    @staticmethod
    @csrf_exempt
    @require_POST
    def modell_sichern(request):
        """Eine Modellvorgabe schreiben."""
        name, daten, fehler = Anfragerumpf.name_und_daten(request)
        if fehler:
            return fehler
        # Nur Buchstaben, Ziffern, Leerzeichen, Binde- und Unterstriche.
        sauber = re.sub(r'[^\w\s\-]', '', name).strip()
        ordner = Modelldateien._modellordner()
        pfad = (Modellpfad.geprueft(ordner, sauber, '.json')
                if sauber else None)
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        os.makedirs(ordner, exist_ok=True)
        # Das Feld `name` in der Datei muss zum Dateinamen passen.
        daten['name'] = sauber
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei, indent=2, ensure_ascii=False)
        return JsonResponse({'ok': True, 'filename': '%s.json' % sauber})

    # ----------------------------------------------------------- Frisuren

    @staticmethod
    @require_GET
    def frisuren(request):
        """Alle Frisuren (GLB-Dateien) samt Farbtabelle."""
        ordner = Modelldateien._frisurordner()
        stile = []
        if os.path.isdir(ordner):
            for dateiname in sorted(os.listdir(ordner)):
                if not dateiname.endswith('.glb'):
                    continue
                name = dateiname[:-4]
                stile.append({
                    'name': name,
                    'label': name.replace('_', ' ').title(),
                    'url': '/api/character/hairstyle/%s/' % name,
                })
        return JsonResponse({
            'hairstyles': stile,
            'colors': {name: wert['viewport']
                       for name, wert in Modelldateien.HAARFARBEN.items()},
        })

    @staticmethod
    def frisur_glb(request, name):
        """Die GLB-Datei EINER Frisur."""
        pfad = Modellpfad.geprueft(Modelldateien._frisurordner(),
                                   name, '.glb')
        if pfad is None:
            return JsonResponse({'error': 'Invalid name'}, status=400)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('Hairstyle not found: %s' % name)
        return FileResponse(open(pfad, 'rb'),
                            content_type='model/gltf-binary',
                            filename='%s.glb' % name)
