# -*- coding: utf-8 -*-
"""Retargetdaten — eine BVH-Datei auf das Rigify/DEF-Skelett rechnen.

Herausgeloest aus `core/api/retarget.py` (18.08.2026). Zwei Gruende:

1. **Es ist Fachlogik, kein Endpunkt.** Drei Endpunkte in zwei Modulen rufen
   sie (`api/retarget.py`, `api/bvhtext.py`, `api/dateien.py`).
2. **Sie hat einen Ringimport ausgeloest.** `api/dateien.py` holte sie aus
   `api/retarget.py`, und `api/retarget.retarget_job_bvh` leitet umgekehrt auf
   `api/dateien.serve_bvh_file` weiter — `abhaengigkeiten` meldete den Zyklus
   sofort, nachdem der (tote) Import in `dateien.py` repariert war. Fachlogik
   in `dienste/` haengt an keinem Endpunkt, damit ist der Ring auf.

DER ZWISCHENSPEICHER
====================
Das Ergebnis liegt als JSON NEBEN der BVH-Datei, mit einem Namen aus den
Parametern (`…_retarget_<hash>.json`). Er gilt nur, solange er JUENGER ist als
die BVH-Datei — wird die bearbeitet (Glaetten, Effekte), faellt er von selbst
weg. Eine unlesbare Ablage ist kein Drama; sie wird neu gerechnet, aber
protokolliert: Wenn sie es JEDES Mal ist, sucht man sonst lange.
"""

import hashlib
import json
import logging
import os

from .skelettgeometrie import Skelettgeometrie
from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
from humanbody_core.skeleton.retarget.fassung import REGELFASSUNG

logger = logging.getLogger('core')


class Retargetdaten:
    """Retarget-Ergebnis einer BVH-Datei, mit Zwischenspeicher."""

    ERSATZHOEHE = 1.68
    #: Zielskelette — siehe `Retargetwahl.ZIELE`.
    ZIEL_DEF = 'def'
    ZIEL_UMA = 'uma'
    ZIEL_SMPL = 'smpl'
    ZIEL_MH = 'makehuman'
    ZIEL_UMAPY = 'umapython'

    def __init__(self, bvh_pfad, body_height=ERSATZHOEHE, fmt=None,
                 foot_correction=False, delta_norm=None, ziel=ZIEL_DEF,
                 figur=None, formung=None):
        self.bvh_pfad = bvh_pfad
        self.hoehe = body_height
        self.format = fmt
        self.fusskorrektur = foot_correction
        self.delta_norm = delta_norm
        self.ziel = ziel or self.ZIEL_DEF
        #: Dateiname der UMA-Figur bzw. Name des SMPL-Koerpers, dessen
        #: Skelett das Ziel ist (06.09.2026); ohne Angabe bei UMA die Datei
        #: aus `aktuell.json` — siehe `Retargetwahl`.
        self.figur = figur
        #: `Mhformung` der MakeHuman-Figur (07.09.2026). Ihr Skelett haengt
        #: an 269 Reglern; ohne sie waere das Ziel die Vorgabefigur.
        self.formung = formung

    # ------------------------------------------------------- Zwischenspeicher

    @property
    def ablage(self):
        # DIE FASSUNG DER REGELN GEHOERT IN DEN NAMEN (09.09.2026): Ohne
        # sie liefern vorhandene Ablagen nach einer Regelaenderung
        # weiter das alte Ergebnis — still, und die Aenderung kommt
        # nirgends an. Begruendung in `retarget/fassung.py`.
        merkmal = (f'v{REGELFASSUNG}_{self.hoehe:.4f}_{self.format}'
                   f'_{self.fusskorrektur}_{self.delta_norm}')
        if self.ziel != self.ZIEL_DEF:
            merkmal += f'_{self.ziel}'
        if self.figur:
            # je Figur ein eigenes Skelett, eine eigene Ablage
            merkmal += f'_{self.figur}'
        if self.formung is not None:
            # Je Reglerstellung ein eigenes Skelett: Ohne diesen Teil im
            # Namen laege die Bewegung der schlanken Figur in derselben
            # Datei wie die der kraeftigen.
            merkmal += '_' + self._formmerkmal()
        kuerzel = hashlib.md5(merkmal.encode()).hexdigest()[:8]
        return self.bvh_pfad.rsplit('.', 1)[0] + f'_retarget_{kuerzel}.json'

    def gemerkt(self):
        """Das gespeicherte Ergebnis — oder `None`."""
        pfad = self.ablage
        if not os.path.isfile(pfad):
            return None
        if os.path.getmtime(pfad) <= os.path.getmtime(self.bvh_pfad):
            return None      # die BVH-Datei ist neuer
        try:
            with open(pfad, 'r') as datei:
                return Bewegungsspuren.aus_dict(json.load(datei))
        except (OSError, ValueError):
            logger.warning('[retarget] Zwischenspeicher %s unlesbar, wird neu '
                           'gerechnet', pfad, exc_info=True)
            return None

    def merken(self, ergebnis):
        try:
            with open(self.ablage, 'w') as datei:
                json.dump(ergebnis.als_dict(), datei)
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)

    # ---------------------------------------------------------------- Rechnen

    def holen(self):
        """Das Ergebnis — aus der Ablage oder frisch gerechnet."""
        gemerkt = self.gemerkt()
        if gemerkt is not None:
            return gemerkt
        ergebnis = self._rechnen()
        self.merken(ergebnis)
        return ergebnis

    def _rechnen(self):
        from humanbody_core.skeleton import Skeleton, SkeletonRigify
        bvh = SkeletonRigify.parse_bvh(self.bvh_pfad)
        bauart = (Skeleton.get_format(self.format) if self.format
                  else Skeleton.detect_format(bvh.names))
        if self.ziel == self.ZIEL_UMA:
            return self._auf_uma(bvh, bauart)
        if self.ziel == self.ZIEL_SMPL:
            return self._auf_smpl(bvh, bauart)
        if self.ziel == self.ZIEL_MH:
            return self._auf_makehuman(bvh, bauart)
        if self.ziel == self.ZIEL_UMAPY:
            return self._auf_umapython(bvh, bauart)
        geometrie = Skelettgeometrie.holen()
        if bauart and bauart.BONE_MAP_TO_RIGIFY:
            return bauart.retarget_to_rigify(
                bvh, geometrie, body_height=self.hoehe,
                foot_correction=self.fusskorrektur, delta_norm=self.delta_norm)
        return SkeletonRigify.retarget_bvh(
            bvh, geometrie, fmt=self.format, body_height=self.hoehe,
            foot_correction=self.fusskorrektur)

    def _auf_uma(self, bvh, bauart):
        """Dasselbe Verfahren mit Ziel UMA (05.09.2026).

        Geometrie aus der GLB im Figurkatalog (`Umaskelett`), die Zuordnung
        des Formats ueber `DEF_ZU_UMA` uebersetzt — eine Tabelle fuer alle
        Formate, siehe `formats/uma_knochen.py`. Ohne erkanntes Format
        derselbe Rueckfall wie `SkeletonRigify.retarget_bvh`: MocapNET.
        """
        from humanbody_core.skeleton.formats import SkeletonMocapNet
        from humanbody_core.skeleton.formats.uma_knochen import Umazuordnung
        from .umaskelett import Umaskelett
        if bauart is None or not bauart.BONE_MAP_TO_RIGIFY:
            bauart = SkeletonMocapNet
        return bauart.retarget_to_rigify(
            bvh, Umaskelett.geometrie(self.figur), body_height=self.hoehe,
            foot_correction=self.fusskorrektur, delta_norm=self.delta_norm,
            mapping=Umazuordnung.fuer(bauart),
            skip_bones=Umazuordnung.ausnahmen(bauart))

    # ------------------------------------------------- SMPL und MakeHuman

    def _auf_smpl(self, bvh, bauart):
        u"""Ziel ist das SMPL-Skelett der Figur in der Szene (07.09.2026).

        Es braucht keine neue Zuordnungstabelle: Die 24 Gelenke heissen
        genau so, wie der Motor SMPL schon kennt (`SkeletonAIST_SMPL`), und
        `Smplzuordnung` kehrt dessen Tabelle um. Die Geometrie kommt aus
        derselben Kette, aus der auch der Browser seine Knochen baut
        (`Smplfiguren.kette`) — sonst rechnete der Motor gegen eine
        Ruhelage, die die Figur gar nicht hat.
        """
        from humanbody_core.skeleton.formats.smpl_knochen import Smplzuordnung
        from .smplfigur import Smplfiguren
        kette = Smplfiguren.kette(self.figur)
        if kette is None:
            raise ValueError('Kein SMPL-Skelett fuer %r' % (self.figur,))
        return self._auf_kette(bvh, bauart, kette.geometrie(), Smplzuordnung)

    def _auf_makehuman(self, bvh, bauart):
        u"""Ziel ist das MakeHuman-Rig (`default.mhskel`) DIESER Reglerstellung."""
        from humanbody_core.skeleton.formats.mh_zuordnung import Mhzuordnung
        from MakeHuman.skelett import Mhskelett
        if not Mhskelett.vorhanden():
            raise ValueError('MakeHuman-Upstream fehlt — siehe MakeHuman/HERKUNFT.md')
        return self._auf_kette(bvh, bauart,
                               Mhskelett(self.formung).kette().geometrie(),
                               Mhzuordnung)

    def _auf_umapython(self, bvh, bauart):
        u"""Ziel ist die in Python gebaute UMA-Figur (08.09.2026).

        Es braucht keine neue Zuordnungstabelle: Die Knochen heissen
        genau wie in der GLB aus Unity — beide Wege bauen dasselbe
        UMA-Rig. `Umazuordnung` (05.09.2026) gilt deshalb unveraendert,
        und ein Fehler darin ist auf beiden Wegen einer.

        Die Geometrie kommt aus derselben Kette, aus der auch der
        Browser seine Knochen baut (`Umagelenke.bauplan`). Waere es eine
        zweite Rechnung, rechnete der Motor gegen eine Ruhelage, die
        die Figur gar nicht hat — der Befund vom 07.09.2026 bei SMPL.

        `self.figur` traegt hier den RASSENNAMEN, keinen Dateinamen.
        """
        from humanbody_core.skeleton.formats.uma_knochen import Umazuordnung
        from UMA_Python.gelenke import Umagelenke
        from .umapythonfiguren import Umapythonfiguren
        if not self.figur:
            raise ValueError('Kein Rassenname fuer das UMA-Python-Ziel')
        gebaut = Umapythonfiguren.bauen(self.figur)
        gelenke = Umagelenke(gebaut, self.formung)
        return self._auf_kette(bvh, bauart, gelenke.geometrie(), Umazuordnung)

    def _auf_kette(self, bvh, bauart, geometrie, zuordnung):
        u"""Dasselbe Verfahren, anderes Zielskelett — wie `_auf_uma`.

        Ohne erkanntes Format derselbe Rueckfall wie
        `SkeletonRigify.retarget_bvh`: MocapNET.
        """
        from humanbody_core.skeleton.formats import SkeletonMocapNet
        if bauart is None or not bauart.BONE_MAP_TO_RIGIFY:
            bauart = SkeletonMocapNet
        return bauart.retarget_to_rigify(
            bvh, geometrie, body_height=self.hoehe,
            foot_correction=self.fusskorrektur, delta_norm=self.delta_norm,
            mapping=zuordnung.fuer(bauart),
            skip_bones=zuordnung.ausnahmen(bauart))

    def _formmerkmal(self):
        u"""Ein kurzes Kennzeichen der Reglerstellung fuer den Ablagenamen.

        Ein Woerterbuch wird SORTIERT verschriftet (UMA Python schickt
        seine DNA so). `repr` eines dict folgt der Einfuegereihenfolge —
        dieselbe Stellung, zweimal anders getippt, ergaebe zwei Ablagen,
        und beide waeren gueltig. Ein Ablagename, der von der
        Tippreihenfolge abhaengt, ist keiner.
        """
        if isinstance(self.formung, dict):
            roh = repr(sorted((str(k), round(float(v), 6))
                              for k, v in self.formung.items()))
        else:
            fingerabdruck = getattr(self.formung, 'fingerabdruck', None)
            roh = (fingerabdruck() if callable(fingerabdruck)
                   else repr(self.formung))
        return hashlib.md5(roh.encode('utf-8')).hexdigest()[:8]
