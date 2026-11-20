# -*- coding: utf-8 -*-
"""Meshgenesistesthautkorrektur — die Haut-Korrekturen aus „Charakter“ an der Figur eines Mesh-Genesis-Tests, also auch eines Foto-Genesis-Jobs (20.11.2026, Edgar: „Du solltest
die Haut Regler aus "Charakter" auf die Jobseite einbauen … die sind nicht da“).

Die Korrekturen sind die von `G9hautausgleich` (Eigenheiten, Gleichmäßigkeit, Symmetrie, Schatten aufhellen, Retusche, Muttermale behalten). Die Werte stehen in ganzen
Prozent wie `inst.hautausgleich` im Browser, nur die von der Vorgabe abweichenden, in `haut_<g>/korrekturen.json` des Tests. Die Figur des Tests (`Meshgenesistest` →
`figur_genesis`) trägt sie als `hautausgleich`; `Genesis9Modell` rechnet sie nach jedem Bau an — Genesis-Ergebnis der Jobseite, Abspielleiste, Export, Testseite.

Quelle des Hautausgleichs sind die Hautkacheln des Tests (`Meshgenesistesthaut.kacheln`: Adressen `/api/meshgenesis/test/<k>/figur/<g>/bild/10xx.jpg`). `bibliothek` legt eine
solche Kachel als Bild der eigenen Bibliothek ab, wie `G9fotohaut` die Häute der Foto-Jobs: `Runtime/Textures/TESTHAUT/<Test>_<g>/<Stand>_<Kachel>.jpg`, der Stand (Test,
Größe, Zeit der Kachel) im Namen — eine neu gerechnete Haut bekommt neue Dateien statt still der alten.

    Meshgenesistesthautkorrektur.figur(figur, kennung, g)     -> figur (+ 'hautausgleich')
    Meshgenesistesthautkorrektur.schreiben(kennung, g, roh)   -> {Name: %} oder None (unbekannter Test)
    Meshgenesistesthautkorrektur.bibliothek(adresse)          -> 'Runtime/Textures/TESTHAUT/…jpg' oder None
"""
import hashlib
import json
import logging
import re
import shutil

from .meshgenesistest import Meshgenesistest
from .meshgenesistesthaut import Meshgenesistesthaut

logger = logging.getLogger('core')

__all__ = ['Meshgenesistesthautkorrektur']


class Meshgenesistesthautkorrektur:
    DATEI = 'korrekturen.json'
    FASSUNG = 1
    #: Felder und Vorgaben wie `Genesis9.hautausgleich.G9hautausgleich` (FELDER, VORGABEN) in Prozent
    FELDER = ('gleich', 'symmetrie', 'schatten', 'retusche', 'behalten', 'eigen')
    VORGABEN = {'behalten': 100, 'eigen': 100}
    ADRESSE = re.compile(r'^/api/meshgenesis/test/([^/?]+)/figur/([^/?]+)/bild/(10\d\d\.jpg)(?:\?.*)?$')

    @classmethod
    def _datei(cls, kennung, g):
        p = Meshgenesistest.pfad(kennung)
        if p is None or g not in Meshgenesistest.GESCHLECHTER:
            return None
        return p / ('haut_%s' % g) / cls.DATEI

    @classmethod
    def werte(cls, roh):
        """Abweichende Werte in ganzen Prozent (0 … 100) — Unbekanntes und Unlesbares fällt weg."""
        aus = {}
        for name in cls.FELDER:
            try:
                w = int(round(float((roh or {}).get(name, cls.VORGABEN.get(name, 0)))))
            except (TypeError, ValueError):
                continue
            w = max(0, min(100, w))
            if w != cls.VORGABEN.get(name, 0):
                aus[name] = w
        return aus

    @classmethod
    def lesen(cls, kennung, g):
        datei = cls._datei(kennung, g)
        if datei is None or not datei.is_file():
            return {}
        try:
            return cls.werte(json.loads(datei.read_text(encoding='utf-8')).get('werte'))
        except (OSError, ValueError):
            return {}

    @classmethod
    def schreiben(cls, kennung, g, roh):
        datei = cls._datei(kennung, g)
        if datei is None or not datei.parent.is_dir():
            return None
        werte = cls.werte(roh)
        neu = datei.with_name(datei.name + '.neu')
        neu.write_text(json.dumps({'fassung': cls.FASSUNG, 'werte': werte}, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        logger.info('Haut-Korrekturen %s (%s): %s', kennung, g, werte)
        return werte

    @classmethod
    def figur(cls, figur, kennung, g):
        """Die Figur des Tests mit ihren Korrekturen (`hautausgleich`), ohne Korrekturen unverändert."""
        werte = cls.lesen(kennung, g) if figur else {}
        return dict(figur, hautausgleich=werte) if werte else figur

    @classmethod
    def bibliothek(cls, adresse):
        m = cls.ADRESSE.match(str(adresse or ''))
        if not m:
            return None
        kennung, g, name = m.groups()
        quelle = Meshgenesistesthaut.bild(kennung, g, name)
        if quelle is None:
            return None
        from Genesis9.pfade import G9pfade
        s = quelle.stat()
        stand = hashlib.sha1(('v%d|%s|%s|%d|%d' % (cls.FASSUNG, kennung, g, s.st_size, int(s.st_mtime))).encode('utf-8')).hexdigest()[:10]
        ordner = G9pfade.eigene() / 'Runtime' / 'Textures' / 'TESTHAUT' / ('%s_%s' % (kennung, g))
        ziel = ordner / ('%s_%s' % (stand, name))
        if not ziel.is_file():
            ordner.mkdir(parents=True, exist_ok=True)
            for alt in ordner.glob('*_%s' % name):                 # ältere Stände derselben Kachel (nur in diesem eigenen Ordner)
                alt.unlink(missing_ok=True)
            vorlaeufig = ziel.with_name(ziel.stem + '.neu.jpg')
            shutil.copyfile(quelle, vorlaeufig)
            vorlaeufig.replace(ziel)
            logger.info('Test-Haut %s (%s): Kachel %s für den Hautausgleich abgelegt', kennung, g, name)
        return 'Runtime/Textures/TESTHAUT/%s_%s/%s' % (kennung, g, ziel.name)
