# -*- coding: utf-8 -*-
"""Fallergebnis — was ein Oberflächen-Testfall zurückmeldet.

WARUM EINE KLASSE (17.08.2026, Kriterium 10/11)
===============================================
`TestCase.run()` gab ein Wörterbuch mit fünf Schlüsseln zurück, und ACHT Stellen
lasen daraus — die Testseite (`fallanzeige.js`), der Läufer
(`core/api/testlauf._einer`, der drei weitere Schlüssel dazuschreibt), der
Bildfolgen-Render, der Videokodierer und `server_neu.py`. Ein Wörterbuch, das so
weit reist, hat keine Stelle, an der steht, welche Felder es hat.

Die Klasse hat sie:

    ok           bestanden?
    name         Anzeigename des Falls
    description  Kurzbeschreibung (steht als Tooltip in der Tabelle)
    detail       Meldung des Falls („6 Presets vollständig")
    error        Ausnahme samt Rückverfolgung — `None`, wenn bestanden

`als_dict()` liefert genau die alten Schlüssel; der Vertrag mit dem Browser
bleibt unverändert.

WARUM `detail` UND `error` GETRENNT BLEIBEN
==========================================
`detail` ist die Aussage des Falls (auch im Erfolgsfall interessant: „Skip: kein
bake.npz"), `error` die Ausnahme. Zusammengelegt wüsste die Oberfläche nicht, ob
sie den Text grün oder rot zeigen soll.
"""

import traceback


class Fallergebnis:
    """Das Ergebnis eines Testfalls — mit `als_dict()` in der Browser-Form."""

    __slots__ = ('ok', 'name', 'description', 'detail', 'error')

    def __init__(self, ok, name, description='', detail='', error=None):
        self.ok = bool(ok)
        self.name = name
        self.description = description
        self.detail = detail
        self.error = error

    # ------------------------------------------------------------- Erzeugen

    @classmethod
    def aus_rueckgabe(cls, wert, name, description=''):
        """`True`, `(True, 'Text')` oder `(False, 'Grund')` -> Ergebnis.

        Ein Fall darf beides liefern: nur einen Wahrheitswert oder ein Paar mit
        Meldung. Ein Paar mit nur einem Element ist erlaubt (Meldung leer).
        """
        if isinstance(wert, tuple):
            ok = wert[0]
            detail = wert[1] if len(wert) > 1 else ''
        else:
            ok, detail = wert, ''
        return cls(ok, name, description, detail)

    @classmethod
    def aus_ausnahme(cls, fehler, name, description=''):
        """Gescheitert — mit Typ, Text und Rückverfolgung.

        Die Rückverfolgung gehört dazu: Ohne sie steht in der Tabelle
        „AssertionError" ohne Zeile, und der Fall muss von Hand nachgestellt
        werden.
        """
        return cls(False, name, description, '',
                   '%s: %s\n%s' % (type(fehler).__name__, fehler,
                                   traceback.format_exc()))

    # ------------------------------------------------------------- Ausgeben

    def als_dict(self):
        # Dictionary gewollt: geht als JSON an die Testseite.
        return {'ok': self.ok, 'name': self.name,
                'description': self.description, 'detail': self.detail,
                'error': self.error}
