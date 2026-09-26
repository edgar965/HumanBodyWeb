# -*- coding: utf-8 -*-
"""Meshlauf — ein Mesh-Auftrag von den Fotos bis zum GLB (läuft in `mesh_fahren`).

Die Rechnung selbst steht in `VideoToBVH/wrappers/_run_mesh.py` (Umgebung
`settings.MESH_PYTHON`, eigene venv für TRELLIS.2/Hunyuan3D): EIN Prozess für alle
Schritte, damit die Modelle einmal geladen werden (TRELLIS.2 4B + DINOv3 belegen die
Karte). Hier nur: Auftragsbeschreibung schreiben, Zeilen des Runners deuten,
Fortschritt und Ergebnis in die Datenbank.

Zeilen des Runners (stdout, je eine Zeile):
    [fortschritt] <0..100> <Text>     Balken des Auftrags (Bänder je Schritt macht der Runner)
    [schritt] <name>                  aktueller Schritt (`SCHRITTE`)
    [bild] {"datei": …, …}             Befund der Vorbereitung je Foto (Rolle, Maske, Kasten)
    [ergebnis] {…}                     am Ende: Dateien, Zahlen, Dauer je Schritt
Alles andere ist Ausgabe der Bibliotheken und landet nur im Log.
"""

import json
import logging
import os
import time

from django.conf import settings
from django.utils import timezone

from ..daten.meshablage import Meshablage
from ..daten.wrapperpfad import Wrapperpfad
from ..models import Meshauftrag
from ..pipeline_process import PipelineProzess, PipelineStille
from .meshoptionen import Meshoptionen

logger = logging.getLogger('core')

__all__ = ['Meshlauf']


class Meshlauf:
    SCHRITTE = ('vorbereitung', 'form', 'gesicht', 'textur', 'export')
    RUNNER = '_run_mesh.py'
    #: So lange darf der Runner schweigen: Laden von TRELLIS.2 (16 GB) und die
    #: 1536³-Dekodierung geben minutenlang keine Zeile aus.
    STILLE_S = 1800

    def __init__(self, job_id):
        self.job = Meshauftrag.objects.get(pk=job_id)
        self.ablage = Meshablage(self.job.kennung)
        self._ergebnis = None
        self._letzte_db = 0.0

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self, ab=None):
        job = self.job
        self.ablage.anlegen()
        auftrag = self.ablage.unter(Meshablage.ARBEIT) / 'auftrag.json'
        auftrag.write_text(json.dumps(self.beschreibung(ab), ensure_ascii=False, indent=1), encoding='utf-8')
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        pp = PipelineProzess.starten([settings.MESH_PYTHON, runner, str(auftrag)], cwd=Wrapperpfad.pfad(),
                                     env_extra=self.umgebung())
        logger.info('Mesh %s: Runner %s gestartet (%s)', job.kennung, pp.proc.pid, job.optionen.get('formmodell'))
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                self._zeile(zeile.rstrip('\n'))
                if self._angehalten():
                    pp.beenden()
                    return
        except PipelineStille as fehler:
            self._scheitern(str(fehler))
            return
        rc = pp.warten(timeout=120)
        if rc != 0 or self._ergebnis is None:
            self._scheitern('Runner endete mit %s: %s' % (rc, pp.fehlertext(1500) or 'ohne Meldung'))
            return
        job.refresh_from_db()
        job.ergebnis = self._ergebnis
        job.status = 'fertig'
        job.progress = 100
        job.progress_detail = 'Fertig'
        job.finished_at = timezone.now()
        job.save(update_fields=['ergebnis', 'status', 'progress', 'progress_detail', 'finished_at', 'updated_at'])
        logger.info('Mesh %s: fertig (%s Flächen)', job.kennung, self._ergebnis.get('flaechen'))

    def beschreibung(self, ab=None):
        """Was der Runner rechnen soll — Pfade, Rollen, Optionen (JSON-Datei)."""
        job = self.job
        optionen = Meshoptionen.pruefen(job.optionen)
        bilder = []
        for name in self.ablage.eingaenge():
            eintrag = job.bild(name) or {}
            bilder.append({'datei': name, 'pfad': str(self.ablage.unter(Meshablage.EINGANG) / name),
                           'rolle': Meshoptionen.rolle_pruefen(eintrag.get('rolle'))})
        return {
            'kennung': job.kennung,
            'name': job.name,
            'ab': ab,
            'optionen': optionen,
            'bilder': bilder,
            'ordner': {n: str(self.ablage.unter(n)) for n in (Meshablage.VORBEREITET, Meshablage.ARBEIT,
                                                              Meshablage.ERGEBNIS)},
            'wurzeln': {'videotobvh': str(settings.VIDEOTOBVH_ROOT)},
        }

    def umgebung(self):
        """HF-Ablage auf A:, Zwischendateien im Auftrag (nie System-Temp), xformers für die
        Sparse-Attention von TRELLIS.2 (kein flash-attn unter Windows/sm_120)."""
        tmp = self.ablage.unter(Meshablage.ARBEIT) / 'tmp'
        tmp.mkdir(parents=True, exist_ok=True)
        return {
            'HF_HOME': str(settings.HF_HOME_DIR),
            'HF_HUB_OFFLINE': '1',
            'TORCH_HOME': str(settings.VIDEOTOBVH_ROOT / 'models' / 'torch_hub'),
            'ATTN_BACKEND': 'xformers',
            'SPARSE_ATTN_BACKEND': 'xformers',
            'PYTORCH_CUDA_ALLOC_CONF': 'expandable_segments:True',
            'OPENCV_IO_ENABLE_OPENEXR': '1',
            'TMP': str(tmp),
            'TEMP': str(tmp),
        }

    # --------------------------------------------------------------- Zeilen

    def _zeile(self, zeile):
        if zeile.startswith('[fortschritt] '):
            teile = zeile[len('[fortschritt] '):].split(' ', 1)
            try:
                wert = max(0, min(99, int(float(teile[0]))))
            except ValueError:
                return
            self._melden(wert, teile[1] if len(teile) > 1 else '')
        elif zeile.startswith('[schritt] '):
            self.job.schritt = zeile[len('[schritt] '):].strip()[:30]
            self.job.save(update_fields=['schritt', 'updated_at'])
        elif zeile.startswith('[bild] '):
            self._bild(zeile[len('[bild] '):])
        elif zeile.startswith('[ergebnis] '):
            try:
                self._ergebnis = json.loads(zeile[len('[ergebnis] '):])
            except ValueError:
                logger.error('Mesh %s: Ergebniszeile nicht lesbar: %.200s', self.job.kennung, zeile)

    def _melden(self, wert, text):
        """Fortschritt — höchstens zweimal je Sekunde in die Datenbank, der Balken geht nie zurück."""
        jetzt = time.monotonic()
        if jetzt - self._letzte_db < 0.5 and wert < 99:
            return
        self._letzte_db = jetzt
        job = self.job
        job.progress = max(job.progress or 0, wert)
        job.progress_detail = text[:200]
        job.save(update_fields=['progress', 'progress_detail', 'updated_at'])

    def _bild(self, roh):
        try:
            befund = json.loads(roh)
        except ValueError:
            return
        job = self.job
        job.refresh_from_db(fields=['bilder'])
        eintraege = list(job.bilder or [])
        for e in eintraege:
            if e.get('datei') == befund.get('datei'):
                e.update({k: v for k, v in befund.items() if k != 'rolle'})
                e['erkannt'] = befund.get('rolle')
                break
        else:
            eintraege.append({**{k: v for k, v in befund.items() if k != 'rolle'}, 'erkannt': befund.get('rolle'),
                              'rolle': 'auto'})
        job.bilder = eintraege
        job.bilder_sichern()

    def _angehalten(self):
        return Meshauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists()

    def _scheitern(self, text):
        job = self.job
        job.refresh_from_db()
        if job.status == 'angehalten':
            return
        job.status = 'gescheitert'
        job.error_message = text[:4000]
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at', 'updated_at'])
        logger.error('Mesh %s: gescheitert — %s', job.kennung, text[:500])
