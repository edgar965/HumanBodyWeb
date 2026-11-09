# -*- coding: utf-8 -*-
"""Ai2d3djoblauf — ein ganzer Job der Seite 2d-3d-AI in einem Lauf (06.11.2026, Edgar: „alle fixes, damit es generisch läuft für beide Pipelines“).

Bis dahin startete das Web nur „Genesis rechnen“; PSHuman und die Foto-Kette liefen von Hand (`pshuman_job_rechnen.py`, `nurfotos_kette.py`, Sammellauf `genesis_vergleich_alle.py`).
Der Knopf „Job rechnen“ reiht den Job in dieselbe Schlange wie die Tests (`Mesh3dairechenschlange`, ein Lauf zur Zeit):

    pshuman     PSHuman-Netz aus den Fotos des Jobs; ist es zur Wahl schon gerechnet, kehrt `job_rechnen` sofort zurück
    fotokette   nur mit Häkchen „Genesis direkt aus dem Foto“ (`pshuman.genesis_aus_foto`): die Stufen von `nurfotos_kette.py`
    genesis     neuer Mesh3D-AI-Test aus dem Netz (`Ai2d3dgenesisstart`), er steht danach in der Schlange und zeigt seinen Fortschritt auf der Testseite

Ein Schritt mit Fehler hält den Lauf an. `pshuman_job_rechnen.py` fängt Fehler je Job ab und endet mit 0, darum zählt hier die Zeile mit `FEHLER` und das fertige Netz, nicht der Rückgabewert.
Stand und Log: `<Job>/rechnen/stand.json`, `lauf.log`. Je Schritt die Felder von `Mesh3dairechenmessung`.

    Ai2d3djoblauf(job).ausfuehren()       # im Arbeitsprozess (`manage.py mesh3dai_rechnen`)
"""
import json
import logging
import os
import sys
import time
from pathlib import Path

from django.conf import settings

from core.atomic_write import AtomarSchreiber

from .ai2d3dgenesisstart import Ai2d3dgenesisstart
from .ai2d3djobs import Ai2d3djobs
from .mesh3dairechenmessung import Mesh3dairechenmessung
from .mesh3dairechenschlange import Mesh3dairechenschlange
from .mesh3dairechenschritt import Mesh3dairechenschritt

logger = logging.getLogger('core')

__all__ = ['Ai2d3djoblauf']


class Ai2d3djoblauf:
    ORDNER = 'rechnen'
    PSHUMAN = ('pshuman_port14', 'pshuman_job_rechnen.py')
    FOTOKETTE = ('ai2d3d', 'nurfotos_kette.py')
    TEXTE = {'pshuman': 'PSHuman-Netz aus den Fotos', 'fotokette': 'Foto-Kette: Genesis direkt aus den Fotos', 'genesis': 'Mesh3D-AI-Test aus dem Netz anlegen und einreihen'}

    def __init__(self, job):
        self.job = job
        self.name = Path(job['ordner']).name
        self.ordner = Path(job['ordner']) / self.ORDNER

    @classmethod
    def aus_kennung(cls, kennung):
        job = Ai2d3djobs.job(kennung)
        if job is None:
            raise ValueError('Kein Job %s' % kennung)
        return cls(job)

    def schritte(self):
        """Die Schlüssel der Schritte dieses Jobs."""
        foto = (self.job.get('pshuman') or {}).get('genesis_aus_foto')
        return ('pshuman', 'fotokette', 'genesis') if foto else ('pshuman', 'genesis')

    def stand(self):
        try:
            return json.loads((self.ordner / 'stand.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    def stand_fuer_seite(self):
        """Der Stand; rechnet ihn kein Arbeitsprozess mehr (hart beendet), gilt er als abgebrochen, sonst bliebe der Knopf der Seite für immer gesperrt."""
        stand = self.stand()
        if stand and stand.get('status') in ('wartet', 'laeuft') and not Mesh3dairechenschlange.job_aktiv(self.job['id']):
            stand.update(status='fehler', fehler='Der Lauf wurde abgebrochen, kein Arbeitsprozess rechnet ihn mehr')
        return stand

    def _schreiben(self, stand):
        self.ordner.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(self.ordner / 'stand.json', stand)

    def vorbereiten(self):
        """Stand „wartet“ mit allen Schritten. `ValueError`, wenn der Lauf nicht beginnen kann."""
        if not self.job.get('geschlecht'):
            raise ValueError('Erst das Geschlecht der Genesis-Figur wählen')
        stand = {'job': self.job['id'], 'status': 'wartet', 'angefragt': time.strftime('%Y-%m-%dT%H:%M:%S'), 'test': None,
                 'schritte': [{'schluessel': s, 'text': self.TEXTE[s], 'status': 'offen'} for s in self.schritte()]}
        self._schreiben(stand)
        return stand

    def ausfuehren(self):
        """Alle Schritte der Reihe nach; hält beim ersten Fehler an. → Stand."""
        stand = self.stand() or self.vorbereiten()
        stand.update(status='laeuft', beginn=time.strftime('%Y-%m-%dT%H:%M:%S'), fehler=None)
        self._schreiben(stand)
        t_alles = time.perf_counter()
        with open(self.ordner / 'lauf.log', 'a', encoding='utf-8') as aus:
            aus.write('\n==== Job %s, Lauf %s\n' % (self.name, time.strftime('%Y-%m-%d %H:%M:%S')))
            for eintrag in stand['schritte']:
                eintrag.update(status='laeuft', beginn=time.strftime('%H:%M:%S'))
                self._schreiben(stand)
                aus.write('== %s %s\n' % (eintrag['text'], time.strftime('%H:%M:%S')))
                aus.flush()
                t0 = time.perf_counter()
                with Mesh3dairechenmessung() as messung:
                    fehler = self._schritt(eintrag['schluessel'], aus, messung, stand)
                eintrag['dauer_s'] = round(time.perf_counter() - t0, 1)
                eintrag.update(messung.bericht(eintrag['dauer_s']))
                eintrag['status'] = 'fehler' if fehler else 'fertig'
                if fehler:
                    stand.update(status='fehler', fehler='Schritt „%s“: %s' % (eintrag['text'], fehler), ende=time.strftime('%Y-%m-%dT%H:%M:%S'),
                                 dauer_s=round(time.perf_counter() - t_alles, 1))
                    self._schreiben(stand)
                    logger.warning('Ai2d3djoblauf %s: %s', self.name, stand['fehler'])
                    return stand
                self._schreiben(stand)
        stand.update(status='fertig', ende=time.strftime('%Y-%m-%dT%H:%M:%S'), dauer_s=round(time.perf_counter() - t_alles, 1))
        self._schreiben(stand)
        logger.info('Ai2d3djoblauf %s fertig in %.0f s, Test %s', self.name, stand['dauer_s'], stand.get('test'))
        return stand

    def _schritt(self, schluessel, aus, messung, stand):
        """Ein Schritt. → Fehlertext oder None. Auch ein unerwarteter Fehler kommt in den Stand, sonst bliebe der Job auf „läuft“."""
        try:
            return self._rechnen(schluessel, aus, messung, stand)
        except Exception as fehler:          # noqa: BLE001
            logger.exception('Ai2d3djoblauf %s: Schritt %s', self.name, schluessel)
            return '%s: %s' % (type(fehler).__name__, fehler)

    def _rechnen(self, schluessel, aus, messung, stand):
        """Ein Schritt. → Fehlertext oder None."""
        if schluessel == 'genesis':
            return self._genesis(stand)
        if schluessel == 'pshuman':
            zeilen, rc = self._skript(self.PSHUMAN, [self.name], aus, messung)
            return self.fehler(zeilen, rc) or (None if Ai2d3dgenesisstart.eingang(self.job['ordner'])[0] else 'kein PSHuman-Netz')
        return self.fehler(*self._skript(self.FOTOKETTE, ['--job', self.name], aus, messung))

    @staticmethod
    def fehler(zeilen, rc):
        """Fehlertext aus den letzten Zeilen eines Skripts oder None."""
        if rc != 0:
            return 'Fehlercode %s — %s' % (rc, ' / '.join(zeilen[-5:]))
        return next((z for z in zeilen if ' FEHLER ' in z or 'Traceback (most recent call last)' in z), None)

    def _skript(self, ort, argumente, aus, messung):
        ordner = Path(settings.TOOLS_ROOT) / ort[0]
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        return Mesh3dairechenschritt.rechnen([sys.executable, '-u', str(ordner / ort[1]), *argumente], aus, messung, ordner, env, 'Job %s' % self.name)

    def _genesis(self, stand):
        try:
            stand['test'] = Ai2d3dgenesisstart.starten(Ai2d3djobs.job(self.job['id']))
        except ValueError as fehler:
            return str(fehler)
        return None
