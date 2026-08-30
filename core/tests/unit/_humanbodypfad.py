# -*- coding: utf-8 -*-
u"""Das HumanBody-Paket in den Suchpfad legen — fuer Tests, die es brauchen.

BEFUND `doppelcode` (30.08.2026): Dieselben fuenf Zeilen standen in
``test_cloth_bruecke.py`` und ``test_kollision_ton_pfade.py``. Beide Tests
pruefen Code aus ``HumanBody/collision/``, der nicht ueber den normalen
Importweg dieses Projekts erreichbar ist.

WARUM ERST IM TEST UND NICHT IN DEN EINSTELLUNGEN: ``ui/settings.py`` legt den
Pfad bereits an — aber nur, wenn Django hochgefahren ist. Diese Faelle laufen
als ``SimpleTestCase`` ohne Datenbank und muessen sich selbst behelfen.

DER EINTRAG WIRD NUR EINMAL GESETZT. Ein zweiter Eintrag desselben Pfades
schadet nicht, aber bei jedem Testlauf waechst ``sys.path`` sonst weiter — und
lange Suchpfade machen JEDEN Import langsamer.
"""
import sys

from django.conf import settings


class Humanbodypfad:
    u"""Der Suchpfad zum HumanBody-Paket."""

    @staticmethod
    def setzen():
        u"""Die HumanBody-Wurzel voranstellen. Gibt den Pfad zurueck (oder '')."""
        wurzel = str(getattr(settings, 'HUMANBODY_ROOT', ''))
        if wurzel and wurzel not in sys.path:
            sys.path.insert(0, wurzel)
        return wurzel
