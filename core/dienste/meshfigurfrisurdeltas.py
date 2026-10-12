# -*- coding: utf-8 -*-
"""Meshfigurfrisurdeltas — die Wirkung eines Frisurreglers bei Wert 1 direkt auf den Punkten, die er bewegt (12.10.2026).

Anlass: Die Feinsuche der Frisurwahl (`Meshfigurfrisur.feinsuche`) stellt je Regler `punkte(stil, {regler: 1})` einmal echt und zieht den Grundstand ab (`Meshfigurfrisurstueck.deltas`, Daz-Morphe sind linear). Für
jeden Regler heißt das: alle Morphe des Stücks neu summieren (Eirgrid: 185 Morphe, 44,8 Mio. Deltas) und alle Punkte neu häuten. Gemessen 12.10.2026 (py-spy, Zauberer Kopie, Eirgrid Hair G9 with dForce gewinnt
die Vorrunde): 51 s von 69 s des Schritts „regler" liegen in diesen Aufrufen.

`G9folger.punkte_zu` rechnet für ein Stück ohne Prop (`lage is None`):  Körperverschiebung projiziert → eigene Morphe `Σ wert · delta` → Passform → Häutung `Σ_k w_k (L_k · p + t_k)`. Ändert sich nur der Wert EINES
Kanals `n`, ändert sich nur der Summand `(1 − wert₀) · delta_n` in der zweiten Stufe — die Körperverschiebung bleibt (der Kanal, den das Stück kennt, kommt in `formung.morphpunkte_ohne(eigene)` nicht vor, sonst stünde
er schon im Grundstand), die Passform tut bei Haar nichts. Die Häutung ist in den Punkten linear; die Translation `t_k` hebt sich in der Differenz auf. Also:  `Δ = Σ_k w_k · L_k · (1 − wert₀) · delta_n`, nur an den Punkten
von `delta_n`. Gleiche Zahlen wie die Differenz zweier voller Rechnungen bis auf Rundung (größte Abweichung steht im Test/Messskript `frisurdeltas_pruefen.py`).

Nicht auf diesem Weg (→ `None`, der Aufrufer rechnet wie bisher): ein Prop (`lage`), Passform-Kanäle im Zusatz, ein Kanal mit nicht streng aufsteigenden Punktnummern, ein Kanal, den auch der Körper stellt.
"""

import numpy as np

__all__ = ['Meshfigurfrisurdeltas']


class Meshfigurfrisurdeltas:
    def __init__(self, formung, teile, zusatz, knochen):
        """`teile`: `[(Folger, lage)]` des Stücks; `zusatz`/`knochen` wie im Grundstand (Vorgaben, Stil)."""
        self.formung = formung
        self.teile = teile
        self.zusatz = dict(zusatz or {})
        self.knochen = knochen
        self.werte = dict(formung.morphwerte())
        self.werte.update({k: float(v) for k, v in self.zusatz.items()})
        self.haeutung = [self._haeutung(f, lage) for f, lage in teile] if self.moeglich() else []

    # --------------------------------------------------------------- Vorbereitung

    def moeglich(self):
        """Gilt die Herleitung für dieses Stück? Nur Netzteile (`G9folger`) ohne Prop und ohne Passform — Strangteile (`G9strang`, dForce-Haar) legen ihre Morphe über eine Verdichtung und rechnen dicht."""
        from Genesis9.folger import G9folger

        if not all(isinstance(f, G9folger) and lage is None for f, lage in self.teile):
            return False
        return not any(str(k).startswith('passform') for k in self.zusatz)

    def _haeutung(self, folger, lage):
        """`(lin (B, 3, 3), index (N, 4), gewicht (N, 4))` der Häutung dieses Teils — oder `None`, wenn `punkte_zu` nicht häutet."""
        if lage is not None:
            return None
        if folger.eigene is not None:
            matrizen, haut = folger.eigene.matrizen(self.formung, self.knochen), folger.eigene.haut
        else:
            matrizen, haut = self.formung.matrizen(), folger.haut
            if not haut:
                return None
        if matrizen.leer or haut is None:
            return None
        karte = matrizen.matrizen()
        lin = np.zeros((len(haut.knochen), 3, 3))
        for i, name in enumerate(haut.knochen):
            m = karte.get(name)
            lin[i] = np.eye(3) if m is None else m[:3, :3]
        return lin, np.asarray(haut.index, dtype=np.int64), np.asarray(haut.gewicht, dtype=np.float64)

    # ------------------------------------------------------------------- Rechnen

    def delta(self, regler):
        """`(N, 3)` über alle Teile hintereinander — die Wirkung von `regler` = 1 gegen den Grundstand, oder `None`, wenn dieser Regler nicht auf diesem Weg zu rechnen ist."""
        if len(self.haeutung) != len(self.teile):
            return None
        stuecke = []
        for (folger, _lage), haeutung in zip(self.teile, self.haeutung, strict=True):
            anzahl = len(folger.punkte)
            aus = np.zeros((anzahl, 3), dtype=np.float64)
            if regler in folger.morphe.deltas:
                if regler in self.formung.morphwerte():
                    return None
                nummern, deltas = folger.morphe.deltas[regler]
                if len(nummern) > 1 and not bool((nummern[1:] > nummern[:-1]).all()):
                    return None
                gueltig = int(np.searchsorted(nummern, anzahl))
                zeilen = np.asarray(nummern[:gueltig], dtype=np.int64)
                aus[zeilen] = self._haeuten(np.asarray(deltas[:gueltig], dtype=np.float64) * (1.0 - self.werte.get(regler, 0.0)), zeilen, haeutung)
            stuecke.append(aus)
        return np.vstack(stuecke)

    @staticmethod
    def _haeuten(delta, zeilen, haeutung):
        """Der lineare Anteil der Häutung (`G9knochenmatrizen.anwenden` ohne Translation) an den `zeilen` — Punkte jenseits der Häutungsdaten bleiben ungehäutet."""
        if haeutung is None:
            return delta
        lin, index, gewicht = haeutung
        innen = zeilen < len(index)
        aus = delta.copy()
        if innen.any():
            r, d = zeilen[innen], delta[innen]
            summe = np.zeros_like(d)
            for k in range(index.shape[1]):
                summe += gewicht[r, k:k + 1] * np.einsum('nij,nj->ni', lin[index[r, k]], d)
            aus[innen] = summe
        return aus
