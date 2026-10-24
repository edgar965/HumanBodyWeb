# -*- coding: utf-8 -*-
"""Architekturai2d3dnetz — das vorgeschlagene Netz von 2d-3d-AI (Weg B: Fotos direkt → KI → Genesis-Modell), Schicht für Schicht (24.10.2026).

Edgar: „erstelle eine neue Seite hilfe - Architektur - 2d-3d-AI in der Art von /hilfe/architektur/mesh3dai/ … inkl. grafischer Darstellung des neuronalen Netzes“. Das Netz ist ein VORSCHLAG,
nicht gebaut und nicht trainiert. Die Gewichte je Schicht sind aus den Maßen GERECHNET (Linear: ein·aus + aus; Aufmerksamkeit: 4·d² + 4·d; MLP: 2·d·m + d + m; LayerNorm: 2·d), nicht gemessen.
Das Rückgrat (Sapiens2-0.4B) zählt nicht mit: es ist vortrainiert und bleibt in Stufe 1 eingefroren; „0,4 Mrd.“ ist die Angabe aus dem Modellnamen.

Zeile: `(art, titel, was, eingang, ausgang, neuronen, gewichte, stichwort)` — `neuronen` = Zahlen, die EIN Token (bzw. ein Pixel, eine Figur) nach der Schicht trägt.
"""

__all__ = ['Architekturai2d3dnetz']


class Architekturai2d3dnetz:
    #: Maße (alle Setzungen dieses Vorschlags, keine Messungen)
    ANSICHTEN = 4                  # Exporte; echte Fotos bis 8 (dieselben Gewichte, mehr Tokens)
    BILD = (512, 384)              # Höhe × Breite je Foto (3 : 4 wie die Exporte)
    FELD = 16                      # Bildfeld des Rückgrats (Pixel je Kante)
    BREITE = 512                   # Breite der Tokens hinter der Projektion
    RUECKGRAT_BREITE = 1024        # Breite der Merkmale des Rückgrats — Setzung für die Rechnung, an Sapiens2-0.4B NICHT nachgelesen
    BUENDEL = 64                   # lernbare Anfragen je Ansicht
    SCHICHTEN_FUSION = 6
    MLP = 2048
    WINKEL_FREQUENZEN = 16         # Fourier-Einbettung des Kamerawinkels (sin, cos je Frequenz)
    KNOCHEN = 138                  # Genesis-9-Rig von Mesh3D-AI (`Mesh3dairig`)
    FORMREGLER = 1323              # `3DObjects/mesh3dai/formregler_v6.json` → `regler` (gelesen 24.10.2026)
    KLEIDUNG = 544                 # Garderobe der Charakter-Seite, Art „kleidung“ (API, 24.10.2026)
    HAAR = 32                      # Art „haar“ (API, 24.10.2026)

    @staticmethod
    def linear(ein, aus):
        return ein * aus + aus

    @classmethod
    def block(cls, d, m):
        """Eine Transformer-Schicht: Selbstaufmerksamkeit + MLP + zwei LayerNorm."""
        return 4 * d * d + 4 * d + 2 * d * m + d + m + 4 * d

    @classmethod
    def tokens(cls):
        return (cls.BILD[0] // cls.FELD) * (cls.BILD[1] // cls.FELD)

    @classmethod
    def schichten(cls):
        d, t, v = cls.BREITE, cls.tokens(), cls.ANSICHTEN
        einbettung = cls.linear(2 * cls.WINKEL_FREQUENZEN, d)
        buendel = cls.BUENDEL * d + (4 * d * d + 4 * d) + 2 * d + cls.linear(cls.RUECKGRAT_BREITE, d)
        figur = d + (4 * d * d + 4 * d) + 2 * d
        return (
            ('eingabe', 'Fotos', 'die Fotos des Jobs, je Pixel Farbe und Maske (Figur ja/nein)', '%d × %d × %d' % (v, *cls.BILD), '%d × %d × %d × 4' % (v, *cls.BILD), 4, 0,
             'RGB + Maske'),
            ('rueckgrat', 'Rückgrat', 'Sapiens2-0.4B, ein ViT für Menschenbilder (Feld %d px), je Ansicht dieselben Gewichte, eingefroren' % cls.FELD, 'je Ansicht 4 Kanäle',
             '%d Tokens je Ansicht' % t, cls.RUECKGRAT_BREITE, 0, '%d Felder je Foto' % t),
            ('versteckt', 'Bündel', 'Projektion %d → %d, Winkel des Fotos dazu (Fourier, %d Frequenzen), %d lernbare Anfragen lesen die %d Tokens (Kreuzaufmerksamkeit)' % (
                cls.RUECKGRAT_BREITE, d, cls.WINKEL_FREQUENZEN, cls.BUENDEL, t), '%d × %d' % (t, cls.RUECKGRAT_BREITE), '%d × %d je Ansicht' % (cls.BUENDEL, d), d,
             buendel + einbettung, '%d je Ansicht' % cls.BUENDEL),
            ('versteckt', 'Fusion 1–%d' % cls.SCHICHTEN_FUSION, 'Transformer über alle Ansichten zugleich (%d Tokens), so sieht jedes Token Vorder-, Seiten- und Rückansicht' % (v * cls.BUENDEL),
             '%d × %d' % (v * cls.BUENDEL, d), '%d × %d' % (v * cls.BUENDEL, d), d, cls.SCHICHTEN_FUSION * cls.block(d, cls.MLP), '%d Schichten, MLP %d' % (cls.SCHICHTEN_FUSION, cls.MLP)),
            ('figur', 'Figur', 'ein lernbares Token liest alle Tokens der Fusion: die ganze Figur in einem Vektor', '%d × %d' % (v * cls.BUENDEL, d), d, d, figur, 'ein Vektor je Figur'),
            ('ausgabe', 'Haltung', 'Daz-Winkel aller %d Knochen (in den Grenzen von Genesis 9 wie bei Mesh3D-AI) + Wurzel (Drehung 6D, Lage 3)' % cls.KNOCHEN, d, cls.KNOCHEN * 3 + 9,
             cls.KNOCHEN * 3 + 9, cls.linear(d, 1024) + cls.linear(1024, cls.KNOCHEN * 3 + 9), '%d × 3 + 9' % cls.KNOCHEN),
            ('ausgabe', 'Form', 'die Genesis-Formregler von Mesh3D-AI (Wirkung je Regler bekannt, `formregler_wirkung_v6.npz`)', d, cls.FORMREGLER, cls.FORMREGLER,
             cls.linear(d, 1024) + cls.linear(1024, cls.FORMREGLER), '%d Regler' % cls.FORMREGLER),
            ('ausgabe', 'Haut', 'Hautton (Stufe 1); die Hautkacheln des Hautkopfs von Mesh3D-AI in Stufe 3', d, 3, 3, cls.linear(d, 256) + cls.linear(256, 3), 'RGB'),
            ('ausgabe', 'Kleider', 'je Stück der Garderobe: getragen ja/nein und seine Farbe (Katalogwahl, Edgar 24.10.2026: „Kleider nicht 100 % wichtig“)', d,
             (cls.KLEIDUNG + cls.HAAR) * 4, (cls.KLEIDUNG + cls.HAAR) * 4, cls.linear(d, 1024) + cls.linear(1024, (cls.KLEIDUNG + cls.HAAR) * 4),
             '%d Stücke × (ja + RGB)' % (cls.KLEIDUNG + cls.HAAR)),
            ('ausgabe', 'Kamera', 'nur echte Fotos: je Ansicht Abstand, Öffnungswinkel und Versatz x/y (Exporte: die Regel der Charakter-Seite)', '%d × %d' % (cls.BUENDEL, d), '4 je Ansicht',
             4, cls.linear(d, 4), '4 je Ansicht'),
        )

    @classmethod
    def summe(cls):
        return sum(z[6] for z in cls.schichten())

    @classmethod
    def danach(cls):
        """Was nach dem Netz geschieht — ohne Gewichte, alles auf der Grafikkarte (`Architekturai2d3dgpu`)."""
        return (
            ('Genesis 9 bauen', 'Formregler → Punkte über die bekannte Wirkung je Regler (linear), Winkel → Vorwärtskinematik der %d Knochen → Häutung; Kleider aus dem Katalog anziehen' % cls.KNOCHEN),
            ('Rendern', 'nvdiffrast rastert die Figur aus den %d Kameras der Fotos (Exporte: Regel der Charakter-Seite, 20°, Hülle × 1,08)' % cls.ANSICHTEN),
            ('Vergleichen', 'Umriss (Maske), Farbe in der Figur, im Training zusätzlich Regler, Winkel und Punkte gegen die Wahrheit — daraus der Verlust'),
            ('Anpassen', 'beim Rechnen eines neuen Jobs dieselbe Schleife noch einige Schritte nur an den Eingabefotos (Edgar 24.10.2026: erlaubt) — nie an einer Wahrheit'),
        )
