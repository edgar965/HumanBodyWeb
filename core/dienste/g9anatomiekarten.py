# -*- coding: utf-8 -*-
u"""G9anatomiekarten — die im Browser gerechneten Karten des Anatomie-Stücks dauerhaft ablegen (19.10.2026).

Edgar, 19.10.2026: „warum muss die immer neu gerechnet werden? kannst du die im modell nicht speichern?" und „alle Anzeigen speichern, sodass sie beim Laden
schnell angezeigt werden". `Anatomiebacken` rechnet Farbe, Normalen und Rauheit des Stücks aus den Karten der Haut — gemessen am 19.10.2026 an Damira0
(Mesh3D-AI, zwei Figuren, grob) 9,6 s von „Texturen da" bis „Hautfarbe fertig", bei jedem Laden. Die Karten hängen nur an der Eingabe: Lage des Stücks und der
Haut darunter (`Anatomiehash`), den Bildern der Haut (ihre Adressen), der Größe und der Fassung der Rechnung — der Schlüssel ist ein Hash darüber
(`gemeinsam/anatomievorrat.js`). Hier liegen sie unter ihm, bis zu `PLATTE_MB`; was am längsten nicht gelesen wurde, fällt zuerst.

    Genesis9/ablage/anatomiekarten/<schluessel>/meta.json      {nr, arten, zeit}  — nr: die Haut-Gruppe, deren Farbe und Material das Stück trägt
                                                  farbe.png / normal.png / rauheit.png
"""
import json
import logging
import re
import shutil
import threading
import time

from Genesis9.pfade import G9pfade

__all__ = ['G9anatomiekarten']

logger = logging.getLogger('core')


class G9anatomiekarten:

    ORDNER = 'anatomiekarten'
    ARTEN = ('farbe', 'normal', 'rauheit')
    PLATTE_MB = 5000
    MUSTER = re.compile(r'^[a-z0-9]{8,64}$')

    _schloss = threading.Lock()

    @classmethod
    def wurzel(cls):
        return G9pfade.ablage() / cls.ORDNER

    @classmethod
    def ordner(cls, schluessel):
        u"""Der Ordner eines Schlüssels — None, wenn der Schlüssel nicht wie einer aussieht (er kommt aus der Anfrage)."""
        return cls.wurzel() / schluessel if cls.MUSTER.match(str(schluessel or '')) else None

    @classmethod
    def meta(cls, schluessel):
        u"""`{nr, arten}` — oder None. Ein Treffer frischt die Zeit auf (für das Ausdünnen)."""
        ordner = cls.ordner(schluessel)
        datei = ordner / 'meta.json' if ordner else None
        try:
            meta = json.loads(datei.read_text(encoding='utf-8'))
        except (AttributeError, OSError, ValueError):
            return None
        try:
            datei.touch()
        except OSError:
            pass
        return meta

    @classmethod
    def datei(cls, schluessel, art):
        ordner = cls.ordner(schluessel)
        if not ordner or art not in cls.ARTEN:
            return None
        pfad = ordner / ('%s.png' % art)
        return pfad if pfad.is_file() else None

    @classmethod
    def ablegen(cls, schluessel, nr, bilder):
        u"""Karten ablegen (`bilder`: Art → PNG-Bytes). Ganz oder gar nicht: erst in einen Nebenordner, dann umbenennen."""
        ordner = cls.ordner(schluessel)
        if not ordner or 'farbe' not in bilder:
            return False
        if (ordner / 'meta.json').is_file():
            return True
        neben = ordner.with_name('%s.%d.tmp' % (ordner.name, threading.get_ident()))
        try:
            neben.mkdir(parents=True, exist_ok=True)
            for art, inhalt in bilder.items():
                if art in cls.ARTEN and inhalt[:8] == b'\x89PNG\r\n\x1a\n':
                    (neben / ('%s.png' % art)).write_bytes(inhalt)
            (neben / 'meta.json').write_text(json.dumps({'nr': int(nr), 'arten': sorted(a for a in bilder if a in cls.ARTEN),
                                                         'zeit': time.time()}), encoding='utf-8')
            with cls._schloss:
                if ordner.exists():
                    shutil.rmtree(neben, ignore_errors=True)
                    return True
                neben.rename(ordner)
        except OSError as fehler:
            shutil.rmtree(neben, ignore_errors=True)
            logger.warning('Anatomiekarten: nicht abgelegt (%s)', fehler)
            return False
        cls.ausduennen()
        return True

    @classmethod
    def ausduennen(cls):
        u"""Über `PLATTE_MB`: die am längsten nicht gelesenen Einträge (Zeit von `meta.json`) zuerst weg — nur Ordner dieses Vorrats."""
        eintraege = []
        for ordner in cls.wurzel().iterdir():
            meta = ordner / 'meta.json'
            if ordner.is_dir() and cls.MUSTER.match(ordner.name) and meta.is_file():
                eintraege.append((meta.stat().st_mtime, sum(d.stat().st_size for d in ordner.iterdir()), ordner))
        summe = sum(e[1] for e in eintraege)
        for _zeit, groesse, ordner in sorted(eintraege):
            if summe <= cls.PLATTE_MB * 1024 * 1024:
                break
            shutil.rmtree(ordner, ignore_errors=True)
            summe -= groesse
