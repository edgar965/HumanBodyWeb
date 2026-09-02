# -*- coding: utf-8 -*-
u"""Tensorattrappe — ein Tensor ohne torch, fuer die Pruefungen.

Die Runner laufen in `python10`/`python8ENV` mit CUDA-torch; die
Testsuite laeuft in `python14`, wo es kein torch gibt. Geprueft werden
soll trotzdem, was die Runner aus der Modellausgabe herausziehen — also
genau die Kette `feld[0].detach().cpu().numpy().tolist()`.

Deshalb fragen `Smplestxbefund` und `Pymafxausgabe` nicht
`isinstance(wert, torch.Tensor)`, sondern `hasattr(wert, 'cpu')`. Diese
Attrappe erfuellt das: Sie reicht sich selbst durch `detach()` und
`cpu()` weiter und gibt bei `numpy()` das Feld heraus.

WAS SIE NICHT KANN
==================
Rechnen. Sie ist eine Huelle um ein numpy-Feld, kein Ersatz fuer torch —
wer eine Multiplikation prueft, braucht den echten Lauf.
"""
import numpy as np

__all__ = ['Tensorattrappe']


class Tensorattrappe:
    u"""Verhaelt sich wie ein Tensor, soweit die Ausgabe ihn anfasst."""

    def __init__(self, werte):
        #: Der Datentyp kommt aus den Werten — Klassennummern bleiben
        #: ganzzahlig, Formparameter bleiben Fliesskomma.
        self.werte = np.asarray(werte)

    def __getitem__(self, schluessel):
        return Tensorattrappe(self.werte[schluessel])

    def __len__(self):
        return len(self.werte)

    # Vergleiche geben ein Feld zurueck, keinen Wahrheitswert — genau wie
    # bei torch. `detectron2`-Filter (`pred_classes == 0`, `scores > 0.5`)
    # haengen daran.
    def __eq__(self, andere):
        return self.werte == andere

    def __gt__(self, andere):
        return self.werte > andere

    #: Mit `__eq__` faellt die Standard-Hashbarkeit weg; gebraucht wird
    #: sie hier nicht.
    __hash__ = None

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.werte

    def tolist(self):
        return self.werte.tolist()
