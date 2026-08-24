# -*- coding: utf-8 -*-
"""Kleidungsanpassung — eine Vorlage an ein gerechnetes Koerpernetz legen.

Aus `garment_fit` herausgeloest (Umbau 15.08.2026, 151 Zeilen Endpunkt). Dort
standen DREI Zweige fuer die Anpassung, von denen zwei buchstabengleich waren:

    elif fit_mode == 'body_refine':   result = fit_garment(... dieselben Werte)
    else:                             result = fit_garment(... dieselben Werte)

`body_refine` unterschied sich nur im Kommentar. Solche Zweige entstehen, wenn
eine Variante geplant, dann aber nie ausgearbeitet wird — und sie kosten bei
jeder Aenderung doppelte Aufmerksamkeit. Es bleiben zwei echte Wege: um den
Koerper oder um eine Huelle.

Die Knochengewichte kommen ueber den naechsten Koerpervertex. Das stand vorher
in drei Endpunkten je einmal von Hand da (character_cloth, garment_fit,
mh_proxy_fit).
"""
from ..daten.netzantwort import Netzantwort
from ..daten.stoffantwort import Stoffantwort
import base64
import logging

import numpy as np

from ..daten.anpassungsergebnis import Anpassungsergebnis
from .koerperhuelle import Koerperhuelle

logger = logging.getLogger('core')


class Kleidungsanpassung:
    """Passt eine Kleidungsvorlage an einen Koerper an und kodiert das Ergebnis."""

    #: MakeHuman-Vorlagen liegen in einem anderen Koordinatensystem.
    MAKEHUMAN_QUELLE = 'makehuman-assets'

    def __init__(self, vorlage, koerper):
        self.vorlage = vorlage
        self.koerper = koerper            # Koerperzustand
        self.ergebnis = None

    @property
    def koordinatensystem(self):
        return ('makehuman' if self.vorlage.source == self.MAKEHUMAN_QUELLE
                else 'auto')

    # ---------------------------------------------------------------- anpassen

    def anpassen(self, regler, huelle_vertices=None):
        """Vertices/Faces/Normalen der angepassten Kleidung, oder None."""
        from GarmentFitter import fit_garment

        if regler.um_huelle:
            huelle = (huelle_vertices if huelle_vertices is not None
                      else Koerperhuelle.glatt(self.koerper.vertices,
                                               self.koerper.faces))
            roh = Koerperhuelle.allgemein_anpassen(
                self.vorlage.vertices, self.vorlage.faces, huelle,
                offset=regler.abstand, stiffness=regler.steifigkeit,
                color=regler.farbe,
                coordinate_system=self.koordinatensystem)
        else:
            roh = fit_garment(
                self.vorlage.vertices, self.vorlage.faces,
                self.koerper.vertices, body_faces=self.koerper.faces,
                **regler.als_argumente(self.koordinatensystem))
        self.ergebnis = Anpassungsergebnis.aus_dict(roh)
        return self.ergebnis

    # ------------------------------------------------------------------ Antwort

    def als_antwort(self, garment_id, regler):
        """Die JSON-Form fuer den Browser — Feldnamen unveraendert."""
        if self.ergebnis is None:
            return None
        vertices = self.ergebnis.vertices
        antwort = {
            'vertex_count': self.ergebnis.vertexzahl,
            'vertices': Netzantwort.feld(vertices, 'vertices'),
            'face_count': self.ergebnis.flaechenzahl,
            'faces': Netzantwort.feld(self.ergebnis.flaechen_flach(), 'faces'),
            'normals': Netzantwort.feld(self.ergebnis.normals, 'normals'),
            'color': list(regler.farbe),
            'garment_id': garment_id,
            'garment_name': self.vorlage.name,
        }
        antwort.update(self.knochengewichte(vertices))
        return antwort

    def knochengewichte(self, kleidungsvertices):
        """Gewichte des naechstgelegenen Koerpervertex, kodiert.

        Leeres Ergebnis, wenn keine Basisgewichte vorliegen — die Kleidung wird
        dann nicht mitbewegt, ist aber sichtbar.

        Rechnung und Kodierung stehen in `Stoffantwort.gewichte`; dieselbe
        Übertragung gab es am 17.08.2026 an fünf Stellen.
        """
        return Stoffantwort.gewichte(kleidungsvertices, self.koerper.vertices,
                                     self.koerper.geschlecht)

    # ------------------------------------------------------------------ Huelle

    @staticmethod
    def huelle_aus_anfrage(request):
        """Huellvertices aus dem POST-Rumpf, oder None.

        Der Browser schickt sie als base64-Float32 — sie kommen aus der ersten
        Stufe (grobes Anlegen) und ersparen das Neuberechnen."""
        if request.method != 'POST':
            return None
        import json
        try:
            daten = json.loads(request.body or b'{}')
            roh = daten.get('hull_vertices')
            if not roh:
                return None
            return (np.frombuffer(base64.b64decode(roh), dtype=np.float32)
                    .reshape(-1, 3).astype(np.float64))
        except Exception as e:                                    # noqa: BLE001
            logger.error('Huellvertices nicht lesbar: %s', e)
            return None
