# -*- coding: utf-8 -*-
"""Seitenaufrufe ohne Fachlogik — Vorlage rendern, sonst nichts.

Herausgeloest aus core/character_api.py (Umbau 15.08.2026). Die Datei hatte
6.495 Zeilen und 110 Endpunkte; die Themen darin waren nur durch Reihenfolge
getrennt.

UMBAU 17.08.2026: Hier standen SECHZEHN freie Funktionen und keine einzige
Klasse — der Spitzenbefund des Werkzeugs `freie-funktionen`. Dreizehn davon
waren wortgleich

    def x(request):
        return render(request, 'x.html')

also genau das, was Djangos ``TemplateView`` seit Jahren mitbringt. Sie sind
jetzt Instanzen von :class:`Vorlagenseite`; die Namen in ``core/urls.py``
bleiben unveraendert. Die drei Seiten MIT Logik (Theatre-Einstellungen,
BVH-Studio-Einstellungen, Fotoauftragsliste) stehen als je eine Klasse in
eigenen Modulen daneben — siehe ``seite_*.py``.

Warum kein selbstgeschriebener Rahmen: ``TemplateView`` beantwortet nur
GET/HEAD/OPTIONS. Geprueft, dass keine der dreizehn Vorlagen ein
``method="post"``-Formular enthaelt — sonst waere aus einem stillen 200 ein
405 geworden.
"""

from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView


class Vorlagenseite(TemplateView):
    """Eine Seite, die nur ihre Vorlage braucht.

    ``ansicht()`` liefert die fertige Django-Ansicht — damit bleibt in
    ``core/urls.py`` der gewohnte ``seiten.<name>`` stehen und niemand muss
    dort ``as_view()`` schreiben.

    **Der Name ist Pflicht, nicht Zierde.** ``View.as_view()`` gibt eine
    Funktion zurueck, die schlicht ``view`` heisst — bei dreizehn Seiten also
    dreizehnmal derselbe Name. Alles, was Routen ueber
    ``callback.__name__`` unterscheidet (Stapelspuren, Djangos Fehlerseite,
    das Werkzeug `testdeckung`), sieht dann EINE Seite statt dreizehn.
    Deshalb wird er hier gesetzt — genauso wie er vorher als Funktionsname
    dastand.
    """

    @classmethod
    def ansicht(cls, vorlage, name):
        fertig = cls.as_view(template_name=vorlage)
        fertig.__name__ = name
        fertig.__qualname__ = name
        return fertig


# --- Charakter und Szene ----------------------------------------------------
character_viewer = Vorlagenseite.ansicht('character_viewer.html',
                                         'character_viewer')
scene_config = Vorlagenseite.ansicht('scene_config.html', 'scene_config')
scene_model = Vorlagenseite.ansicht('scene_model.html', 'scene_model')

# --- Theatre ----------------------------------------------------------------
theatre_page = Vorlagenseite.ansicht('theatre.html', 'theatre_page')
theatre_studio_page = Vorlagenseite.ansicht('theatre_studio.html',
                                            'theatre_studio_page')
theatre_help_page = Vorlagenseite.ansicht('theatre_help.html',
                                          'theatre_help_page')

# --- BVH ---------------------------------------------------------------------
bvh_studio_page = Vorlagenseite.ansicht('bvh_studio.html', 'bvh_studio_page')
animations_page = Vorlagenseite.ansicht('animations.html', 'animations_page')
test_animation_page = Vorlagenseite.ansicht('skeleton_test.html',
                                            'test_animation_page')

# --- Hilfe und Tests ---------------------------------------------------------
rigging_help_page = Vorlagenseite.ansicht('rigging_help.html',
                                          'rigging_help_page')
test_character_page = Vorlagenseite.ansicht('test_character.html',
                                            'test_character_page')
smpl_test_page = Vorlagenseite.ansicht('test_smpl.html', 'smpl_test_page')

#: Die Foto-Seite laeuft im iframe der eigenen Seite — der Dekorator gilt fuer
#: die fertige Ansicht, nicht fuer die Klasse.
photo_to_3d_page = xframe_options_sameorigin(
    Vorlagenseite.ansicht('photo_to_3d.html', 'photo_to_3d_page'))
