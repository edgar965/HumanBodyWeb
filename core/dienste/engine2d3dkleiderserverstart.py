# -*- coding: utf-8 -*-
u"""Engine2d3dKleiderserverstart — Läufe von „2D3D Kleider" über die Server-API starten und abwarten (01.10.2026).

Arbeitsprozesse entstehen nur über den Dev-Server (`.claude/rules/engine2d3dkleider.md`: ein Prozess aus einem Skript hängt
nicht am Server, „Anhalten" und die GPU-Sperre sehen ihn nicht). Diese Klasse holt sich die CSRF-Marke wie ein
Browser, ruft `POST …/starten/` oder `POST …/begutachtung/` und wartet, bis der Auftrag steht.
"""

import http.cookiejar
import json
import time
import urllib.error
import urllib.request

__all__ = ['Engine2d3dKleiderserverstart']


class Engine2d3dKleiderserverstart:
    BASIS = 'http://127.0.0.1:8081'
    ENDE = ('fertig', 'gescheitert', 'angehalten', 'wartet')
    TAKT_S = 15

    def __init__(self, basis=None, melden=print):
        self.basis = basis or self.BASIS
        self.melden = melden
        self.kekse = http.cookiejar.CookieJar()
        self.oeffner = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.kekse))

    def _post(self, pfad, daten):
        self.oeffner.open(self.basis + '/2d3dKleider/', timeout=30).read()
        marke = next(k.value for k in self.kekse if k.name == 'csrftoken')
        anfrage = urllib.request.Request(self.basis + pfad, data=json.dumps(daten).encode('utf-8'), method='POST',
                                         headers={'X-CSRFToken': marke, 'Referer': self.basis + '/2d3dKleider/',
                                                  'Content-Type': 'application/json'})
        try:
            with self.oeffner.open(anfrage, timeout=60) as antwort:
                return json.loads(antwort.read().decode('utf-8'))
        except urllib.error.HTTPError as fehler:
            raise RuntimeError('%s %s: %s' % (pfad, fehler.code, fehler.read().decode('utf-8', 'replace')[:300])) \
                from fehler

    def starten(self, job, ab, bis=None):
        daten = {'ab': ab, **({'bis': bis} if bis else {})}
        return self._post('/api/engine2d3dkleider/%s/starten/' % job.id, daten)

    def automatisch(self, job, runden):
        return self._post('/api/engine2d3dkleider/%s/begutachtung/' % job.id, {'automatisch': True, 'runden': int(runden)})

    def warten(self, job):
        from .engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
        gemeldet = ''
        while True:
            time.sleep(self.TAKT_S)
            job.refresh_from_db()
            text = '%s · %s%% · %s · %s' % (job.status, job.progress, job.schritt, job.progress_detail)
            if text != gemeldet:
                self.melden('%s %s %s' % (time.strftime('%H:%M:%S'), job.kennung, text))
                gemeldet = text
            if job.status in self.ENDE and not Engine2d3dKleiderarbeiter.lebt(job):
                return job.status
