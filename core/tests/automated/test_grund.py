# -*- coding: utf-8 -*-
"""Grundabsicherung aus djangoBase — Art „automated".

Die Testklassen stehen in `djangobase.grundtests` und laufen in allen sechs
Projekten, die djangoBase einbinden. Hier werden sie nur eingesammelt; was sie
prüfen, steht dort im Modulkopf:

    Seiten        kein 5xx auf einer parameterlosen Route
    Urls          jede Route zeigt auf ein aufrufbares Ziel in einem Modul,
                  das es gibt
    Module        jede Datei der eigenen Apps ist importierbar
    Migrationen   Modell geändert, `makemigrations` vergessen
    Vorlagen      TemplateSyntaxError fällt sonst erst beim Aufruf auf
    Logging       Fehler landen nirgends (Kriterium 16)
    Menü          Eintrag zeigt auf eine Route, die es nicht mehr gibt
    EsModule      „Seite lädt, Konsole schweigt, Knopf tot"

Eingestellt wird über `DJANGOBASE["grundtests"]` in `ui/settings.py` — dort
stehen die Seiten, die nicht angefahren werden (Render, GPU, Blender).

Eine eigene Kopie dieser Prüfungen wäre die falsche Antwort: Sie gehören zu
djangoBase, damit ein Fund in einem Projekt allen zugutekommt.
"""

from djangobase.grundtests import *      # noqa: F401,F403
