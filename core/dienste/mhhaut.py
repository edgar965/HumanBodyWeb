# -*- coding: utf-8 -*-
u"""Mhhaut — welche Knochen welchen Punkt der MakeHuman-Figur bewegen.

WARUM (Edgar, 07.09.2026: „Das Rigging funktioniert wohl nicht fuer die neuen
Modelle SMPL, MakeHuman")
=========================================================
Die MakeHuman-Figur war ein reines Netz. Beim Abspielen hing die Szene ihr
das Rigify-Skelett samt HumanBody-Hautgewichten an — 176 fremde Knochen fuer
ein Netz mit anderer Topologie. Es bewegte sich nichts.

Erfunden wird nichts: MakeHuman bringt die Gewichte zu `default.mhskel`
selbst mit, in `default_weights.mhw` (139 der 163 Knochen tragen welche;
die uebrigen sind Dreh- und Hilfsknochen ohne eigene Haut). Die Datei nennt
je Knochen eine Liste ``[Vertexnummer, Gewicht]`` — die Sicht ist also
umgedreht und wird hier einmal gekippt.

DREI DINGE MUESSEN ZUSAMMENPASSEN, UND JEDES EINZELN IST STILL FALSCH
====================================================================
1. **Die Auswahl.** Gezeigt wird nur ein Teil des Grundnetzes (`teile`:
   Haut, Helfergeometrie, Gelenkwuerfel). Die Gewichte stehen aber unter den
   Nummern des VOLLEN Netzes.
2. **Die Glaettung.** Mit „Smooth" hat das Netz eine andere Punktzahl und
   eine andere Reihenfolge (Catmull-Clark). Die Gewichte muessen durch
   DIESELBE Matrix wie die Punkte — ein Punkt, der geometrisch zu 25 % aus
   einem Basispunkt entsteht, gehoert auch zu 25 % zu dessen Knochen. Genau
   das ist die Lektion aus dem HumanBody-Weg („Blender's evaluated mesh has
   a DIFFERENT vertex order"), und `CatmullClarkSubdivider` bringt die
   Matrix dafuer mit.
3. **Das Verdichten.** Nach dem Ausblenden verdeckter Haut faellt ein Teil
   der Punkte weg und alles wird neu nummeriert (`Mhnetzformen.verdichten`).
   Dieselbe Auswahl muss auf die Gewichte.

Wer eine der drei Stufen ueberspringt, bekommt eine Figur, die sich bewegt —
nur eben verkehrt: Die Schulter zuckt, wenn das Knie sich beugt. Kein
Fehler, keine Meldung.

DIE GEWICHTE HAENGEN NICHT AN DEN REGLERN. Sie stehen je VERTEXNUMMER, und
die aendert kein Modellierregler. Deshalb wird je (Teile, Glaettung) genau
einmal gerechnet — sonst laege bei jedem Reglerzug eine Matrixmultiplikation
ueber 53.000 Punkte im Weg.
"""

import json
import logging
import os
import threading

import numpy as np
from django.conf import settings

from .mhglaettung import Mhglaettung
from .mhskelett import Mhskelett

logger = logging.getLogger('core')

__all__ = ['Mhhaut']


class Mhhaut:
    u"""Die Hautgewichte des MakeHuman-Rigs, fuer ein Anzeigenetz aufbereitet."""

    ORDNER = 'rigs'
    DATEI = 'default_weights.mhw'
    #: So viele Knochen traegt ein Punkt in einem `SkinnedMesh`.
    JE_PUNKT = 4

    _roh = None
    _fein = {}
    #: RLock, nicht Lock: `fuer_netz` haelt ihn und ruft ueber `_matrix`
    #: wieder `roh()` — mit einem gewoehnlichen Lock steht der Prozess
    #: STILL. Kein Fehler, keine Meldung, nur eine Anfrage, die nie
    #: zurueckkommt (07.09.2026, beim ersten Messlauf zugeschlagen).
    _schloss = threading.RLock()

    # ----------------------------------------------------------------- Datei

    @classmethod
    def pfad(cls):
        return os.path.join(str(settings.MAKEHUMAN_DATA_DIR), cls.ORDNER,
                            cls.DATEI)

    @classmethod
    def vorhanden(cls):
        return os.path.isfile(cls.pfad())

    @classmethod
    def roh(cls):
        u"""``{knochenname: [[vertexnummer, gewicht], …]}`` aus der Datei."""
        if cls._roh is None:
            with cls._schloss:
                if cls._roh is None:
                    with open(cls.pfad(), 'r', encoding='utf-8') as datei:
                        cls._roh = json.load(datei)['weights']
                    logger.info('MakeHuman-Hautgewichte gelesen: %d Knochen',
                                len(cls._roh))
        return cls._roh

    @classmethod
    def vergessen(cls):
        cls._roh = None
        cls._fein = {}
        cls._grund = None

    # --------------------------------------------------------------- rechnen

    @classmethod
    def knochennamen(cls):
        u"""Die Knochen in der Spaltenreihenfolge der Gewichtsmatrix.

        ALLE Knochen des Rigs, nicht nur die 139 mit Gewichten: Sonst fehlte
        ausgerechnet `root` die Spalte, an die ein Punkt ohne jedes Gewicht
        gehaengt wird — und er landete auf `breast.L`, dem ersten Namen der
        Datei. Sortiert, damit die Reihenfolge nicht an der Reihenfolge
        einer JSON-Datei haengt; an den Browser gehen ohnehin NAMEN.
        """
        return sorted(Mhskelett.rig()['bones'])

    @classmethod
    def fuer_netz(cls, basisnummern, lokale, teile, glatt):
        u"""``(index, gewicht)`` je Punkt des Anzeigenetzes VOR dem Verdichten.

        @param basisnummern Vertexnummern des vollen Netzes, in der Reihenfolge
                            der Anzeigepunkte (`Mhnetzformen.umschluesseln`)
        @param lokale       die Vierecke mit lueckenlosen Nummern — nur fuer
                            die Glaettung, dieselbe Auswahl wie beim Netz
        """
        schluessel = ('+'.join(teile), bool(glatt))
        if schluessel in cls._fein:
            return cls._fein[schluessel]
        with cls._schloss:
            if schluessel not in cls._fein:
                cls._fein[schluessel] = cls._rechnen(basisnummern, lokale,
                                                     teile, glatt)
        return cls._fein[schluessel]

    @classmethod
    def _rechnen(cls, basisnummern, lokale, teile, glatt):
        matrix = cls._matrix(basisnummern)
        if glatt:
            glaettung = Mhglaettung.holen('+'.join(teile), lokale)
            matrix = np.asarray(glaettung.verteilen(matrix),
                                dtype=np.float64)
        return cls._vier(matrix)

    @classmethod
    def fuer_kleidung(cls, v_indizes, anteile):
        u"""``(index, gewicht)`` je Stoffpunkt aus seiner `.mhclo`-Zuordnung.

        WARUM (Edgar, 07.09.2026: „Kleider werden nicht gerigged bei
        MakeHuman"): Eine `.mhclo` haengt jeden Stoffpunkt an DREI
        Koerperpunkte::

            Punkt = w1·K[v1] + w2·K[v2] + w3·K[v3] + Versatz

        Dieselbe Rechnung gilt fuer die Gewichte. Es wird also nichts
        genaehert und nichts gesucht — der Stoff bekommt genau die Knochen
        des Koerpers, an dem er ohnehin haengt. Das ist der Unterschied zum
        GarmentCode-Weg, wo ueber das naechste Dreieck projiziert werden
        muss, weil es keine Zuordnung gibt.

        @param v_indizes (N, 3) Punktnummern des VOLLEN Basisnetzes
        @param anteile   (N, 3) ihre Gewichte
        """
        grund = cls.grundmatrix()
        v = np.clip(np.asarray(v_indizes, dtype=np.int64), 0, len(grund) - 1)
        a = np.asarray(anteile, dtype=np.float64)
        matrix = (grund[v[:, 0]] * a[:, 0:1] + grund[v[:, 1]] * a[:, 1:2]
                  + grund[v[:, 2]] * a[:, 2:3])
        return cls._vier(matrix)

    _grund = None

    @classmethod
    def grundmatrix(cls):
        u"""(19158, K) — je Punkt des VOLLEN Basisnetzes und Knochen ein Anteil.

        Einmal je Prozess: Die Gewichte stehen je Vertexnummer und aendern
        sich durch keinen Modellierregler.
        """
        if cls._grund is None:
            with cls._schloss:
                if cls._grund is None:
                    from .mhbasisnetz import Mhbasisnetz
                    anzahl = len(Mhbasisnetz.holen().punkte)
                    cls._grund = cls._matrix(np.arange(anzahl))
        return cls._grund

    @classmethod
    def _matrix(cls, basisnummern):
        u"""(P, K) — je Anzeigepunkt und Knochen ein Anteil."""
        namen = cls.knochennamen()
        rueck = np.full(int(np.max(basisnummern)) + 1, -1, dtype=np.int64)
        rueck[np.asarray(basisnummern, dtype=np.int64)] = np.arange(
            len(basisnummern))
        matrix = np.zeros((len(basisnummern), len(namen)), dtype=np.float64)
        for spalte, name in enumerate(namen):
            eintraege = cls.roh().get(name)   # 24 Dreh- und Hilfsknochen fuehren keine
            if not eintraege:
                continue
            nummern = np.asarray([e[0] for e in eintraege], dtype=np.int64)
            werte = np.asarray([e[1] for e in eintraege], dtype=np.float64)
            # Ein Knochen kann Punkte nennen, die diese Auswahl gar nicht
            # zeigt (Helfergeometrie abgeschaltet). Sie fallen weg, statt
            # ausserhalb des Feldes zu schreiben.
            gilt = (nummern < len(rueck))
            nummern, werte = nummern[gilt], werte[gilt]
            ziel = rueck[nummern]
            gilt = ziel >= 0
            np.add.at(matrix, (ziel[gilt], spalte), werte[gilt])
        return matrix

    @classmethod
    def _vier(cls, matrix):
        u"""Die vier staerksten Knochen je Punkt, auf Summe 1 gebracht.

        Ein Punkt ohne jedes Gewicht bekommt die WURZEL — sonst haenge er
        mit 0/0 im Nichts und bliebe beim Abspielen stehen, waehrend die
        Figur davonlaeuft. Das trifft die Helfergeometrie und die
        Gelenkwuerfel, fuer die `default_weights.mhw` nichts fuehrt.
        """
        index = np.argpartition(-matrix, cls.JE_PUNKT - 1,
                                axis=1)[:, :cls.JE_PUNKT]
        gewicht = np.take_along_axis(matrix, index, axis=1)
        summe = gewicht.sum(axis=1, keepdims=True)
        leer = summe[:, 0] <= 1e-9
        if leer.any():
            wurzel = cls._wurzelspalte()
            index[leer] = wurzel
            gewicht[leer] = 0.0
            gewicht[leer, 0] = 1.0
            summe[leer] = 1.0
            logger.debug('MakeHuman: %d Punkte ohne Hautgewicht — an die '
                         'Wurzel gehaengt', int(leer.sum()))
        return index.astype(np.int32), (gewicht / summe).astype(np.float32)

    @classmethod
    def _wurzelspalte(cls):
        namen = cls.knochennamen()
        return namen.index('root') if 'root' in namen else 0
