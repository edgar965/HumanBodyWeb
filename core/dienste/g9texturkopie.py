# -*- coding: utf-8 -*-
u"""G9texturkopie — ein Bild der Daz-Bibliothek mit höchstens `kante` Pixeln an der längsten Seite (19.10.2026, Weg A von `Mesh3daitexturwahl`).

Gemessen 19.10.2026 an Damira0 (Mesh3D-AI, Tagebuch „Spätabend“): ein Satz aus 22 Bildern, 15 davon 4096², kostete beim Laden 1,7–2,8 s `texSubImage2D` auf dem Hauptfaden;
im Browser auf 1024 verkleinert 0,11–0,15 s, im Feld (668 × 735 px) im Mittel 0,16 von 255 verschieden. Hier geschieht dasselbe auf dem Server, einmal je Bild.

Das Format bleibt das des Originals: JPEG bleibt JPEG (Qualität `QUALITAET`), alles andere wird PNG (Durchsichtigkeit bleibt). Ein Bild, das schon klein genug ist, kommt
unverändert. JPEG wird mit `draft` gelesen (der Dekoder rechnet auf das Doppelte der Kante herunter), danach LANCZOS.
"""
import io

from PIL import Image

from .g9texturablage import G9texturablage

__all__ = ['G9texturkopie']


class G9texturkopie(G9texturablage):
    u"""Verkleinerte Kopie, abgelegt je Original und Kante."""

    #: Steigt, wenn sich der Rechenweg ändert (Teil des Dateinamens).
    FASSUNG = 1
    QUALITAET = 92

    @classmethod
    def fuer(cls, original, relativ, art, kante):
        u"""`(Pfad, Art)` der Kopie — das Original selbst, wenn es nicht größer ist als `kante`; `(None, None)` bei einem Fehler."""
        jpeg = art == 'image/jpeg'
        ziel = cls.ziel(original, relativ, 'kante_%d' % kante, '.jpg' if jpeg else '.png', cls.FASSUNG)
        if ziel is None:
            return None, None
        if not ziel.is_file():
            try:
                with Image.open(original) as bild:
                    klein_genug = max(bild.size) <= kante
            except (OSError, SyntaxError):
                return None, None
            if klein_genug:
                return original, art
        ziel = cls.fertig(ziel, lambda: cls._rechnen(original, kante, jpeg))
        return (ziel, 'image/jpeg' if jpeg else 'image/png') if ziel else (None, None)

    @classmethod
    def _rechnen(cls, original, kante, jpeg):
        with Image.open(original) as bild:
            if bild.format == 'JPEG':
                bild.draft(bild.mode, (2 * kante, 2 * kante))
            bild = cls.lesbar(bild)
            bild.thumbnail((kante, kante), Image.LANCZOS)
        puffer = io.BytesIO()
        if jpeg:
            bild.convert('L' if bild.mode == 'L' else 'RGB').save(puffer, 'JPEG', quality=cls.QUALITAET)
        else:
            bild.save(puffer, 'PNG', compress_level=3)
        return puffer.getvalue()
