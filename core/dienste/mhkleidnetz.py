# -*- coding: utf-8 -*-
u"""Mhkleidnetz — ein MakeHuman-Kleidungsstueck auf dem MakeHuman-Basiskoerper.

DER UNTERSCHIED ZU `MhProxyAnpassung`
=====================================
Dort wird ein MakeHuman-Stueck auf einen FREMDEN Koerper gebracht (den
gemorphten Rigify-Koerper des Projekts). Das geht nur mit Nacharbeit:
glaetten, abruecken, skalieren, heben, von T- auf A-Pose, aus dem Koerper
schieben — sieben Schritte, jeder mit einem Regler.

Hier ist der Traeger der Koerper, FUER DEN das Stueck entworfen wurde. Dann
ist die `.mhclo` keine Naeherung mehr, sondern die Definition:

    Punkt = w1·Koerper[v1] + w2·Koerper[v2] + w3·Koerper[v3] + Versatz

Es gibt nichts nachzubessern, und es gibt keinen Regler dafuer. Was bleibt,
ist Aussehen: Farbe, Rauheit, Metallanteil, Deckkraft.

UVs: DIE ECKEN WERDEN AUFGETEILT
================================
Eine OBJ nennt je Ecke einen Punkt UND einen Texturpunkt, und es sind nicht
gleich viele — `female_casualsuit01` hat 2.197 Punkte, aber 2.406 UVs. Three.js
kennt nur EINEN Index fuer beides. Wer die UVs stumpf je Punkt uebernimmt,
bekommt an jeder Naht der Textur einen verschmierten Streifen. Deshalb wird
je EINZIGARTIGEM Paar (Punkt, Texturpunkt) ein Vertex gebaut; die Lagen
werden dabei mehrfach kopiert, die Zuordnung stimmt.

Umlaufsinn: derselbe wie beim Basisnetz (`[a,b,c]` + `[a,c,d]`). Gemessen an
vier Stuecken ueber die Richtung „weg vom naechsten Koerperpunkt": 84,8 %
(Hose), 82,7 % (Schuhe), 80,5 % (Kleid), 58,6 % (Anzug — er hat Innen- und
Aussenlage, der naechste Koerperpunkt ist dort kein sauberer Bezug). Die
umgekehrte Folge ergibt jeweils den Gegenwert. Gezeichnet wird trotzdem
beidseitig, wie beim bestehenden MakeHuman-Weg.
"""

import logging
import os

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mhkleidnetz', 'MhkleidFehler']


class MhkleidFehler(RuntimeError):
    u"""Das Stueck gibt es nicht oder es hat keine brauchbare Zuordnung."""

    def __init__(self, text, status=400):
        super().__init__(text)
        self.status = status


class Mhkleidnetz:
    u"""Ein Stueck der Bibliothek, angepasst an das MakeHuman-Basisnetz."""

    def __init__(self, kennung, formung=None):
        from .mhgarderobe import Mhgarderobe
        self.kennung = kennung
        #: Die Reglerstellung des Traegers — der Stoff folgt ihr (siehe Kopf).
        self.formung = formung
        self.verzeichnis = Mhgarderobe.verzeichnis(kennung)
        if not self.verzeichnis or not os.path.isdir(self.verzeichnis):
            raise MhkleidFehler(u'Kein MakeHuman-Stück: %s' % kennung, 404)
        self.proxy = self._proxy()

    def _proxy(self):
        from tools.mhclo_proxy import MHCLOProxy
        try:
            proxy = MHCLOProxy.from_directory(self.verzeichnis)
        except FileNotFoundError as fehler:
            raise MhkleidFehler(str(fehler), 404) from fehler
        if proxy.vertex_count == 0:
            raise MhkleidFehler(u'Keine Vertexzuordnung in der .mhclo', 400)
        return proxy

    # ------------------------------------------------------------------ Netz

    def netz(self):
        u"""`dict` mit Punkten, Dreiecken, Normalen, UVs und Materialangaben.

        Die Punkte kommen in Three-Achsen (Meter, Y oben) und stehen auf
        demselben Boden wie das Basisnetz — sonst schwebte das Stueck um die
        Fusshoehe ueber oder unter der Figur.
        """
        from .mhbasisnetz import Mhbasisnetz
        from .mhmaterial import MhMaterial
        from .mhnetzformen import Mhnetzformen
        basis = Mhbasisnetz.holen()
        roh = self.formung.punkte() if self.formung else None
        blender = self.proxy.fit_vectorized(basis.punkte_blender(roh))
        punkte = self._nach_three(blender, basis.boden_von(roh))
        ecken, dreiecke, uvs = self._flaechen()
        punkte = punkte[ecken]
        antwort = {
            'kennung': self.kennung,
            'punkte': punkte.astype(np.float32),
            'dreiecke': dreiecke,
            'normalen': Mhnetzformen.normalen(punkte, dreiecke),
            'uvs': uvs,
        }
        logger.debug('MakeHuman-Kleid %s: %d Punkte, %d Dreiecke',
                     self.kennung, len(punkte), len(dreiecke))
        return MhMaterial(self.verzeichnis).in_antwort(antwort)

    @staticmethod
    def _nach_three(blender, boden):
        u"""Blender (Z oben) -> Three (Y oben), dann auf den Boden des Netzes."""
        punkte = np.column_stack([blender[:, 0], blender[:, 2], -blender[:, 1]])
        punkte[:, 1] -= boden
        return punkte

    # --------------------------------------------------------------- Flaechen

    def _flaechen(self):
        u"""`(Eckenpunkte, Dreiecke, UVs)` — je Paar (Punkt, Texturpunkt) ein Vertex.

        `ecken` ist die Liste der ALTEN Punktnummern in der neuen Reihenfolge;
        damit werden die angepassten Lagen umsortiert.
        """
        from GarmentFitter.obj_io import ObjIo
        obj = self._obj_lesen(ObjIo)
        flaechen = np.asarray(obj['faces'])
        if not len(flaechen):
            raise MhkleidFehler(u'Kleidungsnetz ohne Flächen', 400)
        uv_index = obj.get('face_uvs')
        uv_werte = obj.get('uvs')
        if uv_index is None or uv_werte is None or not len(uv_werte):
            return (np.arange(self.proxy.vertex_count),
                    self._dreiecke(flaechen), None)
        return self._aufteilen(flaechen, np.asarray(uv_index),
                               np.asarray(uv_werte))

    def _obj_lesen(self, ObjIo):
        name = self.proxy.obj_file
        pfad = os.path.join(self.verzeichnis, name) if name else ''
        if not name or not os.path.isfile(pfad):
            treffer = [d for d in sorted(os.listdir(self.verzeichnis))
                       if d.endswith('.obj')]
            if not treffer:
                raise MhkleidFehler(u'Keine OBJ neben der .mhclo', 404)
            pfad = os.path.join(self.verzeichnis, treffer[0])
        return ObjIo.load_obj(pfad)

    @classmethod
    def _aufteilen(cls, flaechen, uv_index, uv_werte):
        paare = np.column_stack([flaechen.ravel(), uv_index.ravel()])
        einzigartig, rueck = np.unique(paare, axis=0, return_inverse=True)
        neu = rueck.reshape(flaechen.shape)
        uvs = uv_werte[np.clip(einzigartig[:, 1], 0, len(uv_werte) - 1)]
        # Eine Ecke ohne Texturpunkt (`-1`) bekommt (0, 0) — sichtbar falsch
        # waere ein zufaelliger Wert aus der Liste.
        uvs[einzigartig[:, 1] < 0] = 0.0
        return einzigartig[:, 0], cls._dreiecke(neu), uvs.astype(np.float32)

    @staticmethod
    def _dreiecke(flaechen):
        u"""Vierecke teilen, entartete Dreiecke weglassen.

        `ObjIo` fuellt ein Dreieck in einem Vierecknetz auf `[a,b,c,c]` auf —
        daraus wird ein zweites Dreieck ohne Flaeche. Es stoert nicht beim
        Zeichnen, aber es verfaelscht jede gemittelte Normale.
        """
        from .mhnetzformen import Mhnetzformen
        flaechen = np.asarray(flaechen)
        if flaechen.shape[1] == 4:
            dreiecke = Mhnetzformen.dreiecke(flaechen)
        else:
            dreiecke = flaechen[:, :3].astype(np.uint32)
        gut = ((dreiecke[:, 0] != dreiecke[:, 1])
               & (dreiecke[:, 1] != dreiecke[:, 2])
               & (dreiecke[:, 0] != dreiecke[:, 2]))
        return dreiecke[gut]
