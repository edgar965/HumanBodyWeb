# -*- coding: utf-8 -*-
"""G9eigenehautpflege — eine gespeicherte eigene Haut umbenennen oder löschen (18.10.2026).

Edgar, 18.10.2026: „es sollen doch ALLE Assets umbenannt und gelöscht werden können?" — „mach beide" (eigene Häute und Modellzeilen der Szene). Die eigenen Häute
(`G9eigenehaut`) ließen sich nur speichern.

    UMBENENNEN  ändert den ANZEIGENAMEN im Rezept — der Schlüssel (`eigen:<schluessel>`, Dateiname) bleibt: gespeicherte Modelle nennen die Haut bei ihm, wie bei der
                Garderobe (`G9garderobepflege`). Zwei Häute mit gleichem Namen gibt es nicht (ohne Groß-/Kleinschreibung).
    LÖSCHEN     das Rezept geht nach `<eigene Daten>/haeute/papierkorb/<Zeitstempel>_<schluessel>.json` — zurückholen heißt die Datei zurückkopieren. Der Papierkorb liegt in
                einem Unterordner, `praesets()` liest nur den Ordner selbst. Bilder gibt es nicht zu löschen: eine Haut ist ein Rezept (die Bilder gehören dem Grundsatz).
"""
import logging
import re
from datetime import datetime

from .g9eigenehaut import G9eigenehaut

logger = logging.getLogger('core')

__all__ = ['G9eigenehautpflege']


class G9eigenehautpflege:
    """Umbenennen und Löschen. `LookupError` bei unbekannter Haut, `ValueError` bei untauglichem Namen."""

    PAPIERKORB = 'papierkorb'

    @classmethod
    def _rezept(cls, schluessel):
        """Das Rezept zu `schluessel` — LookupError, wenn es die Haut nicht gibt (auch bei Pfadzeichen im Schlüssel)."""
        rezept = G9eigenehaut.rezept(G9eigenehaut.PRAEFIX + str(schluessel or '')) if re.fullmatch(r'[a-z0-9_]{1,50}', str(schluessel or '')) else None
        if rezept is None:
            raise LookupError('Unbekannte eigene Haut: %s' % schluessel)
        return rezept

    @classmethod
    def umbenennen(cls, schluessel, roh):
        """Den Anzeigenamen setzen → der neue Eintrag der Hautauswahl. ValueError bei leerem Namen oder wenn eine andere Haut so heißt."""
        rezept = cls._rezept(schluessel)
        name = G9eigenehaut.name(roh)
        anderer = G9eigenehaut.vorhandener(name)
        if anderer and anderer != schluessel:
            raise ValueError('Eine eigene Haut „%s" gibt es schon.' % name)
        alt = rezept.get('name')
        rezept['name'] = name
        G9eigenehaut.schreiben(schluessel, rezept)
        logger.info('Eigene Haut %s umbenannt: %r -> %r', schluessel, alt, name)
        return G9eigenehaut.eintrag(schluessel, rezept)

    @classmethod
    def loeschen(cls, schluessel):
        """Das Rezept in den Papierkorb legen → der Pfad dort."""
        cls._rezept(schluessel)
        quelle = G9eigenehaut._pfad(schluessel)         # noqa: SLF001 — dieselbe Ablage
        ziel_ordner = quelle.parent / cls.PAPIERKORB
        ziel_ordner.mkdir(parents=True, exist_ok=True)
        ziel = ziel_ordner / ('%s_%s.json' % (datetime.now().strftime('%Y%m%d-%H%M%S'), schluessel))
        quelle.replace(ziel)
        logger.info('Eigene Haut %s gelöscht (Papierkorb: %s)', schluessel, ziel)
        return ziel
