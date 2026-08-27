# -*- coding: utf-8 -*-
"""Beiwerk der Kamera-Tests: Kurzbogen-Slerp und der Speichern-Laden-Umlauf.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `camera_track_tests.py` herausgeloest (17.08.2026, 393 Zeilen).

`slerp_kurzbogen` ist die PRUEFFASSUNG der Rechnung, die im Browser in
`playback.js` steht: Sie dreht das Ziel-Quaternion um, wenn das Skalarprodukt
negativ ist — sonst nimmt die Kamera den langen Weg um die Kugel („wilde
Spruenge"). Die Tests dazu stehen in `kamera_slerp_tests.py`.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassenreif` Frage 1): vier freie
Funktionen und ein Zwischenspeicher mit `global`. Beides steht jetzt in
`Kamerabasis`.
"""

from __future__ import annotations

import urllib.parse
from pathlib import Path

import numpy as np

from core.projekt_temp import ProjektTemp

from .base import Netzruf


class Kamerabasis:
    """Kurzbogen-Slerp und der Speichern-Laden-Umlauf der Kamera-Tests."""

    #: Ab diesem Skalarprodukt ist die Drehung so klein, dass die
    #: Kugelinterpolation numerisch kippt — dann linear mischen.
    ENTARTET_AB = 0.9995

    #: Das Ergebnis des Speichern-Laden-Umlaufs, einmal gerechnet. Er faehrt
    #: zwei HTTP-Aufrufe und wird von zehn Pruefungen gebraucht; als
    #: KLASSENFELD laesst er sich mit `Kamerabasis.umlauf = None` leeren.
    umlauf = None

    # ------------------------------------------------------------------ Slerp

    @classmethod
    def slerp_kurzbogen(cls, q0, q1, t):
        """Kugelinterpolation auf dem KURZEN Weg — wie `playback.js`."""
        q0 = np.asarray(q0, dtype=np.float64)
        q1 = np.asarray(q1, dtype=np.float64)
        if q0 @ q1 < 0:
            q1 = -q1
        punkt = float(np.clip(q0 @ q1, -1.0, 1.0))
        if punkt > cls.ENTARTET_AB:
            gemischt = (1 - t) * q0 + t * q1
            return gemischt / np.linalg.norm(gemischt)
        winkel = np.arccos(punkt)
        anteil0 = np.sin((1 - t) * winkel) / np.sin(winkel)
        anteil1 = np.sin(t * winkel) / np.sin(winkel)
        return anteil0 * q0 + anteil1 * q1

    # ------------------------------------------------------------- Der Umlauf

    @classmethod
    def projekt(cls):
        """Das Studio-Projekt der Umlauf-Pruefung — zwei Kamera-Keyframes.

        Als eigene Methode, weil es reine DATEN sind: Der Ablauf darunter
        (speichern, laden, vergleichen) ist die Pruefung, das hier ist ihr
        Aufbau.

        Der Kniff steckt im zweiten Keyframe: Sein Quaternion ist auf der
        GESPIEGELTEN Hemisphaere (alle Vorzeichen umgedreht). Mathematisch ist
        das dieselbe Drehung; ein Slerp ohne Kurzbogen-Korrektur dreht die
        Kamera trotzdem einmal fast ganz herum. Genau das soll die Pruefung
        sehen.
        """
        # Dictionary gewollt: geht unveraendert als JSON an
        # /api/studio/project-save/.
        return {
            'name': 'T', 'fps': 30,
            'tracks': [{
                'name': 'Kamera', 'type': 'camera', 'color': '#4caf50',
                'muted': False, 'position': [0, 0, 0], 'cameraActive': True,
                'clips': [
                    cls.keyframe(1, {'x': 2.0, 'y': 1.5, 'z': 3.0},
                                 {'x': -0.12, 'y': 0.55, 'z': 0.06},
                                 {'x': 0.103, 'y': 0.275, 'z': -0.031,
                                  'w': 0.956}, 'KF1'),
                    cls.keyframe(200, {'x': 2.05, 'y': 1.51, 'z': 3.02},
                                 {'x': -0.12, 'y': 0.56, 'z': 0.06},
                                 {'x': -0.104, 'y': -0.280, 'z': 0.031,
                                  'w': -0.955}, 'KF2'),
                ],
            }],
        }

    @staticmethod
    def keyframe(bild, position, drehung, quaternion, name):
        """Ein Kamera-Keyframe-Clip in der Form, die das Studio speichert."""
        return {
            'type': 'camera_kf', 'name': name, 'startFrame': bild,
            'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0,
            'speed': 1.0,
            'data': {
                'position': position, 'rotation': drehung,
                'quaternion': quaternion, 'fov': 45,
                'interpolation': 'smooth', 'fade': True,
            },
        }

    @classmethod
    def umlauf_ergebnis(cls):
        """Speichern, laden, vergleichen — einmal je Prozess."""
        if cls.umlauf is not None:
            return cls.umlauf
        # ProjektTemp statt tempfile: SafePath laesst nur MEDIA_ROOT zu
        # (System-Temp gab 403 — 48 Tests rot seit 12.08.2026).
        with ProjektTemp.wegwerfordner() as ordner:
            pfad = Path(ordner) / 'cam_proj.studio.json'
            code, gesichert = Netzruf.senden(
                '/api/studio/project-save/', method='POST',
                data={'path': str(pfad), 'project': cls.projekt()})
            if code != 200 or not gesichert.get('ok'):
                cls.umlauf = {'_save_code': code, '_save_ok': False}
                return cls.umlauf
            adresse = urllib.parse.quote(str(pfad))
            code, geladen = Netzruf.senden(
                '/api/studio/project-load/?path=%s' % adresse)
        if code != 200 or not geladen.get('ok'):
            cls.umlauf = {'_save_ok': True, '_load_code': code,
                          '_load_ok': False}
            return cls.umlauf
        cls.umlauf = cls._auswerten(geladen.get('project', {}))
        return cls.umlauf

    @staticmethod
    def _auswerten(projekt):
        spuren = [s for s in projekt.get('tracks', [])
                  if s.get('type') == 'camera']
        clips = spuren[0].get('clips', []) if spuren else []
        return {
            '_save_ok': True, '_load_ok': True,
            'track_count': len(spuren),
            'clip_count': len(clips),
            'kf1': clips[0] if len(clips) > 0 else None,
            'kf2': clips[1] if len(clips) > 1 else None,
            'cameraActive': spuren[0].get('cameraActive') if spuren else None,
        }
