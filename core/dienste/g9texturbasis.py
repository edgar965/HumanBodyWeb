# -*- coding: utf-8 -*-
u"""G9texturbasis — ein Bild der Daz-Bibliothek als UASTC (KTX2, basis_universal) mit allen Mip-Stufen, für /Charakter/ (19.10.2026, `Szenentexturwahl`).

Edgar, 19.10.2026, nach dem KTX2-Versuch auf Mesh3D-AI („würde das auch was bringen für die Charakter seite?“ → „mach das“): auf /Charakter/ wählbar zwischen den
vollen Bildern, dem S3TC-Block (`G9texturblock`, Weg C) und UASTC. Gemessen am Bildersatz von Damira0 (22 Bilder, 17 mit 4096 px, Mesh3D-AI, Probe 41): UASTC ist
fast so genau wie das Original (Gesicht von nah im Mittel 0,054 von 255) und hält die Seite höchstens 0,08 s an, braucht im Browser aber 4,4–5,1 s, bis alle Bilder
auf der Karte sind (der Browser wandelt in Workern nach BC7). Kodiert wird mit `basisu` (BinomialLLC/basis_universal v2.50.0, Apache-2.0, selbst gebaut unter
`tools/basisu_src/bin/basisu.exe`, nicht im Repo) — rund 45 s je 4096er-Bild auf sechs Kernen.

**Darum im Hintergrund:** Liegt die UASTC-Fassung noch nicht, kommt der S3TC-Block (Weg C, 1,9 s beim ersten Mal) und das Bild wird in die Reihe
(`G9texturbasisreihe`) gestellt; beim nächsten Laden der Seite kommt UASTC. Beides sind komprimierte Texturen mit Mip-Stufen — der Browser setzt sie in dasselbe
Texturobjekt (`Genesis9texturblock.setzen`). Fehlt `basisu`, bleibt es beim Block (Warnung im Log, einmal).

Datei `<schluessel>.g9kx`, Zahlen little-endian:  b'G9KX' · uint32 Kopflänge · Kopf (JSON: fassung, breite, hoehe, linear, vorschau {art, bytes}, ktx2) · Vorschau · KTX2
- **Farbraum:** Farbbilder (Albedo) mit `-srgb`, alle anderen (Normalen, Rauheit, Deckkraft …) mit `-linear` (Mip-Stufen linear gefiltert); Normalenkarten nach dem
  Dateinamen zusätzlich `-normal_map` — so wie im Versuch gemessen (`ProjektTemp/_wegwerf/mesh3dai_textur/ktx2_kodieren.py`). Welches Bild ein Farbbild ist, weiß
  nur der Browser; er schreibt es in die Adresse (`raum=lin`, `Texturweg.abfrage`).
- **`-y_flip`:** die Stufen stehen wie beim Block auf dem Kopf (WebGL dreht komprimierte Daten nicht).
- **Seiten als Zweierpotenz** (höchstens 4096) wie beim Block: S3TC/BC7 verlangen Vielfache von 4.
- **Die Vorschau** (1024 px) lesen die Rechnungen im Browser (Hautton, Karten der Scham, Umfärbung), wie beim Block.
"""
import json
import logging
from pathlib import Path

from .g9texturablage import G9texturablage
from .g9texturblock import G9texturblock

logger = logging.getLogger('core')

__all__ = ['G9texturbasis']


class G9texturbasis(G9texturablage):
    u"""UASTC-Fassung mit Vorschau, abgelegt je Original und Farbraum; bis sie liegt, der S3TC-Block."""

    FASSUNG = 1
    ART = 'application/x-g9kx'
    MAGIE = b'G9KX'

    @classmethod
    def ziel_fuer(cls, original, relativ, linear):
        return cls.ziel(original, relativ, 'uastc-lin' if linear else 'uastc', '.g9kx', cls.FASSUNG)

    @classmethod
    def fuer(cls, original, relativ, linear):
        u"""`(Pfad, Art)` — die UASTC-Fassung, wenn sie liegt; sonst der S3TC-Block, und das Bild kommt in die Reihe. `(None, None)` bei einem Fehler."""
        ziel = cls.ziel_fuer(original, relativ, linear)
        if ziel is None:
            return None, None
        if ziel.is_file():
            return ziel, cls.ART
        from .g9texturbasisreihe import G9texturbasisreihe
        G9texturbasisreihe.anstellen(ziel, original, relativ, linear)
        return G9texturblock.fuer(original, relativ)

    @classmethod
    def liegt(cls, original, relativ, linear):
        u"""Liegt die UASTC-Fassung schon? (Teil des ETags im Bündel: sonst bekäme der Browser den Block für immer als 304.)"""
        ziel = cls.ziel_fuer(original, relativ, linear)
        return bool(ziel and ziel.is_file())

    @staticmethod
    def normalenkarte(relativ):
        name = Path(str(relativ)).name.lower()
        return '_nm' in name or name.endswith('_n.jpg') or 'normalmap' in name

    @classmethod
    def packen(cls, bild, ktx2, linear):
        u"""Container aus dem (lesbaren, ungewendeten) Bild für die Vorschau und den KTX2-Bytes."""
        alpha = cls.hat_alpha(bild)
        vorschau, art = G9texturblock._vorschau(bild.convert('RGBA' if alpha else 'RGB'), alpha)
        groesse = (G9texturblock.zweierpotenz(bild.width), G9texturblock.zweierpotenz(bild.height))
        kopf = json.dumps({'fassung': cls.FASSUNG, 'breite': groesse[0], 'hoehe': groesse[1], 'linear': bool(linear),
                           'vorschau': {'art': art, 'bytes': len(vorschau)}, 'ktx2': len(ktx2)}).encode('utf-8')
        return b''.join([cls.MAGIE, len(kopf).to_bytes(4, 'little'), kopf, vorschau, ktx2])
