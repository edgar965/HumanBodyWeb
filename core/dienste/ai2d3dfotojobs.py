# -*- coding: utf-8 -*-
"""Ai2d3dfotojobs — Jobs von „2d-3d-AI“ aus echten Fotos (24.10.2026, Edgar: „auch echte Fotos, …\\Tripo\\Randy, …\\Tripo\\Ed\\2026, …\\Tripo\\zauberer“).

Echte Fotos haben keinen festen Namen und keine feste Zahl (Randy 4, Ed 8, Zauberer 8), keine bekannte Kamera und keine Wahrheit. Darum beschreibt je Job eine Datei
`3DObjects/ai2d3d/<Name>/job.json`, was dazugehört — die Fotos bleiben, wo sie liegen (nichts kopiert, nichts in Edgars Ordnern geschrieben):

    {"name": "Randy", "fotos": [{"datei": "A:\\\\…\\\\R1.jpg", "winkel": 0}, …], "netze": [{"art": "tripo3d", "datei": "…glb"}],
     "mesh3dai_test": "randy_tropical", "hinweis": "…", "koerpergroesse_m": 1.85}

`koerpergroesse_m`: Größe der Person, von Edgar angegeben (Feld oben auf der Testseite, `Ai2d3dkoerpergroesse`); fehlt = unbekannt.
`winkel` wie in `Ai2d3djobs` (0 vorne, 90 links, 180 hinten, 270 rechts; `null` unbekannt). `mesh3dai_test`: der Mesh3D-AI-Test zum selben Netz (dort steht heute das Genesis-Ergebnis).
"""

import json
import logging
from pathlib import Path

from django.conf import settings

from .ai2d3dkoerpergroesse import Ai2d3dkoerpergroesse
from .mesh3dainame import Mesh3dainame

logger = logging.getLogger('core')

__all__ = ['Ai2d3dfotojobs']


class Ai2d3dfotojobs:
    #: ohne Tripo3D (26.10.2026, Edgar: „lösche das Tripo mesh aus dem Job, sonst schummelst du wieder. Lösche Tripo Meshes aus allen Jobs … auch als Vergleichsnetz“) — ein Netz dieser Art
    #: zeigt und liefert 2d-3d-AI nicht mehr, auch wenn eine job.json oder ein Exportordner (`tripo3d/`) es noch nennt; die Dateien selbst bleiben (Eingang von Mesh3D-AI)
    NETZNAMEN = {'hunyuan3d': 'Hunyuan3D-2mv'}
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
            # Freigestellt auf weißem Grund (24.10.2026, `VideoToBVH/wrappers/_run_ai2d3d_freistellen.py`, BiRefNet wie 2D3D Kleider) — die Seite zeigt dann diese Fassung.
            frei = cls.ordner() / ordnername / 'freigestellt' / ('%d.png' % i)
            fotos.append({'name': f.get('name') or 'Bild %d' % (i + 1), 'pfad': frei if frei.is_file() else pfad, 'original': pfad, 'frei': frei.is_file(),
                          'winkel': int(winkel) % 360 if isinstance(winkel, (int, float)) else None})
        if not fotos:
            return None
        test = str(info['mesh3dai_test']) if info.get('mesh3dai_test') else None
        # eigener Name (Stift auf der Testseite, 24.10.2026) aus name.json über dem der job.json — wie Mesh3D-AI (`Mesh3dainame`)
        vorgabe = str(info.get('name') or ordnername)
        name = Mesh3dainame.lesen(cls.ordner() / ordnername) or vorgabe
        return {'id': ordnername.lower(), 'name': name, 'name_vorgabe': vorgabe, 'art': 'foto', 'figur': '', 'fotos': fotos, 'paar': None, 'ordner': cls.ordner() / ordnername,
                'test': test, 'wahrheit': False, 'netze': cls.netze([(n.get('art'), Path(str(n.get('datei') or ''))) for n in info.get('netze') or []]),
                'hinweis': str(info.get('hinweis') or ''), 'kopf': cls.kopf(cls.ordner() / ordnername), 'koerpergroesse_m': Ai2d3dkoerpergroesse.lesen(info)}

    @staticmethod
    def kopf(ordner):
        """Das Kopf-Ergebnis der KopfKI (`<Job>/kopfki/ergebnis.json`, 24.10.2026, Edgar: „Ich sehe keine Ergebnisse von Dir“) für die Karte „Kopf“ der Jobseite — Zahlen als Text
        („2,49 %“), Bilder mit Pfad (ausgeliefert nur über ihre Nummer, `Ai2d3ddatenendpunkte.kopfbild`). Ohne Datei: None."""
        datei = ordner / 'kopfki' / 'ergebnis.json'
        if not datei.is_file():
            return None
        try:
            k = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Ai2d3dfotojobs: %s nicht lesbar (%s)', datei, fehler)
            return None
        for z in k.get('zeilen', []):
            z['texte'] = [Ai2d3dfotojobs._zahl(w, ' %') for w in z.get('werte', [])]
        for g in k.get('gegenprobe', []):
            g['texte'] = {n: Ai2d3dfotojobs._zahl(g.get(n), ' mm' if n.endswith('_mm') else ' %')
                          for n in ('vorher_mm', 'nachher_mm', 'wahrheit_vorne_prozent', 'vorne_vorher_prozent', 'vorne_nachher_prozent')}
        k['bilder'] = [dict(b, pfad=datei.parent / b['datei']) for b in k.get('bilder', []) if (datei.parent / b['datei']).is_file()]
        return k

    @staticmethod
    def _zahl(wert, einheit):
        return '—' if wert is None else ('%.2f' % wert).replace('.', ',') + einheit

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
