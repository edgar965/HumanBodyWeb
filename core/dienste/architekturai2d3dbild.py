# -*- coding: utf-8 -*-
"""Architekturai2d3dbild — die Grafik des neuronalen Netzes von 2d-3d-AI für Hilfe → Architektur → 2d-3d-AI (24.10.2026).

Edgar: „mach genau wie diese Seite [/hilfe/architektur/mesh3dai/] die komplette Dokumentation, inkl. grafischer Darstellung des neuronalen Netzes“. Dieselbe Bildsprache wie `Architekturmesh3daibild`:
je Schicht ein gestrichelter Kasten, rot die Eingabe, blau verdeckte Schichten, grau-blau die ganze Figur, grün die Ausgabe, grau was NACH dem Netz geschieht (ohne Gewichte); die große Zahl =
so viele Zahlen (Neuronen) trägt ein Token nach der Schicht; Kreise sind Sinnbild, „⋮“ = weitere. Dazu violett das vortrainierte Rückgrat und ein Pfeil zurück: der Vergleich Rendering ↔ Foto
ist der Verlust, aus dem das Netz lernt. Alle Zahlen aus `Architekturai2d3dnetz` (dieselbe Tabelle, die die Seite zeigt). Ein Vorschlag — nichts davon ist gebaut.
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .architekturai2d3dnetz import Architekturai2d3dnetz

__all__ = ['Architekturai2d3dbild']


class Architekturai2d3dbild:
    FARBEN = {'eingabe': ('#f8cecc', '#b85450'), 'rueckgrat': ('#e1d5e7', '#9673a6'), 'versteckt': ('#dae8fc', '#6c8ebf'), 'figur': ('#eef1f6', '#8a99b3'),
              'ausgabe': ('#d5e8d4', '#82b366'), 'danach': ('#eeeeee', '#999999')}
    WORT = {'eingabe': 'Zahlen je Pixel', 'rueckgrat': 'Merkmale je Feld', 'figur': 'Zahlen je Figur', 'ausgabe': 'Zahlen je Figur'}
    ZAHLFARBE = '#1f3f7a'
    BREITE, HOEHE = 1800, 700
    SPALTE, ABSTAND = 150, 40
    OBEN, UNTEN = 70, 560
    KREISE_OBEN, KREISE_HOEHE = 100, 200
    TEXT_OBEN = 330

    @staticmethod
    def _de(n):
        return f'{int(n):,}'.replace(',', '.')

    @classmethod
    def _x(cls, i):
        return 20 + i * (cls.SPALTE + cls.ABSTAND)

    @classmethod
    def _text(cls, teile, x, y, text, groesse=13, gewicht=400, farbe='#222', anker='middle'):
        teile.append('<text x="%.0f" y="%.0f" text-anchor="%s" font-size="%d" font-weight="%d" fill="%s">%s</text>' % (x, y, anker, groesse, gewicht, farbe, escape(text)))

    @classmethod
    def _kasten(cls, teile, x, oben, breite, hoehe, art):
        fuell, rand = cls.FARBEN[art]
        teile.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="4" fill="%s" stroke="%s" stroke-dasharray="5 3"/>' % (x, oben, breite, hoehe, fuell, rand))

    @classmethod
    def _kreise(cls, teile, cx, art):
        rand = cls.FARBEN[art][1]
        ys = [cls.KREISE_OBEN + cls.KREISE_HOEHE * (k + 0.5) / 5 for k in range(5)]
        beschriftung = ('R', 'G', 'B', '', 'M') if art == 'eingabe' else ('', '', '', '', '')
        for k in (0, 1, 2, 4):
            teile.append('<circle cx="%.0f" cy="%.0f" r="16" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (cx, ys[k], rand))
            if beschriftung[k]:
                cls._text(teile, cx, ys[k] + 5, beschriftung[k], 13, 600)
        cls._text(teile, cx, ys[3] + 6, '⋮', 22, 700, rand)

    @classmethod
    def _pfeil(cls, teile, x1, y1, x2, y2, farbe='#555', strich=''):
        teile.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2" marker-end="url(#a2d-spitze)"%s/>' % (x1, y1, x2, y2, farbe, strich))

    @classmethod
    def _spalte(cls, teile, i, zeile):
        art, titel, _was, _ein, _aus, neuronen, gewichte, stichwort = zeile
        x = cls._x(i)
        cx = x + cls.SPALTE / 2
        cls._kasten(teile, x, cls.OBEN, cls.SPALTE, cls.UNTEN - cls.OBEN, art)
        cls._text(teile, cx, cls.OBEN + 22, titel, 16, 600)
        cls._kreise(teile, cx, art)
        cls._text(teile, cx, cls.TEXT_OBEN + 22, cls._de(neuronen), 28, 700, cls.ZAHLFARBE)
        cls._text(teile, cx, cls.TEXT_OBEN + 42, cls.WORT.get(art, 'Neuronen je Token'), 12, 600, cls.ZAHLFARBE)
        cls._text(teile, cx, cls.TEXT_OBEN + 70, stichwort, 12)
        if art == 'rueckgrat':
            cls._text(teile, cx, cls.TEXT_OBEN + 90, '≈ 0,4 Mrd. Gewichte', 12, 600)
            cls._text(teile, cx, cls.TEXT_OBEN + 108, 'vortrainiert, eingefroren', 12)
        elif gewichte:
            cls._text(teile, cx, cls.TEXT_OBEN + 90, 'Gewichte %s' % cls._de(gewichte), 12, 600)
        else:
            cls._text(teile, cx, cls.TEXT_OBEN + 90, 'keine Gewichte', 12)

    @classmethod
    def _ausgabe(cls, teile, i, koepfe):
        """Die Köpfe als Stapel kleiner grüner Kästen in einer Spalte; ein Pfeil von der Figur zu jedem."""
        x, n = cls._x(i), len(koepfe)
        hoehe = (cls.UNTEN - cls.OBEN - (n - 1) * 8) / n
        mitten = []
        for k, (_art, titel, _was, _ein, _aus, neuronen, gewichte, stichwort) in enumerate(koepfe):
            oben = cls.OBEN + k * (hoehe + 8)
            cls._kasten(teile, x, oben, cls.SPALTE, hoehe, 'ausgabe')
            cls._text(teile, x + cls.SPALTE / 2, oben + 18, titel, 14, 600)
            cls._text(teile, x + cls.SPALTE / 2, oben + 42, cls._de(neuronen), 22, 700, cls.ZAHLFARBE)
            cls._text(teile, x + cls.SPALTE / 2, oben + 60, stichwort, 11)
            cls._text(teile, x + cls.SPALTE / 2, oben + 76, 'Gewichte %s' % cls._de(gewichte), 11, 600)
            mitten.append(oben + hoehe / 2)
        return mitten

    @classmethod
    def _danach(cls, teile, i0, schritte):
        """Graue Kästen nach dem Netz (ohne Gewichte) und der Pfeil zurück zu den Fotos: der Verlust."""
        for k, (titel, _text) in enumerate(schritte[:3]):
            x = cls._x(i0 + k)
            cls._kasten(teile, x, cls.OBEN + 120, cls.SPALTE, 250, 'danach')
            cls._text(teile, x + cls.SPALTE / 2, cls.OBEN + 150, titel, 15, 600)
            for z, wort in enumerate({'Genesis 9 bauen': ('Formregler → Punkte', 'Winkel → Skelett', 'Häutung, Kleider'),
                                      'Rendern': ('nvdiffrast', 'Kameras der Fotos', 'alles auf der GPU'),
                                      'Vergleichen': ('Umriss, Farbe', 'Training: + Wahrheit', '→ Verlust')}.get(titel, ())):
                cls._text(teile, x + cls.SPALTE / 2, cls.OBEN + 185 + 22 * z, wort, 12)
            if k:
                cls._pfeil(teile, x - cls.ABSTAND + 2, cls.OBEN + 245, x - 4, cls.OBEN + 245)
        rechts = cls._x(i0 + 2) + cls.SPALTE / 2
        links = cls._x(0) + cls.SPALTE / 2
        teile.append('<path d="M %.0f %.0f L %.0f %.0f L %.0f %.0f L %.0f %.0f" fill="none" stroke="#b85450" stroke-width="2" stroke-dasharray="7 4" marker-end="url(#a2d-spitze-rot)"/>' % (
            rechts, cls.OBEN + 370, rechts, cls.HOEHE - 70, links, cls.HOEHE - 70, links, cls.UNTEN + 4))
        cls._text(teile, (rechts + links) / 2, cls.HOEHE - 78, 'Verlust: die Renderings müssen aussehen wie die Fotos — im Training zusätzlich Regler und Winkel gegen die Wahrheit',
                  13, 600, '#b85450')

    @classmethod
    def svg(cls):
        zeilen = Architekturai2d3dnetz.schichten()
        netz = [z for z in zeilen if z[0] != 'ausgabe']
        koepfe = [z for z in zeilen if z[0] == 'ausgabe']
        teile = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="Neuronales Netz von 2d-3d-AI: Fotos → Genesis-Modell" class="m3a-bild">' % (cls.BREITE, cls.HOEHE),
                 '<defs><marker id="a2d-spitze" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#555"/></marker>'
                 '<marker id="a2d-spitze-rot" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#b85450"/></marker></defs>',
                 '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (cls.BREITE, cls.HOEHE)]
        cls._text(teile, 20, 30, 'Die Fotos auf dem Weg durch das Netz — die große Zahl: so viele Zahlen (Neuronen) trägt ein Token nach der Schicht. Kreise = Sinnbild, ⋮ = weitere.', 15, 600,
                  anker='start')
        cls._text(teile, 20, 50, 'Vorschlag (Weg B), nicht gebaut. Gewichte aus den Maßen gerechnet; das Rückgrat ist vortrainiert und zählt nicht mit.', 13, anker='start')
        for i, zeile in enumerate(netz):
            cls._spalte(teile, i, zeile)
            if i:
                cls._pfeil(teile, cls._x(i) - cls.ABSTAND + 2, cls.OBEN + 200, cls._x(i) - 4, cls.OBEN + 200)
        i_aus = len(netz)
        for y in cls._ausgabe(teile, i_aus, koepfe):
            cls._pfeil(teile, cls._x(i_aus) - cls.ABSTAND + 2, cls.OBEN + 200, cls._x(i_aus) - 4, y)
        cls._pfeil(teile, cls._x(i_aus) + cls.SPALTE + 2, cls.OBEN + 245, cls._x(i_aus + 1) - 4, cls.OBEN + 245)
        cls._danach(teile, i_aus + 1, Architekturai2d3dnetz.danach())
        cls._text(teile, 20, cls.HOEHE - 20, 'Summe %s Gewichte (lernbare Zahlen, ohne Rückgrat) · Netz in python10 (torch 2.10 + CUDA 12.8, nvdiffrast 0.4.0) · alles im Speicher und auf der GPU' % (
            cls._de(Architekturai2d3dnetz.summe())), 13, 600, anker='start')
        teile.append('</svg>')
        return mark_safe(''.join(teile))
