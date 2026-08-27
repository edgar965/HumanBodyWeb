# -*- coding: utf-8 -*-
"""Auftragssteuerung: starten, anhalten, Dateien wegraeumen.

WARUM (Umbau 16.08.2026): Das Anhalten stand ZWEIMAL in core/api/auftraege.py —
einmal in `stop_processing` (Formular, 68 Zeilen) und einmal in
`api_stop_processing` (AJAX, 44 Zeilen). Beide schrieben dieselben Stoppmarken,
beendeten dieselben Teilprozesse, warteten dieselben 30 Sekunden auf v4 und
setzten denselben Fehlertext. Unterschiedlich waren nur die Antwort (Umleitung
oder JSON) und eine Protokollzeile.

Zwei Fassungen desselben Abbruchs sind gefaehrlich: Wer eine Pipeline ergaenzt,
aendert die eine und uebersieht die andere — dann laesst sich ein Auftrag ueber
die Oberflaeche sauber abbrechen, ueber das Formular aber nicht.
"""

import logging
import os
import shutil
import subprocess
import threading
from pathlib import Path

from django.conf import settings

from ..dienste.haenger import Haenger
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..pipelines.prozesspruefung import Prozesspruefung
from ..pipelines.videolaenge import Videolaenge

logger = logging.getLogger('core')
pipeline_logger = logging.getLogger('core.pipeline')

#: Sekunden, die v4 zum geordneten Beenden bekommt. Das Skript prueft die
#: Stoppmarke je Bild und schreibt danach ein Teilergebnis.
V4_GEDULD = 30

#: Sekunden nach einem harten Beenden, bevor aufgegeben wird.
KILL_GEDULD = 5


class Auftragssteuerung:
    """Ein laufender Auftrag und was man mit ihm tun kann."""

    @staticmethod
    def _ausgabeordner(job):
        return Path(settings.MEDIA_ROOT) / 'output' / str(job.id)

    # ------------------------------------------------------------------ Start

    #: Zustaende, aus denen ein Auftrag gestartet werden darf.
    STARTBAR = ('pending', 'complete', 'failed')

    @staticmethod
    def _beanspruchen(job, zustand):
        """Den Auftrag in EINEM Schritt auf „laeuft" setzen.

        Zwei Startanfragen kurz hintereinander (Doppelklick, zwei Reiter) lasen
        beide „complete", und beide warfen einen Hintergrundfaden an: doppelte
        Last auf der Grafikkarte, und wer die Ergebnisdatei schreibt, ist Zufall.
        Ein bedingtes UPDATE laesst nur EINEN gewinnen — die Datenbank
        entscheidet, nicht die Reihenfolge im Prozess.
        (Sparring mit Nemotron, 18.08.2026.)
        """
        geaendert = type(job).objects.filter(
            id=job.id, status__in=Auftragssteuerung.STARTBAR).update(status=zustand)
        if not geaendert:
            pipeline_logger.info('start_processing: Auftrag %s laeuft bereits '
                                 '— zweiter Start uebergangen', job.id)
        return bool(geaendert)

    @staticmethod
    def starten(job):
        """Zustand zuruecksetzen und den Verarbeitungsfaden anwerfen.

        Liefert `False`, wenn der Auftrag schon laeuft (siehe `_beanspruchen`).
        """
        zustand = Auftragssteuerung._anfangszustand(job.pipeline)
        if not Auftragssteuerung._beanspruchen(job, zustand):
            return False
        job.status = zustand
        job.progress = 0
        job.error_message = ''
        job.bvh_file = ''
        job.bvh_file_face = ''
        bilder = Videolaenge.bilder(
            Path(settings.MEDIA_ROOT) / str(job.video_file))
        job.progress_detail = f'0 / {bilder} frames' if bilder else 'Starting...'
        job.save()
        Auftragssteuerung._faden_starten(str(job.id))
        return True

    @staticmethod
    def _anfangszustand(pipeline):
        if pipeline == 'v4':
            return 'v4_processing'
        if pipeline in ('gvhmr', 'wham', 'prompthmr') or pipeline.startswith('hybrid_'):
            return 'processing'
        if pipeline in ('rtmpose', 'vitpose', 'yolo11'):
            return 'detecting_2d'
        return pipeline

    @staticmethod
    def _faden_starten(job_id):
        """Hintergrundfaden mit Absturzsicherung."""
        from ..pipelines.auftragslauf import Auftragslauf

        def _sicher(jid):
            try:
                Auftragslauf(jid).ausfuehren()
            except Exception:
                logger.exception('Auftrag %s: Hintergrundfaden abgestürzt', jid)
                Auftragssteuerung._absturz_vermerken(jid)

        threading.Thread(target=_sicher, args=(job_id,), daemon=True).start()

    @staticmethod
    def _absturz_vermerken(jid):
        """Unerwarteten Fehler am Auftrag festhalten, statt den Server zu reissen."""
        try:
            import traceback
            from django.apps import apps
            job = apps.get_model('core', 'BVHJob').objects.get(id=jid)
            if job.status != 'failed':
                job.status = 'failed'
                job.error_message = ('Unexpected crash:\n'
                                     + traceback.format_exc())[:4000]
                job.save()
        except Exception:
            logger.warning('Fehlermeldung des Jobs konnte nicht gespeichert werden '
                           '— Ursache nur im Protokoll', exc_info=True)

    # ----------------------------------------------------------------- Abbruch

    @staticmethod
    def anhalten(job, herkunft='api'):
        """Laufenden Auftrag abbrechen.

        Fuer ALLE Pipelines wird eine Stoppmarke geschrieben. v4 prueft sie je
        Bild und beendet sich selbst; die 2D-Pipelines wissen nichts davon, also
        wird der Unterprozess hart beendet — der Hintergrundfaden sieht die
        Marke und rechnet mit den Teildaten weiter.
        """
        jid = str(job.id)
        pipeline_logger.info('stop_processing (%s) job=%s pipeline=%s',
                             herkunft, jid, job.pipeline)
        ordner = Auftragssteuerung._ausgabeordner(job)
        Auftragssteuerung._stoppmarken_schreiben(job, ordner)

        prozess = LaufendeProzesse.holen(jid)
        if job.pipeline.startswith('hybrid_'):
            Auftragssteuerung._teilprozesse_beenden(jid, ordner)
            return                       # Endzustand setzt der Hintergrundfaden
        if prozess and prozess.poll() is None:
            Auftragssteuerung._prozess_beenden(prozess, job.pipeline)
            LaufendeProzesse.entfernen(jid)
            return                       # dito
        # Kein bekannter Prozess — nach Serverneustart verwaister Lauf.
        Auftragssteuerung._per_pid_beenden(ordner)
        LaufendeProzesse.entfernen(jid)
        Auftragssteuerung._als_abgebrochen(job)

    @staticmethod
    def _als_abgebrochen(job):
        """Auf `failed` setzen — aber NUR, wenn er ueberhaupt noch laeuft.

        Zwischen dem Klick des Nutzers und dieser Zeile kann der Lauf von selbst
        fertig geworden sein: Der Hintergrundfaden schreibt dann `complete` samt
        Ergebnisdatei, und wir wuerden das mit „Cancelled by user" ueberschreiben
        — das Ergebnis waere in der Oberflaeche verloren, obwohl die BVH-Datei
        auf der Platte liegt. Der Auftrag wird DESHALB frisch aus der Datenbank
        gelesen; das Objekt in der Hand ist so alt wie die Anfrage.
        (Sparring mit Nemotron, 18.08.2026.)
        """
        frisch = type(job).objects.filter(id=job.id).first()
        if frisch is None or frisch.status not in Haenger.ARBEITET:
            pipeline_logger.info(
                'stop_processing: Auftrag %s steht auf "%s" — nicht mehr '
                'laufend, Zustand bleibt', job.id,
                frisch.status if frisch else 'geloescht')
            return
        frisch.status = 'failed'
        frisch.error_message = 'Cancelled by user'
        frisch.save(update_fields=['status', 'error_message'])
        job.status, job.error_message = frisch.status, frisch.error_message

    @staticmethod
    def _prozess_beenden(prozess, pipeline):
        if pipeline == 'v4':
            try:
                prozess.wait(timeout=V4_GEDULD)
                return
            # stumm gewollt: Die Geduldsfrist ist abgelaufen, jetzt wird
            # hart beendet — die Zeile darunter IST die Behandlung.
            except subprocess.TimeoutExpired:
                pass
        prozess.kill()
        prozess.wait(timeout=KILL_GEDULD)

    @staticmethod
    def _teilprozesse_beenden(jid, ordner):
        """Hybridlaeufe haben je einen Prozess fuer Koerper und Gesicht."""
        for teil in ('body', 'face'):
            prozess = LaufendeProzesse.entfernen(f'{jid}_{teil}')
            if prozess and prozess.poll() is None:
                prozess.kill()
                try:
                    prozess.wait(timeout=KILL_GEDULD)
                except subprocess.TimeoutExpired:
                    logger.debug('uebergangen', exc_info=True)
            else:
                Auftragssteuerung._per_pid_beenden(ordner / teil)

    @staticmethod
    def _stoppmarken_schreiben(job, ordner):
        ziele = [ordner]
        if job.pipeline.startswith('hybrid_'):
            ziele += [ordner / 'body', ordner / 'face']
        for ziel in ziele:
            marke = ziel / 'STOP_FLAG'
            try:
                marke.parent.mkdir(parents=True, exist_ok=True)
                marke.write_text('stop')
            except OSError:
                logger.debug('uebergangen', exc_info=True)

    @staticmethod
    def _per_pid_beenden(ordner):
        """Verwaisten Prozess ueber seine PID-Datei beenden."""
        pid_datei = ordner / 'pipeline.pid'
        if not pid_datei.exists():
            return False
        try:
            pid = int(pid_datei.read_text().strip())
            if Prozesspruefung.lebt(pid):
                os.kill(pid, 9)
                return True
        except (ValueError, OSError, ProcessLookupError):
            logger.debug('uebergangen', exc_info=True)
        finally:
            try:
                pid_datei.unlink()
            except (FileNotFoundError, OSError):
                logger.debug('uebergangen', exc_info=True)
        return False

    # ----------------------------------------------------------------- Loeschen

    @staticmethod
    def dateien_entfernen(job):
        """Video, Ausgabeordner und BVH eines Auftrags loeschen."""
        if job.video_file:
            video = Path(settings.MEDIA_ROOT) / str(job.video_file)
            if video.exists():
                video.unlink()
        ordner = Auftragssteuerung._ausgabeordner(job)
        if ordner.exists():
            shutil.rmtree(ordner, ignore_errors=True)
        if job.bvh_file and os.path.exists(job.bvh_file):
            bvh = Path(job.bvh_file)
            # Liegt die BVH im Ausgabeordner, ist sie schon weg.
            if not str(bvh).startswith(str(ordner)):
                bvh.unlink(missing_ok=True)
