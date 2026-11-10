# -*- coding: utf-8 -*-
"""G9stueckkennung — die Kennung eines eigenen Genesis-9-Garderobenstücks ändern (10.11.2026, Edgar: „mach deine Empfehlungen“, Empfehlung 3: die Stücke
`edgar_2d_3d_ai_*` hießen nach der Umbenennung 2d-3d-AI → Foto-Genesis nur in der Anzeige neu, Kennungen, Daz-Dateien und Datenordner trugen den alten Namen).

Die Kennung ist der geslugte Dateiname der `.duf` (`G9garderobeeintrag`). Darum ändert `G9garderobepflege.umbenennen` nur den Anzeigenamen: Modelle, Rezepte und Szenen
nennen Stücke bei der Kennung, eine neue machte sie blind. Hier zieht alles in einem Zug mit:
1. Dateien des Stücks in der eigenen Bibliothek (`G9pfade.eigene()`): jeder Pfad mit dem alten Dateinamen (`Edgar 2d-3d-AI Uhr`) oder der Netzkennung
   (`EIGEN_Edgar_2d_3d_AI_Uhr`, `G9eigenstueck.kennung_und_name`) — `.duf`, Icon, `.verdeckt.json`, `data/EIGEN/<Name>/…dsf`, `Runtime/Textures/EIGEN/<Name>/…`,
   `Runtime/Support/EIGEN_EIGEN_<…>.dsx`; dazu der Arbeitsordner `eigene_stuecke/<Netzkennung>` (`G9eigenstueck.arbeitsordner`).
2. Inhalt: in `.duf`/`.dsf` (gzip, wie `G9dsonschreiber` sie schreibt) und `.dsx`/`.json` dieselben Namen, auch URL-kodiert (`Edgar%202d-3d-AI%20Uhr`, Verweise der DSON-Dateien).
3. Verweise: Schlüssel und Werte gleich der alten Kennung in `HUMANBODY_MODELS_DIR/*.json` (Modelle und Szenen: `kleidung`) — derselbe Ordner, den `Modellablage`
   beschreibt; der Anzeigename in `garderobe_pflege.json` (`G9garderobepflege`) geht auf die neue Kennung oder entfällt, wenn er dem neuen Dateinamen gleicht.
4. Zwischenspeicher: `G9garderobe.vergessen()`, `G9mbstuecke.vergessen()`. Ablagen unter der alten Kennung (`Genesis9/ablage/`) bleiben liegen und werden nicht mehr gelesen.
Nur eigene Stücke (die Daz-Bibliothek wird nie beschrieben, `G9pfade`). Gibt es Datei oder Kennung schon: `ValueError`, nichts geändert. `plan` ist der Trockenlauf.

    plan = G9stueckkennung.plan('edgar_2d_3d_ai_uhr', 'Edgar Foto-Genesis Uhr')
    bilanz = G9stueckkennung.umbenennen('edgar_2d_3d_ai_uhr', 'Edgar Foto-Genesis Uhr')
"""
import gzip
import json
import logging
import os
import re
from pathlib import Path
from urllib.parse import quote

from django.conf import settings

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['G9stueckkennung']


class G9stueckkennung:
    #: Dateien, deren Inhalt Namen trägt; gzip erkennt `_lesen` am Kopf
    TEXT = ('.duf', '.dsf', '.dsx', '.json')

    @staticmethod
    def kennung(anzeige):
        """Die Kennung zu einem Dateinamen — wie `G9eigenstueck.schreiben` (`stueck_id`)."""
        return re.sub(r'[^a-z0-9]+', '_', str(anzeige).lower()).strip('_')

    @classmethod
    def plan(cls, alt, neuer_name):
        """{alt, neu, ersetzen, dateien: [(alt, neu)], arbeitsordner, modelle: [Pfad], pflege} — ändert nichts. `ValueError`, wenn es nicht geht."""
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.garderobe import G9garderobe
        from Genesis9.pfade import G9pfade
        eintrag = G9garderobe.eintrag(alt)
        if eintrag is None:
            raise ValueError('Kein Stück mit der Kennung %s' % alt)
        if not eintrag.get('eigen'):
            raise ValueError('%s liegt in der Daz-Bibliothek, die wird nie beschrieben' % alt)
        duf = Path(G9garderobe.datei(eintrag))
        alt_name = duf.stem
        alt_netz, _a = G9eigenstueck.kennung_und_name(alt_name)
        neu_netz, neu_name = G9eigenstueck.kennung_und_name(neuer_name)
        neu = cls.kennung(neu_name)
        if neu == alt:
            raise ValueError('Die Kennung bleibt %s' % alt)
        if G9garderobe.eintrag(neu) is not None or duf.with_name(neu_name + duf.suffix).exists():
            raise ValueError('Es gibt schon ein Stück %s' % neu)
        ersetzen = [(alt_name, neu_name), (quote(alt_name), quote(neu_name)), (alt_netz, neu_netz)]
        wurzel = G9pfade.eigene()
        dateien = []
        for p in sorted(wurzel.rglob('*')):
            rel = str(p.relative_to(wurzel))
            if p.is_file() and (alt_name in rel or alt_netz in rel):
                ziel = wurzel / cls._ersetzt(rel, ersetzen)
                if ziel.exists():
                    raise ValueError('%s gibt es schon' % ziel)
                dateien.append((p, ziel))
        if not any(a == duf for a, _z in dateien):
            raise ValueError('Die Datei des Stücks %s fehlt' % duf)
        arbeit = G9eigenstueck.arbeitsordner(alt_netz)
        modelle = [p for p in sorted(Path(settings.HUMANBODY_MODELS_DIR).glob('*.json')) if cls._verweist(cls._json(p), alt)]
        return {'alt': alt, 'neu': neu, 'name': neu_name, 'ersetzen': ersetzen, 'dateien': dateien,
                'arbeitsordner': (arbeit, G9eigenstueck.arbeitsordner(neu_netz)) if arbeit.is_dir() else None, 'modelle': modelle}

    @classmethod
    def umbenennen(cls, alt, neuer_name):
        """Führt `plan` aus; → Bilanz {alt, neu, dateien, inhalte, modelle, pflege}."""
        from Genesis9.garderobe import G9garderobe
        from Genesis9.mbstuecke import G9mbstuecke
        plan = cls.plan(alt, neuer_name)
        inhalte = 0
        for quelle, ziel in plan['dateien']:
            ziel.parent.mkdir(parents=True, exist_ok=True)
            if quelle.suffix.lower() in cls.TEXT:
                daten, gepackt = cls._lesen(quelle)
                neu_text = cls._ersetzt(daten, plan['ersetzen'])
                inhalte += int(neu_text != daten)
                cls._schreiben(ziel, neu_text, gepackt)
                os.remove(quelle)
            else:
                os.replace(quelle, ziel)
        for quelle, _ziel in plan['dateien']:                                   # leer gewordene alte Ordner
            ordner = quelle.parent
            while ordner != ordner.parent and ordner.is_dir() and not any(ordner.iterdir()):
                ordner.rmdir()
                ordner = ordner.parent
        if plan['arbeitsordner']:
            os.replace(*plan['arbeitsordner'])
            cls.arbeitsdateien(plan['arbeitsordner'][1], plan['ersetzen'])
        for pfad in plan['modelle']:
            AtomarSchreiber.json_schreiben(pfad, cls._umgehaengt(cls._json(pfad), alt, plan['neu']))
        pflege = cls._pflege(alt, plan['neu'], plan['name'])
        G9garderobe.vergessen()
        G9mbstuecke.vergessen()
        bilanz = {'alt': alt, 'neu': plan['neu'], 'dateien': len(plan['dateien']), 'inhalte': inhalte,
                  'modelle': [p.name for p in plan['modelle']], 'pflege': pflege}
        logger.info('Stückkennung %s -> %s: %s', alt, plan['neu'], bilanz)
        return bilanz

    @classmethod
    def arbeitsdateien(cls, ordner, ersetzen):
        """Dateinamen im Arbeitsordner (OBJ, Farbbild, Bilanz) wie die Stückdateien. → Zahl der umbenannten."""
        zahl = 0
        for p in sorted(Path(ordner).rglob('*')):
            ziel = p.with_name(cls._ersetzt(p.name, ersetzen))
            if p.is_file() and ziel != p and not ziel.exists():
                os.replace(p, ziel)
                zahl += 1
        return zahl

    @staticmethod
    def _ersetzt(text, ersetzen):
        for a, b in ersetzen:
            text = text.replace(a, b)
        return text

    @staticmethod
    def _lesen(pfad):
        roh = Path(pfad).read_bytes()
        gepackt = roh[:2] == b'\x1f\x8b'
        return (gzip.decompress(roh) if gepackt else roh).decode('utf-8'), gepackt

    @staticmethod
    def _schreiben(pfad, text, gepackt):
        daten = text.encode('utf-8')
        neben = Path(str(pfad) + '.neu')
        neben.write_bytes(gzip.compress(daten, compresslevel=9) if gepackt else daten)
        os.replace(neben, pfad)

    @staticmethod
    def _json(pfad):
        try:
            return json.loads(Path(pfad).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def _verweist(cls, wert, kennung):
        if isinstance(wert, dict):
            return kennung in wert or any(cls._verweist(v, kennung) for v in wert.values())
        if isinstance(wert, list):
            return any(cls._verweist(v, kennung) for v in wert)
        return wert == kennung

    @classmethod
    def _umgehaengt(cls, wert, alt, neu):
        if isinstance(wert, dict):
            return {(neu if k == alt else k): cls._umgehaengt(v, alt, neu) for k, v in wert.items()}
        if isinstance(wert, list):
            return [cls._umgehaengt(v, alt, neu) for v in wert]
        return neu if wert == alt else wert

    @staticmethod
    def _pflege(alt, neu, neu_name):
        """Anzeigename der alten Kennung → neue Kennung; gleicht er dem neuen Dateinamen, entfällt er. → was geschah."""
        from Genesis9.garderobepflege import G9garderobepflege
        name = G9garderobepflege.laden()['namen'].get(alt)
        if name is None:
            return None
        G9garderobepflege.umbenennen(alt, '')
        if name != neu_name:
            G9garderobepflege.umbenennen(neu, name)
            return 'Anzeigename „%s“ auf %s' % (name, neu)
        return 'Anzeigename entfällt (gleich dem Dateinamen)'
