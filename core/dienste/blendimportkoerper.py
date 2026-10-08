# -*- coding: utf-8 -*-
"""Blendimportkoerper — das Körpernetz einer .blend als GLB für „Mesh to 3D" (Körper + Augen, eine Textur).

„Mesh to 3D" liest EIN Netz mit EINER Textur (`Meshfigurscan.laden`: trimesh, `baseColorTexture`). Der Körper von
„cute girl" hat Löcher an den Augen (138 Randkanten über 1,54 m, gemessen 08.10.2026), die Augäpfel sind eigene Netze
mit eigenem Bild. Ohne sie sähe die Gesichtserkennung (FaceLandmarker auf den Renderings) leere Augenhöhlen. Deshalb
kommen Körper und Augen in EINE GLB mit einem Atlas: oben die Körpertextur auf `ATLAS_PX` verkleinert, unten ein Streifen
mit dem Augenbild. Kleider und Haar bleiben draußen — „Mesh to 3D" sieht den nackten Körper, also gibt es nichts zu
trennen (Optionen in `Blendimportfigur`).

ACHSEN: Blender rechnet Meter, Z oben; glTF Y oben. Wie Blenders glTF-Export: (x, y, z) → (x, z, −y). Dieselbe Abbildung
nimmt `Blendimportlage` für Kleider und Haar, damit sie mit der Lage aus „Mesh to 3D" (`scan_lage.npz`) zusammenpassen.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportkoerper']


class Blendimportkoerper:
    #: Kante der Körpertextur im Atlas — für Erkennung und Anpassung reicht sie; gebacken wird aus dem Original.
    ATLAS_PX = 4096
    AUGE_PX = 1024
    DATEI = 'koerper.glb'

    def __init__(self, ablage, inventar, rollen):
        self.ablage = ablage
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen

    @staticmethod
    def gltf(punkte):
        """Blender-Achsen → glTF-Achsen."""
        p = np.asarray(punkte, dtype=np.float64)
        return np.column_stack([p[:, 0], p[:, 2], -p[:, 1]])

    def _laden(self, name):
        netz = self.inventar[name]
        with np.load(self.ablage.export(netz['datei'])) as d:
            return {k: d[k] for k in d.files}, netz

    @staticmethod
    def _bild(pfad, kante):
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None          # 8192² sind gewollt
        with Image.open(pfad) as bild:
            return np.asarray(bild.convert('RGB').resize((kante, kante), Image.LANCZOS), dtype=np.uint8)

    def atlas(self, koerperbild, augenbild):
        """(H, W, 3): oben der Körper (Kante × Kante), darunter links das Augenbild."""
        k, a = self.ATLAS_PX, self.AUGE_PX
        aus = np.full((k + a, k, 3), 255, dtype=np.uint8)
        aus[:k] = self._bild(koerperbild, k)
        if augenbild:
            aus[k:, :a] = self._bild(augenbild, a)
        return aus

    def uv_koerper(self, uv):
        k, a = self.ATLAS_PX, self.AUGE_PX
        return np.column_stack([uv[:, 0], (a + uv[:, 1] * k) / (k + a)])

    def uv_auge(self, uv):
        k, a = self.ATLAS_PX, self.AUGE_PX
        return np.column_stack([uv[:, 0] * a / k, uv[:, 1] * a / (k + a)])

    @staticmethod
    def ecken(punkte, dreiecke, uv_ecken):
        """Punkte je (Punkt, UV)-Paar — glTF trägt UV je Punkt, an UV-Nähten also doppelte Punkte."""
        schluessel = np.column_stack([dreiecke.reshape(-1), np.round(uv_ecken.reshape(-1, 2) * 1e6)])
        einzig, index = np.unique(schluessel, axis=0, return_inverse=True)
        uv = np.zeros((len(einzig), 2))
        uv[index.reshape(-1)] = uv_ecken.reshape(-1, 2)
        return punkte[einzig[:, 0].astype(np.int64)], index.reshape(-1, 3), uv

    def schreiben(self):
        import trimesh
        from PIL import Image

        koerper = next(r for r in self.rollen if r['rolle'] == 'koerper')
        augen = [r for r in self.rollen if r['rolle'] == 'auge']
        teile, uvs, flaechen, versatz = [], [], [], 0
        d, netz = self._laden(koerper['name'])
        p, f, uv = self.ecken(self.gltf(d['punkte']), d['dreiecke'], d['uv_ecken'])
        teile.append(p)
        uvs.append(self.uv_koerper(uv))
        flaechen.append(f)
        versatz += len(p)
        koerperbild = (netz['materialien'][0] or {}).get('farbe') if netz['materialien'] else None
        if not koerperbild:
            raise ValueError('Der Körper „%s" hat kein Bild am Farbeingang' % koerper['name'])
        augenbild = None
        for auge in augen:
            d, netz = self._laden(auge['name'])
            augenbild = augenbild or ((netz['materialien'] or [{}])[0] or {}).get('farbe')
            p, f, uv = self.ecken(self.gltf(d['punkte']), d['dreiecke'], d['uv_ecken'])
            teile.append(p)
            uvs.append(self.uv_auge(uv))
            flaechen.append(f + versatz)
            versatz += len(p)
        bild = Image.fromarray(self.atlas(koerperbild, augenbild))
        material = trimesh.visual.material.PBRMaterial(baseColorTexture=bild, metallicFactor=0.0, roughnessFactor=1.0)
        visuell = trimesh.visual.TextureVisuals(uv=np.vstack(uvs), material=material)
        netz = trimesh.Trimesh(np.vstack(teile), np.vstack(flaechen), visual=visuell, process=False)
        ziel = self.ablage.arbeit(self.DATEI)
        netz.export(str(ziel))
        logger.info('Blender-Import %s: Körpernetz %s (%d Punkte, %d Augen)', self.ablage.kennung, ziel,
                    len(netz.vertices), len(augen))
        return {'datei': str(ziel), 'punkte': int(len(netz.vertices)), 'dreiecke': int(len(netz.faces)),
                'augen': len(augen), 'atlas': list(bild.size)}
