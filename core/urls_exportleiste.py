# -*- coding: utf-8 -*-
"""Routen der Exportleiste (31.10.2026, `core/api/exportleiste.py`) — für jeden Bereich gleich, der Bereich steht in der Adresse (`Exportleistebereiche`)."""

from django.urls import path

from .api.exportleiste import Exportleisteendpunkte

__all__ = ['EXPORTLEISTE']

ENDPUNKT = 'api/exportleiste/<str:bereich>/<str:kennung>/'

EXPORTLEISTE = [
    path(ENDPUNKT, Exportleisteendpunkte.zustand, name='exportleiste_zustand'),
    path(ENDPUNKT + 'export/', Exportleisteendpunkte.export, name='exportleiste_export'),
    path(ENDPUNKT + 'obj/', Exportleisteendpunkte.obj, name='exportleiste_obj'),
    path(ENDPUNKT + 'render/', Exportleisteendpunkte.render, name='exportleiste_render'),
    path(ENDPUNKT + 'render/neu/', Exportleisteendpunkte.render_neu, name='exportleiste_render_neu'),
    path(ENDPUNKT + 'render/loeschen/', Exportleisteendpunkte.render_loeschen, name='exportleiste_render_loeschen'),
    path(ENDPUNKT + 'einstellungen/', Exportleisteendpunkte.einstellungen, name='exportleiste_einstellungen'),
    path(ENDPUNKT + 'datei/<str:name>', Exportleisteendpunkte.datei, name='exportleiste_datei'),
]
