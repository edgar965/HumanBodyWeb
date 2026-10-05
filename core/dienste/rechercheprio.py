# -*- coding: utf-8 -*-
"""Rechercheprio — die Handwertung „Prio" der Recherche-Tabelle: ob wir ein Projekt testen oder einbauen (04.10.2026).

Edgar: „mach in der Tabelle eine neue Spalte: Prio mit veränderbaren Zahlen, ich möchte darin die Prio eingeben, ob wir das testen / einbauen. keine zwei gleiche Prios, wenn ich was
ändere schiebt sich das dazwischen".

Jede Zahl gehört höchstens einem Projekt (1 = zuerst). Vergibt man eine Zahl, die schon ein anderes Projekt trägt, bekommt das neue Projekt sie, und das bisherige rückt um eins nach hinten —
trägt die nächste Zahl wieder ein Projekt, rückt auch dieses, und so fort, bis ein freier Platz kommt. Die eingegebene Zahl bleibt dabei, wie sie ist (anders als die lückenlose Rangliste der
Qualitätsspalten von „2D3D Kleider": dort wäre aus einer 10 bei zwei bewerteten Läufen eine 3 geworden); der frei gewordene alte Platz bleibt leer. Leer lassen nimmt das Projekt aus der Liste.

Die Prioritäten sind Edgars Eingaben und stehen darum NICHT in `core/daten/recherche_human3d.json` — eine neue Recherche schriebe diese Datei neu und löschte sie. Sie liegen unter
`3DObjects/recherche/human3d_prio.json` (nicht versioniert), `{projektkennung: Zahl}`, unteilbar geschrieben (`AtomarSchreiber`). `verteilen` rechnet nur auf einem Wörterbuch; `setzen` liest,
verteilt und schreibt unter einer Sperre (ein zweiter Tab darf nicht zwischen Lesen und Schreiben dazwischenkommen).
"""

import json
import logging
import threading
from pathlib import Path

from django.conf import settings

from ..atomic_write import AtomarSchreiber

__all__ = ['Rechercheprio']

logger = logging.getLogger('core')


class Rechercheprio:
    HOECHSTENS = 9999
    #: `data-sort` einer Zelle ohne Prio: ans Ende sortiert, nicht vor Prio 1.
    SORT_OHNE_PRIO = 999999
    _sperre = threading.Lock()

    @classmethod
    def pfad(cls):
        return Path(settings.OBJECTS_ROOT) / 'recherche' / 'human3d_prio.json'

    @classmethod
    def normieren(cls, wert):
        """Die Prio als ganze Zahl von 1 bis `HOECHSTENS`; `None`/leer = keine Prio. Alles andere wirft ValueError (kein stilles Runden: 2,5 oder „abc" sind Tippfehler)."""
        if wert is None or (isinstance(wert, str) and not wert.strip()):
            return None
        if isinstance(wert, bool):
            raise ValueError('Die Prio muss eine ganze Zahl sein.')
        try:
            zahl = float(str(wert).strip().replace(',', '.')) if isinstance(wert, str) else float(wert)
        except (TypeError, ValueError):
            raise ValueError('Die Prio muss eine ganze Zahl sein.') from None
        if zahl != int(zahl):
            raise ValueError('Die Prio muss eine ganze Zahl sein.')
        zahl = int(zahl)
        if not 1 <= zahl <= cls.HOECHSTENS:
            raise ValueError('Die Prio liegt zwischen 1 und %d.' % cls.HOECHSTENS)
        return zahl

    @classmethod
    def verteilen(cls, prios, kennung, wert):
        """Die neue Zuordnung `{kennung: Prio}`; `prios` bleibt unverändert. `wert = None` nimmt `kennung` heraus. Sonst trägt `kennung` den Wert, und wer ihn schon hatte, rückt um eins
        nach hinten — und wer dort stand, ebenfalls —, bis ein freier Platz kommt."""
        neu = {k: v for k, v in prios.items() if k != kennung}
        if wert is None:
            return neu
        besetzer = {v: k for k, v in neu.items()}
        neu[kennung] = wert
        platz = wert
        while platz in besetzer:
            verdraengt = besetzer[platz]
            platz += 1
            if platz > cls.HOECHSTENS:
                raise ValueError('Kein freier Platz hinter Prio %d.' % wert)
            neu[verdraengt] = platz
        return neu

    @classmethod
    def laden(cls):
        """`{kennung: Prio}` aus der Ablage; fehlt sie oder ist sie unlesbar, ist niemand eingestuft (mit Warnung im Log — eine kaputte Datei darf die Seite nicht kippen)."""
        pfad = cls.pfad()
        if not pfad.is_file():
            return {}
        try:
            roh = json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Rechercheprio: %s ist unlesbar — keine Prioritäten geladen.', pfad)
            return {}
        ergebnis = {}
        for kennung, wert in (roh.items() if isinstance(roh, dict) else []):
            try:
                prio = cls.normieren(wert)
            except ValueError:
                continue
            if prio is not None and prio not in ergebnis.values():
                ergebnis[str(kennung)] = prio
        return ergebnis

    @classmethod
    def setzen(cls, kennung, wert):
        """Vergibt oder löscht die Prio eines Projekts, schreibt sie und gibt die ganze Zuordnung zurück (die Seite stellt damit die Felder ALLER Zeilen nach)."""
        with cls._sperre:
            neu = cls.verteilen(cls.laden(), str(kennung), cls.normieren(wert))
            AtomarSchreiber.json_schreiben(cls.pfad(), dict(sorted(neu.items(), key=lambda e: (e[1], e[0]))))
        return neu
