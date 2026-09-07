# -*- coding: utf-8 -*-
u"""Mhmakrowerte — aus sieben Reglern die Faktoren der Ziele.

Portiert aus `MakeHuman/makehuman/apps/human.py` (`_setGenderVals`,
`_setAgeVals`, `_setWeightVals`, `_setMuscleVals`, `_setHeightVals`,
`_setBreastSizeVals`, `_setBreastFirmnessVals`, `_setBodyProportionVals`).
AGPL 3, siehe `MakeHuman/HERKUNFT.md`.

Jeder Makroregler laeuft 0..1 und wird in die Faktoren seiner Kategorie
zerlegt. Zwei Bauarten:

**Dreiteilig** (Gewicht, Muskeln, Groesse, Cup, Festigkeit, Proportionen)::

    max     = max(0, w·2 - 1)
    min     = max(0, 1 - w·2)
    average = 1 - (max + min)

Bei 0,5 ist `average` = 1, an den Enden `min` bzw. `max` = 1. Fuer Groesse,
Cup, Festigkeit und Proportionen schreibt der Upstream `average` ANDERS::

    average = 1 - max   falls max > min, sonst 1 - min

Das ist nicht dasselbe: In der Mitte kommt beides auf 1, an den Raendern auch
— dazwischen liegt die Kurve um bis zu 0 auseinander, weil `min` und `max`
sich nie ueberlappen. Rechnerisch ist es identisch, solange nur eines von
beiden groesser als 0 ist, und das ist immer der Fall. Es steht hier trotzdem
so da wie dort: Wer es „vereinfacht", hat eine Abweichung, die er nicht mehr
findet.

**ALTER ist die Ausnahme** und hat vier Werte auf einer geknickten Skala::

    1 Jahr     10 Jahre    25 Jahre           90 Jahre
    baby        child       young              old
    |-------------|------------|-----------------|
    0          0,1875        0,5                1

Unterhalb 0,5 wirken `baby`, `child` und `young`, darueber nur `young` und
`old`. Die Zahlen 5,333 und 3,2 sind die Kehrwerte der Abschnittslaengen
(1/0,1875 und 1/0,3125).

**RASSE** ist der dritte Fall: drei Werte, die zusammen 1 ergeben muessen
(`EthnicModifier`). Wer einen anstellt, verteilt den Rest auf die anderen
beiden im Verhaeltnis, in dem sie standen.
"""

__all__ = ['Mhmakrowerte']


class Mhmakrowerte:
    u"""Die Makroregler einer Figur und die Faktoren, die daraus folgen."""

    #: Reglername -> Vorgabe. Alle 0..1; Rasse zu je einem Drittel.
    VORGABEN = {
        'gender': 0.5, 'age': 0.5, 'muscle': 0.5, 'weight': 0.5,
        'height': 0.5, 'breastsize': 0.5, 'breastfirmness': 0.5,
        'bodyproportions': 0.5,
        'african': 1.0 / 3, 'asian': 1.0 / 3, 'caucasian': 1.0 / 3,
    }

    #: Die drei Rassenregler — ihre Summe ist immer 1.
    RASSEN = ('african', 'asian', 'caucasian')

    #: Regler -> (kleinster Wert, mittlerer Wert, groesster Wert) der Kategorie.
    #: `mitte_aus_groesserem` merkt sich die zweite Bauart aus dem Kopf.
    DREITEILIG = {
        'weight': ('minweight', 'averageweight', 'maxweight', False),
        'muscle': ('minmuscle', 'averagemuscle', 'maxmuscle', False),
        'height': ('minheight', 'averageheight', 'maxheight', True),
        'breastsize': ('mincup', 'averagecup', 'maxcup', True),
        'breastfirmness': ('minfirmness', 'averagefirmness', 'maxfirmness',
                           True),
        'bodyproportions': ('uncommonproportions', 'regularproportions',
                            'idealproportions', True),
    }

    def __init__(self, werte=None):
        self.werte = dict(Mhmakrowerte.VORGABEN)
        self.setzen(werte or {})

    def setzen(self, werte):
        u"""Regler uebernehmen; Unbekanntes faellt weg, alles wird gekappt."""
        for name, wert in (werte or {}).items():
            if name not in self.werte:
                continue
            try:
                self.werte[name] = min(1.0, max(0.0, float(wert)))
            except (TypeError, ValueError):
                continue
        self._rassen_normieren()
        return self

    def _rassen_normieren(self):
        u"""Die drei Rassenregler auf Summe 1 bringen.

        Der Upstream verteilt beim Verstellen EINES Reglers den Rest auf die
        anderen im Verhaeltnis, in dem sie standen (`human._setEthnVals`).
        Hier kommen alle drei auf einmal von der Seite — dann ist Normieren
        dasselbe Ergebnis und braucht keinen Merkzustand.
        """
        summe = sum(self.werte[r] for r in Mhmakrowerte.RASSEN)
        if summe <= 0:
            for rasse in Mhmakrowerte.RASSEN:
                self.werte[rasse] = 1.0 / 3
            return
        for rasse in Mhmakrowerte.RASSEN:
            self.werte[rasse] /= summe

    # -------------------------------------------------------------- Faktoren

    def faktoren(self):
        u"""Wertname -> Faktor, fuer alle neun Kategorien."""
        aus = {}
        aus.update(self._geschlecht())
        aus.update(self._alter())
        for regler, angabe in Mhmakrowerte.DREITEILIG.items():
            aus.update(self._dreiteilig(self.werte[regler], *angabe))
        for rasse in Mhmakrowerte.RASSEN:
            aus[rasse] = self.werte[rasse]
        return aus

    def _geschlecht(self):
        return {'male': self.werte['gender'],
                'female': 1.0 - self.werte['gender']}

    def _alter(self):
        alter = self.werte['age']
        if alter < 0.5:
            jung = max(0.0, (alter - 0.1875) * 3.2)
            return {
                'old': 0.0,
                'baby': max(0.0, 1.0 - alter * 5.333),
                'young': jung,
                'child': max(0.0, min(1.0, 5.333 * alter) - jung),
            }
        alt = max(0.0, alter * 2.0 - 1.0)
        return {'child': 0.0, 'baby': 0.0, 'old': alt, 'young': 1.0 - alt}

    @staticmethod
    def _dreiteilig(wert, klein, mitte, gross, mitte_aus_groesserem):
        u"""Die drei Faktoren einer dreiteiligen Kategorie — siehe Kopf."""
        oben = max(0.0, wert * 2.0 - 1.0)
        unten = max(0.0, 1.0 - wert * 2.0)
        if mitte_aus_groesserem:
            mittelwert = 1.0 - (oben if oben > unten else unten)
        else:
            mittelwert = 1.0 - (oben + unten)
        return {klein: unten, mitte: mittelwert, gross: oben}
