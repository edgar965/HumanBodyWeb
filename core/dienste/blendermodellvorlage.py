# -*- coding: utf-8 -*-
"""Blendermodellvorlage — das erste Foto der Bildauswahl als kleines Tabellenbild (29.09.2026).

Die Spalte „Vorlage" der Tabelle zeigt das Foto auf Platz 1. Die Originale sind mehrere MB groß — bei
sechzehn Zeilen wären das zweistellige Megabyte nur für Daumennägel —, deshalb liegt daneben eine verkleinerte
Fassung: `netz/vorlage.png` (`Meshicon.vorlage_schreiben`), ihr Name in `ergebnis['vorlage_foto']`.

Sie muss nachgezogen werden, wann immer sich Platz 1 ändert: beim Anlegen, beim Umsortieren, beim Ersetzen,
Hinzufügen und Entfernen von Fotos. Nur Pillow, kein OpenGL — das darf im Serverprozess laufen.

`updated_at` wird immer mit gespeichert: Die Tabelle hängt es als `?v=` an die Bildadresse, und ein
gleichnamiges Bild mit neuem Inhalt käme sonst aus dem Browsercache.
"""

from ..daten.blendermodellablage import Blendermodellablage
from .meshicon import Meshicon

__all__ = ['Blendermodellvorlage']


class Blendermodellvorlage:
    SCHLUESSEL = 'vorlage_foto'

    @classmethod
    def erneuern(cls, job):
        """Das Vorlagenbild neu schreiben und im Auftrag vermerken → sein Dateiname oder ''."""
        ablage = Blendermodellablage(job.kennung)
        name = cls._schreiben(job, ablage)
        ergebnis = dict(job.ergebnis or {})
        if name:
            ergebnis[cls.SCHLUESSEL] = name
        else:
            ergebnis.pop(cls.SCHLUESSEL, None)
        job.ergebnis = ergebnis
        job.save(update_fields=['ergebnis', 'updated_at'])
        return name

    @staticmethod
    def _schreiben(job, ablage):
        bilder = job.bilder or []
        if not bilder or not bilder[0].get('datei'):
            return ''
        quelle = ablage.unter(Blendermodellablage.EINGANG) / bilder[0]['datei']
        ziel = ablage.netz()
        ziel.mkdir(parents=True, exist_ok=True)
        if not quelle.is_file():
            return ''
        return Meshicon.vorlage_schreiben(quelle, ziel)
