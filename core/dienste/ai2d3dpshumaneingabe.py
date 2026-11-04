# -*- coding: utf-8 -*-
"""Ai2d3dpshumaneingabe — die Bildplätze der PSHuman-Eingabe auf der Testseite von 2d-3d-AI (03.11.2026).

Edgar: „mach im job ein UI das entweder eines oder mehrere Bilder nimmt, mach vorschlag, wie die sein sollten,
z.B. Umriss vom Körper, mit Upload möglichkeit für alle. Wenn ein Bild als Input, dann zeige die erzeugten
bilder von pshuman“ — „passe das an mit deinem Vorschlag“.

Sechs Plätze = die sechs Ansichten, die PSHumans Rekonstruktion bekommt (`reconstruct.py` Z. 74 und 84:
front_face, front_right, right, back, left, front_left; Kameras `six_human_pose` 0, 1, 2, 4, 6, 7, je 45°).
Winkel wie die Fotojobs (`job.json` `fotos[].winkel`): 90 = linke Körperseite, die Person blickt im Bild nach
links (EdgarTrip 4.jpg). PSHumans „right“ ist diese Ansicht — am 03.11.2026 an Edgar_1Foto geprüft: in
`rekon/rembg/farbe_2_right.png` blickt die Person nach links und trägt die Uhr am linken Handgelenk wie in
4.jpg; „left“ (nach dem Spiegeln) blickt nach rechts wie 3.jpg (Winkel 270).

Je Platz: ein eigenes Bild (hochgeladen nach `<Job>/pshuman/eingabe/w<winkel><endung>`, job.json
`pshuman.eingabe` {"<winkel>": Pfad}), sonst das Foto des Jobs mit diesem Winkel (nur `fotos`, nie die
zurückgehaltenen `pruefung`), sonst leer. Dazu die von PSHuman erzeugte Farb- und Normalenansicht, wenn
gerechnet (`<Job>/pshuman/rekon/rembg/{farbe|normale}_<nr>_<ansicht>.png` — die Bilder, die die
Rekonstruktion bekommt, nach rembg). Ein ersetztes oder entferntes eigenes Bild bleibt als
`w<winkel>.vor_<Zeit><endung>` liegen (nie gelöscht).
"""

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger('core')

__all__ = ['Ai2d3dpshumaneingabe']


class Ai2d3dpshumaneingabe:
    #: (Winkel, Name, PSHuman-Ansicht, Nummer in PSHuman)
    PLAETZE = ((0, 'vorn', 'front_face', 0), (45, 'vorn-links', 'front_right', 1),
               (90, 'linke Seite', 'right', 2), (180, 'hinten', 'back', 3),
               (270, 'rechte Seite', 'left', 4), (315, 'vorn-rechts', 'front_left', 5))
    ENDUNGEN = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
    GROESSE_MAX = 40 * 2 ** 20
    ARTEN = ('eingabe', 'farbe', 'normale')
    #: Vorschlag, wie die Fotos sein sollten — Punkt 4 folgt aus der Rekonstruktion (EINE Figur, aus allen
    #: Ansichten zugleich geschnitzt), die übrigen sind Vorschlag
    VORSCHLAG = (
        '„vorn“ ist Pflicht. Jedes weitere Foto ersetzt eine Ansicht, die PSHuman sonst erfindet.',
        'Ganzer Körper von Kopf bis Fuß im Bild, mit etwas Rand, Person in der Mitte.',
        'Stehend, Arme etwas vom Körper weg, Beine leicht auseinander, Blick geradeaus — wie der Umriss.',
        'In allen Fotos dieselbe Haltung: die Rekonstruktion schnitzt EINE Figur aus allen Ansichten.',
        'Kamera auf Hüft- bis Brusthöhe, 2–3 m Abstand, nicht nah mit Weitwinkel.',
        'Gleichmäßiges Licht, ruhiger Hintergrund (Freistellung); enge Kleidung zeigt die Körperform.',
    )

    @classmethod
    def platz(cls, winkel):
        """(Winkel, Name, Ansicht, Nummer) oder `ValueError`."""
        for p in cls.PLAETZE:
            if p[0] == int(winkel):
                return p
        erlaubt = ', '.join(str(p[0]) for p in cls.PLAETZE)
        raise ValueError('Kein Bildplatz für Winkel %s (erlaubt: %s)' % (winkel, erlaubt))

    @staticmethod
    def _eigene(info):
        roh = (info.get('pshuman') or {}).get('eingabe') or {}
        return {str(k): Path(str(v)) for k, v in roh.items()} if isinstance(roh, dict) else {}

    @staticmethod
    def _stand(pfad):
        return int(pfad.stat().st_mtime) if pfad and pfad.is_file() else 0

    @classmethod
    def _quelle(cls, info, fotos, winkel):
        """('upload'|'job'|None, Pfad)."""
        eigen = cls._eigene(info).get(str(winkel))
        if eigen is not None and eigen.is_file():
            return 'upload', eigen
        foto = next((f for f in fotos if f.get('winkel') == winkel), None)
        return ('job', Path(foto['pfad'])) if foto else (None, None)

    @classmethod
    def _erzeugt(cls, ordner, winkel, art):
        """Die von PSHuman erzeugte Datei im eigenen Ordner oder None (jeder Job steht für sich, 04.11.2026,
        Edgar: „die jobs sollen immer unabhängig sein“)."""
        _w, _n, ansicht, nr = cls.platz(winkel)
        datei = Path(ordner) / 'pshuman' / 'rekon' / 'rembg' / ('%s_%d_%s.png' % (art, nr, ansicht))
        return datei if datei.is_file() else None

    @classmethod
    def lesen(cls, ordner, info, fotos):
        """Die sechs Plätze für die Seite: [{winkel, name, quelle, stand, erzeugt, stand_erzeugt}]."""
        plaetze = []
        for w, name, _a, _nr in cls.PLAETZE:
            quelle, pfad = cls._quelle(info, fotos, w)
            farbe, normale = cls._erzeugt(ordner, w, 'farbe'), cls._erzeugt(ordner, w, 'normale')
            plaetze.append({'winkel': w, 'name': name, 'quelle': quelle, 'stand': cls._stand(pfad),
                            'erzeugt': bool(farbe and normale), 'stand_erzeugt': cls._stand(farbe)})
        return plaetze

    @classmethod
    def pfad(cls, job, winkel, art):
        """Die Datei eines Platzes (`art`: eingabe | farbe | normale) oder None — nur, was der Job nennt."""
        if art not in cls.ARTEN:
            return None
        cls.platz(winkel)
        if art != 'eingabe':
            return cls._erzeugt(job['ordner'], int(winkel), art)
        return cls._quelle(cls._info(job), job.get('fotos') or [], int(winkel))[1]

    @staticmethod
    def _info(job):
        return json.loads((job['ordner'] / 'job.json').read_text(encoding='utf-8'))

    @classmethod
    def _schreiben(cls, job, eingabe):
        datei = job['ordner'] / 'job.json'
        info = cls._info(job)
        info['pshuman'] = dict(info.get('pshuman') or {}, eingabe=eingabe)
        neu = datei.with_name('job.json.neu')
        neu.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        return info

    @staticmethod
    def _beiseite(pfad):
        """Ein vorhandenes eigenes Bild umbenennen statt löschen."""
        if pfad.is_file():
            stempel = time.strftime('%Y%m%d_%H%M%S')
            ziel = pfad.with_name('%s.vor_%s%s' % (pfad.stem, stempel, pfad.suffix))
            pfad.replace(ziel)
            return ziel
        return None

    @classmethod
    def _platz_aus(cls, job, info, winkel):
        plaetze = cls.lesen(job['ordner'], info, job.get('fotos') or [])
        return next(p for p in plaetze if p['winkel'] == winkel)

    @classmethod
    def hochladen(cls, job, winkel, datei):
        """Ein Bild für den Platz `winkel` (Django-Upload) → Platz wie `lesen`. `ValueError` bei falschem
        Platz, falscher Endung oder zu groß."""
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine PSHuman-Eingabe')
        w = cls.platz(winkel)[0]
        endung = Path(str(datei.name or '')).suffix.lower()
        if endung not in cls.ENDUNGEN:
            raise ValueError('Nur %s, nicht „%s“' % (', '.join(sorted(cls.ENDUNGEN)), endung or datei.name))
        if datei.size > cls.GROESSE_MAX:
            mb = (datei.size / 2 ** 20, cls.GROESSE_MAX // 2 ** 20)
            raise ValueError('Bild zu groß (%.1f MB, höchstens %d MB)' % mb)
        ordner = job['ordner'] / 'pshuman' / 'eingabe'
        ordner.mkdir(parents=True, exist_ok=True)
        eingabe = {k: str(v) for k, v in cls._eigene(cls._info(job)).items()}
        alt = Path(eingabe[str(w)]) if str(w) in eingabe else None
        ziel = ordner / ('w%d%s' % (w, endung))
        zwischen = ziel.with_name(ziel.name + '.neu')
        with open(zwischen, 'wb') as aus:
            for stueck in datei.chunks():
                aus.write(stueck)
        for p in {ziel, alt} - {None}:
            cls._beiseite(p)
        zwischen.replace(ziel)
        eingabe[str(w)] = str(ziel)
        info = cls._schreiben(job, eingabe)
        logger.info('Ai2d3dpshumaneingabe: %s Platz %d ← %s (%d Bytes)',
                    job['ordner'].name, w, datei.name, datei.size)
        return cls._platz_aus(job, info, w)

    @classmethod
    def entfernen(cls, job, winkel):
        """Das eigene Bild eines Platzes aus der Eingabe nehmen (Datei umbenannt, nicht gelöscht) → Platz."""
        w = cls.platz(winkel)[0]
        eingabe = {k: str(v) for k, v in cls._eigene(cls._info(job)).items()}
        if str(w) not in eingabe:
            raise ValueError('Platz %d hat kein eigenes Bild' % w)
        beiseite = cls._beiseite(Path(eingabe.pop(str(w))))
        info = cls._schreiben(job, eingabe)
        logger.info('Ai2d3dpshumaneingabe: %s Platz %d entfernt (Datei → %s)',
                    job['ordner'].name, w, beiseite)
        return cls._platz_aus(job, info, w)
