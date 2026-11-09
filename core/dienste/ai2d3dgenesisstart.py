# -*- coding: utf-8 -*-
"""Ai2d3dgenesisstart — vom Job zur Mesh3D-AI-Kette (06.11.2026, Punkt 7 der Lückenliste beider Pipelines).

Edgar: „mach den besten code den wir haben in beiden pipelines“. Bis dahin lief das nur von Hand über
`_wegwerf/ai2d3d/mesh3dai_test_anlegen.py`, und der Sammellauf übergab kein Foto: `edgar_1_mesh3d_ai_2` hatte
kein `foto/`, der Schritt „foto“ (`Mesh3daifotogelenke`, Mesh-Anpassung 19 und 21) tat dort nichts.

Dieser Dienst legt den Test `<Job>-mesh3d-AI` an, immer mit dem Foto, das PSHuman wirklich bekommen hat: Bei
einer liegenden Person ist das die aufgerichtete Fassung (`Fotoaufrichtung`, `befund.json` → `aufrichtung`),
denn das Netz steht in deren Kamera. Liegt das Netz selbst, richtet die Kette es auf (`Testaufrecht`).

Jeder Start ist ein neuer Test (`Mesh3dairechenschlange.anlegen` hängt `_2`, `_3` an), der alte bleibt liegen.
Die job.json nennt danach den neuen, die vorige Fassung bleibt in `job.json.vor_mesh3dai_test`. Ein Start
kommt nur vom Knopf auf der Jobseite (rund 20 Minuten Karte, gemessen an n2: 1.080 s), nie von selbst.

    Ai2d3dgenesisstart.eingang(ordner)     # (Netz, Foto, Maske); Foto und Maske None ohne Bilder
    Ai2d3dgenesisstart.starten(job)        # Kennung des Tests; job: Eintrag aus `Ai2d3djobs`
"""
import json
import logging
import shutil
from pathlib import Path

import numpy as np
from django.core.files import File

from core.atomic_write import AtomarSchreiber

from .mesh3daijobtest import Mesh3daijobtest
from .mesh3dairechenschlange import Mesh3dairechenschlange
from .mesh3daitest import Mesh3daitest

logger = logging.getLogger('core')

__all__ = ['Ai2d3dgenesisstart']


class Ai2d3dgenesisstart:
    NETZ = 'pshuman/result_clr_scale4_1.glb'
    BEFUND = 'pshuman/befund.json'
    MASKE = 'pshuman/eingang_maske.png'
    SICHERUNG = 'job.json.vor_mesh3dai_test'
    #: Einpassung des PSHuman-Laufs, darin die Gelenke aus den sechs Ansichten, und ihr Name im Test (`Mesh3daifotogelenke.ANSICHTEN`)
    GELENKE, GELENKE_TEST = 'pshuman/rekon/1/genesis.json', 'foto/gelenke_ansichten.json'

    @classmethod
    def netz(cls, ordner):
        """Das Netz, das die Jobseite zeigt: der Eintrag `pshuman` der job.json, sonst `NETZ`. Er kann eine bessere Textur tragen als das Rechenergebnis (`result_alle_fotos.glb`)."""
        ordner = Path(ordner)
        try:
            netze = json.loads((ordner / 'job.json').read_text(encoding='utf-8')).get('netze') or []
        except (OSError, ValueError):
            netze = []
        eingetragen = next((Path(str(n.get('datei') or '')) for n in netze if n.get('art') == 'pshuman'), None)
        return eingetragen if eingetragen and eingetragen.is_file() else ordner / cls.NETZ

    @classmethod
    def eingang(cls, ordner):
        """(Netz, Foto, Maske) des Jobs. Netz None ohne PSHuman-Ergebnis; Foto und Maske beide oder keins."""
        ordner = Path(ordner)
        netz = cls.netz(ordner)
        if not netz.is_file():
            return None, None, None
        try:
            befund = json.loads((ordner / cls.BEFUND).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return netz, None, None
        foto, maske = Path(str(befund.get('foto') or '')), ordner / cls.MASKE
        erstes = (befund.get('aufrichtung') or [{}])[0]
        if erstes.get('gedreht') and erstes.get('aufgerichtet'):
            foto = Path(erstes['aufgerichtet'])
            maske = foto.with_name(foto.name.replace('foto_', 'maske_'))
        return (netz, foto, maske) if foto.is_file() and maske.is_file() else (netz, None, None)

    @staticmethod
    def punktfarben(netz):
        """Das Netz selbst, oder bei Material ohne uv (PSHuman) eine Kopie mit Punktfarben daneben. Sonst
        bricht die Bilderkennung der Kette ab (04.11.2026, Docstring von `mesh3dai_test_anlegen.py`)."""
        import trimesh
        s = trimesh.load(netz, process=False)
        g = list(s.geometry.values()) if hasattr(s, 'geometry') else [s]
        v = g[0].visual if len(g) == 1 else None
        ohne_uv = v is not None and v.kind == 'texture' and getattr(v, 'uv', None) is None
        if not ohne_uv or 'color' not in v.vertex_attributes:
            return netz
        lin = np.clip(np.asarray(v.vertex_attributes['color'], dtype=np.float64)[:, :3], 0, 1)
        srgb = np.where(lin <= 0.0031308, 12.92 * lin, 1.055 * lin ** (1 / 2.4) - 0.055)
        farben = np.concatenate([np.round(srgb * 255), np.full((len(srgb), 1), 255)], 1).astype(np.uint8)
        ziel = netz.with_name(netz.stem + '_punktfarben.glb')
        trimesh.Trimesh(g[0].vertices, g[0].faces, vertex_colors=farben, process=False).export(ziel)
        return ziel

    @classmethod
    def anlegen(cls, name, netz, geschlecht, foto=None, maske=None):
        """Test aus Dateien anlegen → Kennung. Auch für `mesh3dai_test_anlegen.py`."""
        netz = cls.punktfarben(Path(netz))
        with open(netz, 'rb') as f:
            eingang = File(f, name=netz.name)
            if foto is None:
                return Mesh3dairechenschlange.anlegen(name, eingang, geschlecht)
            with open(foto, 'rb') as ff, open(maske, 'rb') as fm:
                bilder = File(ff, name=Path(foto).name), File(fm, name=Path(maske).name)
                return Mesh3dairechenschlange.anlegen(name, eingang, geschlecht, *bilder)

    @staticmethod
    def _groesse_setzen(kennung, groesse):
        """Die Körpergröße des Jobs an den Test: PSHuman rechnet maßstabsfrei, die Kette liest sie in `Mesh3daimeshziel.hoehe_test`. Vor dem Einreihen, darum `ordner()`: `pfad` kennt den Test erst mit seiner `test.json`."""
        if not groesse:
            return
        datei = Mesh3daitest.ordner() / kennung / 'einstellung.json'
        AtomarSchreiber.json_schreiben(datei, dict(json.loads(datei.read_text(encoding='utf-8')), koerpergroesse_m=float(groesse)))

    @classmethod
    def _gelenke_mitgeben(cls, kennung, ordner):
        """Die Gelenke aus den sechs Ansichten an den Test: Die Einpassung startet dann an ihnen statt an MIA. Vor dem Einreihen, wie `_groesse_setzen`."""
        quelle = Path(ordner) / cls.GELENKE
        if quelle.is_file():
            ziel = Mesh3daitest.ordner() / kennung / cls.GELENKE_TEST
            ziel.parent.mkdir(exist_ok=True)
            shutil.copyfile(quelle, ziel)

    @classmethod
    def starten(cls, job):
        """Test anlegen, einreihen und in die job.json schreiben → Kennung. `ValueError`, wenn etwas fehlt."""
        ordner = job['ordner']
        netz, foto, maske = cls.eingang(ordner)
        if netz is None:
            raise ValueError('Noch kein PSHuman-Netz — erst PSHuman rechnen')
        if not job.get('geschlecht'):
            raise ValueError('Erst das Geschlecht der Genesis-Figur wählen')
        kennung = cls.anlegen(Mesh3daijobtest.TESTNAME % ordner.name, netz, job['geschlecht'], foto, maske)
        cls._groesse_setzen(kennung, job.get('koerpergroesse_m'))
        cls._gelenke_mitgeben(kennung, ordner)
        Mesh3dairechenschlange.starten(kennung)
        datei = ordner / 'job.json'
        shutil.copyfile(datei, ordner / cls.SICHERUNG)
        info = json.loads(datei.read_text(encoding='utf-8'))
        info['mesh3dai_test'] = kennung
        AtomarSchreiber.json_schreiben(datei, info, einzug=1)
        logger.info('Ai2d3dgenesisstart: %s → Test %s (Foto %s)', ordner.name, kennung, foto)
        return kennung
