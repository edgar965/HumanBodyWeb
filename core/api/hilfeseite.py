# -*- coding: utf-8 -*-
u"""Hilfeseite — die gemeinsame Bauform der eigenen Hilfe-Ansichten.

Fuenf Seiten unter Hilfe -> Kleidung/Koerper fuehrten dieselben zwei
Bausteine je Datei (Befund `doppelcode`, 12.09.2026): `get_context_data`
mit dem `aktiv`-Schluessel fuer die Menuegruppe und `ansicht()`, das der
Funktion aus `View.as_view()` einen sprechenden Namen gibt — im Fehlerlog
und in `manage.py show_urls` stuende sonst fuenfmal `view`.

Eine Unterklasse nennt `template_name`, `AKTIV` (den Menuepunkt) und
liefert in `kontext()` ihre Daten; `NAME` nur, wenn der Funktionsname vom
Menuepunkt abweicht.
"""
from django.views.generic import TemplateView


class Hilfeseite(TemplateView):

    #: Der Menuepunkt, den die Seite in der Hilfe-Gruppe hervorhebt.
    AKTIV = ''
    #: Name der Ansichtsfunktion; leer heisst wie `AKTIV`.
    NAME = ''

    def kontext(self):
        u"""Die Daten der Seite — die Unterklasse liefert sie."""
        return {}

    def get_context_data(self, **kwargs):
        kontext = super().get_context_data(**kwargs)
        kontext['aktiv'] = self.AKTIV
        kontext.update(self.kontext())
        return kontext

    @classmethod
    def ansicht(cls):
        u"""Die fertige Ansicht mit sprechendem Namen."""
        ansicht = cls.as_view()
        ansicht.__name__ = cls.NAME or cls.AKTIV
        return ansicht
