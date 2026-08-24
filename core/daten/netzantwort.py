# -*- coding: utf-8 -*-
"""Netzantwort — ein Netz als JSON-taugliches Wörterbuch für den Browser.

WARUM EINE KLASSE (17.08.2026): `base64.b64encode(x.astype(np.float32)
.tobytes()).decode('ascii')` stand SECHZEHNMAL im Projekt, verteilt über
`api/netz.py`, `api/kleidung.py`, `api/mhproxy.py`, `api/netzbearbeitung.py`,
`api/schnittmuster.py`, `api/smpl.py`, `api/smplx_ausgabe.py` und
`test_character_api.py`. Dazu zwei private `_b64`-Helfer, die dasselbe taten.
Gefunden vom Werkzeug `doppelcode` (Kriterium 6).

DER GEFÄHRLICHE TEIL SIND DIE TYPEN, nicht das base64. Der Browser liest die
Puffer mit einer festen Breite:

    vertices, normals, uvs   Float32Array   -> muss float32 sein
    faces                    Uint32Array    -> muss uint32 sein
    skin_indices/-weights    Float32Array   -> muss float32 sein

Ein Feld, das versehentlich als float64 herausgeht, ist doppelt so groß UND
wird auf der Gegenseite falsch gelesen: Jeder zweite Wert wird zum Exponenten
des Nachbarn. Das Modell sieht dann zerrissen aus, und niemand vermutet einen
Datentyp. Deshalb setzt jede Methode hier den Typ selbst — statt sich darauf zu
verlassen, dass der Aufrufer `.astype(np.float32)` nicht vergisst.

`ravel()` gehört dazu: Ein (N, 3)-Feld und ein flaches 3N-Feld liefern dieselben
Bytes, aber nur, wenn das Feld C-zusammenhängend ist. Nach einem `[:, [0, 2, 1]]`
ist es das nicht mehr.
"""

import base64

import numpy as np


class Netzantwort:
    """Baut das Wörterbuch, das `JsonResponse` an den Browser gibt."""

    #: Feldname -> Zieltyp. Der Browser liest genau diese Breiten.
    TYPEN = {
        'vertices': np.float32,
        'normals': np.float32,
        'uvs': np.float32,
        'skin_indices': np.float32,
        'skin_weights': np.float32,
        'faces': np.uint32,
    }

    #: Die SMPL-X-Antwort (`api/smplx_ausgabe.py`) hat einen EIGENEN Vertrag:
    #: Dort sind die Knochenindizes `uint16`, nicht float32 — die Gegenseite
    #: liest sie mit `base64ToUint16`. Gemessen am Erzeuger
    #: (`wrappers/smplest_x_wrapper.generate_mesh`), nicht geraten:
    #:
    #:     vertices, joints, uv_*coords/vertices, *skin_weights   float32
    #:     faces, uv_faces                                        uint32
    #:     skin_indices, uv_skin_indices                          uint16
    #:
    #: Wer diese Breiten angleicht, macht die Foto-zu-3D-Kette kaputt, ohne
    #: dass etwas rot wird. Deshalb geht der Typ dort ausdrücklich mit.
    TYPEN_SMPLX = {
        'faces': np.uint32, 'uv_faces': np.uint32,
        'skin_indices': np.uint16, 'uv_skin_indices': np.uint16,
    }

    @classmethod
    def feld(cls, werte, name, typ=None):
        """Ein Feld als base64 — mit dem Typ, den der Browser erwartet.

        `typ` schlägt die Tabelle: Für einen zweiten Vertrag (SMPL-X, siehe
        `TYPEN_SMPLX`) wird er ausdrücklich mitgegeben, statt die Tabelle zu
        einer Sammlung von Sonderfällen wachsen zu lassen.
        """
        if typ is None:
            typ = cls.TYPEN.get(name, np.float32)
        flach = np.ascontiguousarray(np.asarray(werte).ravel(), dtype=typ)
        return base64.b64encode(flach.tobytes()).decode('ascii')

    @classmethod
    def smplx_feld(cls, werte, name):
        """Ein Feld der SMPL-X-Antwort, mit deren eigenen Breiten."""
        return cls.feld(werte, name, cls.TYPEN_SMPLX.get(name, np.float32))

    @classmethod
    def aus(cls, vertices, faces=None, normals=None, uvs=None, **weitere):
        """Die übliche Antwort: Punkte, optional Dreiecke, Normalen, UVs.

        `vertex_count` und `face_count` kommen aus den Feldern selbst — sie von
        Hand mitzugeben war die zweite Fehlerquelle: In zwei Fassungen zählte
        `face_count` die VIERECKE, obwohl `faces` schon Dreiecke enthielt.
        """
        punkte = np.asarray(vertices)
        aus = {
            'vertex_count': int(punkte.reshape(-1, 3).shape[0]),
            'vertices': cls.feld(punkte, 'vertices'),
        }
        if faces is not None:
            dreiecke = np.asarray(faces)
            aus['face_count'] = int(dreiecke.reshape(-1, 3).shape[0])
            aus['faces'] = cls.feld(dreiecke, 'faces')
        if normals is not None:
            aus['normals'] = cls.feld(normals, 'normals')
        if uvs is not None:
            aus['uvs'] = cls.feld(uvs, 'uvs')
        for name, werte in weitere.items():
            aus[name] = (cls.feld(werte, name) if name in cls.TYPEN else werte)
        return aus
