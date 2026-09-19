# -*- coding: utf-8 -*-
"""Bildmodellpersonkatalog — Listen für die Personenkarte: Daz-Haare und Proportionen.

Ausgelagert aus `Bildmodellkatalog` (der stand bei 319 Zeilen): das Haar-
Feld des Personenformulars (Edgar, 19.09.2026: „Alter, Größe, Gewicht,
Tonus, Haar") und die 18 Maße des Proportionen-Popups (`G9proportionen`).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Bildmodellpersonkatalog']


class Bildmodellpersonkatalog:
    """Haare der Garderobe (einmal gelesen) und der Maßkatalog."""

    _haare = None

    @classmethod
    def proportionen(cls):
        """Die 18 Maße (`G9proportionen.MASSE`) mit Name, Ansicht, formbar."""
        from Genesis9.proportionen import G9proportionen

        return G9proportionen.katalog()

    @classmethod
    def haare(cls):
        """Die Daz-Haare der Garderobe (`[{id, name}]`) für das Personenfeld „Haar"."""
        if cls._haare is None:
            try:
                from Genesis9.garderobe import G9garderobe

                gesehen = set()
                aus = []
                for e in G9garderobe.liste():
                    if e.get('art') != 'haar' or not e.get('zeigbar') or e.get('id') in gesehen:
                        continue
                    gesehen.add(e['id'])
                    aus.append({'id': e['id'], 'name': e.get('name') or e['id']})
                cls._haare = sorted(aus, key=lambda h: h['name'].lower())
            except Exception as fehler:  # noqa: BLE001
                logger.warning('Haare der Garderobe nicht lesbar: %s', fehler)
                cls._haare = []
        return cls._haare

    @classmethod
    def vergessen(cls):
        cls._haare = None
