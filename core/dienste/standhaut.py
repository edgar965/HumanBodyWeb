# -*- coding: utf-8 -*-
"""Standhaut — die Haut des Stand-Körpers aus der Daz-Bibliothek (07.10.2026): Hautsatz nach Grundfigur, größere Kacheln, die Normalenkarten der Haut.

Edgar: „mach alle 5" (Prioliste aus Hilfe → Andere Modelle: Poren und Mikrodetail, Kachelgröße, Männerhaut). Gelesen am Stand `stand_533347be49c4.glb` von Randy (Runde 64,
`ProjektTemp/_wegwerf/randy/verbessern/stand_pruefen.py`, `kacheln_pruefen.py`, `haut_vergleich.py`):

  * Die Hautkacheln 1001–1003 und 1005 standen mit 1024² in der Datei (51–76 KB je JPEG), nur die Arme (Handhaut) mit 2048². Die Daz-Originale sind 4096². Film und Bühne lesen dieselbe GLB.
  * Randys Grundfigur ist „masculine", die Haut war die Vorgabe `G9Feminine01` (Hautsatz der Basis).
  * Jede Kachel nennt eine 4K-Normalenkarte (`G9…_NM_…`), die der Stand ausließ (Klassenkopf von `Standmodellglb`: „die Bühne soll schnell laden"): echte Poren, Falten und Haarwurzeln,
    UV-gleich mit der Albedo — kein Abbild auf die Kacheln nötig.

Jetzt: der Hautsatz folgt der Grundfigur (`SAETZE`: masculine → `G9 Masculine Skin 01 MAT`, die mittlere Hautfarbe der Kacheln liegt dicht an der Vorgabe: Beine 159/119/104 gegen 160/120/105,
Rumpf 163/122/98 gegen 168/127/107, Arme 165/125/105 gegen 169/127/109, Kopf 152/117/101 gegen 172/131/114; Bräune und Tönung des Films bleiben deshalb, wie sie sind), die Albedo
bleibt bis 2048² (Kopf 4096²: die Nahaufnahmen), die Normalenkarte der Kachel kommt als `normalTexture` in die Datei (2048², JPEG 4:4:4; Film: `Gltfmaterial` → Mitsuba `normalmap`, Bühne: three.js).
Auf den Armen liegt das Handrelief (`Handhaut`) über der Daz-Karte (`verrechnen`: Neigungen addiert). Dazu je Kachel die Dünnheit der Haut für das Durchlicht im Film (`Standdurchlicht`).

    Standhaut.legen(glb, netz, kacheln)        # früher `Standmodellglb.koerper`
"""

import io
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Standhaut']


class Standhaut:
    #: Zählt hoch, wenn sich ändert, was diese Klasse in die Datei legt (Fassung des Stands, `Engine2d3dKleiderstandmodell.fassung`).
    #: 2 (07.10.2026): dazu die Dünnheitskarte je Kachel für das Durchlicht im Film (`Standdurchlicht`).
    VERSION = 2
    #: Grundfigur der Optionen (`figur.basis`) → Hautsatz der Starter Essentials (`G9hautpresets`); was fehlt, behält die Vorgabe der Basis.
    SAETZE = {'masculine': 'G9 Masculine Skin 01 MAT'}
    #: Längste Kante der Albedo je Kachel in Pixeln (kleinere Bilder bleiben, wie sie sind) und der Normalenkarte.
    KANTE = 2048
    KANTE_JE_KACHEL = {1001: 4096}
    KANTE_NORMALE = 2048
    ALBEDO_JPEG_GUETE = 88
    #: 4:4:4 — bei 4:2:0 verlöre die Normalenkarte die Schärfe in Rot und Grün (die Neigung steckt dort).
    NORMAL_JPEG_GUETE = 92

    # ------------------------------------------------------------------ Hautsatz

    @classmethod
    def preset(cls, job):
        """Der Hautsatz zur Grundfigur des Auftrags (`figur.basis`) oder None (Vorgabe der Basis)."""
        from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

        return cls.SAETZE.get(str(Engine2d3dKleideroptionen.figur(getattr(job, 'optionen', None)).get('basis')))      # `getattr`: Attrappen der Tests tragen keine Optionen

    @classmethod
    def fassung(cls, job):
        """Alles, was die Haut des Stands bestimmt — geht in die Fassung ein (Regel artefakte-benennen)."""
        return [cls.VERSION, cls.preset(job), cls.KANTE, sorted(cls.KANTE_JE_KACHEL.items()), cls.KANTE_NORMALE]

    # ------------------------------------------------------------------ Bilder

    @classmethod
    def normalenbild(cls, bilder):
        """PIL RGB: die Normalenkarte der Kachel (`bilder['normalen']`, Daz `_NM_`) auf `KANTE_NORMALE` — None ohne Karte oder bei einem Lesefehler (dann bleibt die Kachel glatt wie bisher)."""
        from Genesis9.material import G9material
        from PIL import Image

        if not (bilder or {}).get('normalen'):
            return None
        datei = G9material.datei(bilder['normalen'])
        if datei is None:
            return None
        try:
            with Image.open(datei) as roh:
                bild = roh.convert('RGB')
            if max(bild.size) > cls.KANTE_NORMALE:
                bild = bild.resize((cls.KANTE_NORMALE, cls.KANTE_NORMALE), Image.LANCZOS)
            return bild
        except (OSError, ValueError) as fehler:
            logger.warning('Standhaut: Normalenkarte %s nicht gelesen (%s)', datei, fehler)
            return None

    @staticmethod
    def verrechnen(unten, oben):
        """Zwei Normalenkarten (PIL RGB, Tangentenraum, flach = 128/128/255) zu einer: die Neigungen addiert, die Höhe der unteren (UDN-Mischung).

        `unten` ist die Daz-Karte der Haut, `oben` das Handrelief (`Handhaut`); gleiche Größe wird hergestellt (`oben` gibt sie vor)."""
        from PIL import Image

        if unten.size != oben.size:
            unten = unten.resize(oben.size, Image.BICUBIC)
        a = np.asarray(unten, dtype=np.float32) / 127.5 - 1.0
        b = np.asarray(oben, dtype=np.float32) / 127.5 - 1.0
        n = np.stack([a[..., 0] + b[..., 0], a[..., 1] + b[..., 1], a[..., 2]], axis=-1)
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        return Image.fromarray(np.rint(np.clip((n * 0.5 + 0.5) * 255.0, 0, 255)).astype(np.uint8), 'RGB')

    @staticmethod
    def ablegen(glb, bild, qualitaet, **optionen):
        """Ein PIL-Bild als JPEG in die GLB legen → Nummer der glTF-Textur."""
        speicher = io.BytesIO()
        bild.save(speicher, format='JPEG', quality=qualitaet, **optionen)
        glb.gltf.setdefault('images', []).append({'bufferView': glb._ablegen(speicher.getvalue()), 'mimeType': 'image/jpeg'})
        glb.gltf.setdefault('textures', []).append({'source': len(glb.gltf['images']) - 1, 'sampler': 0})
        glb.zahl['bilder'] += 1
        return len(glb.gltf['textures']) - 1

    @classmethod
    def normale(cls, glb, bild):
        """Nummer der glTF-Textur der Normalenkarte `bild` — None ohne Bild."""
        return None if bild is None else cls.ablegen(glb, bild, cls.NORMAL_JPEG_GUETE, subsampling=0)

    # ------------------------------------------------------------------ Körper

    @classmethod
    def legen(cls, glb, netz, kacheln):
        """Der Körper je UDIM-Kachel ein Netz: das gebackene Foto (`kacheln` {1001: Pfad}), sonst die Daz-Haut der ersten Gruppe der Kachel (mit ihrer Farbe); dazu die Normalenkarte der Haut.
        (Bis 07.10.2026 `Standmodellglb.koerper`.)"""
        from Genesis9.material import G9material

        from .standdurchlicht import Standdurchlicht
        from .standhandhaut import Standhandhaut
        from .standhautdetail import Standhautdetail
        glb._koerper = netz
        durchlicht = Standdurchlicht.karten(netz)              # Dünnheit der Haut je Kachel (Ohren, Nase, Lippen, Finger): der Film lässt dort Licht hindurch
        dreiecke = np.asarray(netz['dreiecke'], dtype=np.int64).reshape(-1, 3)
        uv = glb._uv(netz['uv'])
        uv[:, 0] = np.clip(uv[:, 0], 0.0, 1.0)
        haut = glb._haut(netz['haut'], len(netz['punkte']))
        je_kachel = {}
        for g in netz['gruppen']:
            von = int(g['index_ab']) // 3
            je_kachel.setdefault(int(g.get('kachel') or 1001), []).append((von, von + int(g['index_anzahl']) // 3, g))
        for kachel, stuecke in sorted(je_kachel.items()):
            bilder = stuecke[0][2].get('bilder') or {}
            foto = kacheln.get(kachel)
            albedo = foto or (G9material.datei(bilder['albedo']) if bilder.get('albedo') else None)
            faktor = (1.0, 1.0, 1.0) if foto else glb._zahl(bilder.get('farbe'), (1.0, 1.0, 1.0))
            wahl = np.concatenate([dreiecke[a:b] for a, b, _ in stuecke])
            karte = cls.normalenbild(bilder)
            hand = Standhandhaut(glb).karten(netz, albedo, detail=glb.hautdetail, basisnormale=karte) if kachel == Standhandhaut.KACHEL and albedo else None     # Arme, Hände: Hautlinien, Falten, Sehnen und Farbe (`Handhaut`)
            detail = (Standhautdetail.karte(glb, albedo) if glb.hautdetail and albedo and kachel != Standhandhaut.KACHEL and Standhautdetail.gilt(kachel, albedo)
                      else None)                     # Beine: ruhigere Flecken, Poren und Haare (vor den Iterationen)
            textur, normale = hand or ((detail if detail is not None else glb._bild(albedo, kante=cls.KANTE_JE_KACHEL.get(kachel, cls.KANTE))), cls.normale(glb, karte))
            vorher = len(glb.gltf['materials'])
            glb._netz('koerper__koerper__0_k%d' % kachel, netz['punkte'], wahl, netz.get('normalen'), uv, haut,
                      textur, faktor, zweiseitig=False, normale=normale)
            if len(glb.gltf['materials']) > vorher:
                Standdurchlicht.anhaengen(glb, vorher, Standdurchlicht.ablegen(glb, durchlicht.get(kachel), kachel))
