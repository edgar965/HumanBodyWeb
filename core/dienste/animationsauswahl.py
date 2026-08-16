# -*- coding: utf-8 -*-
"""Animationsauswahl — der BVH-Bestand fuer das Auswahlfeld der Einstellungen.

PERFORMANCE 16.08.2026: Die fuenf Einstellungsseiten brauchten 235–408 ms, und
das Profil zeigte keinen einzigen teuren Aufruf, sondern 71.000
Variablenaufloesungen je Seitenaufbau. Ursache war die Vorgaengerfunktion
`_get_available_animations()`: sie lieferte **7.067 Animationen in 14
Kategorien**, und `_anim_selector.html` rendete jede einzelne als eigenes
`<div>` mit Inline-Stil — rund 400 Byte pro Eintrag.

    /settings/model/   4.741.402 Byte   14.138 Eintraege (Baustein zweimal drin)
    /settings/result/  2.379.937 Byte    7.070 Eintraege
    /settings/scene/   2.382.994 Byte    7.070 Eintraege
    /settings/theatre/ 2.251.882 Byte    7.070 Eintraege

Der Witz daran: jede Kategorie startet zugeklappt (`display:none`). Von den
7.067 Eintraegen sieht der Benutzer beim Aufruf **keinen**. Deshalb liefert
diese Klasse zwei getrennte Sichten — die 14 Kategoriekoepfe fuer die Seite,
die Eintraege einer Kategorie erst auf Nachfrage ueber
`/api/animationen/<kategorie>/`.

Zwei Wertformate, weil die Seiten den Wert unterschiedlich brauchen: die
Viewer-Seiten wollen die fertige URL `/api/character/bvh/<kat>/<name>/`, die
Theatre-Seite den kurzen Pfad `<kat>/<name>`. Frueher steuerte das der
Schalter `url_format` der Hilfsfunktion.
"""

from .bvhverzeichnis import Bvhverzeichnis


class Animationsauswahl:
    """Sicht auf `HumanBody/data/animations/bvh/` — Kategorien und Eintraege."""

    #: Wertformat fuer die Viewer-Seiten (Model, Result, Szene).
    ALS_URL = 'url'
    #: Wertformat fuer die Theatre-Seite.
    ALS_PFAD = 'pfad'

    def __init__(self, wertformat=ALS_URL, verzeichnis=None):
        self.wertformat = wertformat if wertformat == self.ALS_PFAD else self.ALS_URL
        self.verzeichnis = verzeichnis or Bvhverzeichnis()

    @classmethod
    def aus_anfrage(cls, request):
        return cls(wertformat=request.GET.get('wertformat', cls.ALS_URL))

    def kategorien(self):
        """Nur die Koepfe: Name und Anzahl. Leere Ordner fallen raus."""
        gefunden = []
        for name in self.verzeichnis.kategorienamen():
            anzahl = self.verzeichnis.anzahl(name)
            if anzahl:
                gefunden.append({'name': name, 'anzahl': anzahl})
        return gefunden

    def eintraege(self, kategorie):
        """Die Animationen EINER Kategorie.

        `kategorie` kommt aus der URL. Geprueft wird gegen die tatsaechlich
        vorhandenen Ordnernamen, nicht gegen ein Muster — damit ist auch
        `../../etc` erledigt, ohne dass man an jede Sonderform denken muss.
        """
        if kategorie not in self.verzeichnis.kategorienamen():
            return []
        return [{'value': self._wert(kategorie, datei.name), 'label': datei.name}
                for datei in self.verzeichnis.dateien(kategorie)]

    def _wert(self, kategorie, stamm):
        if self.wertformat == self.ALS_PFAD:
            return '%s/%s' % (kategorie, stamm)
        return '/api/character/bvh/%s/%s/' % (kategorie, stamm)

    def fehlt(self, wert):
        """True, wenn ein Wert gespeichert ist, die Datei aber nicht existiert.

        Befund 16.08.2026: In den Einstellungen stand
        `/api/character/bvh/Results/nussknacker/` — die Datei gibt es nicht
        (mehr). Sichtbar wurde das nur als zwei rote Zeilen in der
        Browserkonsole, wenn jemand die Konfigurationsseite oeffnete; die
        Einstellungsseite zeigte den Wert unbeanstandet an. Wer eine Animation
        umbenennt, soll das hier sehen.
        """
        zerlegt = self.zerlegen(wert)
        if zerlegt is None:
            return False
        kategorie, name = zerlegt
        return name not in {d.name for d in self.verzeichnis.dateien(kategorie)}

    def fehlende(self, werte):
        """Welche der uebergebenen Werte nicht mehr im Bestand liegen.

        Prueft je Kategorie nur einmal — zwei Auswahlfelder derselben Seite
        zeigen meist in denselben Ordner.
        """
        bekannt, fehlend = {}, set()
        for wert in werte:
            zerlegt = self.zerlegen(wert)
            if zerlegt is None:
                continue
            kategorie, name = zerlegt
            if kategorie not in bekannt:
                bekannt[kategorie] = {d.name
                                      for d in self.verzeichnis.dateien(kategorie)}
            if name not in bekannt[kategorie]:
                fehlend.add(wert)
        return fehlend

    def seitenteil(self, werte=()):
        """Der Zusammenhang, den `_anim_selector.html` braucht."""
        return {'anim_kategorien': self.kategorien(),
                'anim_fehlt': self.fehlende(werte)}

    @staticmethod
    def zerlegen(wert):
        """(Kategorie, Name) aus beiden Wertformaten, sonst None."""
        if not wert:
            return None
        teile = wert.strip('/').split('/')
        if wert.startswith('/api/character/bvh/'):
            teile = teile[3:]
        if len(teile) != 2 or not all(teile):
            return None
        return teile[0], teile[1]
