# -*- coding: utf-8 -*-
"""Engine2d3dKleiderfilmoptionen — die Gruppe `film` der Optionen von „Haar Engine" (30.09.2026).

Was der Schritt „film" braucht: die BVH-Datei, die Zahl der Bilder, Bildgröße. Dieselbe Katalogform wie
`Meshoptionen` (`schluessel`, `titel`, `art`, `vorgabe`, `werte`, `hinweis`), dazu die Art `text` (Pfad der
BVH) — `Meshoptionenformular` kennt sie. Die Werte liegen im Auftrag unter `optionen['film']`. Was die
Engine sonst noch einstellen lässt (Renderer, Licht, Kamera), kommt mit ihren Einzelheiten.
"""

__all__ = ['Engine2d3dKleiderfilmoptionen']


class Engine2d3dKleiderfilmoptionen:
    KATALOG = [
        {
            'schluessel': 'bvh',
            'titel': 'BVH-Datei (Pfad)',
            'art': 'text',
            'vorgabe': '',
            'hinweis': 'Die Bewegung, die auf das Rig gelegt wird — SMPL-X-Dateien aus VideoToBVH (Gelenke „Pelvis", '
            '„Left_hip" …; Finger werden nicht übertragen) oder eine BVH aus der Bibliothek. Die Bühne spielt sie live auf der '
            'Figur ab. Vorgabe: der Tanz der Bibliothek (Daz/Dance.bvh). Leer = der Schritt „film" wird '
            'übersprungen.',
        },
        {
            'schluessel': 'bilder',
            'titel': 'Bilder',
            'art': 'zahl',
            'vorgabe': 300,
            'min': 2,
            'max': 20000,
            'hinweis': 'Höchstens so viele Bilder der BVH; gerendert wird in ihrer Bildrate (60 fps bei VideoToBVH).',
        },
        {
            'schluessel': 'breite',
            'titel': 'Breite (px)',
            'art': 'zahl',
            'vorgabe': 960,
            'min': 64,
            'max': 4096,
        },
        {'schluessel': 'hoehe', 'titel': 'Höhe (px)', 'art': 'zahl', 'vorgabe': 960, 'min': 64, 'max': 4096},
    ]

    #: Die Standardbewegung (Edgar, 01.10.2026: „Standard Animation (dance)"), relativ zur BVH-Bibliothek.
    TANZ = ('Daz', 'Dance.bvh')

    @classmethod
    def tanz(cls):
        """Pfad der Standardbewegung, wenn es sie gibt — sonst '' (dann bleibt der Schritt „film" aus)."""
        import os

        from .bvhverzeichnis import Bvhverzeichnis
        pfad = os.path.join(Bvhverzeichnis().wurzel(), *cls.TANZ)
        return pfad if os.path.isfile(pfad) else ''

    @classmethod
    def vorgaben(cls):
        aus = {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}
        aus['bvh'] = cls.tanz()
        return aus

    @classmethod
    def katalog(cls):
        return {
            'optionen': [
                dict(
                    e,
                    werte=[{'wert': w, 'text': t} for w, t in e.get('werte', [])],
                    fein=bool(e.get('fein')),
                )
                for e in cls.KATALOG
            ]
        }

    @classmethod
    def pruefen(cls, roh):
        """Nur bekannte Schlüssel mit gültigen Werten — der Rest wird Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['art'] == 'text':
                aus[e['schluessel']] = str(wert).strip()[:500]
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except TypeError, ValueError:
                    continue
                if e.get('min', zahl) <= zahl <= e.get('max', zahl):
                    aus[e['schluessel']] = int(zahl) if zahl.is_integer() else zahl
        return aus
