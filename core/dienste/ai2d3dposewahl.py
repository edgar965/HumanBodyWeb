# -*- coding: utf-8 -*-
"""Ai2d3dposewahl — woher 2d-3d-AI die Gelenke der Person in den Fotos nimmt (24.10.2026).

Edgar: „für pose, rig habe ich bei mesh3d-AI auch eine lösung, schau nach“ → „wenn du meinst, ViTPose ist besser, kannst du das auch ausprobieren, ggf. optional? Mach auch du eine Seite
Einstellungen - 2d-3d-KI wo du sowas einstellen kannst, damit man das später beides ausprobieren kann?“. Gespeichert in `AppSettings.ui_prefs` wie `Mesh3daikostuemstufe`; gelesen von
`KoerperKI_Fotos.Fotogelenke` beim nächsten Lauf (Körperlage und Einpassen), ein gerechneter Lauf bleibt, wie er ist.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dposewahl']


class Ai2d3dposewahl:
    SCHLUESSEL = 'ai2d3d_pose_quelle'
    VORGABE = 'vitpose'
    WERTE = (('vitpose', 'ViTPose-H (im Prozess, VitposeTorch)'), ('sam3dbody', 'SAM 3D Body (wie Mesh-3D und Mesh3D-AI)'))
    BESCHREIBUNG = {
        'vitpose': 'ViTPose-H WholeBody (133 Punkte) als eigener Nachbau in python14, im selben Prozess auf der Grafikkarte (`A:\\3DTools\\VitposeTorch`). Gegen das Original (FootMR, python10) '
                   'gemessen: höchstens 1,05 px Abstand, 0,04 s je Foto. Liefert je Gelenk eine Zuversicht (Gewicht). An den EdgarTrip-Fotos liegen Ellbogen, Handgelenke, Knie und Knöchel '
                   'auch im Profil richtig (angesehen, `ProjektTemp/_wegwerf/ai2d3d/kopf/vitpose_*.png`).',
        'sam3dbody': 'SAM 3D Body (MHR-70) über `Posebestimmung` und den Runner `_run_sam3dpose.py` (python12, eigener Prozess, Modell laden 27–85 s) — derselbe Weg, mit dem Mesh-3D und die '
                     'Vorstufe „Nur Rig“ von Mesh3D-AI die Gelenke am Bild finden. Genommen werden die Bildpunkte (k2) der zwölf Hauptgelenke, Gewicht 1. Das Ergebnis liegt je Foto als '
                     '`sam3d.json` neben dem Lauf und wird bei gleichem Bild nicht neu gerechnet.',
    }

    @classmethod
    def aus(cls, prefs):
        w = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return w if w in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Quelle — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Ai2d3dposewahl: Einstellung nicht lesbar (%s) — Vorgabe %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, str(wert))
