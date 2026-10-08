# -*- coding: utf-8 -*-
"""Standdurchlicht — die Dünnheit der Haut als Bild je Kachel, für das Durchlicht im Film (07.10.2026).

Edgar: „mach alle 5" (Prioliste aus „Andere Modelle", Punkt 3: Streuung unter der Haut). Mitsuba 3.9.1 hat kein Streuvolumen für ein offenes Netz (Augen, Mund); der Körper ist keine geschlossene Hülle.
Was es kann: `principledthin` mit diffuser Durchlässigkeit (`diff_trans`, auch als Bild). Wo die Haut dünn ist — Ohren, Nasenflügel, Lippen, Lider, Finger —, scheint Licht von hinten hindurch, wie es Daz' „Durchlicht"
tut (`durchlicht` am Hautsatz: Gewicht 0,85, Farbe 0,98/0,48/0,35). Wo die Haut dick ist (Rumpf, Beine), bleibt sie undurchsichtig. Die Dünnheit je Punkt rechnet `G9dicke` seit dem Browser-Durchlicht
(`netz['dicke']`: 0 = dick … 1 = dünn; gemessen 07.10.2026 an der Basisfigur, 27.087 Punkte: Mittel 0,28, Median 0, 95 % der Punkte der Kopfkachel unter 0,87, Nägel Median 0,97).

Hier wird sie je Kachel in ein 1024²-Graubild gebacken (`G9uvraster`: die Dünnheit wird wie eine Lage je Texel aus den Ecken gemischt), an den Inselrändern fortgesetzt und als PNG in die GLB gelegt — als EXTRA-Textur, die
kein Material nennt: Die Bühne (three.js) lädt sie nicht, der Film liest sie über `extras.figurfilm.durchlicht_textur` (`Gltfmaterial` → `durchlicht_bild`, `Material` → `blendbsdf`).
Die Dünnheit hängt nur an der Basisfigur und nicht an den Reglern (`stufe.skalar(basis.duenne())`), die Bilder liegen deshalb im Genesis-Cache (`ablage/durchlicht/`), je Netz einmal.

    karten = Standdurchlicht.karten(netz)                # {kachel: PIL 'L'}
    textur = Standdurchlicht.ablegen(glb, karten.get(k), k)
"""

import hashlib
import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Standdurchlicht']


class Standdurchlicht:
    GROESSE = 1024
    #: Pixel, um die die Dünnheit über den Inselrand hinaus fortgesetzt wird (bilineare Abtastung und Mip-Stufen sollen am Rand keine Schwärze holen).
    RAND = 4
    #: Zählt hoch, wenn sich das Bild bei gleicher Eingabe ändern würde.
    VERSION = 1

    @classmethod
    def _schluessel(cls, netz):
        h = hashlib.md5(('%d|%d' % (cls.VERSION, cls.GROESSE)).encode())
        for feld in ('dreiecke', 'uv', 'dicke'):
            a = np.ascontiguousarray(np.round(np.asarray(netz[feld], dtype=np.float64), 5))
            h.update(a.tobytes())
        return h.hexdigest()[:12]

    @classmethod
    def _backen(cls, netz):
        """`{kachel: (H, W) float32}` — die Dünnheit je Texel der Kachel, außerhalb der Inseln fortgesetzt."""
        from Genesis9.uvraster import G9uvraster
        from scipy import ndimage

        n = cls.GROESSE
        dicke = np.asarray(netz['dicke'], dtype=np.float64)
        raster = G9uvraster(np.column_stack([dicke, np.zeros_like(dicke), np.zeros_like(dicke)]), netz['dreiecke'], netz['uv'], netz['gruppen'], netz['normalen'], n)
        je = {}
        for g in netz['gruppen']:
            if int(g.get('index_anzahl') or 0) < 3:
                continue
            kachel = int(g.get('kachel') or 1001)
            karte = raster.karte(g)
            bild = je.setdefault(kachel, {'wert': np.zeros((n, n), dtype=np.float32), 'maske': np.zeros((n, n), dtype=bool)})
            neu = karte['maske'] & ~bild['maske']
            bild['wert'][neu] = karte['lage'][..., 0][neu]
            bild['maske'] |= karte['maske']
        aus = {}
        for kachel, b in je.items():
            abstand, (iy, ix) = ndimage.distance_transform_edt(~b['maske'], return_indices=True)
            rand = (~b['maske']) & (abstand <= cls.RAND)
            wert = b['wert'].copy()
            wert[rand] = b['wert'][iy[rand], ix[rand]]
            aus[kachel] = np.clip(wert, 0.0, 1.0)
        return aus

    @classmethod
    def karten(cls, netz):
        """`{kachel: PIL 'L'}` — aus dem Genesis-Cache oder gebacken und abgelegt; `{}` ohne `dicke` im Netz oder bei einem Fehler (der Stand entsteht dann ohne Durchlicht)."""
        from PIL import Image

        if netz.get('dicke') is None:
            return {}
        try:
            from Genesis9.pfade import G9pfade
            ordner = G9pfade.ablage() / 'durchlicht'
            schluessel = cls._schluessel(netz)
            aus, fehlt = {}, False
            for g in netz['gruppen']:
                kachel = int(g.get('kachel') or 1001)
                if kachel in aus:
                    continue
                pfad = ordner / ('%s_%d.png' % (schluessel, kachel))
                if pfad.is_file():
                    with Image.open(pfad) as bild:
                        aus[kachel] = bild.convert('L').copy()
                else:
                    fehlt = True
                    break
            if not fehlt:
                return aus
            aus = {}
            ordner.mkdir(parents=True, exist_ok=True)
            for kachel, wert in cls._backen(netz).items():
                bild = Image.fromarray(np.rint(wert * 255.0).astype(np.uint8), 'L')
                bild.save(str(ordner / ('%s_%d.png.teil' % (schluessel, kachel))), format='PNG')
                (ordner / ('%s_%d.png.teil' % (schluessel, kachel))).replace(ordner / ('%s_%d.png' % (schluessel, kachel)))
                aus[kachel] = bild
            return aus
        except Exception:  # noqa: BLE001 — das Durchlicht ist eine Zugabe: der Stand muss in jedem Fall entstehen
            logger.exception('Standdurchlicht: Dünnheitskarten nicht gebacken — der Stand entsteht ohne Durchlicht')
            return {}

    @staticmethod
    def ablegen(glb, bild, kachel):
        """Nummer der glTF-Textur des Bildes (PNG, je Kachel einmal in der Datei) — None ohne Bild."""
        return None if bild is None else glb._bild_aus(bild, ('durchlicht', int(kachel)))

    @staticmethod
    def anhaengen(glb, material_index, textur):
        """Die Textur an das Material hängen: `extras.figurfilm.durchlicht_textur` (kein Materialfeld, die Bühne ignoriert es)."""
        if textur is not None:
            glb.gltf['materials'][material_index].setdefault('extras', {}).setdefault('figurfilm', {})['durchlicht_textur'] = int(textur)
