# -*- coding: utf-8 -*-
"""Fotogenesisjobs — die Jobs von „Foto-Genesis“ (24.10.2026): Fotos rein, Genesis-Modell raus.

Edgar: „ein Konzept für das Erstellen eines 3D Modells aus Fotos, mit einer KI … als Eingabe kommen die Fotos (so wie die Fotos aus einigen der Jobs der Mesh3d-AI Kette), als Ausgabe ein Genesis Modell …
passe dazu die Jobs an, so dass Eingabe (Fotos), ggf. Mesh (Hunyuan), Genesis Modell und das Ergebnis zu sehen ist“ — dazu „auch echte Fotos“ (Randy, Ed/2026, Zauberer).

Zwei Arten, eine Form (`{id, name, art, figur, fotos: [{name, pfad, winkel}], netze, paar, test, wahrheit, hinweis}`):
- **Export** (`art = export`, mit Wahrheit): ein Ordner unter `3DObjects/_Output/modelsExport/` mit `<Stamm>.json` und den vier Aufnahmen `<Stamm>_vorne|links|rechts|hinten.jpg` (`Modellansichten`:
  1536 × 2048, 20°, Kamera aus der Hülle der Figur). Netz: Hunyuan3D-2mv aus genau diesen Fotos (`meshgenesis/_bild3d/<Paar>_tripovergleich/…/mesh.glb` oder `<Job>/hunyuan3d/*.glb`), dann Tripo3D
  (`<Job>/tripo3d/*.glb`). `paar` = der Mesh-Genesis-Job, dessen `paar.json` diese JSON als Quelle nennt — sein Ergebnis ist heute das Genesis-Modell der Seite (Messlatte A: Tripo-Netz → Mesh-Genesis).
  Ein neuer Export mit vier Fotos erscheint ohne Eintrag im Code.
- **Foto** (`art = foto`, ohne Wahrheit): `Fotogenesisfotojobs`, je Job eine `job.json` unter `3DObjects/_Foto_3D/`.

`winkel` je Foto: Standort der Kamera um die Figur in Grad — 0 vorne, 90 links (Kamera bei +X, die linke Körperseite), 180 hinten, 270 rechts (`Modellansichten.ANSICHTEN`); `None` = unbekannt.
"""

import copy
import json
import logging
import threading
import time
from pathlib import Path

from django.conf import settings

from .fotogenesisadresse import Fotogenesisadresse
from .fotogenesisfotojobs import Fotogenesisfotojobs
from .fotogenesispapierkorb import Fotogenesispapierkorb

logger = logging.getLogger('core')

__all__ = ['Fotogenesisjobs']


class Fotogenesisjobs:
    ANSICHTEN = (('vorne', 0), ('links', 90), ('rechts', 270), ('hinten', 180))
    #: Ablage von `alle()` (08.11.2026, Edgar: „alle modelle sollen innerhalb von max. 5 s angezeigt werden“): Jede Anfrage der Jobseite fragt `job(<id>)`, und das las jedes Mal alle
    #: Exporte, alle `paar.json` von Mesh-Genesis und alle Foto-Jobs von der Platte — gemessen im Log vom 07.11.2026 23:04 rund 0,45 s je Anfrage bei ~46 Anfragen je Seitenaufruf, am
    #: 08.11.2026 01:35–02:13 bei Plattenlast durch einen Virenscan 26–290 s je Anfrage (py-spy: Fäden in `_paare`/`_figurname`). Gilt höchstens FRISCH_S lang; eine geänderte
    #: `job.json`/`name.json` oder Ausblendliste (Schlüssel `_stand`) baut sofort neu. Was nicht im Schlüssel steht (PSHuman fertig, Kopf-Ergebnis, Netze), zeigt sich nach FRISCH_S.
    FRISCH_S = 3.0
    _ablage = None          # (Stand, Zeit, Jobs)
    _index = None           # (Stand, Zeit, [(Eckdaten mit Adresse, Bauer)]) für `job`
    _einzeln = {}           # Kennung → (Stand, Zeit, Job)
    _sperre = threading.Lock()

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / '_Output' / 'modelsExport'

    @staticmethod
    def meshgenesis():
        return Path(settings.OBJECTS_ROOT) / '_Output' / 'MeshGenesisJobs'

    @classmethod
    def alle(cls):
        """Exporte (Reiter „Jobs“) und echte Fotos (Reiter „Test“); ausgeblendete Exporte (`Fotogenesispapierkorb`) fehlen. Aus der Ablage (`FRISCH_S`), als Kopie: Aufrufer dürfen die
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
            cls._ablage, cls._index, cls._einzeln = None, None, {}

    @classmethod
    def _stand(cls):
        """Zeitstempel der Dateien, deren Änderung sofort sichtbar sein muss: `job.json` und `name.json` der Foto-Jobs, die Ausblendliste der Exporte, die Liste der Exportordner."""
        werte = []
        for muster in ('*/job.json', '*/name.json'):
            for p in Fotogenesisfotojobs.ordner().glob(muster):
                try:
                    werte.append((str(p), p.stat().st_mtime_ns))
                except OSError:
                    pass
        for p in (Fotogenesispapierkorb.wurzel() / Fotogenesispapierkorb.AUSGEBLENDET, cls.ordner(), Fotogenesisfotojobs.ordner()):
            try:
                werte.append((str(p), p.stat().st_mtime_ns))
            except OSError:
                werte.append((str(p), None))
        return tuple(sorted(werte, key=lambda w: w[0]))

    @classmethod
    def _alle_lesen(cls):
        return [dict(bauen(), adresse=eck['adresse']) for eck, bauen in cls._eintraege()]

    @classmethod
    def _eintraege(cls):
        """`[(eck, bauen)]` in der Reihenfolge der Liste — Exporte, dann Foto-Jobs. `eck`: die Eckdaten (`id`, `name`, bei Foto-Jobs `name_vorgabe`) mit der `adresse`
        aus `Fotogenesisadresse.vergeben`; `bauen()` liefert den ganzen Job ohne Adresse."""
        eintraege, wurzel, paare = [], cls.ordner(), {}

        def paare_lesen():          # alle paar.json erst, wenn ein Export ausgebaut wird
            if 'p' not in paare:
                paare['p'] = cls._paare()
            return paare['p']
        if wurzel.is_dir():
            weg = Fotogenesispapierkorb.ausgeblendet()
            for o in sorted(p for p in wurzel.iterdir() if p.is_dir()):
                gefunden = cls._export(o)
                if gefunden and o.name.lower() not in weg:
                    eintraege.append(({'id': o.name.lower(), 'name': o.name}, lambda o=o, g=gefunden: cls._ausbauen(o, *g, paare_lesen())))
        bekannt = {eck['id'] for eck, _ in eintraege}
        eintraege += [(eck, lambda eck=eck, info=info: Fotogenesisfotojobs.ausbauen(eck, info)) for eck, info in Fotogenesisfotojobs.eckdaten() if eck['id'] not in bekannt]
        Fotogenesisadresse.vergeben([eck for eck, _ in eintraege])
        return eintraege

    @classmethod
    def exporte(cls):
        return [j for j in cls.alle() if j['art'] == 'export']

    @classmethod
    def tests(cls):
        return [j for j in cls.alle() if j['art'] == 'foto']

    @classmethod
    def job(cls, kennung):
        """Der Job zu seiner Kennung oder zu seiner Adresse (`Fotogenesisadresse`), sonst `None`. Ohne frische Liste wird nur DIESER Job ausgebaut, die übrigen nur bis zu
        ihren Eckdaten (Adresse, Gültigkeit) — gleich frisch wie die Liste (Schlüssel `_stand`, FRISCH_S). 23.11.2026, Edgar: „alles schneller, max 2. s“: Jeder Seitenaufruf nach
        mehr als FRISCH_S baute alle 40 Jobs neu, 91–96 ms allein (`_wegwerf/ladezeit/fotojobs_profil.py`), im Seitenaufbau 170 ms vor dem ersten Byte der Seite (py-spy,
        `seite_spy4.txt`); mit frischer Liste kam die Seite nach 129–141 statt rund 300 ms, die Figur 0,3 s früher. Dazu kopiert `job` nur noch den einen Job, nicht alle (12,5 ms)."""
        gesucht = str(kennung).lower()
        with cls._sperre:
            stand, jetzt = cls._stand(), time.monotonic()
            a = cls._ablage
            if a is not None and a[0] == stand and jetzt - a[1] <= cls.FRISCH_S:
                return copy.deepcopy(next((j for j in a[2] if gesucht in (j['id'], j['adresse'])), None))
            i = cls._index
            if i is None or i[0] != stand or jetzt - i[1] > cls.FRISCH_S:
                i = cls._index = (stand, jetzt, cls._eintraege())
            eck, bauen = next(((e, b) for e, b in i[2] if gesucht in (e['id'], e['adresse'])), (None, None))
            if eck is None:
                return None
            j = cls._einzeln.get(eck['id'])
            if j is None or j[0] != stand or jetzt - j[1] > cls.FRISCH_S:
                j = cls._einzeln[eck['id']] = (stand, jetzt, dict(bauen(), adresse=eck['adresse']))
            return copy.deepcopy(j[2])

    @classmethod
    def _export(cls, ordner):
        """Ein Ordner ist ein Job, wenn ein Stamm alle vier Fotos und seine JSON hat: dann `(Beschreibung, Fotos)`, sonst `None` (kein Job, kein Fehler)."""
        for beschreibung in sorted(ordner.glob('*.json')):
            stamm = beschreibung.stem
            fotos = [{'name': a, 'pfad': ordner / ('%s_%s.jpg' % (stamm, a)), 'winkel': w} for a, w in cls.ANSICHTEN]
            if all(f['pfad'].is_file() for f in fotos):
                return beschreibung, fotos
        return None

    @classmethod
    def _ausbauen(cls, ordner, beschreibung, fotos, paare):
        paar = paare.get(beschreibung.resolve())
        return {'id': ordner.name.lower(), 'name': ordner.name, 'art': 'export', 'figur': cls._figurname(beschreibung), 'fotos': fotos, 'paar': paar,
                'test': None, 'wahrheit': True, 'netze': cls._netze(ordner, paar), 'hinweis': '', 'koerpergroesse_m': None}

    @staticmethod
    def _figurname(beschreibung):
        try:
            figur = json.loads(beschreibung.read_text(encoding='utf-8')).get('figur') or {}
        except (OSError, ValueError) as fehler:
            logger.warning('Fotogenesisjobs: %s nicht lesbar (%s)', beschreibung, fehler)
            return ''
        return str(figur.get('figur') or figur.get('presetName') or '')

    @classmethod
    def _netze(cls, ordner, paar):
        """Die Netze aus den Fotos: Hunyuan3D-2mv. `[{art, name, pfad, bytes}]`. Tripo3D nicht mehr (26.10.2026, Edgar: „Lösche Tripo Meshes aus allen Jobs … auch als
        Vergleichsnetz“) — der Ordner `<Job>/tripo3d/` bleibt, er gehört zu Mesh-Genesis."""
        kandidaten = []
        if paar:
            kandidaten.append(('hunyuan3d', cls.meshgenesis() / '_bild3d' / ('%s_tripovergleich' % paar['ordner']) / 'mesh' / 'ergebnis' / 'mesh.glb'))
        kandidaten += [('hunyuan3d', p) for p in sorted((ordner / 'hunyuan3d').glob('*.glb'))]
        return Fotogenesisfotojobs.netze(kandidaten)

    @classmethod
    def _paare(cls):
        """`{Pfad der Export-JSON: {kennung, ordner, name}}` aus den `paar.json` von Mesh-Genesis (Trainingspaare, `Meshgenesispaare`)."""
        paare = {}
        for marke in cls.meshgenesis().glob('*/paar.json'):
            try:
                info = json.loads(marke.read_text(encoding='utf-8'))
                pfad = Path(info['quellen']['json']['pfad']).resolve()
            except (OSError, ValueError, KeyError, TypeError) as fehler:
                logger.warning('Fotogenesisjobs: %s ohne Quelle (%s)', marke, fehler)
                continue
            paare[pfad] = {'kennung': str(info.get('kennung') or marke.parent.name.lower()), 'ordner': marke.parent.name, 'name': info.get('name') or marke.parent.name}
        return paare
