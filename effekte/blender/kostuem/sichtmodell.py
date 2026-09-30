# -*- coding: utf-8 -*-
"""Sichtmodell — das zweite Modell einer Runde: der Sichtkörper der Vorlage (`Kostuemsichtkoerper`) mit Fototextur, dazu der Stab.

Das Modell aus Teilen (Mantel, Ärmel, Hut …) ist beweglich und benotbar, aber blockig: Ärmel als Kästen, Haar und Bart als
Platten. Der Sichtkörper hat den Umriss der Vorlage in jeder Ansicht; was innen liegt, malt die Fototextur — von den acht
Ansichten aus sieht er aus wie die Fotos (Kompass auf dem Rücken, Gürtelschnalle, Fläschchen), dazwischen wie eine dicke Puppe.
Er hängt an demselben Rig (Gewichte von ALLEN Körperpunkten, auch den Armen: der Ärmel ist ja in der Hülle) und trägt den Stab der
Teile — der ist zu dünn für die Hülle.

Der Körper der Grundfigur bleibt nur, wo er in der Hülle liegt: Ohne das ragten die Finger der hängenden Hand als bunte Zacken aus
dem Mantel (Bild vom 30.09.2026) — die Hülle kennt keine Finger, sie sind dünner als die Öffnung der Masken.
"""

import bmesh  # pyright: ignore[reportMissingImports]
import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

from effekte.blender.kostuem.fototextur import Fototextur
from effekte.blender.kostuem.kostuemsichtkoerper import Kostuemsichtkoerper
from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Sichtmodell']


class Sichtmodell:
    #: Diese Teile der Teile-Fassung gehören zum Sichtmodell (Namen der dichten Kopien beginnen so).
    BEHALTEN = ('Stab',)
    #: Ein Körperpunkt bleibt, wenn so viele Ansichten der Vorlage ihn für Figur halten (die Hülle selbst verlangt 0,85).
    KOERPER_ANTEIL = 0.6
    #: So weit (m) reicht die Hutspitze der Teile-Fassung unter das obere Ende des Sichtkörpers hinein.
    SPITZE_UEBERLAPP = 0.06

    def __init__(self, bau):
        """`bau`: der `Kostuembau` (Körper, Rig, Haltung, Bindung, Fototextur, Ansichten)."""
        self.bau = bau

    @staticmethod
    def _kopie_ohne(obj, name, weg):
        """Eine Kopie von `obj` ohne die Punkte, für die `weg(punkte)` (Weltpunkte der gestellten Haltung) wahr ist."""
        kopie = obj.copy()
        kopie.data = obj.data.copy()
        kopie.name = name
        kopie[Rohr.MARKE] = True
        bpy.context.collection.objects.link(kopie)
        fertig = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        netz = fertig.to_mesh()
        try:
            punkte, _ = Fototextur._weltdaten(netz, obj.matrix_world)  # noqa: SLF001
        finally:
            fertig.to_mesh_clear()
        indizes = np.flatnonzero(weg(punkte))
        bm = bmesh.new()
        bm.from_mesh(kopie.data)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in indizes], context='VERTS')
        bm.to_mesh(kopie.data)
        bm.free()
        return kopie

    def _koerper_kopie(self, huelle):
        """Der Körper ohne die Punkte außerhalb der Hülle."""
        return self._kopie_ohne(
            self.bau.koerper, 'Koerper_sicht', lambda punkte: huelle.innen(punkte) < self.KOERPER_ANTEIL
        )

    def _spitze_kopie(self, dichte, z_ab):
        """Die Hutspitze der Teile-Fassung, nur oberhalb von `z_ab`: Der Sichtkörper endet dort, wo die Maske dünner wird als ihre
        Öffnung (7 Bildpunkte, gut 2 cm) — die Spitze mit ihrer Biegung fehlte (Bild vom 30.09.2026)."""
        spitze = next((d for d in dichte if d.name.startswith('Hutspitze')), None)
        if spitze is None:
            return []
        return [self._kopie_ohne(spitze, 'Hutspitze_sicht', lambda punkte: punkte[:, 2] < z_ab)]

    def bauen(self, auftrag, huelle, teile, dichte, abbildungen, ordner):
        """→ {'sicht_glb': Dateiname, 'sicht_bilder': {winkel: Datei}, 'sicht_bindung_mm': …}: Sichtkörper bauen, binden,
        einfärben, aus den `textur_winkel` rendern und als GLB ablegen. Die Teile der Teile-Fassung (`teile`) und ihre
        dichten Kopien (`dichte`) bleiben unberührt (nur versteckt, solange gerendert und exportiert wird)."""
        bau = self.bau
        foto = bau.foto
        koerper = Kostuemsichtkoerper(huelle, bau.masse.boden, bau.masse.hoehe, (0.3, 0.3, 0.35)).bauen()
        if not koerper:
            return {}
        # Erst verdichten, DANN binden (bei den Teilen ist es umgekehrt): Eine durchgehende Fläche hängt an Rumpf UND Armen.
        # Wird das grobe Netz gebunden und danach unterteilt, entstehen zwischen zwei Punkten mit verschiedenen Knochen
        # Zwischenpunkte mit gemischten Gewichten, und in der Haltung stehen sie als Zacken aus dem Mantel (Bild vom
        # 30.09.2026). Das dichte Netz in der Haltung ist glatt; seine Gewichte kommen je Punkt vom nächsten Körperpunkt.
        dicht = [foto.verdichten(o) for o in koerper]
        bindung_mm = bau.bindung.binden(dicht, bau.pose.punkte())
        for o in dicht:
            foto.einfaerben(o, abbildungen, ausgewertet=True)
        kopie = self._koerper_kopie(huelle)
        z_oben = max(v.co.z for o in koerper for v in o.data.vertices)
        stab = [d for d in dichte if d.name.startswith(self.BEHALTEN)]
        fremd = [*teile, *[d for d in dichte if d not in stab], *koerper]
        stab += self._spitze_kopie(dichte, z_oben - self.SPITZE_UEBERLAPP)
        aus = {'sicht_bindung_mm': bindung_mm, 'sicht_teile': {o.name: len(o.data.vertices) for o in dicht}}
        bau.koerper.hide_render = True
        for o in fremd:
            o.hide_render = True
        winkel = auftrag.get('textur_winkel')
        if winkel:
            aus['sicht_bilder'] = bau.ansichten.rendern(winkel, ordner, 'sicht_', 'VERTEX')
        bau.koerper.hide_render = False
        for o in fremd:
            o.hide_render = False
        if auftrag.get('glb'):
            for o in [bau.koerper, *fremd]:
                o.hide_viewport = True
            aus['sicht_glb'] = bau._glb(  # noqa: SLF001 — derselbe Export, anderer Dateiname
                bau.rig, kopie, [*dicht, *stab], ordner, auftrag.get('haltung', True), True, 'sicht.glb'
            )
            for o in [bau.koerper, *fremd]:
                o.hide_viewport = False
        return aus
