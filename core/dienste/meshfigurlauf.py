# -*- coding: utf-8 -*-
"""Meshfigurlauf — ein Auftrag „Mesh to 3D" vom Netz bis zur Genesis-Figur (läuft in `meshfigur_fahren`).

Zwei Welten wechseln sich ab: Die Registrierung rechnet auf der Karte in python10
(`VideoToBVH/wrappers/_run_meshfigur.py`, ein Schritt je Aufruf), Genesis 9 lebt hier in
python14 — zwischen den Runden wird die Figur ECHT nachgerechnet (Formelketten, Knochen-
skalierung, Gelenkkorrekturen), bevor die nächste Runde auf ihr aufsetzt.

    erkennung     Netz ausrichten, Landmarken (Körper 33, Gesicht 478), Übersichtsbilder, Vorlagebild
    kalibrierung  nur einmal je Rechner: Genesis durch denselben Detektor (`G9netzlandmarken`)
    koerper       Körperkette in Runden (`Meshfigurkette`), dazwischen ggf. auf „Körpergröße"
    gesicht       Gesichtskette (296 Kopfregler, 478 Gesichtspunkte)
    rest          Eigenmorph aus dem Rest (`Meshfigurende`)
    textur        Farbe des Netzes auf die Genesis-Kacheln (`Meshfigurende`)
    vorschau      Bilder, Abstände, Vergleich, Testfall (`Meshfigurvorschau`)
    speichern     Modell und Ablage in `output/Export/MeshTo3D` (`Meshfigurspeichern`)

Runner-Zeilen: `[fortschritt] <0..100> <Text>` (je Schritt auf sein Band umgerechnet),
`[ergebnis] {…}`, `[fehler] {…}`. Alles, was die Seite zeigt, steht in `job.ergebnis`.
"""

import json
import logging
import os
import time

from django.conf import settings
from django.utils import timezone

from ..daten.meshfigurablage import Meshfigurablage
from ..daten.wrapperpfad import Wrapperpfad
from ..models import Meshfigurauftrag
from ..pipeline_process import PipelineProzess, PipelineStille
from .meshfiguroptionen import Meshfiguroptionen

logger = logging.getLogger('core')

__all__ = ['Meshfigurlauf']


class Meshfigurlauf:
    SCHRITTE = ('erkennung', 'haar', 'kalibrierung', 'koerper', 'gesicht', 'rest', 'textur', 'vorschau',
                'speichern')
    BAENDER = {
        'erkennung': (0, 10),
        'haar': (10, 12),
        'kalibrierung': (12, 14),
        'koerper': (14, 62),
        'gesicht': (62, 80),
        'rest': (80, 85),
        'textur': (85, 92),
        'vorschau': (92, 97),
        'speichern': (97, 100),
    }
    RUNNER = '_run_meshfigur.py'
    #: So lange darf der Runner schweigen (Modelle laden, eine lange Stufe).
    STILLE_S = 900

    class Angehalten(Exception):
        """Der Nutzer hat angehalten — kein Fehler, der Lauf endet still."""

    def __init__(self, job_id):
        self.job = Meshfigurauftrag.objects.get(pk=job_id)
        self.ablage = Meshfigurablage(self.job.kennung)
        self.optionen = Meshfiguroptionen.pruefen(self.job.optionen)
        self.zusatz = {}
        self._band = (0, 100)
        self._letzte_db = 0.0

    # --------------------------------------------------------------- Ablauf

    def ausfuehren(self, ab=None):
        from .meshfigurende import Meshfigurende
        from .meshfigurhaar import Meshfigurhaar
        from .meshfigurkette import Meshfigurkette
        from .meshfigurspeichern import Meshfigurspeichern
        from .meshfigurvorschau import Meshfigurvorschau

        job = self.job
        self.ablage.anlegen()
        job.ergebnis = dict(job.ergebnis or {})
        start = self.SCHRITTE.index(ab) if ab in self.SCHRITTE else 0
        schritte = {
            'erkennung': self._erkennung,
            'haar': lambda: Meshfigurhaar(self).ausfuehren(),
            'kalibrierung': self._kalibrierung,
            'koerper': lambda: Meshfigurkette(self).koerper(),
            'gesicht': lambda: Meshfigurkette(self).gesicht(),
            'rest': lambda: Meshfigurende(self).rest(),
            'textur': lambda: Meshfigurende(self).textur(),
            'vorschau': lambda: Meshfigurvorschau(self).ausfuehren(),
            'speichern': lambda: Meshfigurspeichern(self).ausfuehren(),
        }
        t0 = time.perf_counter()
        try:
            for name in self.SCHRITTE[start:]:
                self._schritt(name)
                t = time.perf_counter()
                schritte[name]()
                job.ergebnis.setdefault('dauer', {})[name] = round(time.perf_counter() - t, 1)
                self.sichern('ergebnis')
        except self.Angehalten:
            logger.info('Mesh to 3D %s: angehalten', job.kennung)
            return
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler beendet den Lauf sichtbar
            logger.exception('Mesh to 3D %s: Schritt %s gescheitert', job.kennung, job.schritt)
            self._scheitern('%s: %s' % (job.schritt, fehler))
            return
        job.ergebnis['dauer_s'] = round(time.perf_counter() - t0, 1)
        job.status = 'fertig'
        job.progress = 100
        job.progress_detail = 'Fertig'
        job.finished_at = timezone.now()
        job.save(
            update_fields=['ergebnis', 'status', 'progress', 'progress_detail', 'finished_at', 'updated_at']
        )
        logger.info('Mesh to 3D %s: fertig in %.0f s', job.kennung, job.ergebnis['dauer_s'])

    def _schritt(self, name):
        if Meshfigurauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists():
            raise self.Angehalten()
        self._band = self.BAENDER[name]
        self.job.schritt = name
        self.job.save(update_fields=['schritt', 'updated_at'])
        self.melden(0, name)

    def sichern(self, *felder):
        self.job.save(update_fields=list(felder) + ['updated_at'])

    def melden(self, anteil, text):
        """Fortschritt im Band des Schritts — höchstens zweimal je Sekunde in die Datenbank."""
        jetzt = time.monotonic()
        if jetzt - self._letzte_db < 0.5 and anteil < 1.0:
            return
        self._letzte_db = jetzt
        von, bis = self._band
        self.job.progress = max(self.job.progress or 0, int(von + (bis - von) * max(0.0, min(1.0, anteil))))
        self.job.progress_detail = str(text)[:200]
        self.sichern('progress', 'progress_detail')

    # --------------------------------------------------------------- Runner

    def auftrag(self):
        """`arbeit/auftrag.json` — Netz, Ordner, Optionen und was die Schritte dazulegen."""
        pfad = self.ablage.arbeit('auftrag.json')
        netz = self.ablage.netzdatei()
        if netz is None:
            raise RuntimeError('Kein Netz im Eingang')
        daten = {
            'kennung': self.job.kennung,
            'name': self.job.name,
            'netz': str(netz),
            'optionen': dict(self.optionen, daempfung_wert=Meshfiguroptionen.daempfung(self.optionen)),
            'ordner': {'arbeit': str(self.ablage.arbeit()), 'ergebnis': str(self.ablage.ergebnis())},
            **self.zusatz,
        }
        kopf = self.ablage.netzdatei('kopf') if (self.job.eingang or {}).get('kopf') else None
        if kopf is not None:
            daten['kopfnetz'] = str(kopf)
        pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding='utf-8')
        return pfad

    def runner(self, schritt, runde=None, von=0.0, bis=1.0):
        """Einen Schritt des Runners rechnen — sein `[ergebnis]` (dict) oder ein Fehler."""
        befehl = [
            settings.PIPELINE_PYTHON,
            os.path.join(Wrapperpfad.pfad(), self.RUNNER),
            str(self.auftrag()),
            schritt,
        ]
        if runde is not None:
            befehl.append(str(runde))
        pp = PipelineProzess.starten(befehl, cwd=Wrapperpfad.pfad(), env_extra=self.umgebung())
        ergebnis, meldung = None, None
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                zeile = zeile.rstrip('\n')
                if zeile.startswith('[fortschritt] '):
                    teile = zeile[14:].split(' ', 1)
                    try:
                        wert = float(teile[0]) / 100.0
                    except ValueError:
                        continue
                    self.melden(von + (bis - von) * wert, teile[1] if len(teile) > 1 else schritt)
                elif zeile.startswith('[ergebnis] '):
                    ergebnis = json.loads(zeile[11:])
                elif zeile.startswith('[fehler] '):
                    meldung = json.loads(zeile[9:]).get('fehler')
                if Meshfigurauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists():
                    pp.beenden()
                    raise self.Angehalten()
        except PipelineStille as fehler:
            pp.beenden()
            raise RuntimeError('Runner schweigt (%s)' % fehler) from fehler
        rc = pp.warten(timeout=120)
        if rc != 0 or ergebnis is None:
            raise RuntimeError(meldung or pp.fehlertext(1500) or 'Runner endete mit %s' % rc)
        return ergebnis

    def umgebung(self):
        """Zwischendateien im Auftrag (nie System-Temp), Modelle aus der Projektablage."""
        tmp = self.ablage.arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        return {
            'TMP': str(tmp),
            'TEMP': str(tmp),
            'HF_HOME': str(settings.HF_HOME_DIR),
            'TORCH_HOME': str(settings.VIDEOTOBVH_ROOT / 'models' / 'torch_hub'),
            'PYTHONIOENCODING': 'utf-8',
        }

    # ------------------------------------------------------------- Schritte

    def _erkennung(self):
        e = self.runner('erkennung')
        self.job.ergebnis['erkennung'] = e
        self.job.ergebnis['vorlage'] = self.vorlage()

    def vorlage(self):
        """Tabellenbild des Körpernetzes (`ergebnis/vorlage.png`, Edgar 27.09.2026: „eine Spalte
        für die Vorlage … so ähnlich wie bei #mesh"), von vorn in der Lage der Erkennung — hier
        in python14 gerendert wie `Meshicon` im Reiter „Mesh". None, wenn es scheitert."""
        import numpy as np

        from .meshicon import Meshicon

        lage, matrix = self.ablage.arbeit('scan_lage.npz'), None
        if lage.is_file():
            with np.load(lage) as d:
                matrix = d['matrix']
        netz = self.ablage.netzdatei()
        return Meshicon.schreiben(netz, self.ablage.ergebnis(), Meshicon.VORLAGE, matrix) or None

    def _kalibrierung(self):
        """Genesis durch denselben Detektor — nur, wenn die Tabelle auf diesem Rechner fehlt."""
        import numpy as np
        from Genesis9.figurglb import G9figurglb
        from Genesis9.netzlandmarken import G9netzlandmarken

        from .meshfigurregler import Meshfigurregler

        if G9netzlandmarken.holen() is not None:
            self.job.ergebnis['kalibrierung'] = {'vorhanden': True, **G9netzlandmarken.holen().steckbrief()}
            return
        grund = Meshfigurregler.GRUNDFIGUREN['feminine']
        G9figurglb(grund).schreiben(self.ablage.arbeit('genesis_kalibrierung.glb'))
        self.runner('kalibrierung')
        with np.load(self.ablage.arbeit('kalibrierung.npz')) as d:
            tabelle = G9netzlandmarken.bauen(grund, d['koerper'], d['gesicht'], d['gesicht_treffer'])
        tabelle.speichern()
        self.job.ergebnis['kalibrierung'] = {'vorhanden': False, **tabelle.steckbrief()}

    def _scheitern(self, text):
        job = self.job
        job.refresh_from_db()
        if job.status == 'angehalten':
            return
        job.status = 'gescheitert'
        job.error_message = text[:4000]
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at', 'updated_at'])
