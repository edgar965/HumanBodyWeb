# -*- coding: utf-8 -*-
"""`manage.py exportleiste_render <bereich> <kennung>` — der Render-Schritt der Exportleiste (31.10.2026, `Exportleisterender`).

Wie `engine2d3dkleider_render`, nur ohne Auftrag: GLB, Stellung, BVH und die Wahl der Seite stehen in `arbeit/render/auftrag.json`. Stufen: Render-Figur (`Exportleisterender.figur`),
Bewegung rechnen (`quelle.bewegung`: derselbe Retarget wie im Browser, bei 2D3D Kleider der des Auftrags) und auf die Länge schneiden → Figurcache (CPU) → Stoff und Strähnen (GPU) →
Render (Mitsuba, Entrauscher) und Video mit Ton; danach die Warteschlange von „Neu rendern". Programme aus dem Rezept des Modells (`Exportleisterender.rezept`).
Die GPU-Stufen laufen unter der Gpusperre (`mesh3dai_gpusperre.Gpusperre`), damit kein Render einem Trainingslauf die Karte wegnimmt. Das Video: `ergebnis/render_video.mp4`,
als Lauf mit Nummer (`Engine2d3dKleiderrenderlaeufe`) und als Kopie `<Name>_render.mp4` im Ordner der Seite (nie überschrieben: `_2`, `_3` …).
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
    help = 'Rendert die Figur einer Exportleiste mit Bewegung und Ton als Video.'
    TOOLS = r'A:\3DTools'
    GPUSPERRE = r'A:\3DTools\mesh3dai'
    GPU_BEDARF_GB = 8

    def add_arguments(self, parser):
        parser.add_argument('bereich')
        parser.add_argument('kennung')

    def handle(self, *args, **optionen):
        from core.dienste.exportleiste import Exportleiste
        from core.dienste.exportleistebereiche import Exportleistebereiche
        from core.dienste.exportleisterender import Exportleisterender

        quelle = Exportleistebereiche.quelle(optionen['bereich'], optionen['kennung'])
        if quelle is None:
            raise CommandError('Keine Exportleiste %s/%s' % (optionen['bereich'], optionen['kennung']))
        from core.dienste.engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
        render = Exportleisterender(Exportleiste(quelle))
        pid = render._datei('render.pid')
        pid.write_text(str(os.getpid()))
        try:
            self._lauf(render)
            self._warteschlange(render)
        except Exception as fehler:  # noqa: BLE001 — der Fehler gehört ins Protokoll und auf die Seite
            logger.exception('Exportleiste %s/%s: Render gescheitert', quelle.BEREICH, quelle.kennung)
            render.melden(status='fehler', fehler=str(fehler)[:600])
            Engine2d3dKleiderrenderneu(render).leeren()             # nach einem Fehler nicht stumm mit dem Rest weiterrechnen
        finally:
            pid.unlink(missing_ok=True)

    def _warteschlange(self, render):
        """Die Läufe, die „Neu rendern" hinter dem ersten vorgemerkt hat (`Exportleisterender.neu`), nacheinander — eine Karte, ein Lauf."""
        from core.dienste.engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
        neu = Engine2d3dKleiderrenderneu(render)
        while True:
            auftrag = neu.naechster()
            if auftrag is None:
                return
            render._datei('auftrag.json').write_text(json.dumps(auftrag, ensure_ascii=False, indent=1), encoding='utf-8')
            self._lauf(render)

    def _lauf(self, render):
        from Figurfilm.filmregler import Filmregler

        from core.dienste.bewegungsschnitt import Bewegungsschnitt
        from core.dienste.engine2d3dkleiderrenderallgemein import Engine2d3dKleiderrenderallgemein
        from core.dienste.engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe
        from core.dienste.engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
        from core.dienste.exportleistebewegung import Exportleistebewegung
        from core.dienste.modellexportziel import Modellexportziel

        auftrag = json.loads(render._datei('auftrag.json').read_text(encoding='utf-8'))
        wartend = Engine2d3dKleiderrenderneu(render).wartend()           # Läufe, die nach diesem noch kommen („Neu rendern")
        rezept = render.rezept()
        if rezept is None:
            raise RuntimeError('Die Programme des Render-Rezepts fehlen (Figurfilm/standfilm)')
        if rezept.get('allgemein'):                    # das allgemeine Rezept: die Programme der Vorlage in den Ordner des Modells kopieren
            Engine2d3dKleiderrenderallgemein(render._datei('')).einrichten()
        programme, name = Path(rezept['programme']), str(rezept.get('name') or 'render')
        t0 = time.time()
        render.melden(status='laeuft', schritt='Figur wird für den Render vorbereitet', fortschritt=0.01, start=t0, ausgabe=None, fehler=None,
                      neu_nr=auftrag.get('neu_nr'), wartend=wartend)
        glb = render.figur(Path(auftrag['glb']), auftrag.get('stellung') or {})
        render.melden(schritt='Bewegung wird auf die Figur gerechnet', fortschritt=0.03)
        voll = render.job.bewegung(Exportleistebewegung.pfad(auftrag['bvh']), auftrag.get('stellung') or {})
        n = Bewegungsschnitt.bilder(voll, auftrag['sekunden'])          # 30 je Sekunde nach den Zeiten der Bewegung (DanceKurz kommt mit 60)
        bewegung = programme / 'bewegungen' / ('%s_bewegung.json' % name)
        Bewegungsschnitt.schreiben(voll, bewegung, n)
        self._vorbereiten(programme, name, glb)
        optionen = render.leiste.optionen() if auftrag.get('physik') is not False else render.ohne_physik(render.leiste.optionen())
        regler = Filmregler.schreiben(render._datei('regler.json'), optionen)
        py = sys.executable
        gesamt = max(n, int(round(float(auftrag.get('bvh_sekunden') or 0) * render.FPS)))
        gemeinsam = [str(programme / 'video_bauen.py'), name, str(bewegung), '--glb', str(glb), '--regler', str(regler), '--gesamt-bilder', str(gesamt), '--start-bild', '0']
        # Variante B (01.11.2026, Edgar: „alles im Speicher“): mit dem allgemeinen Rezept häutet `film_video.py --speicher` die Figur je Bild auf der Karte (`Figurkarte`) —
        # vorher nur Mimik- und Korrekturdaten (`video_bauen.py` ohne Stufe); bis dahin 504 s Figurcache auf der CPU und 5,7 GB PC2 (koenigin1, 502 Bilder). Eigene Rezepte wie bisher.
        speicher = bool(rezept.get('allgemein'))
        if speicher:
            self._stufe(render, 'Mimik und Gelenkkorrektur werden vorbereitet (CPU)', 0.08, [py] + gemeinsam)
        else:
            self._stufe(render, 'Figurcache wird gerechnet (CPU)', 0.08, [py] + gemeinsam + ['--cpu'])
        ziel = render.ablage.ergebnis(render.VIDEO)
        befehl = [py, str(programme / 'film_video.py'), name, '--kamera', auftrag['kamera'], '--breite', str(auftrag['breite']), '--hoehe', str(auftrag['hoehe']),
                  '--spp', str(int(auftrag.get('spp') or 48)), '--von', '1', '--bis', str(n), '--ausname', 'film', '--zusammen', '--ausdatei', str(ziel), '--regler', str(regler)]
        if speicher:
            befehl.append('--speicher')
        if auftrag.get('ton'):
            befehl += ['--ton', str(auftrag['ton'])]
        sys.path.insert(0, self.GPUSPERRE)
        from mesh3dai_gpusperre import Gpusperre
        render.melden(schritt='Wartet auf die Grafikkarte (Gpusperre)')
        with Gpusperre('exportleiste_render_%s' % render.job.kennung, bedarf=self.GPU_BEDARF_GB):
            if not speicher:                           # die Stufe `--gpu` des allgemeinen Rezepts simuliert nichts
                self._stufe(render, 'Stoff und Strähnen werden simuliert (GPU)', 0.45, [py] + gemeinsam + ['--gpu'])
            self._stufe(render, 'Figur wird je Bild gehäutet und gerendert (GPU)' if speicher else 'Bilder werden gerendert (GPU)', 0.6, befehl)
        ordner = Modellexportziel.ordner(auftrag['ordner'])
        wunsch = Modellexportziel.name(auftrag['datei']) if auftrag.get('datei') else '%s_render' % Modellexportziel.name(auftrag.get('name'))
        stamm = Modellexportziel.eindeutiger_stamm(ordner, wunsch, ('.mp4',))
        kopie = ordner / (stamm + '.mp4')
        shutil.copyfile(ziel, kopie)
        lauf = Engine2d3dKleiderrenderlaeufe(render).eintragen(dict(auftrag, licht='studio'), ziel, time.time() - t0)
        q = render.job
        # Folgen noch Läufe der Warteschlange, bleibt der Stand „läuft": Sonst zeigte die Seite zwischen zwei Läufen kurz „fertig" und gäbe „Rendern" frei.
        render.melden(status='fertig' if not wartend else 'laeuft', schritt='Fertig' if not wartend else 'Lauf #%d fertig — der nächste folgt' % lauf['nr'],
                      fortschritt=1.0, dauer_s=round(time.time() - t0, 1), lauf=lauf['nr'], ausgabe={
            'datei': render.VIDEO, 'pfad': str(ziel), 'export': str(kopie), 'ordner': str(ordner), 'bytes': ziel.stat().st_size, 'ton': auftrag.get('ton') or None,
            'adresse': '/api/exportleiste/%s/%s/datei/%s' % (q.BEREICH, q.kennung, render.VIDEO)})

    @staticmethod
    def _vorbereiten(programme, name, glb):
        """Alte Läufe dieses Namens weg (Zwischenablagen der Programme) und die GLB in `figur.json` eintragen (Stoff und Strähnen lesen sie dort)."""
        shutil.rmtree(programme / 'videos' / name, ignore_errors=True)
        shutil.rmtree(programme / 'straehnen' / name, ignore_errors=True)
        (programme / 'straehnen' / ('objekte_%s.json' % name)).unlink(missing_ok=True)
        for art in ('korrektur_daten', 'mimik_daten'):                   # je GLB ein Ordner: die früherer Figuren weg, den der laufenden prüft `video_bauen` selbst (Größe, Fassung)
            for alt in (programme / art).glob('*'):
                if alt.is_dir() and alt.name != glb.stem:
                    shutil.rmtree(alt, ignore_errors=True)
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
            raise RuntimeError('%s: Rückgabe %d (siehe %s)' % (text, lauf.returncode, render.ablage.log()))
        logger.info('Exportleiste %s: %s in %.0f s', render.job.kennung, text, time.time() - t)
