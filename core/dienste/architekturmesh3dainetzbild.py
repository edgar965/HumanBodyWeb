# -*- coding: utf-8 -*-
"""Architekturmesh3dainetzbild — EINE Grafik je KI für Hilfe → Architektur → Mesh3DAI (24.10.2026 abends, Edgar: „für alle KIs eine einzelne Grafik wie diese: Neuronale Netz - Figur“).

Dieselbe Bildsprache wie `Architekturmesh3daibild` (Eingabe rot, verdeckte Schichten blau, Ausgabe grün): je Baustein des Netzes eine Spalte — Wort, die Zahl der Kanäle danach groß, die Kette
der Kanäle durch seine Schichten, die Gewichte. Die Bausteine und Zahlen kommen aus dem Steckbrief der Gewichtsdatei (`Architekturmesh3daikis.spalten`), Eingang und Ausgang aus `KIS`.

    svg = Architekturmesh3dainetzbild.svg(beschreibung, spalten)
"""

from django.utils.html import escape
from django.utils.safestring import mark_safe

from .architekturmesh3daibild import Architekturmesh3daibild

__all__ = ['Architekturmesh3dainetzbild']


def _de(n):
    return '{:,}'.format(int(n)).replace(',', '.')


class Architekturmesh3dainetzbild:
    #: Köpfe, die nicht HINTER dem vorigen Baustein rechnen, sondern daneben aus dem Merkmal der ganzen Figur (`Formnetz.form`, Haarmaße der Zerlegung) — gelb wie im Bild „Figur“
    NEBENKOEPFE = ('form', 'haar')
    SPALTE, ABSTAND = 150, 26
    OBEN, HOEHE = 20, 250
    ZEICHEN = 22

    @classmethod
    def _umbrechen(cls, text, breite=None):
        breite = breite or cls.ZEICHEN
        zeilen, z = [], ''
        for w in str(text).split():
            if z and len(z) + 1 + len(w) > breite:
                zeilen.append(z)
                z = w
            else:
                z = (z + ' ' + w).strip()
        if z:
            zeilen.append(z)
        return zeilen

    @classmethod
    def _kasten(cls, x, art, titel, gross, zeilen):
        fuell, rand = Architekturmesh3daibild.FARBEN[art]
        teile = ['<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" stroke="%s" stroke-width="2"/>' % (x, cls.OBEN, cls.SPALTE, cls.HOEHE, fuell, rand),
                 '<text x="%d" y="%d" text-anchor="middle" font-size="14" font-weight="bold" fill="#222">%s</text>' % (x + cls.SPALTE // 2, cls.OBEN + 24, escape(titel))]
        y = cls.OBEN + 64
        if gross:
            teile.append('<text x="%d" y="%d" text-anchor="middle" font-size="28" font-weight="bold" fill="%s">%s</text>' % (x + cls.SPALTE // 2, y, Architekturmesh3daibild.ZAHLFARBE,
                                                                                                                         escape(gross)))
            y += 26
        for z, fett in zeilen:
            for teil in cls._umbrechen(z):
                teile.append('<text x="%d" y="%d" text-anchor="middle" font-size="12" %sfill="#333">%s</text>' % (x + cls.SPALTE // 2, y, 'font-weight="bold" ' if fett else '', escape(teil)))
                y += 16
        return teile

    @classmethod
    def svg(cls, beschr, spalten):
        n = len(spalten) + 2
        breite = 20 + n * (cls.SPALTE + cls.ABSTAND)
        teile = []
        x = 20
        teile += cls._kasten(x, 'eingabe', 'Eingang', None, [(beschr['eingang'], False)])
        for i, s in enumerate(spalten):
            x = 20 + (i + 1) * (cls.SPALTE + cls.ABSTAND)
            kette = s['kette']
            zeilen = [('%s Gewichte' % _de(s['gewichte']), True)]
            if len(kette) > 1:
                zeilen.insert(0, ('Kanäle ' + ' → '.join(_de(k) for k in kette), False))
            neben = s['erst'] in cls.NEBENKOEPFE
            if neben:
                zeilen.append(('neben dem Kopf, aus dem Merkmal der ganzen Figur', False))
            teile += cls._kasten(x, 'form' if neben else 'versteckt', s['wort'], _de(kette[-1]) if kette else None, zeilen)
        x = 20 + (n - 1) * (cls.SPALTE + cls.ABSTAND)
        teile += cls._kasten(x, 'ausgabe', 'Ausgang', None, [(beschr['ausgang'], False)])
        for i in range(n - 1):
            x0 = 20 + i * (cls.SPALTE + cls.ABSTAND) + cls.SPALTE
            y = cls.OBEN + cls.HOEHE // 2
            teile.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#555" stroke-width="2" marker-end="url(#pfeil-netz)"/>' % (x0 + 2, y, x0 + cls.ABSTAND - 4, y))
        kopf = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-label="%s" style="background:#fff;max-width:%dpx">'
                '<defs><marker id="pfeil-netz" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#555"/></marker></defs>'
                % (breite, cls.OBEN * 2 + cls.HOEHE, escape(beschr['titel']), breite))
        return mark_safe(kopf + ''.join(teile) + '</svg>')
