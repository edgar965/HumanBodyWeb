# -*- coding: utf-8 -*-
u"""Erkennerattrappen — YOLO und detectron2 ohne Modell und ohne Karte.

Die beiden Foto-Wege benutzen verschiedene Personendetektoren, und beide
antworten in ihrer eigenen Form:

* **ultralytics/YOLO** (SMPLest-X): `predict(...)` gibt eine Liste; das
  erste Element traegt `boxes.xyxy` und `boxes.conf`.
* **detectron2/ViTDet** (HMR 2.0): der Aufruf gibt ein Woerterbuch mit
  `instances`, darin `pred_classes`, `scores` und `pred_boxes.tensor`.

Beide Antworten sind hier nachgebaut — mit `Tensorattrappe` als
Feldtyp, damit die Kette `.detach().cpu().numpy()` durchlaeuft, ohne
dass torch installiert sein muss.

WARUM ZWEI KLASSEN UND NICHT EINE
=================================
Beide hiessen zuerst `Detektorattrappe`, jede in ihrer Testdatei. Zwei
verschiedene Klassen mit demselben Namen sind genau das, was die
Pruefung `EineQuelle` im Wrapperbaum verbietet — bei einem Fehlschlag
nennt die Ausgabe nur den Namen, und der stimmt dann fuer beide.
"""
from ._tensorattrappe import Tensorattrappe

__all__ = ['Yolokaesten', 'Yoloattrappe', 'Kastenfeld', 'Erkennungen',
           'Detectronattrappe']


class Yolokaesten:
    u"""Was YOLO als `results[0].boxes` zurueckgibt."""

    def __init__(self, kaesten, guete):
        self.xyxy = Tensorattrappe(kaesten)
        self.conf = Tensorattrappe(guete)


class Yoloattrappe:
    u"""Ein YOLO-Ersatz mit fester Antwort; merkt sich seine Argumente."""

    def __init__(self, kaesten, guete):
        self.boxes = Yolokaesten(kaesten, guete)
        #: Je Aufruf die benannten Argumente — so laesst sich pruefen,
        #: dass die Guetegrenze aus der Konfiguration ankommt.
        self.aufrufe = []

    def predict(self, bild, **benannt):
        self.aufrufe.append(benannt)
        return [self]


class Kastenfeld:
    u"""`instances.pred_boxes` — traegt nur das Feld `tensor`."""

    def __init__(self, kaesten):
        self.tensor = Tensorattrappe(kaesten)


class Erkennungen:
    u"""Was detectron2 als `det_out['instances']` liefert."""

    def __init__(self, klassen, guete, kaesten):
        self.pred_classes = Tensorattrappe(klassen)
        self.scores = Tensorattrappe(guete)
        self.pred_boxes = Kastenfeld(kaesten)


class Detectronattrappe:
    u"""Ein detectron2-Ersatz mit fester Antwort."""

    def __init__(self, erkennungen):
        self.erkennungen = erkennungen

    def __call__(self, bild):
        return {'instances': self.erkennungen}
