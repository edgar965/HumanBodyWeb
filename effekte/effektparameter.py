# -*- coding: utf-8 -*-
u"""Effektparameter — die Stellgroessen der Pipeline „Kleid + Wind", an EINER Stelle.

Drei Stellen lesen dieselbe Liste: die Karte auf der Seite „Process Videos —
Effekte" (Felder, Vorgaben, Grenzen), der Befehlsaufbau in Django
(`Effektbefehl`) und der Blender-Prozess (`kleidwind.py`, ueber `aus_argv`).
Stuende die Liste dreimal, wuerde eine Grenze irgendwann nur an zwei Stellen
geaendert — und Blender rechnete etwas anderes, als die Karte zeigte
(Regel `JederParameterWirkt`, 12.09.2026).

Das Gemeinsame (Grenzen, Karte, Kommandozeile) liegt in `Parametersatz`;
hier stehen nur die Felder dieser Pipeline. Geschlecht: MakeHuman zaehlt
0 = weiblich, 1 = maennlich.
"""
from __future__ import print_function

from .parametersatz import Parametersatz

__all__ = ['Effektparameter']


class Effektparameter(Parametersatz):
    u"""Namen, Typen, Vorgaben und Grenzen — plus Lesen aus `sys.argv`."""

    PROG = 'kleidwind'
    PFLICHT = ('bvh', 'kleid', 'ausgabe')
    #: (name, typ, vorgabe, minimum, maximum, beschriftung, hinweis)
    FELDER = (
        ('bilder', int, 300, 10, 6000, 'Bilder',
         'Zahl der simulierten und gerenderten Bilder; die BVH begrenzt sie'),
        ('breite', int, 1280, 320, 3840, 'Breite (px)', 'Videobreite'),
        ('hoehe', int, 720, 240, 2160, 'Höhe (px)', 'Videohöhe'),
        ('unterteilung', int, 1, 0, 3, 'Stoffunterteilung',
         'Unterteilungsstufen des Kleids vor der Simulation: 0 = wie geliefert, '
         'je Stufe viermal so viele Flächen (feinere Falten, längere Rechnung)'),
        ('qualitaet', int, 5, 1, 20, 'Simulationsschritte',
         'Teilschritte je Bild (Blender „Quality"); mehr = stabiler, langsamer'),
        ('wind', float, 2.0, 0.0, 50.0, 'Windstärke',
         'Kraft des Windfelds (Blender-Einheit); 0 = kein Wind. Bei 6 wickelte '
         'sich der Rock um die Hüfte (002_Dance, 12.09.2026)'),
        ('turbulenz', float, 2.0, 0.0, 20.0, 'Turbulenz',
         'Rauschen auf der Windstärke — Böen statt gleichmäßigem Zug'),
        ('steifigkeit', float, 1.0, 0.05, 20.0, 'Biegesteifigkeit',
         'Blender „Bending"; 0,5 = Baumwolle, 10 = Jeans'),
        ('reibung', float, 1.0, 0.0, 80.0, 'Reibung am Körper',
         'Blender „Friction" der Kollision (Vorgabe dort 5). Gemessen bei '
         'Bild 120 von 002_Dance: mit 5 hing der Saum 1,6 cm unter der Hüfte, '
         'mit 1 waren es 7,8 cm — der Rock rutscht wieder herunter'),
        ('selbstkollision', bool, True, 0, 1, 'Selbstkollision',
         'Stoff stößt an sich selbst — ohne das faltet sich der Rock durch '
         'sich hindurch und zerknüllt; kostet Rechenzeit'),
    )
    GESCHLECHTER = (('weiblich', 0.0), ('maennlich', 1.0))
    RENDERER = ('workbench', 'eevee')
    WAHLEN = {'geschlecht': ('weiblich', ('weiblich', 'maennlich')),
              'renderer': ('workbench', RENDERER)}

    def __init__(self, bvh, kleid, ausgabe, geschlecht='weiblich',
                 renderer='workbench', **werte):
        super().__init__(bvh=bvh, kleid=kleid, ausgabe=ausgabe,
                         geschlecht=geschlecht, renderer=renderer, **werte)

    @property
    def geschlechtswert(self):
        return dict(self.GESCHLECHTER)[self.geschlecht]
