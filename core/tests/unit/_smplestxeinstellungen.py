# -*- coding: utf-8 -*-
u"""Smplestxeinstellungen — der Teil von `cfg`, den `Smplestxbild` liest.

SMPLest-X laedt seine Konfiguration ueber `main.config.Config` — ein
verschachteltes Objekt, das ohne das Fremdprojekt nicht entsteht.
Gelesen werden davon aber nur vier Werte::

    cfg.inference.detection.conf     Guetegrenze des Detektors
    cfg.data.bbox_ratio              Rand um den Kasten
    cfg.model.input_img_shape        Eingabeform des Netzes

Die drei Traeger stehen hier als eigene Klassen auf Modulebene, nicht
als verschachtelte: Der Rumpf einer inneren Klasse sieht die Namen der
aeusseren NICHT (`class Vorlauf: detection = Erkennung()` scheitert mit
`NameError`) — eine Falle, in die diese Attrappe beim ersten Versuch
prompt gelaufen ist.
"""

__all__ = ['Erkennungsteil', 'Vorlaufteil', 'Datenteil', 'Modellteil',
           'Smplestxeinstellungen']


class Erkennungsteil:
    u"""`cfg.inference.detection` — nur das Feld `conf` wird gelesen."""

    conf = 0.42


class Vorlaufteil:
    u"""`cfg.inference`."""

    detection = Erkennungsteil()


class Datenteil:
    u"""`cfg.data` — nur `bbox_ratio`."""

    bbox_ratio = 1.5


class Modellteil:
    u"""`cfg.model` — nur die Eingabeform."""

    input_img_shape = (256, 192)


class Smplestxeinstellungen:
    u"""Steht fuer `cfg`, soweit `Smplestxbild` es anfasst."""

    inference = Vorlaufteil()
    data = Datenteil()
    model = Modellteil()
