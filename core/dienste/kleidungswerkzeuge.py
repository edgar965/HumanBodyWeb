# -*- coding: utf-8 -*-
"""Kleidungswerkzeuge — Rechenschritte rund um ein Kleidungsstueck.

Vier Helfer aus core/api/kleidung.py, die mit HTTP nichts zu tun haben: die
Umrechnung von T- auf A-Pose, die Glaettung eines Kleidungsnetzes und die
Uebernahme der Knochengewichte vom Koerper auf das Kleidungsstueck
(Umbau 15.08.2026).
"""

from .skingewichte import Skingewichte
import logging
import numpy as np
import os
from django.conf import settings


logger = logging.getLogger('core')


class Kleidungswerkzeuge:
    """Kleidungswerkzeuge — Rechenschritte rund um ein Kleidungsstueck."""

    #: So viele MakeHuman-Punkte gehen in die Verschiebung EINES
    #: Kleidungspunktes ein — gewichtet nach Abstand.
    NACHBARN = 8

    @classmethod
    def tpose_zu_apose(cls, garment_verts, body_verts, gender='female'):
        """Kleidung von der T-Pose in die A-Pose bringen — ueber den Index.

        `base_vertices.npy` (MakeHuman in T-Pose) und `mh_base_apose.npy`
        (dasselbe Netz mit gedrehten Armen) haben DIESELBE Topologie. Die
        Verschiebung je Punkt ist damit eine Subtraktion; eine Nachbarsuche
        braucht es nur fuer die Kleidung, nicht fuer den Koerper.

        Fehlt eine der beiden Dateien oder passen ihre Formen nicht
        zusammen, kommt die Kleidung UNVERAENDERT zurueck — mit einem Eintrag
        im Protokoll. Stillschweigend falsch zu rechnen waere schlimmer.
        """
        mh_tpose = cls._mh_tpose(body_verts)
        if mh_tpose is None:
            return garment_verts
        verschiebung = cls._verschiebung(mh_tpose)
        if verschiebung is None:
            return garment_verts
        return cls._uebertragen(garment_verts, mh_tpose, verschiebung)

    @staticmethod
    def _mh_tpose(body_verts):
        """Der MakeHuman-Koerper in T-Pose, in Blender-Koordinaten.

        MakeHuman rechnet in Dezimetern mit Y nach oben, Blender in Metern
        mit Z nach oben. Danach werden die Fuesse auf die Hoehe des
        Koerpers gelegt, sonst schwebt die ganze Verschiebung.
        """
        pfad = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman',
                            'base_vertices.npy')
        if not os.path.isfile(pfad):
            logger.error('[T→A] No MH base_vertices.npy')
            return None
        roh = np.load(pfad)
        anzahl = min(roh.shape[0], body_verts.shape[0])
        tpose = np.column_stack([
            roh[:anzahl, 0] * 0.1,
            -roh[:anzahl, 2] * 0.1,
            roh[:anzahl, 1] * 0.1,
        ])
        tpose[:, 2] -= tpose[:, 2].min()
        tpose[:, 2] += body_verts[:, 2].min()
        return tpose

    @staticmethod
    def _verschiebung(mh_tpose):
        """A-Pose minus T-Pose — je Punkt, ohne Nachbarsuche.

        Beide Netze haben dieselbe Topologie; eine Nachbarsuche hier
        wuerde nur Artefakte einbauen.
        """
        pfad = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman',
                            'mh_base_apose.npy')
        if not os.path.isfile(pfad):
            logger.error('[T→A] No mh_base_apose.npy — skipping displacement')
            return None
        apose = np.load(pfad)
        if apose.shape != mh_tpose.shape:
            logger.error('[T→A] Shape mismatch: tpose=%s apose=%s',
                         mh_tpose.shape, apose.shape)
            return None
        return apose - mh_tpose

    @classmethod
    def _uebertragen(cls, garment_verts, mh_tpose, verschiebung):
        """Die Verschiebung des Koerpers auf die Kleidung uebertragen.

        Je Kleidungspunkt die `NACHBARN` naechsten Koerperpunkte, gewichtet
        mit dem Kehrwert des Abstands.
        """
        from humanbody_core.nachbarsuche import Nachbarsuche

        abstaende, kennungen = Nachbarsuche(mh_tpose).naechste(
            garment_verts, k=cls.NACHBARN)
        ergebnis = garment_verts.copy().astype(np.float64)
        for punkt in range(len(garment_verts)):
            gewicht = 1.0 / (abstaende[punkt] + 1e-6)
            gewicht /= gewicht.sum()
            ergebnis[punkt] += (gewicht[:, None]
                                * verschiebung[kennungen[punkt]]).sum(axis=0)
        logger.info('[T→A] Displaced %d garment verts (MH T-pose → Rigify '
                    'A-pose, K=%d)', len(ergebnis), cls.NACHBARN)
        return ergebnis.astype(np.float32)

    @staticmethod
    def glaetten(verts, faces, iterations=3, factor=0.5):
        """Laplacian smooth on garment mesh. Preserves boundary vertices."""
        from collections import defaultdict
        n = len(verts)
        # Build adjacency
        adj = defaultdict(set)
        for f in faces:
            for i in range(len(f)):
                for j in range(len(f)):
                    if i != j:
                        adj[f[i]].add(f[j])
        result = verts.copy().astype(np.float64)
        for _ in range(iterations):
            new_verts = result.copy()
            for vi in range(n):
                neighbors = adj.get(vi)
                if not neighbors or len(neighbors) < 2:
                    continue
                avg = np.mean(result[list(neighbors)], axis=0)
                new_verts[vi] = result[vi] + factor * (avg - result[vi])
            result = new_verts
        return result.astype(np.float32)

    @staticmethod
    def _zuordnung(garment_verts, body_verts, ref_body=None):
        u"""Zu jedem Kleidungspunkt der naechste Koerperpunkt — als Indexfeld.

        BEFUND `doppelcode` (30.08.2026): Diese vierzehn Zeilen standen zweimal,
        in ``knochenindizes`` und ``knochengewichte``. Die beiden Methoden
        unterschieden sich in EINEM Buchstaben (``si`` gegen ``sw``) — und
        gerade deshalb ist die Doppelung gefaehrlich: Wer die Zuordnung an einer
        Stelle verbessert, bekommt Indizes und Gewichte aus zwei verschiedenen
        Rechnungen. Das Kleidungsstück haengt dann an den richtigen Knochen mit
        den falschen Anteilen, was wie ein Verzerrungsfehler aussieht und keiner
        ist.

        MIT ``ref_body`` ZWEI SCHRITTE: Das Stück wurde gegen einen fremden
        Koerper gerechnet (etwa den von MakeHuman). Dann wird erst dessen
        naechster Punkt gesucht und dieser auf den naechsten Rigify-Punkt
        abgebildet. Ein Schritt weniger wuerde bei abweichendem Armwinkel den
        Aermel an den Rumpf binden.
        """
        from humanbody_core.nachbarsuche import Nachbarsuche
        if ref_body is not None and len(ref_body) != len(body_verts):
            _, nearest_ref = Nachbarsuche(ref_body).naechster(garment_verts)
            _, ref_to_body = Nachbarsuche(body_verts).naechster(ref_body)
            return ref_to_body[nearest_ref]
        _, nearest = Nachbarsuche(body_verts).naechster(garment_verts)
        return nearest

    @staticmethod
    def knochenindizes(garment_verts, body_verts, gender='female', ref_body=None):
        """Compute skin indices for garment by nearest-body-vertex transfer."""
        si, _sw = Skingewichte.arrays(gender)
        nearest = Kleidungswerkzeuge._zuordnung(garment_verts, body_verts, ref_body)
        return si[nearest].astype(np.float32).tobytes()

    @staticmethod
    def knochengewichte(garment_verts, body_verts, gender='female', ref_body=None):
        """Compute skin weights for garment by nearest-body-vertex transfer."""
        _si, sw = Skingewichte.arrays(gender)
        nearest = Kleidungswerkzeuge._zuordnung(garment_verts, body_verts, ref_body)
        return sw[nearest].astype(np.float32).tobytes()
