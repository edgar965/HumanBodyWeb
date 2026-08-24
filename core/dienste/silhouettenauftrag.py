# -*- coding: utf-8 -*-
"""Silhouettenauftrag — die Umrisse zu einem Fotoauftrag zusammensetzen.

Herausgelöst aus `api/fotoabgleich.photo_silhouette_data` (74 Zeilen, nach einem
ersten Umbau von 338). Übrig geblieben war ein Endpunkt, der immer noch fünf
Bausteine in der richtigen Reihenfolge bediente: Netz erzeugen, projizieren,
Körperumriss abnehmen, Gesicht auf drei Wegen suchen, Vorschau schreiben.

DIE DREI WEGE ZUM GESICHT (Reihenfolge zählt)
=============================================
1. **SMPL-X-Punkte** — genau, wenn die Pose stimmt.
2. **MediaPipe auf dem Foto** — findet das echte Gesicht im Bild, auch wenn die
   Pose daneben liegt.
3. **Kopfbereich schätzen** — der Rückfall, damit der Assistent überhaupt etwas
   zeigt.

Weg 2 wird auch dann gefahren, wenn Weg 1 etwas geliefert hat: Er ist im Bild
gemessen und deshalb näher an dem, was der Nutzer sieht. Nur wenn BEIDE nichts
haben, wird geschätzt.
"""

import json
import logging
import os

from django.conf import settings

from .gesichtskontur import Gesichtskontur
from .silhouette import Silhouette
from .silhouettenvorschau import Silhouettenvorschau
from ..daten.silhouettenergebnis import Silhouettenergebnis
from .smplxnetz import SmplxNetz, SmplxNetzFehler

logger = logging.getLogger(__name__)


class Fotofehler(Exception):
    """Ein Grund, mit einem Statuscode abzubrechen (`code`, Text)."""

    def __init__(self, text, code=500):
        super().__init__(text)
        self.code = code


class Silhouettenauftrag:
    """Baut aus einem `PhotoAnalysisJob` die Umriss-Antwort für den Assistenten."""

    def __init__(self, job, posierte_punkte):
        self.job = job
        #: Aufrufbar `(job_id, daten, breite, hoehe) -> (punkte, anzahl) | None`.
        #: Als Parameter, damit diese Klasse die Pipeline-Datei nicht kennt.
        self.posierte_punkte = posierte_punkte
        self.daten = self._daten()

    def _daten(self):
        try:
            return json.loads(self.job.result_json)
        except (json.JSONDecodeError, TypeError) as fehler:
            logger.exception('Silhouettenauftrag: result_json unlesbar')
            raise Fotofehler('Invalid result data', 500) from fehler

    # ------------------------------------------------------------------- Foto

    def foto(self, cv2):
        pfad = os.path.join(str(settings.BASE_DIR), self.job.photo_file)
        if not os.path.isfile(pfad):
            raise Fotofehler('Photo not found', 404)
        bild = cv2.imread(pfad)
        if bild is None:
            raise Fotofehler('Could not read photo', 500)
        return bild

    def netz(self):
        try:
            return SmplxNetz.erzeugen(self.daten.get('betas', [0.0] * 10),
                                      self.daten.get('gender', 'neutral'))
        except SmplxNetzFehler as fehler:
            logger.exception('Silhouettenauftrag: SmplxNetzFehler')
            raise Fotofehler(str(fehler), 500) from fehler

    # ---------------------------------------------------------------- Ergebnis

    def ergebnis(self, cv2):
        """Das Wörterbuch für den Assistenten — oder `Fotofehler`."""
        foto = self.foto(cv2)
        hoehe, breite = foto.shape[:2]
        punkte, flaechen, _netz = self.netz()
        silhouette = self._silhouette(punkte, flaechen, breite, hoehe)
        ergebnis = self._umrisse(silhouette, cv2, breite, hoehe)
        self._gesicht(ergebnis, silhouette, foto, cv2, breite, hoehe)
        self._vorschau(cv2, foto, ergebnis)
        ergebnis.bearbeitete_konturen_uebernehmen()
        return ergebnis.als_dict()

    def _silhouette(self, punkte, flaechen, breite, hoehe):
        """Projizieren — mit der gespeicherten Pose, sonst orthographisch."""
        ausrichtung = self.daten.get('alignment_data') or {}
        silhouette = Silhouette(punkte, flaechen, breite, hoehe)
        posiert = self.posierte_punkte(self.job.id, self.daten, breite, hoehe)
        if posiert is not None:
            stellen, anzahl = posiert
            silhouette.anzahl_posiert = anzahl
            silhouette.posierte_projektion(stellen,
                                           ausrichtung.get('proj_2d_offset'))
        else:
            silhouette.orthographische_projektion(
                ausrichtung.get('body_transform'))
        return silhouette

    def _umrisse(self, silhouette, cv2, breite, hoehe):
        ergebnis = Silhouettenergebnis(breite, hoehe)
        ergebnis.ausrichtung = self.daten.get('alignment_data')
        ergebnis.posiert = silhouette.posiert
        ergebnis.koerperkontur = silhouette.koerperkontur(cv2)
        ergebnis.netz_rahmen = silhouette.netz_rahmen()
        ergebnis.yolo_rahmen = self.daten.get('bbox_xyxy')
        return ergebnis

    @staticmethod
    def _gesicht(ergebnis, silhouette, foto, cv2, breite, hoehe):
        """Die drei Wege zum Gesicht — siehe Modul-Docstring."""
        gesicht = Gesichtskontur(silhouette.projektion, breite, hoehe)
        gesicht.aus_smplx_vertices(silhouette.anzahl_posiert)
        if not gesicht.aus_mediapipe(foto, cv2) and not gesicht.kontur:
            gesicht.aus_kopfbereich()
        ergebnis.gesichtskontur = gesicht.kontur
        ergebnis.gesichtsrahmen_netz = gesicht.rahmen_netz
        ergebnis.gesichtsrahmen_erkannt = (gesicht.rahmen_erkannt
                                           or gesicht.rahmen_netz)
        ergebnis.aus_smplx = gesicht.aus_smplx

    def _vorschau(self, cv2, foto, ergebnis):
        """Vorschaubild schreiben und den Pfad im Auftrag vermerken.

        Der Pfad steht im `result_json`, damit die Seite das Bild ohne zweiten
        Aufruf zeigen kann.
        """
        pfad = Silhouettenvorschau.speichern(cv2, foto, ergebnis.koerperkontur,
                                             ergebnis.gesichtskontur,
                                             self.job.id)
        if not pfad:
            return
        self.daten['silhouette_path'] = pfad
        self.job.result_json = json.dumps(self.daten, default=str)
        self.job.save(update_fields=['result_json'])
