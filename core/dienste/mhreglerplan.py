# -*- coding: utf-8 -*-
u"""Mhreglerplan — wie MakeHuman seine 269 Regler auf Seiten verteilt.

`modeling_sliders.json` und `measurement_sliders.json` sind MakeHumans eigene
Oberflaechen-Beschreibung: Reiter („Face", „Torso", „Gender", „Main"),
darunter Abschnitte („head shape", „head size"), darunter die Regler mit
ihrer Beschriftung. Ohne diese Datei stuenden 269 Regler in einer Liste, und
kein Mensch fuende darin `r-eye-eyefold-angle-down|up`.

DIE BESCHRIFTUNGEN BLEIBEN ENGLISCH. Es sind MakeHumans Namen; wer sie
uebersetzt, kann sie in keiner MakeHuman-Anleitung mehr nachschlagen, und bei
269 Stueck laufen Uebersetzung und Original mit jedem Upstream-Wechsel weiter
auseinander. Fehlt ein `label`, wird der Reglername lesbar gemacht — so macht
es MakeHuman auch (`humanmodifier` -> `guimodifier.getModifierLabel`).

Regler, die in keiner Slider-Datei stehen, gehen NICHT verloren: Sie landen
am Ende unter ihrer Modifier-Gruppe. Sonst waere ein Regler bedienbar, aber
unsichtbar — und niemand merkte es.
"""

import json
import logging
import os
import threading
from collections import OrderedDict

from .mhmodifikatoren import Mhmodifikatoren

logger = logging.getLogger('core')

__all__ = ['Mhreglerplan']


class Mhreglerplan:
    u"""Die Reiter-, Abschnitts- und Reglerliste fuer die Seite."""

    DATEIEN = ('modeling_sliders.json', 'measurement_sliders.json')

    #: Reiter, die im Eigenschaften-Panel oben stehen sollen. Alles Weitere
    #: folgt in der Reihenfolge der Dateien.
    VORNE = ('Macro modelling', 'Gender', 'Torso', 'Arms and Legs',
             'Face', 'Measure')

    _plan = None
    _schloss = threading.Lock()

    @classmethod
    def ordner(cls):
        from django.conf import settings
        return str(settings.MAKEHUMAN_MODIFIER_DIR)

    @classmethod
    def holen(cls):
        if cls._plan is not None:
            return cls._plan
        with cls._schloss:
            if cls._plan is None:
                cls._plan = cls._bauen()
        return cls._plan

    # ------------------------------------------------------------------ bauen

    @classmethod
    def _bauen(cls):
        katalog = Mhmodifikatoren.holen()
        seiten = OrderedDict()
        vergeben = set()
        for datei in cls.DATEIEN:
            cls._aus_datei(datei, katalog, seiten, vergeben)
        cls._rest(katalog, seiten, vergeben)
        plan = [{'name': name, 'abschnitte': abschnitte}
                for name, abschnitte in cls._sortiert(seiten)]
        logger.info('MakeHuman-Reglerplan: %d Seiten, %d Regler',
                    len(plan), len(vergeben))
        return plan

    @classmethod
    def _aus_datei(cls, datei, katalog, seiten, vergeben):
        pfad = os.path.join(cls.ordner(), datei)
        if not os.path.isfile(pfad):
            return
        with open(pfad, encoding='utf-8') as quelle:
            daten = json.load(quelle, object_pairs_hook=OrderedDict)
        for seitenname, seite in daten.items():
            abschnitte = seiten.setdefault(seitenname, OrderedDict())
            for abschnitt, eintraege in seite.get('modifiers', {}).items():
                zeilen = abschnitte.setdefault(abschnitt, [])
                for eintrag in eintraege:
                    regler = katalog.regler.get(eintrag.get('mod'))
                    if regler is None:
                        logger.debug('Reglerplan nennt Unbekanntes: %s',
                                     eintrag.get('mod'))
                        continue
                    zeilen.append(cls._zeile(regler, katalog,
                                             eintrag.get('label')))
                    vergeben.add(regler.kennung)

    @classmethod
    def _rest(cls, katalog, seiten, vergeben):
        u"""Regler ohne Platz in den Slider-Dateien — nach Gruppe sortiert."""
        offen = [r for k, r in katalog.regler.items() if k not in vergeben]
        if not offen:
            return
        abschnitte = seiten.setdefault('Weitere', OrderedDict())
        for regler in offen:
            abschnitte.setdefault(regler.gruppe, []).append(
                cls._zeile(regler, katalog, None))
            vergeben.add(regler.kennung)

    @classmethod
    def _zeile(cls, regler, katalog, beschriftung):
        return {
            'kennung': regler.kennung,
            'name': beschriftung or cls.lesbar(regler.name),
            'hinweis': katalog.beschreibungen.get(regler.kennung, ''),
            'min': regler.kleinster,
            'max': 1.0,
            'vorgabe': regler.vorgabe,
            'makro': regler.makro or '',
        }

    @staticmethod
    def lesbar(name):
        u"""`head-scale-horiz-decr|incr` -> `Head scale horiz`.

        Die Seiten des Reglers (`decr|incr`) fallen weg: Sie stehen links und
        rechts am Schieber, nicht in seinem Namen.
        """
        ohne_seiten = name.split('-decr|')[0].split('-')
        while ohne_seiten and '|' in ohne_seiten[-1]:
            ohne_seiten.pop()
        text = ' '.join(ohne_seiten).replace('|', ' ')
        return text[:1].upper() + text[1:] if text else name

    @classmethod
    def _sortiert(cls, seiten):
        def schluessel(paar):
            name = paar[0]
            return (cls.VORNE.index(name) if name in cls.VORNE
                    else len(cls.VORNE), name)
        return sorted(((name, [{'name': a, 'regler': z}
                               for a, z in abschnitte.items() if z])
                       for name, abschnitte in seiten.items()), key=schluessel)
