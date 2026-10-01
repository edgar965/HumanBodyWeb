# -*- coding: utf-8 -*-
"""Kleidermodellglb — die Teile eines `Kleidermodellbau` als GLB für die Bühne (30.09.2026, aus `Kleidermodellbau.glb`
herausgelöst, als die Texturen dazukamen).

Ein Teil ohne UV (Körper, Stranghaar-Bänder) wird ein Knoten mit flacher Farbe (Vertexfarben). Ein Teil mit UV wird
seit 01.10.2026 JE MATERIALGRUPPE ein eigener Knoten `<art>__<sorte>__<n>_g<k>__<slug>` — mit Bild (PBR, Farbfaktor =
Daz-Farbe × Tönung), sonst flach, aber mit UV: So kennt die Bühne für jeden Treffer eines Pinselstrichs die Gruppe (der
Slug ist der von `G9kleidtexturen.pfad`, `Haarenginemalen`), und `Haarenginebuehnenmodell.art` liest weiter den Anfang.
Dreiecke, die keine Gruppe nennt, bleiben flach.
"""

import numpy as np

__all__ = ['Kleidermodellglb']


class Kleidermodellglb:
    #: Längste Kante eines Bildes in der GLB (die Runden-GLB soll klein bleiben; die Bühne lädt sie je Runde).
    KANTE = 1024

    @staticmethod
    def _flach(trimesh, punkte, dreiecke, farbe):
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64),
                               faces=np.asarray(dreiecke, dtype=np.int64), process=False)
        rgb = [int(round(float(c) * 255)) for c in np.asarray(farbe)[:3]]
        netz.visual = trimesh.visual.ColorVisuals(
            netz, vertex_colors=np.tile(np.array([*rgb, 255], dtype=np.uint8), (len(netz.vertices), 1)))
        return netz

    @classmethod
    def _bild(cls, pfad):
        from PIL import Image
        with Image.open(pfad) as roh:
            bild = roh.convert('RGB')
            if max(bild.size) > cls.KANTE:
                bild.thumbnail((cls.KANTE, cls.KANTE))
            return bild.copy()

    @classmethod
    def _gruppe(cls, trimesh, punkte, dreiecke, uv, ab, anzahl, textur, farbe):
        """Ein Knoten je Materialgruppe: die Dreiecke der Gruppe auf den Punkten, die sie brauchen — mit Bild
        (`textur`: ab, anzahl, albedo, normalen, faktor) oder flach in `farbe`, in beiden Fällen mit UV."""
        wahl = np.asarray(dreiecke, dtype=np.int64)[ab:ab + anzahl]
        if not len(wahl):
            return None
        nummern, neu = np.unique(wahl.ravel(), return_inverse=True)
        netz = trimesh.Trimesh(vertices=np.asarray(punkte, dtype=np.float64)[nummern],
                               faces=neu.reshape(-1, 3), process=False)
        if textur is not None:
            material = trimesh.visual.material.PBRMaterial(
                baseColorTexture=cls._bild(textur['albedo']),
                baseColorFactor=[int(round(float(c) * 255)) for c in textur['faktor']] + [255],
                metallicFactor=0.0, roughnessFactor=0.85, doubleSided=True)
            if textur.get('normalen') is not None:
                material.normalTexture = cls._bild(textur['normalen'])
        else:
            material = trimesh.visual.material.PBRMaterial(
                baseColorFactor=[int(round(float(c) * 255)) for c in np.asarray(farbe)[:3]] + [255],
                metallicFactor=0.0, roughnessFactor=0.85, doubleSided=True)
        netz.visual = trimesh.visual.TextureVisuals(uv=np.asarray(uv, dtype=np.float64)[nummern], material=material)
        return netz

    @classmethod
    def schreiben(cls, teile, pfad, punkte_je_teil=None):
        from Genesis9.kleidtexturen import G9kleidtexturen
        import trimesh
        szene = trimesh.Scene()
        for i, t in enumerate(teile):
            punkte = t['punkte'] if punkte_je_teil is None else punkte_je_teil[i]
            name = '%s__%s__%d' % (t.get('art'), t.get('sorte') or t.get('art'), i)
            uv = t.get('uv')
            gruppen = [g for g in (t.get('gruppen') or []) if int(g.get('index_anzahl') or 0) >= 3]
            if uv is None or not gruppen:
                szene.add_geometry(cls._flach(trimesh, punkte, t['dreiecke'], t['farbe']), node_name=name)
                continue
            je_ab = {int(g['ab']): g for g in (t.get('textur') or []) if g.get('albedo') is not None}
            belegt = np.zeros(len(t['dreiecke']), dtype=bool)
            for k, g in enumerate(gruppen):
                ab, anzahl = int(g['index_ab']) // 3, int(g['index_anzahl']) // 3
                netz = cls._gruppe(trimesh, punkte, t['dreiecke'], uv, ab, anzahl, je_ab.get(ab), t['farbe'])
                if netz is not None:
                    belegt[ab:ab + anzahl] = True
                    szene.add_geometry(netz, node_name='%s_g%d__%s' % (name, k, G9kleidtexturen.slug(g['name'])))
            if not belegt.all():
                szene.add_geometry(cls._flach(trimesh, punkte, np.asarray(t['dreiecke'])[~belegt], t['farbe']),
                                   node_name=name + '_flach')
        pfad.parent.mkdir(parents=True, exist_ok=True)
        szene.export(str(pfad))
        return pfad
