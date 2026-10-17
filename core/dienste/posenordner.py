# -*- coding: utf-8 -*-
"""Posenordner — HumanBody-Posen verschieben und loeschen, Ordner anlegen, umbenennen, loeschen.

Edgar, 17.10.2026 (Reiter „Posen"): „Mach Funktionen zum Verschieben, Loeschen
der Poses in andere Ordner als Kontextmenue, so wie bei Animationen, Loeschen,
Umbenennen der Ordner auch."

WIE BEI DEN ANIMATIONEN (`Bvhordner`): Ein Ordner IST ein Verzeichnis unter
`HumanBody/data/poseData/`, eine Pose eine Datei `<Ordner>/<Name>.json`.
Verschieben und Umbenennen aendern die Platte, nicht einen Eintrag in einer
Liste. Ordner duerfen verschachtelt sein (`charmorph/glamour`) — die Kennung
einer Pose ist ihr Pfad ohne `.json` (`Posenlader.list_poses`).

GELOESCHT WIRD NICHT VON DER PLATTE: Pose und Ordner gehen nach
`poseData/.trash/<Pfad>` (die Liste laesst Ordner mit Punkt vorn aus).
`rest_poses/` und `charmorph/` kommen aus CharMorph und MB-Lab — ein Fehlgriff
im Menue soll zurueckholbar sein. Geleert wird `.trash` von Hand.

FEST: `rest_poses/t-pose` nennt der Code mit Namen (Hauptmenue „T-Pose",
`menubar.js`; Startpose, `starteinstellungen.js`), der Ordner `rest_poses`
damit auch. Verschoben, umbenannt oder geloescht ginge das Menue ins Leere.

Die Daz-Posen (Genesis 9) verwaltet `G9poseneinteilung` — die Daz-Bibliothek
wird nie beschrieben (`G9pfade`).
"""

import logging
import shutil
from pathlib import Path

from .posenablage import Posenablage, PosenFehler

logger = logging.getLogger('core')

__all__ = ['Posenordner']


class Posenordner:
    """Datei- und Ordneraktionen unter `poseData/`. Wirft `PosenFehler`."""

    PAPIERKORB = '.trash'
    #: Kennungen, die der Code fest nennt — nicht verschiebbar, nicht loeschbar.
    FESTE_POSEN = frozenset({'rest_poses/t-pose'})
    #: Ordner, in denen eine feste Pose liegt — nicht umbenennbar, nicht loeschbar.
    FESTE_ORDNER = frozenset(p.rsplit('/', 1)[0] for p in FESTE_POSEN)

    # ------------------------------------------------------------ Pruefen

    @classmethod
    def name_pruefen(cls, name):
        """Ein Ordnername (EIN Pfadteil) — dieselben Zeichen wie ein Posenname."""
        name = str(name or '').strip()
        if not name or len(name) > Posenablage.NAME_MAX:
            raise PosenFehler(f'Der Name fehlt oder ist zu lang (höchstens {Posenablage.NAME_MAX} Zeichen).')
        if not Posenablage.NAME_MUSTER.match(name) or name.endswith(('.', ' ')):
            raise PosenFehler('Im Namen sind nur Buchstaben, Ziffern, Leerzeichen und _ . ( ) + - erlaubt.')
        if name.lower() in Posenablage.GERAETE:
            raise PosenFehler(f'„{name}" ist als Name nicht möglich.')
        return name

    @classmethod
    def _pfad(cls, wurzel, relativ, endung=''):
        """`wurzel/relativ+endung`, aufgeloest — aus der Wurzel oder in den Papierkorb geht nicht."""
        relativ = str(relativ or '').strip().strip('/')
        teile = [t for t in relativ.split('/') if t]
        if any(t.startswith('.') or '\\' in t for t in teile):
            raise PosenFehler(f'Ungültiger Pfad: {relativ}')
        basis = Path(wurzel).resolve()
        ziel = (basis.joinpath(*teile) if teile else basis)
        if endung:
            ziel = ziel.with_name(ziel.name + endung)
        ziel = ziel.resolve()
        if not ziel.is_relative_to(basis):
            raise PosenFehler(f'Ungültiger Pfad: {relativ}')
        return ziel

    @classmethod
    def _ordner(cls, wurzel, pfad):
        """Ein vorhandener Ordner (nicht die Wurzel selbst)."""
        ordner = cls._pfad(wurzel, pfad)
        if ordner == Path(wurzel).resolve() or not ordner.is_dir():
            raise PosenFehler(f'Ordner „{pfad}" gibt es nicht.', 404)
        return ordner

    @classmethod
    def _pose(cls, wurzel, pose_id):
        datei = cls._pfad(wurzel, pose_id, '.json')
        if not datei.is_file():
            raise PosenFehler(f'Pose „{pose_id}" gibt es nicht.', 404)
        return datei

    @classmethod
    def _fest(cls, pose_id=None, ordner=None):
        if pose_id in cls.FESTE_POSEN:
            raise PosenFehler(f'„{pose_id}" nennt das Hauptmenü (T-Pose) mit Namen — '
                              'sie bleibt, wo sie ist.', 409)
        if ordner is not None:
            ordner = ordner.strip('/')
            if any(f == ordner or f.startswith(ordner + '/') for f in cls.FESTE_ORDNER):
                raise PosenFehler(f'Im Ordner „{ordner}" liegt die T-Pose des Hauptmenüs — '
                                  'er bleibt, wie er ist.', 409)

    # -------------------------------------------------------------- Posen

    @classmethod
    def verschieben(cls, wurzel, pose_id, ziel_ordner):
        """Eine Pose in einen anderen (auch neuen) Ordner. → `{ok, id}`."""
        cls._fest(pose_id=pose_id)
        datei = cls._pose(wurzel, pose_id)
        ziel_ordner = '/'.join(cls.name_pruefen(t) for t in str(ziel_ordner or '').split('/') if t.strip())
        if not ziel_ordner:
            raise PosenFehler('Kein Zielordner angegeben.')
        ordner = cls._pfad(wurzel, ziel_ordner)
        ziel = ordner / datei.name
        if ziel.exists():
            raise PosenFehler(f'In „{ziel_ordner}" gibt es „{datei.stem}" schon.', 409)
        ordner.mkdir(parents=True, exist_ok=True)
        datei.rename(ziel)
        logger.info('[posenbaum] Pose verschoben: %s -> %s', datei, ziel)
        return {'ok': True, 'id': f'{ziel_ordner}/{datei.stem}'}

    @classmethod
    def loeschen(cls, wurzel, pose_id):
        """Eine Pose in den Papierkorb. → `{ok, papierkorb}`."""
        cls._fest(pose_id=pose_id)
        datei = cls._pose(wurzel, pose_id)
        ziel = cls._entsorgen(wurzel, datei)
        return {'ok': True, 'papierkorb': ziel}

    # ------------------------------------------------------------- Ordner

    @classmethod
    def ordner_anlegen(cls, wurzel, eltern, name):
        """`eltern/name` anlegen (`eltern` leer = oberste Ebene). → `{ok, pfad}`."""
        name = cls.name_pruefen(name)
        pfad = f'{eltern.strip("/")}/{name}' if str(eltern or '').strip('/') else name
        ordner = cls._pfad(wurzel, pfad)
        if ordner.exists():
            raise PosenFehler(f'Ordner „{pfad}" gibt es schon.', 409)
        ordner.mkdir(parents=True)
        logger.info('[posenbaum] Ordner angelegt: %s', ordner)
        return {'ok': True, 'pfad': pfad}

    @classmethod
    def ordner_umbenennen(cls, wurzel, pfad, neu):
        """Den letzten Pfadteil umbenennen — der Ordner bleibt unter seinem Elternordner. → `{ok, pfad}`."""
        cls._fest(ordner=pfad)
        alt = cls._ordner(wurzel, pfad)
        neu = cls.name_pruefen(neu)
        ziel = alt.with_name(neu)
        # `samefile`: nur Gross-/Kleinschreibung geaendert — unter Windows „existiert" das Ziel dann schon.
        if ziel.exists() and not ziel.samefile(alt):
            raise PosenFehler(f'Ordner „{neu}" gibt es dort schon.', 409)
        try:
            alt.rename(ziel)
        except OSError as fehler:
            raise PosenFehler(f'Ordner nicht umbenannt: {fehler}', 409) from fehler
        logger.info('[posenbaum] Ordner umbenannt: %s -> %s', alt, ziel)
        eltern = pfad.strip('/').rpartition('/')[0]
        return {'ok': True, 'pfad': f'{eltern}/{neu}' if eltern else neu}

    @classmethod
    def ordner_loeschen(cls, wurzel, pfad):
        """Leer: entfernen. Mit Inhalt: in den Papierkorb. → `{ok, posen, papierkorb}`."""
        cls._fest(ordner=pfad)
        ordner = cls._ordner(wurzel, pfad)
        posen = sum(1 for _ in ordner.rglob('*.json'))
        if not any(ordner.iterdir()):
            ordner.rmdir()
            logger.info('[posenbaum] Leeren Ordner entfernt: %s', ordner)
            return {'ok': True, 'posen': 0, 'papierkorb': None}
        ziel = cls._entsorgen(wurzel, ordner)
        return {'ok': True, 'posen': posen, 'papierkorb': ziel}

    # ---------------------------------------------------------- Papierkorb

    @classmethod
    def _entsorgen(cls, wurzel, quelle):
        """`quelle` nach `.trash/<Pfad>`; steht dort schon etwas, mit `_2`, `_3` … → Pfad unter der Wurzel."""
        basis = Path(wurzel).resolve()
        relativ = quelle.relative_to(basis)
        ziel = basis / cls.PAPIERKORB / relativ
        ziel.parent.mkdir(parents=True, exist_ok=True)
        datei = quelle.is_file()
        stamm, endung, zaehler = (ziel.stem if datei else ziel.name), (ziel.suffix if datei else ''), 2
        while ziel.exists():
            ziel, zaehler = ziel.with_name(f'{stamm}_{zaehler}{endung}'), zaehler + 1
        try:
            shutil.move(str(quelle), str(ziel))
        except OSError as fehler:
            raise PosenFehler(f'Nicht gelöscht: {fehler}', 409) from fehler
        logger.info('[posenbaum] In den Papierkorb: %s -> %s', quelle, ziel)
        return ziel.relative_to(basis).as_posix()
