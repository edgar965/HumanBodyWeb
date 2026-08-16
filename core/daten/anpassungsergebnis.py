# -*- coding: utf-8 -*-
"""Anpassungsergebnis — das Netz, das beim Anpassen eines Kleidungsstuecks
herauskommt.

WARUM eine Klasse (Umbau 16.08.2026, Anforderung 11): Das Ergebnis war ein
Woerterbuch mit vier festen Schluesseln, das zwischen `Kleidungsanpassung.
anpassen()` und `als_antwort()` gereicht und dort fuenfmal per
`self.ergebnis['…']` gelesen wurde. Genau der Fall, den die Regel meint —
anders als etwa das Antwort-Woerterbuch weiter unten, das den Prozess sofort
als JSON verlaesst und deshalb eines bleibt.

Der Anpasser aus GarmentFitter liefert weiterhin ein Woerterbuch; `aus_dict`
nimmt es entgegen. Zusaetzliche Felder gehen dabei nicht verloren.
"""

import numpy as np


class Anpassungsergebnis:
    """Vertices, Dreiecke, Normalen und Farbe eines angepassten Kleidungsstuecks."""

    __slots__ = ('vertices', 'faces', 'normals', 'color', 'weiteres')

    def __init__(self, vertices, faces, normals, color, weiteres=None):
        self.vertices = vertices
        self.faces = faces
        self.normals = normals
        self.color = color
        #: Felder, die ein fremder Anpasser zusaetzlich mitgibt.
        self.weiteres = weiteres or {}

    @classmethod
    def aus_dict(cls, daten):
        """Aus dem Woerterbuch eines Anpassers. None bleibt None."""
        if daten is None:
            return None
        if isinstance(daten, cls):
            return daten
        bekannt = ('vertices', 'faces', 'normals', 'color')
        return cls(*(daten.get(k) for k in bekannt),
                   weiteres={k: v for k, v in daten.items() if k not in bekannt})

    @property
    def vertexzahl(self):
        return int(self.vertices.shape[0])

    @property
    def flaechenzahl(self):
        return int(self.faces.shape[0])

    def flaechen_flach(self):
        """Dreiecksindizes als flaches uint32-Feld — so will es der Browser."""
        return self.faces.ravel().astype(np.uint32)
