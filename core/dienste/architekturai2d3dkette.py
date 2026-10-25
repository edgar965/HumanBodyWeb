# -*- coding: utf-8 -*-
"""Architekturai2d3dkette — wie die KIs der Foto-Kette aufgerufen werden: Ablauf in Kästen, für Hilfe → Architektur → 2d-3d-AI (24.10.2026).

Edgar: „eine übergeordnete Grafik mit Kästchen und Ablauf, wie die KIs aufgerufen werden“ und „Mach die KopfKI … rein“. Zwei Grafiken mit demselben Zeichner: die ganze Kette (`uebersicht`)
und die KopfKI (`kopfki`). Je Kasten Titel, Skript bzw. Klasse, die aufgerufenen KIs als farbige Marke (Farbe je KI wie in `MARKEN`) und was er tut; gestrichelt grau = nicht gebaut.
Inhalt aus dem Code gelesen (Skripte unter `ProjektTemp/_wegwerf/ai2d3d/`, Klassen in `KopfKI`, `KoerperKI_Fotos`, `KoerperKI_alle`) — keine Zahlen, die nicht dort oder in einer
Messdatei stehen.
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

__all__ = ['Architekturai2d3dkette']


class Architekturai2d3dkette:
    MARKEN = {'Sapiens2': '#9673a6', 'SAM 3': '#d79b00', 'ViTPose': '#b85450', 'MediaPipe': '#6c8ebf', 'Haut-KI': '#82b366', 'Genesis': '#888888'}
    BREITE, ABSTAND, OBEN, ZEILE = 228, 36, 70, 15

    @staticmethod
    def _text(teile, x, y, text, groesse=11, gewicht=400, farbe='#222', anker='middle'):
        teile.append('<text x="%.0f" y="%.0f" text-anchor="%s" font-size="%d" font-weight="%d" fill="%s">%s</text>' % (x, y, anker, groesse, gewicht, farbe, escape(text)))

    @classmethod
    def svg(cls, kennung, titel, kaesten, schleife=None):
        hoehe_kasten = 130 + cls.ZEILE * max(len(k['zeilen']) for k in kaesten) + 22 * max(len(k['kis']) for k in kaesten)
        breite = 20 + len(kaesten) * (cls.BREITE + cls.ABSTAND)
        hoehe = cls.OBEN + hoehe_kasten + (90 if schleife else 30)
        teile = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="%s" class="m3a-bild">' % (breite, hoehe, escape(titel)),
                 '<defs><marker id="%s-sp" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#555"/></marker>'
                 '<marker id="%s-rot" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#b85450"/></marker></defs>' % (kennung, kennung),
                 '<rect width="%d" height="%d" fill="#ffffff"/>' % (breite, hoehe)]
        cls._text(teile, 20, 26, titel, 15, 600, anker='start')
        x = 20
        for name, farbe in cls.MARKEN.items():
            teile.append('<rect x="%d" y="38" width="12" height="12" rx="2" fill="%s"/>' % (x, farbe))
            cls._text(teile, x + 16, 48, name + (' (kein Netz)' if name == 'Genesis' else ''), 11, anker='start')
            x += 30 + 7 * len(name) + (70 if name == 'Genesis' else 0)
        for i, k in enumerate(kaesten):
            x = 20 + i * (cls.BREITE + cls.ABSTAND)
            offen = k.get('stand') == 'offen'
            teile.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" stroke-width="1.5"%s/>' % (
                x, cls.OBEN, cls.BREITE, hoehe_kasten, '#f6f6f6' if offen else '#f4f8fd', '#999999' if offen else '#6c8ebf', ' stroke-dasharray="6 4"' if offen else ''))
            cls._text(teile, x + cls.BREITE / 2, cls.OBEN + 22, '%d  %s' % (i + 1, k['titel']), 14, 700)
            cls._text(teile, x + cls.BREITE / 2, cls.OBEN + 40, k.get('skript', ''), 10, 400, '#555')
            y = cls.OBEN + 62
            for ki in k['kis']:
                farbe = cls.MARKEN[ki[0]]
                teile.append('<rect x="%d" y="%d" width="%d" height="18" rx="9" fill="%s"/>' % (x + 10, y - 13, cls.BREITE - 20, farbe))
                cls._text(teile, x + cls.BREITE / 2, y, '%s: %s' % ki, 10, 600, '#ffffff')
                y += 22
            y += 6
            for z in k['zeilen']:
                cls._text(teile, x + 10, y, z, 11, anker='start')
                y += cls.ZEILE
            if i:
                teile.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#555" stroke-width="2" marker-end="url(#%s-sp)"/>' % (
                    x - cls.ABSTAND + 3, cls.OBEN + 30, x - 4, cls.OBEN + 30, kennung))
        if schleife:
            von, nach, text = schleife
            x1 = 20 + von * (cls.BREITE + cls.ABSTAND) + cls.BREITE / 2
            x2 = 20 + nach * (cls.BREITE + cls.ABSTAND) + cls.BREITE / 2
            if von == nach:                 # Schleife auf demselben Kasten: links hinaus, rechts zurück
                x1, x2 = x1 - 60, x2 + 60
            y = cls.OBEN + hoehe_kasten + 40
            teile.append('<path d="M %.0f %d L %.0f %d L %.0f %d L %.0f %d" fill="none" stroke="#b85450" stroke-width="2" stroke-dasharray="7 4" marker-end="url(#%s-rot)"/>' % (
                x1, cls.OBEN + hoehe_kasten + 2, x1, y, x2, y, x2, cls.OBEN + hoehe_kasten + 4, kennung))
            cls._text(teile, (x1 + x2) / 2, y + 20, text, 12, 600, '#b85450')
        teile.append('</svg>')
        return mark_safe(''.join(teile))

    @classmethod
    def uebersicht(cls):
        kaesten = [
            {'titel': 'Fotos und Angaben', 'skript': '3DObjects/ai2d3d/<Job>/job.json', 'kis': [],
             'zeilen': ['4 Fotos (vorn, links,', 'hinten, rechts)', 'Körpergröße und Gewicht', 'aus der job.json', 'Brennweite aus EXIF/XMP', '(Fotobrennweite)']},
            {'titel': 'Erkennen', 'skript': 'Fotosegmente · Fotogelenke', 'kis': [('Sapiens2', '29 Klassen je Pixel'), ('SAM 3', 'Bart, Haar, Ohr'), ('ViTPose', '12 Gelenke'),
                                                                         ('MediaPipe', '478 Gesichtspunkte')],
             'zeilen': ['je Foto einmal,', 'im selben Prozess', 'auf der Grafikkarte']},
            {'titel': 'Kopf (KopfKI)', 'skript': 'nurfotos_kopf.py', 'kis': [('MediaPipe', 'Foto UND Rendering'), ('Haut-KI', 'Kopfhaut'), ('SAM 3', 'Ohr: Foto + Rendering'),
                                                                               ('Genesis', '523 Kopfregler')],
             'zeilen': ['Regler in Runden,', 'jede Runde gerendert', 'und gemessen', 'Haut, Bart, Haar, Ohren', 'aus den Fotos']},
            {'titel': 'Körper einpassen', 'skript': 'nurfotos_einpassen.py', 'kis': [('Genesis', 'Körperregler, je Runde gebaut')],
             'zeilen': ['Fotoeinpassung, 3 Runden:', 'Form + Haltung + Kamera', 'je Foto (perspektivisch)', 'Ziele: Umriss, Haut,', 'Gelenke, Kopf', 'fest: Größe, Volumen,',
                        'Kopfform']},
            {'titel': 'Haut, Kleider, Haar', 'skript': 'nurfotos_koerper.py', 'kis': [('Haut-KI', 'Kopf + Körper'), ('Genesis', 'Figur bauen, Rig')],
             'zeilen': ['Körpertexel aus den Fotos,', 'KI nur ungesehen', 'Kleider ausgeschnitten', '(Fotoschale)', 'Haar mit dem Kopf versetzt', 'Haut unter Stoff weg']},
            {'titel': 'Prüfen', 'skript': 'koerperpruefung_lauf.py', 'kis': [('Sapiens2', 'Foto UND Rendering'), ('ViTPose', 'Foto UND Rendering')],
             'zeilen': ['Koerperbild rendert die', 'Figur in jede Fotokamera', 'Deckung je Gruppe,', 'Farbe, Gelenke in mm']},
            {'titel': 'Jobseite', 'skript': '/2d-3d-AI/test/<Job>/', 'kis': [],
             'zeilen': ['Feld 2/3: Genesis-Modell', 'Karte „Foto Vorlage -', 'Ergebnis“: je Foto', 'Vorlage | Ergebnis']},
        ]
        return cls.svg('a2d-kette', 'Die Kette heute: wie die KIs aufgerufen werden (alles in python14, auf der Grafikkarte, unter der Gpusperre)', kaesten,
                       (5, 3, 'Rückkopplung Prüfen → Einpassen/Kleider: beim Kopf gebaut (Kopfbildangleich), beim Körper noch nicht — heute nur gemessen'))

    @classmethod
    def kopfki(cls):
        kaesten = [
            {'titel': 'Fotos', 'skript': '1.jpg vorn · 3.jpg / 4.jpg Profil', 'kis': [('Sapiens2', 'Haut, Haar'), ('SAM 3', 'Bart, Haar, Ohr')],
             'zeilen': ['Fotosegmente: Masken', 'je Foto', '2.jpg (hinten) ohne Lage']},
            {'titel': 'Lage je Foto', 'skript': 'Kopflagen', 'kis': [('MediaPipe', '478 Punkte vorn')],
             'zeilen': ['Drehung, Maßstab,', 'Verschiebung je Foto', 'Profil: Profillinie']},
            {'titel': 'Kopfregler angleichen', 'skript': 'Kopfbildangleich', 'kis': [('Genesis', 'G9formung, Kopfmodell'), ('MediaPipe', 'auf dem Rendering')],
             'zeilen': ['523 Kopfregler in Runden', 'Kopfbild rendert den Kopf', 'in die Lage des Fotos;', 'derselbe Detektor auf', 'Foto und Rendering;',
                        'nur Besseres übernommen']},
            {'titel': 'Kopfhaut', 'skript': 'Fotohaut · Fotobart', 'kis': [('Haut-KI', 'Farbe je Texel')],
             'zeilen': ['Eingang: Punkte aus', 'den Fotos statt Netz', 'danach Falten aus dem', 'steilsten Foto, Bart', 'als eigene Schicht']},
            {'titel': 'Haar', 'skript': 'Fotohaarschale', 'kis': [],
             'zeilen': ['Schale über der Kopfhaut', 'Höhe aus den Umrissen', 'Farbe aus Haarpixeln', 'starr am Kopfknochen']},
            {'titel': 'Ohren', 'skript': 'Kopfohren', 'kis': [('SAM 3', 'Foto UND Rendering')],
             'zeilen': ['Abstehen, Größe, Lage', 'je Seite angeglichen']},
        ]
        return cls.svg('a2d-kopfki', 'KopfKI: der Kopf aus den Fotos (A:\\3dTools\\KopfKI) — kein eigenes Netz, sondern drei vortrainierte KIs (Sapiens2, SAM 3, MediaPipe) und die Haut-KI in einer Schleife', kaesten,
                       (2, 2, 'je Runde: Regler → Kopf formen → rendern → MediaPipe auf dem Rendering → Fehler gegen das Foto'))
