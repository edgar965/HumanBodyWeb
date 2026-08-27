# -*- coding: utf-8 -*-
"""Der CharMorph-Bestand: Koerpertypen, Kleider, Frisuren.

Aus `core/api/system.py` herausgeloest (27.08.2026, Befunde `freie-funktionen`
und `klassen-je-datei`). Dort standen sechs freie Funktionen aus ZWEI Themen in
einer Datei: die Einstellungen der Anwendung und der Bestand eines fremden
Plugins. Die drei Bestandsfunktionen rechneten ausserdem dreimal denselben
Pfad aus (`TOOLS_ROOT/tools/CharMorphPlugin/data/characters/mb_female/…`) und
holten sich jede fuer sich `import os as _os`.
"""

import json
import logging
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


class CharmorphBestand:
    """Was das CharMorph-Plugin an Vorgaben und Bestand mitbringt."""

    #: Die Figur, deren Bestand die Oberflaeche anbietet.
    FIGUR = 'mb_female'
    #: Vorgabefarbe eines Haares, wenn die Datei keine nennt.
    FARBE_VORGABE = [0.5, 0.3, 0.1]
    #: Vorgabe-Melaninwert.
    MELANIN_VORGABE = 0.5

    # -------------------------------------------------------------- Pfade

    @staticmethod
    def wurzel():
        return os.path.join(str(settings.TOOLS_ROOT), 'tools',
                            'CharMorphPlugin', 'data')

    @classmethod
    def figurordner(cls, unterordner):
        """`…/data/characters/mb_female/<unterordner>`."""
        return os.path.join(cls.wurzel(), 'characters', cls.FIGUR,
                            unterordner)

    # -------------------------------------------------------- Koerpertypen

    @staticmethod
    @require_GET
    def koerpertypen(request):
        """Die Koerpertyp-Vorgaben von CharMorph."""
        ordner = CharmorphBestand.figurordner('presets')
        vorgaben = []
        if os.path.isdir(ordner):
            for dateiname in sorted(os.listdir(ordner)):
                if not dateiname.endswith('.json'):
                    continue
                eintrag = CharmorphBestand._vorgabe(ordner, dateiname)
                if eintrag:
                    vorgaben.append(eintrag)
        return JsonResponse({'presets': vorgaben})

    @staticmethod
    def _vorgabe(ordner, dateiname):
        name = (dateiname.replace('.json', '').replace('type_', '')
                .replace('specialtype_', 'special_'))
        try:
            with open(os.path.join(ordner, dateiname)) as datei:
                daten = json.load(datei)
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)
            return None
        return {
            'name': name,
            'label': name.replace('_', ' ').title(),
            'meta': daten.get('metaproperties', {}),
            'structural': daten.get('structural', {}),
        }

    # -------------------------------------------------------------- Kleider

    @staticmethod
    @require_GET
    def kleider(request):
        """Der Kleiderbestand von CharMorph (Ordner mit `config.yaml`)."""
        try:
            import yaml
        # stumm gewollt: Die Antwort nennt die Ursache („pyyaml not
        # installed") und steht in der Oberflaeche.
        except ImportError:
            return JsonResponse({'assets': [],
                                 'error': 'pyyaml not installed'})
        ordner = CharmorphBestand.figurordner('assets')
        stuecke = []
        if os.path.isdir(ordner):
            for eintrag in sorted(os.listdir(ordner)):
                stueck = CharmorphBestand._kleid(yaml, ordner, eintrag)
                if stueck:
                    stuecke.append(stueck)
        return JsonResponse({'assets': stuecke})

    @staticmethod
    def _kleid(yaml, ordner, eintrag):
        pfad = os.path.join(ordner, eintrag)
        if eintrag.endswith('.blend') and not os.path.isdir(pfad):
            return {'name': eintrag.replace('.blend', ''), 'category': 'Other',
                    'tags': [], 'fitting': 'soft', 'parameters': {},
                    'material_presets': []}
        einstellung = os.path.join(pfad, 'config.yaml')
        if not os.path.isdir(pfad) or not os.path.isfile(einstellung):
            return None
        try:
            with open(einstellung) as datei:
                werte = yaml.safe_load(datei) or {}
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)
            return None
        return {
            'name': eintrag,
            'category': werte.get('category', 'Other'),
            'tags': werte.get('tags', []),
            'fitting': werte.get('fitting', 'soft'),
            'parameters': werte.get('parameters', {}),
            'material_presets': list(werte.get('material_presets', {}).keys()),
        }

    # ------------------------------------------------------------- Frisuren

    @staticmethod
    @require_GET
    def frisuren(request):
        """Frisuren (`.npz`) und die Haarfarben von CharMorph."""
        ordner = CharmorphBestand.figurordner('hairstyles')
        frisuren = []
        if os.path.isdir(ordner):
            for dateiname in sorted(os.listdir(ordner)):
                if not dateiname.endswith('.npz'):
                    continue
                name = dateiname.replace('.npz', '')
                frisuren.append({
                    'name': name,
                    'label': (name.replace('_', ' ').replace('1', ' 1')
                              .strip().title()),
                    'file': dateiname,
                })
        return JsonResponse({'hairstyles': frisuren,
                             'colors': CharmorphBestand._haarfarben()})

    @staticmethod
    def _haarfarben():
        datei = os.path.join(CharmorphBestand.wurzel(), 'hair_colors.yaml')
        if not os.path.isfile(datei):
            return {}
        farben = {}
        try:
            import yaml
            with open(datei) as offen:
                roh = yaml.safe_load(offen)
            for name, werte in (roh or {}).items():
                if isinstance(werte, dict):
                    farben[name] = {
                        'viewport_color': werte.get(
                            'viewport_color',
                            CharmorphBestand.FARBE_VORGABE),
                        'melanin': werte.get('melanin',
                                             CharmorphBestand.MELANIN_VORGABE),
                    }
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)
        return farben
