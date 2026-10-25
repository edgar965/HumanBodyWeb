# -*- coding: utf-8 -*-
"""Architekturai2d3dnetzbild — eine KI der Foto-Kette als Grafik in der Bildsprache von „Neuronales Netz – Figur“ (Mesh3D-AI-Seite), für Hilfe → Architektur → 2d-3d-AI (24.10.2026).

Edgar: „Mach die KopfKI, Haut KI rein, für alle KIs eine einzelne Grafik wie diese: Neuronale Netz - Figur“. Je Spalte ein gestrichelter Kasten: rot die Eingabe, violett ein vortrainiertes Rückgrat,
blau verdeckte Schichten, grün die Ausgabe, grau was davor oder danach ohne Gewichte geschieht; die große Zahl ist die Breite (so viele Zahlen trägt ein Feld, Punkt oder Token nach der Schicht),
Kreise sind Sinnbild, „⋮“ = weitere. Gezeichnet wird nur, was der Aufrufer übergibt — die Zahlen kommen aus der Vermessung der Gewichtsdateien (`Architekturai2d3dkis`).

    svg = Architekturai2d3dnetzbild.svg(kennung, titel, untertitel, spalten, fuss)
    spalten: [{'art', 'titel', 'zahl', 'wort', 'zeilen': [...], 'gewichte': int oder None}]
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

__all__ = ['Architekturai2d3dnetzbild']


class Architekturai2d3dnetzbild:
    FARBEN = {'eingabe': ('#f8cecc', '#b85450'), 'rueckgrat': ('#e1d5e7', '#9673a6'), 'versteckt': ('#dae8fc', '#6c8ebf'), 'figur': ('#eef1f6', '#8a99b3'),
              'ausgabe': ('#d5e8d4', '#82b366'), 'danach': ('#eeeeee', '#999999')}
    ZAHLFARBE = '#1f3f7a'
    SPALTE, ABSTAND = 150, 34
    OBEN, KREISE_OBEN, KREISE_HOEHE = 64, 92, 170
    TEXT_OBEN = 278
    ZEILE = 17

    @staticmethod
    def _de(n):
        return f'{int(n):,}'.replace(',', '.')

    @classmethod
    def _x(cls, i):
        return 20 + i * (cls.SPALTE + cls.ABSTAND)

    @staticmethod
    def _text(teile, x, y, text, groesse=12, gewicht=400, farbe='#222', anker='middle'):
        teile.append('<text x="%.0f" y="%.0f" text-anchor="%s" font-size="%d" font-weight="%d" fill="%s">%s</text>' % (x, y, anker, groesse, gewicht, farbe, escape(text)))

    @classmethod
    def _spalte(cls, teile, i, s, unten):
        fuell, rand = cls.FARBEN[s['art']]
        x = cls._x(i)
        cx = x + cls.SPALTE / 2
        teile.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="4" fill="%s" stroke="%s" stroke-dasharray="5 3"/>' % (x, cls.OBEN, cls.SPALTE, unten - cls.OBEN, fuell, rand))
        cls._text(teile, cx, cls.OBEN + 20, s['titel'], 14, 600)
        if s['art'] == 'danach':
            for z, zeile in enumerate(s.get('zeilen', ())):
                cls._text(teile, cx, cls.KREISE_OBEN + 40 + z * cls.ZEILE, zeile, 12)
            return
        ys = [cls.KREISE_OBEN + cls.KREISE_HOEHE * (k + 0.5) / 5 for k in range(5)]
        for k, beschriftung in zip((0, 1, 2, 4), s.get('kreise') or ('', '', '', '')):
            teile.append('<circle cx="%.0f" cy="%.0f" r="14" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (cx, ys[k], rand))
            if beschriftung:
                cls._text(teile, cx, ys[k] + 4, beschriftung, 11, 600)
        cls._text(teile, cx, ys[3] + 6, '⋮', 20, 700, rand)
        cls._text(teile, cx, cls.TEXT_OBEN + 4, cls._de(s['zahl']) if isinstance(s.get('zahl'), (int, float)) else str(s.get('zahl', '')), 26, 700, cls.ZAHLFARBE)
        cls._text(teile, cx, cls.TEXT_OBEN + 22, s.get('wort', ''), 11, 600, cls.ZAHLFARBE)
        y = cls.TEXT_OBEN + 44
        for zeile in s.get('zeilen', ()):
            cls._text(teile, cx, y, zeile, 11)
            y += cls.ZEILE - 2
        g = s.get('gewichte')
        cls._text(teile, cx, y + 4, ('Gewichte %s' % cls._de(g)) if g else 'keine Gewichte', 11, 600 if g else 400)

    @classmethod
    def svg(cls, kennung, titel, untertitel, spalten, fuss=()):
        zeilen = max([len(s.get('zeilen', ())) for s in spalten] + [0])
        unten = cls.TEXT_OBEN + 54 + zeilen * (cls.ZEILE - 2)
        breite = cls._x(len(spalten)) + 6
        hoehe = unten + 26 + 18 * len(fuss)
        teile = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="%s" class="m3a-bild">' % (breite, hoehe, escape(titel)),
                 '<defs><marker id="%s-spitze" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#555"/></marker></defs>' % kennung,
                 '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (breite, hoehe)]
        cls._text(teile, 20, 24, titel, 15, 600, anker='start')
        cls._text(teile, 20, 44, untertitel, 12, anker='start')
        for i, s in enumerate(spalten):
            cls._spalte(teile, i, s, unten)
            if i:
                y = cls.KREISE_OBEN + cls.KREISE_HOEHE / 2
                teile.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#555" stroke-width="2" marker-end="url(#%s-spitze)"/>' % (
                    cls._x(i) - cls.ABSTAND + 2, y, cls._x(i) - 4, y, kennung))
        for z, f in enumerate(fuss):
            cls._text(teile, 20, unten + 22 + 18 * z, f, 12, 600 if z == 0 else 400, anker='start')
        teile.append('</svg>')
        return mark_safe(''.join(teile))
