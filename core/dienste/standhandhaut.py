# -*- coding: utf-8 -*-
"""Standhandhaut — die Hauttextur der Arme und Hände für die Stand-GLB (04.10.2026, Edgar: „die Hände sind unnatürlich, viel zu zart und ohne Textur, viel zu glänzend").

Die Fotokachel der Arme (1004) ist unscharf: keine Hautlinien, keine Knitterfalten, keine Sehnen. `Figurfilm.Handhaut` backt sie aus 3D-Rauschen (Normalenkarte + Farbvariation); diese
Klasse legt das Ergebnis in die glTF-Datei: das Farbbild der Kachel mit der Variation und eine `normalTexture`. DIESELBE Datei liest die Bühne (three.js) und der Film
(`Figurfilm.Gltfmaterial` → Mitsuba `normalmap`), Bühne und Film sehen also dasselbe.

    textur, normale = Standhandhaut(glb).karten(netz, albedo)           # glTF-Texturnummern; `albedo` Pfad der Armkachel (Foto oder Daz-Bild)

Zwischenspeicher `Genesis9/ablage/handhaut/<schluessel>_normal.png` und `…_faktor.png`: die Karten hängen nur an Netz, Gewichten und Skelett der Arme (Reglerstellung der Hände) und
nicht am Foto — gerechnet werden sie nur, wenn sich die Hand ändert (gemessen 04.10.2026: 66 s bei 2048 Pixeln, ohne Zwischenspeicher bei jedem Stand). Das Farbbild wird jedes Mal neu
multipliziert (Zehntelsekunden). `VERSION` hochzählen, wenn sich `Handhaut`, `Handrelief` oder `Handfarbe` ändern. Fehler beim Backen brechen den Stand nicht ab: dann bleibt die Kachel
wie sie war (Log `core`).
"""

import hashlib
import io
import logging

import numpy as np

from .standhandangleich import Standhandangleich
from .standhautdetail import Standhautdetail

logger = logging.getLogger('core')

__all__ = ['Standhandhaut']


class Standhandhaut:
    KACHEL = 1004
    GROESSE = 2048
    #: 4:4:4 — bei 4:2:0 verlöre die Normalenkarte die Schärfe in Rot und Grün (die Neigung steckt dort).
    NORMAL_JPEG_GUETE = 92
    BILD_JPEG_GUETE = 88
    #: Zählt hoch, wenn sich die Karten bei gleicher Eingabe ändern würden. 2 (04.10.2026): dazu die Masken von Hand und Unterarm (`_masken.png`) für den Tonangleich (`Standhandangleich`).
    VERSION = 2
    KNOCHEN = ('hand', 'forearm', 'forearmtwist1', 'forearmtwist2', 'index', 'mid', 'ring', 'pinky', 'thumb')

    def __init__(self, glb):
        self.glb = glb

    # ------------------------------------------------------------------ Schlüssel

    @classmethod
    def schluessel(cls, netz):
        """12 Zeichen: Fingerabdruck von allem, was die Karten bestimmt (Armpunkte auf 0,1 mm, UV, Gewichte, Hand- und Armknochen auf 0,1 mm)."""
        from Figurfilm.handhaut import Handhaut

        h = hashlib.md5(('%d|%d|%s' % (cls.VERSION, cls.GROESSE, Handhaut.__dict__.get('STAERKE'))).encode())
        dr = np.asarray(netz['dreiecke'], dtype=np.int64).reshape(-1, 3)
        gruppen = [g for g in netz['gruppen'] if int(g.get('kachel') or 1001) in (Handhaut.KACHEL, Handhaut.NAGEL_KACHEL)]
        wahl = np.concatenate([dr[int(g['index_ab']) // 3: int(g['index_ab']) // 3 + int(g['index_anzahl']) // 3] for g in gruppen])
        nummern = np.unique(wahl)
        h.update(wahl.tobytes())
        h.update(np.rint(np.asarray(netz['punkte'])[nummern] * 1e4).astype(np.int64).tobytes())
        h.update(np.rint(np.asarray(netz['uv'])[nummern] * 1e5).astype(np.int64).tobytes())
        haut = netz['haut']
        h.update(np.asarray(haut['index']).reshape(-1, 4)[nummern].astype(np.int64).tobytes())
        h.update(np.rint(np.asarray(haut['gewicht']).reshape(-1, 4)[nummern] * 1e3).astype(np.int64).tobytes())
        h.update('|'.join(str(n) for n in haut['knochen']).encode())
        for k in sorted(netz['skelett']['knochen'], key=lambda b: b['name']):
            if k['name'][2:].startswith(cls.KNOCHEN) and k['name'][1] == '_':
                h.update(k['name'].encode())
                h.update(np.rint(np.asarray([k['kopf'] or (0, 0, 0), k['schwanz'] or (0, 0, 0)], dtype=np.float64) * 1e4).astype(np.int64).tobytes())     # Endknochen haben keinen Schwanz
        return h.hexdigest()[:12]

    # ------------------------------------------------------------------ Karten

    @classmethod
    def ordner(cls):
        from Genesis9.pfade import G9pfade

        return G9pfade.ablage() / 'handhaut'

    @staticmethod
    def _masken_bild(masken):
        """Hand-, Unterarmgewicht und belegt (0…1) als 8-Bit-RGB-Bild."""
        from PIL import Image

        return Image.fromarray(np.rint(np.clip(masken, 0.0, 1.0) * 255.0).astype(np.uint8), 'RGB')

    def _gerechnet(self, netz):
        """(normal PIL, faktoren float32, masken float32 (H, W, 3)) — aus dem Zwischenspeicher oder gerechnet und abgelegt."""
        from PIL import Image

        from Figurfilm.handhaut import Handhaut

        schluessel = self.schluessel(netz)
        ordner = self.ordner()
        normal, faktor, maske = (ordner / (schluessel + '_normal.png'), ordner / (schluessel + '_faktor.png'), ordner / (schluessel + '_masken.png'))
        if normal.is_file() and faktor.is_file() and maske.is_file():
            try:
                with Image.open(normal) as n, Image.open(faktor) as f, Image.open(maske) as m:
                    return n.convert('RGB'), Handhaut.faktoren_aus_bild(f), np.asarray(m.convert('RGB'), dtype=np.float32) / 255.0
            except (OSError, ValueError) as fehler:
                logger.warning('Handhaut: Zwischenspeicher %s unlesbar (%s), wird neu gerechnet', schluessel, fehler)
        karten = Handhaut(netz, self.GROESSE).rechnen()
        try:
            ordner.mkdir(parents=True, exist_ok=True)
            Handhaut.faktoren_als_bild(karten.faktoren).save(str(faktor) + '.teil', format='PNG')
            karten.normal.save(str(normal) + '.teil', format='PNG')
            self._masken_bild(karten.masken).save(str(maske) + '.teil', format='PNG')
            for ziel in (faktor, normal, maske):
                ziel.with_name(ziel.name + '.teil').replace(ziel)
        except OSError as fehler:
            logger.warning('Handhaut: Zwischenspeicher %s nicht geschrieben (%s)', schluessel, fehler)
        logger.info('Handhaut %s: %s', schluessel, karten.bericht)
        return karten.normal, karten.faktoren, karten.masken

    def _ablegen(self, bild, qualitaet, **optionen):
        speicher = io.BytesIO()
        bild.save(speicher, format='JPEG', quality=qualitaet, **optionen)
        g = self.glb
        g.gltf.setdefault('images', []).append({'bufferView': g._ablegen(speicher.getvalue()), 'mimeType': 'image/jpeg'})
        g.gltf.setdefault('textures', []).append({'source': len(g.gltf['images']) - 1, 'sampler': 0})
        g.zahl['bilder'] += 1
        return len(g.gltf['textures']) - 1

    @classmethod
    def _netzfarbe(cls, albedo):
        """`(H, W)` bool in der Größe der Kachel: Texel mit Farbe aus dem Netz (`meshfigur_herkunft_<k>.png` neben `meshfigur_<k>.jpg`, Alpha > 0) — None ohne Herkunftskarte (Kachel aus anderer Quelle)."""
        from pathlib import Path

        from PIL import Image

        pfad = Path(str(albedo))
        if not pfad.name.startswith('meshfigur_') or pfad.suffix.lower() != '.jpg':
            return None
        karte = pfad.with_name(pfad.name.replace('meshfigur_', 'meshfigur_herkunft_').replace(pfad.suffix, '.png'))
        if not karte.is_file():
            return None
        with Image.open(karte) as bild:
            hd = np.asarray(bild.convert('RGBA'))[..., 3] > 0
        if hd.shape[0] != cls.GROESSE:
            hd = np.kron(hd, np.ones((cls.GROESSE // hd.shape[0],) * 2, dtype=bool)) if cls.GROESSE % hd.shape[0] == 0 else None
        return hd

    def karten(self, netz, albedo, detail=False, basisnormale=None):
        """(textur, normale): glTF-Texturnummern des Farbbilds mit der Variation und der Normalenkarte. `detail`: vorher die Flecken der Netzkachel dämpfen und feine Zeichnung dazu (`Standhautdetail`, nur vor den
        Iterationen). `basisnormale`: die Daz-Normalenkarte der Armkachel (PIL, `Standhaut.normalenbild`) — das Handrelief liegt darüber (`Standhaut.verrechnen`, seit 07.10.2026). Bei einem Fehler `None` — der Aufrufer
        nimmt dann die Kachel wie sie war."""
        from PIL import Image

        from Figurfilm.handhaut import Handhaut

        try:
            normal, faktoren, masken = self._gerechnet(netz)
            if basisnormale is not None:
                from .standhaut import Standhaut
                normal = Standhaut.verrechnen(basisnormale, normal)
            with Image.open(albedo) as roh:
                if detail and Standhautdetail.gilt(self.KACHEL, albedo):           # ruhigere Flecken des Netzes und feine Zeichnung (Haare, Poren), solange es keine Haut aus den Fotos gibt
                    roh = Standhautdetail.anwenden(roh)
                farbe = Handhaut.albedo_mit(Standhandangleich.anwenden(roh, masken, self._netzfarbe(albedo)), faktoren)      # dann die Daz-Haut im Ton der Netzfarbe, zuletzt die Zeichnung der Hand
            return self._ablegen(farbe, self.BILD_JPEG_GUETE), self._ablegen(normal, self.NORMAL_JPEG_GUETE, subsampling=0)
        except Exception as fehler:  # noqa: BLE001 — die Hautdetails sind eine Zugabe: der Stand muss in jedem Fall entstehen (mit dem Fehler im Log `core`)
            logger.exception('Handhaut: Karten der Arme nicht gebacken (%s: %s) — Kachel bleibt wie sie war', type(fehler).__name__, fehler)
            return None
