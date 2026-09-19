# -*- coding: utf-8 -*-
"""Bildmodellpersonkatalog — Listen für die Personenkarte: Daz-Haare und Proportionen.

Ausgelagert aus `Bildmodellkatalog` (der stand bei 319 Zeilen): das Haar-
Feld des Personenformulars (Edgar, 19.09.2026: „Alter, Größe, Gewicht,
Tonus, Haar"), die 19 Maße des Proportionen-Popups (`G9proportionen`) und
die Referenzfiguren eines Testfalls (Bibliothekseinträge des Genesis-9-Katalogs).
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Bildmodellpersonkatalog']


class Bildmodellpersonkatalog:
    """Haare der Garderobe (einmal gelesen) und der Maßkatalog."""

    _haare = None
    _testfiguren = None

    @classmethod
    def proportionen(cls):
        """Die 19 Maße (`G9proportionen.MASSE`) mit Name, Ansicht, formbar."""
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
    def testfiguren(cls):
        """Die Figuren der Daz-Bibliothek (`G9charaktere.liste`) als `[{name, anzeige}]` —
        die Referenz eines Testfalls (Edgar, 19.09.2026: „Testcase … Ursula9")."""
        if cls._testfiguren is None:
            try:
                from Genesis9.charaktere import G9charaktere

                cls._testfiguren = [
                    {'name': e['name'], 'anzeige': e.get('anzeige') or e['name']}
                    for e in G9charaktere.liste()
                ]
            except Exception as fehler:  # noqa: BLE001
                logger.warning('Genesis-9-Figuren nicht lesbar: %s', fehler)
                cls._testfiguren = []
        return cls._testfiguren

    @classmethod
    def vergessen(cls):
        cls._haare = None
        cls._testfiguren = None
