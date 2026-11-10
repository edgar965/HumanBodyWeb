# -*- coding: utf-8 -*-
"""Fotogenesisgeschlecht — mit welcher Genesis-Grundfigur ein Foto-Genesis-Test rechnet (04.11.2026, Edgar: „Auswahl ob Genesis Männlich, weiblich oder Kind“).

Der Job erkennt das Geschlecht nicht selbst: Es steht von Hand in `3DObjects/fotogenesis/<Name>/job.json` als `geschlecht`. Gelesen wird es von der Foto-Kette (`KoerperKI_Fotos.Fotojob`) und von PSHuman
(`pshuman_job_rechnen.py`); die Mesh-Genesis-Kette liest `einstellung.json` ihres Tests (`Meshgenesistest.geschlecht_setzen`). Darum schreibt `setzen` beide Stellen, sonst bliebe die Wahl dort ohne Wirkung.

„Kind“ steht nicht in der Wahl: Die Kette hat nur diese zwei Grundfiguren (`meshgenesis_formfigur.GRUND`), und eine Körper-Einpassung nach dem Foto eines echten Kindes baut Claude nicht (Edgar bekannt).

    POST /api/fotogenesis/<job>/geschlecht/   {geschlecht: 'maennlich' | 'weiblich'}   → {ok, geschlecht}
"""

import json
import logging

from core.atomic_write import AtomarSchreiber

from .meshgenesistest import Meshgenesistest

logger = logging.getLogger('core')

__all__ = ['Fotogenesisgeschlecht']


class Fotogenesisgeschlecht:
    FELD = 'geschlecht'
    WAHL = (('maennlich', 'männlich'), ('weiblich', 'weiblich'))

    @classmethod
    def lesen(cls, info):
        """Der Wert aus einer gelesenen job.json, `None` ohne (gültige) Angabe."""
        wert = info.get(cls.FELD)
        return wert if wert in dict(cls.WAHL) else None

    @classmethod
    def setzen(cls, job, wert):
        """Schreibt die Wahl in die job.json (mischend) und in den Mesh-Genesis-Test des Jobs. Gibt den Wert zurück; `ValueError` bei Export oder falschem Wert."""
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine Geschlechtswahl — die Figur eines Exports ist bekannt')
        if wert not in dict(cls.WAHL):
            raise ValueError('geschlecht %r: erlaubt %s' % (wert, ', '.join(dict(cls.WAHL))))
        datei = job['ordner'] / 'job.json'
        info = json.loads(datei.read_text(encoding='utf-8'))
        info[cls.FELD] = wert
        AtomarSchreiber.json_schreiben(datei, info, einzug=1)
        if job.get('test') and not Meshgenesistest.geschlecht_setzen(job['test'], wert):
            logger.warning('Fotogenesisgeschlecht: Mesh-Genesis-Test %s nicht gefunden — nur die job.json trägt %s', job['test'], wert)
        logger.info('Fotogenesisgeschlecht: %s → %s', datei, wert)
        return wert
