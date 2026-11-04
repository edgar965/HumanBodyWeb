# -*- coding: utf-8 -*-
"""Ai2d3dform — wie die Figur eines 2d-3d-AI-Jobs an die Fotos angepasst wird (03.11.2026).

Edgar: „keine eigenen erfindungen, mach zuerst das was die anderen machen!“ — „deine eigenen Zutaten
optional, per Checkbox einstellbar im UI“. Anlass: der leere Saum der Zeile 2 (Figur ringsum 1,5–3 mm
zu schmal, `Stueckumriss.INNEN_PX`).

In `3DObjects/ai2d3d/<Name>/job.json` als `form`: {engine, bilder, finger}; fehlt es, gilt die Vorgabe
(`auswendig`, der bisherige Weg). Gelesen von der Kette beim nächsten Lauf der Körperstufe
(`KoerperKI_Fotos.fotokonsens.Fotokonsens.wahl`).
  engine   auswendig = `Fotoauswendig` allein; videoavatars = danach der Silhouettenkonsens von
           videoavatars (`Fotokonsens`)
  bilder   eigene Zutat: Silhouettenterm × 120 / Zahl der Fotos (videoavatars: Strafen für 120 Bilder)
  finger   Finger je Foto an die Handpunkte von ViTPose wie SMPLify-X (`Fingerhaltung`)

    POST /api/2d3dai/<job>/form/   {engine, bilder, finger}   → {ok, form}
"""

import json
import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dform']


class Ai2d3dform:
    FELD = 'form'
    VORGABE = {'engine': 'auswendig', 'bilder': False, 'finger': False}  # noqa: RUF012 — nur gelesen
    ENGINES = (('auswendig', 'Fotoauswendig (bisher)'), ('videoavatars', 'Silhouettenkonsens (videoavatars)'))
    BESCHREIBUNG = {  # noqa: RUF012 — nur gelesen
        'auswendig': 'Der bisherige Weg: Körper, Stücke und Haltung je Foto gegen die Umrisse gelernt (Adam, '
                     'Abstandsfelder); ein Randpunkt wird erst ab 2 Maßpixeln nach außen gezogen.',
        'videoavatars': 'Danach der Konsens von videoavatars (Alldieck, CVPR 2018, Code thmoa/videoavatars): '
                        'Versätze je Punkt gegen die Konturstrahlen aller Fotos, Geman-McClure, Laplace, '
                        'Symmetrie, Dogleg.',
    }

    @classmethod
    def auswahl(cls):
        """Combo-Box „Form“: Wert, Text, Beschreibung je Engine."""
        return [{'wert': w, 'text': t, 'beschreibung': cls.BESCHREIBUNG[w]} for w, t in cls.ENGINES]

    @classmethod
    def lesen(cls, info):
        """Die Wahl aus einer job.json samt Vorgabe; Unbrauchbares gilt als Vorgabe (mit Warnung)."""
        roh = info.get(cls.FELD) or {}
        w = dict(cls.VORGABE, **{k: roh[k] for k in cls.VORGABE if k in roh})
        if w['engine'] not in dict(cls.ENGINES):
            logger.warning('Ai2d3dform: %r unbrauchbar — Vorgabe', roh)
            return dict(cls.VORGABE)
        return w

    @classmethod
    def setzen(cls, job, rumpf):
        """Schreibt die Wahl in die job.json (mischend). `ValueError` bei unbekannter Engine."""
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine Form-Wahl')
        engine = rumpf.get('engine', cls.VORGABE['engine'])
        if engine not in dict(cls.ENGINES):
            raise ValueError('Unbekannte Engine %r' % (engine,))
        datei = job['ordner'] / 'job.json'
        info = json.loads(datei.read_text(encoding='utf-8'))
        info[cls.FELD] = dict(info.get(cls.FELD) or {}, engine=engine, bilder=bool(rumpf.get('bilder')),
                              finger=bool(rumpf.get('finger')))
        neu = datei.with_name('job.json.neu')
        neu.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        logger.info('Ai2d3dform: %s → %s', datei, info[cls.FELD])
        return info[cls.FELD]
