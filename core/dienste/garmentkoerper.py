# -*- coding: utf-8 -*-
"""Garmentkoerper — den Koerper der GEWAEHLTEN Figur zum Drapieren ablegen.

WARUM (Edgar, 06.09.2026: „ergebnis ist schlecht ... er liegt aber nicht an"):
Der Stoff fiel auf `mean_all`, GarmentCodes Durchschnittskoerper — im Code
stand `Drapierung(spezifikation, koerper=None)`, und `None` heisst `mean_all`.
Danach wurde das Netz an der Figur nur VERANKERT, nicht auf sie gelegt.
Gemessen an der Rig-Datei des letzten Laufs: Median 27,4 mm Abstand zur Haut,
31 % der 5.658 Punkte weiter als 5 cm weg, im Maximum 86 mm. Das Rendering aus
demselben Lauf zeigt dasselbe T-Shirt tadellos sitzen — auf `mean_all`.

Die Bausteine dafuer lagen fertig da und hatten keinen einzigen Aufrufer:
`GarmentCode.koerperablage.Koerperablage` schreibt Netz und Masse in der
Lage, die GarmentCode erwartet, und `GarmentCode.segmentierung.Segmentierung`
baut die Koerperteil-Zuordnung fuer das MB-Lab-Netz. Dieses Modul ist die
Bruecke: Figur -> abgelegter Koerper -> Name und Ordner fuer den Simulationslauf.

FASSUNGSNAME
============
Der Dateiname traegt einen Fingerabdruck der PUNKTE, nicht der Morphnamen:
`figur_<12 Hexstellen>.obj`. Zwei Figuren mit verschiedenen Reglern bekommen
verschiedene Dateien, dieselbe Figur bekommt dieselbe — der zweite Lauf spart
das Schreiben. Ohne diesen Namen laege je Geschlecht EINE Datei, die jeder
Lauf ueberschreibt, waehrend ein paralleler Lauf noch darauf simuliert.

EIN ORDNER JE GESCHLECHT
========================
Die Segmentierung heisst bei GarmentCode fest `ggg_body_segmentation.json`
(`sim_config.py`) — es gibt keinen Schalter fuer einen anderen Namen. Sie
gilt fuer eine TOPOLOGIE, und die weiblichen und maennlichen MB-Lab-Netze
haben verschiedene. Deshalb liegt je Geschlecht ein eigener Unterordner mit
seiner eigenen Segmentierung; die Koerpernetze darin teilen sie sich.

DIE SEGMENTE BRAUCHT AUCH DIE MASSMESSUNG (06.09.2026)
======================================================
`Koerpermasse` trennte die Arme bis dahin an Luecken der Scheibe ab und
verlor damit den halben Rumpf (`bust` roh 44,5 cm). Jetzt bekommt sie die
Segmente ueber `segmente()` — dieselbe Zuordnung, die die Drapierung nutzt.
"""

import hashlib
import logging
import os

import numpy as np

from .charakterdaten import Charakterdaten

logger = logging.getLogger('core')


class Garmentkoerper:
    """Legt den Koerper einer Figur so ab, wie die Drapierung ihn sucht."""

    #: So viele Hexstellen des Fingerabdrucks stehen im Dateinamen. Zwoelf
    #: sind reichlich: Es geht um ein paar Dutzend Figuren, nicht um Kryptos.
    STELLEN = 12

    #: Die gebauten Segmente je Geschlecht. Sie haengen nur an der Topologie
    #: und kosten einen Durchlauf ueber 18.210 Vertices mit ihren
    #: Knochengewichten — das muss nicht bei jeder Drapierung sein.
    _segmente = {}

    # ------------------------------------------------------------ bereitstellen

    @classmethod
    def bereitstellen(cls, geschlecht, punkte, masse):
        """Netz, Masse und Segmentierung ablegen.

        `punkte` sind die Vertices der Figur MIT ihren Morphs, `masse` ihre
        gemessenen Koerpermasse. Rueckgabe: `{'name', 'ordner'}` fuer den
        Simulationslauf — oder `None`, wenn etwas fehlt; dann drapiert der
        Aufrufer wie bisher auf dem Vorgabekoerper.
        """
        from GarmentCode.koerperablage import Koerperablage

        netz = Charakterdaten.netzdaten(geschlecht)
        if punkte is None or getattr(netz, 'faces', None) is None:
            logger.warning('GarmentCode: kein Figurkoerper — Netz fehlt')
            return None

        punkte = np.asarray(punkte, dtype=np.float64)
        name = cls.name(punkte)
        ordner = cls.ordner(geschlecht)
        ablage = Koerperablage(name, punkte, netz.faces, ordner=ordner)

        # Die Segmentierung nur schreiben, wenn sie im Ordner fehlt — sie
        # haengt an der Topologie, nicht an der Figur. Das Netz schreibt
        # `ablegen` ohnehin; derselbe Fingerabdruck ueberschreibt sich mit
        # identischem Inhalt.
        segmentdatei = os.path.join(ordner, Koerperablage.SEGMENTDATEI)
        segmente = None
        if not os.path.isfile(segmentdatei):
            segmente = cls.segmente(geschlecht, len(punkte))
        ablage.ablegen(masse, segmentierung=segmente)
        return {'name': name, 'ordner': ordner}

    # -------------------------------------------------------------- Bausteine

    @classmethod
    def name(cls, punkte):
        """Ein Fingerabdruck der Punkte als Dateiname."""
        roh = np.asarray(punkte, dtype=np.float32).tobytes()
        return 'figur_%s' % hashlib.sha1(roh).hexdigest()[:cls.STELLEN]

    @staticmethod
    def ordner(geschlecht):
        """Der Ablageort dieses Geschlechts — siehe Modulkopf."""
        from GarmentCode.koerperablage import Koerperablage
        return os.path.join(Koerperablage.ORDNER, geschlecht)

    @classmethod
    def segmente(cls, geschlecht, anzahl=None):
        """Die Koerperteil-Zuordnung dieses Geschlechts, einmal gebaut.

        dict `{'body': [...], 'left_arm': [...], ...}` mit Vertex-Indizes —
        oder None, wenn das Netz keine Skinning-Gewichte hat.

        `anzahl` wird NICHT mehr geglaubt (07.09.2026). Sie kam vom
        Aufrufer, und der erste Aufrufer bestimmte, wie lang die Listen
        wurden — beim Mann einmal 18.210 statt 17.996, weil das Grundnetz
        das weibliche war. Danach lief jede weitere Messung in einen
        IndexError, obwohl mit dem Netz alles stimmte. Die Laenge steht im
        Netz selbst: so viele Skinning-Gewichte, wie es Vertices hat.
        """
        if geschlecht in cls._segmente:
            return cls._segmente[geschlecht]
        from GarmentCode.segmentierung import Segmentierung
        netz = Charakterdaten.netzdaten(geschlecht)
        # Die Segmentierung laeuft ueber das BASISNETZ — dessen Gewichte,
        # wenn es sie gibt (die unterteilte Datei fuehrt die Basis-Vertices
        # zwar zuerst, aber das ist eine Annahme ueber die Reihenfolge).
        gewichte = (getattr(netz, 'skin_weights_base', None)
                    or getattr(netz, 'skin_weights', None))
        if not gewichte or getattr(netz, 'faces', None) is None:
            logger.warning('GarmentCode: keine Skinning-Gewichte — '
                           'Segmentierung nicht baubar')
            return None
        vertexzahl = len(gewichte.get('weights') or [])
        if anzahl is not None and int(anzahl) != vertexzahl:
            logger.warning('GarmentCode: Segmentierung %s — Netz hat %d '
                           'Punkte, der Aufrufer nannte %d; das Netz gilt',
                           geschlecht, vertexzahl, int(anzahl))
        segmente = Segmentierung(
            netz.faces, netz.face_materials, netz.material_names or [],
            gewichte, vertexzahl).segmente()
        cls._segmente[geschlecht] = segmente
        logger.info('GarmentCode: Segmentierung %s — %s', geschlecht,
                    ', '.join('%s %d' % (n, len(v))
                              for n, v in sorted(segmente.items())))
        return segmente
