# -*- coding: utf-8 -*-
"""Ai2d3dfotoneu — „Neuer Test aus Fotos“ im Reiter „Test“ von `/2d-3d-AI/` (24.10.2026; Gegenstück zu „Neuer Test aus einem Mesh“ auf `/mesh-3D-AI/`, `Mesh3dairechenschlange.anlegen`).

Legt `3DObjects/ai2d3d/<Name>/` an: die hochgeladenen Fotos unter `fotos/` und eine `job.json` für `Ai2d3dfotojobs` (Winkel unbekannt — `null`, bis jemand sie einträgt). Gerechnet wird noch nichts:
2d-3d-AI hat noch keine eigene KI (Weg B des Konzepts). Ein vorhandener Ordner wird nie überschrieben.
"""

import json
import logging
import re

from .ai2d3dfotojobs import Ai2d3dfotojobs

logger = logging.getLogger('core')

__all__ = ['Ai2d3dfotoneu']


class Ai2d3dfotoneu:
    #: Höchstens so viele Fotos und so groß je Foto (Edgars Fotos: 8 PNG zu 1,8–4,2 MB).
    HOECHSTENS = 24
    GROESSE_MAX = 40 * 1024 * 1024
    NAME = re.compile(r'[^A-Za-z0-9_-]+')

    @classmethod
    def anlegen(cls, name, dateien):
        """→ Kennung des neuen Tests. `ValueError` mit Text für die Seite, wenn etwas nicht passt."""
        if not dateien:
            raise ValueError('Keine Fotos')
        if len(dateien) > cls.HOECHSTENS:
            raise ValueError('Höchstens %d Fotos' % cls.HOECHSTENS)
        ordnername = cls.NAME.sub('', str(name or '').replace(' ', '_'))[:60] or cls.NAME.sub('', dateien[0].name.rsplit('.', 1)[0])[:60]
        if not ordnername:
            raise ValueError('Kein Name')
        ordner = Ai2d3dfotojobs.ordner() / ordnername
        if ordner.exists():
            raise ValueError('Es gibt schon einen Test „%s“' % ordnername)
        for d in dateien:
            if '.' + d.name.rsplit('.', 1)[-1].lower() not in Ai2d3dfotojobs.BILDENDUNGEN:
                raise ValueError('%s ist kein Foto (erlaubt: %s)' % (d.name, ', '.join(Ai2d3dfotojobs.BILDENDUNGEN)))
            if d.size > cls.GROESSE_MAX:
                raise ValueError('%s ist größer als %d MB' % (d.name, cls.GROESSE_MAX // (1024 * 1024)))
        (ordner / 'fotos').mkdir(parents=True)
        fotos = []
        for i, d in enumerate(dateien):
            ziel = ordner / 'fotos' / ('%02d_%s' % (i + 1, cls.NAME.sub('_', d.name)))
            with open(ziel, 'wb') as aus:
                for stueck in d.chunks():
                    aus.write(stueck)
            fotos.append({'datei': str(ziel), 'winkel': None})
        info = {'name': str(name or ordnername), 'fotos': fotos, 'netze': [], 'mesh3dai_test': None,
                'hinweis': 'Hochgeladen auf /2d-3d-AI/. Winkel der Fotos noch nicht eingetragen (0 vorne, 90 links, 180 hinten, 270 rechts).'}
        (ordner / 'job.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        logger.info('Ai2d3dfotoneu: Test %s mit %d Fotos angelegt (%s)', ordnername, len(fotos), ordner)
        return ordnername.lower()
