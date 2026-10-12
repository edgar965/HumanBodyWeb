# -*- coding: utf-8 -*-
"""Mesh3dname — den Namen eines Mesh-3D-Auftrags auf der Jobseite ändern (12.10.2026).

Edgar: „Name des Jobs nicht änderbar (schau die 2D3D Kleider an, da ist der Name änderbar)“. Dort ist die Überschrift selbst das Eingabefeld (`gemeinsam/auftragname.js`, Klick oder Stift, Enter speichert);
bei Mesh-3D stand der Name nur in der Karte „Quelle“ und änderte sich dort zusammen mit der Datei (`Mesh3dquellwechsel`).

Der Name eines Auftrags ist `stand.quelle.name`. Die Liste, die Überschrift, der Tab-Titel und die Kopie lesen ihn dort; die Karte „Quelle“ zeigt `einstellungen.eigener_name`. Beides wird gesetzt, damit die Karte nach dem
Umbenennen denselben Namen zeigt und ein späteres „Netz ändern“ ihn behält. Es gilt die Regel des Import-Namensfelds (`Blendimportquelle.eigener`: Buchstaben, Ziffern, Leerzeichen, Bindestrich, höchstens 60 Zeichen),
weil der Name Teil von Dateinamen der Stücke wird.

**Der Name ist Beschriftung:** das gespeicherte Modell und der Auftrag „Mesh to 3D“ eines früheren Laufs behalten ihren Namen; der nächste Lauf ab „figur“ bzw. „modell“ benennt sie nach dem neuen.
Während eines Laufs geht nichts: der Arbeitsprozess schreibt `stand.json` aus seinem Speicher und würde den neuen Namen zurücksetzen (409 im Endpunkt, wie bei `Mesh3dquellwechsel`).
"""

from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter
from .blendimportquelle import Blendimportquelle

__all__ = ['Mesh3dname']


class Mesh3dname:
    class Laeuft(ValueError):
        """Der Auftrag rechnet — der Endpunkt antwortet 409."""

    def __init__(self, kennung):
        try:
            self.ablage = Blendimportablage(kennung)
        except ValueError as fehler:
            raise ValueError('Kein Auftrag %s' % kennung) from fehler
        self.stand = self.ablage.stand()
        if not self.stand:
            raise ValueError('Kein Auftrag %s' % kennung)

    def setzen(self, text):
        """→ der gespeicherte Name; `ValueError` bei leerem Text, `Laeuft`, solange der Auftrag rechnet."""
        name = Blendimportquelle.eigener(text)
        if Blendimportarbeiter.lebt(self.ablage) and self.stand.get('status') in ('laeuft', 'neu'):
            raise self.Laeuft('Der Auftrag rechnet — den Namen nach dem Lauf ändern (oder erst anhalten)')
        stand = self.ablage.stand()
        stand['quelle'] = {**(stand.get('quelle') or {}), 'name': name}
        stand['einstellungen'] = {**(stand.get('einstellungen') or {}), 'name': 'eigen', 'eigener_name': name}
        self.ablage.stand_schreiben(stand)
        return name
