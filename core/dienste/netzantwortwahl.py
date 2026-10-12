# -*- coding: utf-8 -*-
"""Netzantwortwahl — wo die Szene die Netzantworten ihrer Genesis-9-Figuren hält: im RAM (Vorgabe) oder gar nicht.

Edgar (12.10.2026): „mach das einstellbar im RAM, einstellbar unter Einstellungen - Charakter. Default: RAM." Gemeint ist der Antwortspeicher der Figuren
(`static/viewer/gemeinsam/genesis9antwortspeicher.js`): Körper und jedes Daz-Stück bleiben je Stufe (grob, fein, ultrafein) im Arbeitsspeicher des Browsers liegen, damit
ein Stufenwechsel und ein Hautwechsel das Netz nicht noch einmal vom Server holen. Die Wahl liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL` (Seite Einstellungen →
Charakter, `core/api/einstellungen/szenenseite.py`); die Szene liest sie beim Laden (`static/viewer/charakter/starteinstellungen.js`), sie wirkt nach dem Neuladen.

    ram     jede gebaute Antwort bleibt im Speicher der Figur (gemessen, cute girl Daz mit fünf Stücken: grob und fein rund 24 MB, mit ultrafein rund 61 MB)
    server  nichts wird gehalten: jeder Stufen- und Hautwechsel fragt den Server wie vor dem 12.10.2026 (Hautwechsel: das ganze Netz, 10 MB bei fein)
"""

__all__ = ['Netzantwortwahl']


class Netzantwortwahl:
    SCHLUESSEL = 'netzantworten'
    RAM = 'ram'
    SERVER = 'server'
    VORGABE = RAM
    #: Wert → Anzeigetext, in der Reihenfolge der Auswahl.
    WAHLEN = {
        RAM: 'Im RAM halten (Vorgabe)',
        SERVER: 'Nicht halten — jedes Mal vom Server holen',
    }

    @classmethod
    def aus(cls, prefs):
        """Die Wahl aus einem `ui_prefs`-Dict; Unbekanntes heißt Vorgabe."""
        wert = str((prefs or {}).get(cls.SCHLUESSEL) or cls.VORGABE)
        return wert if wert in cls.WAHLEN else cls.VORGABE
