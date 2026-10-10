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

    def __init__(self, ablage, inventar, rollen, ergaenzen=False):
        self.ablage = ablage
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        #: Einstellung „Körper unter Kleidung ergänzen" — nur die GLB für „Mesh to 3D" bekommt die Beine aus dem Kleidungsnetz;
        #: die Haut (`Blendimporthaut`) bleibt beim Original (`Blendimportkoerperergaenzung`).
        self.ergaenzen = ergaenzen

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

    def atlas(self, koerperbild, augenbild, hautkachel=None):
        """(H, W, 3): oben der Körper (Kante × Kante), darunter links das Augenbild, rechts daneben die Haut der Ergänzung."""
        k, a = self.ATLAS_PX, self.AUGE_PX
        aus = np.full((k + a, k, 3), 255, dtype=np.uint8)
        aus[:k] = self._bild(koerperbild, k)
        if augenbild:
            aus[k:, :a] = self._bild(augenbild, a)
        if hautkachel is not None:
            aus[k:, a:a + self.HAUT_PX] = hautkachel
        return aus

    #: Genesis-9-Standardhaut (Feminine 01, Körper-Diffuse), ruhiger Ausschnitt (Streuung 0,48, Mittel 174/136/117) — gemessen
    #: 10.10.2026 (`ProjektTemp/_wegwerf/asian/g9haut_ausschnitt.py`). Die Datei liegt in der Daz-Bibliothek, nicht im Repo.
    HAUT_QUELLE = 'Runtime/Textures/DAZ/Characters/Genesis9/Base/Feminine_01/G9Feminine01_Body_D_1002.jpg'
    HAUT_AUSSCHNITT = (1792, 0, 512)
    HAUT_FARBE = (174, 136, 117)
    HAUT_PX = 1024
    #: Höhe, nach der sich die Hautkachel am Bein wiederholt (m).
    HAUT_WIEDERHOLUNG_M = 0.5

    def _hautkachel(self):
        """Die Genesis-9-Haut als HAUT_PX-Kachel für den Atlas. Fehlt die Datei, eine flache Farbe mit Warnung im Log."""
        from Genesis9.pfade import G9pfade
        from PIL import Image

        pfad = G9pfade.finden(self.HAUT_QUELLE)
        if not pfad.is_file():
            logger.warning('Körperergänzung: Genesis-9-Haut %s fehlt — flache Hautfarbe %s', pfad, self.HAUT_FARBE)
            return np.full((self.HAUT_PX, self.HAUT_PX, 3), self.HAUT_FARBE, dtype=np.uint8)
        Image.MAX_IMAGE_PIXELS = None
        with Image.open(pfad) as bild:
            ausschnitt = bild.convert('RGB').crop((self.HAUT_AUSSCHNITT[0], self.HAUT_AUSSCHNITT[1],
                                                   self.HAUT_AUSSCHNITT[0] + self.HAUT_AUSSCHNITT[2],
                                                   self.HAUT_AUSSCHNITT[1] + self.HAUT_AUSSCHNITT[2]))
        kachel = np.asarray(ausschnitt.resize((self.HAUT_PX // 2, self.HAUT_PX // 2), Image.LANCZOS), dtype=np.uint8)
        return np.tile(kachel, (2, 2, 1))

    def uv_haut(self, winkel, hoehe):
        """UV im Atlas je Punkt: Winkel um die Stückmitte → x im Hautfeld, Höhe → y (wiederholt sich alle HAUT_WIEDERHOLUNG_M)."""
        k, a = self.ATLAS_PX, self.AUGE_PX
        fu = (np.asarray(winkel, dtype=np.float64) / (2 * np.pi)) % 1.0
        fv = (np.asarray(hoehe, dtype=np.float64) / self.HAUT_WIEDERHOLUNG_M) % 1.0
        ux = (a + self.HAUT_PX * fu) / k
        uy = self.HAUT_PX * (1.0 - fv) / (k + a)
        return np.column_stack([ux, uy])

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
        ergaenzt = None
        hautkachel = None
        if self.ergaenzen:
            from .blendimportkoerperergaenzung import Blendimportkoerperergaenzung

            ergaenzt = Blendimportkoerperergaenzung(self.ablage, {'netze': list(self.inventar.values())}, self.rollen).ergaenzen(d)
        if ergaenzt:
            hautkachel = self._hautkachel()
            # Haut aus der Genesis-9-Standardhaut, zylindrisch um die Stückmitte gelegt (Winkel → x, Höhe → y, Kachel wiederholt sich).
            uv_punkt = self.uv_haut(ergaenzt['winkel'], ergaenzt['hoehe'])
            p, f, uv = self.ecken(self.gltf(ergaenzt['punkte']), ergaenzt['dreiecke'], uv_punkt[ergaenzt['dreiecke']])
            teile.append(p)
            uvs.append(uv)
            flaechen.append(f + versatz)
            versatz += len(p)
        augenbild = None
        for auge in augen:
            d, netz = self._laden(auge['name'])
            augenbild = augenbild or ((netz['materialien'] or [{}])[0] or {}).get('farbe')
            p, f, uv = self.ecken(self.gltf(d['punkte']), d['dreiecke'], d['uv_ecken'])
            teile.append(p)
            uvs.append(self.uv_auge(uv))
            flaechen.append(f + versatz)
            versatz += len(p)
        bild = Image.fromarray(self.atlas(koerperbild, augenbild, hautkachel))
        material = trimesh.visual.material.PBRMaterial(baseColorTexture=bild, metallicFactor=0.0, roughnessFactor=1.0)
        visuell = trimesh.visual.TextureVisuals(uv=np.vstack(uvs), material=material)
        netz = trimesh.Trimesh(np.vstack(teile), np.vstack(flaechen), visual=visuell, process=False)
        ziel = self.ablage.arbeit(self.DATEI)
        netz.export(str(ziel))
        logger.info('Blender-Import %s: Körpernetz %s (%d Punkte, %d Augen)', self.ablage.kennung, ziel,
                    len(netz.vertices), len(augen))
        return {'datei': str(ziel), 'punkte': int(len(netz.vertices)), 'dreiecke': int(len(netz.faces)),
                'augen': len(augen), 'atlas': list(bild.size),
                'ergaenzt': {'punkte': int(len(ergaenzt['punkte'])), 'kleider': ergaenzt['kleider'],
                             'haut': 'Genesis-9-Standardhaut' if hautkachel is not None else None} if ergaenzt else None}
