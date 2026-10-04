# -*- coding: utf-8 -*-
"""Engine2d3dKleideranimexport — das Modell eines Auftrags „2D3D Kleider" als GLB und/oder Blender-Datei, wahlweise MIT BVH-Animation
und MIT Audio.

Edgar (01.10.2026): „Export als glb / blender inkl. animation"; (03.10.2026): „rechts soll neben dem Export als glb auch erscheinen:
export in blender und als Option (per default aktiviert): Audio (mit Pfad), ausgewählte BVH (Pfad)".

Quelle ist das Modell, das die Bühne zeigt: das Stand-Modell (`Engine2d3dKleiderstandmodell`: Körper, Kleider, Haar und Zubehör am
Rig), sonst die Runden-GLB der besten Runde. Die Bewegung ist die der gewählten BVH (`film_bewegung.json`, bei einer anderen BVH wird
sie auf die Figur gerechnet und wie vom Schritt „film" abgelegt); sie geht als glTF-Animation in die GLB (`G9glbanimation`), Blender
macht daraus die `.blend`. Das Audio kann keine GLB tragen: Es liegt als Datei neben dem Export und läuft in der `.blend` als
Tonstreifen des Sequenzers mit.

Ergebnis in `ergebnis/` (`modell_animiert.glb`, `.blend`) und als Kopie im Exportordner des Auftrags (`<Name>.glb`, `<Name>.blend`,
`<Name>_audio.<Endung>`, `<Name>_export.json` mit den Pfaden); Bericht unter `job.ergebnis['animexport']`.
"""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from .studioton import Studioton

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleideranimexport']


class Engine2d3dKleideranimexport:
    GLB, BLEND, BEWEGUNG = 'modell_animiert.glb', 'modell_animiert.blend', 'film_bewegung.json'
    BLENDER_TIMEOUT_S = 300

    def __init__(self, job):
        self.job = job
        self.ablage = Engine2d3dKleiderablage(job.kennung)

    # ------------------------------------------------------------------ Quelle

    def quelle(self):
        """`(Pfad, Runde, Art)` des Modells — das Stand-Modell der Bühne, sonst die Runden-GLB der besten Runde; `(None, None, None)` ohne."""
        from .engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
        stand = Engine2d3dKleiderstandmodell(self.job, self.ablage).eintrag() or {}
        if stand.get('datei') and self.ablage.ergebnis(stand['datei']).is_file():
            return self.ablage.ergebnis(stand['datei']), stand.get('runde'), 'stand'
        e = self.job.ergebnis or {}
        beste = int(((e.get('kreislauf') or {}).get('runde_bester')) or 0)
        if beste:
            pfad = self.ablage.iterationen('runde_%03d_modell.glb' % beste)
            if not pfad.is_file():                  # die Runden schreiben keine GLB mehr: einmal hier bauen
                from .begutachtungswerkzeug import Begutachtungswerkzeug
                Begutachtungswerkzeug(self.job, self.ablage).bestes_glb(e.get('kreislauf') or {}, 'modell.glb')
            if pfad.is_file():
                return pfad, beste, 'runde'
        pfad = self.ablage.ergebnis('modell.glb')
        return (pfad, None, 'modell') if pfad.is_file() else (None, None, None)

    def bewegung(self, bvh_pfad):
        """Die Bewegung der BVH auf diese Figur: `ergebnis/film_bewegung.json`, wenn sie zu dieser BVH gehört — sonst neu gerechnet und so
        abgelegt wie vom Schritt „film" (die Play-Leiste der Bühne spielt sie dann ebenfalls)."""
        film = (self.job.ergebnis or {}).get('film') or {}
        bvh = str(bvh_pfad or film.get('bvh') or '').strip()
        if not bvh:
            raise ValueError('Keine BVH gewählt — in den Optionen unter „Film“ eine BVH-Datei eintragen')
        ablage = self.ablage.ergebnis(self.BEWEGUNG)
        if not (Path(bvh).is_file() and bvh.lower().endswith('.bvh')):
            raise ValueError('BVH-Datei nicht gefunden: %s' % bvh)
        if not (ablage.is_file() and Path(str(film.get('bvh') or '')) == Path(bvh)):
            from .engine2d3dkleiderbewegung import Engine2d3dKleiderbewegung
            aus = self.ablage.arbeit('film')
            aus.mkdir(parents=True, exist_ok=True)
            pfad, spuren = Engine2d3dKleiderbewegung(SimpleNamespace(job=self.job)).rechnen(bvh, aus)
            shutil.copyfile(pfad, ablage)
            ergebnis = dict(self.job.ergebnis or {})
            ergebnis['film'] = dict(film, bewegung=self.BEWEGUNG, bvh=bvh, bewegung_bilder=int(spuren.frame_count))
            self.job.ergebnis = ergebnis
            self.job.save(update_fields=['ergebnis', 'updated_at'])
        with open(ablage, encoding='utf-8') as d:
            return json.load(d), bvh

    # ----------------------------------------------------------------- Ausführen

    def ausfuehren(self, glb=True, blend=True, bvh=True, bvh_pfad='', audio=False, audio_pfad='', name=''):
        """→ Bericht (Dict, geht als JSON hinaus und in `job.ergebnis['animexport']`). `bvh`/`audio`: die Beigaben (Vorgabe an)."""
        from Genesis9.glbanimation import G9glbanimation

        from .engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
        quelle, runde, art = self.quelle()
        if quelle is None:
            raise ValueError('Es gibt noch kein Modell — erst die Iterationen rechnen')
        ton = Studioton.pruefen(audio_pfad) if audio else None
        bewegung, bvh_datei = self.bewegung(bvh_pfad) if bvh else (None, '')
        modell = G9glbanimation(quelle)
        bericht = ({'kanaele': 0, 'fehlend': [], 'bilder': 0, 'sekunden': 0.0} if bewegung is None
                   else modell.einbauen(bewegung, name=Path(bvh_datei).stem or 'tanz'))
        ziel = self.ablage.ergebnis(self.GLB)
        bericht['glb'] = {'datei': self.GLB, 'bytes': modell.schreiben(ziel)}
        bericht.update(runde=runde, quelle=quelle.name, quellart=art, bvh=bvh_datei or None, audio=str(ton) if ton else None)
        if blend:
            bericht['blend'] = self._blend(ziel, bewegung, ton)
        bericht['ablage'] = self._ablegen(Engine2d3dKleiderspeichern.zielordner_fuer(self.job), name, glb, blend, ziel, ton, bericht)
        # Dictionary gewollt: geht als JSON in die Antwort und in `job.ergebnis`.
        self.job.ergebnis = dict(self.job.ergebnis or {}, animexport=bericht)
        self.job.save(update_fields=['ergebnis', 'updated_at'])
        return bericht

    def _ablegen(self, ordner, name, glb, blend, glb_pfad, ton, bericht):
        """Kopien im Exportordner des Auftrags (`Randy.glb`, `Randy.blend`, `Randy_audio.mp3`, `Randy_export.json`) → {ordner, dateien}."""
        stamm = (name or self.job.name or 'modell').strip() or 'modell'
        ordner.mkdir(parents=True, exist_ok=True)
        dateien = []
        if glb:
            shutil.copyfile(glb_pfad, ordner / (stamm + '.glb'))
            dateien.append(stamm + '.glb')
        if blend and (bericht.get('blend') or {}).get('datei'):
            shutil.copyfile(self.ablage.ergebnis(self.BLEND), ordner / (stamm + '.blend'))
            dateien.append(stamm + '.blend')
        if ton:
            shutil.copyfile(ton, ordner / (stamm + '_audio' + ton.suffix.lower()))
            dateien.append(stamm + '_audio' + ton.suffix.lower())
        zettel = {k: bericht.get(k) for k in ('runde', 'quelle', 'bvh', 'audio', 'bilder', 'sekunden', 'kanaele')}
        (ordner / (stamm + '_export.json')).write_text(json.dumps(zettel, ensure_ascii=False, indent=1), encoding='utf-8')
        dateien.append(stamm + '_export.json')
        return {'ordner': str(ordner), 'dateien': dateien}

    def _blend(self, glb, bewegung, ton):
        ziel = self.ablage.ergebnis(self.BLEND)
        bilder = max(1, len((bewegung or {}).get('times') or []))
        dauer = float((bewegung or {}).get('duration') or 0.0)
        fps = round(bilder / dauer) if dauer else 30
        befehl = [str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python',
                  str(settings.MODELLEXPORT_BLENDER_SKRIPT), '--', '--glb', str(glb), '--blend', str(ziel),
                  '--fps', str(int(fps)), '--polygone', '1.0']
        if ton:
            befehl += ['--audio', str(ton)]
        try:
            lauf = subprocess.run(befehl, capture_output=True, text=True, timeout=self.BLENDER_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {'fehler': 'Blender hat das Zeitlimit überschritten (%d s)' % self.BLENDER_TIMEOUT_S}
        if lauf.returncode != 0 or not ziel.is_file():
            logger.error('2D3D Kleider %s: Blender-Export gescheitert (%d): %s', self.job.kennung, lauf.returncode,
                         lauf.stderr[-2000:])
            return {'fehler': 'Blender konnte keine .blend schreiben (siehe Log)'}
        return {'datei': self.BLEND, 'bytes': ziel.stat().st_size, 'fps': int(fps), 'audio': bool(ton)}
