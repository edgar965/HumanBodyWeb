# -*- coding: utf-8 -*-
"""Figurvideostuecke — Kleidungsstuecke aus der Szene fuer den Filmlauf.

WARUM (11.09.2026): Der Server-Weg nahm nur GarmentCode-Stuecke mit, ueber
ihre `_sim_rig.json`. Vorlagen-Cloth, Garderobe und MakeHuman-Proxys haben
keine solche Datei — die Figur kam im Video ohne sie an. Jetzt schickt der
Browser jedes gehaeutete Netz so, wie es in der Szene haengt
(`scene/figurvideo_stuecke.js`), und hier wird daraus je Stueck eine
`.npz`, die `ModelPhysik/figurnetze.py` wie eine Rig-Datei liest.

Aufbau eines Pakets (ohne Kopf, die Zahlen stehen im Auftrag):

    Float32[n*3]  Punkte, Lage der Figur, Y OBEN (Three.js)
    Uint32 [m*3]  Dreiecke
    Uint16 [n*4]  Knochennummern in der Reihenfolge von `knochen`
    Float32[n*4]  Gewichte

DIE ACHSEN WERDEN HIER GEDREHT: Die Szene rechnet Y oben, der Filmlauf in
Blender-Lage (Z oben) — `blender = (x, -z, y)`, die Umkehrung von
`blenderToThreeCoords`. Ein Stueck ohne diese Drehung laege im Video flach
am Boden neben der Figur (dieselbe Falle wie am 06.09.2026 beim Anziehen).
"""
import os

import numpy as np


class Figurvideostuecke:
    """Pakete aus dem Formular -> `.npz` je Stueck im Auftragsordner."""

    #: Standardfarbe, wenn das Material keine nennt (Blau wie bisher).
    FARBE = [0.29, 0.44, 0.72]

    @classmethod
    def ablegen(cls, dateien, liste, knochen, ordner):
        """Schreibt jedes Stueck und gibt `[{name, pfad, farbe}]` zurueck.

        `dateien` ist `request.FILES`, `liste` die Stueckliste des Auftrags
        (`name, farbe, punkte, dreiecke, datei`), `knochen` die Namensliste
        des Skeletts in der Reihenfolge der Knochennummern.
        """
        if not liste:
            return []
        if not knochen:
            raise ValueError('Stuecke ohne Knochenliste.')
        ziel = os.path.join(ordner, 'stuecke')
        os.makedirs(ziel, exist_ok=True)
        aus = []
        for nummer, meta in enumerate(liste):
            name = str(meta.get('name') or 'Stueck %d' % (nummer + 1))
            datei = dateien.get(str(meta.get('datei') or ''))
            if datei is None:
                raise ValueError('Stueck „%s" ohne Daten.' % name)
            pfad = os.path.join(ziel, '%02d.npz' % nummer)
            cls._schreiben(pfad, datei.read(), int(meta.get('punkte') or 0),
                           int(meta.get('dreiecke') or 0), knochen, name)
            aus.append({'name': name, 'pfad': pfad,
                        'farbe': cls.farbe(meta.get('farbe'))})
        return aus

    @classmethod
    def _schreiben(cls, pfad, roh, n, m, knochen, name):
        erwartet = n * 12 + m * 12 + n * 8 + n * 16
        if n <= 0 or m <= 0 or len(roh) != erwartet:
            raise ValueError('Stueck „%s": %d Bytes, erwartet %d '
                             '(%d Punkte, %d Dreiecke).'
                             % (name, len(roh), erwartet, n, m))
        punkte = np.frombuffer(roh, dtype=np.float32, count=n * 3
                               ).reshape(n, 3)
        versatz = n * 12
        dreiecke = np.frombuffer(roh, dtype=np.uint32, count=m * 3,
                                 offset=versatz).reshape(m, 3)
        versatz += m * 12
        nummern = np.frombuffer(roh, dtype=np.uint16, count=n * 4,
                                offset=versatz).reshape(n, 4)
        versatz += n * 8
        gewichte = np.frombuffer(roh, dtype=np.float32, count=n * 4,
                                 offset=versatz).reshape(n, 4)
        if dreiecke.size and int(dreiecke.max()) >= n:
            raise ValueError('Stueck „%s": Dreieck zeigt auf Punkt %d von %d.'
                             % (name, int(dreiecke.max()), n))
        belegt = nummern[gewichte > 0]
        if belegt.size and int(belegt.max()) >= len(knochen):
            raise ValueError('Stueck „%s": Knochennummer %d, aber nur %d '
                             'Namen.' % (name, int(belegt.max()), len(knochen)))
        # Three.js (Y oben) -> Blender (Z oben).
        blender = np.column_stack([punkte[:, 0], -punkte[:, 2], punkte[:, 1]])
        np.savez(pfad, punkte=blender.astype(np.float64),
                 dreiecke=dreiecke.astype(np.int64),
                 skin_index=nummern.astype(np.int32),
                 skin_weight=gewichte.astype(np.float64),
                 knochen=np.array([str(k) for k in knochen]))

    @classmethod
    def farbe(cls, wert):
        """`#rrggbb` -> [r, g, b] in 0..1; sonst die Standardfarbe."""
        try:
            farbe = str(wert or '').lstrip('#')
            if len(farbe) == 6:
                return [int(farbe[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        # stumm gewollt: ein unlesbarer Farbwert aus dem Browser faellt auf die Standardfarbe
        except (TypeError, ValueError):
            pass
        return list(cls.FARBE)
