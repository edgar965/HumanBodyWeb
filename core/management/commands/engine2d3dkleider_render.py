# -*- coding: utf-8 -*-
"""`manage.py engine2d3dkleider_render <id>` — der Render-Schritt eines Auftrags „2D3D Kleider" (03.10.2026, `Engine2d3dKleiderrender`).

Liest die Wahl der Seite aus `arbeit/render/auftrag.json` (`sekunden`, `kamera`, `breite`, `hoehe`, `ton`) und rechnet in Stufen mit den Programmen
des Rezepts (`arbeit/render/rezept.json`): Bewegung auf die gewählte Länge schneiden → Figurcache (CPU) → Stoff und Strähnen (GPU) → Render
(Mitsuba, Entrauscher) und Video mit Ton. Jede Stufe steht danach in `zustand.json`; die Seite zeigt sie im Takt des Zustands. Vor den GPU-Stufen
wartet der Prozess, bis die Karte frei ist (weniger als `GPU_FREI_MB` belegt) — andere Aufträge (Pixal) füllen sie bis auf wenige MB.
"""

import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('core')


class Command(BaseCommand):
    help = 'Rendert das Modell eines Auftrags „2D3D Kleider" mit Bewegung und Ton als Video.'
    GPU_FREI_MB = 6000
    GPU_WARTEN_S = 40 * 60
    TOOLS = r'A:\3DTools'

    def add_arguments(self, parser):
        parser.add_argument('job_id', help='Die Kennung (UUID) des Auftrags')

    def handle(self, *args, **optionen):
        from core.dienste.engine2d3dkleiderrender import Engine2d3dKleiderrender
        from core.models import Engine2d3dKleiderauftrag

        job = Engine2d3dKleiderauftrag.objects.filter(id=optionen['job_id']).first()
        if job is None:
            raise CommandError('Kein Auftrag „2D3D Kleider" %s' % optionen['job_id'])
        render = Engine2d3dKleiderrender(job)
        pid = render._datei('render.pid')
        pid.write_text(str(os.getpid()))
        try:
            self._lauf(job, render)
        except Exception as fehler:  # noqa: BLE001 — der Fehler gehört ins Protokoll und auf die Seite
            logger.exception('2D3D Kleider %s: Render gescheitert', job.kennung)
            render.melden(status='fehler', fehler=str(fehler)[:600])
        finally:
            pid.unlink(missing_ok=True)

    # ------------------------------------------------------------------ Ablauf

    def _lauf(self, job, render):
        from core.dienste.engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe
        from core.dienste.engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
        from core.dienste.engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell

        auftrag = json.loads(render._datei('auftrag.json').read_text(encoding='utf-8'))
        rezept = render.rezept()
        programme, name = Path(rezept['programme']), str(rezept.get('name') or 'render')
        stand = Engine2d3dKleiderstandmodell(job, render.ablage).eintrag() or {}
        glb = render.ablage.ergebnis(stand['datei']) if stand.get('datei') else None
        if glb is None or not glb.is_file():
            raise RuntimeError('Es gibt noch kein Modell — erst die Iterationen rechnen')
        film = (job.ergebnis or {}).get('film') or {}
        n = max(2, int(round(float(auftrag['sekunden']) * render.FPS)))
        t0 = time.time()
        render.melden(status='laeuft', schritt='Bewegung wird geschnitten', fortschritt=0.03, bilder=n, sekunden=auftrag['sekunden'], start=t0,
                      ausgabe=None, fehler=None)
        bewegung = programme / 'bewegungen' / ('%s_bewegung.json' % name)
        self._schneiden(render.ablage.ergebnis(film.get('bewegung') or 'film_bewegung.json'), bewegung, n)
        self._vorbereiten(programme, name, glb)
        py = sys.executable
        self._stufe(render, 'Figurcache wird gerechnet (CPU)', 0.08, [py, str(programme / 'video_bauen.py'), name, str(bewegung), '--glb', str(glb), '--cpu'])
        self._grafikkarte(render)
        self._stufe(render, 'Stoff und Strähnen werden simuliert (GPU)', 0.45,
                    [py, str(programme / 'video_bauen.py'), name, str(bewegung), '--glb', str(glb), '--gpu'])
        ziel = render.ablage.ergebnis(render.VIDEO)
        befehl = [py, str(programme / 'film_video.py'), name, '--kamera', auftrag['kamera'], '--breite', str(auftrag['breite']),
                  '--hoehe', str(auftrag['hoehe']), '--spp', str(int(auftrag.get('spp') or 48)), '--von', '1', '--bis', str(n), '--ausname', 'film', '--zusammen',
                  '--ausdatei', str(ziel)]
        if auftrag.get('ton'):
            befehl += ['--ton', str(auftrag['ton'])]
        self._grafikkarte(render)
        self._stufe(render, 'Bilder werden gerendert (GPU)', 0.6, befehl)
        ordner = Engine2d3dKleiderspeichern.zielordner_fuer(job)
        ordner.mkdir(parents=True, exist_ok=True)
        kopie = ordner / ('%s_render.mp4' % ((auftrag.get('name') or job.name or 'modell').strip() or 'modell'))
        shutil.copyfile(ziel, kopie)
        lauf = Engine2d3dKleiderrenderlaeufe(render).eintragen(dict(auftrag, licht='studio'), ziel, time.time() - t0)     # bleibt als Lauf Nr. N
        render.melden(status='fertig', schritt='Fertig', fortschritt=1.0, dauer_s=round(time.time() - t0, 1), lauf=lauf['nr'], ausgabe={
            'datei': render.VIDEO, 'pfad': str(ziel), 'export': str(kopie), 'ordner': str(ordner), 'bytes': ziel.stat().st_size,
            'ton': auftrag.get('ton') or None, 'adresse': '/api/engine2d3dkleider/%s/datei/ergebnis/%s' % (job.id, render.VIDEO)})

    # ------------------------------------------------------------------ Stufen

    @staticmethod
    def _schneiden(quelle, ziel, n):
        """Die ersten `n` Bilder der Bewegung (Quaternionen 4, Position 3 Werte je Bild)."""
        d = json.loads(quelle.read_text(encoding='utf-8'))
        if n > int(d.get('frame_count') or 0):
            raise RuntimeError('Die Bewegung hat nur %d Bilder, gewünscht %d' % (int(d.get('frame_count') or 0), n))
        neu = dict(d, tracks={k: v[:4 * n] for k, v in (d.get('tracks') or {}).items()})
        if d.get('position_track'):
            neu['position_track'] = dict(d['position_track'], values=d['position_track']['values'][:3 * n])
        neu.update(times=[round(i / 30.0, 6) for i in range(n)], frame_count=n, duration=round(n / 30.0, 6))
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(json.dumps(neu), encoding='utf-8')

    @staticmethod
    def _vorbereiten(programme, name, glb):
        """Alte Läufe dieses Namens weg (eigene Zwischenablagen) und die GLB des Stands in `figur.json` eintragen (Stoff und Strähnen lesen sie dort)."""
        shutil.rmtree(programme / 'videos' / name, ignore_errors=True)
        shutil.rmtree(programme / 'straehnen' / name, ignore_errors=True)
        (programme / 'straehnen' / ('objekte_%s.json' % name)).unlink(missing_ok=True)
        figur = programme / 'figur.json'
        daten = json.loads(figur.read_text(encoding='utf-8'))
        daten['glb'] = str(glb)
        figur.write_text(json.dumps(daten, indent=1), encoding='utf-8')

    def _stufe(self, render, text, fortschritt, befehl):
        render.melden(schritt=text, fortschritt=fortschritt)
        t = time.time()
        with open(render.ablage.log(), 'ab') as protokoll:
            protokoll.write(('\n=== Render: %s ===\n' % text).encode('utf-8'))
            lauf = subprocess.run(befehl, cwd=self.TOOLS, stdout=protokoll, stderr=subprocess.STDOUT)
        if lauf.returncode:
            raise RuntimeError('%s: Rückgabe %d (siehe Protokoll des Auftrags)' % (text, lauf.returncode))
        logger.info('2D3D Kleider %s: %s in %.0f s', render.job.kennung, text, time.time() - t)

    def _grafikkarte(self, render):
        """Wartet, bis die Karte frei ist (andere Aufträge belegen sie vollständig) — höchstens `GPU_WARTEN_S`."""
        ende = time.time() + self.GPU_WARTEN_S
        while time.time() < ende:
            belegt = self._belegt_mb()
            if belegt is None or belegt < self.GPU_FREI_MB:
                return
            render.melden(schritt='Wartet auf die Grafikkarte (%d MB belegt)' % belegt)
            time.sleep(10)
        raise RuntimeError('Die Grafikkarte wurde nicht frei (über %d Minuten belegt)' % (self.GPU_WARTEN_S // 60))

    @staticmethod
    def _belegt_mb():
        try:
            aus = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=20)
            return int(aus.stdout.split()[0])
        except (OSError, ValueError, IndexError, subprocess.SubprocessError):
            return None
