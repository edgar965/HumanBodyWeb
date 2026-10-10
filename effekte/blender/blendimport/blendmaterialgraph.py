# -*- coding: utf-8 -*-
"""Blendmaterialgraph — läuft IN Blender (aus `blendexport.py`): der Knotengraph hinter Base Color, Roughness und Normal eines Materials als JSON.

Der lokale Backer (`core/dienste/hautbacken`) rechnet dieselben Knoten wie Cycles, ohne Blender. Dafür bekommt er den Graphen so, wie Cycles ihn sieht
(`add_nodes_inlined`, `intern/cycles/blender/shader.cpp`, gelesen 10.10.2026, lokal unter `ProjektTemp/_wegwerf/cycles_quelle/b_shader.cpp`):
  * Gruppen werden aufgelöst (nur der aktive Gruppenausgang zählt, ein unverbundener Gruppeneingang gilt mit dem Standardwert der Gruppenbuchse),
  * stumme Knoten und Reroutes werden durch ihre inneren Verbindungen ersetzt, ungültige oder stumme Verbindungen und nicht verfügbare Buchsen zählen nicht.
Wie `blendbacken.py` (`als_emission`) gilt der ERSTE Principled-BSDF des Materials auf oberster Ebene.

Schlüssel: `ziel` (`farbe`, `rauheit`, `normal` → Quelle), `knoten` (`typ`, `eig`, `ein` mit Quellen je Buchsen-Identifier, `ein_art`, `aus_art`), `reihenfolge` (Eltern vor Kindern),
`bilder`. Eine Quelle ist `{'von': [knoten, ausgang]}` oder `{'wert': …, 'art': 'f'|'c'|'v'|'i'|'b'|'r'}` (f Zahl, c Farbe, v Vektor, i/b Ganzzahl, r Drehung).
"""

from blendmaterialbild import Blendmaterialbild
from blendmaterialknoten import Blendmaterialknoten


class Blendmaterialgraph:
    ZIELE = (('farbe', 'Base Color'), ('rauheit', 'Roughness'), ('normal', 'Normal'))

    def __init__(self, exporter):
        self.bilder = Blendmaterialbild(exporter)
        self.knoten = {}
        self.reihenfolge = []
        self.uv_namen = set()
        self.farb_namen = set()

    def bauen(self, mat):
        """Der Graph eines Materials — oder `{'version': 1, 'grund': …}`, wenn es keinen Principled-BSDF auf oberster Ebene hat."""
        baum = mat.node_tree if mat else None
        if baum is None:
            return {'version': 1, 'grund': 'kein Knotenbaum'}
        bsdf = next((k for k in baum.nodes if k.type == 'BSDF_PRINCIPLED'), None)
        if bsdf is None:
            return {'version': 1, 'grund': 'kein Principled BSDF auf oberster Ebene'}
        ziel = {schluessel: self.eingang(bsdf.inputs[name], ()) for schluessel, name in self.ZIELE}
        return {'version': 1, 'ziel': ziel, 'knoten': self.knoten, 'reihenfolge': self.reihenfolge, 'bilder': self.bilder.bilder,
                'uv_namen': sorted(self.uv_namen), 'farb_namen': sorted(self.farb_namen)}

    # ------------------------------------------------------------ Verbindungen

    def eingang(self, buchse, pfad):
        """Die Quelle einer Eingangsbuchse: ein Knotenausgang oder ihr fester Wert."""
        link = next((l for l in buchse.links if l.is_valid and not l.is_muted and l.from_socket.enabled and l.to_socket.enabled), None)
        quelle = self.aufwaerts(link.from_node, link.from_socket, pfad) if link is not None and buchse.enabled else None
        if quelle is not None:
            return quelle
        return {'wert': Blendmaterialknoten.konstante(buchse), 'art': Blendmaterialknoten.kurz(buchse)}

    def aufwaerts(self, knoten, ausgang, pfad):
        """Von einem Knotenausgang aufwärts durch Reroutes, stumme Knoten und Gruppen bis zum Knoten, der rechnet; None = nichts verbunden."""
        if knoten.mute or knoten.type == 'REROUTE':
            innen = next((l for l in knoten.internal_links if l.to_socket.identifier == ausgang.identifier), None)
            return self.eingang(innen.from_socket, pfad) if innen is not None else None
        if knoten.type == 'GROUP_INPUT':
            if not pfad:
                return None
            gruppe = pfad[-1]
            aussen = next((b for b in gruppe.inputs if b.identifier == ausgang.identifier), None)
            return self.eingang(aussen, pfad[:-1]) if aussen is not None else None
        if knoten.type == 'GROUP':
            if knoten.node_tree is None:
                return None
            ende = next((n for n in knoten.node_tree.nodes if n.type == 'GROUP_OUTPUT' and n.is_active_output), None)
            innen = next((b for b in ende.inputs if b.identifier == ausgang.identifier), None) if ende is not None else None
            return self.eingang(innen, pfad + (knoten,)) if innen is not None else None
        return {'von': [self.aufnehmen(knoten, pfad), ausgang.identifier]}

    # ------------------------------------------------------------------ Knoten

    def aufnehmen(self, knoten, pfad):
        """Schlüssel des Knotens im Graphen; legt ihn (und alles stromaufwärts) beim ersten Besuch an."""
        schluessel = '/'.join([g.name for g in pfad] + [knoten.name])
        if schluessel in self.knoten:
            return schluessel
        eintrag = {'typ': knoten.type, 'eig': {}, 'ein': {}, 'ein_art': {}, 'aus_art': {}}
        self.knoten[schluessel] = eintrag
        eintrag['eig'] = Blendmaterialknoten.eigenschaften(knoten)
        if knoten.type == 'TEX_IMAGE':
            eintrag['eig']['bild'] = self.bilder.eintrag(knoten.image) if knoten.image is not None else None
        elif knoten.type in ('UVMAP', 'NORMAL_MAP', 'TANGENT'):
            self.uv_namen.add(eintrag['eig'].get('uv_map') or '')
        elif knoten.type in ('VERTEX_COLOR', 'ATTRIBUTE'):
            self.farb_namen.add(eintrag['eig'].get('layer_name', eintrag['eig'].get('attribute_name', '')) or '')
        for buchse in knoten.outputs:
            if buchse.enabled:
                eintrag['aus_art'][buchse.identifier] = Blendmaterialknoten.kurz(buchse)
        for buchse in knoten.inputs:
            if buchse.enabled:
                eintrag['ein_art'][buchse.identifier] = Blendmaterialknoten.kurz(buchse)
                eintrag['ein'][buchse.identifier] = self.eingang(buchse, pfad)
        self.reihenfolge.append(schluessel)
        return schluessel
