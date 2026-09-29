# -*- coding: utf-8 -*-
"""Kostuemparameter — das Kostüm als DATEN: jedes Maß, jede Farbe, jeder Teile-Schalter mit Startwert und
Grenzen.

Edgar (29.09.2026): „für das Verfahren brauche ich einen Code der dann später per Knopfdruck durch alle
Iterationen bis zum fertigen Ergebnis läuft". Eine Runde ändert deshalb nur noch Zahlen, keinen Code: der
Optimierer (`Kostuemoptimierer`) und die Prüf-KI (`Kostuemkritik`) schlagen Wertesätze vor, gebaut wird immer
derselbe Code (`effekte/blender/kostuem/`). Neue TEILARTEN (ein Stab, ein Haar) werden einmal von Hand gebaut
und bekommen hier ihren Schalter — danach verwaltet die Schleife sie selbst.

Startwerte = die Faktoren der Handrunde 9 (bis dahin fest im Code), dazu Stab und Haar ausgeschaltet.
Schlüssel `teil.name`, Farben `farbe.<stoff>.r|g|b` (0…1, Workbench-Grundfarbe). `art`: `mass` (stetig),
`schalter` (0/1).
"""

__all__ = ['Kostuemparameter']


class Kostuemparameter:
    #: (schluessel, titel, start, min, max) — Titel gehen wörtlich an die Prüf-KI.
    MASSE = [
        # Die Haltung der Grundfigur für den Vergleich (`Koerperpose`): Genesis 9 steht in A-Haltung, die
        # Vorlage lässt die Arme hängen. Kein Kostüm, aber ohne sie verbiegt der Kreislauf Ärmel, um Arme zu
        # treffen.
        ('pose.arme', 'Haltung: Oberarme gesenkt aus der A-Haltung (Grad)', 35.0, 0.0, 60.0),
        ('pose.ellbogen', 'Haltung: Unterarme nach vorn gebeugt (Grad)', 0.0, 0.0, 90.0),
        ('unterkleid.luft', 'Unterkleid: Weite am Rumpf (× Körper)', 1.10, 1.0, 1.5),
        ('unterkleid.mitte_weite', 'Unterkleid: Weite auf Kniehöhe (× Hüfte)', 1.35, 1.0, 2.5),
        ('unterkleid.saum_hoehe', 'Unterkleid: Saum über dem Boden (× Körperhöhe)', 0.06, 0.0, 0.2),
        ('unterkleid.saum_weite', 'Unterkleid: Weite am Saum (× Hüfte)', 1.9, 1.2, 3.0),
        ('unterkleid.welle', 'Unterkleid: Faltenwurf am Saum', 0.03, 0.0, 0.12),
        ('mantel.hals_weite', 'Mantel: Weite am Hals (× Hals)', 1.5, 1.1, 2.2),
        ('mantel.schulter_weite', 'Mantel: Breite über den Schultern (× Schulter)', 1.45, 1.1, 2.2),
        ('mantel.schulter_tiefe', 'Mantel: Tiefe über den Schultern (× Schulter)', 1.6, 1.1, 2.4),
        ('mantel.luft', 'Mantel: Weite an Brust, Taille, Hüfte (× Körper)', 1.22, 1.05, 1.6),
        ('mantel.mitte_weite', 'Mantel: Weite auf Kniehöhe (× Hüfte)', 1.5, 1.1, 2.6),
        ('mantel.saum_hoehe', 'Mantel: Saum über dem Boden (× Körperhöhe)', 0.16, 0.02, 0.25),
        ('mantel.saum_weite', 'Mantel: Weite am Saum (× Hüfte)', 2.1, 1.3, 3.2),
        ('mantel.offen_grad', 'Mantel: Öffnung vorn (Grad)', 22.0, 0.0, 100.0),
        ('mantel.welle', 'Mantel: Faltenwurf am Saum', 0.04, 0.0, 0.12),
        ('aermel.weite_oben', 'Ärmel: Weite an der Schulter (× Arm)', 1.9, 1.0, 3.5),
        ('aermel.weite_mitte', 'Ärmel: Weite am Unterarm (× Arm)', 1.65, 1.0, 3.5),
        ('aermel.weite_saum', 'Ärmel: Weite am Saum (× Arm)', 1.85, 1.0, 4.0),
        ('aermel.laenge', 'Ärmel: Länge (× Arm)', 1.05, 0.7, 1.3),
        ('guertel.weite', 'Gürtel: Weite (× Mantel)', 1.04, 0.95, 1.3),
        ('guertel.breite', 'Gürtel: Breite (m)', 0.04, 0.01, 0.1),
        ('taschen.groesse', 'Gürteltaschen: Größe', 1.0, 0.5, 2.0),
        ('kapuze.kopf_weite', 'Kapuze: Weite am Kopf (× Kopf)', 1.25, 1.0, 1.8),
        ('kapuze.hals_weite', 'Kapuze: Weite am Hals (× Hals)', 1.9, 1.3, 2.8),
        ('kapuze.schulter_weite', 'Kapuze: Weite auf den Schultern (× Schulter)', 1.75, 1.3, 2.6),
        ('kapuze.offen_grad', 'Kapuze: Öffnung vorn (Grad)', 120.0, 40.0, 200.0),
        ('bart.laenge', 'Bart: Länge (× Körperhöhe)', 0.30, 0.08, 0.45),
        ('bart.breite', 'Bart: Breite (× Kopf)', 0.7, 0.3, 1.2),
        ('bart.abstand', 'Bart: Abstand vor der Kopfmitte (× Kopftiefe)', 1.3, 1.0, 1.8),
        ('haar.laenge', 'Haar: Länge unter dem Kinn (× Körperhöhe)', 0.18, 0.05, 0.35),
        ('haar.weite', 'Haar: Weite (× Kopf)', 1.15, 0.9, 1.6),
        ('hut.krone_weite', 'Hut: Weite der Krone (× Kopf)', 1.3, 1.0, 1.8),
        ('hut.krempe_weite', 'Hut: Weite der Krempe (× Kopf)', 3.1, 2.0, 4.5),
        ('hut.krempe_haengen', 'Hut: Krempe hängt außen (m)', 0.035, 0.0, 0.08),
        ('hut.hoehe', 'Hut: Höhe der Spitze (× Körperhöhe)', 0.26, 0.1, 0.4),
        ('hut.biegung', 'Hut: Spitze nach hinten gebogen (× Körperhöhe)', 0.16, 0.0, 0.3),
        ('stab.hoehe', 'Stab: Höhe (× Körperhöhe)', 1.12, 0.8, 1.4),
        ('stab.dicke', 'Stab: Radius (m)', 0.018, 0.008, 0.04),
        ('stab.knauf', 'Stab: Radius des Knaufs (m)', 0.05, 0.0, 0.12),
        ('stab.abstand', 'Stab: seitlich neben der Hand (m)', 0.15, 0.0, 0.4),
    ]
    #: Teile, die an- und ausgehen können — (schluessel, titel, start).
    SCHALTER = [
        ('taschen.an', 'Gürteltaschen', 1),
        ('kapuze.an', 'Kapuze', 1),
        ('bart.an', 'Bart', 1),
        ('haar.an', 'Langes Haar', 0),
        ('hut.an', 'Spitzhut', 1),
        ('stab.an', 'Wanderstab', 0),
    ]
    #: Stoffe und ihre Startfarbe (RGB 0…1).
    FARBEN = {
        'mantel': ('Mantel, Ärmel, Kapuze, Hut', (0.12, 0.14, 0.22)),
        'unterkleid': ('Unterkleid', (0.62, 0.55, 0.42)),
        'leder': ('Gürtel und Taschen', (0.30, 0.18, 0.09)),
        'bart': ('Bart und Haar', (0.72, 0.70, 0.66)),
        'stab': ('Stab', (0.30, 0.20, 0.10)),
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
