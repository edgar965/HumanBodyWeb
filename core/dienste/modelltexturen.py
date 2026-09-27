# -*- coding: utf-8 -*-
"""Modelltexturen — die Fotokacheln eines gespeicherten Genesis-Modells neben dem Modell.

Edgar, 27.09.2026: „die Szene soll natürlich mit Textur gezeigt und gespeichert werden. Speichere
die Textur gleich so, dass sie mit dem Genesis Export verfügbar ist."

Bis dahin stand im Modell (`figur.fototextur`, `figur.hautverschiebung`) je UDIM-Kachel eine
Adresse in den AUFTRAG — die Szene zeigte sie nicht, und ein gelöschter Auftrag nahm die Haut mit.
Jetzt kopiert jedes Speichern (Auftrag „Mesh to 3D", „Modell aus Bildern", „Modell speichern" der
Szene) die Kacheln nach

    data/models/Texturen/<Modellname>/<Datei>

und schreibt ihre Adresse `/api/character/genesis9-figur/fototextur/<Modell>/<Datei>/?v=<Stand>`
ins Modell. Die Szene lädt sie als Albedo des Körpers (`Genesis9fototextur`) über den Texturvorrat
— darauf wartet der Export (`Modellexport`: `Genesis9texturen.wartenAufAlle`), GLB, OBJ und DAE
tragen sie also mit.

Muster und Begründung wie `GarmentCode/szenenstuecke.py`: kopiert wird beim SPEICHERN, nicht beim
Bauen; liegt die Datei schon im Ordner DIESES Modells, wird nichts kopiert; eine fremde Adresse
bleibt stehen, eine fehlende Datei auch (mit Warnung) — lieber ein Modell ohne Haut als keins.
`?v=` ist der Stand der Datei (`artefakte-benennen.md`): wer dasselbe Modell mit neuen Kacheln
speichert, bekommt eine neue Adresse, der Browser behält keine alte.
"""

import json
import logging
import mimetypes
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote

from django.conf import settings

from ..daten.modellpfad import Modellpfad
from ..daten.texturquelle import Texturquelle

logger = logging.getLogger('core')

__all__ = ['Modelltexturen']


class Modelltexturen:
    ORDNER = 'Texturen'
    ADRESSE = '/api/character/genesis9-figur/fototextur/'
    #: Felder in `figur`, die `{kachel: Adresse}` tragen.
    FELDER = ('fototextur', 'hautverschiebung')
    ENDUNGEN = ('.jpg', '.jpeg', '.png', '.webp')
    _NAME = re.compile(r'[^\w.\-]+')

    @classmethod
    def wurzel(cls):
        return Path(settings.HUMANBODY_MODELS_DIR) / cls.ORDNER

    @classmethod
    def ordner(cls, modellname):
        """`Texturen/<Modellname>` — ValueError bei einem Namen, der die Wurzel verlassen will."""
        pfad = Modellpfad.geprueft(cls.wurzel(), str(modellname or ''), '')
        if pfad is None:
            raise ValueError('Ungültiger Modellname: %s' % modellname)
        return Path(pfad)

    @classmethod
    def adresse(cls, modellname, datei, stand):
        return '%s%s/%s/?v=%d' % (cls.ADRESSE, quote(modellname), quote(datei), int(stand))

    @classmethod
    def datei(cls, modellname, name):
        """Eine Kachel zum Ausliefern (`Path`) — nur ein Bildname ohne Pfad, nur unter der Wurzel."""
        name = str(name or '')
        if not name or any(z in name for z in Modellpfad.VERBOTEN) or not name.lower().endswith(cls.ENDUNGEN):
            return None
        try:
            return cls.ordner(modellname) / name
        except ValueError:
            return None

    @staticmethod
    def art(pfad):
        return mimetypes.guess_type(Path(pfad).name)[0] or 'application/octet-stream'

    # -------------------------------------------------------------- Sichern

    @classmethod
    def sichern(cls, modellname, figur):
        """Eine Kopie von `figur`, deren Kachel-Adressen in `Texturen/<Modellname>` zeigen."""
        if not isinstance(figur, dict):
            return figur
        neu = dict(figur)
        behalten = set()
        for feld in cls.FELDER:
            kacheln = figur.get(feld)
            if isinstance(kacheln, dict) and kacheln:
                neu[feld] = {k: cls._eine(modellname, str(a), behalten) for k, a in kacheln.items()}
        if behalten:
            cls._aufraeumen(cls.ordner(modellname), behalten)
            logger.info('Modell %s: %d Texturdateien in %s', modellname, len(behalten), cls.ORDNER)
        return neu

    @classmethod
    def _eine(cls, modellname, adresse, behalten):
        quelle = cls._quelle(adresse)
        if quelle is None:
            return adresse  # fremde Adresse — stehen lassen, nicht raten
        if not quelle.is_file():
            logger.warning('Modell %s: Textur %s fehlt (%s) — Adresse bleibt', modellname, adresse, quelle)
            return adresse
        name = cls._NAME.sub('_', quelle.name)
        try:
            ziel = cls.ordner(modellname) / name
            if quelle.resolve() != ziel.resolve():
                ziel.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(quelle, ziel)
        except OSError, ValueError:
            logger.exception('Modell %s: Textur %s nicht sicherbar', modellname, adresse)
            return adresse
        behalten.add(name)
        return cls.adresse(modellname, name, ziel.stat().st_mtime)

    @classmethod
    def _quelle(cls, adresse):
        """Die Datei hinter einer Kachel-Adresse: eigene Ablage oder Auftrag (`Texturquelle`)."""
        rein = adresse.split('?')[0]
        if rein.startswith(cls.ADRESSE):
            teile = [unquote(t) for t in rein[len(cls.ADRESSE):].split('/') if t]
            return cls.datei(teile[0], teile[1]) if len(teile) == 2 else None
        return Texturquelle.pfad(rein)

    @classmethod
    def _aufraeumen(cls, ordner, behalten):
        """Kacheln eines früheren Stands entfernen, die das Modell nicht mehr nennt (nur Bilder, flach)."""
        for p in ordner.iterdir():
            if p.is_file() and p.suffix.lower() in cls.ENDUNGEN and p.name not in behalten:
                p.unlink()

    # ------------------------------------------------- Umbenennen, Löschen

    @classmethod
    def entfernen(cls, modellname):
        """Die Kacheln eines gelöschten Modells entfernen — nur Bilder, nicht rekursiv."""
        ordner = cls.ordner(modellname)
        if not ordner.is_dir():
            return False
        for p in ordner.iterdir():
            if p.is_file() and p.suffix.lower() in cls.ENDUNGEN:
                p.unlink()
        if not any(ordner.iterdir()):
            ordner.rmdir()
        logger.info('Modell %s: Texturen entfernt', modellname)
        return True

    @classmethod
    def umbenennen(cls, alt, neu, modellpfad):
        """Den Ordner mitnehmen und die Adressen in der (schon umbenannten) Modelldatei umschreiben."""
        quelle, ziel = cls.ordner(alt), cls.ordner(neu)
        if not quelle.is_dir() or ziel.exists():
            return False
        quelle.rename(ziel)
        with open(modellpfad, encoding='utf-8') as f:
            daten = json.load(f)
        figur = daten.get('figur') if isinstance(daten.get('figur'), dict) else {}
        vorher, nachher = cls.ADRESSE + quote(alt) + '/', cls.ADRESSE + quote(neu) + '/'
        for feld in cls.FELDER:
            if isinstance(figur.get(feld), dict):
                figur[feld] = {k: str(a).replace(vorher, nachher, 1) for k, a in figur[feld].items()}
        with open(modellpfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, indent=2, ensure_ascii=False)
        return True
