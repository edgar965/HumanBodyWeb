# -*- coding: utf-8 -*-
"""Ai2d3dgesichtswahl — welcher Erkenner bei 2d-3d-AI die Gesichtspunkte misst (27.10.2026).

Edgar: „ich brauche eine einzige Lösung für beides, Profil und vorne“ → „mach A [insightface auf torch], aber in den Einstellungen umschaltbar zwischen Insight und MediaPipe. MediaPipe soll
weiter lauffähig bleiben“. Gespeichert in `AppSettings.ui_prefs` wie `Ai2d3dposewahl`; gelesen von `KoerperKI_Fotos.Gesichtserkenner` beim nächsten Lauf (Kopf-KI: Eingang und Verlust,
Abnahme: Feld 3 der Jobseite) — ein gerechneter Lauf bleibt, wie er ist; ein Netz der Kopf-KI gehört zu dem Erkenner, mit dem es trainiert wurde (andere Punktzahl im Eingang).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dgesichtswahl']


class Ai2d3dgesichtswahl:
    SCHLUESSEL = 'ai2d3d_gesicht_erkenner'
    VORGABE = 'insightface'
    WERTE = (('insightface', 'insightface 2d106 (InsightfaceTorch) — vorn und im Profil'), ('mediapipe', 'MediaPipe FaceLandmarker (MediapipeTorch) — nur von vorn'))
    BESCHREIBUNG = {
        'insightface': 'Finder SCRFD (det_10g) und 106 Punkte (2d106det) aus dem Modellpaket buffalo_l, nachgebaut in torch auf der Grafikkarte (`A:\\3DTools\\InsightfaceTorch`). Gegen '
                       'insightface selbst gemessen (27.10.2026, 18 Kopfausschnitte von EdgarTrip): Netz gegen Netz höchstens 1e-5, Punkte im Mittel 0,1–0,5 px, 50 ms je Ausschnitt. '
                       'Findet das Gesicht vorn und im Profil (Fundwert 0,53–0,88, auch auf den Seitenbildern); im Profil zählen nur die sichtbare Gesichtshälfte und die Mitte, die '
                       'Kontur (33 Punkte) nur von vorn.',
        'mediapipe': 'MediaPipe FaceLandmarker (478 Punkte, Lider, Iris, Lippen) als torch-Nachbau (`A:\\3DTools\\MediapipeTorch`), gegen MediaPipe 0.10.32 gemessen: gleiche Fundwerte '
                     'und Anwesenheit, Punkte 0,1–1 px. Nur von vorn verlässlich: im Profil springt die Anwesenheit des Punktnetzes bei 10° Drehung zwischen 0 und 1, auf den '
                     'Seitenbildern bleibt sie ≈ 0 — laut Google eine Grenze des Modells (nur auf Gesichtern von vorn trainiert, GitHub google-ai-edge/mediapipe #3510).',
    }

    @classmethod
    def aus(cls, prefs):
        w = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return w if w in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Der gespeicherte Erkenner — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Ai2d3dgesichtswahl: Einstellung nicht lesbar (%s) — Vorgabe %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, str(wert))
