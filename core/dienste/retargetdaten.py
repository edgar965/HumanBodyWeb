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
import logging
import os

import ujson

from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
from humanbody_core.skeleton.retarget.fassung import REGELFASSUNG

from .skelettgeometrie import Skelettgeometrie

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
    ZIEL_G9 = 'genesis9'

    def __init__(
        self,
        bvh_pfad,
        body_height=ERSATZHOEHE,
        fmt=None,
        foot_correction=False,
        delta_norm=None,
        ziel=ZIEL_DEF,
        figur=None,
        formung=None,
    ):
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
        merkmal = f'v{REGELFASSUNG}_{self.hoehe:.4f}_{self.format}_{self.fusskorrektur}_{self.delta_norm}'
        if self.ziel != self.ZIEL_DEF:
            merkmal += f'_{self.ziel}'
        if self.figur:
            # je Figur ein eigenes Skelett, eine eigene Ablage
            merkmal += f'_{self.figur}'
        if self.ziel == self.ZIEL_SMPL:
            # Das Skelett der SMPL-Figur hat eine eigene Fassung (seit dem
            # 15.09.2026 SMPL-X mit 55 Gelenken) — sonst liefern Ablagen
            # mit 24 Gelenken weiter das alte Ergebnis (`Smplfiguren`).
            from .smplfigur import Smplfiguren

            merkmal += f'_sx{Smplfiguren.SKELETTFASSUNG}'
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
            return None  # die BVH-Datei ist neuer
        try:
            with open(pfad) as datei:
                return Bewegungsspuren.aus_dict(ujson.load(datei))
        except OSError, ValueError:
            logger.warning('[retarget] Zwischenspeicher %s unlesbar, wird neu gerechnet', pfad, exc_info=True)
            return None

    def merken(self, ergebnis):
        try:
            with open(self.ablage, 'w') as datei:
                ujson.dump(ergebnis.als_dict(), datei)
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)

    # ---------------------------------------------------------------- Rechnen

    def holen(self):
        """Das Ergebnis — aus der Ablage oder frisch gerechnet."""
        gemerkt = self.gemerkt()
        if gemerkt is not None:
            return self._mimik_dazu(self._gesicht_dazu(gemerkt))
        ergebnis = self._rechnen()
        self.merken(ergebnis)
        return self._mimik_dazu(self._gesicht_dazu(ergebnis))

    def _mimik_dazu(self, ergebnis):
        """Die im Studio eingerechnete Mimik (`<stamm>_mimik.json`, 14.09.2026)
        auf das DEF-Ergebnis legen — nach der Ablage, wie das Gesicht."""
        if self.ziel != self.ZIEL_DEF:
            return ergebnis
        from .mimikspuren import Mimikspuren

        return Mimikspuren.mischen(ergebnis, self.bvh_pfad)

    #: Die Marke der eigenen SMPL-X-Pipeline neben ihrem BVH (12.09.2026).
    SMPLX_MARKE = '_smplx.npz'

    def _gesicht_dazu(self, ergebnis):
        """Das Gesicht der SMPL-X-Pipeline auf das DEF-Ergebnis legen.

        Ihr BVH traegt Koerper und Finger; Kiefer und Ausdruck liegen daneben
        als `<stamm>_blendshapes.json` (dieselbe Datei wie beim Hybrid). Gemischt
        wird NACH der Ablage, damit die Ablage die reine Knochenumsetzung bleibt.
        Nur fuer Dateien, neben denen die SMPL-X-Bahn liegt — die Gesichts-BVH des
        Hybrids (v4) hat dieselbe Nachbardatei und wird in `retarget_job_merge`
        gemischt, nicht hier.
        """
        stamm = self.bvh_pfad.rsplit('.', 1)[0]
        if self.ziel != self.ZIEL_DEF or not os.path.isfile(stamm + self.SMPLX_MARKE):
            return ergebnis
        from .gesichtsspuren import Gesichtsspuren

        return Gesichtsspuren.mischen(ergebnis, Gesichtsspuren.laden(self.bvh_pfad))

    def _rechnen(self):
        from humanbody_core.skeleton import Skeleton, SkeletonRigify

        bvh = SkeletonRigify.parse_bvh(self.bvh_pfad)
        bauart = Skeleton.get_format(self.format) if self.format else Skeleton.detect_format(bvh.names)
        if self.ziel == self.ZIEL_UMA:
            return self._auf_uma(bvh, bauart)
        if self.ziel == self.ZIEL_SMPL:
            return self._auf_smpl(bvh, bauart)
        if self.ziel == self.ZIEL_MH:
            return self._auf_makehuman(bvh, bauart)
        if self.ziel == self.ZIEL_UMAPY:
            return self._auf_umapython(bvh, bauart)
        if self.ziel == self.ZIEL_G9:
            return self._auf_genesis9(bvh, bauart)
        geometrie = Skelettgeometrie.holen()
        if bauart and bauart.BONE_MAP_TO_RIGIFY:
            return bauart.retarget_to_rigify(
                bvh,
                geometrie,
                body_height=self.hoehe,
                foot_correction=self.fusskorrektur,
                delta_norm=self.delta_norm,
            )
        return SkeletonRigify.retarget_bvh(
            bvh, geometrie, fmt=self.format, body_height=self.hoehe, foot_correction=self.fusskorrektur
        )

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
            bvh,
            Umaskelett.geometrie(self.figur),
            body_height=self.hoehe,
            foot_correction=self.fusskorrektur,
            delta_norm=self.delta_norm,
            mapping=Umazuordnung.fuer(bauart),
            skip_bones=Umazuordnung.ausnahmen(bauart),
        )

    # ------------------------------------------------- SMPL und MakeHuman

    def _auf_smpl(self, bvh, bauart):
        """Ziel ist das SMPL-X-Skelett der Figur in der Szene (07.09.2026,
        seit dem 15.09.2026 SMPL-X mit Fingern, Kiefer und Augen).

        Es braucht keine neue Zuordnungstabelle: Die 22 Koerpergelenke
        heissen genau so, wie der Motor SMPL schon kennt
        (`SkeletonAIST_SMPL`), die Finger wie in `SkeletonSMPLX`;
        `Smplxzuordnung` kehrt beide Tabellen um. Die Geometrie kommt aus
        derselben Kette, aus der auch der Browser seine Knochen baut
        (`Smplfiguren.kette`) — sonst rechnete der Motor gegen eine
        Ruhelage, die die Figur gar nicht hat.
        """
        from .smplfigur import Smplfiguren
        from .smplxzuordnung import Smplxzuordnung

        kette = Smplfiguren.kette(self.figur)
        if kette is None:
            raise ValueError('Kein SMPL-X-Skelett fuer %r' % (self.figur,))
        return self._auf_kette(bvh, bauart, kette.geometrie(), Smplxzuordnung)

    def _auf_makehuman(self, bvh, bauart):
        """Ziel ist das MakeHuman-Rig (`default.mhskel`) DIESER Reglerstellung."""
        from humanbody_core.skeleton.formats.mh_zuordnung import Mhzuordnung
        from MakeHuman.skelett import Mhskelett

        if not Mhskelett.vorhanden():
            raise ValueError('MakeHuman-Upstream fehlt — siehe MakeHuman/HERKUNFT.md')
        return self._auf_kette(bvh, bauart, Mhskelett(self.formung).kette().geometrie(), Mhzuordnung)

    def _auf_umapython(self, bvh, bauart):
        """Ziel ist die in Python gebaute UMA-Figur (08.09.2026).

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

    def _auf_genesis9(self, bvh, bauart):
        """Ziel ist das Daz-Rig von Genesis 9 DIESER Reglerstellung (17.09.2026).

        Woher das Skelett kommt, steht in `G9retargetziel` — dieselbe Kette
        wie im Browser. `self.formung` ist die `G9formung` oder None.
        """
        from .g9retargetziel import G9retargetziel

        return self._auf_kette(
            bvh, bauart, G9retargetziel.geometrie(self.formung), G9retargetziel.zuordnung()
        )

    def _auf_kette(self, bvh, bauart, geometrie, zuordnung):
        """Dasselbe Verfahren, anderes Zielskelett — wie `_auf_uma`.

        Ohne erkanntes Format derselbe Rueckfall wie
        `SkeletonRigify.retarget_bvh`: MocapNET.
        """
        from humanbody_core.skeleton.formats import SkeletonMocapNet

        if bauart is None or not bauart.BONE_MAP_TO_RIGIFY:
            bauart = SkeletonMocapNet
        defnamen = getattr(zuordnung, 'defnamen', None)
        return bauart.retarget_to_rigify(
            bvh,
            geometrie,
            body_height=self.hoehe,
            foot_correction=self.fusskorrektur,
            delta_norm=self.delta_norm,
            mapping=zuordnung.fuer(bauart),
            skip_bones=zuordnung.ausnahmen(bauart),
            def_namen=defnamen() if callable(defnamen) else None,
        )

    def _formmerkmal(self):
        """Ein kurzes Kennzeichen der Reglerstellung fuer den Ablagenamen.

        Ein Woerterbuch wird SORTIERT verschriftet (UMA Python schickt
        seine DNA so). `repr` eines dict folgt der Einfuegereihenfolge —
        dieselbe Stellung, zweimal anders getippt, ergaebe zwei Ablagen,
        und beide waeren gueltig. Ein Ablagename, der von der
        Tippreihenfolge abhaengt, ist keiner.
        """
        if isinstance(self.formung, dict):
            roh = repr(sorted((str(k), round(float(v), 6)) for k, v in self.formung.items()))
        else:
            fingerabdruck = getattr(self.formung, 'fingerabdruck', None)
            roh = fingerabdruck() if callable(fingerabdruck) else repr(self.formung)
        return hashlib.md5(roh.encode('utf-8')).hexdigest()[:8]
