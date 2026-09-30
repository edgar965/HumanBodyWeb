# -*- coding: utf-8 -*-
"""Kostuemmodellablage — das Modell EINER Runde (GLB, Ansichten mit Fototextur, Sichtmodell) nach `iterationen/` legen.

Bis 30.09.2026 stand das in `Kostuemrunde.ablegen`, und nur dort: Ein Modell bekam nur, wer übernommen war und zufällig in
ein Zeitfenster fiel (`Kostuemrunde.modell_faellig`). Die NEUESTE Runde war deshalb meist ein verworfener Vorschlag der Prüf-KI
ohne Modell, und die Tabelle „Iterationen" zeigte von ihr nur den flachen Render — neben dem texturierten Bild der besten Runde
sah das wie eine uralte Runde aus (Edgar, 30.09.2026: „das ist ein Bild von einer sehr alten Runde!"). `nachtragen` baut das
Modell für einen schon abgelegten Eintrag nach; `Kostuemabschluss` ruft es für die neueste Runde am Ende jedes Laufs.
"""

import logging
import shutil

logger = logging.getLogger('core')

__all__ = ['Kostuemmodellablage']


class Kostuemmodellablage:
    @classmethod
    def ablegen(cls, runde_, runde, werte, dateien, je_ansicht, sicht=False):
        """Modell zu `werte` bauen (`Kostuemrunde.modell`) und nach `iterationen/` kopieren; `dateien` (`modell`, `sicht`) und
        `je_ansicht` (`textur`, `sicht` je Ansicht) werden dabei ergänzt. Scheitert der Bau, bleibt beides unverändert."""
        ziel = runde_.ablage.iterationen()
        modell = runde_.modell(runde, werte, sicht=sicht)
        if modell.glb is not None:
            dateien['modell'] = 'runde_%03d_modell.glb' % runde
            shutil.copyfile(modell.glb, ziel / dateien['modell'])
        if modell.sicht is not None:
            dateien['sicht'] = 'runde_%03d_sicht.glb' % runde
            shutil.copyfile(modell.sicht, ziel / dateien['sicht'])
        for a in je_ansicht:
            w = str(int(round(a['winkel'])))
            for schluessel, fotos, vorsatz in (
                ('textur', modell.fotos, 'textur_'),
                ('sicht', modell.sichtfotos, 'sicht_'),
            ):
                quelle = fotos.get(w)
                if quelle is not None and quelle.is_file():
                    a[schluessel] = 'runde_%03d_%s%s' % (runde, vorsatz, quelle.name.split(vorsatz, 1)[-1])
                    runde_.zuschneiden(quelle, ziel / a[schluessel])

    @classmethod
    def nachtragen(cls, runde_, eintrag):
        """Das Modell für einen Eintrag von `ergebnis['iterationen']` nachbauen, der keines hat (verworfene Vorschläge der
        Prüf-KI, Runden außerhalb des Zeitfensters). Der Eintrag wird verändert, gesichert wird vom Aufrufer.
        → True, wenn danach ein Modell da ist."""
        dateien = eintrag.setdefault('dateien', {})
        if dateien.get('modell'):
            return True
        runde = int(eintrag['runde'])
        cls.ablegen(runde_, runde, eintrag['werte'], dateien, eintrag.get('je_ansicht') or [])
        runde_.aufraeumen(runde)
        if not dateien.get('modell'):
            logger.warning('BlenderModel %s: Modell der Runde %d nicht entstanden', runde_.job.kennung, runde)
        return bool(dateien.get('modell'))
