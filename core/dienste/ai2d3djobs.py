# -*- coding: utf-8 -*-
"""Ai2d3djobs — die Jobs von „2d-3d-AI“ (24.10.2026): Fotos rein, Genesis-Modell raus.

Edgar: „ein Konzept für das Erstellen eines 3D Modells aus Fotos, mit einer KI … als Eingabe kommen die Fotos (so wie die Fotos aus einigen der Jobs der Mesh3d-AI Kette), als Ausgabe ein Genesis Modell …
passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell und das Ergebnis zu sehen ist“ — dazu „auch echte Fotos“ (Randy, Ed/2026, Zauberer).

Zwei Arten, eine Form (`{id, name, art, figur, fotos: [{name, pfad, winkel}], netze, paar, test, wahrheit, hinweis}`):
- **Export** (`art = export`, mit Wahrheit): ein Ordner unter `3DObjects/modelsExport/` mit `<Stamm>.json` und den vier Aufnahmen `<Stamm>_vorne|links|rechts|hinten.jpg` (`Modellansichten`:
  1536 × 2048, 20°, Kamera aus der Hülle der Figur). Netz: Hunyuan3D-2mv aus genau diesen Fotos (`mesh3dai/_bild3d/<Paar>_tripovergleich/…/mesh.glb` oder `<Job>/hunyuan3d/*.glb`), dann Tripo3D
  (`<Job>/tripo3d/*.glb`). `paar` = der Mesh3D-AI-Job, dessen `paar.json` diese JSON als Quelle nennt — sein Ergebnis ist heute das Genesis-Modell der Seite (Messlatte A: Tripo-Netz → Mesh3D-AI).
  Ein neuer Export mit vier Fotos erscheint ohne Eintrag im Code.
- **Foto** (`art = foto`, ohne Wahrheit): `Ai2d3dfotojobs`, je Job eine `job.json` unter `3DObjects/ai2d3d/`.

`winkel` je Foto: Standort der Kamera um die Figur in Grad — 0 vorne, 90 links (Kamera bei +X, die linke Körperseite), 180 hinten, 270 rechts (`Modellansichten.ANSICHTEN`); `None` = unbekannt.
"""

import copy
import json
import logging
import threading
import time
from pathlib import Path

from django.conf import settings

from .ai2d3dadresse import Ai2d3dadresse
from .ai2d3dfotojobs import Ai2d3dfotojobs
from .ai2d3dpapierkorb import Ai2d3dpapierkorb

logger = logging.getLogger('core')

__all__ = ['Ai2d3djobs']


class Ai2d3djobs:
    ANSICHTEN = (('vorne', 0), ('links', 90), ('rechts', 270), ('hinten', 180))
    #: Ablage von `alle()` (08.11.2026, Edgar: „alle modelle sollen innerhalb von max. 5 s angezeigt werden“): Jede Anfrage der Jobseite fragt `job(<id>)`, und das las jedes Mal alle
    #: Exporte, alle `paar.json` von Mesh3D-AI und alle Foto-Jobs von der Platte — gemessen im Log vom 07.11.2026 23:04 rund 0,45 s je Anfrage bei ~46 Anfragen je Seitenaufruf, am
    #: 08.11.2026 01:35–02:13 bei Plattenlast durch einen Virenscan 26–290 s je Anfrage (py-spy: Fäden in `_paare`/`_figurname`). Gilt höchstens FRISCH_S lang; eine geänderte
    #: `job.json`/`name.json` oder Ausblendliste (Schlüssel `_stand`) baut sofort neu. Was nicht im Schlüssel steht (PSHuman fertig, Kopf-Ergebnis, Netze), zeigt sich nach FRISCH_S.
    FRISCH_S = 3.0
    _ablage = None          # (Stand, Zeit, Jobs)
    _sperre = threading.Lock()

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'modelsExport'

    @staticmethod
    def mesh3dai():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai'

    @classmethod
    def alle(cls):
        """Exporte (Reiter „Jobs“) und echte Fotos (Reiter „Test“); ausgeblendete Exporte (`Ai2d3dpapierkorb`) fehlen. Aus der Ablage (`FRISCH_S`), als Kopie: Aufrufer dürfen die
        Einträge verändern, ohne sie für die nächste Anfrage zu verändern. Gleichzeitige Anfragen warten auf EINE Rechnung."""
        with cls._sperre:
            stand = cls._stand()
            a = cls._ablage
            if a is None or a[0] != stand or time.monotonic() - a[1] > cls.FRISCH_S:
                a = cls._ablage = (stand, time.monotonic(), cls._alle_lesen())
            return copy.deepcopy(a[2])

    @classmethod
    def vergessen(cls):
        """Die Ablage verwerfen (Tests, Löschen)."""
        with cls._sperre:
            cls._ablage = None

    @classmethod
    def _stand(cls):
        """Zeitstempel der Dateien, deren Änderung sofort sichtbar sein muss: `job.json` und `name.json` der Foto-Jobs, die Ausblendliste der Exporte, die Liste der Exportordner."""
        werte = []
        for muster in ('*/job.json', '*/name.json'):
            for p in Ai2d3dfotojobs.ordner().glob(muster):
                try:
                    werte.append((str(p), p.stat().st_mtime_ns))
                except OSError:
                    pass
        for p in (Ai2d3dpapierkorb.wurzel() / Ai2d3dpapierkorb.AUSGEBLENDET, cls.ordner(), Ai2d3dfotojobs.ordner()):
            try:
                werte.append((str(p), p.stat().st_mtime_ns))
            except OSError:
                werte.append((str(p), None))
        return tuple(sorted(werte, key=lambda w: w[0]))

    @classmethod
    def _alle_lesen(cls):
        jobs = []
        wurzel = cls.ordner()
        if wurzel.is_dir():
            paare, weg = cls._paare(), Ai2d3dpapierkorb.ausgeblendet()
            jobs = [j for j in (cls._job(o, paare) for o in sorted(p for p in wurzel.iterdir() if p.is_dir())) if j and j['id'] not in weg]
        bekannt = {j['id'] for j in jobs}
        return Ai2d3dadresse.vergeben(jobs + [j for j in Ai2d3dfotojobs.alle() if j['id'] not in bekannt])

    @classmethod
    def exporte(cls):
        return [j for j in cls.alle() if j['art'] == 'export']

    @classmethod
    def tests(cls):
        return [j for j in cls.alle() if j['art'] == 'foto']

    @classmethod
    def job(cls, kennung):
        """Der Job zu seiner Kennung oder zu seiner Adresse (`Ai2d3dadresse`), sonst `None`."""
        gesucht = str(kennung).lower()
        return next((j for j in cls.alle() if gesucht in (j['id'], j['adresse'])), None)

    @classmethod
    def _job(cls, ordner, paare):
        """Ein Ordner ist ein Job, wenn ein Stamm alle vier Fotos und seine JSON hat; sonst `None` (kein Job, kein Fehler)."""
        for beschreibung in sorted(ordner.glob('*.json')):
            stamm = beschreibung.stem
            fotos = [{'name': a, 'pfad': ordner / ('%s_%s.jpg' % (stamm, a)), 'winkel': w} for a, w in cls.ANSICHTEN]
            if all(f['pfad'].is_file() for f in fotos):
                paar = paare.get(beschreibung.resolve())
                return {'id': ordner.name.lower(), 'name': ordner.name, 'art': 'export', 'figur': cls._figurname(beschreibung), 'fotos': fotos, 'paar': paar,
                        'test': None, 'wahrheit': True, 'netze': cls._netze(ordner, paar), 'hinweis': '', 'koerpergroesse_m': None}
        return None

    @staticmethod
    def _figurname(beschreibung):
        try:
            figur = json.loads(beschreibung.read_text(encoding='utf-8')).get('figur') or {}
        except (OSError, ValueError) as fehler:
            logger.warning('Ai2d3djobs: %s nicht lesbar (%s)', beschreibung, fehler)
            return ''
        return str(figur.get('figur') or figur.get('presetName') or '')

    @classmethod
    def _netze(cls, ordner, paar):
        """Die Netze aus den Fotos: Hunyuan3D-2mv. `[{art, name, pfad, bytes}]`. Tripo3D nicht mehr (26.10.2026, Edgar: „Lösche Tripo Meshes aus allen Jobs … auch als
        Vergleichsnetz“) — der Ordner `<Job>/tripo3d/` bleibt, er gehört zu Mesh3D-AI."""
        kandidaten = []
        if paar:
            kandidaten.append(('hunyuan3d', cls.mesh3dai() / '_bild3d' / ('%s_tripovergleich' % paar['ordner']) / 'mesh' / 'ergebnis' / 'mesh.glb'))
        kandidaten += [('hunyuan3d', p) for p in sorted((ordner / 'hunyuan3d').glob('*.glb'))]
        return Ai2d3dfotojobs.netze(kandidaten)

    @classmethod
    def _paare(cls):
        """`{Pfad der Export-JSON: {kennung, ordner, name}}` aus den `paar.json` von Mesh3D-AI (Trainingspaare, `Mesh3daipaare`)."""
        paare = {}
        for marke in cls.mesh3dai().glob('*/paar.json'):
            try:
                info = json.loads(marke.read_text(encoding='utf-8'))
                pfad = Path(info['quellen']['json']['pfad']).resolve()
            except (OSError, ValueError, KeyError, TypeError) as fehler:
                logger.warning('Ai2d3djobs: %s ohne Quelle (%s)', marke, fehler)
                continue
            paare[pfad] = {'kennung': str(info.get('kennung') or marke.parent.name.lower()), 'ordner': marke.parent.name, 'name': info.get('name') or marke.parent.name}
        return paare
