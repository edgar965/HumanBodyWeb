# -*- coding: utf-8 -*-
"""Einstellungsseite des BVH Studios — Vorgaben fuer Pfade, Bildrate, Export.

Aus ``core/api/seiten.py`` herausgeloest (Umbau 17.08.2026). Dort war es eine
freie Funktion zwischen zwoelf Einzeilern; die Vorgabewerte standen als
``prefs.setdefault(...)``-Kette mitten im Ablauf.

Jetzt eine Klasse mit den Vorgaben als Klassenfeld: Wer einen Wert ergaenzt,
schreibt eine Zeile in ``VORGABEN`` statt eine in den Ablauf. Die Pfade haengen
an ``settings`` und werden deshalb erst beim Aufruf gebildet, nicht beim Import.
"""

from pathlib import Path

from django.conf import settings
from django.views.generic import TemplateView


class BvhStudioEinstellungenSeite(TemplateView):
    """Zeigt die gespeicherten Vorgaben; gespeichert wird ueber die API."""

    template_name = 'settings_bvh_studio.html'

    #: Feste Vorgaben ohne Pfadbezug.
    VORGABEN = {
        'studio_default_model': 'Rig2',
        'studio_body_type': 'Female_Caucasian',
        'studio_fps': '30',
        'studio_zoom': '100',
        'studio_export_resolution': '1080',
        'studio_export_crf': '18',
    }

    def get_context_data(self, **kwargs):
        from ..models import AppSettings
        prefs = AppSettings.load().ui_prefs or {}
        for name, wert in self.VORGABEN.items():
            prefs.setdefault(name, wert)
        for name, wert in self._pfadvorgaben().items():
            prefs.setdefault(name, wert)
        return dict(super().get_context_data(**kwargs), prefs=prefs)

    @staticmethod
    def _pfadvorgaben():
        """Vorgabepfade aus den Einstellungen — nicht eingetippt, abgeleitet."""
        bvh = Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data' / 'animations' / 'bvh'
        return {
            'studio_bvh_input': str(bvh),
            'studio_bvh_output': str(bvh / 'Results'),
            'studio_video_output': str(Path(settings.MEDIA_ROOT) / 'output'),
            'studio_project_path': str(Path(settings.TOOLS_ROOT) / 'HumanBody'
                                       / 'data' / 'studio_projects'),
        }


#: Review 16.08.2026: Hier wurde zusaetzlich eine feste Liste von sechs
#: Modellnamen als ``models`` uebergeben — ``settings_bvh_studio.html`` liest
#: den Namen nirgends. Das Ganze stand in einem ``try/except``, in dem nichts
#: werfen konnte, sodass auch der Ersatzzweig unerreichbar war.
#: Der Name muss gesetzt werden: ``as_view()`` liefert eine Funktion, die
#: schlicht ``view`` heisst — Stapelspuren und Werkzeuge, die Routen ueber
#: ``callback.__name__`` unterscheiden, koennten sie sonst nicht benennen.
bvh_studio_settings_page = BvhStudioEinstellungenSeite.as_view()
bvh_studio_settings_page.__name__ = 'bvh_studio_settings_page'
