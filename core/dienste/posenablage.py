# -*- coding: utf-8 -*-
"""Posenablage — die Stellung einer Figur als neue Pose unter `poseData/eigene/` ablegen.

Edgar, 17.10.2026: „alle anderen Vorschläge auch" — dazu gehört „Aktuelle Pose
speichern", der Knopf im Reiter „Posen", der die Stellung der Figur als neue
Pose ablegt.

WAS EINE POSE-DATEI IST
=======================
Je Steuerknochen (CharMorph/MB-Lab-Namen, `thigh_L`) ein Quaternion
`[w, x, y, z]`. Beim Laden macht `PoseData` daraus drei Schritte:

    1. Steuerknochen -> DEF-Knochen        `CONTROL_TO_DEF`
    2. Umbasierung ueber eine 4x4-Matrix   `BONE_TRANSFORM[steuerknochen] @ q`
    3. Blender -> Three.js                 `[w, x, y, z] -> [x, z, -y, w]`

Der Betrachter schickt hier die Drehungen als Three.js-Quaternionen je
DEF-Knochen (Abweichung von der Ruhelage, wie sie `Posenanwendung.anwenden`
auf die Knochen multipliziert; die Namen so, wie Three.js sie fuehrt:
`DEF-thigh_L`). Dieses Modul geht die drei Schritte RUECKWAERTS. Alle
Matrizen sind Drehungen oder Spiegelungen, also umkehrbar.

BELEGT (17.10.2026, `ProjektTemp/_wegwerf/pose_rundreise.py`): Alle 40 Posen
unter `poseData/` vorwaerts geladen, rueckwaerts geschrieben und wieder
geladen - 1.856 bewegte Knochen, groesste Abweichung der Drehung 1e-7. Mit
absichtlich vertauschten Achsen (`pose_rundreise_sabotage.py`) werden 1.386
davon rot.

WAS DABEI VERLOREN GEHT, und es wird gemeldet (`uebersprungen`): DEF-Knochen
ohne Steuerknochen (z. B. `DEF-spine.005`, das Gesicht). Die Namenstabelle
kennt sie nicht, eine geladene Pose koennte sie nie wieder setzen.
`root` und `pelvis` zeigen beide auf `DEF-spine`; beim Laden gewinnt `pelvis`,
geschrieben wird deshalb nur `pelvis`.

Geschrieben wird NUR nach `eigene/`. `rest_poses/` und `charmorph/` kommen aus
CharMorph und MB-Lab (Produktionsdaten) und werden hier nie angefasst.
"""

import logging
import math
import re
from pathlib import Path

import numpy as np

from ..atomic_write import AtomarSchreiber
from .dienstfehler import DienstFehler

logger = logging.getLogger('core')

__all__ = ['Posenablage', 'PosenFehler']


class PosenFehler(DienstFehler):
    """Ablehnung beim Speichern einer Pose. Rumpf und Kennzahl siehe `DienstFehler`."""


class Posenablage:
    """Eine Pose aus Three.js-Drehungen in eine Pose-Datei umrechnen und ablegen."""

    #: Ordner unter `poseData/`, in den eigene Posen kommen.
    KATEGORIE = 'eigene'
    #: Laenge eines Namens — der Dateiname bleibt auf jedem Laufwerk gueltig.
    NAME_MAX = 64
    #: Ein Name: Buchstaben, Ziffern, Leerzeichen und `_ . ( ) + -` — nichts, was ein Pfad ist.
    NAME_MUSTER = re.compile(r'^\w[\w .()+\-]*$')
    #: Windows-Geraetenamen — unter Windows kein gueltiger Dateiname.
    GERAETE = {
        'con', 'prn', 'aux', 'nul',
        *(f'com{i}' for i in range(1, 10)),
        *(f'lpt{i}' for i in range(1, 10)),
    }
    #: Name der Pose ohne Datei (A-Pose) — darf keine Datei verdecken.
    RESERVIERT = {'ruhelage'}
    #: So viele Knochen hat die ganze Namenstabelle (Obergrenze fuer die Anfrage).
    KNOCHEN_MAX = 200
    #: Unter dieser Abweichung gilt ein Knochen als nicht bewegt — nur Rechenrauschen
    #: (im Betrachter ~1e-9). NICHT 0.001 wie `PoseData.non_identity_bones`: Das waeren
    #: bis ~0,11 Grad je Knochen, die beim Speichern still verloren gingen.
    SCHWELLE = 1e-6

    # ------------------------------------------------------------- Ablegen

    @classmethod
    def speichern(cls, wurzel, name, drehungen):
        """Die Pose `name` aus `drehungen` ({DEF-Name: [x, y, z, w]}) ablegen.

        Liefert `{id, name, knochen, uebersprungen}`. Wirft `PosenFehler`:
        400 fuer eine falsche Anfrage, 409 wenn es den Namen schon gibt.
        """
        name = cls.name_pruefen(name)
        steuer, uebersprungen = cls.steuerknochen(drehungen)
        if not steuer:
            raise PosenFehler('Die Figur steht in der Ruhelage - nichts zu speichern.')
        ziel = cls._ziel(wurzel, name)
        if ziel.exists():
            raise PosenFehler(f'Die Pose „{name}" gibt es schon.', 409)
        AtomarSchreiber.json_schreiben(ziel, steuer)
        logger.info('[pose-manage] Saved: %s (%d Knochen, %d uebersprungen)',
                    ziel, len(steuer), len(uebersprungen))
        return {
            'id': f'{cls.KATEGORIE}/{name}',
            'name': name,
            'category': cls.KATEGORIE,
            'knochen': len(steuer),
            'uebersprungen': uebersprungen,
        }

    @classmethod
    def name_pruefen(cls, name):
        """Der bereinigte Name — oder `PosenFehler`."""
        name = str(name or '').strip()
        if not name:
            raise PosenFehler('Bitte einen Namen für die Pose eingeben.')
        if len(name) > cls.NAME_MAX:
            raise PosenFehler(f'Der Name ist zu lang (höchstens {cls.NAME_MAX} Zeichen).')
        if not cls.NAME_MUSTER.match(name) or name.endswith(('.', ' ')):
            raise PosenFehler('Im Namen sind nur Buchstaben, Ziffern, Leerzeichen und _ . ( ) + - erlaubt.')
        if name.lower() in cls.GERAETE or name.lower() in cls.RESERVIERT:
            raise PosenFehler(f'„{name}" ist als Name nicht möglich.')
        return name

    @classmethod
    def _ziel(cls, wurzel, name):
        """Der Dateipfad unter `eigene/` — er darf die Wurzel nicht verlassen."""
        wurzel = Path(wurzel).resolve()
        ziel = (wurzel / cls.KATEGORIE / f'{name}.json').resolve()
        if not ziel.is_relative_to(wurzel):
            raise PosenFehler('Ungültiger Name.')
        return ziel

    # ----------------------------------------------------------- Umrechnen

    @classmethod
    def steuerknochen(cls, drehungen):
        """`({Steuerknochen: [w, x, y, z]}, [nicht abbildbare DEF-Knochen])`.

        Rueckwaerts durch dieselben drei Schritte, die `PoseData` vorwaerts geht.
        Unbewegte Knochen fehlen: Was in der Datei fehlt, bleibt beim Laden unveraendert.
        """
        from humanbody_core.pose.knochennamen import DEF_TO_CONTROL
        from humanbody_core.pose.matrizen import BONE_TRANSFORM

        if not isinstance(drehungen, dict) or len(drehungen) > cls.KNOCHEN_MAX:
            raise PosenFehler('Die Drehungen fehlen oder sind zu viele.')
        # Three.js liest einen Punkt im Knochennamen als Trenner, deshalb heissen die
        # Knochen im Betrachter `DEF-thigh_L` statt `DEF-thigh.L` (`Posenanwendung.jsName`).
        # Der Unterstrich ist NICHT umkehrbar (`DEF-upper_arm.L` hat einen echten) -
        # darum wird jeder Name der Tabelle in beiden Schreibweisen nachgeschlagen.
        js_zu_def = {name.replace('.', '_'): name for name in DEF_TO_CONTROL}
        steuer, uebersprungen = {}, []
        for roh_name, wert in drehungen.items():
            q = cls._blender(wert)
            if cls._unbewegt(q):
                continue
            def_name = roh_name if roh_name in DEF_TO_CONTROL else js_zu_def.get(roh_name)
            kontrolle = DEF_TO_CONTROL.get(def_name)
            if kontrolle is None:
                uebersprungen.append(roh_name)
                continue
            matrix = BONE_TRANSFORM.get(kontrolle)
            if matrix is not None:
                q = list(np.linalg.inv(matrix) @ np.array(q, dtype=float))
            steuer[kontrolle] = [round(float(x), 8) for x in q]
        return steuer, sorted(uebersprungen)

    @classmethod
    def _blender(cls, wert):
        """Three.js `[x, y, z, w]` -> Blender `[w, x, y, z]`, normiert, `w >= 0`.

        Umkehrung von `[w, x, y, z] -> [x, z, -y, w]`: `x = tx`, `y = -tz`, `z = ty`.
        """
        if not isinstance(wert, (list, tuple)) or len(wert) != 4:
            raise PosenFehler('Eine Drehung hat nicht vier Zahlen.')
        try:
            tx, ty, tz, tw = (float(v) for v in wert)
        except (TypeError, ValueError):
            raise PosenFehler('Eine Drehung enthält keine Zahlen.') from None
        laenge = math.sqrt(tx * tx + ty * ty + tz * tz + tw * tw)
        if not math.isfinite(laenge) or laenge < 1e-9:
            raise PosenFehler('Eine Drehung hat die Länge null.')
        q = [tw / laenge, tx / laenge, -tz / laenge, ty / laenge]
        return [-v for v in q] if q[0] < 0 else q

    @classmethod
    def _unbewegt(cls, q):
        return abs(q[0] - 1.0) <= cls.SCHWELLE and all(abs(v) <= cls.SCHWELLE for v in q[1:])
