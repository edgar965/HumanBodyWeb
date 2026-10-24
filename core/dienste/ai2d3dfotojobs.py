# -*- coding: utf-8 -*-
"""Ai2d3dfotojobs — Jobs von „2d-3d-AI“ aus echten Fotos (24.10.2026, Edgar: „auch echte Fotos, …\\Tripo\\Randy, …\\Tripo\\Ed\\2026, …\\Tripo\\zauberer“).

Echte Fotos haben keinen festen Namen und keine feste Zahl (Randy 4, Ed 8, Zauberer 8), keine bekannte Kamera und keine Wahrheit. Darum beschreibt je Job eine Datei
`3DObjects/ai2d3d/<Name>/job.json`, was dazugehört — die Fotos bleiben, wo sie liegen (nichts kopiert, nichts in Edgars Ordnern geschrieben):

    {"name": "Randy", "fotos": [{"datei": "A:\\\\…\\\\R1.jpg", "winkel": 0}, …], "netze": [{"art": "tripo3d", "datei": "…glb"}],
     "mesh3dai_test": "randy_tropical", "hinweis": "…"}

`winkel` wie in `Ai2d3djobs` (0 vorne, 90 links, 180 hinten, 270 rechts; `null` unbekannt). `mesh3dai_test`: der Mesh3D-AI-Test zum selben Netz (dort steht heute das Genesis-Ergebnis).
"""

import json
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Ai2d3dfotojobs']


class Ai2d3dfotojobs:
    NETZNAMEN = {'hunyuan3d': 'Hunyuan3D-2mv', 'tripo3d': 'Tripo3D'}
    BILDENDUNGEN = ('.jpg', '.jpeg', '.png', '.webp')

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'ai2d3d'

    @classmethod
    def alle(cls):
        jobs = []
        for datei in sorted(cls.ordner().glob('*/job.json')):
            try:
                info = json.loads(datei.read_text(encoding='utf-8'))
            except (OSError, ValueError) as fehler:
                logger.warning('Ai2d3dfotojobs: %s nicht lesbar (%s)', datei, fehler)
                continue
            job = cls._job(datei.parent.name, info)
            if job:
                jobs.append(job)
        return jobs

    @classmethod
    def _job(cls, ordnername, info):
        fotos = []
        for i, f in enumerate(info.get('fotos') or []):
            pfad = Path(str(f.get('datei') or ''))
            if pfad.suffix.lower() not in cls.BILDENDUNGEN or not pfad.is_file():
                logger.warning('Ai2d3dfotojobs: %s — Foto %s fehlt', ordnername, pfad)
                continue
            winkel = f.get('winkel')
            fotos.append({'name': f.get('name') or 'Bild %d' % (i + 1), 'pfad': pfad, 'winkel': int(winkel) % 360 if isinstance(winkel, (int, float)) else None})
        if not fotos:
            return None
        test = str(info['mesh3dai_test']) if info.get('mesh3dai_test') else None
        return {'id': ordnername.lower(), 'name': str(info.get('name') or ordnername), 'art': 'foto', 'figur': '', 'fotos': fotos, 'paar': None, 'ordner': cls.ordner() / ordnername,
                'test': test, 'wahrheit': False, 'netze': cls.netze([(n.get('art'), Path(str(n.get('datei') or ''))) for n in info.get('netze') or []]),
                'hinweis': str(info.get('hinweis') or '')}

    @classmethod
    def netze(cls, kandidaten):
        """`[(art, pfad)]` → `[{art, name, pfad, bytes}]`: je Art das erste vorhandene GLB, in der gegebenen Reihenfolge."""
        netze, arten = [], set()
        for art, pfad in kandidaten:
            if art not in cls.NETZNAMEN or art in arten or pfad.suffix.lower() != '.glb' or not pfad.is_file():
                continue
            arten.add(art)
            netze.append({'art': art, 'name': cls.NETZNAMEN[art], 'pfad': pfad, 'bytes': pfad.stat().st_size})
        return netze
