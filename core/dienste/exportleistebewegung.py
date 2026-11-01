# -*- coding: utf-8 -*-
"""Exportleistebewegung — die BVH der Exportleiste auf die Figur der Seite (31.10.2026, `Exportleiste`).

Derselbe Retarget wie die Abspielleiste im Browser (`fetchRetarget` → `/api/retarget/`, Ziel `genesis9`): Regler und Höhe der Figur schickt die Seite mit (`stellung`), gerechnet wird mit
`Retargetdaten(…, ziel=genesis9, formung=G9formung.aus_abfrage(regler))` — so trägt die exportierte Animation dieselben Knochendrehungen, die die Seite abspielt. `Retargetdaten` legt
das Ergebnis selbst ab (Fingerabdruck aus BVH, Höhe und Formung), hier wird nichts zwischengespeichert.

Die BVH ist ein Pfad oder ein Eintrag der Bibliothek (`Kategorie/Name`, wie die Standardanimation der Seite); die Länge liest `dauer` aus dem Kopf der Datei (Frames × Frame Time),
ohne zu rechnen — sie gibt dem Render die Obergrenze der Länge.
"""

from pathlib import Path

__all__ = ['Exportleistebewegung']


class Exportleistebewegung:
    @staticmethod
    def pfad(roh):
        """Pfad der BVH (Path) aus einem Pfad oder `Kategorie/Name` der Bibliothek — sonst ValueError mit der Meldung für die Seite."""
        from .bvhablage import Bvhablage
        text = str(roh or '').strip().strip('"')
        if not text:
            raise ValueError('Keine BVH-Datei angegeben')
        direkt = Path(text)
        if direkt.is_absolute():
            if direkt.suffix.lower() != '.bvh' or not direkt.is_file():
                raise ValueError('BVH-Datei nicht gefunden: %s' % text)
            return direkt
        geprueft = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / ('%s.bvh' % text))
        if not geprueft or not geprueft.is_file():
            raise ValueError('BVH nicht in der Bibliothek: %s' % text)
        return Path(geprueft)

    @staticmethod
    def dauer(pfad):
        """`(bilder, sekunden)` aus dem Kopf der BVH (`Frames:` und `Frame Time:`) — ValueError, wenn sie fehlen."""
        bilder = zeit = None
        with open(pfad, encoding='utf-8', errors='replace') as d:
            for zeile in d:
                kopf = zeile.strip().lower()
                if kopf.startswith('frames:'):
                    bilder = int(kopf.split(':', 1)[1])
                elif kopf.startswith('frame time:'):
                    zeit = float(kopf.split(':', 1)[1])
                    break
        if not bilder or not zeit:
            raise ValueError('BVH ohne Frames/Frame Time im Kopf: %s' % pfad)
        return bilder, round(bilder * zeit, 3)

    @staticmethod
    def rechnen(pfad, stellung):
        """`Bewegungsspuren.als_dict()` der BVH auf die Figur (`stellung`: {figur, regler, hoehe_m})."""
        from Genesis9.formung import G9formung

        from .retargetdaten import Retargetdaten
        hoehe = float(stellung.get('hoehe_m') or 0) or Retargetdaten.ERSATZHOEHE
        regler = stellung.get('regler') if isinstance(stellung.get('regler'), dict) else {}
        return Retargetdaten(str(pfad), body_height=hoehe, ziel=Retargetdaten.ZIEL_G9, figur=stellung.get('figur') or None,
                             formung=G9formung.aus_abfrage(regler)).holen().als_dict()
