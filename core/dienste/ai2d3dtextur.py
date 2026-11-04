# -*- coding: utf-8 -*-
"""Ai2d3dtextur — die Textur-Engine eines 2d-3d-AI-Jobs (03.11.2026).

Edgar: „mach die textur umschaltbar, über zusatzprojekte, Recherchiere welche die besten sind, danach portiere
sie auf torch nach unserem Muster“. Konzept `Docu/konzepte/2026-11-03_textur-engines-konzept.md`.

In `3DObjects/ai2d3d/<Name>/job.json` als `textur`: {engine}; fehlt es, gilt die Vorgabe (`hautki`, der
bisherige Weg). Gelesen von der Kette beim nächsten Lauf der Körperstufe (`KoerperKI_Fotos.texturwahl`).

    POST /api/2d3dai/<job>/textur/   {engine}   → {ok, textur}
"""

import json
import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dtextur']


class Ai2d3dtextur:
    FELD = 'textur'
    VORGABE = {'engine': 'hautki', 'optionen': None}  # noqa: RUF012 — nur gelesen
    ENGINES = (('hautki', 'Haut-KI + Fotos (bisher)'), ('auswahl', 'Auswahl je Dreieck (mvs-texturing)'),
               ('optimiert', 'Optimiert gegen alle Fotos (TRELLIS)'))
    BESCHREIBUNG = {  # noqa: RUF012 — nur gelesen
        'hautki': 'Der bisherige Weg: Kopfkachel aus den Fotos über Fotohaut, Körper je Texel als Mittel '
                  'über die Fotos nach Blickwinkel, Ungesehenes aus Spiegelstelle, Umgebung und Haut-KI.',
        'auswahl': 'mvs-texturing (Waechter 2014, BSD; gepflegt in OpenMVS und OpenDroneMap): je Dreieck das '
                   'beste Foto (Schärfe × Fläche, Potts-MRF), dann globaler und lokaler Nahtausgleich — kein '
                   'Mischen mehrerer Fotos, also keine Geisterbilder. Auch das Gesicht kommt daraus.',
        'optimiert': 'TRELLIS bake_texture (MIT): die Textur per Adam gegen alle Fotos optimiert (L1 + '
                     'Glättung, 2.500 Schritte). Auch das Gesicht kommt daraus.',
    }

    @classmethod
    def auswahl(cls):
        """Combo-Box „Textur“: Wert, Text, Beschreibung je Engine."""
        return [{'wert': w, 'text': t, 'beschreibung': cls.BESCHREIBUNG[w]} for w, t in cls.ENGINES]

    @classmethod
    def lesen(cls, info):
        """Die Wahl aus einer job.json samt Vorgabe; Unbrauchbares gilt als Vorgabe (mit Warnung)."""
        roh = info.get(cls.FELD) or {}
        w = dict(cls.VORGABE, **{k: roh[k] for k in cls.VORGABE if k in roh})
        if w['engine'] not in dict(cls.ENGINES):
            logger.warning('Ai2d3dtextur: %r unbrauchbar — Vorgabe', roh)
            return dict(cls.VORGABE)
        return w

    @classmethod
    def setzen(cls, job, rumpf):
        """Schreibt die Wahl in die job.json (mischend; `ohne` und alle anderen Felder bleiben).

        `ValueError` bei unbekannter Engine.
        """
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine Textur-Wahl')
        engine = rumpf.get('engine', 'hautki')
        if engine not in dict(cls.ENGINES):
            raise ValueError('Unbekannte Engine %r' % (engine,))
        datei = job['ordner'] / 'job.json'
        info = json.loads(datei.read_text(encoding='utf-8'))
        # Checkboxen „Personenmaske“ (videoavatars `step3_texture.py`) und „Teilmaske“ (`Hautteile`,
        # Alldieck 2018), 03.11.2026, eigene Zutaten, nicht für hautki: textur.optionen.*
        alt = info.get(cls.FELD) or {}
        optionen = dict(alt.get('optionen') or {}, personenmaske=bool(rumpf.get('personenmaske')),
                        teilmaske=bool(rumpf.get('teilmaske')))
        mit = engine in ('auswahl', 'optimiert')
        info[cls.FELD] = dict(alt, engine=engine, optionen=optionen if mit else alt.get('optionen'))
        neu = datei.with_name('job.json.neu')
        neu.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        logger.info('Ai2d3dtextur: %s → %s', datei, info[cls.FELD])
        return info[cls.FELD]
