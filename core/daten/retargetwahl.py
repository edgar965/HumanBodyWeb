# -*- coding: utf-8 -*-
"""Retargetwahl — die vier Stellschrauben einer Retarget-Anfrage.

Sie kamen als Vierertupel aus `_wahlwerte` und wurden beim Aufrufer wieder
auseinandergenommen (Befund `rueckgabetupel`, 27.08.2026) — genau die Bauform,
gegen die `daten/koerperzustand.py` schon einmal getauscht wurde:

    groesse, art, fusskorrektur, delta = cls._wahlwerte(request.GET)

Ein Tupel sagt nicht, was `[2]` bedeutet, und beim Erweitern verschieben sich
alle Stellen stillschweigend.

`delta_norm` ist DREIWERTIG und deshalb kein `bool`: `'1'` schaltet ein, `'0'`
aus, und alles andere (auch ein fehlender Parameter) heisst „wie das Format es
vorsieht". Ein `bool` haette den dritten Fall verschluckt.

`figur` (06.09.2026) nennt die UMA-Datei im Figurkatalog, deren Skelett das
Ziel ist. Ohne sie gilt die Datei aus `aktuell.json` — das ist die, die
Roomguest spielt, nicht die, die in der Szene steht.
"""
import re


class Retargetwahl:
    """Was der Aufrufer am Retarget einstellen darf."""

    __slots__ = ('groesse', 'format', 'fusskorrektur', 'delta_norm', 'ziel',
                 'figur')
    #: Ein Dateiname im Figurkatalog, kein Pfad (wie `Umafigur.NAME`).
    FIGUR = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_ .\-]*\.glb$')

    #: Werte, die in der Abfragezeichenkette „ja" bedeuten.
    JA = ('1', 'true')
    #: Zielskelette (`target=`): das DEF-Skelett oder die UMA-Figur aus dem
    #: Figurkatalog (05.09.2026). Der erste Eintrag ist die Vorgabe.
    ZIELE = ('def', 'uma')

    def __init__(self, werte, vorgabe_groesse):
        self.groesse = float(werte.get('body_height', vorgabe_groesse))
        self.format = werte.get('format', None)
        self.fusskorrektur = (werte.get('foot_correction', '').lower()
                              in self.JA)
        self.delta_norm = self._dreiwertig(werte.get('delta_norm', ''))
        self.ziel = (werte.get('target') or self.ZIELE[0]).lower()
        if self.ziel not in self.ZIELE:
            raise ValueError('Unbekanntes Ziel %r — erlaubt: %s'
                             % (self.ziel, ', '.join(self.ZIELE)))
        # WELCHE UMA-Figur (06.09.2026): Ohne `figur` galt die Datei aus
        # `aktuell.json` — die Roomguest setzt, nicht die Szene. Deren
        # `UmaKleidung_bewegt.glb` traegt einen anders gedrehten Wurzelknoten;
        # die Hueftspur landete damit in der falschen Achse (Hoehe in X), und
        # jede UMA-Figur der Szene lag bei `0101_Boden` flach am Boden.
        self.figur = (werte.get('figur') or '').strip() or None
        if self.figur and (not self.FIGUR.match(self.figur) or '..' in self.figur):
            raise ValueError('Ungültiger Figurname %r' % (self.figur,))

    @staticmethod
    def _dreiwertig(roh):
        """`'1'` -> True, `'0'` -> False, sonst None (Format entscheidet)."""
        text = str(roh).lower()
        if text == '1':
            return True
        if text == '0':
            return False
        return None

    def __repr__(self):
        return ('<Retargetwahl %.2f m, %s, Fuss=%s, Delta=%s, Ziel=%s%s>'
                % (self.groesse, self.format or 'erkannt', self.fusskorrektur,
                   self.delta_norm, self.ziel,
                   ' ' + self.figur if self.figur else ''))
