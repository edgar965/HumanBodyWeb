# -*- coding: utf-8 -*-
"""Modellstuecke — mit einem Modell gehen die Stücke, die nur für dieses Modell gebaut wurden (11.10.2026).

Edgar, 11.10.2026, nachdem er „cute girl Daz", „Daz1" und „Daz2" in der Oberfläche gelöscht hatte: „fixe: Warum liegen die noch in der Bibliothek?" Gemessen: `Modellablage.loeschen` löschte genau die Datei
`<Modell>.json` (Server-Log 14:24, drei Aufrufe von `modell/loeschen/`); die Stücke „cute girl Daz Scham", „Daz1 Scham" und „Daz2 Scham" (`Dazgeograftangepasst`) blieben in der eigenen Bibliothek. Sie gehören keinem
Blender-Import — `Blendimportloeschen` kennt sie nicht —, sondern dem Modell, das `Dazgeograftangepasst.modell_ableiten` für sie anlegt. Dieses Modell nennt sie jetzt in `figur.herkunft.daz_stuecke`.

HIER: `eigene` liest, welche Stücke ein Modell so nennt; `entfernen` legt jedes davon in den Papierkorb der Garderobe (`G9garderobepflege.loeschen`, zurückholbar), sofern KEIN anderes gespeichertes Genesis-9-Modell
es als Kleidung trägt. Ein Fehler bei einem Stück bricht das Löschen des Modells nie ab (Protokoll).
"""
import json
import logging

__all__ = ['Modellstuecke']

logger = logging.getLogger('core')


class Modellstuecke:
    @staticmethod
    def eigene(daten):
        """Kennungen (Garderobe, z. B. `cute_girl_daz3_scham`) der Stücke, die das Modell mit sich führt — `daten`: Inhalt von `<Modell>.json`."""
        figur = daten.get('figur') if isinstance(daten, dict) else None
        herkunft = (figur or {}).get('herkunft')
        if not isinstance(herkunft, dict):
            return []
        # `daz_stuecke`: das Daz-Stück von `modell_ableiten`; `eigene_stuecke`: ein für dieses Modell gebautes Eigen-Stück (z. B. „cute girl alt Scham")
        return [str(k) for s in ('daz_stuecke', 'eigene_stuecke') if isinstance(herkunft.get(s), list) for k in herkunft[s]]

    @classmethod
    def lesen(cls, pfad):
        """Die Stücke, die das Modell in der Datei `pfad` mit sich führt — leer, wenn die Datei fehlt oder nicht lesbar ist."""
        try:
            with open(pfad, encoding='utf-8') as datei:
                return cls.eigene(json.load(datei))
        except (OSError, ValueError):
            logger.warning('Modell %s: Stücke nicht lesbar', pfad)
            return []

    @classmethod
    def entfernen(cls, kennungen):
        """Die Stücke `kennungen` in den Papierkorb, die kein gespeichertes Modell mehr trägt → die Kennungen, die weg sind."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.garderobepflege import G9garderobepflege

        from .blendimportloeschen import Blendimportloeschen

        gebraucht = set()
        for modell in Blendimportloeschen.modelle_lesen():
            gebraucht |= modell['kleidung']
        weg = []
        for kennung in kennungen:
            if kennung in gebraucht:
                logger.info('Stück %s bleibt: ein anderes Modell trägt es', kennung)
                continue
            eintrag = G9garderobe.eintrag(kennung)
            if not eintrag or not eintrag.get('eigen'):
                logger.info('Stück %s: nicht (mehr) in der eigenen Garderobe', kennung)
                continue
            try:
                G9garderobepflege.loeschen(eintrag)
                weg.append(kennung)
            except (OSError, ValueError):
                logger.exception('Stück %s nicht gelöscht', kennung)
        return weg
