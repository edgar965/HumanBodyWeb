# -*- coding: utf-8 -*-
"""Garmentanfrage — was der Browser fuer Schnitt, Masse und Drapierung mitschickt.

Herausgeloest aus `api/garmentcode.py` (19.09.2026), als `figurart` und
`regler_figur` dazukamen (Edgar: „garment Code Assets funktioniert nicht auf
Genesis") und die Datei ueber 300 Zeilen ging. Drei Leser (`garmentcode`,
`garmentgemeinsam`, `garmentabsatzvorschau`), eine Form.

Die Felder:

    vorlage, geschlecht, bauart, morphs, meta   die HumanBody-Figur (Morphs als
                                                JSON — es sind Dutzende)
    regler                                      die GarmentCode-Regler des Schnitts
    koerper, smpl                               ein SMPL-Referenzkoerper von
                                                GarmentCode statt der Figur (06.09.)
    figurart, regler_figur                      eine Genesis-9-Figur schickt statt
                                                Bauart und Morphs ihre Daz-Regler
                                                (`genesis9drapierung.py`)
"""

import json
import logging
from collections import namedtuple

logger = logging.getLogger(__name__)

Felder = namedtuple(
    'Felder', 'vorlage geschlecht bauart morphs regler meta koerper smpl figurart regler_figur'
)


class Garmentanfrage(Felder):
    """Die Formulardaten einer GarmentCode-Anfrage, gelesen und geprueft."""

    #: Figurarten mit eigenem Koerperweg neben HumanBody und SMPL (19.09.2026).
    FIGURARTEN = ('genesis9',)

    @classmethod
    def lesen(cls, request):
        """Geschlecht, Bauart, Morphs — und Figurart samt Reglern — aus dem Rumpf."""
        from ..dienste.smplfigur import Smplfiguren

        felder = request.POST
        koerper = felder.get('koerper') or None
        figurart = felder.get('figurart') or None
        return cls(
            vorlage=felder.get('vorlage', 't-shirt'),
            geschlecht=felder.get('geschlecht', 'female'),
            bauart=felder.get('bauart') or None,
            morphs=cls.woerterbuch(felder, 'morphs', 'Morphs unlesbar, nehme Grundkoerper'),
            regler=cls.woerterbuch(felder, 'regler', 'Reglerwerte unlesbar, nehme Vorgabe'),
            meta=cls.woerterbuch(felder, 'meta', 'Metaregler unlesbar, nehme keine'),
            koerper=koerper,
            smpl=bool(koerper) and Smplfiguren.ist_smpl(koerper),
            figurart=figurart if figurart in cls.FIGURARTEN else None,
            regler_figur=cls.woerterbuch(felder, 'regler_figur', 'Figurregler unlesbar, nehme Basis'),
        )

    @staticmethod
    def woerterbuch(felder, name, warnung):
        """Ein JSON-Feld des Formulars als dict; unlesbar oder keins -> leer, mit Warnung."""
        try:
            wert = json.loads(felder.get(name) or '{}')
        except ValueError:
            logger.warning('GarmentCode: %s', warnung)
            return {}
        return wert if isinstance(wert, dict) else {}
