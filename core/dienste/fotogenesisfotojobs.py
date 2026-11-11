# -*- coding: utf-8 -*-
"""Fotogenesisfotojobs — Jobs von „Foto-Genesis“ aus echten Fotos (24.10.2026, Edgar: „auch echte Fotos, …\\Tripo\\Randy, …\\Tripo\\Ed\\2026, …\\Tripo\\zauberer“).

Echte Fotos haben keinen festen Namen und keine feste Zahl (Randy 4, Ed 8, Zauberer 8), keine bekannte Kamera und keine Wahrheit. Darum beschreibt je Job eine Datei
`3DObjects/fotogenesis/<Name>/job.json`, was dazugehört — die Fotos bleiben, wo sie liegen (nichts kopiert, nichts in Edgars Ordnern geschrieben):

    {"name": "Randy", "fotos": [{"datei": "A:\\\\…\\\\R1.jpg", "winkel": 0}, …], "netze": [{"art": "tripo3d", "datei": "…glb"}],
     "meshgenesis_test": "randy_tropical", "hinweis": "…", "koerpergroesse_m": 1.85}

`koerpergroesse_m`: Größe der Person, von Edgar angegeben (Feld oben auf der Testseite, `Fotogenesiskoerpergroesse`); fehlt = unbekannt.
`winkel` wie in `Fotogenesisjobs` (0 vorne, 90 links, 180 hinten, 270 rechts; `null` unbekannt). `meshgenesis_test`: der Mesh-Genesis-Test zum selben Netz (dort steht heute das Genesis-Ergebnis).
"""

import json
import logging
from pathlib import Path

from django.conf import settings

from .fotogenesisform import Fotogenesisform
from .fotogenesisgeschlecht import Fotogenesisgeschlecht
from .fotogenesiskoerpergroesse import Fotogenesiskoerpergroesse
from .fotogenesisnormalen import Fotogenesisnormalen
from .fotogenesispshuman import Fotogenesispshuman
from .fotogenesispshumaneingabe import Fotogenesispshumaneingabe
from .fotogenesistextur import Fotogenesistextur
from .meshgenesisname import Meshgenesisname

logger = logging.getLogger('core')

__all__ = ['Fotogenesisfotojobs']


class Fotogenesisfotojobs:
    #: ohne Tripo3D (26.10.2026, Edgar: „lösche das Tripo mesh aus dem Job, sonst schummelst du wieder. Lösche Tripo Meshes aus allen Jobs … auch als Vergleichsnetz“) — ein Netz dieser Art
    #: zeigt und liefert Foto-Genesis nicht mehr, auch wenn eine job.json oder ein Exportordner (`tripo3d/`) es noch nennt; die Dateien selbst bleiben (Eingang von Mesh-Genesis)
    #: 'pshuman' (03.11.2026, Edgar: „mach einen Job, so dass man die volle Qualität sehen kann mit PS Human“):
    #: PSHumans eigene Rekonstruktion aus EINEM Foto, nur zum Ansehen
    #: 'pshuman_smplx' (03.11.2026, Edgar: „im Job mach als zusätzliche 4. View in jeder Zeile das SMPLX
    #: modell bei pshuman jobs, zum testen“): PSHumans eingepasstes SMPL-X (Start der freien Netzformung) —
    #: nicht im Feld „Netz“, sondern eigenes Feld jeder Zeile (`Fotogenesisseitendaten.STARTKOERPER`). Seit 07.11.2026 'pshuman_start': Genesis statt SMPL-X, alte Jobs und UP2You behalten `pshuman_smplx`
    #: 'pshuman_apose' (10.11.2026, Edgar: „mach doch das pshuman mesh und die genesis ausgabe in allen jobs auf die A-Pose“): dasselbe Netz in der A-Pose (`pshuman_port14/pshuman_apose.py`), nur fürs Feld „PSHuman“
    NETZNAMEN = {'hunyuan3d': 'Hunyuan3D-2mv', 'pshuman': 'PSHuman (1 Foto)',
                 'pshuman_smplx': 'SMPL-X (PSHuman)', 'pshuman_start': 'Startkörper (Genesis)', 'pshuman_apose': 'PSHuman in der A-Pose',
                 'pshuman_lhm': 'PSHuman mit LHM++-Farbe'}   # 11.11.2026: Probe LHM++ (`Fotogenesisseitendaten.PSHUMAN_LHM`)
    BILDENDUNGEN = ('.jpg', '.jpeg', '.png', '.webp')

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'fotogenesis'

    @classmethod
    def alle(cls):
        jobs = []
        for datei in sorted(cls.ordner().glob('*/job.json')):
            try:
                info = json.loads(datei.read_text(encoding='utf-8'))
            except (OSError, ValueError) as fehler:
                logger.warning('Fotogenesisfotojobs: %s nicht lesbar (%s)', datei, fehler)
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
                logger.warning('Fotogenesisfotojobs: %s — Foto %s fehlt', ordnername, pfad)
                continue
            winkel = f.get('winkel')
            # Freigestellt auf weißem Grund (24.10.2026, `VideoToBVH/wrappers/_run_fotogenesis_freistellen.py`, BiRefNet wie 2D3D Kleider) — die Seite zeigt dann diese Fassung.
            frei = cls.ordner() / ordnername / 'freigestellt' / ('%d.png' % i)
            fotos.append({'name': f.get('name') or 'Bild %d' % (i + 1), 'pfad': frei if frei.is_file() else pfad, 'original': pfad, 'frei': frei.is_file(),
                          'winkel': int(winkel) % 360 if isinstance(winkel, (int, float)) else None})
        if not fotos:
            return None
        test = str(info['meshgenesis_test']) if info.get('meshgenesis_test') else None
        # eigener Name (Stift auf der Testseite, 24.10.2026) aus name.json über dem der job.json — wie Mesh-Genesis (`Meshgenesisname`)
        vorgabe = str(info.get('name') or ordnername)
        name = Meshgenesisname.lesen(cls.ordner() / ordnername) or vorgabe
        return {'id': ordnername.lower(), 'name': name, 'name_vorgabe': vorgabe, 'art': 'foto', 'figur': '', 'fotos': fotos, 'paar': None, 'ordner': cls.ordner() / ordnername,
                'test': test, 'wahrheit': False, 'netze': cls.netze([(n.get('art'), Path(str(n.get('datei') or ''))) for n in info.get('netze') or []]),
                'hinweis': str(info.get('hinweis') or ''), 'kopf': cls.kopf(cls.ordner() / ordnername), 'koerpergroesse_m': Fotogenesiskoerpergroesse.lesen(info), 'geschlecht': Fotogenesisgeschlecht.lesen(info),
                'normalen': Fotogenesisnormalen.lesen(info),  # Combo-Boxen „Normalen“, „Textur“ (03.11.)
                'textur': Fotogenesistextur.lesen(info), 'form': Fotogenesisform.lesen(info),
                'pshuman': dict(Fotogenesispshuman.lesen(info),
                                gerechnet=Fotogenesispshuman.gerechnet(cls.ordner() / ordnername),
                                eingabe=Fotogenesispshumaneingabe.lesen(cls.ordner() / ordnername, info, fotos))}

    @staticmethod
    def kopf(ordner):
        """Das Kopf-Ergebnis der KopfKI (`<Job>/kopfki/ergebnis.json`, 24.10.2026, Edgar: „Ich sehe keine Ergebnisse von Dir“) für die Karte „Kopf“ der Jobseite — Zahlen als Text
        („2,49 %“), Bilder mit Pfad (ausgeliefert nur über ihre Nummer, `Fotogenesisdatenendpunkte.kopfbild`). Ohne Datei: None."""
        datei = ordner / 'kopfki' / 'ergebnis.json'
        if not datei.is_file():
            return None
        try:
            k = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError) as fehler:
            logger.warning('Fotogenesisfotojobs: %s nicht lesbar (%s)', datei, fehler)
            return None
        for z in k.get('zeilen', []):
            z['texte'] = [Fotogenesisfotojobs._zahl(w, ' %') for w in z.get('werte', [])]
        for g in k.get('gegenprobe', []):
            g['texte'] = {n: Fotogenesisfotojobs._zahl(g.get(n), ' mm' if n.endswith('_mm') else ' %')
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
