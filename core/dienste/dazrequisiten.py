# -*- coding: utf-8 -*-
"""Dazrequisiten — Props, die Daz AUSSERHALB von `People/` ablegt, als Requisiten einer Fremdfigur in die Garderobe (10.10.2026).

Edgar: „portiere die auch, wenn es geht: Melee-Waffen (Szenen-Props)". `Scifi Melee Weapons` (Daz 12014, 2014) liegen als
`Props/SciFiMelee/<Waffe>.duf` (`wearable`, Elternknochen `rHand` bzw. `rForeArm`, keine Griffpose) direkt unter der Bibliothekswurzel, die Garderobe
liest Props aber nur unter `People/<Figur>/Props`. Die Daz-Bibliothek wird nie beschrieben; deshalb wandern die `.duf` (und ihre Vorschaubilder) als
KOPIE in die eigene Wurzel `People/Genesis/Props/<Satz>` — Genesis (1), weil die Knoten an `rHand` hängen und ihre Lage im Raum dieser Figur steht
(Ruhelage Hand bei x ≈ −79 cm). Netze (`/data/DAZ 3D/Sci-Fi Melee Weapons/…`) und Texturen (`/Runtime/Textures/SciFiMelee/…`) löst `G9pfade` in der
Daz-Bibliothek auf; kopiert wird nur, was klein und lesbar ist. Die Kopien sind Daz-Inhalt: `3DObjects/` ist nicht im Git (`HERKUNFT.md`).
"""
import logging
import shutil

logger = logging.getLogger('core')

__all__ = ['Dazrequisiten']


class Dazrequisiten:
    #: `(Ordner unter Props/ der Daz-Bibliothek, Figur unter People/ der eigenen Wurzel)`.
    SAETZE = (('SciFiMelee', 'Genesis'),)

    @classmethod
    def einbauen(cls):
        """Alle `SAETZE` kopieren → `{satz: [Dateinamen der .duf]}`. Wiederholbar; vorhandene Kopien werden überschrieben."""
        from Genesis9.pfade import G9pfade

        aus = {}
        for satz, figur in cls.SAETZE:
            quelle = G9pfade.bibliothek() / 'Props' / satz
            if not quelle.is_dir():
                raise FileNotFoundError('Daz-Bibliothek hat keinen Ordner Props/%s (%s)' % (satz, quelle))
            ziel = G9pfade.eigene() / 'People' / figur / 'Props' / satz
            ziel.mkdir(parents=True, exist_ok=True)
            namen = []
            for datei in sorted(quelle.iterdir()):
                if datei.suffix.lower() in ('.duf', '.png'):
                    shutil.copy2(datei, ziel / datei.name)
                    if datei.suffix.lower() == '.duf':
                        namen.append(datei.name)
            logger.info('Daz-Requisiten %s: %d .duf nach %s kopiert', satz, len(namen), ziel)
            aus[satz] = namen
        return aus
