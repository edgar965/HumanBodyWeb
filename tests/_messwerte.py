# -*- coding: utf-8 -*-
"""Messwerte einer Vorlage — benannt statt als Woerterbuch.

ANLASS (Befund `rueckgabedict`, 27.08.2026): `Clothbasis.npz_rundlauf` und
`Kamerabasis.*` gaben Woerterbuecher mit sieben Schluesseln zurueck, und der
Fehlerfall reiste als Sonderschluessel `'_err'` mit. Jede Pruefung begann
deshalb mit derselben Zeile::

    if '_err' in r: return False, r['_err']

Ein Tippfehler in einem Schluessel faellt dabei nicht auf: `r['rigid_v']`
statt `r['rigid_V']` wirft erst beim Lauf, und in einer Pruefung, die selten
laeuft, faellt es nie auf.

`Messwerte` haelt beides: die Werte unter ihren Namen und den Fehler als
eigenes Feld. Wer einen unbekannten Namen liest, bekommt sofort einen
`AttributeError` mit der Liste der vorhandenen.
"""


class Messwerte:
    """Das Ergebnis einer Vorlage: entweder Werte oder ein Fehler."""

    def __init__(self, fehler=None, **werte):
        #: Klartext, wenn die Vorlage nicht gebaut werden konnte; sonst None.
        self.fehler = fehler
        self._werte = dict(werte)

    @classmethod
    def gescheitert(cls, text):
        return cls(fehler=text)

    def __getattr__(self, name):
        # Nur gerufen, wenn das Attribut nicht regulaer existiert.
        werte = self.__dict__.get('_werte') or {}
        if name in werte:
            return werte[name]
        raise AttributeError(
            '%s hat keinen Wert `%s` — vorhanden: %s'
            % (type(self).__name__, name, ', '.join(sorted(werte)) or '(keine)'))

    def __contains__(self, name):
        return name in self._werte

    def __repr__(self):
        if self.fehler:
            return '<Messwerte gescheitert: %s>' % self.fehler
        return '<Messwerte %s>' % ', '.join(
            '%s=%r' % paar for paar in sorted(self._werte.items()))
