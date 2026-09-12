# -*- coding: utf-8 -*-
u"""Umaablage — eine UMA-Figur im Figurkatalog umbenennen oder löschen.

Eine Figur ist immer ein PAAR: `<name>.glb` und der Beipackzettel
`<name>.json` daneben (`Figuren/VERTRAG.md`). Wer nur die GLB anfasst, lässt
einen Zettel zurück, der auf nichts mehr zeigt.

Dazu kommt `aktuell.json`: Der Zeiger nennt je Quelle die gültige Datei, und
Roomguest liest ihn. Zeigt er nach einer Umbenennung ins Leere, nimmt
Roomguest die jüngste Datei und warnt nur im Log — ein stiller Zustand, der
nach außen richtig aussieht. Deshalb wird der Zeiger hier mitgeführt:
umbenannt wandert er mit, gelöscht fällt er weg.

Geschrieben wird ausschließlich unter `Figuren/uma/`; `HumanBody/data/`
bleibt unberührt. 06.09.2026.
"""
import json
import logging
import os

from django.conf import settings

from ..daten.modellpfad import Modellpfad

logger = logging.getLogger(__name__)

__all__ = ['Umaablage', 'Ablagefehler']


class Ablagefehler(Exception):
    u"""Der Vorgang ist nicht ausführbar — die Meldung geht an den Nutzer."""


class Umaablage:

    QUELLE = 'uma'
    ZEIGER = 'aktuell.json'

    @classmethod
    def ordner(cls):
        return os.path.join(str(settings.FIGUREN_KATALOG), cls.QUELLE)

    @classmethod
    def pfade(cls, name):
        u"""(GLB, Zettel) zu einem Dateinamen wie `Uma_HumanFemale30.glb`.

        Wirft, wenn der Name den Ordner verlassen will — die Prüfung steht in
        `Modellpfad.geprueft` und ist dieselbe wie bei den Modellvorgaben.
        """
        if not name.endswith('.glb'):
            raise Ablagefehler(u'Nur .glb-Dateien: %s' % name)
        stamm = name[:-4]
        glb = Modellpfad.geprueft(cls.ordner(), stamm, '.glb')
        zettel = Modellpfad.geprueft(cls.ordner(), stamm, '.json')
        if glb is None or zettel is None:
            raise Ablagefehler(u'Ungültiger Name: %s' % name)
        return glb, zettel

    # -- Vorgänge -------------------------------------------------------------

    @classmethod
    def umbenennen(cls, alt, neu):
        u"""`<alt>.glb`/`.json` heißen danach `<neu>.glb`/`.json`."""
        alt_glb, alt_zettel = cls.pfade(alt)
        neu_glb, neu_zettel = cls.pfade(neu)
        if not os.path.isfile(alt_glb):
            raise Ablagefehler(u'Figur nicht gefunden: %s' % alt)
        if os.path.exists(neu_glb):
            raise Ablagefehler(u'Es gibt schon eine Figur %s' % neu)
        os.rename(alt_glb, neu_glb)
        if os.path.isfile(alt_zettel):
            os.rename(alt_zettel, neu_zettel)
            cls._zettelname(neu_zettel, os.path.basename(neu)[:-4])
        cls._zeiger_setzen(alt, os.path.basename(neu))
        logger.info(u'UMA-Figur umbenannt: %s -> %s', alt, neu)
        return os.path.basename(neu)

    @classmethod
    def loeschen(cls, name):
        u"""GLB und Zettel entfernen; ein Zeiger darauf fällt weg.

        Gelöscht werden GENAU diese zwei Dateien, kein Verzeichnis und nichts
        rekursiv.
        """
        glb, zettel = cls.pfade(name)
        if not os.path.isfile(glb):
            raise Ablagefehler(u'Figur nicht gefunden: %s' % name)
        os.remove(glb)
        if os.path.isfile(zettel):
            os.remove(zettel)
        cls._zeiger_setzen(name, None)
        logger.info(u'UMA-Figur gelöscht: %s', name)
        return True

    # -- Zeiger und Zettel ----------------------------------------------------

    @classmethod
    def zeiger(cls):
        u"""Der Inhalt von `aktuell.json`, oder {}."""
        pfad = os.path.join(str(settings.FIGUREN_KATALOG), cls.ZEIGER)
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        # stumm gewollt: ohne aktuell.json gibt es keinen Zeiger — das ist ein
        # gueltiger Stand
        except (OSError, ValueError):
            return {}

    @classmethod
    def _zeiger_setzen(cls, betrifft, neuer_wert):
        u"""Zeigt `aktuell.json` auf `betrifft`, wird der Eintrag nachgeführt.

        `neuer_wert` None entfernt ihn. Zeigt der Zeiger auf eine andere
        Figur, bleibt er unverändert — er gehört Roomguest, nicht uns.
        """
        pfad = os.path.join(str(settings.FIGUREN_KATALOG), cls.ZEIGER)
        stand = cls.zeiger()
        if stand.get(cls.QUELLE) != os.path.basename(betrifft):
            return False
        if neuer_wert is None:
            stand.pop(cls.QUELLE, None)
        else:
            stand[cls.QUELLE] = neuer_wert
        try:
            with open(pfad, 'w', encoding='utf-8') as datei:
                json.dump(stand, datei, ensure_ascii=False, indent=2)
        except OSError:
            logger.warning(u'Zeiger %s nicht schreibbar', pfad, exc_info=True)
            return False
        logger.info(u'Zeiger %s: %s -> %s', cls.QUELLE, betrifft, neuer_wert)
        return True

    @classmethod
    def _zettelname(cls, pfad, name):
        u"""Das Feld `name` im Beipackzettel nachziehen."""
        try:
            with open(pfad, encoding='utf-8') as datei:
                zettel = json.load(datei)
            zettel['name'] = name
            with open(pfad, 'w', encoding='utf-8') as datei:
                json.dump(zettel, datei, ensure_ascii=False, indent=2)
        except (OSError, ValueError):
            logger.warning(u'Zettel %s nicht nachgezogen', pfad, exc_info=True)
