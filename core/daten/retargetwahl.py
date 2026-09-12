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
                 'figur', 'makro', 'regler')
    #: Ein Name ohne Pfad — bei UMA ein Dateiname im Figurkatalog (wie
    #: `Umafigur.NAME`), bei SMPL der Koerpername aus `Smplfiguren.KOERPER`
    #: bzw. einer Formvariante. Der Endpunkt prueft danach gegen seinen
    #: eigenen Bestand; hier faellt nur weg, was nach Pfad aussieht.
    FIGUR = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_ .\-]{0,120}$')

    #: Werte, die in der Abfragezeichenkette „ja" bedeuten.
    JA = ('1', 'true')
    #: Zielskelette (`target=`): das DEF-Skelett, die UMA-Figur aus dem
    #: Figurkatalog (05.09.2026), der SMPL-Koerper oder die MakeHuman-Figur
    #: (07.09.2026). Der erste Eintrag ist die Vorgabe.
    #: `umapython` (08.09.2026) ist die in Python gebaute UMA-Figur —
    #: dieselben Knochennamen wie `uma`, aber das Skelett kommt aus dem
    #: Bau, nicht aus einer GLB. Deshalb ein eigenes Ziel und KEIN
    #: Dateiname: `figur` traegt hier den Rassennamen.
    ZIELE = ('def', 'uma', 'smpl', 'makehuman', 'umapython')
    #: Ziele, deren `figur` ein GLB-Dateiname sein muss.
    GLB_ZIELE = ('uma',)

    def __init__(self, werte, vorgabe_groesse):
        self.groesse = float(werte.get('body_height', vorgabe_groesse))
        self.format = werte.get('format', None)
        self.fusskorrektur = str(
            werte.get('foot_correction', '')).lower() in self.JA
        self.delta_norm = self._dreiwertig(werte.get('delta_norm', ''))
        self.ziel = self._ziel(werte.get('target'))
        self.figur = self._figur(werte.get('figur'), self.ziel)
        # Die Reglerstellung der MakeHuman-Figur (07.09.2026). Ihr Skelett
        # sind Mittelwerte von Punkten DIESER Stellung — ohne sie stuende
        # das Ziel in der Vorgabefigur, und die Bewegung landete auf einem
        # anderen Koerper als dem in der Szene. 269 Regler passen in keine
        # Abfragezeichenkette; sie kommen deshalb aus dem JSON-Rumpf.
        rumpf = werte if isinstance(werte, dict) else {}
        self.makro = rumpf.get('makro')
        self.regler = rumpf.get('regler')

    @classmethod
    def _ziel(cls, roh):
        ziel = (roh or cls.ZIELE[0]).lower()
        if ziel not in cls.ZIELE:
            raise ValueError('Unbekanntes Ziel %r — erlaubt: %s'
                             % (ziel, ', '.join(cls.ZIELE)))
        return ziel

    @classmethod
    def _figur(cls, roh, ziel):
        """WELCHE UMA-Figur (06.09.2026): Ohne `figur` galt die Datei aus
        `aktuell.json` — die Roomguest setzt, nicht die Szene. Deren
        `UmaKleidung_bewegt.glb` traegt einen anders gedrehten Wurzelknoten;
        die Hueftspur landete damit in der falschen Achse (Hoehe in X), und
        jede UMA-Figur der Szene lag bei `0101_Boden` flach am Boden."""
        figur = (roh or '').strip() or None
        if figur is None:
            return None
        if not cls.FIGUR.match(figur) or '..' in figur:
            raise ValueError('Ungültiger Figurname %r' % (figur,))
        if ziel in cls.GLB_ZIELE and not figur.lower().endswith('.glb'):
            raise ValueError('Ungültiger Figurname %r' % (figur,))
        return figur

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
