# -*- coding: utf-8 -*-
u"""``{% szenenskript %}`` — die Adresse des Startskripts der Szene-Seite.

Entweder das gebündelte Skript (eine Anfrage) oder der Einstiegspunkt der
230 Einzelmodule (230 Anfragen). Warum das einen Unterschied von mehreren
Sekunden macht und wie das Bündel entsteht: `core/dienste/modulbuendel.py`.

Als Vorlagen-Marke und nicht im Seitenkontext, weil `Vorlagenseite` für
dreizehn Seiten gilt und nur diese eine das Bündel braucht. Die Entscheidung
steht damit an genau der Stelle, an der sie wirkt — in der Zeile, die das
Skript einbindet.
"""

import logging

from django import template

from ..dienste.modulbuendel import Modulbuendel

register = template.Library()

logger = logging.getLogger('core')

#: Der Weg ohne Bündel: der Einstiegspunkt der Einzelmodule.
EINZELN = 'viewer/scene/main.js'


@register.simple_tag
def szenenskript():
    u"""Die fertige Adresse — mit Fassung im Pfad."""
    from djangobase.fassungsstatik import Fassungsstatik
    if _gewuenscht():
        try:
            # `bereit` liefert eine fertige Adresse (`/buendel/<fassung>/…`),
            # keinen Statik-Pfad: Das Bündel liegt ausserhalb von `static/`.
            adresse = Modulbuendel.bereit(Fassungsstatik.fassung())
            if adresse:
                return adresse
        except Exception:
            # Ein Fehler beim Bündeln darf die Seite nicht kosten: Sie lädt
            # dann die Einzelmodule — langsamer, aber vollständig.
            logger.exception('Szenenskript: Bündel nicht verfügbar')
    return Fassungsstatik.pfad(EINZELN)


def _gewuenscht():
    u"""Steht der Schalter unter Einstellungen → Szene auf „an"?

    Vorgabe ist AN: Wer nichts einstellt, bekommt die schnelle Seite. Zum
    Suchen eines Fehlers im JavaScript schaltet man ihn aus — dann liegt
    jedes Modul wieder einzeln im Browser, mit seinem eigenen Namen.
    """
    try:
        from ..models import AppSettings
        prefs = AppSettings.load().ui_prefs or {}
        return str(prefs.get('module_buendeln', '1')) != '0'
    except Exception:
        logger.exception('Szenenskript: Einstellung nicht lesbar')
        return False
