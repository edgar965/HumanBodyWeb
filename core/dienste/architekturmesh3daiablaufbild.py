# -*- coding: utf-8 -*-
"""Architekturmesh3daiablaufbild — die übergeordnete Grafik „Wie die KIs aufgerufen werden“ für Hilfe → Architektur → Mesh3DAI (24.10.2026 abends, Edgar: „eine übergeordnete Grafik mit Kästchen und
Ablauf, wie die KIs aufgerufen werden“).

Links die elf Schritte des Rechenlaufs in ihrer Reihenfolge (aus `Mesh3dairechenlauf.SCHRITTE`), rechts je Schritt, wer rechnet: unsere KIs grün (mit dem Lauf aus ki_fassungen.json), fertige
Modelle anderer grau, eigene Rechnung ohne Gewichte blau. Was zu wem gehört, steht in `Architekturmesh3daikis.BETEILIGT`.

    svg = Architekturmesh3daiablaufbild.svg(schritte)
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

__all__ = ['Architekturmesh3daiablaufbild']


class Architekturmesh3daiablaufbild:
    ZEILE, KASTEN_H = 64, 46
    LINKS_B = 430
    CHIP_B, CHIP_ABSTAND = 300, 14
    FARBEN = {'ki': ('#d5e8d4', '#82b366'), 'fremd': ('#eeeeee', '#999999'), 'rechnung': ('#dae8fc', '#6c8ebf'), 'schritt': ('#ffffff', '#555555')}
    LEGENDE = (('ki', 'unsere KI (Netz aus ki_fassungen.json)'), ('fremd', 'fertiges Modell eines anderen'), ('rechnung', 'eigene Rechnung, ohne Gewichte'))

    @classmethod
    def _kasten(cls, x, y, b, art, zeilen):
        fuell, rand = cls.FARBEN[art]
        teile = ['<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x, y, b, cls.KASTEN_H, fuell, rand)]
        for i, (text, fett) in enumerate(zeilen[:2]):
            teile.append('<text x="%d" y="%d" font-size="%d" %sfill="#222">%s</text>' % (x + 10, y + 19 + 17 * i, 13 if i == 0 else 11, 'font-weight="bold" ' if fett else '', escape(text)))
        return teile

    @classmethod
    def svg(cls, schritte):
        meist = max((len(s['beteiligt']) for s in schritte), default=1)
        breite = 20 + cls.LINKS_B + 60 + meist * (cls.CHIP_B + cls.CHIP_ABSTAND)
        oben = 60
        hoehe = oben + len(schritte) * cls.ZEILE + 40
        teile = ['<text x="20" y="26" font-size="16" font-weight="bold" fill="#222">Rechnen per Knopf: Mesh → Genesis-Figur mit Kleidern, Haar, Haut</text>']
        lx = 20
        for art, text in cls.LEGENDE:
            fuell, rand = cls.FARBEN[art]
            teile.append('<rect x="%d" y="36" width="14" height="14" fill="%s" stroke="%s"/><text x="%d" y="48" font-size="12" fill="#333">%s</text>' % (lx, fuell, rand, lx + 20, escape(text)))
            lx += 30 + 7 * len(text)
        for i, s in enumerate(schritte):
            y = oben + i * cls.ZEILE
            teile += cls._kasten(20, y, cls.LINKS_B, 'schritt', [('%d · %s' % (s['nr'], s['text'][:58]), True), (s['schluessel'], False)])
            if i < len(schritte) - 1:
                teile.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#555" stroke-width="2" marker-end="url(#pfeil-ablauf)"/>' % (
                    20 + cls.LINKS_B // 2, y + cls.KASTEN_H + 1, 20 + cls.LINKS_B // 2, y + cls.ZEILE - 3))
            for j, b in enumerate(s['beteiligt']):
                x = 20 + cls.LINKS_B + 60 + j * (cls.CHIP_B + cls.CHIP_ABSTAND)
                if j == 0:
                    teile.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#888" stroke-width="1.5" stroke-dasharray="4 3"/>' % (
                        20 + cls.LINKS_B, y + cls.KASTEN_H // 2, x - 2, y + cls.KASTEN_H // 2))
                zweite = (b['lauf'] or '—', False) if b['art'] == 'ki' else ({'fremd': 'fremdes Modell', 'rechnung': 'eigene Rechnung'}[b['art']], False)
                teile += cls._kasten(x, y, cls.CHIP_B, b['art'], [(b['titel'][:40], True), (str(zweite[0])[:48], False)])
        kopf = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-label="Ablauf der KIs" style="background:#fff;max-width:%dpx">'
                '<defs><marker id="pfeil-ablauf" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#555"/></marker></defs>'
                % (breite, hoehe, breite))
        return mark_safe(kopf + ''.join(teile) + '</svg>')
