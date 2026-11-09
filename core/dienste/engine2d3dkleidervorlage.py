# -*- coding: utf-8 -*-
"""Engine2d3dKleidervorlage — das erste Foto der Bildauswahl als kleines Tabellenbild (30.09.2026).

Die Spalte „Vorlage" der Tabelle zeigt das Foto auf Platz 1. Die Originale sind mehrere MB groß — bei
sechzehn Zeilen wären das zweistellige Megabyte nur für Daumennägel —, deshalb liegt daneben eine
verkleinerte Fassung: `vorlage/vorlage.png` (`Meshicon.vorlage_schreiben`), ihr Name in
`ergebnis['vorlage_foto']`.

Sie muss nachgezogen werden, wann immer sich Platz 1 ändert: beim Anlegen, beim Umsortieren, beim Ersetzen,
Hinzufügen und Entfernen von Fotos. Nur Pillow, kein OpenGL — das darf im Serverprozess laufen.

`updated_at` wird immer mit gespeichert: Die Tabelle hängt es als `?v=` an die Bildadresse, und ein
gleichnamiges Bild mit neuem Inhalt käme sonst aus dem Browsercache.
"""

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .meshicon import Meshicon
from .blendermodellvorlage import Blendermodellvorlage

__all__ = ['Engine2d3dKleidervorlage']


class Engine2d3dKleidervorlage:
    ABLAGE = Engine2d3dKleiderablage        # Ablage der Familie (`Blendermodellvorlage.erneuern`)
    SCHLUESSEL = 'vorlage_foto'

    erneuern = classmethod(Blendermodellvorlage.erneuern.__func__)          # dieselbe Rechnung wie `Blendermodellvorlage.erneuern` (bis 08.11.2026 eine Kopie hier)

    @staticmethod
    def _schreiben(job, ablage):
        bilder = job.bilder or []
        if not bilder or not bilder[0].get('datei'):
            return ''
        quelle = ablage.unter(Engine2d3dKleiderablage.EINGANG) / bilder[0]['datei']
        ziel = ablage.vorlage()
        ziel.mkdir(parents=True, exist_ok=True)
        if not quelle.is_file():
            return ''
        return Meshicon.vorlage_schreiben(quelle, ziel)
