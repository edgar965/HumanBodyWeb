# -*- coding: utf-8 -*-
"""``{% szenenskript %}``/``{% studioskript %}`` — die Adresse des Startskripts.

Entweder das gebündelte Skript (eine Anfrage) oder der Einstiegspunkt der
Einzelmodule (229/290 Anfragen). Warum das einen Unterschied von mehreren
Sekunden macht und wie das Bündel entsteht: `core/dienste/modulbuendel.py`.

Als Vorlagen-Marke und nicht im Seitenkontext, weil `Vorlagenseite` für
dreizehn Seiten gilt und nur diese beiden das Bündel brauchen. Die Entscheidung
steht damit an genau der Stelle, an der sie wirkt — in der Zeile, die das
Skript einbindet.

BVH STUDIO (22.09.2026): dieselbe Marke, zweite Seite (`Modulbuendel.
EINSTIEGE['studio']`) — Edgar: „warum dauert denn laden von 230 modulen
länger als laden einer gebündelten datei???", nachdem ein Refresh trotz
warmer HumanBody-Merker noch > 10 s brauchte. `_gewuenscht()` liest denselben
Schalter (Einstellungen → Szene) für beide Seiten — ein Aus-Schalter für
beide, nicht zwei.
"""

import logging

from django import template

from ..dienste.modulbuendel import Modulbuendel

register = template.Library()

logger = logging.getLogger('core')

#: Der Weg ohne Bündel je Seite: der Einstiegspunkt der Einzelmodule.
EINZELN = Modulbuendel.EINSTIEGE['scene']
EINZELN_STUDIO = Modulbuendel.EINSTIEGE['studio']


@register.simple_tag
def szenenskript():
    """Die fertige Adresse der Szene-Seite — mit Fassung im Pfad."""
    return _skript('scene', EINZELN)


@register.simple_tag
def studioskript():
    """Die fertige Adresse von BVH Studio — mit Fassung im Pfad."""
    return _skript('studio', EINZELN_STUDIO)


def _skript(seite, einzeln):
    from djangobase.fassungsstatik import Fassungsstatik

    if _gewuenscht():
        try:
            # `bereit` liefert eine fertige Adresse (`/buendel/<fassung>/…`),
            # keinen Statik-Pfad: Das Bündel liegt ausserhalb von `static/`.
            adresse = Modulbuendel.bereit(seite, Fassungsstatik.fassung())
            if adresse:
                return adresse
        except Exception:
            # Ein Fehler beim Bündeln darf die Seite nicht kosten: Sie lädt
            # dann die Einzelmodule — langsamer, aber vollständig.
            logger.exception('%s: Bündel nicht verfügbar', seite)
    return Fassungsstatik.pfad(einzeln)


def _gewuenscht():
    """Steht der Schalter unter Einstellungen → Szene auf „an"?

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
