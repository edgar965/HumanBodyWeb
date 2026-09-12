# -*- coding: utf-8 -*-
u"""Effektlauf — den Blender-Prozess eines Effektauftrags fahren und beobachten.

Wie `Smpllauf`: Der Prozess schreibt in eine DATEI neben der Ausgabe (kein
Rohr — ein Lauf ueberlebt so den Neustart des Entwicklungsservers), der
`Effektbeobachter` liest daraus den Fortschritt (`n / N`), und
`LaufendeProzesse` kennt den Prozess fuers Anhalten.

Es laeuft immer nur EIN Effektauftrag: Blender rechnet Stoff auf allen
Kernen; zwei Laeufe waeren beide doppelt so langsam (12.09.2026).
"""
import json
import logging
import os
import subprocess
import threading
from pathlib import Path

from django.db import connection
from django.utils import timezone

from ..dienste.laufende_prozesse import LaufendeProzesse
from ..models import Effektauftrag
from .effektbefehl import Effektbefehl
from .effektbeobachter import Effektbeobachter

logger = logging.getLogger('core')

__all__ = ['Effektlauf']


class Effektlauf:

    ENDE_S = 120
    FEHLERZEILEN = 25

    def __init__(self, auftrag):
        self.auftrag = auftrag
        self.ausgabe = Path(auftrag.ausgabe)
        self.logdatei = self.ausgabe.with_suffix('.log')

    # ------------------------------------------------------------- Sperre

    @staticmethod
    def laufender(ausser=None):
        frage = Effektauftrag.objects.filter(status__in=Effektauftrag.LAEUFT)
        if ausser is not None:
            frage = frage.exclude(id=ausser)
        return frage.first()

    @classmethod
    def verwaiste_aufraeumen(cls):
        u"""Nach einem Serverneustart: lebt der Blender-Prozess noch, wird er
        wieder beobachtet (der Faden starb mit dem Server, der Prozess nicht);
        ist er weg, entscheiden Video und Bericht: da -> fertig, sonst
        gescheitert."""
        from ..pipelines.prozesspruefung import Prozesspruefung
        for auftrag in Effektauftrag.objects.filter(status__in=Effektauftrag.LAEUFT):
            if LaufendeProzesse.holen(auftrag.id) is not None:
                continue
            if auftrag.pid and Prozesspruefung.lebt(auftrag.pid):
                if str(auftrag.id) not in cls._beobachtet:
                    cls._beobachtet.add(str(auftrag.id))
                    threading.Thread(target=cls._sicher_wieder, args=(auftrag.id,),
                                     daemon=True).start()
                continue
            # Prozess weg: Sind Video und Bericht da, war er fertig — sonst
            # ist er ohne Zeugen gestorben.
            cls(auftrag).abschliessen_ohne_prozess()

    #: Auftraege, die nach einem Neustart schon wieder einen Faden haben.
    _beobachtet = set()

    @classmethod
    def _sicher_wieder(cls, auftrag_id):
        try:
            cls(Effektauftrag.objects.get(id=auftrag_id)).wieder_verfolgen()
        except Exception:
            logger.exception('Effektauftrag %s: Wiederaufnahme abgestürzt', auftrag_id)
            cls._absturz_vermerken(auftrag_id)
        finally:
            cls._beobachtet.discard(str(auftrag_id))
            connection.close()

    def wieder_verfolgen(self):
        u"""Ohne Prozessgriff: Ende ueber die PID, Erfolg ueber die Dateien."""
        Effektbeobachter(self.auftrag, str(self.logdatei),
                         Effektbefehl(self.auftrag).bilder(),
                         pid=self.auftrag.pid).verfolgen()
        self.abschliessen_ohne_prozess()

    def abschliessen_ohne_prozess(self):
        fertig = (self.ausgabe.is_file()
                  and self.ausgabe.with_suffix('.json').is_file())
        self._abschliessen(0 if fertig else 'unbekannt (Prozess nicht mehr vorhanden)')

    # -------------------------------------------------------------- Start

    @classmethod
    def starten(cls, auftrag):
        auftrag.status = 'running'
        auftrag.progress = 0
        auftrag.progress_detail = 'Blender startet …'
        auftrag.error_message = ''
        auftrag.started_at = timezone.now()
        auftrag.finished_at = None
        auftrag.save()
        threading.Thread(target=cls._sicher, args=(auftrag.id,), daemon=True).start()

    @classmethod
    def _sicher(cls, auftrag_id):
        try:
            cls(Effektauftrag.objects.get(id=auftrag_id)).fahren()
        except Exception:
            logger.exception('Effektauftrag %s: Faden abgestürzt', auftrag_id)
            cls._absturz_vermerken(auftrag_id)
        finally:
            connection.close()

    @staticmethod
    def _absturz_vermerken(auftrag_id):
        import traceback
        try:
            auftrag = Effektauftrag.objects.get(id=auftrag_id)
            auftrag.status = 'failed'
            auftrag.error_message = ('Unerwarteter Fehler:\n'
                                     + traceback.format_exc())[:4000]
            auftrag.finished_at = timezone.now()
            auftrag.save()
        except Exception:
            logger.warning('Fehlermeldung nicht speicherbar', exc_info=True)

    # -------------------------------------------------------------- Lauf

    def fahren(self):
        self.ausgabe.parent.mkdir(parents=True, exist_ok=True)
        befehl = Effektbefehl(self.auftrag)
        self.auftrag.log_pfad = str(self.logdatei)
        self.auftrag.save(update_fields=['log_pfad'])
        prozess, protokoll = self._starten(befehl.bauen())
        try:
            Effektbeobachter(self.auftrag, str(self.logdatei), befehl.bilder(),
                             proc=prozess).verfolgen()
        finally:
            protokoll.close()
        prozess.wait(timeout=self.ENDE_S)
        LaufendeProzesse.entfernen(self.auftrag.id)
        self._abschliessen(prozess.returncode)

    def _starten(self, befehl):
        protokoll = open(self.logdatei, 'w', encoding='utf-8')
        try:
            prozess = subprocess.Popen(befehl, stdout=protokoll,
                                       stderr=subprocess.STDOUT,
                                       cwd=str(self.ausgabe.parent))
        except Exception:
            protokoll.close()
            raise
        self.auftrag.pid = prozess.pid
        self.auftrag.save(update_fields=['pid'])
        LaufendeProzesse.eintragen(self.auftrag.id, prozess)
        return prozess, protokoll

    def _abschliessen(self, code):
        self.auftrag.refresh_from_db()
        if self.auftrag.status == 'cancelled':
            return
        if code == 0 and self.ausgabe.is_file():
            self.auftrag.status = 'complete'
            self.auftrag.progress = 100
            self.auftrag.progress_detail = 'Fertig'
            self.auftrag.bericht = self._bericht()
        else:
            self.auftrag.status = 'failed'
            self.auftrag.error_message = ('Blender endete mit Code %s\n%s'
                                          % (code, self._logauszug()))
        self.auftrag.finished_at = timezone.now()
        self.auftrag.pid = None
        self.auftrag.save()

    def _bericht(self):
        datei = self.ausgabe.with_suffix('.json')
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Effektbericht %s nicht lesbar', datei, exc_info=True)
            return {}

    def _logauszug(self):
        try:
            zeilen = self.logdatei.read_text(encoding='utf-8',
                                             errors='replace').splitlines()
        except OSError:
            return ''
        wichtig = [z for z in zeilen if not z.startswith('[MB-Lab')
                   and 'addon_updater' not in z and z.strip()]
        return '\n'.join(wichtig[-self.FEHLERZEILEN:])

    # ------------------------------------------------------------ Abbruch

    @staticmethod
    def anhalten(auftrag):
        LaufendeProzesse.beenden(auftrag.id)
        auftrag.status = 'cancelled'
        auftrag.progress_detail = 'Abgebrochen'
        auftrag.finished_at = timezone.now()
        auftrag.pid = None
        auftrag.save()
        return auftrag
