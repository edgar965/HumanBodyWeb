# -*- coding: utf-8 -*-
u"""Mhmodifikatoren — MakeHumans Regler und die Gewichte, die sie erzeugen.

Portiert aus `MakeHuman/makehuman/apps/humanmodifier.py` (AGPL 3, siehe
`MakeHuman/HERKUNFT.md`), Klassen `UniversalModifier`, `MacroModifier`,
`EthnicModifier` und `loadModifiers`.

ZWEI ARTEN VON REGLERN
======================
**Detailregler** (`UniversalModifier`) — rund 250 Stueck. Sie haben eine
linke und eine rechte Zielgruppe, manchmal eine mittlere::

    {"target": "head-age", "min": "decr", "max": "incr"}
    -> links `head-head-age-decr`, rechts `head-head-age-incr`

Der Gruppenname steht davor, deshalb `head-head-age-…`: Der Ordner heisst
`head` und die Datei `head-age-decr.target`, und MakeHuman setzt beides
zusammen. Wer das „aufraeumt", findet kein einziges Ziel mehr.

Der Regler laeuft -1..+1 (oder 0..1 ohne linke Seite) und setzt::

    links  = -min(wert, 0)      mitte = 1 - |wert|      rechts = max(0, wert)

**Makroregler** (`MacroModifier`) — Geschlecht, Alter, Rasse, Muskeln,
Gewicht, Groesse, Proportionen, Cup, Festigkeit. Sie setzen kein Ziel direkt,
sondern die Makrovariablen (`Mhmakrowerte`); ihre Zielgruppe ist der
Gruppenname selbst, mit Faktor 1. Welches der 850 Kombinationsziele wirkt,
entscheiden allein die Faktoren aus den Makrovariablen.

DAS GEWICHT EINES ZIELS ist das Produkt der Faktoren aller seiner Woerter —
Makrowerte und Gruppenname zusammen (`getTargetWeights` im Upstream). Ein Ziel
mit `maxmuscle` verschwindet von selbst, sobald der Muskelregler in der Mitte
steht.
"""

import json
import logging
import os
import threading
from collections import OrderedDict

from .mhmakrowerte import Mhmakrowerte
from .mhzielbaum import Mhzielbaum

logger = logging.getLogger('core')

__all__ = ['Mhmodifikator', 'Mhmodifikatoren']


class Mhmodifikator:
    u"""Ein Regler: seine Zielgruppen und wie er sie gewichtet."""

    __slots__ = ('gruppe', 'name', 'links', 'mitte', 'rechts', 'makro',
                 'vorgabe')

    def __init__(self, gruppe, name, links=None, mitte=None, rechts=None,
                 makro=None, vorgabe=0.0):
        self.gruppe = gruppe
        self.name = name
        self.links = links
        self.mitte = mitte
        self.rechts = rechts
        #: Name der Makrovariablen (`gender`, `age`, …) oder `None`.
        self.makro = makro
        self.vorgabe = vorgabe

    @property
    def kennung(self):
        return '%s/%s' % (self.gruppe, self.name)

    @property
    def kleinster(self):
        return -1.0 if self.links else 0.0

    def gruppen(self):
        u"""Die Zielgruppen, aus denen dieser Regler schoepft."""
        return [g for g in (self.links, self.mitte, self.rechts) if g]

    def eigene_faktoren(self, wert):
        u"""Die Faktoren, die NUR dieser Regler beisteuert."""
        if self.makro:
            # Makroregler: die Gruppe zaehlt voll, den Rest machen die
            # Makrovariablen.
            return {self.rechts: 1.0}
        faktoren = {}
        if self.links:
            faktoren[self.links] = -min(wert, 0.0)
        if self.mitte:
            faktoren[self.mitte] = 1.0 - abs(wert)
        faktoren[self.rechts] = max(0.0, wert)
        return faktoren


class Mhmodifikatoren:
    u"""Der Katalog aus `modeling_modifiers.json`."""

    #: Beide Reglersaetze von MakeHuman: Modellieren und Maße. Der zweite
    #: bringt die 20 Regler des „Measure"-Reiters (Brustumfang, Taille,
    #: Schrittlänge …) — dieselbe Mechanik, eigene Datei.
    DATEIEN = ('modeling_modifiers.json', 'measurement_modifiers.json')
    BESCHREIBUNGEN = ('modeling_modifiers_desc.json',
                      'measurement_modifiers_desc.json')

    #: Makrovariable im JSON -> Reglername in `Mhmakrowerte`.
    MAKRONAMEN = {
        'Gender': 'gender', 'Age': 'age', 'Muscle': 'muscle',
        'Weight': 'weight', 'Height': 'height',
        'BodyProportions': 'bodyproportions', 'BreastSize': 'breastsize',
        'BreastFirmness': 'breastfirmness',
        'African': 'african', 'Asian': 'asian', 'Caucasian': 'caucasian',
    }

    _katalog = None
    _schloss = threading.Lock()

    def __init__(self, regler, beschreibungen):
        #: Kennung -> `Mhmodifikator`, in Dateireihenfolge.
        self.regler = regler
        self.beschreibungen = beschreibungen

    # ------------------------------------------------------------------ laden

    @classmethod
    def ordner(cls):
        from django.conf import settings
        return str(settings.MAKEHUMAN_MODIFIER_DIR)

    @classmethod
    def vorhanden(cls):
        return os.path.isfile(os.path.join(cls.ordner(), cls.DATEIEN[0]))

    @classmethod
    def holen(cls):
        if cls._katalog is not None:
            return cls._katalog
        with cls._schloss:
            if cls._katalog is None:
                cls._katalog = cls._einlesen()
        return cls._katalog

    @classmethod
    def _einlesen(cls):
        regler = OrderedDict()
        for name in cls.DATEIEN:
            pfad = os.path.join(cls.ordner(), name)
            if not os.path.isfile(pfad):
                continue
            with open(pfad, encoding='utf-8') as quelle:
                daten = json.load(quelle, object_pairs_hook=OrderedDict)
            for gruppe in daten:
                for angabe in gruppe['modifiers']:
                    eintrag = cls._bauen(gruppe['group'], angabe)
                    regler[eintrag.kennung] = eintrag
        logger.info('MakeHuman-Regler gelesen: %d', len(regler))
        return cls(regler, cls._beschreibungen())

    @classmethod
    def _beschreibungen(cls):
        aus = {}
        for name in cls.BESCHREIBUNGEN:
            pfad = os.path.join(cls.ordner(), name)
            if os.path.isfile(pfad):
                with open(pfad, encoding='utf-8') as quelle:
                    aus.update(json.load(quelle))
        return aus

    @classmethod
    def _bauen(cls, gruppe, angabe):
        if 'macrovar' in angabe:
            variable = angabe['macrovar']
            makro = cls.MAKRONAMEN.get(variable, variable.lower())
            return Mhmodifikator(gruppe, variable, rechts=gruppe, makro=makro,
                                 vorgabe=Mhmakrowerte.VORGABEN.get(makro, 0.5))
        ziel = angabe['target']
        basis = '%s-%s' % (gruppe, ziel)
        links, rechts, mitte = angabe.get('min'), angabe.get('max'), angabe.get('mid')
        if links and rechts:
            teile = [links, mitte, rechts] if mitte else [links, rechts]
            name = '%s-%s' % (ziel, '|'.join(teile))
            return Mhmodifikator(
                gruppe, name, links='%s-%s' % (basis, links),
                mitte=('%s-%s' % (basis, mitte)) if mitte else None,
                rechts='%s-%s' % (basis, rechts),
                vorgabe=angabe.get('defaultValue', 0.0))
        return Mhmodifikator(gruppe, ziel, rechts=basis,
                             vorgabe=angabe.get('defaultValue', 0.0))

    # --------------------------------------------------------------- Gewichte

    def gewichte(self, reglerwerte, makro):
        u"""`{Zielpfad: Gewicht}` fuer diese Reglerstellung.

        GESETZT, NICHT AUFSUMMIERT — wie `human.setDetail` im Upstream. In der
        Gruppe `macrodetails` haengen FUENF Makroregler (Geschlecht, Alter und
        die drei Rassen) an denselben 96 Zielen und rechnen alle dasselbe
        Gewicht aus. Wer addiert, traegt es fuenfmal ein und verformt die
        Figur um das Fuenffache; dasselbe in `breast` mit Cup und Festigkeit.

        Ein Ziel mit Gewicht 0 faellt weg — es zu laden und mit 0 zu
        multiplizieren waere bei 850 Makrozielen die ganze Arbeit umsonst.
        """
        baum = Mhzielbaum.holen()
        makrofaktoren = makro.faktoren()
        aus = {}
        for kennung, regler in self.regler.items():
            wert = self._wert(reglerwerte, kennung, regler, makro)
            faktoren = dict(makrofaktoren)
            faktoren.update(regler.eigene_faktoren(wert))
            for gruppe in regler.gruppen():
                for ziel in baum.in_gruppe(gruppe):
                    gewicht = Mhmodifikatoren._gewicht(ziel, faktoren)
                    if gewicht:
                        aus[ziel.pfad] = gewicht
        return aus

    @staticmethod
    def _gewicht(ziel, faktoren):
        u"""Produkt der Faktoren aller Woerter dieses Ziels.

        Ein Wort ohne Faktor waere im Upstream ein `KeyError`
        (`getTargetWeights` ohne `ignoreNotfound`). Hier gilt 0 — ein Ziel,
        das niemand ansteuert, soll nicht die ganze Anfrage abbrechen. Dass
        es keine solchen Woerter GIBT, prueft `test_mhregler`.
        """
        gewicht = 1.0
        for name in ziel.faktoren:
            gewicht *= faktoren.get(name, 0.0)
            if gewicht == 0.0:
                return 0.0
        return gewicht

    def angesteuerte_gruppen(self):
        u"""Die Zielgruppen, die ueberhaupt an einem Regler haengen.

        Von den 653 Gruppen des Upstreams sind 179 an KEINEN Regler gebunden
        (`armslegs-l-foot-scale-depth-decr` etwa, oder die 20 Massziele, die in
        `measurement_modifiers.json` stehen). Das ist kein Fehler der
        Portierung — `modeling_modifiers.json` ist auch in MakeHuman selbst
        die Liste dessen, was bedienbar ist.
        """
        gruppen = set()
        for regler in self.regler.values():
            gruppen.update(regler.gruppen())
        return gruppen

    def unbekannte_woerter(self):
        u"""Zielwoerter ohne Faktor — in den ANGESTEUERTEN Gruppen.

        Die Probe fuer den Kopf von `_gewicht`: Ist die Liste leer, kann kein
        erreichbares Ziel still durch die 0-Vorgabe fallen.
        """
        bekannt = set(Mhmakrowerte().faktoren())
        gruppen = self.angesteuerte_gruppen()
        bekannt.update(gruppen)
        baum = Mhzielbaum.holen()
        fehlend = set()
        for gruppe in gruppen:
            for ziel in baum.in_gruppe(gruppe):
                fehlend.update(w for w in ziel.faktoren if w not in bekannt)
        return sorted(fehlend)

    @staticmethod
    def _wert(reglerwerte, kennung, regler, makro):
        u"""Die Stellung eines Reglers — Makroregler holen sie aus `makro`."""
        if regler.makro:
            return makro.werte.get(regler.makro, regler.vorgabe)
        wert = reglerwerte.get(kennung, regler.vorgabe)
        try:
            wert = float(wert)
        except (TypeError, ValueError):
            return regler.vorgabe
        return min(1.0, max(regler.kleinster, wert))
