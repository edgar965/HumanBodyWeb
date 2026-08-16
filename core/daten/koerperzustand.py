# -*- coding: utf-8 -*-
"""Koerperzustand — was aus den Morph-Parametern einer Anfrage entsteht.

WARUM EINE KLASSE (Umbau 15.08.2026): Vorher gab `_build_body_state(request)`
ein Vierertupel `(state, gender, vertices, faces)` zurueck, das durch mehrere
Endpunkte gereicht und dort per Index ausgepackt wurde:

    state, gender, verts, faces = _build_body_state(request)

Vier Werte, die zusammengehoeren, die ihre Funktion verlassen und anderswo
wieder auseinandergenommen werden — das ist der Fall, fuer den die Regel
„eigene Klasse" gilt. Ein Tupel sagt ausserdem nicht, was `[1]` bedeutet, und
beim Erweitern (Geschlecht, Netzdaten, Unterteiler) verschieben sich alle
Indizes stillschweigend.
"""


class Koerperzustand:
    """Der gerechnete Koerper einer Anfrage: Zustand, Geschlecht, Geometrie."""

    __slots__ = ('zustand', 'geschlecht', 'vertices', 'faces', 'koerpertyp')

    def __init__(self, zustand, geschlecht, vertices, faces, koerpertyp=''):
        self.zustand = zustand          # humanbody_core.CharacterState
        self.geschlecht = geschlecht    # 'female' | 'male'
        self.vertices = vertices        # (V, 3) float32 oder None
        self.faces = faces              # (F, 4) oder None
        self.koerpertyp = koerpertyp    # 'Female_Caucasian' ...

    # ------------------------------------------------------------------ lesen

    @property
    def vertex_anzahl(self):
        return 0 if self.vertices is None else len(self.vertices)

    @property
    def hat_geometrie(self):
        return self.vertices is not None and self.faces is not None

    def __iter__(self):
        """Uebergangsweise auspackbar wie das alte Tupel.

        Damit laesst sich `state, gender, verts, faces = koerper` weiter
        schreiben, solange noch nicht jede Aufrufstelle umgestellt ist. Neue
        Stellen benutzen die Namen."""
        return iter((self.zustand, self.geschlecht, self.vertices, self.faces))

    def __repr__(self):
        return ('<Koerperzustand %s %s, %d Vertices>'
                % (self.koerpertyp or '?', self.geschlecht,
                   self.vertex_anzahl))
