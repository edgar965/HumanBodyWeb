# -*- coding: utf-8 -*-
"""Blendermodellblenderoptionen — die Gruppe `blender` der Optionen von „BlenderModel" (29.09.2026).

Was der Blender-Teil der Pipeline braucht (`Docu/konzept_blendermodell.md`, Stufe 2): die BVH-Datei, die
Zahl der Bilder, Bildgröße und Renderer. Dieselbe Katalogform wie `Meshoptionen` (`schluessel`, `titel`,
`art`, `vorgabe`, `werte`, `hinweis`), dazu die Art `text` (Pfad der BVH) — `Meshoptionenformular` kennt
sie seit heute. Die Werte liegen im Auftrag unter `optionen['blender']`.
"""

__all__ = ['Blendermodellblenderoptionen']


class Blendermodellblenderoptionen:
    KATALOG = [
        {'schluessel': 'bvh', 'titel': 'BVH-Datei (Pfad)', 'art': 'text', 'vorgabe': '',
         'hinweis': 'Die Bewegung, die Blender auf das Rig legt — SMPL-X-Dateien aus VideoToBVH '
                    '(Gelenke „Pelvis", „Left_hip" …; Finger werden nicht übertragen) oder eine BVH aus der '
                    'Bibliothek. Leer = der Schritt „blender" wird übersprungen.'},
        {'schluessel': 'bilder', 'titel': 'Bilder', 'art': 'zahl', 'vorgabe': 300, 'min': 2, 'max': 20000,
         'hinweis': 'Höchstens so viele Bilder der BVH; gerendert wird in ihrer Bildrate (60 fps bei VideoToBVH).'},
        {'schluessel': 'breite', 'titel': 'Breite (px)', 'art': 'zahl', 'vorgabe': 960, 'min': 64, 'max': 4096},
        {'schluessel': 'hoehe', 'titel': 'Höhe (px)', 'art': 'zahl', 'vorgabe': 960, 'min': 64, 'max': 4096},
        {'schluessel': 'renderer', 'titel': 'Renderer', 'art': 'wahl', 'vorgabe': 'workbench', 'werte': [
            ('workbench', 'Workbench — schnell, Texturen und Schatten'),
            ('eevee', 'Eevee — Licht und Material'),
        ], 'hinweis': 'Workbench rendert 60 Bilder in Sekunden (gemessen 29.09.2026: 6,6 s bei 480 × 640). '
                      'Cycles kommt mit Stufe 5 des Konzepts.'},
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def katalog(cls):
        return {'optionen': [dict(e, werte=[{'wert': w, 'text': t} for w, t in e.get('werte', [])],
                                  fein=bool(e.get('fein'))) for e in cls.KATALOG]}

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit gültigen Werten — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['art'] == 'wahl' and str(wert) in [w for w, _ in e['werte']]:
                aus[e['schluessel']] = str(wert)
            elif e['art'] == 'text':
                aus[e['schluessel']] = str(wert).strip()[:500]
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except (TypeError, ValueError):
                    continue
                if e.get('min', zahl) <= zahl <= e.get('max', zahl):
                    aus[e['schluessel']] = int(zahl) if zahl.is_integer() else zahl
        return aus
