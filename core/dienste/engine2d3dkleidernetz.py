# -*- coding: utf-8 -*-
"""Engine2d3dKleidernetz — Schritt „netz" von „2D3D Kleider": Fotos → Netz (GLB) mit TRELLIS.2 (30.09.2026).

Die Rechnung steht in `VideoToBVH/wrappers/_run_mesh.py` (Umgebung `settings.MESH_PYTHON`, eigene venv für
TRELLIS.2) — derselbe Runner wie im Reiter „Mesh". Hier läuft nur TRELLIS.2, kein Hunyuan3D
(`Engine2d3dKleidernurtrellis`, 02.10.2026). Hier nur: Auftragsbeschreibung schreiben, die
Zeilen des Runners deuten, Fortschritt und Ergebnis in den Auftrag (`job.ergebnis['netz']`, `job.eingang`),
Ansicht des Netzes für die Tabelle. Kopie von `Blendermodellnetz` (BlenderModel, 29.09.2026, dort ausgebaut).

Das Netz ist der 3D-Bezug der Iterationen (`Iterationsnetznote`), sobald der Körper darauf gerechnet ist
(`Engine2d3dKleiderkoerper`, Quelle „rechnen"). Wird der Körper aus einem Auftrag „Mesh to 3D" übernommen, ist DESSEN
Netz der Bezug — das hier gerechnete zeigt nur, dass der Schritt läuft.

Zeilen des Runners (stdout): `[fortschritt] <0..99> <Text>`, `[bild] {…}` (Befund je Foto), `[ergebnis] {…}`.
"""

import json
import logging
import os

from django.conf import settings

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..daten.wrapperpfad import Wrapperpfad
from ..pipeline_process import PipelineProzess, PipelineStille
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .engine2d3dkleiderrollen import Engine2d3dKleiderrollen
from .engine2d3dkleidervorlage import Engine2d3dKleidervorlage
from .meshicon import Meshicon
from .meshoptionen import Meshoptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidernetz']


class Engine2d3dKleidernetz:
    RUNNER = '_run_mesh.py'
    #: So lange darf der Runner schweigen (TRELLIS.2 lädt 16 GB, dekodiert 1536³) — wie `Meshlauf.STILLE_S`.
    STILLE_S = 5400

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        # Gruppe `mesh` (Interface von TRELLIS.2: Auflösung, Seed, Flächen, Texturgröße, Sampler) liegt über `netz`.
        self.optionen = dict(Engine2d3dKleideroptionen.netz(self.job.optionen), **Engine2d3dKleideroptionen.mesh(self.job.optionen),
                             **Engine2d3dKleideroptionen.vorbereitung(self.job.optionen))
        # Die Wahl „Modell" der Gruppe `mesh` ist das `formmodell` des Runners (trellis2 | pixal3d | pixal3d_mv, `mesh_pixal3d`).
        self.optionen['formmodell'] = self.optionen.get('modell', 'trellis2')
        self._ergebnis = None
        self._fotopruefung = None
        self._seed = None

    def ausfuehren(self):
        auftrag = self.ablage.netz_arbeit('auftrag.json')
        auftrag.write_text(json.dumps(self.beschreibung(), ensure_ascii=False, indent=1), encoding='utf-8')
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        pp = PipelineProzess.starten(
            [settings.MESH_PYTHON, runner, str(auftrag)], cwd=Wrapperpfad.pfad(), env_extra=self.umgebung()
        )
        logger.info('2D3D Kleider %s: Netz-Runner %s gestartet (%s, %s)', self.job.kennung, pp.proc.pid,
                    self.optionen.get('formmodell'), self.optionen.get('aufloesung'))
        try:
            for zeile in pp.stdout_zeilen(stille_timeout=self.STILLE_S):
                self._zeile(zeile.rstrip('\n'))
                if self.lauf.angehalten():
                    pp.beenden()
                    raise self.lauf.Angehalten()
        except PipelineStille as fehler:
            pp.beenden()
            raise RuntimeError('Netz-Runner schweigt (%s)' % fehler) from fehler
        rc = pp.warten(timeout=120)
        if rc != 0 or self._ergebnis is None:
            raise RuntimeError('Netz-Runner endete mit %s: %s' % (rc, pp.fehlertext(1500) or 'ohne Meldung'))
        self._abschluss()

    def beschreibung(self):
        """Was der Runner rechnen soll — Pfade, Rollen, Optionen (JSON-Datei `netz_arbeit/auftrag.json`)."""
        job = self.job
        bilder = self.bilder_fuer(job, self.ablage)
        if not bilder:
            raise RuntimeError('Keine Fotos in der Bildauswahl')
        return {
            'kennung': job.kennung,
            'name': job.name,
            'ab': None,
            # Fotos mit anderer Kleidung fallen vor der Form heraus (`mesh_fotopruefung`, 01.10.2026) — Vorgabe an; die Option
            # `fotopruefung` der Gruppe `mesh` schaltet es aus (03.10.2026: Seitenfoto im Mehrbild prüfen).
            'optionen': dict(self.optionen, fotopruefung=self.optionen.get('fotopruefung', 'an')),
            'bilder': bilder,
            'ordner': {
                'vorbereitet': str(self.ablage.unter(Engine2d3dKleiderablage.VORBEREITET)),
                'arbeit': str(self.ablage.netz_arbeit()),
                'ergebnis': str(self.ablage.netz()),
            },
            'wurzeln': {'videotobvh': str(settings.VIDEOTOBVH_ROOT)},
        }

    @classmethod
    def bilder_fuer(cls, job, ablage):
        """Die Fotos, die der Runner bekommt (Schritte „vorbereitung" und „netz"): Datei, Pfad, Rolle, Gewicht, Bereich — in der Reihenfolge der
        Bildauswahl. Auch die Seite fragt es (`Engine2d3dKleidervorbereitungsliste`: gehört die abgelegte Vorbereitung noch zu diesen Fotos?)."""
        bilder = []
        for name in cls._reihenfolge(job, ablage):
            eintrag = job.bild(name) or {}
            bilder.append({
                'datei': name,
                'pfad': str(ablage.unter(Engine2d3dKleiderablage.EINGANG) / name),
                'rolle': Meshoptionen.rolle_pruefen(eintrag.get('rolle')),
                'gewicht': Meshoptionen.gewicht_pruefen(eintrag.get('gewicht', 100)),
                'bereich': Meshoptionen.bereich_pruefen(eintrag.get('bereich')),
            })
        return bilder

    @staticmethod
    def _reihenfolge(job, ablage):
        """Die Fotos in der Reihenfolge der Bildauswahl (Platz 1 zuerst — bei „Automatisch" gilt das erste als
        „vorne"), dahinter, was nur im Ordner liegt. Ein Foto mit Rolle „aus" bleibt draußen."""
        da = ablage.eingaenge()
        gewollt = [b.get('datei') for b in job.bilder or []
                   if isinstance(b, dict) and b.get('rolle') != 'aus']
        # „Nur Iterationen" (`Engine2d3dKleiderrollen`): diese Fotos bekommt das Netz nicht, auch nicht „was nur im Ordner liegt".
        nur_iterationen = Engine2d3dKleiderrollen.nur_iterationen(job.bilder)
        return [n for n in [n for n in gewollt if n in da] + [n for n in da if n not in gewollt]
                if n not in nur_iterationen]

    def umgebung(self):
        """HF-Ablage auf A:, Zwischendateien im Auftrag (nie System-Temp) — die Werte von `Meshlauf.umgebung`."""
        tmp = self.ablage.netz_arbeit('tmp')
        tmp.mkdir(parents=True, exist_ok=True)
        return {
            'HF_HOME': str(settings.HF_HOME_DIR),
            'HF_HUB_OFFLINE': '1',
            'TORCH_HOME': str(settings.VIDEOTOBVH_ROOT / 'models' / 'torch_hub'),
            'ATTN_BACKEND': 'flash_attn',
            'SPARSE_ATTN_BACKEND': 'flash_attn',
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
            self.lauf.melden(wert / 100.0, teile[1] if len(teile) > 1 else '')
        elif zeile.startswith('[bild] '):
            self._bild(zeile[len('[bild] '):])
        elif zeile.startswith('[seed] '):
            # Der Seed, mit dem TRELLIS.2 gerechnet hat — bei „Randomize Seed" sonst nirgends zu finden.
            self._seed = zeile[len('[seed] '):].strip()
            logger.info('2D3D Kleider %s: TRELLIS.2 rechnet mit Seed %s', self.job.kennung, self._seed)
        elif zeile.startswith('[fotopruefung] '):
            try:
                self._fotopruefung = json.loads(zeile[len('[fotopruefung] '):])
            except ValueError:
                logger.error('2D3D Kleider %s: Fotoprüfung nicht lesbar: %.200s', self.job.kennung, zeile)
        elif zeile.startswith('[ergebnis] '):
            try:
                self._ergebnis = json.loads(zeile[len('[ergebnis] '):])
            except ValueError:
                logger.error('2D3D Kleider %s: Ergebniszeile nicht lesbar: %.200s', self.job.kennung, zeile)

    def _bild(self, roh):
        """Der Befund je Foto (erkannte Rolle, Kasten) in `bilder` — Rolle, Gewicht, Bereich und Platz behalten,
        was der Nutzer gestellt hat (`bilder_sichern`)."""
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
        job.bilder = eintraege
        job.bilder_sichern()

    # ------------------------------------------------------------ Abschluss

    def _abschluss(self):
        job, ablage = self.job, self.ablage
        glb = ablage.netzdatei()
        if glb is None:
            raise RuntimeError('Der Runner meldet Ergebnis, aber %s fehlt' % ablage.netz(ablage.NETZDATEI))
        ergebnis = dict(self._ergebnis)
        if self._seed is not None:
            ergebnis['seed'] = self._seed
        dateien = dict(ergebnis.get('dateien') or {})
        icon = Meshicon.schreiben(glb, ablage.netz())
        if icon:
            dateien['icon'] = icon
        ergebnis['dateien'] = dateien
        job.ergebnis = {**(job.ergebnis or {}), 'netz': ergebnis}
        if self._fotopruefung is not None:
            job.ergebnis['fotopruefung'] = self._fotopruefung
        stat = glb.stat()
        job.eingang = {'datei': glb.name, 'original': glb.name, 'bytes': stat.st_size, 'ursprung': str(glb),
                       'stand': [stat.st_mtime_ns, stat.st_size]}
        self.lauf.sichern('ergebnis', 'eingang')
        Engine2d3dKleidervorlage.erneuern(job)
        logger.info('2D3D Kleider %s: Netz fertig (%s Flächen)', job.kennung, ergebnis.get('flaechen'))
