# -*- coding: utf-8 -*-
"""Posenbaum — die Posen ALLER Modelle als Ordnerbaum fuer den Reiter „Posen" (17.10.2026).

Edgar, 17.10.2026: „mache alle vorhandenen Poses aus allen Modellen in Ordner bei
Poses (auch valkyrie, HumanBody usw). Mache Ordner damit sie struktuiert sind."

ZWEI BESTAENDE, EIN BAUM
========================
- `humanbody`: die JSON-Posen unter `HumanBody/data/poseData/` (rest_poses,
  CharMorph/MB-Lab, eigene). Ein Ordner ist ein Verzeichnis (`Posenordner`),
  angewendet wird im Browser auf das Rig (`Posenanwendung`).
- `genesis9`: die Daz-Posen und -Ausdruecke von `G9posen` (Base Poses, Daily
  Ease, Kin, Space Valkyrie, G9 Anime …). Ein Ordner kommt aus der Einteilung
  neben der Bibliothek (`G9poseneinteilung`), angewendet wird auf dem Server
  (`Genesis9Modell.poseSetzen` backt die Pose ins Netz).

Gibt es eine Pose fuer das andere Modell nicht, sagt das der Browser beim
Anklicken (`Posenwahl`) — die Formate sind nicht austauschbar (Quaternionen je
Rigify-Knochen gegen Daz-Winkel und Regler).

Ein Knoten: `{name, pfad, ordner: [Knoten], posen: [{id, name, art?}]}`;
`pfad` ist der Ordner mit `/` innerhalb seines Bestands.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Posenbaum']


class Posenbaum:
    """`baum(wurzel)` -> `{bestaende: [...]}`."""

    @classmethod
    def baum(cls, wurzel_humanbody):
        bestaende = [cls.humanbody(wurzel_humanbody)]
        genesis9 = cls.genesis9()
        if genesis9 is not None:
            bestaende.append(genesis9)
        return {'bestaende': bestaende}

    # ---------------------------------------------------------- HumanBody

    @classmethod
    def humanbody(cls, wurzel):
        from humanbody_core.pose.posenlader import Posenlader

        from .posenordner import Posenordner

        ordner = [pfad for pfad, _ in Posenlader._find_pose_dirs(wurzel)]
        posen = [(kategorie, {'id': p['id'], 'name': p['name']})
                 for kategorie, liste in Posenlader.list_poses(wurzel).items() for p in liste]
        return {
            'kennung': 'humanbody',
            'titel': 'HumanBody',
            'quelle': 'modell',
            'hinweis': 'Ordner unter HumanBody/data/poseData/ — Gelöschtes liegt in .trash/.',
            'feste_posen': sorted(Posenordner.FESTE_POSEN),
            'feste_ordner': sorted(Posenordner.FESTE_ORDNER),
            'umbenennbar': True,
            'baum': cls.knoten(ordner, posen),
        }

    # ---------------------------------------------------------- Genesis 9

    @classmethod
    def genesis9(cls):
        """Der Daz-Bestand — `None` ohne Bibliothek oder wenn der Katalog nicht lesbar ist."""
        try:
            from Genesis9.pfade import G9pfade
            from Genesis9.posen import G9posen
            from Genesis9.poseneinteilung import G9poseneinteilung

            if not G9pfade.vorhanden():
                return None
            stand = G9poseneinteilung.laden()
            eintraege = G9poseneinteilung.eintraege(G9posen.katalog(), stand)
        except Exception:  # noqa: BLE001 — der HumanBody-Teil soll trotzdem kommen
            logger.exception('[posenbaum] Genesis-9-Posen nicht lesbar')
            return None
        posen = [(ordner, {'id': e['id'], 'name': e['name'], 'art': e['art']}) for ordner, e in eintraege]
        return {
            'kennung': 'genesis9',
            'titel': 'Genesis 9 (Daz)',
            'quelle': 'genesis9',
            'hinweis': 'Die Daz-Bibliothek bleibt unverändert: Ordner und Löschen stehen in '
                       '3DObjects/models/Genesis9/posen_einteilung.json.',
            'feste_posen': [],
            'feste_ordner': [],
            'umbenennbar': False,
            'baum': cls.knoten(stand['ordner'], posen),
        }

    # ------------------------------------------------------------ Knoten

    @classmethod
    def knoten(cls, ordnerpfade, posen):
        """Aus Ordnerpfaden und `[(Ordnerpfad, Pose)]` den Baum bauen — Ordner vor Posen, nach Namen."""
        wurzel = {'name': '', 'pfad': '', 'ordner': {}, 'posen': []}
        for pfad in ordnerpfade:
            cls._stelle(wurzel, pfad)
        for pfad, pose in posen:
            cls._stelle(wurzel, pfad)['posen'].append(pose)
        return cls._fertig(wurzel)

    @staticmethod
    def _stelle(wurzel, pfad):
        """Der Knoten zu `pfad` — fehlende Ordner unterwegs werden angelegt."""
        stelle = wurzel
        teile = [t for t in str(pfad).split('/') if t]
        for i, teil in enumerate(teile):
            stelle = stelle['ordner'].setdefault(
                teil, {'name': teil, 'pfad': '/'.join(teile[:i + 1]), 'ordner': {}, 'posen': []})
        return stelle

    @classmethod
    def _fertig(cls, stelle):
        unter = sorted(stelle['ordner'].items(), key=lambda x: x[0].lower())
        return {'name': stelle['name'], 'pfad': stelle['pfad'],
                'ordner': [cls._fertig(k) for _, k in unter],
                'posen': sorted(stelle['posen'], key=lambda p: p['name'].lower())}
