# -*- coding: utf-8 -*-
"""Netzanfrage — aus den Query-Parametern von `/api/character/mesh/` ein Netz.

Herausgelöst aus `api/netz.character_mesh` (141 Zeilen, Grenze 60). Die Ansicht
tat fünf Dinge hintereinander: Regler und Meta-Werte aus der Anfrage lesen, die
Punkte rechnen, wahlweise die T-Pose einsetzen, und die Antwort in zwei ganz
verschiedenen Fassungen bauen — mit Catmull-Clark-Unterteiler (der Normalfall)
oder ohne (Fallback für Netze, die keine Vierecke haben).

DER SPARSAME MODUS (`nur_punkte=1`)
===================================
Gemessen am 16.08.2026 mit dem weiblichen Grundkörper (70.851 Punkte):

    vollständig   5,24 MB   (vertices 1,13 + normals 1,13 + faces 2,21 + uvs 0,76)
    nur_punkte    2,26 MB   —  57 % weniger

Wer beim Ziehen eines Morph-Reglers neu lädt (`Charakterkoerper.neuLaden`),
verwirft Dreiecke und UVs ohnehin: Die Topologie ändert sich durch Morphs nicht,
nur die Punktlagen. `face_count` bleibt trotzdem drin — die Oberfläche zeigt die
Dreieckszahl auch ohne die Dreiecke.
"""

import logging
import os

import numpy as np
from django.conf import settings
from humanbody_core import CharacterState

from ..daten.materialgruppen import Materialgruppen
from ..daten.netzantwort import Netzantwort
from ..dienste.charakterdaten import Charakterdaten
from ..models import AppSettings

logger = logging.getLogger(__name__)


class Netzanfrage:
    """Eine Anfrage an `/api/character/mesh/` — Zustand, Punkte, Antwort."""

    #: Vorsätze der Query-Parameter und die Setzer dahinter.
    REGLER = (('morph_', 'set_morph'), ('meta_', 'set_meta'))
    #: Die Punktdatei der T-Pose (nur lesen — Produktivdaten).
    TPOSE = 'vertices_tpose.npy'

    def __init__(self, request):
        self.anfrage = request
        self.nur_punkte = request.GET.get('nur_punkte') == '1'
        self.bauart = request.GET.get('body_type', 'Female_Caucasian')
        self.geschlecht = Charakterdaten.geschlecht_zu(self.bauart)
        self.netz = Charakterdaten.netzdaten(self.geschlecht)

    # ------------------------------------------------------------- Rechnen

    def punkte(self):
        """Die Punktlagen zu dieser Anfrage — oder `None`, wenn es nicht geht."""
        zustand = CharacterState(Charakterdaten.morphdaten(),
                                 Charakterdaten.voreinstellungen())
        zustand.set_body_type(self.bauart)
        self._regler(zustand)
        punkte = zustand.compute()
        return None if punkte is None else self._pose(punkte)

    def _regler(self, zustand):
        """Morph- und Meta-Werte aus der Anfrage setzen.

        Ein unlesbarer Wert wird übergangen und protokolliert: Ein einzelner
        kaputter Regler darf nicht die ganze Figur kosten.
        """
        for vorsatz, methode in self.REGLER:
            setzen = getattr(zustand, methode)
            for name, wert in self.anfrage.GET.items():
                if not name.startswith(vorsatz):
                    continue
                try:
                    setzen(name[len(vorsatz):], float(wert))
                except (ValueError, AttributeError):
                    logger.debug('uebergangen', exc_info=True)

    def _pose(self, punkte):
        """T-Pose einsetzen, wenn sie gewünscht ist und die Datei passt."""
        if self._gewuenschte_pose() != 't_pose':
            return punkte
        pfad = os.path.join(str(settings.HUMANBODY_DATA_DIR), self.TPOSE)
        if not os.path.isfile(pfad):
            return punkte
        tpose = np.load(pfad)
        if tpose.shape != punkte.shape:
            # Andere Punktzahl heisst: andere Figur. Stillschweigend einsetzen
            # waere der Fall, der die Maennerfigur einmal zerstoert hat.
            logger.warning('[Mesh] %s passt nicht (%s statt %s) — A-Pose bleibt',
                           self.TPOSE, tpose.shape, punkte.shape)
            return punkte
        logger.info('[Mesh] Using T-pose vertices')
        return tpose

    def _gewuenschte_pose(self):
        pose = self.anfrage.GET.get('pose', '')
        if pose:
            return pose
        return (AppSettings.load().ui_prefs or {}).get('default_pose', 'a_pose')

    # ------------------------------------------------------------- Antworten

    def antwort(self, punkte):
        """Das Wörterbuch für den Browser — mit Unterteiler oder ohne."""
        unterteiler = Charakterdaten.unterteiler(self.geschlecht)
        if unterteiler is not None:
            return self._unterteilt(unterteiler, punkte)
        return self._grob(punkte)

    def _unterteilt(self, cc, punkte):
        """Der Normalfall: Catmull-Clark wie in Blender, glatte Normalen.

        Die Normalen kommen aus der VIERECK-Topologie (`compute_quad_normals`) —
        aus den Dreiecken gerechnet gäbe es sichtbare Kanten an den Diagonalen.
        """
        feine = cc.subdivide(punkte)
        weitere = {}
        if not self.nur_punkte:
            weitere = {'groups': cc.groups,
                       'material_names': self.netz.material_names or []}
            if cc.uvs is not None:
                weitere['uvs'] = cc.uvs
        antwort = Netzantwort.aus(
            feine, normals=cc.compute_quad_normals(feine),
            faces=None if self.nur_punkte else cc.triangles, **weitere)
        antwort['face_count'] = int(len(cc.triangles))
        return antwort

    def _grob(self, punkte):
        """Fallback ohne Unterteiler — Netze, die keine reinen Vierecke sind."""
        antwort = Netzantwort.aus(punkte)
        if self.netz.faces is not None and not self.nur_punkte:
            gruppen = Materialgruppen.aus_flaechen(
                self.netz.faces, self.netz.face_materials,
                self.netz.material_names)
            dreiecke = gruppen.sortiert()
            bereiche = gruppen.bereiche()
            if bereiche:
                antwort['groups'] = bereiche
                antwort['material_names'] = gruppen.namen
            antwort['face_count'] = int(dreiecke.shape[0])
            antwort['faces'] = Netzantwort.feld(dreiecke, 'faces')
        if self.netz.uvs is not None and not self.nur_punkte:
            antwort['uvs'] = Netzantwort.feld(self.netz.uvs, 'uvs')
        return antwort
