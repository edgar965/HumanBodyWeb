# -*- coding: utf-8 -*-
u"""G9texturblock — ein Bild der Daz-Bibliothek als Block für die Grafikkarte (S3TC), mit allen Mip-Stufen (19.10.2026, Weg C von `Mesh3daitexturwahl`).

Ein 4096²-Bild als ImageBitmap kostet im Browser 53–92 ms `texSubImage2D` (einzeln), beim Laden bis 0,57 s; dazu `generateMipmap`. Als S3TC-Block (BC1: 8 Byte, BC3:
16 Byte je 4 × 4 Pixel) geht es ohne Umwandlung auf die Karte, die Mip-Stufen liegen schon fertig darin. Ursprünglich war KTX2/Basis gemeint; dafür fehlt hier der
Kodierer (`basisu` wäre ein Download). Pillow (ab 11.2) kodiert BC1/BC3 selbst; gemessen 19.10.2026: 4096² BC1 1,3 s, BC3 0,9 s (Kodierer `bcn`, ein Faden).
Chrome unter Windows kann S3TC (`WEBGL_compressed_texture_s3tc` und `_srgb`); die Seite prüft das (`Texturweg.anmelden`) und fällt sonst auf Weg A zurück.

Datei `<schluessel>.g9bc`, alle Zahlen little-endian:
    b'G9BC' · uint32 Kopflänge · Kopf (JSON: fassung, format bc1|bc3, breite, hoehe, stufen [[b, h, bytes] …], vorschau {art, bytes}) · Vorschau · Stufe 0 · Stufe 1 · …
- **Die Stufen stehen auf dem Kopf** (unterste Bildzeile zuerst): WebGL dreht komprimierte Daten beim Hochladen nicht (`UNPACK_FLIP_Y` gilt dort nicht); die Bitmaps des
  Vorrats kommen ohnehin gewendet (`imageOrientation: 'flipY'`, `Texture.flipY = false`).
- **Seiten als Zweierpotenz** (höchstens 4096): S3TC verlangt für jede Stufe ein Vielfaches von 4 oder 1/2 — eine Kette aus 2000 px hätte bei 250 px eine ungültige Stufe.
- **Die Vorschau** (`VORSCHAU` px, aufrecht, JPEG oder PNG mit Alpha) ist das, was Rechnungen im Browser lesen (`textur.image`: Hautton, Karten der Scham, Umfärbung):
  ein komprimierter Block lässt sich nicht auf eine Leinwand zeichnen. Diese Rechnungen sehen also dieselbe Auflösung wie bei Weg A.
"""
import io
import json

from PIL import Image

from .g9texturablage import G9texturablage

__all__ = ['G9texturblock']


class G9texturblock(G9texturablage):
    u"""S3TC-Kette mit Vorschau, abgelegt je Original."""

    FASSUNG = 1
    ART = 'application/x-g9bc'
    MAGIE = b'G9BC'
    KANTE_MAX = 4096
    VORSCHAU = 1024
    QUALITAET = 90

    @classmethod
    def fuer(cls, original, relativ):
        u"""`(Pfad, Art)` des Blocks — `(None, None)` bei einem Fehler."""
        ziel = cls.ziel(original, relativ, 'bc', '.g9bc', cls.FASSUNG)
        ziel = cls.fertig(ziel, lambda: cls._rechnen(original)) if ziel else None
        return (ziel, cls.ART) if ziel else (None, None)

    @staticmethod
    def zweierpotenz(n):
        u"""Die größte Zweierpotenz ≤ n (höchstens `KANTE_MAX`)."""
        return min(1 << (max(1, int(n)).bit_length() - 1), G9texturblock.KANTE_MAX)

    @classmethod
    def _rechnen(cls, original):
        with Image.open(original) as bild:
            bild = cls.lesbar(bild)
            bild.load()
        alpha = cls.hat_alpha(bild)
        bild = bild.convert('RGBA' if alpha else 'RGB')
        vorschau, vorschau_art = cls._vorschau(bild, alpha)
        groesse = (cls.zweierpotenz(bild.width), cls.zweierpotenz(bild.height))
        stufe = (bild if bild.size == groesse else bild.resize(groesse, Image.LANCZOS)).transpose(Image.FLIP_TOP_BOTTOM)
        stufen, daten = [], []
        while True:
            block = stufe.tobytes('bcn', 3 if alpha else 1)
            stufen.append([stufe.width, stufe.height, len(block)])
            daten.append(block)
            if stufe.width == 1 and stufe.height == 1:
                break
            stufe = stufe.resize((max(1, stufe.width // 2), max(1, stufe.height // 2)), Image.BOX)
        kopf = json.dumps({'fassung': cls.FASSUNG, 'format': 'bc3' if alpha else 'bc1', 'breite': groesse[0], 'hoehe': groesse[1], 'stufen': stufen,
                           'vorschau': {'art': vorschau_art, 'bytes': len(vorschau)}}).encode('utf-8')
        return b''.join([cls.MAGIE, len(kopf).to_bytes(4, 'little'), kopf, vorschau, *daten])

    @classmethod
    def _vorschau(cls, bild, alpha):
        klein = bild.copy()
        klein.thumbnail((cls.VORSCHAU, cls.VORSCHAU), Image.LANCZOS)
        puffer = io.BytesIO()
        if alpha:
            klein.save(puffer, 'PNG', compress_level=3)
            return puffer.getvalue(), 'image/png'
        klein.save(puffer, 'JPEG', quality=cls.QUALITAET)
        return puffer.getvalue(), 'image/jpeg'
