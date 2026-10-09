# -*- coding: utf-8 -*-
"""Blendimporthaltung — Haltungstreue eines Stücks: trägt die Figur es in der Haltung des Originals, wo liegt es dann?

Warum (09.10.2026, Edgar: „das muss doch generisch für jedes Modell gelten"): `G9gcfigurbau.pruefen` („angezogen") misst nur, ob ein
Stück der Figur beim Tragen FOLGT — das Ziel ist das eigene Ergebnis der Rückrechnung. Ob es in der Haltung des Netzes wieder dort
liegt, wo es im Original lag, prüfte nichts: ein grünes „angezogen" (p99 1,4 mm) sagte nichts über die zerrissenen Shorts. Die
Haltung steht im Auftrag von „Mesh to 3D" als Knochendrehungen (`arbeit/zustand.npz`: θ je freiem Knochen in Daz-Kanalwerten, `rg`,
`tg`), dieselben Zahlen, mit denen die Registrierung den Käfig stellte (`Meshfigurkinematik`, gegen `G9formung(drehung)` geprüft).

    Käfig      die Figur (Regler samt Eigenmorph) in der Haltung → `X = Rg · (P − Boden) + tg` gegen `posiert.npy`: die Probe, dass die
               Abbildung stimmt (Median 0,004 mm; p99 7 mm, weil `posiert.npy` die Gelenkkorrekturen trägt)
    Stück      das GESPEICHERTE Stück (Ruhelage nach `G9gcfigurbau`) über `G9folger.punkte_zu` in derselben Haltung, in dieselbe Lage:
               Abstand zu den Originalpunkten (`Blendimportlage.ins_netz`)
    Absatz     ein Schuh steht in der Ruhelage schon in Absatzhaltung (`Blendimportfuss`): die Haltung des Fußes wird um diese Drehung
               zurückgenommen (`E' = E · Eqᵀ`, in Kanalwerten), sonst drehte sie ihn zweimal

Nicht für Haar und Augen (starr am Kopf, `Blendimportlage.kopf_starr`): ihre Bindung ist nicht die Hautbindung des Folgers.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimporthaltung']


class Blendimporthaltung:
    def __init__(self, lage):
        self.lage = lage
        self._bereit = None
        self._pose = {}
        self.letzte = None

    # ------------------------------------------------------------------ Haltung

    def _lesen(self):
        """`(theta, rg, tg, frei, knochen, reihenfolge)` aus dem Auftrag; None, wenn der Auftrag keine Haltung führt."""
        arbeit = self.lage.ablage.arbeit
        try:
            with np.load(arbeit('zustand.npz')) as z:
                theta, rg, tg = (np.asarray(z[k], dtype=np.float64) for k in ('theta', 'rg', 'tg'))
            with np.load(arbeit('genesis_ende.npz')) as g:
                frei = np.asarray(g['frei'], dtype=np.int64)
                knochen = [str(k) for k in g['knochen']]
                reihenfolge = [str(r) for r in g['reihenfolge']]
        except (OSError, KeyError) as fehler:
            logger.warning('Blender-Import: keine Haltung im Auftrag (%s)', fehler)
            return None
        return theta, rg, tg, frei, knochen, reihenfolge

    def drehung(self, griff=None):
        """`{knochen: {'rotation/x': Grad, …}}` der Haltung; `griff` (`Blendimportfuss.griff()`): die Drehung des Fußes im Stück."""
        from Genesis9.knochenmatrizen import G9knochenmatrizen
        from scipy.spatial.transform import Rotation

        theta, _, _, frei, knochen, reihenfolge = self._bereit['haltung']
        aus = {}
        for b, t in zip(frei, theta, strict=True):
            name = knochen[b]
            werte = [float(x) for x in t]
            if griff and name in griff:
                ordnung = reihenfolge[b].upper()
                q = [float(griff[name].get('rotation/%s' % a, 0.0)) for a in 'xyz']
                e = G9knochenmatrizen.euler(werte, ordnung) @ G9knochenmatrizen.euler(q, ordnung).T
                grad = Rotation.from_matrix(e).as_euler(ordnung.lower(), degrees=True)
                werte = [0.0, 0.0, 0.0]
                for a, w in zip(ordnung.lower(), grad, strict=True):
                    werte['xyz'.index(a)] = float(w)
            aus[name] = {'rotation/%s' % a: w for a, w in zip('xyz', werte, strict=True)}
        return aus

    def vorbereiten(self):
        """Haltung, Figur in Ruhe und in der Haltung, Lage; die Probe am Käfig. `None`, wenn der Auftrag keine Haltung führt."""
        if self._bereit is not None:
            return self._bereit or None
        from Genesis9.formung import G9formung
        from scipy.spatial.transform import Rotation

        haltung = self._lesen()
        if haltung is None:
            self._bereit = False
            return None
        self._bereit = {'haltung': haltung}
        regler = self.lage.stellung()
        ruhe = G9formung.aus_abfrage(dict(regler), {})
        self._bereit.update(regler=regler, boden=ruhe.boden(), r=Rotation.from_rotvec(haltung[1]).as_matrix(), tg=haltung[2])
        figur = G9formung.aus_abfrage(dict(regler), self.drehung())
        self._pose[()] = figur
        x = self.abbilden(figur.punkte() - np.array([0.0, self._bereit['boden'], 0.0]))
        d = np.linalg.norm(x - self.lage.kaefig_posiert, axis=1) * 1000.0
        self._bereit['probe'] = {'median_mm': round(float(np.median(d)), 3), 'p99_mm': round(float(np.percentile(d, 99)), 2)}
        return self._bereit

    def abbilden(self, p):
        """Punkte der Figur in der Haltung (Füße 0 der Ruhe) → Lage des Netzes."""
        return np.asarray(p, dtype=np.float64) @ self._bereit['r'].T + self._bereit['tg']

    def figur(self, griff=None):
        """Die Figur in der Haltung; mit `griff` mit zurückgenommener Fußdrehung (je Fußdrehung einmal gebaut)."""
        from Genesis9.formung import G9formung

        schluessel = tuple(sorted((k, tuple(sorted(v.items()))) for k, v in (griff or {}).items()))
        if schluessel not in self._pose:
            self._pose[schluessel] = G9formung.aus_abfrage(dict(self._bereit['regler']), self.drehung(griff))
        return self._pose[schluessel]

    # ------------------------------------------------------------------ Stück

    def treue(self, stueck, original, griff=None):
        """Haltungstreue des gespeicherten Stücks `stueck` (Garderobenkennung) gegen die Originalpunkte `original` (Lage des Netzes,
        `Blendimportlage.ins_netz`): `{median_mm, p90_mm, p99_mm, max_mm, ueber_10, ueber_25, teile}`, `{'fehler': …}` oder None ohne Haltung."""
        if self.vorbereiten() is None:
            return None
        from Genesis9.gcfigurbau import G9gcfigurbau
        from Genesis9.koerperteile import G9koerperteile

        folger = G9gcfigurbau.folger(stueck)
        folger._projektion = None
        gestellt = self.abbilden(folger.punkte_zu(self.figur(griff)) - np.array([0.0, self._bereit['boden'], 0.0]))
        if len(gestellt) != len(original):
            return {'fehler': 'Punktzahl %d gegen %d' % (len(gestellt), len(original))}
        abstand = np.linalg.norm(gestellt - original, axis=1) * 1000.0
        self.letzte = {'gestellt': gestellt, 'abstand_mm': abstand}                      # für den Kontaktbogen (`Blendimportbogen`)
        _, nah = self.lage.entposen().baum.query(original)
        teil = self.lage.teil[nah]
        namen = {v: k for k, v in G9koerperteile.NUMMER.items()}
        teile = []
        for t in np.argsort(-np.bincount(teil, minlength=len(namen)))[:4]:
            m = teil == t
            if m.sum() >= 0.02 * len(teil):
                teile.append({'teil': namen.get(int(t), str(t)), 'punkte': int(m.sum()), 'median_mm': round(float(np.median(abstand[m])), 1),
                              'p90_mm': round(float(np.percentile(abstand[m], 90)), 1)})
        return {'median_mm': round(float(np.median(abstand)), 1), 'p90_mm': round(float(np.percentile(abstand, 90)), 1),
                'p99_mm': round(float(np.percentile(abstand, 99)), 1), 'max_mm': round(float(abstand.max()), 1),
                'ueber_10': round(float((abstand > 10).mean()), 4), 'ueber_25': round(float((abstand > 25).mean()), 4), 'teile': teile}
