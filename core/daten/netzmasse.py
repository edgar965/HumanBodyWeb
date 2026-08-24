# -*- coding: utf-8 -*-
"""Netzmasse — die Maße eines SMPL-X-Netzes samt Bildgröße.

Aus `Fotoausrichtung.automatisch` herausgelöst (17.08.2026): Die Methode hatte
194 Zeilen und rechnete acht Werte aus, die danach durch drei Rechenschritte und
zwei Zweige weitergereicht wurden — `cx`, `cy`, `base_scale`, `mesh_h`, `y_max`,
`y_min`, `img_w`, `img_h`. Genau der Fall aus Kriterium 10: Ein Satz Felder, der
seine Funktion verlässt, gehört in eine Klasse.

WAS `base_scale` IST (und warum es zweimal gebraucht wird)
==========================================================
Der Backvorgang (`bake_texture.py`) projiziert das Netz orthografisch so, dass es
mit 5 % Rand ins Bild passt. `base_scale` ist genau dieser Faktor. Die
Pipelinekameras liefern dagegen einen Maßstab in PIXELN — `scale` im
`body_transform` ist deshalb immer das VERHÄLTNIS der beiden. Wer `base_scale`
anders rechnet als der Backvorgang, bekommt ein Netz, das um einen konstanten
Faktor daneben liegt; deshalb steht die Rechnung an einer Stelle.
"""

import numpy as np


class Netzmasse:
    """Maße des Netzes und des Fotos — einmal gerechnet, überall gelesen."""

    #: Rand, den der Backvorgang um das Netz lässt (5 % je Seite).
    RAND = 0.05

    #: Bildgröße, wenn das Ergebnis der Pipeline keine nennt.
    VORGABE_BREITE = 1920
    VORGABE_HOEHE = 1080

    def __init__(self, vertices, img_w, img_h):
        punkte = np.asarray(vertices)
        self.img_w = img_w
        self.img_h = img_h
        x_min, x_max = punkte[:, 0].min(), punkte[:, 0].max()
        self.y_min = punkte[:, 1].min()          # Füße
        self.y_max = punkte[:, 1].max()          # Kopf
        #: Mitte des Netzes — Bezugspunkt der Projektion.
        self.cx = (x_min + x_max) / 2
        self.cy = (self.y_min + self.y_max) / 2
        self.mesh_w = x_max - x_min
        self.mesh_h = self.y_max - self.y_min
        self.base_scale = min(
            img_w * (1 - 2 * self.RAND) / max(self.mesh_w, 1e-6),
            img_h * (1 - 2 * self.RAND) / max(self.mesh_h, 1e-6))

    @classmethod
    def aus(cls, vertices, cam_data):
        """Maße aus Netzpunkten und den Kameradaten der Pipeline.

        `or` statt Vorgabewert in `.get()` (Review 13.08.2026): Die gespeicherten
        SMPL-X-Parameter enthalten `'image_width': result.get('image_width')` —
        der Schlüssel ist also VORHANDEN und kann None sein. `.get(k, 1920)`
        greift dann NICHT, die Vorgabe ist toter Code, und weiter unten rechnet
        `img_w * (1 - 2*margin)` mit None: TypeError. Bei 0 wird `base_scale` zu 0
        und `s_pixels / base_scale` zu einer Division durch Null. Beides gemessen.
        """
        return cls(vertices,
                   cam_data.get('image_width') or cls.VORGABE_BREITE,
                   cam_data.get('image_height') or cls.VORGABE_HOEHE)

    def bildhoehe_von(self, y_netz, verschiebung):
        """Wohin ein Netz-Y bei diesem `body_transform` im Bild fällt."""
        s = self.base_scale * verschiebung['scale']
        return (self.cy - y_netz) * s + verschiebung['center_y']
