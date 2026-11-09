# -*- coding: utf-8 -*-
"""Exportleistekragen — der Rand eines Stücks am Hals liegt im Render an der Haut an (06.11.2026, Edgar zu Edgar2010: ausgefranstes Loch am Kragen in Bild 340).

Das Loch ist keins: Am gesenkten Kopf sieht die Kamera am Nacken zwischen Haut und Kragen hindurch auf die Innenseite des Oberteils. Dort kommt kein Licht hin, der gezackte Rand des Netzes steht
schwarz vor ihr (je Pixel `ProjektTemp/_wegwerf/render_boden/kragen_loch.py`: Rückseite des Oberteils, zweiter Treffer die Wand; Texel dort Median 81, also nicht die Textur). Der Rand steht in Ruhe 1,7
bis 3 cm von der Haut ab (`kragen_schnitt.py`), weil das Netz des Eingangs dort nur die Außenseite kennt, und folgt dem Hals gut (Abstand in Ruhe Median 6,8 mm, im Bild 10,6 mm, `kragen_gewichte.py`).
Die Seite zeichnet ohne Schatten und zeigt den Spalt nicht als Loch, darum nur hier, im Bau der Render-Figur.

Randpunkte eines deckenden Stücks in Halshöhe, die `NAH_M` bis `WEIT_M` über der Haut stehen, gehen längs der Hautnormale auf `LUFT_M` heran; das Stück folgt weich über `FALL_M`. Ein weiter Ausschnitt
bleibt, wie er ist: Er steht weiter ab oder liegt tiefer. Haar deckt nicht und bleibt. Die Haut unter dem Stück rechnet `Exportleistehautmaske` danach, auf dem angelegten Stück.
"""

import numpy as np
from scipy.spatial import cKDTree

__all__ = ['Exportleistekragen']


class Exportleistekragen:
    #: Rand näher an der Haut (m) liegt schon an.
    NAH_M = 0.005
    #: Rand weiter von der Haut (m) ist ein Ausschnitt, kein Kragen. Edgar2010 höchstens 20,4 mm längs der Normale; mit 4 cm griff die Regel bei koenigin1 und session3dtools bis an die Grenze
    #: (06.11.2026, `kragen_gegen.py`, sechs Tests mit Seite-GLB): dort steht der Stoff weit ab, das ist Schnitt, kein Spalt.
    WEIT_M = 0.025
    #: Weniger Randpunkte (Hutkrempe, ein Zacken) sind kein Kragen.
    MIN_PUNKTE = 20
    LUFT_M = 0.003
    FALL_M = 0.06
    #: So weit unter `neck1` (m) zählt der Rand noch zum Hals; nach oben bis `head`, um die Halsachse bis `RADIUS_M`.
    UNTER_HALS_M, RADIUS_M = 0.03, 0.13
    #: Nachbarn je Punkt für den weichen Versatz.
    NACHBARN = 24

    @staticmethod
    def _rand(punkte, dreiecke):
        """Lagen der offenen Ränder eines Netzes, Nahtkopien verschweißt (Punkte, die nur einmal an einer Kante hängen)."""
        from .exportleistehautmaske import Exportleistehautmaske
        p, t = Exportleistehautmaske.verschweissen(punkte, dreiecke)
        n = len(p)
        kanten = np.sort(np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]]), axis=1)
        einzig, zahl = np.unique(kanten[:, 0] * n + kanten[:, 1], return_counts=True)
        offen = einzig[zahl == 1]
        return p[np.unique(np.concatenate([offen // n, offen % n]))]

    @classmethod
    def anlegen(cls, stuecke, netz):
        """`stuecke` (`Exportleisterendermodell.stuecke`, `punkte` wird ersetzt), `netz` (`G9koerpernetz`, Ruhelage) → Bericht `{stück: {punkte, weit_mm}}`."""
        knochen = {k['name']: k for k in netz['skelett']['knochen']}
        if 'neck1' not in knochen or 'head' not in knochen:
            return {}
        haut, normalen = np.asarray(netz['punkte'], dtype=np.float64), np.asarray(netz['normalen'], dtype=np.float64)
        unten, oben = float(knochen['neck1']['kopf'][1]) - cls.UNTER_HALS_M, float(knochen['head']['kopf'][1])
        achse = np.asarray(knochen['head']['kopf'], dtype=np.float64)[[0, 2]]
        am_hals = lambda q: (q[:, 1] > unten) & (q[:, 1] < oben) & (np.linalg.norm(q[:, [0, 2]] - achse, axis=1) < cls.RADIUS_M)
        feld = (haut[:, 1] > unten - cls.WEIT_M) & (haut[:, 1] < oben + cls.WEIT_M)
        baum, flaeche, richtung = cKDTree(haut[feld]), haut[feld], normalen[feld]
        bericht = {}
        for s in stuecke:
            if not s['deckt'] or not len(s['dreiecke']):
                continue
            rand = cls._rand(s['punkte'], s['dreiecke'])
            rand = rand[am_hals(rand)]
            if not len(rand):
                continue
            _ab, nah = baum.query(rand)
            hoehe = ((rand - flaeche[nah]) * richtung[nah]).sum(1)
            offen = (hoehe > cls.NAH_M) & (hoehe < cls.WEIT_M)
            if offen.sum() < cls.MIN_PUNKTE:
                continue
            ziel = rand[offen]
            versatz = -richtung[nah][offen] * (hoehe[offen] - cls.LUFT_M)[:, None]
            bericht[s['name']] = {'punkte': int(offen.sum()), 'weit_mm': round(float((hoehe[offen] - cls.LUFT_M).max()) * 1000, 1)}
            s['punkte'] = cls._versetzt(np.asarray(s['punkte'], dtype=np.float64), ziel, versatz)
        return bericht

    @classmethod
    def _versetzt(cls, punkte, ziel, versatz):
        """Jeder Punkt näher als `FALL_M` an `ziel` nimmt das Mittel des Versatzes seiner Nachbarn, nach außen ausgeblendet → Kopie."""
        k = min(cls.NACHBARN, len(ziel))
        ab, nah = cKDTree(ziel).query(punkte, k=k, distance_upper_bound=cls.FALL_M)
        ab, nah = ab.reshape(len(punkte), k), nah.reshape(len(punkte), k)
        treffer = np.isfinite(ab)
        an = treffer.any(1)
        nah_an, treffer_an = nah[an], treffer[an]
        mittel = (versatz[np.minimum(nah_an, len(ziel) - 1)] * treffer_an[:, :, None]).sum(1) / treffer_an.sum(1, keepdims=True)
        t = np.clip(1.0 - ab[an, 0] / cls.FALL_M, 0.0, 1.0)
        neu = punkte.copy()
        neu[an] += mittel * (t * t * (3.0 - 2.0 * t))[:, None]
        return neu
