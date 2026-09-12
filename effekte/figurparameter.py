# -*- coding: utf-8 -*-
u"""Figurparameter — die Stellgroessen der Pipeline „HumanBody-Figur (DEF-Skelett)".

WARUM (Edgar, 12.09.2026): „ich brauche was, wo ich auch mein HumanBody
Modell mit meinem DEF skeleton nutzen kann." Die Pipeline „Kleid + Wind"
baut eine MPFB-Figur in Blender; diese hier nimmt ein gespeichertes Modell
der Szene (`HumanBody/data/models/<name>.json`: Koerpertyp, Morphs,
GarmentCode-Stuecke, Frisur) und rechnet es ueber den Server-Videoweg
(`TheatreJS/ModelPhysik/hbfilm.py`: Retarget der Web-App, LBS auf 176
DEF-Knochen, pyrender).

Dieselbe Liste lesen die Karte der Seite, `Effektbefehl` und der
Unterprozess `effekte/figur/figurfilm.py` (Regel `JederParameterWirkt`).
"""
from __future__ import print_function

from .parametersatz import Parametersatz

__all__ = ['Figurparameter']


class Figurparameter(Parametersatz):

    PROG = 'figurfilm'
    #: `modell` ist der Pfad der Modelldatei (`<name>.json`), nicht der Name:
    #: Der Unterprozess soll nicht selbst im Modellordner suchen.
    PFLICHT = ('modell', 'bvh', 'ausgabe')
    #: (name, typ, vorgabe, minimum, maximum, beschriftung, hinweis)
    FELDER = (
        ('bilder', int, 120, 10, 2000, 'Bilder',
         'Zahl der Videobilder; die BVH begrenzt sie (bei 30 fps sind 150 '
         'Bilder 5 Sekunden)'),
        ('fps', int, 30, 10, 60, 'Bildrate',
         'Bilder je Sekunde im Video; die BVH wird mit ganzzahligem Schritt '
         '(Bildrate der BVH durch fps, gerundet) abgetastet — 60 fps → 30 heißt jedes zweite Bild'),
        ('breite', int, 720, 320, 3840, 'Breite (px)', 'Videobreite'),
        ('hoehe', int, 900, 240, 2160, 'Höhe (px)', 'Videohöhe'),
        ('physik', float, 0.0, 0.0, 80.0, 'Weichgewebe (mm)',
         'Velocity Skinning: höchster Zuschlag in Millimetern, 0 = aus '
         '(Hilfe → Körperphysik)'),
        ('ab', float, 0.0, 0.0, 600.0, 'Ab Sekunde',
         'Beginn in der BVH, in Sekunden'),
        # -- Stoffdynamik mit Newton SolverStyle3D (12.09.2026) --
        ('stoff', bool, True, 0, 1, 'Stoffdynamik (Newton)',
         'GarmentCode-Stücke als Stoff rechnen: Dehnung, Biegung, Kollision mit '
         'dem bewegten Körper, Wind. Aus = Kleidung folgt dem Körper starr (LBS)'),
        ('wind', float, 4.0, 0.0, 30.0, 'Wind (m/s)',
         'Windgeschwindigkeit; die Kraft je Stoffpunkt ist der Staudruck auf '
         'seine Fläche. 0 = kein Wind'),
        ('turbulenz', float, 0.3, 0.0, 1.0, 'Böen',
         'Anteil, um den die Windstärke schwankt (zeitlich und längs der '
         'Windrichtung)'),
        ('dichte', float, 0.2, 0.02, 2.0, 'Stoffgewicht (kg/m²)',
         'Flächengewicht: Seide 0,05, Baumwolle 0,15–0,25, Jeans 0,4'),
        ('steifigkeit', float, 1.0, 0.05, 20.0, 'Dehnsteifigkeit',
         'Faktor auf die Dehnsteifigkeit der Kleiderphysik-Probe'),
        ('biegung', float, 1.0, 0.05, 50.0, 'Biegesteifigkeit',
         'Faktor auf die Biegesteifigkeit der Probe; höher = steifer Stoff, '
         'weniger kleine Falten'),
        ('bund', float, 3.0, 0.0, 30.0, 'Fester Rand (cm)',
         'Das obere Band jedes Stücks folgt dem Körper starr (Bund, Schultern); '
         'darunter rechnet Newton'),
        ('teilschritte', int, 20, 2, 60, 'Teilschritte je Bild',
         'Newton-Schritte je Videobild; 20 bei 30 fps sind 600 Schritte je Sekunde'),
        ('iterationen', int, 10, 2, 40, 'Löser-Iterationen',
         'Style3D-Iterationen je Teilschritt'),
        ('einlauf', float, 0.5, 0.1, 3.0, 'Einlauf (s)',
         'Vor Bild 0 wandert der Körper aus der A-Haltung in die erste Pose; '
         'der Stoff (Drapierung der A-Haltung) folgt ihm — so startet er ohne '
         'die Verzerrung des Skinnings'),
    )
    WAHLEN = {'windrichtung': ('seite', ('seite', 'vorn', 'hinten'))}

    def __init__(self, modell, bvh, ausgabe, windrichtung='seite', **werte):
        super().__init__(modell=modell, bvh=bvh, ausgabe=ausgabe,
                         windrichtung=windrichtung, **werte)
