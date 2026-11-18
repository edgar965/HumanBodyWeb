# -*- coding: utf-8 -*-
"""G9fotohaut — die Haut eines Foto-Genesis-Jobs als Hautsatz von Genesis 9 (18.11.2026).

Edgar, 18.11.2026: „dann möchte ich die n1 Haut in der Bibliothek haben und mit den Reglern ausprobieren“ (Regler: `G9hautausgleich`). Je Foto-Job
(`3DObjects/fotogenesis/<Job>/job.json`) die Hautkacheln seines Mesh-Genesis-Tests (`meshgenesis_test` → `_test/<Test>/haut_<geschlecht>/1001…1004.jpg`,
geschrieben vom Schritt „Haut“, mit oder ohne Haut-KI). Der Hautsatz ist der der Grundfigur (`G9 Feminine/Masculine Skin 01 MAT`: Normalen, Rauheit,
Durchlicht) mit den Kacheln des Jobs als Albedo — wie `G9bedlamhaut`; die Diffusfarbe fällt weg, der Ton steckt in der Kachel (wie `Genesis9fototextur`).

Die Kacheln werden in die eigene Bibliothek kopiert, `Runtime/Textures/FOTOHAUT/<Job>/<Stand>_<Kachel>.jpg` — der Stand (Test, Größe, Zeit von `haut.json`)
steht im Namen, ein neu gerechneter Job bekommt neue Dateien statt still der alten. Kennung `foto:<Job>`.
"""
import copy
import hashlib
import json
import logging
import shutil
from pathlib import Path

from django.conf import settings
from Genesis9.hautpresets import G9hautpresets

logger = logging.getLogger('core')

__all__ = ['G9fotohaut']


class G9fotohaut:
    """Anbieter von Hautsätzen für `G9hautpresets` (`anbieten`)."""

    PRAEFIX = 'foto:'
    FASSUNG = 1
    GRUPPEN = ('Head', 'Body', 'Arms', 'Legs')
    GESCHLECHTER = (('weiblich', 'weiblich'), ('maennlich', 'männlich'))
    GRUND = {'weiblich': 'G9 Feminine Skin 01 MAT', 'männlich': 'G9 Masculine Skin 01 MAT'}

    @staticmethod
    def _jobs():
        return Path(settings.OBJECTS_ROOT) / 'fotogenesis'

    @staticmethod
    def _tests():
        return Path(settings.OBJECTS_ROOT) / 'meshgenesis' / '_test'

    @classmethod
    def gehoert(cls, preset):
        return str(preset or '').startswith(cls.PRAEFIX)

    @classmethod
    def _haut(cls, job):
        """(Ordner `haut_<geschlecht>`, Geschlecht der Anzeige) des Tests eines Jobs — oder (None, None)."""
        try:
            test = json.loads((cls._jobs() / job / 'job.json').read_text(encoding='utf-8')).get('meshgenesis_test')
        except (OSError, ValueError):
            return None, None
        if not test:
            return None, None
        for ordnername, anzeige in cls.GESCHLECHTER:
            ordner = cls._tests() / str(test) / ('haut_%s' % ordnername)
            if (ordner / 'haut.json').is_file() and all((ordner / ('%d.jpg' % k)).is_file() for k in (1001, 1002, 1003, 1004)):
                return ordner, anzeige
        return None, None

    @classmethod
    def praesets(cls):
        """`[{id, name, geschlecht, vorschau}]` — je Foto-Job mit Hautkacheln ein Eintrag."""
        if not cls._jobs().is_dir():
            return []
        aus = []
        for job in sorted(p.name for p in cls._jobs().iterdir() if p.is_dir()):
            ordner, anzeige = cls._haut(job)
            if ordner is not None:
                aus.append({'id': cls.PRAEFIX + job, 'name': 'Foto · %s (%s)' % (job, anzeige), 'geschlecht': anzeige, 'vorschau': False})
        return aus

    @classmethod
    def bilder(cls, preset):
        """Die Bilder des Hautsatzes je Gruppe (wie `G9hautpresets.haut`) — oder {}."""
        job = str(preset)[len(cls.PRAEFIX):]
        if not job or '/' in job or '\\' in job or job.startswith('.'):
            return {}
        ordner, anzeige = cls._haut(job)
        if ordner is None:
            return {}
        kacheln = cls._kopieren(job, ordner)
        aus = copy.deepcopy(G9hautpresets.haut(cls.GRUND[anzeige]))
        for gruppe, kachel in cls._kachel_je_gruppe().items():
            if gruppe in aus and kachel in kacheln:
                aus[gruppe]['albedo'] = kacheln[kachel]
                aus[gruppe].pop('farbe', None)
        return aus

    @staticmethod
    def _kachel_je_gruppe():
        from Genesis9.basisnetz import G9basisnetz
        return {g['name']: int(g['kachel']) for g in G9basisnetz.netzstufe(0).gruppen if g.get('name') in G9fotohaut.GRUPPEN}

    @classmethod
    def _kopieren(cls, job, ordner):
        """`{kachel: Pfad relativ zur eigenen Bibliothek}` — kopiert, was für diesen Stand noch fehlt."""
        from Genesis9.pfade import G9pfade
        s = (ordner / 'haut.json').stat()
        stand = hashlib.sha1(('v%d|%s|%d|%d' % (cls.FASSUNG, ordner.parent.name, s.st_size, int(s.st_mtime))).encode('utf-8')).hexdigest()[:10]
        ziel = G9pfade.eigene() / 'Runtime' / 'Textures' / 'FOTOHAUT' / job
        aus = {}
        for kachel in (1001, 1002, 1003, 1004):
            datei = ziel / ('%s_%d.jpg' % (stand, kachel))
            if not datei.is_file():
                ziel.mkdir(parents=True, exist_ok=True)
                vorlaeufig = datei.with_name(datei.stem + '.neu.jpg')
                shutil.copyfile(ordner / ('%d.jpg' % kachel), vorlaeufig)
                vorlaeufig.replace(datei)
                logger.info('Foto-Haut %s: Kachel %d aus %s', job, kachel, ordner)
            aus[kachel] = 'Runtime/Textures/FOTOHAUT/%s/%s' % (job, datei.name)
        return aus


G9hautpresets.anbieten(G9fotohaut)           # beim ersten Import als Anbieter von Hautsätzen eintragen
