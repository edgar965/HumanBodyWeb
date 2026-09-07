# -*- coding: utf-8 -*-
u"""Mhgarderobe — welche Stuecke der Kleiderbibliothek MakeHuman-Stuecke sind.

Der Katalog (`Kleiderbibliothek` -> `GarmentLibrary.scan`) fuehrt 181 Stuecke
in sieben Kategorien. MakeHuman-Stuecke erkennt man an EINER Datei: der
`.mhclo` mit der Vertexzuordnung. Ohne sie gibt es keinen exakten Sitz auf dem
MakeHuman-Basiskoerper, und das Stueck gehoert nicht in diese Liste.

GEPRUEFT, NICHT GERATEN (06.09.2026): Beide denkbaren Kriterien treffen heute
dieselben 181 Stuecke — `source == 'makehuman-assets'` ebenso wie „hat eine
`.mhclo`". Gewaehlt ist trotzdem die Datei, und zwar aus einem Grund, den man
an `female_casualsuit01` sieht: Dort steht `source` gar nicht in der `.mhclo`,
sondern in einer daneben liegenden `garment.json`, aus der
`GarmentTemplate._load_native_meta` sie liest. `source` ist damit eine
Beschriftung, die jeder setzen (und vergessen) kann; die `.mhclo` ist das,
WOMIT gerechnet wird. Fehlt sie, gibt es keinen exakten Sitz — dann gehoert
das Stueck nicht in diese Liste, egal was daneben steht.
"""

import glob
import logging
import os
import threading

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mhgarderobe']


class Mhgarderobe:
    u"""Der Bestand an MakeHuman-Kleidung, nach Kategorien."""

    #: Kategorieordner -> Anzeigename. Was hier fehlt, steht unter seinem
    #: Ordnernamen — eine neue Kategorie soll nicht unsichtbar werden.
    KATEGORIEN = {
        'tops': u'Oberteile',
        'bottoms': u'Unterteile',
        'pants': u'Hosen',
        'skirts': u'Röcke',
        'dresses': u'Kleider',
        'shoes': u'Schuhe',
        'underwear': u'Unterwäsche',
        'accessories': u'Zubehör',
    }

    _bestand = None
    _schloss = threading.Lock()

    # ------------------------------------------------------------------ lesen

    @classmethod
    def wurzel(cls):
        return str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)

    @classmethod
    def liste(cls):
        u"""Alle MakeHuman-Stuecke — beim ersten Aufruf eingelesen."""
        if cls._bestand is not None:
            return cls._bestand
        with cls._schloss:
            if cls._bestand is None:
                cls._bestand = cls._einlesen()
        return cls._bestand

    @classmethod
    def neu_einlesen(cls):
        with cls._schloss:
            cls._bestand = cls._einlesen()
        return cls._bestand

    @classmethod
    def _einlesen(cls):
        wurzel = cls.wurzel()
        stuecke = []
        if not os.path.isdir(wurzel):
            logger.info('Kleiderbibliothek fehlt: %s', wurzel)
            return stuecke
        for kategorie in sorted(os.listdir(wurzel)):
            ordner = os.path.join(wurzel, kategorie)
            if not os.path.isdir(ordner) or kategorie.startswith('.'):
                continue
            for eintrag in sorted(os.listdir(ordner)):
                stueck = cls._stueck(kategorie, eintrag)
                if stueck:
                    stuecke.append(stueck)
        logger.info('MakeHuman-Garderobe: %d Stuecke', len(stuecke))
        return stuecke

    @classmethod
    def _stueck(cls, kategorie, eintrag):
        ordner = os.path.join(cls.wurzel(), kategorie, eintrag)
        if not os.path.isdir(ordner):
            return None
        if not glob.glob(os.path.join(ordner, '*.mhclo')):
            return None
        dateien = os.listdir(ordner)
        return {
            'id': '%s/%s' % (kategorie, eintrag),
            'name': eintrag.replace('_', ' '),
            'kategorie': kategorie,
            'kategoriename': cls.KATEGORIEN.get(kategorie, kategorie),
            'vorschau': any(d.endswith('.thumb') or d.endswith('_diffuse.png')
                            for d in dateien),
        }

    # ----------------------------------------------------------- nachschlagen

    @classmethod
    def verzeichnis(cls, kennung):
        u"""Der Ordner eines Stuecks — oder `None`, wenn es keines ist.

        Die Kennung ist `kategorie/name` und kommt aus der Liste. Sie wird
        NICHT zusammengesetzt geglaubt: Ein `..` darin fuehrte sonst aus der
        Bibliothek heraus.
        """
        for stueck in cls.liste():
            if stueck['id'] == kennung:
                return os.path.join(cls.wurzel(), *kennung.split('/'))
        return None
