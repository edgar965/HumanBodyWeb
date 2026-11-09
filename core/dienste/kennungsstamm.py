# -*- coding: utf-8 -*-
"""Kennungsstamm — aus einem Namen wird der Teil einer Adresse: klein, Umlaute ausgeschrieben, alles andere `_`.

    Kennungsstamm.aus_name('Session3dTools', 96)   -> 'session3dtools'
    Kennungsstamm.aus_name('Königin 1 (neu)', 96)  -> 'koenigin_1_neu'
    Kennungsstamm.aus_name('...', 96)              -> ''
"""
import re

__all__ = ['Kennungsstamm']


class Kennungsstamm:
    ERSETZEN = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'}

    @classmethod
    def aus_name(cls, name, laenge):
        """Der Stamm, höchstens `laenge` Zeichen; '' , wenn vom Namen nichts übrig bleibt."""
        text = str(name or '').lower()
        for alt, neu in cls.ERSETZEN.items():
            text = text.replace(alt, neu)
        return re.sub(r'[^a-z0-9]+', '_', text).strip('_')[:laenge].rstrip('_')
