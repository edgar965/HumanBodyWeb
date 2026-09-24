# -*- coding: utf-8 -*-
"""Modellkatalog — was der Dialog „Charakter hinzufügen" je Reiter anbietet.

ZWEI BEREICHE (Edgar, 17.09.2026: „bei Modell hinzufügen mach zwei
zugeklappte Bereiche - die Standard Modelle (also z.B. die vorgefertigten
Genesis9 aus der Bibliothek, oder die Male, Human usw. aus HumanBody),
zweiter bereich - die gespeicherten Modelle (also alle HumanBody von der
Platte, UMA von der Platte, und die Genesis9 die ich gespeichert habe). Das
programm soll die Genesis9 gespeicherten NUR bei den Genesis9 hinzufügen"):

* STANDARD — was das Programm mitbringt: bei HumanBody die 13 Körpertypen
  von MB-Lab (`MorphData.BODY_TYPES`: Female_Caucasian … Male_Latin), bei
  Genesis 9 der Katalog der Daz-Bibliothek, bei SMPL-X, MakeHuman und UMA
  Python ihre Kataloge.
* GESPEICHERT — was auf der Platte liegt: die Modelldateien unter
  `data/models/` (`.json`, keine `.scene.json`), je nach ihrer `quelle`
  (fehlt sie: HumanBody); die UMA-Figuren aus `Figuren/uma/`.

Bis dahin stand JEDE Modelldatei im HumanBody-Reiter — auch ein
gespeichertes Genesis-9-Modell (`body_type: "Genesis 9"`, leere Morphs),
das beim Laden als HumanBody-Figur scheiterte. Seit demselben Abend
schreibt „Modell speichern" für Figuren mit `quelle` (Genesis 9, UMA,
MakeHuman, SMPL-X, UMA Python) `{name, quelle, figur: toJSON()}`
(`Szenenausgabe.modelldaten`), und `quelle` entscheidet den Reiter.

Ein Körpertyp ist keine Datei: `/api/character/model/<Körpertyp>/` liefert
ihn als Modellvorgabe ohne Morphs (`koerpertyp`), damit jeder Lader
(Szene, Studio, Theatre) ihn wie ein gespeichertes Modell holen kann.
"""

import json
import logging
import os

from django.conf import settings
from humanbody_core.morphing.morphdata import MorphData

logger = logging.getLogger('core')

__all__ = ['Modellkatalog']


class Modellkatalog:
    """Körpertypen, gespeicherte Modelle und ihre `quelle`."""

    SZENE = '.scene.json'
    #: Modelldateien ohne `quelle` sind HumanBody.
    VORGABE_QUELLE = 'modell'

    @staticmethod
    def ordner():
        return str(settings.HUMANBODY_MODELS_DIR)

    # ------------------------------------------------------------ Standard

    @staticmethod
    def koerpertypen():
        """Die Standardfiguren von HumanBody, wie MB-Lab sie nennt."""
        return [
            {
                'name': name,
                'anzeige': name.replace('_', ' '),
                'geschlecht': ('weiblich' if name.startswith('Female') else 'männlich'),
            }
            for name in MorphData.BODY_TYPES
        ]

    @classmethod
    def koerpertyp(cls, name):
        """Die Modellvorgabe eines Körpertyps (ohne Morphs) — oder None."""
        if name not in MorphData.BODY_TYPES:
            return None
        return {
            'name': name,
            'body_type': name,
            'morphs': {},
            'meta': {},
            'cloth': [],
            'hair_style': None,
            'garments': [],
            'mh_proxy': [],
            'garmentcode': [],
            'koerpertyp': True,
        }

    # ---------------------------------------------------------- Gespeichert

    @classmethod
    def gespeicherte(cls):
        """`[{name, label, quelle}]` aller Modelldateien, nach Namen."""
        ordner = cls.ordner()
        aus = []
        if not os.path.isdir(ordner):
            return aus
        for dateiname in sorted(os.listdir(ordner)):
            if not dateiname.endswith('.json') or dateiname.endswith(cls.SZENE):
                continue
            name = dateiname[:-5]
            daten = cls._lesen(os.path.join(ordner, dateiname))
            if cls._koerperart_unbrauchbar(daten):
                continue
            aus.append({'name': name, 'label': name, 'quelle': cls.quelle(daten)})
        return aus

    @classmethod
    def _koerperart_unbrauchbar(cls, daten):
        u"""True für eine HumanBody-Datei mit einer Körperart, die weder ein
        echter MB-Lab-Typ noch ein erzeugtes Modell (Rig-Baukasten,
        `type: "generated_model"`) ist.

        FUND (24.09.2026, Studio-Assettest „lade alle Assets"): zwei
        Modelldateien (`FrauBasic.json`, `Rig4.json`) tragen
        `body_type: "Rig Bones"` — den Marker, den der Rig-Baukasten für
        seine erzeugten Modelle setzt (`scene/modellgenerator/speicher.js`,
        `Modellspeicher._daten`) — OHNE dessen `type: "generated_model"` und
        ohne `bone_parts`. Ohne die Kennung nimmt `HumanbodyModell` sie als
        normale Figur und schickt „Rig Bones" als `body_type` an
        `/api/character/mesh/` — dort kennt `CharacterState.set_body_type`
        nur die 13 MB-Lab-Typen, `compute()` liefert `None`, die Antwort ist
        ein 500. Die anderen erzeugten Modelle (`Rig`, `Rig1`–`Rig3`, `Rig5`,
        `TriadischRock`) tragen `type: "generated_model"` korrekt und bauen
        über `Erzeugtesmodell` — die bleiben im Katalog stehen, nur die zwei
        unvollständigen Speicherstände werden ausgeblendet. Die Dateien
        selbst bleiben unangetastet (`HumanBody/data/` ist nur-lesen).
        """
        if not isinstance(daten, dict):
            return False
        if cls.quelle(daten) != cls.VORGABE_QUELLE:
            return False   # Genesis 9 & Co. pruefen ihre Koerperart selbst.
        if daten.get('type') == 'generated_model':
            return False   # Rig-Baukasten-Modell, geht ueber Erzeugtesmodell.
        return daten.get('body_type') not in MorphData.BODY_TYPES

    @classmethod
    def gespeichert(cls, name, quelle):
        """Die Figurdaten (`figur`) eines gespeicherten Modells DIESER
        Quelle — oder None, wenn es die Datei nicht gibt oder sie einer
        anderen Figurart gehört."""
        if not name or '/' in name or '\\' in name or '..' in name:
            return None
        pfad = os.path.join(cls.ordner(), name + '.json')
        if not os.path.isfile(pfad):
            return None
        daten = cls._lesen(pfad)
        if daten is None or cls.quelle(daten) != quelle:
            return None
        figur = daten.get('figur')
        # Eine Datei vom Vormittag des 17.09.2026 (`body_type: "Genesis 9"`,
        # ohne `figur`) ist die Grundfigur ohne Regler.
        return figur if isinstance(figur, dict) else {}

    @classmethod
    def quelle(cls, daten):
        """Die Figurart einer Modelldatei; ohne Angabe HumanBody."""
        if not isinstance(daten, dict):
            return cls.VORGABE_QUELLE
        quelle = daten.get('quelle')
        if quelle:
            return str(quelle)
        # Vor dem Abend des 17.09.2026 schrieb „Modell speichern" eine Genesis-
        # 9-Figur als HumanBody-Datei mit `body_type: "Genesis 9"`.
        if daten.get('body_type') == 'Genesis 9':
            return 'genesis9'
        return cls.VORGABE_QUELLE

    @staticmethod
    def _lesen(pfad):
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except OSError, json.JSONDecodeError:
            logger.warning('%s nicht lesbar', pfad, exc_info=True)
            return None
