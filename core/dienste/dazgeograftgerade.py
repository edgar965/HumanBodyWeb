# -*- coding: utf-8 -*-
"""Dazgeograftgerade — die gerade Form des Daz-Penis und ihre Marken neben das Stück legen (10.10.2026).

Das Stück liegt in Dazs Default Pose (Gen1 … Gen4 um 77° nach unten gebogen, dicht am Hodensack). Die Regler des Penis erkennen Achse, Länge und Radius aber an
der Form und finden an dieser Haltung eine waagerechte Achse und 24 mm Radius (gemessen 10.10.2026; `G9stueckgerade` hat die Begründung). Daz formt vor der Pose — hier ebenso:
`G9stueckgerade` hält die gerade Form des Stücks, die Drehmatrix der Pose je Punkt und die Marken der geraden Form, die `G9penisgerade` für die Regler braucht.

MARKEN aus dem Käfig (gerade Form, mit Realism, in Metern): `wurzel` der hinterste Punkt der Penisflächen (`gen1 … gen6`) auf der Achse durch den Drehpunkt von `Gen1`;
`spitze` der Schwerpunkt der 5 % am weitesten vom Drehpunkt entfernten Punkte (die Mitte der Kappe, wie `G9penismorphe.koordinaten`); `achse` von der Wurzel zur Spitze;
`radius` das 90. Perzentil des Querabstands der Penispunkte hinter dem ersten Siebtel; `hoden`/`hoden_radius` Schwerpunkt und 90. Perzentil des Abstands der Fläche `testes`.
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Dazgeograftgerade']


class Dazgeograftgerade:
    PENIS = ('gen1', 'gen2', 'gen3', 'gen4', 'gen5', 'gen6')
    HODEN = ('testes',)
    #: Ein Punkt der Stufe 1 liegt höchstens so weit (m) neben dem Punkt des Stücks.
    MAX_ABSTAND_M = 0.01
    SPITZE_ANTEIL = 0.05

    @classmethod
    def marken(cls, quelle, kaefig):
        """`{wurzel, spitze, achse, laenge, radius, hoden, hoden_radius}` der geraden Form (Käfig `kaefig`, m)."""
        k = Torchfeld.feld(kaefig, dtype=torch.float64)
        penis = k[quelle.gruppenpunkte(cls.PENIS)]
        hoden = k[quelle.gruppenpunkte(cls.HODEN)]
        if len(penis) < 30 or len(hoden) < 10:
            raise ValueError('Penis (%d Punkte) oder Hodensack (%d) nicht gefunden' % (len(penis), len(hoden)))
        dreh = quelle.gen_mitte('Gen1')
        weg = Torchfeld.linalg_norm(penis - dreh, dim=1)
        spitze = penis[weg >= Torchfeld.percentile(weg, 100.0 * (1.0 - cls.SPITZE_ANTEIL))].mean(axis=0)
        achse = (spitze - dreh) / Torchfeld.linalg_norm(spitze - dreh)
        wurzel = dreh + achse * min(float(((penis - dreh) @ achse).min()), 0.0)
        laenge = float(Torchfeld.linalg_norm(spitze - wurzel))
        rel = penis - wurzel
        s = rel @ achse
        quer = Torchfeld.linalg_norm(rel - Torchfeld.outer(s, achse), dim=1)
        radius = float(Torchfeld.percentile(quer[s > laenge / 7.0], 90))
        mitte = hoden.mean(axis=0)
        return {'wurzel': wurzel, 'spitze': spitze, 'achse': achse, 'laenge': laenge, 'radius': radius, 'hoden': mitte,
                'hoden_radius': float(Torchfeld.percentile(Torchfeld.linalg_norm(hoden - mitte, dim=1), 90))}

    @classmethod
    def ablegen(cls, bau, quelle, kaefig, roh, duf):
        """Die Datei `<Stück>.gerade.npz` schreiben (Punkte in der Reihenfolge von `roh`, den Punkten des Stücks) → die Marken."""
        from Genesis9.stueckgerade import G9stueckgerade
        from KoerperKI_alle.kartenbaum import Kartenbaum as cKDTree

        stufe = bau._stufe_von(quelle)
        _gepostet, j_kaefig = quelle.posen(kaefig)
        pose = bau.stufe_punkte(quelle, kaefig)
        gerade = Torchfeld.feld(stufe.punkte(Torchfeld.feld(kaefig, dtype=torch.float64)), dtype=torch.float64)
        # Die Drehmatrix je Punkt durch dieselbe Unterteilung wie die Punkte: spaltenweise (Skinning und Unterteilung sind linear).
        j_stufe = Torchfeld.stack([Torchfeld.feld(stufe.punkte(j_kaefig[:, :, c]), dtype=torch.float64) for c in range(3)], axis=2)
        abstand, nummer = cKDTree(pose).query(Torchfeld.feld(roh, dtype=torch.float64))
        if float(abstand.max()) > cls.MAX_ABSTAND_M:
            raise ValueError('Ein Punkt des Stücks liegt %.1f mm von der Stufe 1 des Geografts entfernt' % (abstand.max() * 1000.0))
        marken = cls.marken(quelle, kaefig)
        G9stueckgerade.schreiben(duf, gerade[nummer], j_stufe[nummer], marken)
        return {k: (Torchfeld.round(Torchfeld.feld(v), 4).tolist() if Torchfeld.ist_feld(v) else round(float(v), 4)) for k, v in marken.items()}
