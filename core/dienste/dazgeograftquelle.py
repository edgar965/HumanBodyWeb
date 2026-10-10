# -*- coding: utf-8 -*-
"""Dazgeograftquelle — das Daz-Geograft „Genesis 9 Anatomical Elements" lesen (10.10.2026).

Edgar kaufte die „Genesis 9 Starter Essentials Expansion" und installierte sie: „baue die Morphs in das UI ein". Das Produkt liegt als
`data/Daz 3D/Genesis 9/Anatomical Elements Male|Female/` und `People/Genesis 9/Anatomy/Daz Originals/Base Anatomy/Genesis 9 Anatomical Elements
Male|Female.duf`. Die Bibliothek gehört Daz Studio und wird nur gelesen (`G9pfade`); was hier entsteht, schreibt `Dazgeograft` als eigenes Stück.

Gemessen am Männlichen (10.10.2026, `geograft_lesen*.py`): 1.516 Punkte in Zentimetern, 1.490 Vierecke in zehn Gruppen (`gen1`–`gen6`, `testes`, `Hip`,
`rThigh`, `lThigh`), `graft`: 25.182 Punkte und 25.156 Flächen der Figur, 71 Schweißpaare `[Punkt des Geografts, Punkt der Figur]` (die Randpunkte liegen im
Median 0,95 mm, höchstens 2,2 mm von den Käfigpunkten der Grundfigur) und 180 verdeckte Käfigflächen der Figur (Mitten bei y 0,80–0,87 m). Das Material hat
keine Textur, nur die Farbe 0,478 grau (`current_value`); die Genitaltexturen liefern Charakterprodukte (Damira, Ursula), keine der Grundfiguren.
Morphe (`Morphs/Daz 3D/Base/`): `body_bs_GenitalRealism_HD3` (1.511 Deltas, Vorgabe 1), `body_bs_Uncircumcised_HD3` (1.509, Vorgabe 0); Länge, Breite und
Hodenasymmetrie sind KNOCHENFORMELN (`Gen2…Gen6` Verschiebung, Skalierung; `rTeste`/`lTeste` Verschiebung), keine Formmorphe.
"""
import numpy as np

__all__ = ['Dazgeograftquelle']


class Dazgeograftquelle:
    CM = 0.01
    ORDNER = {'mann': 'Anatomical Elements Male', 'frau': 'Anatomical Elements Female'}
    DATEI = {'mann': 'Genesis9MaleGenitalia.dsf', 'frau': 'Genesis9FemaleGenitalia.dsf'}
    #: Die Formmorphe liegen unter diesem Pfad neben dem Netz (`<name>.dsf`).
    MORPHE = ('Morphs', 'Daz 3D', 'Base')

    def __init__(self, geschlecht='mann'):
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.dson import G9dson
        from Genesis9.pfade import G9pfade

        if geschlecht not in self.ORDNER:
            raise ValueError('Geschlecht %r — erlaubt: %s' % (geschlecht, ', '.join(self.ORDNER)))
        self.geschlecht = geschlecht
        self.ordner = G9pfade.daten() / 'Daz 3D' / 'Genesis 9' / self.ORDNER[geschlecht]
        datei = self.ordner / self.DATEI[geschlecht]
        if not datei.is_file():
            raise ValueError('Das Geograft fehlt: %s (Genesis 9 Starter Essentials Expansion nicht installiert?)' % datei)
        self.geo = G9dson.lesen(datei).geometrie()
        #: Käfigpunkte des Geografts in Metern (Ruhelage der Grundfigur, Y oben).
        self.punkte = np.asarray(self.geo['vertices']['values'], dtype=np.float64) * self.CM
        self.polys = self.geo['polylist']['values']
        self.materialnamen = self.geo['polygon_material_groups']['values']
        self.uvs, self.ueber = G9basisnetz.uvsatz(self.geo.get('default_uv_set'))
        graft = self.geo.get('graft') or {}
        if not graft.get('hidden_polys'):
            raise ValueError('%s trägt kein Geograft (`graft` fehlt)' % datei.name)
        #: Käfigflächen der Figur, die unter dem Geograft entfallen, und die Schweißpaare `[Punkt des Geografts, Punkt der Figur]`.
        self.versteckt = np.asarray(graft['hidden_polys']['values'], dtype=np.int64)
        self.paare = np.asarray(graft['vertex_pairs']['values'], dtype=np.int64)
        self.figur_punkte = int(graft['vertex_count'])
        self.figur_flaechen = int(graft['poly_count'])

    def gepostet(self, kaefig, pose=1.0):
        """Der Käfig `kaefig` (m) mit Dazs „Default Pose" (`body_ctrl_DefaultPose`, Vorgabe 1) auf der Knochenkette `Gen1 … Gen6`: ohne sie steht das Geograft waagerecht, mit ihr hängt es.
        Gemessen 10.10.2026: `Gen1` 37°, `Gen2` 15,5°, `Gen3` 15,5°, `Gen4` 9° um x (zusammen 77° nach unten), `Gen5`/`Gen6` folgen starr. Skinning mit den Gewichten der Gen-Gelenke
        (`SkinBinding`); jedes Gelenk dreht um seinen Mittelpunkt (`center_point`) im Gelenk des Elternknochens — alle Orientierungen sind 0, die Ruhelagen reine Verschiebungen,
        also gilt `S_k = S_(k−1) · T(c_k) · R_k · T(−c_k)`."""
        return self.posen(kaefig, pose)[0]

    def posen(self, kaefig, pose=1.0):
        """`(gepostet, drehungen)`: wie `gepostet`, dazu je Punkt die Drehmatrix `Σ w_k·R(S_k)` des Skinnings `(N, 3, 3)` — ein Morph, auf der geraden Form gerechnet, wandert damit in
        die Pose (Skinning ist linear in der Punktlage: `Delta_Pose = J · Delta_gerade`)."""
        kaefig = np.asarray(kaefig, dtype=np.float64)
        einheit = np.tile(np.eye(3), (len(kaefig), 1, 1))
        if not pose or not self.ordner.joinpath(*self.MORPHE, 'body_ctrl_DefaultPose.dsf').is_file():     # das weibliche Geograft hat keine Kette
            return kaefig, einheit
        winkel, mitten, gewichte = self._gen_kette()
        aus, rest = np.zeros_like(kaefig), np.ones(len(kaefig))
        drehungen = np.zeros_like(einheit)
        s = np.eye(4)
        for knoten in sorted(mitten):                                      # Gen1 … Gen6: jeder hängt am vorigen
            w = np.radians(winkel.get(knoten, 0.0) * float(pose))
            c, sn = np.cos(w), np.sin(w)
            drehung = np.array([[1, 0, 0], [0, c, -sn], [0, sn, c]], dtype=np.float64)
            mitte = mitten[knoten]
            lokal = np.eye(4)
            lokal[:3, :3] = drehung
            lokal[:3, 3] = mitte - drehung @ mitte
            s = s @ lokal
            gewicht = gewichte.get(knoten)
            if gewicht is None:
                continue
            nummer, wert = gewicht
            aus[nummer] += wert[:, None] * (kaefig[nummer] @ s[:3, :3].T + s[:3, 3])
            drehungen[nummer] += wert[:, None, None] * s[:3, :3]
            rest[nummer] -= wert
        return aus + rest[:, None] * kaefig, drehungen + rest[:, None, None] * einheit

    def _gen_kette(self):
        """`({knoten: Grad um x}, {knoten: Mittelpunkt (m)}, {knoten: (Punktnummern, Gewichte)})` der Kette `Gen1 … Gen6` — aus den Formeln der Default Pose, den Knoten und der Hautbindung."""
        from Genesis9.dson import G9dson

        doc = G9dson.lesen(self.ordner / self.DATEI[self.geschlecht])
        pose = G9dson.lesen(self.ordner.joinpath(*self.MORPHE) / 'body_ctrl_DefaultPose.dsf')
        winkel = {}
        for modifikator in pose.bibliothek('modifier_library'):
            for formel in modifikator.get('formulas') or []:
                knoten, _, kanal = formel['output'].partition('#')[2].partition('?')
                if kanal == 'rotation/x':
                    winkel[knoten] = float(formel['operations'][1]['val'])
        zahl = lambda c: float(c['value'] if isinstance(c, dict) else c)       # noqa: E731 — Mittelpunkt: Liste von {id, value}
        mitten = {n['id']: np.array([zahl(c) for c in n['center_point']]) * self.CM
                  for n in doc.bibliothek('node_library') if n['id'] in ('Gen1', 'Gen2', 'Gen3', 'Gen4', 'Gen5', 'Gen6')}
        haut = next(m for m in doc.modifikatoren() if m.get('id') == 'SkinBinding')['skin']
        gewichte = {}
        for gelenk in haut['joints']:
            knoten = str(gelenk.get('node', '')).lstrip('#')
            if knoten in mitten:
                werte = np.asarray(gelenk['node_weights']['values'], dtype=np.float64)
                gewichte[knoten] = (werte[:, 0].astype(np.int64), werte[:, 1])
        return winkel, mitten, gewichte

    def gruppenpunkte(self, namen):
        """Nummern der Käfigpunkte aller Flächen der Polygongruppen `namen` (Penis: `gen1 … gen6`, Hodensack: `testes`)."""
        gruppen = self.geo['polygon_groups']['values']
        gesucht = {i for i, g in enumerate(gruppen) if g in namen}
        return np.unique([v for p in self.polys if p[0] in gesucht for v in p[2:]]).astype(np.int64)

    def gen_mitte(self, knoten='Gen1'):
        """Mittelpunkt (m) eines Knochens der Kette — der Drehpunkt, die Wurzel des Penis."""
        return self._gen_kette()[1][knoten]

    def morph(self, name):
        """`(N, 3)` Deltas (m) des Formmorphs `name` auf den Käfigpunkten des Geografts."""
        from Genesis9.dson import G9dson

        doc = G9dson.lesen(self.ordner.joinpath(*self.MORPHE) / (name + '.dsf'))
        werte = doc.bibliothek('modifier_library')[0]['morph']['deltas']['values']
        aus = np.zeros((len(self.punkte), 3), dtype=np.float64)
        for nummer, dx, dy, dz in werte:
            aus[int(nummer)] = (dx, dy, dz)
        return aus * self.CM
