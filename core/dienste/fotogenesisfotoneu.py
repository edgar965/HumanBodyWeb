# -*- coding: utf-8 -*-
"""Fotogenesisfotoneu — „Neuer Test aus Fotos“ im Reiter „Test“ von `/foto-genesis/` (24.10.2026; Gegenstück zu „Neuer Test aus einem Mesh“ auf `/mesh-genesis/`, `Meshgenesisrechenschlange.anlegen`).

Legt `3DObjects/fotogenesis/<Name>/` an: die hochgeladenen Fotos unter `fotos/` und eine `job.json` für `Fotogenesisfotojobs` (Winkel unbekannt — `null`, bis jemand sie einträgt). Gerechnet wird noch nichts:
Foto-Genesis hat noch keine eigene KI (Weg B des Konzepts). Ein vorhandener Ordner wird nie überschrieben.
"""

import json
import logging
import re

from .fotogenesisfotojobs import Fotogenesisfotojobs

logger = logging.getLogger('core')

__all__ = ['Fotogenesisfotoneu']


class Fotogenesisfotoneu:
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
        ordner = Fotogenesisfotojobs.ordner() / ordnername
        if ordner.exists():
            raise ValueError('Es gibt schon einen Test „%s“' % ordnername)
        for d in dateien:
            if '.' + d.name.rsplit('.', 1)[-1].lower() not in Fotogenesisfotojobs.BILDENDUNGEN:
                raise ValueError('%s ist kein Foto (erlaubt: %s)' % (d.name, ', '.join(Fotogenesisfotojobs.BILDENDUNGEN)))
            if d.size > cls.GROESSE_MAX:
                raise ValueError('%s ist größer als %d MB' % (d.name, cls.GROESSE_MAX // (1024 * 1024)))
        (ordner / 'fotos').mkdir(parents=True)
        fotos = []
        for i, d in enumerate(dateien):
            # Endung bleibt: bis 04.11.2026 machte NAME aus „bild.png“ „bild_png“ — `Fotogenesisfotojobs._job`
            # verwarf das Foto (keine Bildendung), der Test hatte keine Fotos und die Seite gab 404
            stamm, _punkt, endung = d.name.rpartition('.')
            ziel = ordner / 'fotos' / ('%02d_%s.%s' % (i + 1, cls.NAME.sub('_', stamm), endung.lower()))
            with open(ziel, 'wb') as aus:
                for stueck in d.chunks():
                    aus.write(stueck)
            fotos.append({'datei': str(ziel), 'winkel': None})
        info = {'name': str(name or ordnername), 'fotos': fotos, 'netze': [], 'meshgenesis_test': None,
                'hinweis': 'Hochgeladen auf /foto-genesis/. Winkel der Fotos noch nicht eingetragen (0 vorne, 90 links, 180 hinten, 270 rechts).'}
        (ordner / 'job.json').write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        logger.info('Fotogenesisfotoneu: Test %s mit %d Fotos angelegt (%s)', ordnername, len(fotos), ordner)
        return ordnername.lower()
