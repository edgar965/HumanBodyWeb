# -*- coding: utf-8 -*-
"""Architekturmesh3daigrenzen — Abschnitt „Warum die Finger brachen: Ausgabe als Daz-Winkel" der Seite Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar mit einem Bild aus dem Ergebnisfeld (Hand mit abgeknickten Fingern): „ich verstehe nicht, wie du mit Genesis-Reglern so kaputte Finger und Gesichter kriegen kannst. Das sollte doch mit den Reglern gar
nicht gehen, weil die Beschränkungen haben … Was ist falsch an unserem Ansatz?" — dann „mach" und „schreib das rein in die Hilfe-Seite".
GELESEN beim Aufruf (nichts von Hand):
    - `kinematik_bericht.json` im Datensatz (`ProjektTemp/_wegwerf/mesh3dai_kinematik.py`): Kanäle, Grenzverletzungen der Zielposen, Grenzfehler
    - `kinematik.json`: die Grenzen je Knochen (aus Genesis9.dsf), Längen der Fingerglieder (Ruhelage von Ursula1)
    - die Läufe unter `_laeufe/`: der jüngste mit `ausgabe = kanaele` und der jüngste mit freien Punkten bei gleichen Epochen, beide auf denselben Proben; die Knochenlänge rechnet diese Klasse
      selbst aus `vorhersagen.npz` und `soll.npz` (der alte Lauf führt sie nicht), die Grenzverletzungen der Ausgabe aus `<gruppe>_winkel`.
"""

import json

import numpy as np

__all__ = ['Architekturmesh3daigrenzen']


class Architekturmesh3daigrenzen:
    #: Knochen, deren Grenzen die Seite als Beispiel zeigt.
    BEISPIELE = ('l_index1', 'l_index2', 'l_index3', 'l_thumb2', 'l_hand', 'l_forearm', 'l_shin', 'lowerjaw', 'head')
    GRUPPEN = ('training', 'pruefung', 'spagat')
    SPALTEN = ('finger', 'hand', 'gesicht', 'kopf', 'arm', 'rumpf', 'bein')
    _ablage = {}

    @classmethod
    def kontext(cls, ordner):
        bericht = cls._json(ordner / 'kinematik_bericht.json')
        kin = cls._json(ordner / 'kinematik.json')
        if not bericht or not kin:
            return None
        knochen = kin['knochen']
        nach_name = {k['name']: k for k in knochen}
        beispiele = []
        for n in cls.BEISPIELE:
            k = nach_name.get(n)
            if k:
                beispiele.append({'name': n, 'reihenfolge': k['reihenfolge'], 'achsen': [{'achse': a, 'min': k['min'][i], 'max': k['max'][i], 'gesperrt': k['max'][i] <= k['min'][i],
                                                                                          'fest': k['fest'][i]} for i, a in enumerate('xyz')]})
        glieder = [1000 * float(np.linalg.norm(np.subtract(k['zentrum'], knochen[k['eltern']]['zentrum'])))
                   for k in knochen if k['gruppe'] == 'finger' and k['eltern'] >= 0 and knochen[k['eltern']]['gruppe'] == 'finger']
        return {'bericht': bericht, 'beispiele': beispiele, 'glieder_mm': (min(glieder), max(glieder)) if glieder else None,
                'vergleich': cls.vergleich(ordner, knochen)}

    @staticmethod
    def _json(datei):
        try:
            return json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def laeufe(cls, ordner):
        """(Lauf mit Daz-Winkeln, Lauf mit freien Punkten bei gleichen Epochen und Augmentierung) — das jüngste Paar, das sich vergleichen lässt; gibt es keines, der jüngste Daz-Winkel-Lauf allein.
        Seit 16.10.2026 nachmittags: ein längerer Lauf ohne Gegenstück (`kanaele_e2400`) verdrängt das Paar nicht mehr — sonst verschwände der Vergleich, auf den sich der Text des Abschnitts bezieht."""
        wurzel = ordner / '_laeufe'
        if not wurzel.is_dir():
            return None, None
        fertig = []
        for p in sorted(wurzel.iterdir()):
            e = cls._json(p / 'lauf_ergebnis.json')
            if e and (p / 'vorhersagen.npz').is_file():
                fertig.append((p, e))
        alle = [(p, e) for p, e in reversed(fertig) if e.get('ausgabe') == 'kanaele']
        if not alle:
            return None, None
        for kanaele in alle:
            ke = kanaele[1]
            punkte = next(((p, e) for p, e in reversed(fertig) if e.get('ausgabe', 'punkte') == 'punkte' and e.get('epochen') == ke.get('epochen')
                           and e.get('augmentierung', True) == ke.get('augmentierung', True) and e.get('proben') == ke.get('proben')), None)
            if punkte is not None:
                return kanaele, punkte
        return alle[0], None

    @classmethod
    def vergleich(cls, ordner, knochen):
        kanaele, punkte = cls.laeufe(ordner)
        if kanaele is None:
            return None
        stand = tuple((str(p), (p / 'vorhersagen.npz').stat().st_mtime_ns) for p, _e in (kanaele, punkte) if p is not None)
        if cls._ablage.get(str(ordner), {}).get('stand') != stand:
            zeilen = [cls._lauf(ordner, knochen, p, e) for p, e in (punkte, kanaele) if p is not None]
            cls._ablage[str(ordner)] = {'stand': stand, 'zeilen': zeilen}
        return cls._ablage[str(ordner)]['zeilen']

    @classmethod
    def _lauf(cls, ordner, knochen, lauf, ergebnis):
        """Je Gruppe der Proben: Fehler (aus `lauf_ergebnis.json`), Knochenlänge und Grenzverletzungen (gerechnet)."""
        vor = np.load(lauf / 'vorhersagen.npz')
        paare = [(k['eltern'], j) for j, k in enumerate(knochen) if k['eltern'] >= 0]
        lo = np.array([k['min'] for k in knochen])
        hi = np.array([k['max'] for k in knochen])
        wurzel = np.array([k['eltern'] < 0 for k in knochen])
        aus = {'lauf': lauf.name, 'ausgabe': ergebnis.get('ausgabe', 'punkte'), 'dauer_s': ergebnis.get('dauer_s'), 'parameter': ergebnis.get('parameter'),
               'zahlen': ergebnis.get('ausgabe_zahlen', 414), 'gruppen': []}
        for g in cls.GRUPPEN:
            if g + '_nr' not in vor.files:
                continue
            m = (ergebnis.get('maße') or {}).get(g, {})
            soll = np.stack([np.load(ordner / 'proben' / ('%04d' % int(nr)) / 'soll.npz')['rig'] for nr in vor[g + '_nr']])
            rig = vor[g + '_rig']
            l_soll = np.stack([np.linalg.norm(soll[:, j] - soll[:, e], axis=-1) for e, j in paare], axis=1)
            l_vor = np.stack([np.linalg.norm(rig[:, j] - rig[:, e], axis=-1) for e, j in paare], axis=1)
            maske = l_soll > 0.001
            zeile = {'gruppe': g, 'proben': int(len(rig)), 'netz_mm': m.get('netz_mm'), 'je': {s: (m.get('je_gruppe_mm') or {}).get(s) for s in cls.SPALTEN},
                     'laenge_mm': round(float(1000 * np.abs(l_vor - l_soll)[maske].mean()), 2), 'laenge_max_mm': round(float(1000 * np.abs(l_vor - l_soll)[maske].max()), 1),
                     'verletzt': None}
            if g + '_winkel' in vor.files:
                w = vor[g + '_winkel']
                v = np.maximum(0, lo[None] - w) + np.maximum(0, w - hi[None])
                v[:, wurzel] = 0
                zeile['verletzt'] = int((v > 0.01).sum())
            aus['gruppen'].append(zeile)
        return aus
