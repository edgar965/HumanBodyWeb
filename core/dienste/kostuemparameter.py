# -*- coding: utf-8 -*-
"""Kostuemparameter — das Kostüm als DATEN: jedes Maß, jede Farbe, jeder Teile-Schalter mit Startwert und
Grenzen.

Edgar (29.09.2026): „für das Verfahren brauche ich einen Code der dann später per Knopfdruck durch alle
Iterationen bis zum fertigen Ergebnis läuft". Eine Runde ändert deshalb nur noch Zahlen, keinen Code: der
Optimierer (`Kostuemoptimierer`) und die Prüf-KI (`Kostuemkritik`) schlagen Wertesätze vor, gebaut wird immer
derselbe Code (`effekte/blender/kostuem/`). Neue TEILARTEN (ein Stab, ein Haar) werden einmal von Hand gebaut
und bekommen hier ihren Schalter — danach verwaltet die Schleife sie selbst.

Schlüssel `teil.name`, Farben `farbe.<stoff>.r|g|b` (0…1, sRGB — so misst der Kreislauf die Vorlage). `art`:
`mass` (stetig), `schalter` (0/1).

VERSION 2 (30.09.2026, Claude als Kritiker nach Sicht der Vergleichsbilder): Die Werte der Version 1 waren an
ihre Grenzen gelaufen (Mantel-Weite 2,5 von 2,6, Kapuzenhals 2,8 von 2,8 …) und die Farben verwildert (Gürtel
reines Grün, Unterkleid grelles Gelb, Bart reines Weiß) — schwach sichtbare Farben bekamen keinen Gegendruck.
Version 2 hat gemessene Farben (Medianwerte der Vorlage,
`ProjektTemp/_wegwerf/blendermodell/farben_messen.py`), engere Grenzen, den Stab mit Kristallkugel in der
gebeugten rechten Hand, Schuhe, Borten und Hutband. Ändert sich das Kostümmodell, steigt `VERSION`: Der
Kreislauf beginnt dann mit den Startwerten statt mit den Werten des alten Modells (`Kostuemkreislauf`).
"""

__all__ = ['Kostuemparameter']


class Kostuemparameter:
    VERSION = 2
    #: (schluessel, titel, start, min, max) — Titel gehen wörtlich an die Prüf-KI.
    MASSE = [
        # Die Haltung der Grundfigur für den Vergleich (`Koerperpose`): Genesis 9 steht in A-Haltung, die
        # Vorlage lässt die Arme hängen. Kein Kostüm, aber ohne sie verbiegt der Kreislauf Ärmel, um Arme zu
        # treffen. Der rechte Arm hält den Stab vor dem Körper: Ellbogen gebeugt.
        ('pose.arme', 'Haltung: Oberarme gesenkt aus der A-Haltung (Grad)', 35.0, 0.0, 60.0),
        (
            'pose.ellbogen',
            'Haltung: Unterarm des freien (linken) Arms nach vorn gebeugt (Grad)',
            10.0,
            0.0,
            60.0,
        ),
        ('pose.ellbogen_stab', 'Haltung: Ellbogen des Arms, der den Stab hält (Grad)', 85.0, 20.0, 130.0),
        ('pose.arm_vor', 'Haltung: Oberarm des Stab-Arms nach vorn geschwungen (Grad)', 0.0, 0.0, 40.0),
        ('unterkleid.luft', 'Unterkleid: Weite am Rumpf (× Körper)', 1.10, 1.0, 1.4),
        ('unterkleid.mitte_weite', 'Unterkleid: Weite auf Kniehöhe (× Hüfte)', 1.35, 1.0, 2.0),
        ('unterkleid.saum_hoehe', 'Unterkleid: Saum über dem Boden (× Körperhöhe)', 0.05, 0.0, 0.2),
        ('unterkleid.saum_weite', 'Unterkleid: Weite am Saum (× Hüfte)', 1.8, 1.2, 2.6),
        ('unterkleid.welle', 'Unterkleid: Faltenwurf am Saum', 0.02, 0.0, 0.06),
        ('mantel.hals_weite', 'Mantel: Weite am Hals (× Hals)', 1.45, 1.1, 1.9),
        ('mantel.schulter_weite', 'Mantel: Breite über den Schultern (× Schulter)', 1.45, 1.1, 2.0),
        ('mantel.schulter_tiefe', 'Mantel: Tiefe über den Schultern (× Schulter)', 1.6, 1.1, 2.2),
        ('mantel.luft', 'Mantel: Weite an Brust, Taille, Hüfte (× Körper)', 1.22, 1.05, 1.6),
        ('mantel.mitte_weite', 'Mantel: Weite auf Kniehöhe (× Hüfte)', 1.5, 1.1, 2.6),
        ('mantel.saum_hoehe', 'Mantel: Saum über dem Boden (× Körperhöhe)', 0.09, 0.02, 0.2),
        ('mantel.saum_weite', 'Mantel: Weite am Saum (× Hüfte)', 2.1, 1.3, 2.9),
        ('mantel.offen_grad', 'Mantel: Öffnung vorn (Grad)', 25.0, 0.0, 90.0),
        ('mantel.welle', 'Mantel: Faltenwurf am Saum', 0.04, 0.0, 0.1),
        ('aermel.weite_oben', 'Ärmel: Weite an der Schulter (× Arm)', 1.4, 1.0, 3.0),
        ('aermel.weite_mitte', 'Ärmel: Weite am Unterarm und Handgelenk (× Arm)', 1.7, 1.0, 2.4),
        ('aermel.weite_saum', 'Ärmel: Weite am Saum der hängenden Glocke (× Arm)', 3.0, 1.0, 3.8),
        ('aermel.laenge', 'Ärmel: Länge der Glocke unter dem Handgelenk (× Arm)', 0.35, 0.05, 1.0),
        ('aermel.haengen', 'Ärmel: Glocke zusätzlich länger (m)', 0.0, 0.0, 0.2),
        ('aermel.tiefe', 'Ärmel: Tiefe der Glocke gegenüber ihrer Breite (1 = rund)', 1.0, 0.35, 2.0),
        ('guertel.weite', 'Gürtel: Weite (× Mantel)', 1.04, 0.95, 1.2),
        ('guertel.breite', 'Gürtel: Breite (m)', 0.08, 0.06, 0.12),
        ('taschen.groesse', 'Gürteltaschen: Größe', 1.0, 0.3, 1.6),
        ('kapuze.kopf_weite', 'Kapuze: Weite am Kopf (× Kopf)', 1.25, 1.0, 2.2),
        ('kapuze.hals_weite', 'Kapuze: Weite am Hals (× Hals)', 1.9, 1.3, 4.0),
        ('kapuze.schulter_weite', 'Kapuze: Weite auf den Schultern (× Schulter)', 1.6, 0.9, 2.6),
        ('kapuze.offen_grad', 'Kapuze: Öffnung vorn (Grad)', 120.0, 40.0, 200.0),
        ('bart.laenge', 'Bart: Länge (× Körperhöhe)', 0.24, 0.08, 0.30),
        ('bart.breite', 'Bart: Breite (× Kopf)', 0.7, 0.3, 1.3),
        ('bart.abstand', 'Bart: Abstand vor der Kopfmitte (× Kopftiefe)', 1.15, 1.0, 1.8),
        ('haar.laenge', 'Haar: Länge unter dem Kinn (× Körperhöhe)', 0.18, 0.05, 0.3),
        ('haar.weite', 'Haar: Weite (× Kopf)', 1.15, 0.9, 1.5),
        ('hut.krone_weite', 'Hut: Weite der Krone (× Kopf)', 1.3, 1.0, 1.6),
        ('hut.krempe_weite', 'Hut: Weite der Krempe (× Kopf)', 3.5, 2.0, 4.4),
        ('hut.krempe_haengen', 'Hut: Krempe hängt außen (m)', 0.05, 0.0, 0.10),
        ('hut.hoehe', 'Hut: Höhe der Spitze (× Körperhöhe)', 0.24, 0.1, 0.36),
        ('hut.kipp', 'Hut: Krempe vorn angehoben und hinten gesenkt (m)', 0.03, 0.0, 0.09),
        ('hut.biegung', 'Hut: Spitze nach hinten gebogen (× Körperhöhe)', 0.16, 0.0, 0.4),
        (
            'hut.seite',
            'Hut: Spitze zur Seite geneigt (× Körperhöhe, + = zur rechten Bildseite von vorn)',
            0.0,
            -0.12,
            0.12,
        ),
        ('stab.hoehe', 'Stab: Höhe der Kugel über dem Boden (× Körperhöhe)', 1.05, 0.9, 1.3),
        ('stab.dicke', 'Stab: Radius des Schafts (m)', 0.017, 0.01, 0.03),
        ('stab.knorrig', 'Stab: Krümmung und Knoten des Schafts', 0.3, 0.0, 1.0),
        ('stab.kristall', 'Stab: Radius der Kristallkugel (m)', 0.05, 0.04, 0.07),
        ('stab.kopf', 'Stab: Weite der Fassung um die Kugel (× Kugelradius)', 1.5, 1.0, 2.5),
        ('stab.krone', 'Stab: Holzkrone um die Kugel, Größe (m; 0 = keine)', 0.04, 0.0, 0.09),
        ('stab.abstand', 'Stab: seitlich zur Faust (m)', 0.0, -0.12, 0.12),
        ('stab.vorn', 'Stab: nach vorn von der Faust weg (m)', 0.0, -0.05, 0.2),
        ('borte.breite', 'Borte: Breite des Saumbands (m)', 0.045, 0.01, 0.1),
        ('schuhe.groesse', 'Schuhe: Größe (× Fuß)', 1.2, 0.9, 1.5),
    ]
    #: Teile, die an- und ausgehen können — (schluessel, titel, start).
    SCHALTER = [
        ('taschen.an', 'Gürteltaschen', 1),
        ('kapuze.an', 'Kapuze', 1),
        ('bart.an', 'Bart', 1),
        ('haar.an', 'Langes Haar', 1),
        ('hut.an', 'Spitzhut', 1),
        ('stab.an', 'Wanderstab mit Kristallkugel', 1),
        ('borte.an', 'Borten (Saum, Ärmel, Hutband)', 1),
        ('schuhe.an', 'Schuhe', 1),
        ('utensilien.an', 'Amulett, Fläschchen und Gürtelschnalle', 1),
    ]
    #: Stoffe und ihre Startfarbe (sRGB 0…1) — gemessen an der Vorlage (Median je Bereich, dazu ein Zuschlag für
    # die Abdunklung der Studiobeleuchtung des Renders); Borte, Kristall und Schuhe geschätzt.
    FARBEN = {
        'mantel': ('Mantel und Ärmel', (0.27, 0.29, 0.37)),
        'hut': ('Hut (Spitze und Krempe)', (0.33, 0.33, 0.40)),
        'unterkleid': ('Unterkleid', (0.60, 0.53, 0.44)),
        'leder': ('Gürtel und Taschen', (0.30, 0.20, 0.14)),
        'bart': ('Bart und Haar', (0.78, 0.75, 0.72)),
        'stab': ('Stab', (0.36, 0.26, 0.18)),
        'schuhe': ('Schuhe', (0.22, 0.16, 0.12)),
        'borte': ('Borten und Hutband', (0.70, 0.57, 0.33)),
        'kristall': ('Kristallkugel', (0.35, 0.60, 0.85)),
    }

    @classmethod
    def schema(cls):
        """`{schluessel: {titel, art, start, min, max}}` — alle Werte, die eine Runde ändern darf."""
        aus = {}
        for k, titel, start, lo, hi in cls.MASSE:
            aus[k] = {'titel': titel, 'art': 'mass', 'start': start, 'min': lo, 'max': hi}
        for k, titel, start in cls.SCHALTER:
            aus[k] = {
                'titel': '%s an (1) oder aus (0)' % titel,
                'art': 'schalter',
                'start': start,
                'min': 0,
                'max': 1,
            }
        for stoff, (titel, rgb) in cls.FARBEN.items():
            for kanal, wert in zip('rgb', rgb, strict=True):
                aus['farbe.%s.%s' % (stoff, kanal)] = {
                    'titel': 'Farbe %s: %s-Anteil (0…1)' % (titel, kanal.upper()),
                    'art': 'mass',
                    'start': wert,
                    'min': 0.0,
                    'max': 1.0,
                }
        return aus

    @classmethod
    def start(cls):
        return {k: e['start'] for k, e in cls.schema().items()}

    @classmethod
    def pruefen(cls, roh):
        """Vollständiger Wertesatz: bekannte Schlüssel auf ihre Grenzen gezogen, Schalter 0/1, der Rest
        Startwert."""
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for k, e in cls.schema().items():
            try:
                wert = float(roh.get(k, e['start']))
            except TypeError, ValueError:
                wert = float(e['start'])
            if wert != wert:  # NaN
                wert = float(e['start'])
            wert = min(e['max'], max(e['min'], wert))
            aus[k] = int(wert >= 0.5) if e['art'] == 'schalter' else round(wert, 5)
        return aus

    @classmethod
    def unterschiede(cls, alt, neu, genauigkeit=1e-4):
        """`{schluessel: [alt, neu]}` — nur, was sich merklich geändert hat (für die Anzeige einer Runde)."""
        schema = cls.schema()
        aus = {}
        for k in schema:
            a, b = alt.get(k), neu.get(k)
            if a is None or b is None:
                continue
            spanne = schema[k]['max'] - schema[k]['min'] or 1.0
            if abs(float(a) - float(b)) > genauigkeit * spanne:
                aus[k] = [a, b]
        return aus
